# 20260917-0154 SOSIA FAND Data Gateway可変Request化 Phase 2 作業指示書案

> 状態: 未承認・未発行・実行禁止
>
> 本文書は `ChatGPT/作業指示案/` に保存する未承認案であり、Noriの正式承認前はCodexの実行根拠としない。

## 01）目的

Phase 1で確立した `symbol`・`limit` 可変化を維持したまま、`timeframe` を安全に可変化し、`1D / 1W / 1M` をRequestから選択可能にする。

ただし、GitHubミラー上では週足・月足の現行生成方式・保存先・参照方法を確認できなかったため、Phase 2では実装前にCodexがローカル正本・現行DB・既存GatewayをREAD ONLYで確認し、既存方式を特定することを必須とする。

既存方式が確認できない場合は推測実装せず停止する。

## 02）前提

- Phase 1は完了済みで、`symbol` と `limit` は可変化済み。
- Phase 1の安全条件（READ ONLY、SQLプレースホルダー束縛、任意SQL・任意コマンド禁止）を維持する。
- `price_series = daily_prices_raw` はPhase 2でも固定する。
- 起動はNoriの明示指示による手動トリガーを維持する。
- 自動監視、自動検知、自動起動は導入しない。

## 03）実装前確認

こうは実装前に、ローカル正本・DB・既存GatewayをREAD ONLYで確認し、少なくとも次を特定する。

1. 週足・月足データがDBに既存テーブル／ビューとして存在するか。
2. 存在する場合、その正式なテーブル／ビュー名、列構成、価格系列、更新方式。
3. 存在しない場合、既存システム内に日足から週足・月足を集計する実装が存在するか。
4. 週足の期間境界、月足の期間境界、OHLCV集計規則。
5. 既存仕様との整合が確認できるか。

ここで不明・矛盾がある場合は、推測で週足・月足定義を作らず停止してNoriへ報告する。

## 04）Phase 2で可変化する項目

`timeframe` の許可値を次の3つとする。

- `1D`
- `1W`
- `1M`

許可値以外は処理せず、`UNSUPPORTED_TIMEFRAME` の安全なエラーResponseを返す。

## 05）維持する可変・固定項目

### 可変

- `symbol`
- `limit`
- `timeframe`

### 固定

- `request_type = price_history`
- `price_series = daily_prices_raw`
- DB接続 = READ ONLY
- `limit` 許可値 = `20 / 50 / 100 / 200 / 500`

## 06）Request契約

例:

```json
{
  "schema_version": "1.0",
  "request_id": "DG-20260917-101",
  "request_type": "price_history",
  "symbol": "7203",
  "timeframe": "1W",
  "limit": 50,
  "price_series": "daily_prices_raw"
}
```

既存の `request_id`、重複処理、入力検証ルールはPhase 1を継承する。

## 07）Response契約

成功ResponseではRequestの `timeframe` をそのまま返し、`returned_count` は実際の返却件数と一致させる。

```json
{
  "schema_version": "1.0",
  "request_id": "DG-20260917-101",
  "status": "success",
  "symbol": "7203",
  "timeframe": "1W",
  "requested_limit": 50,
  "returned_count": 50,
  "price_series": "daily_prices_raw",
  "data": [],
  "source": "fund_stock.db",
  "read_only": true
}
```

週足・月足の各OHLCVがどの期間を代表するかは、実装前確認で確定した現行仕様に従う。

## 08）実装方針

- 既存Gatewayを拡張し、不要な新Gatewayを並立させない。
- Phase 1の入力検証・SQL安全性を維持する。
- Request値から任意テーブル名、任意SQL、任意式、任意コマンドを指定できるようにしない。
- 週足・月足の既存テーブル／ビューがある場合は、それをREAD ONLYで利用することを優先する。
- 既存DBに週足・月足がなく、既存の承認済み集計ロジックがある場合のみ、そのロジックの再利用を検討する。
- 新しい週足・月足生成仕様を今回の作業だけで独自に定義してはならない。

## 09）検証ケース

最低限、次を検証する。

1. `7203 / 1D / limit=50`
2. `7203 / 1W / limit=50`
3. `7203 / 1M / limit=20`
4. 7203以外のDB存在銘柄 / `1W / limit=200`
5. 許可外timeframe（例 `4H`）
6. Phase 1の異常系（存在しない銘柄、非許可limit、未許可price_series）が引き続き安全にエラーになること

週足・月足の値は、既存仕様に基づく独立計算または既存正本との照合により検証する。

## 10）DB保全

Phase 1と同じく検証前後で次を確認する。

- `fund_stock.db` SHA-256一致
- `fund_stock.db-wal` 不在
- `fund_stock.db-shm` 不在
- `fund_stock.db-journal` 不在

DB更新、schema変更、原本変更は禁止する。

## 11）GitHub受け渡し

- Request: `DataGateway/Exchange/Requests/`
- Response: `DataGateway/Exchange/Responses/`

運用は引き続き次とする。

`ChatGPTがRequest作成 → NoriがCodexへ処理指示 → Codexが処理 → ResponseをGitHub保存 → ChatGPTがResponse確認`

## 12）今回は実施しないこと

- `price_series` 可変化
- 自動監視、自動検知、自動起動
- Webhook
- GitHub Actions
- MCP
- APIサーバー
- 常駐プロセス
- 指標計算
- スクリーニング
- 任意SQL、任意コマンド
- DB schema変更
- 恒久アーキテクチャ確定

## 13）独立監査

Noriが本作業指示を正式承認した場合、こうが調査・実装・検証し、カンが独立監査する。

`要修正` の場合は、承認済み範囲内でこうが是正し、カンが再監査する。

`適合（承認可）` まで現行規程に従って自律反復する。

## 14）成果物

最低限、次を提出する。

- 週足・月足の現行仕様確認結果
- 使用したテーブル／ビュー／既存集計実装の特定結果
- Gateway変更内容
- 変更ファイル一覧
- 正常系・異常系Request/Response
- 週足・月足OHLCV検証結果
- SQL安全性確認
- DB READ ONLY確認
- DB SHA-256前後比較
- WAL / SHM / journal確認
- GitHub commit ID（GitHubへ成果物を保存した場合）
- カン最終監査結果
- 未決事項一覧（ある場合のみ）

## 15）完了条件

次をすべて満たした場合、Phase 2完了とする。

1. `timeframe` が `1D / 1W / 1M` の許可値で選択できる。
2. 週足・月足の参照・集計方法が既存仕様に基づいている。
3. 正常系の各timeframeが正しいResponseを返す。
4. 許可外timeframeが安全なエラーResponseを返す。
5. Phase 1の `symbol`・`limit` 可変化と安全性が維持されている。
6. Requestから任意SQL・任意テーブル・任意コマンドを実行できない。
7. DBが実行前後で不変である。
8. Console、規程、ROLE、WORKFLOWを無断変更していない。
9. カン最終判定が `適合（承認可）` である。
10. 未決事項がある場合は明示されている。

## 16）停止条件

次の場合は該当部分を停止し、Noriへ報告する。

- 週足・月足の現行仕様を特定できない。
- ローカル正本とDB実態に重要な不一致がある。
- 新規の週足・月足仕様を決めないと実装できない。
- DB schema変更や書込みが必要になる。
- SQL安全性またはREAD ONLYを維持できない。
- 対象外の規程、ROLE、WORKFLOW、Console変更が必要になる。
- GitHub分岐・競合を安全に分離できない。
- Public GitHubへ公開できない情報を扱う必要がある。

---

本案はNori承認前の未承認作業指示案である。正式承認後のみCodex側の実行対象とする。
