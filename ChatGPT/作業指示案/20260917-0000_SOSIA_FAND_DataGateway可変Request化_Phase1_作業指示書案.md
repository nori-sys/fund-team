# 20260917-0000 SOSIA FAND Data Gateway可変Request化 Phase 1 作業指示書案

> 状態: 未承認・未発行・実行禁止
>
> 本文書は `ChatGPT/作業指示案/` に保存する未承認案であり、Noriの正式承認前はCodexの実行根拠としない。

## 01）目的

既に完了した固定Requestの最小往復検証を基礎として、Data GatewayのRequestを安全に可変化する。

Phase 1では、可変項目を `symbol` と `limit` の2項目だけに限定し、`timeframe=1D`、`price_series=daily_prices_raw` は固定のままとする。

起動方式は現行どおりNoriの明示指示による手動トリガーを維持し、自動監視、自動検知、自動起動は導入しない。

## 02）前提

- 既存の `ChatGPT → GitHub → Codex → Data Gateway → GitHub → ChatGPT` 最小往復は `DG-TEST-001` で成立済み。
- Data GatewayはSQLiteをREAD ONLYで参照する。
- DB接続方式 `mode=ro&immutable=1` を維持する。
- DB schema、DB内容、既存Console仕様は変更しない。
- GitHubは受け渡し層であり、ローカルWorkspace正本を置き換えない。

## 03）Phase 1で可変化する項目

### `symbol`

- Requestごとに変更可能とする。
- Request値をSQL文字列へ直接連結しない。
- Gateway側で既存DBに対象銘柄が存在することを検証してから処理する。
- 存在しない場合は正常なエラーResponseを返す。

### `limit`

- Requestごとに変更可能とする。
- 許可値方式とし、Phase 1では次の値だけを許可する。

`20 / 50 / 100 / 200 / 500`

- 許可値以外は実行せず、正常なエラーResponseを返す。

## 04）固定項目

Phase 1では次を変更可能にしない。

- `request_type = price_history`
- `timeframe = 1D`
- `price_series = daily_prices_raw`
- DB接続 = READ ONLY

任意SQL、任意テーブル名、任意パス、任意コマンド、任意式をRequestから指定できる仕様にしない。

## 05）Request契約

例:

```json
{
  "schema_version": "1.0",
  "request_id": "DG-20260917-001",
  "request_type": "price_history",
  "symbol": "7203",
  "timeframe": "1D",
  "limit": 50,
  "price_series": "daily_prices_raw"
}
```

### `request_id`

- Requestごとに一意とする。
- 命名形式は `DG-YYYYMMDD-NNN` を基本とする。
- Responseは同じ `request_id` を必ず返す。
- 同じ `request_id` の重複処理を安易に行わない。

## 06）入力検証

GatewayはRequestを命令として信用せず、処理前に少なくとも次を検証する。

- 必須フィールドの存在
- 未知の必須外フィールドの扱いが明確であること
- `schema_version` が対応版であること
- `request_type = price_history`
- `symbol` が対象DBに存在すること
- `timeframe = 1D`
- `limit` が許可値のいずれかであること
- `price_series = daily_prices_raw`

検証失敗時はDB取得処理を進めず、エラーResponseを生成する。

## 07）Response契約

成功時は最低限次を含める。

```json
{
  "schema_version": "1.0",
  "request_id": "DG-20260917-001",
  "status": "success",
  "symbol": "7203",
  "timeframe": "1D",
  "requested_limit": 50,
  "returned_count": 50,
  "price_series": "daily_prices_raw",
  "data": [],
  "source": "fund_stock.db",
  "read_only": true
}
```

データ不足等により `returned_count < requested_limit` となる場合の扱いは、既存DB実態を確認したうえで明示する。推測で100件等に補完しない。

## 08）エラーResponse

エラー時は例として次の形式とする。

```json
{
  "schema_version": "1.0",
  "request_id": "DG-20260917-002",
  "status": "error",
  "error_code": "INVALID_LIMIT",
  "message": "Requested limit is not allowed."
}
```

Phase 1では少なくとも次のエラーを区別する。

