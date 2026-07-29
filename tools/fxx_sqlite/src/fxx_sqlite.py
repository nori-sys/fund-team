#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import struct
import time
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from statistics import median
from typing import Any, Iterable


DATE_FMT = "%Y-%m-%d"
READ_CHUNK = 1024 * 1024


@dataclass(frozen=True)
class FxxHeader:
    stock_capacity: int
    date_capacity: int
    management_size: int


@dataclass(frozen=True)
class FileFingerprint:
    size: int
    modified_at: str
    sha256: str


@dataclass(frozen=True)
class FxxLayout:
    header: FxxHeader
    dates: list[str]
    code_start: int
    data_start: int
    block_width: int
    stock_count: int


@dataclass(frozen=True)
class DailyPrice:
    fchart_code: int
    trade_date: str
    open: int
    high: int
    low: int
    close: int
    volume: int
    reserve: int
    source_fxx: str
    source_record_index: int


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(READ_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(path: Path) -> FileFingerprint:
    stat = path.stat()
    return FileFingerprint(
        size=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        sha256=sha256_file(path),
    )


def read_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    workspace = Path(config["workspace_folder"]).resolve()
    for key in ("database_path", "schema_path", "import_log_folder", "validation_log_folder", "report_folder"):
        target = Path(config[key]).resolve()
        if workspace not in [target, *target.parents]:
            raise ValueError(f"Workspace外へ成果物を書き出す設定です: {key}={target}")
    return config


def list_fxx_files(folder: Path, minimum: int) -> list[Path]:
    results: list[tuple[int, Path]] = []
    for path in folder.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if len(name) < 3 or name[0].upper() != "F" or not name[1:].isdigit():
            continue
        number = int(name[1:])
        if number >= minimum:
            results.append((number, path))
    return [path for _, path in sorted(results)]


def read_header(blob: bytes, source_name: str) -> FxxHeader:
    if len(blob) < 6:
        raise ValueError(f"ヘッダー不足: {source_name}")
    stock_capacity, date_capacity, management_size = struct.unpack("<HHH", blob[:6])
    if stock_capacity <= 0 or date_capacity <= 0:
        raise ValueError(f"ヘッダー値異常: {source_name}")
    return FxxHeader(stock_capacity, date_capacity, management_size)


def parse_dates(blob: bytes, header: FxxHeader, source_name: str) -> list[str]:
    start = 6
    end = start + header.date_capacity * 3
    if len(blob) < end:
        raise ValueError(f"日付領域不足: {source_name}")
    dates: list[str] = []
    found_empty = False
    for index in range(header.date_capacity):
        y, m, d = blob[start + index * 3:start + index * 3 + 3]
        if (y, m, d) == (0, 0, 0):
            found_empty = True
            continue
        if found_empty:
            raise ValueError(f"日付ゼロ領域後に非ゼロ日付があります: {source_name} index={index}")
        try:
            dates.append(date(1970 + y, m, d).isoformat())
        except ValueError as exc:
            raise ValueError(f"不正な日付: {source_name} index={index} bytes={(y, m, d)}") from exc
    if len(dates) != len(set(dates)):
        raise ValueError(f"日付重複: {source_name}")
    if dates != sorted(dates):
        raise ValueError(f"日付が昇順ではありません: {source_name}")
    return dates


def inspect_layout(blob: bytes, source_name: str) -> FxxLayout:
    header = read_header(blob, source_name)
    dates = parse_dates(blob, header, source_name)
    code_start = 6 + header.date_capacity * 3
    data_start = code_start + header.stock_capacity * 3 + header.management_size + 15
    block_width = header.date_capacity * 14 + 13
    if len(blob) < data_start:
        raise ValueError(f"データ領域先頭がファイルサイズを超えています: {source_name}")
    data_size = len(blob) - data_start
    if data_size <= 0:
        raise ValueError(f"データ領域が空です: {source_name}")
    if (data_size + 13) % block_width == 0:
        stock_count = (data_size + 13) // block_width
    else:
        stock_count = data_size // block_width
    stock_count = min(stock_count, header.stock_capacity)
    if stock_count <= 0:
        raise ValueError(f"実銘柄数を算出できません: {source_name}")
    return FxxLayout(header, dates, code_start, data_start, block_width, stock_count)


def stock_code_at(blob: bytes, layout: FxxLayout, index: int) -> int:
    pos = layout.code_start + index * 3
    return struct.unpack("<H", blob[pos:pos + 2])[0]


def decode_record(raw: bytes) -> tuple[int, int, int, int, int, int]:
    open_diff, high_diff, close_diff, low_base, reserve, volume = struct.unpack("<HHHHHI", raw)
    return low_base + open_diff, low_base + high_diff, low_base, low_base + close_diff, volume, reserve


def iter_prices(blob: bytes, layout: FxxLayout, source_name: str) -> Iterable[DailyPrice]:
    for stock_index in range(layout.stock_count):
        fchart_code = stock_code_at(blob, layout, stock_index)
        if fchart_code == 0:
            continue
        block_start = layout.data_start + stock_index * layout.block_width
        for date_index, trade_date in enumerate(layout.dates):
            rec_start = block_start + date_index * 14
            rec = blob[rec_start:rec_start + 14]
            if len(rec) != 14:
                raise ValueError(f"日足レコード不足: {source_name} stock_index={stock_index} date_index={date_index}")
            if rec == b"\x00" * 14:
                continue
            op, hi, lo, cl, vol, reserve = decode_record(rec)
            if op == hi == lo == cl == vol == 0:
                continue
            if hi < max(op, cl, lo) or lo > min(op, cl, hi):
                raise ValueError(
                    f"OHLC不整合: {source_name} code={fchart_code} date={trade_date} "
                    f"open={op} high={hi} low={lo} close={cl}"
                )
            yield DailyPrice(fchart_code, trade_date, op, hi, lo, cl, vol, reserve, source_name, date_index)


def load_master(path: Path) -> dict[int, dict[str, Any]]:
    stocks: dict[int, dict[str, Any]] = {}
    with path.open("r", encoding="cp932", newline="") as handle:
        reader = csv.reader(handle)
        for line_no, row in enumerate(reader, start=1):
            if len(row) < 12:
                raise ValueError(f"kabu.lst 列数不足: line={line_no}")
            try:
                fchart_code = int(row[0])
            except ValueError as exc:
                raise ValueError(f"kabu.lst 内部コード不正: line={line_no}") from exc
            stocks[fchart_code] = {
                "fchart_code": fchart_code,
                "market_code": row[11],
                "security_code": row[11],
                "security_name": row[6] or row[1],
                "security_type": row[2],
                "source_master": str(path),
            }
    return stocks


def connect_db(db_path: Path, schema_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    return conn


def backup_existing_db(db_path: Path) -> Path | None:
    if not db_path.exists():
        return None
    backup_dir = db_path.parent / "backup"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{db_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def upsert_master(conn: sqlite3.Connection, stocks: dict[int, dict[str, Any]]) -> None:
    rows = [
        (
            item["fchart_code"],
            item["market_code"],
            item["security_code"],
            item["security_name"],
            item["security_type"],
            item["source_master"],
        )
        for item in stocks.values()
    ]
    conn.executemany(
        """
        INSERT INTO stocks (fchart_code, market_code, security_code, security_name, security_type, source_master, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(fchart_code) DO UPDATE SET
            market_code=excluded.market_code,
            security_code=excluded.security_code,
            security_name=excluded.security_name,
            security_type=excluded.security_type,
            source_master=excluded.source_master,
            updated_at=CURRENT_TIMESTAMP
        """,
        rows,
    )


def ensure_unknown_stocks(conn: sqlite3.Connection, codes: set[int]) -> int:
    existing = {row[0] for row in conn.execute("SELECT fchart_code FROM stocks")}
    missing = sorted(codes - existing)
    conn.executemany(
        """
        INSERT OR IGNORE INTO stocks
        (fchart_code, market_code, security_code, security_name, security_type, source_master)
        VALUES (?, NULL, NULL, ?, NULL, 'Fxx code list')
        """,
        [(code, f"UNKNOWN_{code}") for code in missing],
    )
    return len(missing)


def import_one_fxx(conn: sqlite3.Connection, path: Path, import_log: Path, force_reimport: bool = False) -> dict[str, Any]:
    before = fingerprint(path)
    previous = conn.execute(
        "SELECT sha256, import_status, date_count, first_date, last_date, stock_count FROM import_files WHERE source_file = ?",
        (path.name,),
    ).fetchone()
    if not force_reimport and previous and previous[0] == before.sha256 and previous[1] == "imported":
        report = {
            "file": path.name,
            "file_size": before.size,
            "modified_at": before.modified_at,
            "sha256": before.sha256,
            "actual_date_count": previous[2],
            "first_date": previous[3],
            "last_date": previous[4],
            "actual_stock_count": previous[5],
            "inserted_or_updated_prices": 0,
            "status": "skipped_same_hash",
        }
        import_log.mkdir(parents=True, exist_ok=True)
        (import_log / f"{path.name}_skip.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return report
    blob = path.read_bytes()
    after = fingerprint(path)
    if before != after:
        raise RuntimeError(f"読込み中に原本ファイルが変更されました: {path.name}")
    layout = inspect_layout(blob, path.name)
    imported_codes: set[int] = set()
    rows: list[tuple[Any, ...]] = []
    for price in iter_prices(blob, layout, path.name):
        imported_codes.add(price.fchart_code)
        rows.append((
            price.fchart_code,
            price.trade_date,
            price.open,
            price.high,
            price.low,
            price.close,
            price.volume,
            price.source_fxx,
            price.source_record_index,
        ))
    ensure_unknown_stocks(conn, imported_codes)
    with conn:
        conn.executemany(
            """
            INSERT INTO daily_prices_raw
            (fchart_code, trade_date, open, high, low, close, volume, source_fxx, source_record_index, imported_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(fchart_code, trade_date) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume,
                source_fxx=excluded.source_fxx,
                source_record_index=excluded.source_record_index,
                imported_at=CURRENT_TIMESTAMP
            """,
            rows,
        )
        conn.execute(
            """
            INSERT INTO import_files
            (source_file, file_size, modified_at, sha256, date_count, first_date, last_date, stock_count, import_status, imported_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'imported', CURRENT_TIMESTAMP)
            ON CONFLICT(source_file) DO UPDATE SET
                file_size=excluded.file_size,
                modified_at=excluded.modified_at,
                sha256=excluded.sha256,
                date_count=excluded.date_count,
                first_date=excluded.first_date,
                last_date=excluded.last_date,
                stock_count=excluded.stock_count,
                import_status='imported',
                imported_at=CURRENT_TIMESTAMP
            """,
            (
                path.name,
                before.size,
                before.modified_at,
                before.sha256,
                len(layout.dates),
                layout.dates[0],
                layout.dates[-1],
                layout.stock_count,
            ),
        )
    report = {
        "file": path.name,
        "file_size": before.size,
        "modified_at": before.modified_at,
        "sha256": before.sha256,
        "stock_capacity": layout.header.stock_capacity,
        "date_capacity": layout.header.date_capacity,
        "actual_date_count": len(layout.dates),
        "first_date": layout.dates[0],
        "last_date": layout.dates[-1],
        "data_start": layout.data_start,
        "block_width": layout.block_width,
        "actual_stock_count": layout.stock_count,
        "inserted_or_updated_prices": len(rows),
        "unique_codes_with_prices": len(imported_codes),
        "status": "imported",
    }
    import_log.mkdir(parents=True, exist_ok=True)
    (import_log / f"{path.name}_import.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def parse_reference(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="cp932", newline="") as handle:
        reader = csv.reader(handle)
        for line_no, row in enumerate(reader, start=1):
            if len(row) < 6:
                raise ValueError(f"照合ファイル列数不足: {path.name}:{line_no}")
            rows.append({
                "trade_date": datetime.strptime(row[0], "%Y%m%d").strftime(DATE_FMT),
                "open": int(row[1]),
                "high": int(row[2]),
                "low": int(row[3]),
                "close": int(row[4]),
                "volume": int(row[5]),
            })
    return rows


def validate_reference(conn: sqlite3.Connection, spec: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    fchart_code = int(spec["fchart_code"])
    mode = spec.get("mode", "exact")
    reference = parse_reference(Path(spec["reference_file"]))
    mismatches: list[dict[str, Any]] = []
    explained: list[dict[str, Any]] = []
    price_ratios: list[float] = []
    for expected in reference:
        row = conn.execute(
            """
            SELECT open, high, low, close, volume
            FROM daily_prices_raw
            WHERE fchart_code = ? AND trade_date = ?
            """,
            (fchart_code, expected["trade_date"]),
        ).fetchone()
        if row is None:
            mismatches.append({"date": expected["trade_date"], "reason": "missing"})
            continue
        actual = {"open": row[0], "high": row[1], "low": row[2], "close": row[3], "volume": row[4]}
        if actual == {k: expected[k] for k in actual}:
            continue
        if mode == "split_factor":
            local_ratios = [actual[k] / expected[k] for k in ("open", "high", "low", "close") if expected[k] != 0]
            factor = median(local_ratios)
            rounded_factor = round(factor)
            price_ok = rounded_factor > 1 and all(abs(actual[k] - expected[k] * rounded_factor) <= rounded_factor for k in ("open", "high", "low", "close"))
            volume_ok = actual["volume"] * rounded_factor == expected["volume"]
            if price_ok and volume_ok:
                price_ratios.append(float(rounded_factor))
                explained.append({"date": expected["trade_date"], "factor": rounded_factor, "actual": actual, "reference": expected})
                continue
        mismatches.append({"date": expected["trade_date"], "actual": actual, "reference": expected})
    unexplained = len(mismatches)
    status = "PASS" if unexplained == 0 else "FAIL"
    result = {
        "fchart_code": fchart_code,
        "reference_file": Path(spec["reference_file"]).name,
        "mode": mode,
        "expected_count": len(reference),
        "actual_count": len(reference) - sum(1 for item in mismatches if item.get("reason") == "missing"),
        "unexplained_mismatch_count": unexplained,
        "explained_split_count": len(explained),
        "detected_split_factors": sorted(set(price_ratios)),
        "status": status,
        "mismatches": mismatches[:50],
        "explained_samples": explained[:10],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"validation_{fchart_code}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    conn.execute(
        """
        INSERT INTO validation_results
        (source_file, fchart_code, test_name, expected_count, actual_count, mismatch_count, status, details, executed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (
            Path(spec["reference_file"]).name,
            fchart_code,
            f"reference_{mode}",
            result["expected_count"],
            result["actual_count"],
            result["unexplained_mismatch_count"],
            status,
            json.dumps({k: v for k, v in result.items() if k not in ("mismatches", "explained_samples")}, ensure_ascii=False),
        ),
    )
    conn.commit()
    return result


def run_integrity_checks(conn: sqlite3.Connection, output_dir: Path) -> dict[str, Any]:
    duplicate_pk = conn.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT fchart_code, trade_date, COUNT(*) c
            FROM daily_prices_raw
            GROUP BY fchart_code, trade_date
            HAVING c > 1
        )
        """
    ).fetchone()[0]
    ohlc_errors = conn.execute(
        """
        SELECT COUNT(*) FROM daily_prices_raw
        WHERE high < open OR high < close OR high < low OR low > open OR low > close OR low > high OR volume < 0
        """
    ).fetchone()[0]
    empty_registered = conn.execute(
        """
        SELECT COUNT(*) FROM daily_prices_raw
        WHERE open = 0 AND high = 0 AND low = 0 AND close = 0 AND volume = 0
        """
    ).fetchone()[0]
    unknown_stocks = conn.execute("SELECT COUNT(*) FROM stocks WHERE security_name LIKE 'UNKNOWN_%'").fetchone()[0]
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    summary = {
        "duplicate_primary_key_count": duplicate_pk,
        "ohlcv_error_count": ohlc_errors,
        "empty_record_registered_count": empty_registered,
        "unknown_stock_count": unknown_stocks,
        "sqlite_integrity_check": integrity,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "validation_overall.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def make_completion_report(
    config: dict[str, Any],
    import_reports: list[dict[str, Any]],
    validation_reports: list[dict[str, Any]],
    integrity: dict[str, Any],
    elapsed: float,
    backup_path: Path | None,
) -> Path:
    db_path = Path(config["database_path"])
    conn = sqlite3.connect(db_path)
    stock_count = conn.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
    price_count = conn.execute("SELECT COUNT(*) FROM daily_prices_raw").fetchone()[0]
    oldest, latest = conn.execute("SELECT MIN(trade_date), MAX(trade_date) FROM daily_prices_raw").fetchone()
    warning_count = integrity["unknown_stock_count"]
    error_count = integrity["duplicate_primary_key_count"] + integrity["ohlcv_error_count"] + integrity["empty_record_registered_count"]
    error_count += sum(1 for item in validation_reports if item["status"] != "PASS")
    conn.close()
    lines = [
        "20260717-01 Fxx SQLite試作実装 作業完了報告書",
        f"作業ID: 20260717-01",
        f"実施日時: {now_text()}",
        "実装内容: Fxxパーサー、SQLite登録、照合、自動検査、再実行可能なUPSERT処理",
        "対象Fxx: " + ", ".join(item["file"] for item in import_reports),
        f"登録銘柄数: {stock_count}",
        f"登録日足件数: {price_count}",
        f"最古日: {oldest}",
        f"最新日: {latest}",
        f"処理時間: {elapsed:.2f}秒",
        "照合結果:",
    ]
    for item in validation_reports:
        factor = f" split_factors={item['detected_split_factors']}" if item["detected_split_factors"] else ""
        lines.append(
            f"  - {item['fchart_code']}: {item['status']} "
            f"expected={item['expected_count']} actual={item['actual_count']} "
            f"unexplained_mismatch={item['unexplained_mismatch_count']} "
            f"explained_split={item['explained_split_count']}{factor}"
        )
    lines.extend([
        f"不一致件数: {sum(item['unexplained_mismatch_count'] for item in validation_reports)}",
        f"警告件数: {warning_count}",
        f"エラー件数: {error_count}",
        "原本フォルダへの書込み: 0件（プログラムは原本を読取り専用で参照し、成果物はWorkspace内のみ）",
        f"SQLite integrity_check結果: {integrity['sqlite_integrity_check']}",
        f"既存DBバックアップ: {backup_path if backup_path else 'なし（新規作成）'}",
        "既知の制約: F00-F49は対象外。株式分割の公式情報は未連携で、照合ファイルとの倍率関係として検出。",
        "未解決事項: F89の日付容量300件中、実データ86件以降はゼロ未使用領域として処理。正式仕様への明文化が必要。",
        "次工程への提案: 分割・併合マスタの追加、F00-F49長期履歴対応、日次更新バッチ化、スクリーニング機能連携。",
    ])
    report_dir = Path(config["report_folder"])
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "20260717-01_作業完了報告書.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run(config_path: Path, force_reimport: bool = False) -> int:
    started = time.perf_counter()
    config = read_config(config_path)
    fxx_folder = Path(config["fxx_source_folder"])
    master_file = Path(config["master_file"])
    db_path = Path(config["database_path"])
    backup_path = backup_existing_db(db_path)
    conn = connect_db(db_path, Path(config["schema_path"]))
    try:
        master = load_master(master_file)
        with conn:
            upsert_master(conn, master)
        import_reports: list[dict[str, Any]] = []
        for path in list_fxx_files(fxx_folder, int(config["minimum_fxx_number"])):
            import_reports.append(import_one_fxx(conn, path, Path(config["import_log_folder"]), force_reimport=force_reimport))
            print(f"imported {path.name}: {import_reports[-1]['inserted_or_updated_prices']} rows")
        validation_reports = [validate_reference(conn, spec, Path(config["validation_log_folder"])) for spec in config["validation_symbols"]]
        integrity = run_integrity_checks(conn, Path(config["validation_log_folder"]))
        report_path = make_completion_report(config, import_reports, validation_reports, integrity, time.perf_counter() - started, backup_path)
        print(f"completion_report={report_path}")
        if integrity["sqlite_integrity_check"] != "ok":
            return 2
        if any(item["status"] != "PASS" for item in validation_reports):
            return 3
        return 0
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("tools/fxx_sqlite/config/config.json"))
    parser.add_argument("--force-reimport", action="store_true")
    args = parser.parse_args()
    return run(args.config, force_reimport=args.force_reimport)


if __name__ == "__main__":
    raise SystemExit(main())
