# 20260722-01 FChart企業業績・財務DAT初期解析

## 構成

- `解析用コピー/`: 原本からコピーした解析用DATとkabu.lst
- `解析プログラム/`: 再実行可能なPython解析プログラム
- `解析結果/`: ファイル情報、ハッシュ、ダンプ、文字列、構造候補
- `比較表/`: kabu.lst照合、銘柄コード検索、4ファイル関係
- `報告書/`: SQLite化評価、未確定事項、完了報告

## 再実行

```powershell
& 'C:\Users\nori\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '作業履歴\20260722-01\解析プログラム\analyze_gyoseki_dat.py' --workdir '作業履歴\20260722-01'
```

## 注意

- 原本は `C:\fchart\gyoseki` と `C:\fchart\kabu.lst` を読み取り専用で参照した。
- 正式DBへの登録は行っていない。
- 解析結果は初期解析であり、財務項目名は未確定。
