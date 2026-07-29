Fxx SQLite 試作セット

収録ファイル
・Fxx_SQLite_試作実装仕様書.txt
・schema.sql
・config.sample.json
・fxx_preflight_validator.py

使用目的
FChart Fxx原本からファンドチーム専用SQLite株価DBを構築する前段階の
仕様固定、DB定義、安全確認に使用します。

注意
fxx_preflight_validator.pyは、現時点ではヘッダー、日付、ハッシュ、
照合用テキスト形式を確認する安全検査版です。
全銘柄のOHLCV抽出処理は、次工程で実装します。

実行例
python fxx_preflight_validator.py ^
  --fxx F50 F88 F89 ^
  --reference 1308.txt 8267.txt 10272.txt ^
  --output preflight_report.json