- `INVALID_REQUEST`
- `UNSUPPORTED_SCHEMA_VERSION`
- `SYMBOL_NOT_FOUND`
- `INVALID_LIMIT`
- `UNSUPPORTED_TIMEFRAME`
- `UNSUPPORTED_PRICE_SERIES`

GitHubへ返すエラーにローカル絶対パス、SQL本文、内部例外全文、認証情報、機密情報を含めない。

## 09）実装対象

既存Gatewayを拡張し、固定されていた `symbol` と `limit` をRequestから安全に受け取れるようにする。

不要な新Gatewayを並立させない。

実際の変更ファイルは、こうが現行実装を確認して必要最小限に特定する。対象外のDB、規程、ROLE、WORKFLOW、Consoleを変更しない。

## 10）検証ケース

最低限、次を検証する。

1. 正常系A: `7203 / limit=50`
2. 正常系B: 7203以外のDB存在銘柄 / `limit=200`
3. 異常系A: 存在しない銘柄
4. 異常系B: `limit=30` など非許可値
5. 異常系C: `timeframe` を `1W` 等へ変更したRequest
6. 異常系D: `price_series` を未許可値へ変更したRequest

正常系Bの銘柄は、こうがDBをREAD ONLYで確認し、存在を確認できる銘柄を1件選定してよい。

## 11）DB保全

検証前後で次を確認する。

- `fund_stock.db` SHA-256一致
- `fund_stock.db-wal` 不在
- `fund_stock.db-shm` 不在
- `fund_stock.db-journal` 不在

DB更新、schema変更、原本変更は禁止する。

## 12）GitHub受け渡し

- Request: `DataGateway/Exchange/Requests/`
- Response: `DataGateway/Exchange/Responses/`

起動は自動化しない。

運用は次のままとする。

`ChatGPTがRequest作成 → NoriがCodexへ処理指示 → Codexが処理 → ResponseをGitHub保存 → ChatGPTがResponse確認`

## 13）今回は実施しないこと

- 自動監視、自動検知、自動起動
- Webhook
- GitHub Actions
- MCP
- APIサーバー
- 常駐プロセス
- `timeframe` 可変化
- `price_series` 可変化
- 指標計算
- スクリーニング
- 任意SQL、任意コマンド
- 恒久アーキテクチャ確定

## 14）独立監査

Noriが本作業指示を正式承認した場合、こうが実装・検証し、カンが独立監査する。

`要修正` の場合は、承認済み範囲内でこうが是正し、カンが再監査する。

`適合（承認可）` まで現行規程に従って自律反復する。

## 15）成果物

最低限、次を提出する。

- 可変Request対応後のGateway変更内容
- 変更ファイル一覧
- 正常系・異常系のRequest JSON
- 各Response JSON
- 入力検証結果
- SQL安全性確認
- DB READ ONLY確認
- DB SHA-256前後比較
- WAL / SHM / journal確認
- GitHub commit ID（GitHubへ成果物を保存した場合）
- カン最終監査結果
- 未決事項一覧（ある場合のみ）

## 16）完了条件

次をすべて満たした場合、Phase 1完了とする。

1. `symbol` をRequestごとに変更できる。
2. `limit` を許可値内で変更できる。
3. `timeframe` と `price_series` は固定されている。
4. 正常系2件が正しいResponseを返す。
5. 異常系RequestがDB取得を進めず安全なエラーResponseを返す。
6. Request値から任意SQL、任意コマンドを実行できない。
7. DBが実行前後で不変である。
8. 既存未commit・未追跡資産を毀損していない。
9. カン最終判定が `適合（承認可）` である。
10. 未決事項がある場合は明示されている。

## 17）停止条件

次の場合は該当部分を停止し、Noriへ報告する。

- 既存Gatewayの構造上、今回の2項目だけを安全に可変化できない。
- SQL注入等の安全性を保証できない。
- DB READ ONLYを維持できない。
- 対象外のDB schema、規程、ROLE、WORKFLOW、Console変更が必要になる。
- Public GitHubへ公開できない情報を扱う必要がある。
- GitHub分岐・競合を安全に分離できない。
- 承認範囲を超える恒久仕様変更が必要になる。

---

本案はNori承認前の未承認作業指示案である。正式承認後のみCodex側の実行対象とする。
