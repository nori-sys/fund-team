#!/usr/bin/env python3
"""
Fxx試作実装の前段階で使用する安全検査ツール。

この版はFxx原本を書き換えない。
ヘッダー、日付一覧、ファイルハッシュ、照合用テキストの形式を確認する。
OHLCVの全銘柄抽出は次工程で実装する。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class FxxHeader:
    stock_capacity: int
    date_capacity: int
    management_size: int


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_header(path: Path) -> FxxHeader:
    with path.open("rb") as handle:
        raw = handle.read(6)
    if len(raw) != 6:
        raise ValueError(f"ヘッダー不足: {path}")
    stock_capacity, date_capacity, management_size = struct.unpack("<HHH", raw)
    return FxxHeader(stock_capacity, date_capacity, management_size)


def read_dates(path: Path, header: FxxHeader) -> list[str]:
    with path.open("rb") as handle:
        handle.seek(6)
        raw = handle.read(header.date_capacity * 3)

    if len(raw) != header.date_capacity * 3:
        raise ValueError(f"日付領域不足: {path}")

    results: list[str] = []
    for index in range(header.date_capacity):
        year_offset, month, day = raw[index * 3:index * 3 + 3]
        try:
            parsed = date(1970 + year_offset, month, day)
        except ValueError as exc:
            raise ValueError(
                f"不正な日付: file={path.name}, index={index}, "
                f"bytes={(year_offset, month, day)}"
            ) from exc
        results.append(parsed.isoformat())
    return results


def inspect_fxx(path: Path) -> dict:
    header = read_header(path)
    dates = read_dates(path, header)
    return {
        "file": path.name,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "stock_capacity": header.stock_capacity,
        "date_capacity": header.date_capacity,
        "management_size": header.management_size,
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "dates_are_unique": len(dates) == len(set(dates)),
        "dates_are_ascending": dates == sorted(dates),
    }


def inspect_reference(path: Path) -> dict:
    rows = []
    with path.open("r", encoding="cp932", newline="") as handle:
        reader = csv.reader(handle)
        for line_no, row in enumerate(reader, start=1):
            if len(row) < 6:
                raise ValueError(f"{path.name}:{line_no} 列数不足")
            rows.append(row)

    dates = [row[0] for row in rows]
    return {
        "file": path.name,
        "record_count": len(rows),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
        "dates_are_unique": len(dates) == len(set(dates)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fxx", nargs="+", type=Path, required=True)
    parser.add_argument("--reference", nargs="*", type=Path, default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = {
        "fxx_files": [inspect_fxx(path) for path in args.fxx],
        "reference_files": [inspect_reference(path) for path in args.reference],
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
