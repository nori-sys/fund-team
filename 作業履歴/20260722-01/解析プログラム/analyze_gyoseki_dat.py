from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


TARGET_FILES = ["kigyo.dat", "kigyo2.dat", "kigyo3.dat", "Zaimu.dat"]
COPY_DIR_NAME = "解析用コピー"
RESULT_DIR_NAME = "解析結果"
COMPARE_DIR_NAME = "比較表"
REPORT_DIR_NAME = "報告書"

COMMON_RECORD_LENGTHS = [16, 20, 24, 28, 32, 36, 40, 48, 52, 56, 60, 64, 68, 72, 80, 96, 100, 108, 112, 120, 128, 160, 192, 200, 224, 256, 300, 320, 384, 400, 512, 600, 640, 800, 1024, 1200, 1600, 2000, 2400, 3200, 4000, 5000, 6000, 8000]
CODE_RE = re.compile(rb"(?<![0-9])([1-9][0-9]{3})(?![0-9])")
KNOWN_RECORD_LENGTHS = {"kigyo.dat": 823, "kigyo2.dat": 330, "kigyo3.dat": 330}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def hex_dump(data: bytes, base: int = 0, width: int = 16) -> str:
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i : i + width]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{base+i:08X}  {hex_part:<{width*3}} {ascii_part}")
    return "\n".join(lines)


def zero_runs(data: bytes, min_len: int = 64, limit: int = 20) -> list[dict]:
    runs = []
    start = None
    for i, b in enumerate(data):
        if b == 0:
            if start is None:
                start = i
        elif start is not None:
            if i - start >= min_len:
                runs.append({"offset": start, "length": i - start})
            start = None
    if start is not None and len(data) - start >= min_len:
        runs.append({"offset": start, "length": len(data) - start})
    runs.sort(key=lambda x: x["length"], reverse=True)
    return runs[:limit]


def printable_runs(data: bytes, enc: str, min_chars: int = 4, limit: int = 500) -> list[dict]:
    results = []
    if enc in {"ascii", "utf-8"}:
        pattern = rb"[\x20-\x7E]{%d,}" % min_chars
        for m in re.finditer(pattern, data):
            raw = m.group(0)
            try:
                text = raw.decode(enc)
            except UnicodeDecodeError:
                continue
            results.append({"offset": m.start(), "length": len(raw), "encoding": enc, "text": text})
    elif enc in {"cp932", "shift_jis"}:
        start = None
        i = 0
        while i < len(data):
            b = data[i]
            step = 0
            if 0x20 <= b <= 0x7E or 0xA1 <= b <= 0xDF:
                step = 1
            elif i + 1 < len(data) and ((0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xFC)) and (0x40 <= data[i + 1] <= 0xFC and data[i + 1] != 0x7F):
                step = 2
            if step:
                if start is None:
                    start = i
                i += step
            else:
                if start is not None and i - start >= min_chars:
                    raw = data[start:i]
                    try:
                        text = raw.decode(enc)
                        if sum(1 for ch in text if ch.isprintable()) >= min_chars:
                            results.append({"offset": start, "length": len(raw), "encoding": enc, "text": text})
                    except UnicodeDecodeError:
                        pass
                start = None
                i += 1
        if start is not None and len(data) - start >= min_chars:
            raw = data[start:]
            try:
                results.append({"offset": start, "length": len(raw), "encoding": enc, "text": raw.decode(enc)})
            except UnicodeDecodeError:
                pass
    elif enc == "utf-16le":
        for m in re.finditer((rb"(?:[\x20-\x7E]\x00){%d,}") % min_chars, data):
            raw = m.group(0)
            try:
                results.append({"offset": m.start(), "length": len(raw), "encoding": enc, "text": raw.decode(enc)})
            except UnicodeDecodeError:
                pass
    clean = []
    seen = set()
    for row in results:
        text = row["text"].replace("\r", " ").replace("\n", " ").strip("\x00 ")
        if len(text) < min_chars:
            continue
        key = (row["offset"], row["encoding"], text)
        if key in seen:
            continue
        seen.add(key)
        row["text"] = text
        clean.append(row)
    clean.sort(key=lambda x: (x["offset"], x["encoding"]))
    return clean[:limit]


