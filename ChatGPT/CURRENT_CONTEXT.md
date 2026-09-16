# CURRENT_CONTEXT

## 現在の目的

SOSIA FANDを、ChatGPTとCodexの長所を併用するAI組織としてレファレンス設計し、最小実装から検証・改善する。

現在は、Data Gateway可変Request化 Phase 2で `timeframe` を `1D / 1W / 1M` に拡張しようとしたが、月足 `1M` の既存正式仕様が確認できず、正式作業指示の停止条件により実装開始前で停止している。

## 確定・合意した方向

- 対象リポジトリは `nori-sys/fund-team`、branchは `main`。
- ChatGPT側の「チャット」は、Nori直属のSOSIA FANDシステム構築アドバイザー。
- NoriをChatGPTとCodex間の途中中継役にしない方向で運用を改善する。
- Codex向け作業指示は目的型とし、承認済み範囲内では `こう → カン → こう修正 → カン再監査` を `適合（承認可）` まで自律反復する。
- カンは独立監査担当として起案・実装・是正を行わない。
- `適合（承認可）` はNoriの正式承認を代替しない。
- Data Gatewayは原則READ ONLY。DB接続は `mode=ro&immutable=1` を維持する。
- GitHubは共有・参照・受け渡し層であり、ローカルWorkspace正本を置き換えない。
- 自動監視、自動検知、自動起動、Webhook、GitHub Actions、APIサーバー、常駐化、MCPは現段階では未導入。起動はNoriの明示指示による手動トリガーを維持する。

## Data Gateway最小往復とPhase 1

`ChatGPT → GitHub → Codex → Data Gateway → GitHub → ChatGPT` の固定Request最小往復は成立済み。

Phase 1では次を完了済み。

- `symbol` 可変
- `limit` 可変
- `limit` 許可値: `20 / 50 / 100 / 200 / 500`
- `timeframe = 1D` 固定
- `price_series = daily_prices_raw` 固定
- SQLは銘柄・件数ともプレースホルダー束縛
- 任意SQL、任意テーブル、任意コマンドの指定不可
- 正常系・異常系の検証成功
- DB SHA-256前後一致
- WAL / SHM / journal副作用なし
- カン最終独立監査: `適合（承認可）`

Phase 1検証結果GitHub commit:

`8b57d089c388e3635403e6950ef41646ae441a1b`

## Phase 2の正式作業指示

正式発行済み:

`作業指示/20260917-0154_SOSIA_FAND_DataGateway可変Request化_Phase2_作業指示書.md`

正式発行commit:

`f9d43cafb9f6d7a4252d076deaad74885d3678e5`

目的は、Phase 1の安全条件を維持したまま `timeframe` を `1D / 1W / 1M` に拡張すること。

実装前に、週足・月足の既存テーブル／ビュー、生成方式、期間境界、OHLCV集計規則をローカル正本・現行DB・既存GatewayからREAD ONLYで確認することを必須条件とした。

## Phase 2停止結果

Codexは実装開始前確認で停止条件を検出し、実装・テスト作成・GitHub書込みを停止した。カンの独立確認判定は `要修正`。

### 確認できた既存週足仕様

- DB: `weekly_prices`、`timeframes`
- timeframe定義: `1W / WEEK / MONDAY_TO_SUNDAY`
- 期間: 月曜開始・日曜終了
- OHLCV:
  - 始値 = 最初の取引日の始値
  - 終値 = 最後の取引日の終値
  - 高値 = 期間最大
  - 安値 = 期間最小
  - 出来高 = 合計
- 生成元: `daily_prices_raw`
- 既存生成実装: `tools/fxx_sqlite/src/generate_timeframes.py`

### 月足 `1M` の未確定点

既存テーブル／ビュー、`timeframes` 定義、生成実装、期間境界、OHLCV規則、更新方式のいずれも確認できなかった。

DBの `timeframes` は `1W` のみで、月足名のDBオブジェクトも確認できていない。

このため、`1M` を実装するには新規の月足仕様を決める必要があり、正式指示の「推測実装禁止」と停止条件に該当した。

DBは読取り確認のみ。SHA-256は維持:

`c3fbe69d3a1d06942b040688765b723b67c756302049af787d7f243b83e74df6`

WAL / SHM / journalも不在。Phase 2停止時点ではGitHub commitなし。

## 次に進める作業

月足 `1M` の仕様を正式に決めるための小さな設計作業を行う。

最低限、Noriが判断・承認する必要がある項目:

1. 期間境界
2. OHLCV集計規則
3. 保存または生成方式
4. 更新方式

チャット側の暫定推奨案:

- 期間境界: 暦月の1日〜末日
- 始値: その月の最初の取引日の始値
- 終値: その月の最後の取引日の終値
- 高値: その月の最大高値
- 安値: その月の最小安値
- 出来高: その月の出来高合計
- 生成元: `daily_prices_raw`
- 保存方式: 週足と同様の専用テーブル方向を候補とする
- 更新方式: 日足更新後に対象月を再集計する方向を候補とする

ただし、保存方式・更新方式は既存週足運用との整合をCodex側で確認してから正式化するのが安全。

推奨手順:

1. 月足仕様の最小設計用の作業指示案を作成。
2. 既存週足実装を参考に、月足の保存先・更新方式まで最小設計。
3. カン監査。
4. Nori承認。
5. Phase 2修正版として実装再開。

## GitHub・作業指示運用

- `ChatGPT/作業指示案/` はChatGPTが作成する未承認Codex向け作業指示案の保存場所。
- Nori承認後のみ正式な `作業指示/` に発行する。
- 作業指示書発行時は、Codexチャットへそのまま貼れる短い指示文も同時表示する。
- GitHub書込み前にはremote最新、ahead/behind/divergence、未commit、未追跡、stage対象、公開安全性を確認する。
- dirty workspaceで安易なpull/merge/rebase/reset/stashを行わない。
- force push、remote変更、Git恒久設定変更、認証変更等はNoriの明示承認が必要。

## 未決事項

- 月足 `1M` の正式仕様。
- 月足の保存先・生成方式・更新方式。
- Phase 2修正版の正式内容。
- Data Gatewayの恒久アーキテクチャ。
- 自動検知・自動起動は現段階では導入しない方針を維持。
- 正規Workspace `main` とGitHub `main` の将来的な安全な同期方法。

## ChatGPTスレッド引き継ぎ

直前の詳細:

- `ChatGPT/HANDOVER/20260917-0221_DataGateway_Phase2月足仕様未確定停止.md`

本ファイルおよびHANDOVERは作業再開用コンテキストであり、正式規程・正式仕様・承認済み成果物を上書きしない。

## 注意事項

- GitHub上の規程文書はローカルWorkspace正本の参照用ミラー。
- 正式規程・ROLE・WORKFLOWの改定はNori承認が必要。
- 月足仕様は未承認であり、暫定推奨案を正式仕様として扱わない。
