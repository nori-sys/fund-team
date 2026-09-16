# CURRENT_CONTEXT

## 現在の目的

SOSIA FANDを、ChatGPTとCodexの長所を併用するAI組織としてレファレンス設計し、最小実装から検証・改善する。

## 確定・合意した方向

- 対象リポジトリは `nori-sys/fund-team`、branchは `main`。
- ChatGPT側の「チャット」は、Nori直属のSOSIA FANDシステム構築アドバイザー。
- 投資相談AIはChatGPT側とCodex側の両方に置き、現時点では一方へ統一しない。
- ChatGPT側の投資相談AIは「バフェット」。総合・俯瞰・対話・仮説整理を重視する。
- Codex側の投資相談AIは「ソロス」。データ重視・テクニカルアナリストとして、株価DB・指標・チャート・スクリーニング・コンソール連携を重視する。
- 旧Codex側バフェットROLEをそのまま前提にしない。今後はソロスへ再設計する方向。
- バフェットが従来担っていたAI間通信・永続記憶管理は、投資相談AIから分離する方向で見直す。
- ChatGPT Plusの範囲内でまず構築する。現時点ではProへのアップグレードやOpenAI API追加課金を前提にしない。
- MCPは将来候補だが、現段階の必須要件にはしない。
- ChatGPTから株価DBへ直接SQLを実行するのではなく、GitHubおよびCodex/Data Gatewayを橋渡しにする方式をレファレンス候補とする。
- Data Gatewayは原則読み取り専用で、事実・数値・計算を担当し、投資判断そのものは担当しない。
- Noriの方針として、完成形を議論だけで詰めすぎず、出来ることから最小レファレンス実装で進め、不具合があれば都度改善する。

## Data Gateway最小レファレンス実装

第1段階のローカル最小レファレンス実装は完了。

最終独立監査は **適合（完了承認可）**。

確認済み内容:

- 対象: トヨタ自動車 `7203`
- 足種: 日足
- 件数: 100取引日固定
- 対象系列: `daily_prices_raw`
- Python GatewayからSQLiteへREAD ONLY接続
- 接続方式: `mode=ro&immutable=1`
- `Data Request → Gateway → Response → gateway-response.js → 静的Browser Console` の経路を確認
- Consoleは7203・日足・100本固定
- 表示名とPayload対象が一致
- 実ブラウザーでローソク足・出来高チャートの正常表示を確認
- DB SHA-256は実行前後で一致
- WAL / SHM / journalの副作用なし

今回の `Python Data Gateway → ローカル生成データ → 静的Console` は最小レファレンスであり、恒久アーキテクチャではない。

## 次に進める作業

次の本命は、まだ未実装の

```text
ChatGPT
   ↓
GitHub
   ↓
Data Gateway
```

部分の設計・検証。

検討候補:

- GitHub上のData Request / Data Response / Console Command保存場所・形式
- ChatGPTからGitHubへの要求書込み権限と運用
- Codex側でGitHub要求を検知する方法
- 手動トリガーを維持するか、自動監視へ進むか
- 将来MCP/APIへ移行可能なRequest/Response仕様

## 未決事項

- ChatGPT側バフェットの正式なROLEまたはプロジェクト配置方法。
- Codex側ソロスの正式ROLE名・責務・権限。
- Data Gatewayの正式仕様化。
- GitHub上のData Request / Data Response / Console Commandの正式保存場所・形式。
- コンソール/GatewayがGitHub命令を検知・処理する正式方式。
- 旧 `ROLE_FUND_バフェット_Advisor.md` と関連WORKFLOWの正式改定範囲。
- AI間通信・永続記憶管理の新しい責任主体。

## ChatGPTスレッド引き継ぎ

直前の詳細は次を参照する。

- `ChatGPT/HANDOVER/20260916-1615_DataGateway最小実装完了.md`

その前段の設計経緯:

- `ChatGPT/HANDOVER/20260916-0110_投資相談AI配置_DataGateway検討.md`

ChatGPTの直接書込み範囲は、承認済み運用に基づき次に限定する。

- `ChatGPT/CURRENT_CONTEXT.md`
- `ChatGPT/HANDOVER/`

本ファイルおよびHANDOVERは作業再開用コンテキストであり、正式規程・正式仕様・承認済み成果物を上書きしない。

## 注意事項

- GitHub上の規程文書はローカルWorkspace正本の参照用ミラー。
- 正式規程・ROLE・WORKFLOWの改定は別途Nori承認が必要。
- 今回の完了承認は、GitHub自動連携、API化、常駐化、MCP、追加指標、スクリーニング等の承認を意味しない。
