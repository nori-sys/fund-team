# CURRENT_CONTEXT

## 現在の目的

SOSIA FANDを、ChatGPTとCodexの長所を併用するAI組織としてレファレンス設計し、最小実装から検証・改善する。

現在は、Data Gateway可変Request化 Phase 2について、月足 `1M` の最小設計・独立監査・Nori承認まで完了し、承認済み正式仕様とPhase 2修正版作業指示をGitHubへ発行した。次はCodexでPhase 2修正版の実装・検証・独立監査を行う段階。

## 確定・合意した方向

- 対象リポジトリは `nori-sys/fund-team`、branchは `main`。
- ChatGPT側の「チャット」は、Nori直属のSOSIA FANDシステム構築アドバイザー。
- NoriをChatGPTとCodex間の途中中継役にしない方向で運用を改善する。
- Codex向け作業指示は目的型とし、承認済み範囲内では `こう → カン → こう修正 → カン再監査` を `適合（承認可）` まで自律反復する。
- カンは独立監査担当として起案・実装・是正を行わない。
- `適合（承認可）` はNoriの正式承認を代替しない。
- Data GatewayはREAD ONLYを維持する。
- GitHubは共有・参照・受け渡し層であり、ローカルWorkspace正本を置き換えない。
- 自動監視、自動検知、自動起動、Webhook、GitHub Actions、APIサーバー、常駐化、MCPは現段階では未導入。起動はNoriの明示指示による手動トリガーを維持する。

## Data Gateway Phase 1

Phase 1は完了済み。

- `symbol` 可変
- `limit` 可変
- `limit` 許可値: `20 / 50 / 100 / 200 / 500`
- `timeframe = 1D` 固定
- `price_series = daily_prices_raw` 固定
- SQLプレースホルダー束縛
- 任意SQL・任意テーブル・任意コマンド指定不可
- 正常系・異常系検証成功
- DB SHA-256前後一致
- WAL / SHM / journal副作用なし
- カン最終独立監査: `適合（承認可）`

Phase 1検証結果commit:

`8b57d089c388e3635403e6950ef41646ae441a1b`

## Phase 2初版停止結果

初版正式指示:

`作業指示/20260917-0154_SOSIA_FAND_DataGateway可変Request化_Phase2_作業指示書.md`

初版発行commit:

`f9d43cafb9f6d7a4252d076deaad74885d3678e5`

実装前確認により、既存週足仕様は確認できたが月足 `1M` の既存正式仕様が存在せず、推測実装禁止の停止条件により実装開始前で停止した。

確認済み週足仕様:

- `weekly_prices`
- timeframe: `1W / WEEK / MONDAY_TO_SUNDAY`
- 月曜開始・日曜終了
- 生成元: `daily_prices_raw`
- O=最初の取引日、C=最後の取引日、H=max、L=min、V=sum
- 生成実装: `tools/fxx_sqlite/src/generate_timeframes.py`

## 月足 `1M` 最小設計

月足仕様最小設計をCodexで実施し、カン最終独立監査は `適合（承認可）`。

Noriはチャットの推奨4点をすべて承認した。

確定事項:

1. 保存先は専用 `monthly_prices`。
2. 月次Payloadの `date` は `period_start`。
3. `is_complete` 列は追加せず、`source_daily_max_date < period_end` の場合にConsumer側で暫定として扱う。
4. 既存週足ウォーターマーク方式の統一はPhase 2では行わず、別作業とする。

正式月足仕様:

- timeframe: `1M`
- 期間: 暦月1日〜末日
- 生成元: `daily_prices_raw`
- Open: 月内最初の取引日の始値
- High: 月内最高値
- Low: 月内最安値
- Close: 月内最後の取引日の終値
- Volume: 月内出来高合計
- 主キー候補: `(fchart_code, timeframe_code, period_start)`
- `timeframes` 登録: `1M / MONTH / 1 / CALENDAR_MONTH_FIRST_TO_LAST`
- Gatewayでは集計せず、保存済み派生月足をREAD ONLY参照
- 日足取込後、手動起動の派生足生成処理で影響月のみ再集計
- 差分境界: `last_generated_at <= imported_at < run_upper_bound`
- `run_upper_bound` は処理開始時のSQLite `CURRENT_TIMESTAMP` を固定
- UPSERTとウォーターマーク更新は同一トランザクションで成功時のみcommit

承認済み正式仕様:

`成果物/20260917-0947_SOSIA_FAND_月足1M_正式仕様.md`

仕様発行commit:

`8f30546a6a7e475ee109a3e65ed94f243574df66`

## Phase 2修正版

正式発行済み:

`作業指示/20260917-0947_SOSIA_FAND_DataGateway可変Request化_Phase2_修正版_作業指示書.md`

発行commit:

`027b3e8c3d87e5b698ba97470d301daf93094f0e`

実装対象:

- `monthly_prices` 追加
- `timeframes` に `1M` 追加
- 承認済み月足仕様に基づく生成・差分更新
- 既存Gatewayを `1D / 1W / 1M` 対応へ拡張
- Gateway自身ではOHLCV再集計しない
- Gateway READ ONLY維持

変更しない対象:

- 既存週足ウォーターマーク方式
- Console
- ROLE
- WORKFLOW
- 自動監視・自動起動
- Webhook / GitHub Actions / APIサーバー / MCP / 常駐処理
- 汎用期間テーブルへの移行

## 次に進める作業

CodexへPhase 2修正版の実行を指示する。

実施フロー:

`こう実装・検証 → カン独立監査 → 要修正ならこう是正 → カン再監査 → 適合（承認可） → Nori最終確認`

停止条件に該当する場合は推測せず停止する。

## GitHub・作業指示運用

- `ChatGPT/作業指示案/` は未承認案。
- Nori承認後のみ正式な `作業指示/` に発行する。
- 作業指示書発行時はCodexチャットへ貼る短い指示文も同時表示する。
- GitHubはローカルWorkspace正本を置き換えない。
- force push、remote変更、Git恒久設定変更、認証変更等はNoriの明示承認なしに行わない。

## 未決事項

- Phase 2修正版の実装・検証結果。
- Data Gatewayの恒久アーキテクチャ。
- 週足ウォーターマーク方式を将来同じ安全境界契約へ統一するか。
- 正規Workspace `main` とGitHub `main` の将来的な安全な同期方法。

## 注意事項

- GitHub上の文書はローカルWorkspace正本の共有・参照ミラーとして扱う。
- 正式規程・ROLE・WORKFLOW変更にはNori承認が必要。
- 月足 `1M` 仕様はNori承認済み。
