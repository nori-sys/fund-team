# CURRENT_CONTEXT

## 現在の目的

ChatGPT側の役割再定義を完了し、次に今回の変更がCodex側の現行規程へ与える影響を分析したうえで、必要な規程改定案を作成する。

## 確定事項

- 対象リポジトリは `nori-sys/fund-team`。
- 対象branchは `main`。
- ChatGPT側AIの名称は「チャット」とする。
- チャットは、SOSIA FANDにおけるNori直属の**システム構築アドバイザー**とする。
- チャットは相場予測、個別株売買判断、投資戦略相談、銘柄選定等を主担当としない。
- チャットの主担当は、SOSIA FANDのシステム設計、AI組織設計、コンソール改善、規程改定案、ROLE・WORKFLOW改善案、Codex向け作業指示案、成果物レビュー、GitHub連携・引き継ぎ方式の改善とする。
- 投資分析・株式DBを使用する専門的な投資評価はCodex側の投資担当AI・専門担当の領域とする。
- Codex側のバフェットは廃止せず、今後は株式DB等へアクセスできる投資戦略・分析担当として再設計する方向で検討する。
- ChatGPT側のプロジェクト設定で、Codex側の実行規則を重複定義しない。
- 正式情報が必要な場合、ChatGPTはGitHub上の `AGENTS.md`、`START_HERE.md`、`規程/ROLE/`、`規程/WORKFLOW/`、`作業指示/` 等の参照用ミラーを確認する。
- GitHub上の規程はローカルWorkspace正本の参照用ミラーであり、正本ではない。
- 安全性を損なわない範囲で、トークン節約に寄与する方法がある場合は提案する。
- ChatGPT会話スレッド引き継ぎとCodex側のスレッド／タスク引き継ぎは別系統として扱う。

## ChatGPTプロジェクト設定

ChatGPT側のプロジェクト設定指示文を全面再構築した。

主な内容：

- チャット＝SOSIA FAND システム構築アドバイザー
- ChatGPTとCodexの役割分離
- 投資判断をChatGPTの主担当外とする
- Codexの実行規則はCodex側規程へ委譲
- GitHub参照用ミラーとローカル正本の区別
- 正本確認が重要でChatGPT自身では確認不能な場合はCodex側で確認
- GitHub書込みは承認済み個別作業指示その他の正式な権限範囲に限定
- 重要文書は現行の監査・承認手順に従う
- ChatGPT専用GitHubスレッド引き継ぎ方式を維持

Markdown成果物として `20260905_SOSIA_FAND_ChatGPTプロジェクト設定.md` を作成済み。

## Codex側との現時点の関係

現在のCodex側規程では、`ROLE_FUND_バフェット_Advisor.md` が「オーナー直属アドバイザー兼主担当AI」「AI間通信・永続記憶管理」等を担っており、今回決めた将来像（投資戦略・DB活用担当）とはずれがある。

また `規程/WORKFLOW/AI間通信運用.md` でも、バフェットが通信管理・記憶管理を担う定義があるため、バフェットROLE変更時には連動確認が必要。

現行 `ROLE_INDEX.md` では、バフェット、こう、カズ、カンが現行ROLEとして掲載されている。

## 未決事項・残作業

次の作業は、今回のChatGPT側変更をCodex側規程へ反映するための**影響分析**。

主な確認候補：

- `規程/ROLE/ROLE_FUND_バフェット_Advisor.md`
- `規程/ROLE/ROLE_INDEX.md`
- `規程/WORKFLOW/AI間通信運用.md`
- `規程/WORKFLOW/GitHub連携運用.md`
- 必要な場合のみ `AGENTS.md`
- 必要な場合のみ `START_HERE.md`
- その他、バフェットの旧役割・ChatGPT代替Advisor思想を参照している文書

まだCodex側規程の変更・正式改定は実施していない。

## 次スレッドで最初に行う作業

1. GitHub上の `ChatGPT/CURRENT_CONTEXT.md` を読む。
2. 必要に応じて直前の `ChatGPT/HANDOVER/20260905-0303_ChatGPT役割再構築_Codex規程改定前.md` を参照する。
3. Codex側の現行規程を検索し、今回のChatGPT役割変更の影響箇所を網羅的に洗い出す。
4. 各文書について「変更必要／確認のみ／変更不要」を分類する。
5. 規程改定案を作る前に、影響分析結果をNoriへ提示する。

## ChatGPTスレッド引き継ぎ運用

- ChatGPTの直接書込み範囲は次に限定する。
  - `ChatGPT/CURRENT_CONTEXT.md`
  - `ChatGPT/HANDOVER/`
- Noriが新しいChatGPTスレッドへの移行を明示した場合、上記範囲で毎回の個別承認なしに引き継ぎ情報を書き込める。
- Publicリポジトリへ保存できない情報は記載しない。
- 引き継ぎ情報は作業再開用コンテキストであり、正典・正式仕様・承認済み成果物を上書きしない。

## 関連ファイル・参照情報

- `ChatGPT/CURRENT_CONTEXT.md`
- `ChatGPT/HANDOVER/20260905-0303_ChatGPT役割再構築_Codex規程改定前.md`
- `ChatGPT/HANDOVER/20260905-0203_ChatGPT_GitHubスレッド引き継ぎ運用.md`
- `規程/ROLE/ROLE_FUND_バフェット_Advisor.md`
- `規程/ROLE/ROLE_INDEX.md`
- `規程/WORKFLOW/AI間通信運用.md`
- `規程/WORKFLOW/GitHub連携運用.md`
- `AGENTS.md`
- `START_HERE.md`
- GitHub repository: `nori-sys/fund-team`
- branch: `main`

## 注意事項

- 本ファイルはChatGPTの作業用コンテキストであり、正式仕様書・運用規程・承認済み成果物を上書きしない。
- Codex側規程の正式改定はまだ行っていない。
- 正式文書との矛盾を発見した場合は正式文書を優先する。
