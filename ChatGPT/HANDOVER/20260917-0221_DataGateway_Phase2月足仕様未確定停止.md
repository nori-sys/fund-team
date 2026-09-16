# SOSIA FAND 司令 引き継ぎ

作成: 2026-09-17 02:21 JST

## 現在地点

Data Gateway可変Request化 Phase 2は、実装前確認で月足 `1M` の既存正式仕様を確認できず停止した。

正式作業指示:

`作業指示/20260917-0154_SOSIA_FAND_DataGateway可変Request化_Phase2_作業指示書.md`

正式発行commit:

`f9d43cafb9f6d7a4252d076deaad74885d3678e5`

## Phase 1

Phase 1は完了済み。`symbol` と `limit` を安全に可変化し、`timeframe=1D`、`price_series=daily_prices_raw`、READ ONLYを維持。

検証commit:

`8b57d089c388e3635403e6950ef41646ae441a1b`

カン最終独立監査は `適合（承認可）`。

## Phase 2停止結果

カン独立確認判定: `要修正`

### 確認できた週足仕様

- DB: `weekly_prices`、`timeframes`
- timeframe: `1W / WEEK / MONDAY_TO_SUNDAY`
- 期間: 月曜開始・日曜終了
- 始値: 最初の取引日の始値
- 終値: 最後の取引日の終値
- 高値: 期間最大
- 安値: 期間最小
- 出来高: 合計
- 生成元: `daily_prices_raw`
- 既存生成実装: `tools/fxx_sqlite/src/generate_timeframes.py`

### 月足 `1M`

次の既存仕様を確認できなかった。

- 既存テーブル／ビュー
- `timeframes` 定義
- 生成実装
- 期間境界
- OHLCV規則
- 更新方式

DBの `timeframes` は `1W` のみ。月足名のDBオブジェクトも確認できなかった。

このため、`1M` 実装には新規仕様決定が必要となり、正式指示の推測実装禁止・停止条件に該当。実装・テスト作成・GitHub書込みは停止。

DB SHA-256は維持:

`c3fbe69d3a1d06942b040688765b723b67c756302049af787d7f243b83e74df6`

WAL / SHM / journal不在。

## 次スレッドの最初の作業

月足 `1M` の正式仕様決定に進む。

最低限の決定項目:

1. 期間境界
2. OHLCV集計規則
3. 保存または生成方式
4. 更新方式

チャット暫定推奨案:

- 暦月の1日〜末日
- O = 月内最初の取引日の始値
- H = 月内最大高値
- L = 月内最小安値
- C = 月内最後の取引日の終値
- V = 月内出来高合計
- 生成元 = `daily_prices_raw`
- 保存方式 = 週足と同様の専用テーブル方式を候補
- 更新方式 = 日足更新後に対象月を再集計する方式を候補

ただし、保存方式・更新方式は既存週足実装との整合をCodexで確認したうえで正式化する。

推奨フロー:

`月足仕様最小設計の作業指示案 → Nori承認 → Codex調査・設計 → カン監査 → Nori正式仕様承認 → Phase 2修正版`。

## 維持する運用方針

- 自動監視、自動検知、自動起動、Webhook、GitHub Actions、APIサーバー、常駐化、MCPは導入しない。
- 起動はNori明示指示の手動トリガー。
- GitHubは共有・受け渡し層。ローカルWorkspace正本を置き換えない。
- `ChatGPT/作業指示案/` は未承認案、`作業指示/` はNori承認済み正式指示。
- 作業指示発行時はCodexチャット貼付用短文も同時表示する。

この引き継ぎは作業再開用コンテキストであり、正式規程・正式仕様・承認済み成果物を上書きしない。
