# ChatGPT GitHubスレッド引き継ぎ運用・引き継ぎメモ

## 現在の目的

ChatGPTのスレッド引き継ぎを、GitHubを利用して安全かつ継続的に行える運用として実証する。

## 今回の確定事項

- 対象リポジトリは `nori-sys/fund-team`。
- 対象branchは `main`。
- ChatGPTの直接書込み範囲は以下に限定する。
  - `ChatGPT/CURRENT_CONTEXT.md`
  - `ChatGPT/HANDOVER/`
- スレッド移行をNoriが明示した場合、ChatGPTは毎回の個別承認なしで上記範囲に引き継ぎ情報を書き込める。
- 引き継ぎ情報は作業用コンテキストであり、正典・正式仕様・承認済み成果物を上書きしない。
- Codex側の正典、開始条件、権限体系は変更しない。
- `ChatGPT GitHubスレッド引き継ぎ運用・個別作業指示書` はNori承認済み。

## 現在の作業状況

- `ChatGPT/CURRENT_CONTEXT.md` の初期作成済み。
- 今回、初回の実運用として本HANDOVERファイルを作成する。
- 次スレッドではGitHub上の `ChatGPT/CURRENT_CONTEXT.md` を読み込み、作業再開性を確認する。

## 現行仕様・前提条件

- GitHubは共有・履歴・参照基盤として利用する。
- GitHub上の引き継ぎ情報はローカルWorkspaceの正式文書や重要資産の正本ではない。
- Publicリポジトリのため、公開可能な情報のみ保存する。
- 個人情報、認証情報、機密情報、非公開の投資口座情報等は保存しない。
- `AGENTS.md`、`START_HERE.md`、`規程/`、DB、コード、その他の正式文書・重要資産には、本運用を根拠として書き込まない。

## 未決事項・残作業

- 新しいスレッド開始時に、ChatGPTが `ChatGPT/CURRENT_CONTEXT.md` を正しく参照できるか確認する。
- 必要に応じて直前の `ChatGPT/HANDOVER/` を参照し、前スレッドの未決事項を復元できるか確認する。
- 実証結果に問題があれば、ChatGPT側の引き継ぎ運用のみを調整する。Codex側規程へは自動波及させない。

## 次スレッドで最初に行う作業

1. GitHub上の `ChatGPT/CURRENT_CONTEXT.md` を読む。
2. 必要に応じて本HANDOVERを参照する。
3. 「GitHubを使ったChatGPTスレッド引き継ぎが正常に成立したか」を確認する。
4. 問題がなければ通常のSOSIA FAND作業へ戻る。

## 関連ファイル・参照情報

- `ChatGPT/CURRENT_CONTEXT.md`
- `ChatGPT/HANDOVER/20260905-0203_ChatGPT_GitHubスレッド引き継ぎ運用.md`
- `20260905-0157_ChatGPT_GitHubスレッド引き継ぎ運用_個別作業指示書.md`
- Repository: `nori-sys/fund-team`
- Branch: `main`

## 注意事項

- 本文書は作業再開用コンテキストであり、正式文書を上書きしない。
- 正式文書との矛盾を発見した場合は正式文書を優先する。