def record_len_candidates(data: bytes) -> list[dict]:
    size = len(data)
    candidates = []
    for header in range(0, min(4096, size), 4):
        remain = size - header
        if remain <= 0:
            continue
        for rec_len in COMMON_RECORD_LENGTHS:
            count, tail = divmod(remain, rec_len)
            if count < 5:
                continue
            score = 0.0
            if tail == 0:
                score += 3.0
            elif tail <= 256:
                score += 1.0
            sample_count = min(count, 200)
            first_bytes = []
            code_hits = 0
            for idx in range(sample_count):
                rec = data[header + idx * rec_len : header + (idx + 1) * rec_len]
                if len(rec) < rec_len:
                    break
                first_bytes.append(rec[: min(8, len(rec))])
                if CODE_RE.search(rec[:64]):
                    code_hits += 1
            if first_bytes:
                score += len(set(first_bytes)) / len(first_bytes)
            score += min(code_hits / max(sample_count, 1), 1.0)
            candidates.append({"header": header, "record_length": rec_len, "record_count": count, "tail": tail, "score": round(score, 4), "code_hits_first64": code_hits})
    candidates.sort(key=lambda x: (-x["score"], x["tail"], x["header"], x["record_length"]))
    return candidates[:30]


def search_known_codes(data: bytes, codes: list[str], context: int = 24) -> list[dict]:
    rows = []
    for code in codes:
        b = code.encode("ascii")
        for m in re.finditer(re.escape(b), data):
            start = max(0, m.start() - context)
            end = min(len(data), m.end() + context)
            rows.append({"code": code, "offset": m.start(), "before_after_hex": data[start:end].hex(" ").upper()})
            if len([r for r in rows if r["code"] == code]) >= 30:
                break
    return rows


def numeric_probe(data: bytes, offsets: list[int]) -> list[dict]:
    rows = []
    fmts = [
        ("i16le", "<h", 2), ("u16le", "<H", 2), ("i32le", "<i", 4), ("u32le", "<I", 4),
        ("f32le", "<f", 4), ("i16be", ">h", 2), ("u16be", ">H", 2), ("i32be", ">i", 4),
        ("u32be", ">I", 4), ("f32be", ">f", 4),
    ]
    for off in offsets:
        for name, fmt, size in fmts:
            if off + size <= len(data):
                val = struct.unpack(fmt, data[off : off + size])[0]
                if isinstance(val, float):
                    if math.isfinite(val) and abs(val) < 1e12:
                        rows.append({"offset": off, "type": name, "value": repr(round(val, 6))})
                elif -10_000_000_000 <= val <= 10_000_000_000:
                    rows.append({"offset": off, "type": name, "value": str(val)})
    return rows


def ascii_digit_hits(rec: bytes) -> list[tuple[int, str]]:
    return [(m.start(), m.group(0).decode("ascii")) for m in re.finditer(rb"[0-9]{4,8}", rec)]


def cp932_preview(rec: bytes, min_len: int = 8) -> list[tuple[int, str]]:
    rows = []
    start = None
    i = 0
    while i < len(rec):
        b = rec[i]
        step = 0
        if 0x20 <= b <= 0x7E or 0xA1 <= b <= 0xDF:
            step = 1
        elif i + 1 < len(rec) and ((0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xFC)) and (0x40 <= rec[i + 1] <= 0xFC and rec[i + 1] != 0x7F):
            step = 2
        if step:
            if start is None:
                start = i
            i += step
        else:
            if start is not None and i - start >= min_len:
                raw = rec[start:i]
                try:
                    text = raw.decode("cp932").strip("\x00 ")
                    if text:
                        rows.append((start, text[:120]))
                except UnicodeDecodeError:
                    pass
            start = None
            i += 1
    if start is not None and len(rec) - start >= min_len:
        try:
            text = rec[start:].decode("cp932").strip("\x00 ")
            if text:
                rows.append((start, text[:120]))
        except UnicodeDecodeError:
            pass
    return rows


