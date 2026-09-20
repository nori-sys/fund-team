# CURRENT_CONTEXT

## 現在の状態

SOSIA FANDの基盤整備はいったん完了し、次スレッドから本来のシステム設計・改善へ戻る。

## 役割

- Nori: オーナー・最終意思決定者
- ChatGPT側「チャット」: SOSIA FANDシステム構築アドバイザー
- Codex側: 実装・検証・データ処理・分析その他の実作業
- カン: 独立監査担当
- GitHub: 共有・履歴・参照用ミラー層
- ローカルWorkspace: 規程、実装、重要資産の正本

## 正式化済みの主要運用

### 指示書・報告書運用
正式文書:
`規程/WORKFLOW/指示書・報告書運用.md`

- 作業指示案: `ChatGPT/作業指示案/`
- 正式作業指示書: `作業指示/`
- 作業履歴: `成果物/作業履歴/＜原正式作業指示書の基底名＞/`
- 正式作業指示書は完了後も移動しない
- 作業報告書は同一作業内で連番管理
- 既定の正式配置先を持つ成果物は作業履歴へ重複コピーしない

命名:
- 作業指示書: `YYYYMMDD-HHMM_プロジェクトID_件名_作業指示書.md`
- 1通目報告書: `YYYYMMDD-HHMM_プロジェクトID_件名_作業報告書.md`
- 2通目以降: `YYYYMMDD-HHMM-NN_プロジェクトID_件名_作業報告書.md`

SOSIA FAND project ID: `FAND`

### 定常GitHub受け渡し運用
正式反映済み:
- `AGENTS.md`
- `START_HERE.md`
- `規程/WORKFLOW/GitHub連携運用.md`
- `規程/WORKFLOW/指示書・報告書運用.md`
- `規程/WORKFLOW/フォルダ構成運用.md`

原則:
- 通常動作は規程に定義し、個別作業指示には作業固有条件と例外だけを書く
- ChatGPTは公開可能な未承認案を `ChatGPT/作業指示案/` と `ChatGPT/規程案/` に保存できる
- CodexはGitHubから対象ファイルだけをローカル同一パスへ限定取得する
- Workspace全体の無条件なgit pull、merge、rebase、reset、stash等を定常同期手段にしない
- Codexは公開可と承認された作業報告書、独立監査結果、検証結果、作業固有成果物をGitHub同一パスへ反映できる
- 公開可否不明、機密情報、個人情報、DB本体、大容量データ、ログ原本等は送信しない

### ChatGPT規程案領域
`ChatGPT/規程案/`
- 直下: AGENTS改定案、START_HERE改定案
- `ROLE/`: ROLE改定案
- `WORKFLOW/`: WORKFLOW改定案
- `ROOT/` は作らない

### ChatGPT運用領域
`ChatGPT/運用/`

ChatGPT自身の作業品質・文書作成方法その他のNori承認済み内部運用基準を保存する。
Codex/FUNDのROLE、権限、実行規則、正式WORKFLOWを拘束しない。

## 作業指示書案作成基準

正式配置:
`ChatGPT/運用/作業指示書案作成基準.md`

GitHub mirror commit:
`f49e24b04397fdbaa6ae2bb3685e958586420023`

標準構成:
1. 目的
2. 対象・範囲
3. 保存先
4. 制約・禁止事項
5. 成果物
6. 合格条件・完了条件
7. 公開区分
8. 通常運用からの例外

原則:
- 目的型指示書
- 必要以上に実現方法を固定しない
- 承認済み規程の通常手順を重複記載しない
- 公開区分はChatGPTが案を提示し、Nori承認で確定
- 不明事項を推測で補完しない
- 完了条件は客観的に判定可能にする
- 上位規程・Nori最新指示を本基準で上書きしない

## Codex貼り付け用指示文の表示

全プロジェクト共通で、Codexへそのまま貼り付ける指示文はコードブロックで表示する。

## GitHubミラー関連

正規Workspaceのmainとorigin/mainは分岐している。
通常pushを無理に行わず、必要時はNori明示承認による一時worktree個別例外で対象ファイルだけを安全に反映する。

直近の正式反映:
- `規程/WORKFLOW/フォルダ構成運用.md`
  commit: `0690d1619f83ba98d02fc5d751b6fc9ee8d03597`
- `ChatGPT/運用/作業指示書案作成基準.md`
  commit: `f49e24b04397fdbaa6ae2bb3685e958586420023`

## Data Gateway

Data Gateway可変Request化 Phase 2修正版は実装・検証・独立監査まで完了済み。
Gatewayは `1D / 1W / 1M` READ ONLY。
月足生成・差分更新・Payload契約・DB保全を検証済み。
カン最終監査: `適合（承認可）`。
未決事項なし。

## 次スレッド

基盤整備はいったん完了。
次スレッドではSOSIA FAND本来のシステム設計・改善へ戻る。

候補:
- SOSIA FANDコンソール改善
- DataGatewayの次段階
- 指標・スクリーニング機能
- インジケータ可変パラメータ入力
- データ基盤・Data Manager関連
- その他Noriが指定するSOSIA FAND本来のテーマ

過去に確定済みの規程・基盤を理由なく再議論しない。
