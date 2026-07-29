PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS stocks (
    fchart_code INTEGER PRIMARY KEY,
    market_code TEXT,
    security_code TEXT,
    security_name TEXT NOT NULL,
    security_type TEXT,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    source_master TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_prices_raw (
    fchart_code INTEGER NOT NULL,
    trade_date TEXT NOT NULL,
    open INTEGER,
    high INTEGER,
    low INTEGER,
    close INTEGER,
    volume INTEGER,
    source_fxx TEXT NOT NULL,
    source_record_index INTEGER,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fchart_code, trade_date),
    FOREIGN KEY (fchart_code) REFERENCES stocks(fchart_code),
    CHECK (volume IS NULL OR volume >= 0),
    CHECK (
        open IS NULL OR high IS NULL OR low IS NULL OR close IS NULL OR
        (high >= open AND high >= close AND high >= low AND
         low <= open AND low <= close AND low <= high)
    )
);

CREATE INDEX IF NOT EXISTS idx_daily_prices_raw_date
ON daily_prices_raw(trade_date);

CREATE TABLE IF NOT EXISTS daily_prices_adjusted (
    fchart_code INTEGER NOT NULL,
    trade_date TEXT NOT NULL,
    open_adjusted REAL,
    high_adjusted REAL,
    low_adjusted REAL,
    close_adjusted REAL,
    volume_adjusted REAL,
    adjustment_factor REAL NOT NULL,
    adjustment_source TEXT NOT NULL,
    calculated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (fchart_code, trade_date),
    FOREIGN KEY (fchart_code, trade_date)
        REFERENCES daily_prices_raw(fchart_code, trade_date)
);

CREATE TABLE IF NOT EXISTS import_files (
    source_file TEXT PRIMARY KEY,
    file_size INTEGER NOT NULL,
    modified_at TEXT,
    sha256 TEXT NOT NULL,
    date_count INTEGER,
    first_date TEXT,
    last_date TEXT,
    stock_count INTEGER,
    import_status TEXT NOT NULL,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS validation_results (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    fchart_code INTEGER,
    test_name TEXT NOT NULL,
    expected_count INTEGER,
    actual_count INTEGER,
    mismatch_count INTEGER,
    status TEXT NOT NULL,
    details TEXT,
    executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