def sample_fixed_records(name: str, data: bytes, rec_len: int) -> list[dict]:
    rows = []
    count = len(data) // rec_len
    sample_indexes = list(dict.fromkeys([0, 1, 2, 3, 4, 10, 100, 1000, max(0, count - 1)]))
    for idx in sample_indexes:
        if idx >= count:
            continue
        rec = data[idx * rec_len : (idx + 1) * rec_len]
        rows.append({
            "file": name,
            "record_index": idx,
            "record_offset": idx * rec_len,
            "record_length": rec_len,
            "head_64_hex": rec[:64].hex(" ").upper(),
            "ascii_digit_hits": json.dumps(ascii_digit_hits(rec)[:20], ensure_ascii=False),
            "cp932_preview": json.dumps(cp932_preview(rec)[:8], ensure_ascii=False),
        })
    return rows


def fixed_record_summary(name: str, data: bytes, rec_len: int) -> dict:
    count, tail = divmod(len(data), rec_len)
    code_offsets = Counter()
    date_offsets = Counter()
    text_offsets = Counter()
    for idx in range(min(count, 1000)):
        rec = data[idx * rec_len : (idx + 1) * rec_len]
        for off, val in ascii_digit_hits(rec):
            if re.fullmatch(r"[1-9][0-9]{3}", val):
                code_offsets[off] += 1
            if re.fullmatch(r"[0-9]{4}|[0-9]{6}|[0-9]{8}", val):
                date_offsets[off] += 1
        for off, text in cp932_preview(rec):
            if any("\u3040" <= ch <= "\u9fff" or "\u30a0" <= ch <= "\u30ff" for ch in text):
                text_offsets[off] += 1
    return {
        "file": name,
        "record_length": rec_len,
        "record_count": count,
        "tail": tail,
        "top_code_offsets_first1000": json.dumps(code_offsets.most_common(10), ensure_ascii=False),
        "top_date_offsets_first1000": json.dumps(date_offsets.most_common(10), ensure_ascii=False),
        "top_text_offsets_first1000": json.dumps(text_offsets.most_common(10), ensure_ascii=False),
    }


def zaimu_record_candidates(size: int, expected_count: int = 10462) -> list[dict]:
    rows = []
    for header in range(0, 4096):
        remain = size - header
        if remain <= 0:
            continue
        rec_len, tail = divmod(remain, expected_count)
        if 4000 <= rec_len <= 5000 and tail < expected_count:
            rows.append({"header": header, "record_length": rec_len, "record_count": expected_count, "tail": tail})
    rows.sort(key=lambda x: (x["tail"], x["header"]))
    return rows[:30]


