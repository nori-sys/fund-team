# CURRENT_CONTEXT

## 現在の目的

ChatGPTのスレッド引き継ぎを、GitHubを利用して安全かつ継続的に行える運用へ移行する。

## 確定事項

- 対象リポジトリは `nori-sys/fund-team`。
- 対象branchは `main`。
- ChatGPTの直接書込み範囲は以下に限定する。
  - `ChatGPT/CURRENT_CONTEXT.md`
  - `ChatGPT/HANDOVER/`
- スレッド引き継ぎの発動条件は、Noriが新しいスレッドへの移行を明示した場合。
- 発動時は、毎回の個別承認を求めず、上記許可範囲でGitHubへ書込みを実施できる。
- 引き継ぎ情報は作業再開用コンテキストであり、正典・正式仕様・承認済み成果物を上書きしない。
- Codex側の正典、開始条件、権限体系は変更しない。

## 現在の作業状況

- `ChatGPT GitHubスレッド引き継ぎ運用・個別作業指示書` を作成済み。
- Noriによる明示承認済み。
- GitHub上の `ChatGPT/CURRENT_CONTEXT.md` 初期作成を実施。
- `ChatGPT/HANDOVER/` は、最初のスレッド移行時に引き継ぎMarkdownを作成することで開始する。

## 現行仕様・前提条件

- GitHubは共有・履歴・参照基盤として使用する。
- GitHub上の引き継ぎ情報は、ローカルWorkspaceの正式文書や重要資産の正本ではない。
- Publicリポジトリのため、公開可能な情報のみ保存する。
- 個人情報、認証情報、機密情報、非公開の投資口座情報などは保存しない。
- `AGENTS.md`、`START_HERE.md`、`規程/`、DB、コード、その他の正式文書・重要資産には、本運用を根拠として書き込まない。

## 未決事項・残作業

- 初回のスレッド移行時に `ChatGPT/HANDOVER/YYYYMMDD-HHMM_件名.md` を作成し、運用を実証する。
- 新しいスレッド開始時に `ChatGPT/CURRENT_CONTEXT.md` を参照して、作業再開性を確認する。

## 次スレッドで最初に行う作業

新しいスレッドへ移行した場合は、まず `ChatGPT/CURRENT_CONTEXT.md` を参照し、必要に応じて直前の `ChatGPT/HANDOVER/` を確認する。その後、重要な作業であれば関係する正式文書を別途確認する。

## 関連ファイル・参照情報

- `20260905-0157_ChatGPT_GitHubスレッド引き継ぎ運用_個別作業指示書.md`
- GitHub repository: `nori-sys/fund-team`
- branch: `main`

## 注意事項

- 本ファイルはChatGPTの作業用コンテキストであり、正式仕様書・運用規程・承認済み成果物を上書きしない。
- 正式文書との矛盾を発見した場合は、正式文書を優先する。
