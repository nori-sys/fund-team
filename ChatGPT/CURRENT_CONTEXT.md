# CURRENT_CONTEXT

## 現在の目的

SOSIA FANDを、ChatGPTとCodexの長所を併用するAI組織としてレファレンス設計し、最小実装から検証・改善する。

現在は、Data Gateway第1段階完了後、`ChatGPT → GitHub → Data Gateway` の第2段階へ進む前に、Codex側の自律監査運用とGitHub同期安全ルールを整備している。

## 確定・合意した方向

- 対象リポジトリは `nori-sys/fund-team`、branchは `main`。
- ChatGPT側の「チャット」は、Nori直属のSOSIA FANDシステム構築アドバイザー。
- NoriをChatGPTとCodex間の途中中継役にしない方向で運用を改善する。
- 今後のCodex向け作業指示書は、目標、対象、制約、成果物、完了条件、停止条件を明確にし、Nori判断が不要な事項はCodex側で目標達成まで自律完結させる。
- 独立監査が指定される場合、承認済み範囲内で `こう → カン → こう修正 → カン再監査` を `適合（承認可）` まで反復する方向。
- カンは独立監査担当として起案・実装・是正を行わない。
- `適合（承認可）` はNoriの正式承認を代替しない。
- 投資相談AIはChatGPT側とCodex側の両方に置き、現時点では一方へ統一しない。
- ChatGPT側の投資相談AIは「バフェット」。Codex側は今後「ソロス」へ再設計する方向。
- Data Gatewayは原則READ ONLYで、事実・数値・計算を担当し、投資判断そのものは担当しない。
- MCP、Webhook、GitHub Actions、Codex自動起動等は現段階では未導入。

## Data Gateway最小レファレンス実装

第1段階のローカル最小レファレンス実装は完了済み。

最終独立監査は **適合（完了承認可）**。

確認済み内容:

- 対象: トヨタ自動車 `7203`
- 足種: 日足
- 件数: 100取引日固定
- 対象系列: `daily_prices_raw`
- Python GatewayからSQLiteへREAD ONLY接続
- 接続方式: `mode=ro&immutable=1`
- `Data Request → Gateway → Response → gateway-response.js → 静的Browser Console` の経路を確認
- 実ブラウザーでローソク足・出来高チャートの正常表示を確認
- DB SHA-256は実行前後で一致
- WAL / SHM / journalの副作用なし

今回の実装は最小レファレンスであり、恒久アーキテクチャではない。

## ChatGPT作業指示案領域

Nori承認により、ChatGPTが作成する未承認のCodex向け作業指示案の保存先として次を採用する方向。

`ChatGPT/作業指示案/`

ローカルWorkspaceにも作成済み。

`E:\AI ワークスペース\CODEX\ファンドチーム_Workspace\ChatGPT\作業指示案`

GitHubには用途説明のREADMEを反映済み。

GitHub commit:

`bf82548876746660a67b05f32408ef8dca139468`

この領域内の文書は未承認・未発行であり、Codexの実行根拠ではない。正式実行にはNori承認済み作業指示が必要。

## GitHub同期に関する新たな知見

ChatGPT側のGitHub直接更新により、GitHub `main` がCodexローカル `main` より先行し、Codexからのpushがnon-fast-forwardで拒否される事象を確認した。

安全にREADMEを反映するため、正規Workspaceを変更せず `origin/main` 起点の一時worktreeで対象commitのみを取り込み、fast-forward通常pushで解決した。

今後の標準候補:

- CodexはGitHub書込み前にremote最新状態を取得・確認する。
- ローカルbranchとremote branchの先行・遅延・分岐を確認する。
- 未コミット／未追跡変更がある場合、安易なpull、merge、rebase、reset、stash等を行わない。
- 必要に応じて一時branch／worktree等で隔離する。
- `ローカルmain = GitHub main` を常に仮定しない。

正規Workspaceの `main` は既存変更保全のため現時点でGitHub `main` と未同期。この不整合は意図的に残している。

## 現在の規程改訂作業

最新の作業指示書案:

`20260916-1820_SOSIA_FAND_自律運用_GitHub連携規程改訂_作業指示書案.md`

対象候補:

- `規程/ROLE/ROLE_FUND_こう_ChiefManager.md`
- `規程/WORKFLOW/監査運用.md`
- `規程/WORKFLOW/GitHub連携運用.md`
- `規程/WORKFLOW/フォルダ構成運用.md`

主な改訂目的:

1. コウ⇄カンの自律監査・修正ループ
2. Nori判断が必要な停止条件の明確化
3. `ChatGPT/作業指示案/` の正式な位置付け
4. ChatGPTの常設GitHub書込み許可範囲への同領域追加
5. GitHub書込み前のremote確認標準化
6. 既存未コミット資産の保全原則
7. ChatGPTとCodexのGitHub同時利用を前提にした分岐対策

まだ正式規程へは反映していない。

## 今後の作業指示書発行ルール

Noriの指示により、今後ChatGPTが作業指示書案を発行するときは、Markdownファイルと同時に、Codexチャットへそのまま貼れる指示文も表示する。

## 次に進める作業

1. 最新の規程改訂作業指示書案を `ChatGPT/作業指示案/` のGitHub運用へ載せる。
2. Nori承認後、Codexへ正式に渡す。
3. コウとカンで改訂案作成・監査・是正・再監査を `適合（承認可）` まで進める。
4. Nori最終承認後に正式規程へ反映する。
5. その後、本命の `ChatGPT → GitHub → Data Gateway` 最小レファレンス実装へ戻る。

## 未決事項

- ChatGPT側バフェットの正式ROLEまたはプロジェクト配置方法。
- Codex側ソロスの正式ROLE名・責務・権限。
- Data Gatewayの正式仕様化。
- GitHub上のData Request / Data Response / Console Commandの正式保存場所・形式。
- コンソール/GatewayがGitHub命令を検知・処理する正式方式。
- 旧 `ROLE_FUND_バフェット_Advisor.md` と関連WORKFLOWの正式改定範囲。
- AI間通信・永続記憶管理の新しい責任主体。
- 正規Workspace `main` とGitHub `main` の将来的な安全な同期方法。

## ChatGPTスレッド引き継ぎ

直前の詳細:

- `ChatGPT/HANDOVER/20260916-2002_自律監査運用_GitHub同期設計.md`

その前:

- `ChatGPT/HANDOVER/20260916-1615_DataGateway最小実装完了.md`

本ファイルおよびHANDOVERは作業再開用コンテキストであり、正式規程・正式仕様・承認済み成果物を上書きしない。

## 注意事項

- GitHub上の規程文書はローカルWorkspace正本の参照用ミラー。
- 正式規程・ROLE・WORKFLOWの改定はNori承認が必要。
- GitHub自動監視、API化、常駐化、Webhook、GitHub Actions、MCP等は現段階では未承認・未導入。
