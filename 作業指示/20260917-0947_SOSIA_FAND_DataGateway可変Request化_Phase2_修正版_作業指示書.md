# SOSIA FAND Data Gateway可変Request化 Phase 2 修正版 作業指示書

> 状態：Nori承認済み・正式発行
> 承認日：2026-09-17 JST

## 01）目的

Phase 1の安全性を維持したまま、Data Gatewayの `timeframe` を `1D / 1W / 1M` から選択可能にする。

Nori承認済みの月足 `1M` 正式仕様に基づき、`1M` の生成・保存・READ ONLY参照を実装する。

参照仕様：

`成果物/20260917-0947_SOSIA_FAND_月足1M_正式仕様.md`

## 02）実装対象

### 月足DB

- `monthly_prices` を追加
- `timeframes` に `1M` を追加
- 月足生成元は `daily_prices_raw`
- OHLCVは承認済み月足仕様に従う

### 派生足生成処理

既存 `generate_timeframes.py` を基礎として、週足・月足で可能な範囲を共通化する。

ただし、既存週足の結果・仕様・更新方式を意図せず変更してはならない。

月足は日足更新後の手動処理で影響月のみ再集計する。

### Data Gateway

既存Gatewayを拡張し、次のtimeframeを許可する。

- `1D`
- `1W`
- `1M`

Gateway自身ではOHLCV再集計を行わず、DBに保存された派生足をREAD ONLYで参照する。

月足Payloadの `date` は `period_start` とする。

## 03）月途中データ

月途中の月足も返却可能とする。

DBへ `is_complete` は追加しない。

Consumerが `source_daily_max_date < period_end` から暫定状態を判定できる情報を保持する。

## 04）安全条件

維持する条件：

- Gateway DB接続はREAD ONLY
- GatewayからDB更新禁止
- SQLプレースホルダー束縛
- 任意SQL禁止
- 任意テーブル指定禁止
- 任意コマンド禁止
- `limit` 許可値維持
- `price_series` の自由指定禁止
- 自動監視・自動起動禁止

月足生成処理によるDB更新は、今回承認された月足派生データ生成に必要な範囲だけ許可する。

## 05）今回変更しないもの

- 既存週足ウォーターマーク方式
- Console
- ROLE
- WORKFLOW
- 自動監視
- Webhook
- GitHub Actions
- APIサーバー
- MCP
- 常駐処理
- 指標計算
- スクリーニング
- 汎用期間テーブルへの移行

## 06）検証

最低限、次を確認する。

1. `7203 / 1D`
2. `7203 / 1W`
3. `7203 / 1M`
4. 別銘柄の `1M`
5. 完了済み過去月のOHLCV
6. 進行中月の暫定月足
7. 許可外timeframe
8. 非許可limit
9. 存在しない銘柄
10. 月足再生成時の再現性
11. 月足差分更新
12. Gateway実行前後のDB不変性

月足値は `daily_prices_raw` から独立計算して照合する。

## 07）DB保全

Gateway検証では従来どおり、次を確認する。

- SHA-256
- WAL
- SHM
- journal

月足生成処理については、意図した `monthly_prices`、`timeframes` および生成管理情報以外が変更されていないことを確認する。

## 08）独立監査

こうが実装・検証し、カンが独立監査する。

`要修正` の場合は承認範囲内で `こう修正 → カン再監査` を行い、`適合（承認可）` まで自律反復する。

## 09）完了条件

- `1D / 1W / 1M` が正常に参照できる
- 月足が承認仕様どおり生成される
- 月途中データを判別可能
- 月足差分更新が再現可能
- 既存週足結果に意図しない変化がない
- GatewayはREAD ONLYを維持
- DB変更が承認範囲内に限定される
- 正常系・異常系検証に合格
- カン最終判定が `適合（承認可）`

## 10）停止条件

次の場合は推測せず停止する。

- 承認済み月足仕様と既存DB構造が両立しない
- 既存週足データへ破壊的変更が必要
- 想定外のDB migrationが必要
- GatewayのREAD ONLYを維持できない
- ROLE・WORKFLOW・Console変更が必要
- Public GitHubへ保存できない情報が必要
- 承認範囲を超える設計変更が必要
