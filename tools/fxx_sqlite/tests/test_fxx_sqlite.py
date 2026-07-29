from __future__ import annotations

import struct
import unittest

from tools.fxx_sqlite.src.fxx_sqlite import FxxHeader, decode_record, parse_dates


class FxxSqliteTests(unittest.TestCase):
    def test_parse_dates_ignores_trailing_zero_capacity(self) -> None:
        blob = struct.pack("<HHH", 1, 3, 0) + bytes([56, 7, 16, 0, 0, 0, 0, 0, 0])
        self.assertEqual(parse_dates(blob, FxxHeader(1, 3, 0), "T"), ["2026-07-16"])

    def test_decode_record_restores_ohlcv(self) -> None:
        raw = struct.pack("<HHHHHI", 25, 25, 20, 2830, 0, 228269)
        self.assertEqual(decode_record(raw), (2855, 2855, 2830, 2850, 228269, 0))


if __name__ == "__main__":
    unittest.main()
