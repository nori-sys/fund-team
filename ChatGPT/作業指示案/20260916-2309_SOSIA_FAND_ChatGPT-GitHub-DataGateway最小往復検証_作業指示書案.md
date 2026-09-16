# 20260916-2309 SOSIA FAND ChatGPT-GitHub-DataGateway最小往復検証 作業指示書案

> 状態: 未承認・未発行・実行禁止
>
> 本文書は `ChatGPT/作業指示案/` に保存する未承認案であり、Noriの正式承認前はCodexの実行根拠としない。

## 01）目的

既に完了しているData Gateway最小レファレンス実装を利用し、GitHubを受け渡し層として、次の最小往復を1回だけ成立させる。

`ChatGPT → GitHub → Codex → Data Gateway → GitHub → ChatGPT`

本作業の目的は恒久運用を決めることではなく、ChatGPTから出したデータ要求がGitHub経由でData Gatewayへ届き、結果がGitHub経由でChatGPTへ戻ることを、最小構成で実証することである。

## 02）今回の検証範囲

要求内容は固定する。

- 銘柄: トヨタ自動車 `7203`
- 足種: 日足
- 件数: 100取引日
- 系列: `daily_prices_raw`
- DB接続: READ ONLY
- 接続方式: `mode=ro&immutable=1`

既存のData Gateway最小実装を再利用し、DB schema、株価DB、既存Console仕様は変更しない。

## 03）最小フロー

1. ChatGPTがGitHub上へData Requestを作成する。
2. NoriがCodexチャットへ「要求を処理してください」と明示指示する。
3. CodexがGitHub上のData Requestを確認する。
4. Codexがローカルの既存Data Gatewayを実行する。
5. Data GatewayがSQLiteをREAD ONLYで参照し、固定Payloadを生成する。
6. CodexがData ResponseをGitHubへ保存する。
7. ChatGPTがGitHub上のData Responseを読み取り、要求と応答の一致を確認する。

今回は自動監視・自動検知を行わない。

## 04）GitHub上の受け渡し構造案

今回の検証専用として、次の最小構造を新設する案とする。

```text
DataGateway/
└─ Exchange/
   ├─ Requests/
   └─ Responses/
```

用途:

- `DataGateway/Exchange/Requests/` : ChatGPTが作成するData Request
- `DataGateway/Exchange/Responses/` : Codex/Data Gateway処理結果のData Response

この領域はGitHub上の受け渡し用ミラーであり、ローカル正本、DB正本、正式規程の保存場所ではない。

今回の作業指示が正式承認された場合に限り、この2フォルダを今回の検証用として作成してよい。

## 05）Data Request契約

RequestはJSON形式とする。

例:

```json
{
  "schema_version": "1.0",
  "request_id": "DG-TEST-001",
  "request_type": "price_history",
  "symbol": "7203",
  "timeframe": "1D",
  "limit": 100,
  "price_series": "daily_prices_raw",
  "purpose": "ChatGPT-GitHub-DataGateway minimal round-trip validation"
}
```

必須条件:

- `request_id` はRequestとResponseの対応確認に使用する。
- 今回は上記固定値から変更しない。
- 任意SQL、任意パス、任意コマンド等をRequestから実行できる仕様にしない。
- Requestはデータ要求だけを表し、Codex操作権限やシェル実行権限を与えない。

## 06）Data Response契約

ResponseもJSON形式とする。

最低限、次を含める。

```json
{
  "schema_version": "1.0",
  "request_id": "DG-TEST-001",
  "status": "success",
  "symbol": "7203",
  "timeframe": "1D",
  "requested_limit": 100,
  "returned_count": 100,
  "price_series": "daily_prices_raw",
  "data": [],
  "source": "fund_stock.db",
  "read_only": true
}
```

`data` は既存Gatewayで確認済みの価格Payload契約に従う。

エラー時は `status` を `error` とし、機密情報、ローカル絶対パス、認証情報を含めず、原因を簡潔に記録する。

## 07）実装・検証要件

### A. 既存Gateway再利用

- 既存の7203・日足・100本固定Gatewayを再利用する。
- 不要な新規Gatewayを作らない。
- DBアクセス方式 `mode=ro&immutable=1` を維持する。
- DB schema、DB内容を変更しない。

### B. DB保全

実行前後に次を確認する。

- `fund_stock.db` SHA-256一致
- `fund_stock.db-wal` 不在
- `fund_stock.db-shm` 不在
- `fund_stock.db-journal` 不在

### C. GitHub安全性

書込み前に現行 `GitHub連携運用.md` に従い、remote最新状態、先行・遅延・分岐、既存未commit変更、未追跡ファイル、stage対象を確認する。

既存資産を安易なpull、merge、rebase、reset、stashで処理しない。

必要に応じて一時branch／worktree等で対象変更を分離する。

### D. 公開安全性

GitHubへ置くRequest/Responseには次を含めない。

- 認証情報
- 個人情報
- ローカル絶対パス
- DB本体
- 秘密情報
- 不要な内部ログ

## 08）今回は実施しないこと

- GitHub自動監視
- Webhook
- GitHub Actions
- MCP
- APIサーバー
- 常駐プロセス
- Codex自動起動
- 任意SQL実行
- 任意コマンド実行
- 7203以外の銘柄対応
- 足種可変化
- 件数可変化
- 指標計算
- スクリーニング
- Console Command実装
- 恒久アーキテクチャ確定

## 09）独立監査

本作業がNoriに正式承認された場合、こうが実装・検証案を作成し、カンが独立監査する。

`要修正` の場合は、現行規程に従い、こうが承認済み範囲内で是正し、カンが再監査する。

`適合（承認可）` まで自律反復する。

## 10）成果物

最低限、次を提出する。

- Request JSON
- Response JSON
- GitHub上の保存先
- 使用した既存Gatewayの確認
- DB READ ONLY確認
- DB SHA-256実行前後比較
- WAL / SHM / journal確認
- RequestとResponseの `request_id` 一致確認
- `returned_count = 100` 確認
- 7203・日足・`daily_prices_raw` 一致確認
- GitHub commit ID
- カン最終監査結果
- 未決事項一覧（ある場合のみ）

## 11）完了条件

次をすべて満たした場合、この最小往復検証を完了とする。

1. ChatGPTが作成したRequestがGitHub上に存在する。
2. CodexがそのRequestを読み取って既存Data Gatewayを実行している。
3. ResponseがGitHub上に保存されている。
4. RequestとResponseの `request_id` が一致する。
5. Responseが7203・日足・100本・`daily_prices_raw` である。
6. DBは実行前後で不変である。
7. 既存未コミット・未追跡資産を毀損していない。
8. 禁止操作を行っていない。
9. カン最終判定が `適合（承認可）` である。
10. ChatGPTがGitHub上のResponseを読み取り、内容確認できる。

## 12）停止条件

次の場合は該当部分を停止し、Noriへ報告する。

- 既存Data Gatewayの仕様が今回の前提と一致しない。
- DB READ ONLYを保証できない。
- Requestから任意SQL・任意コマンド等を実行する必要が生じた。
- Public GitHubへ公開できない情報を扱う必要が生じた。
- 既存資産保全に疑義がある。
- GitHubの分岐・競合を安全に分離できない。
- 承認範囲を超える恒久仕様変更が必要になる。

---

本案はNori承認前の未承認作業指示案である。正式承認後のみCodex側の実行対象とする。
