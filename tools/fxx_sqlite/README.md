# Fxx SQLite 試作実装

## 実行

Codex同梱Pythonを使用します。

```powershell
& 'C:\Users\nori\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\fxx_sqlite\src\fxx_sqlite.py --config tools\fxx_sqlite\config\config.json
```

## 成果物

- SQLite: `database/fund_stock.db`
- 取込ログ: `logs/import`
- 照合・検査ログ: `logs/validation`
- 完了報告書: `reports/20260717-01_作業完了報告書.txt`

## 安全条件

`C:\fchart\fpac` と `C:\fchart\kabu.lst` は読み取り専用で参照します。
DB、ログ、報告書はWorkspace内にのみ作成します。
