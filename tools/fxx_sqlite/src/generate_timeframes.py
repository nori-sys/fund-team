#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, sqlite3, time
from datetime import datetime
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS timeframes (
    timeframe_code TEXT PRIMARY KEY,
    period_unit TEXT NOT NULL,
    period_value INTEGER NOT NULL,
    calendar_rule TEXT NOT NULL,
    last_generated_at TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS weekly_prices (
    fchart_code INTEGER NOT NULL,
    timeframe_code TEXT NOT NULL DEFAULT '1W',
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    open INTEGER,
    high INTEGER,
    low INTEGER,
    close INTEGER,
    volume INTEGER,
    source_daily_max_date TEXT NOT NULL,
    generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fchart_code, timeframe_code, period_start),
    FOREIGN KEY (fchart_code) REFERENCES stocks(fchart_code),
    FOREIGN KEY (timeframe_code) REFERENCES timeframes(timeframe_code),
    CHECK (volume IS NULL OR volume >= 0),
    CHECK (high IS NULL OR (high >= open AND high >= close AND high >= low)),
    CHECK (low IS NULL OR (low <= open AND low <= close AND low <= high))
);
CREATE INDEX IF NOT EXISTS idx_weekly_prices_period ON weekly_prices(period_start, period_end);
'''

def backup(db: Path) -> Path:
    out = db.parent / 'backup' / f'{db.stem}_weekly_{datetime.now():%Y%m%d_%H%M%S}{db.suffix}'
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(db, out)
    return out

def run(db_path: Path, do_backup: bool = True) -> dict:
    backup_path = backup(db_path) if do_backup else None
    con = sqlite3.connect(db_path)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript(SCHEMA)
    con.execute("INSERT OR IGNORE INTO timeframes(timeframe_code,period_unit,period_value,calendar_rule) VALUES('1W','WEEK',1,'MONDAY_TO_SUNDAY')")
    last = con.execute("SELECT last_generated_at FROM timeframes WHERE timeframe_code='1W'").fetchone()[0]
    if last:
        affected = con.execute("""SELECT DISTINCT date(trade_date, '-' || ((CAST(strftime('%w',trade_date) AS INTEGER)+6)%7) || ' days')
            FROM daily_prices_raw WHERE imported_at > ?""", (last,)).fetchall()
    else:
        affected = con.execute("""SELECT DISTINCT date(trade_date, '-' || ((CAST(strftime('%w',trade_date) AS INTEGER)+6)%7) || ' days')
            FROM daily_prices_raw""").fetchall()
    weeks = [r[0] for r in affected]
    if weeks:
        placeholders=','.join('?'*len(weeks))
        con.execute('DROP TABLE IF EXISTS temp.week_agg')
        con.execute(f'''CREATE TEMP TABLE week_agg AS
            SELECT fchart_code,
              date(trade_date, '-' || ((CAST(strftime('%w',trade_date) AS INTEGER)+6)%7) || ' days') period_start,
              MIN(trade_date) first_date, MAX(trade_date) last_date,
              MAX(high) high, MIN(low) low, SUM(volume) volume
            FROM daily_prices_raw
            WHERE date(trade_date, '-' || ((CAST(strftime('%w',trade_date) AS INTEGER)+6)%7) || ' days') IN ({placeholders})
            GROUP BY fchart_code, period_start''', weeks)
        con.execute(f'''INSERT INTO weekly_prices
            (fchart_code,timeframe_code,period_start,period_end,open,high,low,close,volume,source_daily_max_date,generated_at)
            SELECT g.fchart_code,'1W',g.period_start,date(g.period_start,'+6 days'),d1.open,g.high,g.low,d2.close,g.volume,g.last_date,CURRENT_TIMESTAMP
            FROM week_agg g JOIN daily_prices_raw d1 ON d1.fchart_code=g.fchart_code AND d1.trade_date=g.first_date
            JOIN daily_prices_raw d2 ON d2.fchart_code=g.fchart_code AND d2.trade_date=g.last_date
            ON CONFLICT(fchart_code,timeframe_code,period_start) DO UPDATE SET
              period_end=excluded.period_end,open=excluded.open,high=excluded.high,low=excluded.low,close=excluded.close,volume=excluded.volume,source_daily_max_date=excluded.source_daily_max_date,generated_at=CURRENT_TIMESTAMP''')
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    con.execute("UPDATE timeframes SET last_generated_at=?,updated_at=CURRENT_TIMESTAMP WHERE timeframe_code='1W'", (generated_at,))
    con.commit()
    weekly_count=con.execute("SELECT COUNT(*) FROM weekly_prices WHERE timeframe_code='1W'").fetchone()[0]
    con.close()
    return {'backup': str(backup_path) if backup_path else None, 'affected_weeks':len(weeks), 'weekly_count':weekly_count, 'last_generated_at':generated_at}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--db',default='database/fund_stock.db'); ap.add_argument('--no-backup',action='store_true'); args=ap.parse_args()
    print(run(Path(args.db),not args.no_backup))