def parse_kabu(path: Path) -> list[dict]:
    data = path.read_bytes()
    rows = []
    for enc in ("cp932", "shift_jis", "utf-8"):
        try:
            text = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("cp932", errors="replace")
        enc = "cp932?"
    for i, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        m = re.search(r"([1-9][0-9]{3})", stripped)
        rows.append({"line_no": i, "code": m.group(1) if m else "", "text": stripped, "encoding": enc})
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys = []
        for row in rows:
            for key in row.keys():
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--original-dir", type=Path, default=Path(r"C:\fchart\gyoseki"))
    parser.add_argument("--kabu-original", type=Path, default=Path(r"C:\fchart\kabu.lst"))
    args = parser.parse_args()

    workdir = args.workdir
    copy_dir = workdir / COPY_DIR_NAME
    result_dir = workdir / RESULT_DIR_NAME
    compare_dir = workdir / COMPARE_DIR_NAME
    result_dir.mkdir(parents=True, exist_ok=True)
    compare_dir.mkdir(parents=True, exist_ok=True)

    file_rows = []
    structure_rows = []
    strings_rows = []
    code_rows = []
    sample_rows = []
    fixed_summary_rows = []
    dumps = {}
    candidates_by_file = {}
    known_codes = ["7203", "6506", "8267", "1308", "9984", "6758", "4755", "2802"]

    kabu_rows = parse_kabu(copy_dir / "kabu.lst")
    write_csv(compare_dir / "kabu_lst_抽出.csv", kabu_rows[:2000], ["line_no", "code", "text", "encoding"])
    kabu_codes = [r["code"] for r in kabu_rows if r["code"]]
    known_codes = list(dict.fromkeys(known_codes + kabu_codes[:20]))

    for name in TARGET_FILES:
        src = args.original_dir / name
        cp = copy_dir / name
        data = cp.read_bytes()
        src_hash = sha256(src) if src.exists() else ""
        cp_hash = sha256(cp)
        stat = cp.stat()
        file_rows.append({
            "file": name,
            "original_path": str(src),
            "copy_path": str(cp),
            "size": stat.st_size,
            "mtime_copy": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "sha256_original": src_hash,
            "sha256_copy": cp_hash,
            "hash_match": str(src_hash == cp_hash),
            "head_256_hex": data[:256].hex(" ").upper(),
            "tail_256_hex": data[-256:].hex(" ").upper(),
            "zero_runs_top": json.dumps(zero_runs(data, 128, 8), ensure_ascii=False),
        })
        dumps[name] = {
            "head": hex_dump(data[:256], 0),
            "tail": hex_dump(data[-256:], max(0, len(data) - 256)),
        }
        candidates = record_len_candidates(data)
        candidates_by_file[name] = candidates
        for c in candidates[:10]:
            structure_rows.append({"file": name, **c})
        if name in KNOWN_RECORD_LENGTHS:
            rec_len = KNOWN_RECORD_LENGTHS[name]
            fixed_summary_rows.append(fixed_record_summary(name, data, rec_len))
            sample_rows.extend(sample_fixed_records(name, data, rec_len))
        elif name == "Zaimu.dat":
            for c in zaimu_record_candidates(len(data)):
                structure_rows.append({"file": name, "score": "expected_count_10462", **c})
        for enc in ("cp932", "shift_jis", "ascii", "utf-8", "utf-16le"):
            for row in printable_runs(data, enc, 4, 120):
                strings_rows.append({"file": name, **row, "context_hex": data[max(0, row["offset"] - 8): row["offset"] + row["length"] + 8].hex(" ").upper()})
        for row in search_known_codes(data, known_codes[:60]):
            code_rows.append({"file": name, **row})

    write_csv(result_dir / "ファイル情報・ハッシュ一覧.csv", file_rows)
    write_csv(result_dir / "レコード長候補一覧.csv", structure_rows)
    write_csv(result_dir / "固定長レコード概要.csv", fixed_summary_rows)
    write_csv(result_dir / "固定長レコードサンプル.csv", sample_rows)
    write_csv(result_dir / "可読文字列抽出結果.csv", strings_rows)
    write_csv(compare_dir / "銘柄コード検索結果.csv", code_rows)

    with (result_dir / "先頭末尾256バイトダンプ.txt").open("w", encoding="utf-8") as f:
        for name, dd in dumps.items():
            f.write(f"## {name} head\n{dd['head']}\n\n## {name} tail\n{dd['tail']}\n\n")

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "files": file_rows,
        "record_candidates": candidates_by_file,
        "string_count": len(strings_rows),
        "code_hit_count": len(code_rows),
    }
    (result_dir / "analysis_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
