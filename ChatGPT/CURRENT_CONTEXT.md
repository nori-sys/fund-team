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

## 想定構造

```text
Nori
├─ ChatGPT「チャット」
│   └─ SOSIA FANDシステム構築アドバイザー
│
├─ ChatGPT「バフェット」
│   └─ 総合・俯瞰・対話型の投資相談
│
└─ Codex「ソロス」
    └─ データ・テクニカル・チャート・コンソール連携
         ↓
      Data Gateway
         ↓
      株価DB
```

ChatGPT側とCodex側の共有・受け渡しにはGitHubを利用する。

## Data Gatewayの基本方針

- ChatGPT側はSQLではなく、必要な情報をData Requestとして要求する。
- Codex/Data Gatewayが株価DBから必要なデータを取得する。
- 取得結果は標準化したData Responseとして返す。
- DB更新・削除・構造変更はGatewayの通常責務に含めない。
- 将来MCPやAPIへ切り替える場合にも、Request/Response仕様を再利用できる形を目指す。

## コンソール連携の検討状況

- ChatGPT PlusだけでChatGPT本体をSOSIA FANDコンソールへ埋め込むことは前提にしない。
- APIによる専用チャットUIは別課金になるため、現段階では採用しない。
- 代替として、ChatGPT → GitHub → ローカルGateway/Console のコマンド中継を検討している。
- 例として、ChatGPT側バフェットから「トヨタの日足チャートをコンソールに表示して」と要求し、GitHub上の命令をコンソール側が処理する構成は技術的に可能と見込んでいる。
- ただし、まだ実装・正式仕様化はしていない。

## 次に進める作業

最小レファレンス設計を具体化する。

第一候補は「トヨタの日足チャート表示」を題材に、次の最小経路を確認すること。

```text
ChatGPT / GitHub
    ↓
Codex / Data Gateway
    ↓
株価DB
    ↓
SOSIA FAND Console
```

この実装・検証を通じて、必要な通信形式、権限、エラー処理、コンソール側の受信方式を決めていく。

## 未決事項

- ChatGPT側バフェットの正式なROLEまたはプロジェクト配置方法。
- Codex側ソロスの正式ROLE名・責務・権限。
- Data Gatewayの正式仕様。
- GitHub上のData Request / Data Response / Console Commandの保存場所・形式。
- コンソールがGitHub命令を検知・処理する方法。
- 旧 `ROLE_FUND_バフェット_Advisor.md` と関連WORKFLOWの正式改定範囲。
- AI間通信・永続記憶管理の新しい責任主体。

## ChatGPTスレッド引き継ぎ

直前の詳細は次を参照する。

- `ChatGPT/HANDOVER/20260916-0110_投資相談AI配置_DataGateway検討.md`

ChatGPTの直接書込み範囲は、承認済み運用に基づき次に限定する。

- `ChatGPT/CURRENT_CONTEXT.md`
- `ChatGPT/HANDOVER/`

本ファイルおよびHANDOVERは作業再開用コンテキストであり、正式規程・正式仕様・承認済み成果物を上書きしない。

## 注意事項

- GitHub上の規程文書はローカルWorkspace正本の参照用ミラー。
- Codex側規程の正式改定はまだ行っていない。
- 正式変更時は必要に応じてローカル正本との一致確認が必要。
