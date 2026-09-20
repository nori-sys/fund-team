# SOSIA FAND 司令 スレッド引き継ぎ

作成日: 2026-09-20

## 今回のスレッドで完了したこと

ChatGPT↔GitHub↔Codexの受け渡し基盤を整備し、以下を正式化した。

- 指示書・報告書運用
- 定常GitHub受け渡し運用
- ChatGPT規程案の配置体系
- ChatGPT内部運用領域 `ChatGPT/運用/`
- `ChatGPT/運用/作業指示書案作成基準.md`

作業指示案の標準構成は、目的、対象・範囲、保存先、制約・禁止事項、成果物、合格条件・完了条件、公開区分、通常運用からの例外。

通常のGit安全手順、報告書命名、正規Workspace確認などは正式規程に定義済みであり、個別作業指示へ毎回重複記載しない。

## 重要な運用ルール

- 通常動作は規程、例外だけ個別指示
- GitHubは参照用ミラー、ローカルWorkspaceが正本
- GitHubからCodexへの受信は対象ファイル限定
- Workspace全体の無条件なpull/merge/rebase/reset/stashはしない
- 正規Workspace mainとorigin/mainは分岐状態が残る
- GitHub mirror更新に一時worktreeが必要な場合はNoriの明示的な個別例外承認を得る
- Codexへ貼る指示文は全プロジェクト共通でコードブロック表示する

## 直近GitHub反映

- `規程/WORKFLOW/フォルダ構成運用.md`
  commit: `0690d1619f83ba98d02fc5d751b6fc9ee8d03597`
- `ChatGPT/運用/作業指示書案作成基準.md`
  commit: `f49e24b04397fdbaa6ae2bb3685e958586420023`

## 次にやること

基盤整備は一旦完了。

次スレッドではSOSIA FAND本来のシステム設計・改善へ戻る。
Noriが次テーマを指定する。既存規程・基盤は必要時のみ参照し、目的なく再設計しない。
