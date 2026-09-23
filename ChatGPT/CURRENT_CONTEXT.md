# CURRENT_CONTEXT

## 現在の状態

SOSIA FANDの企業業績データ基盤は、FChart企業業績DAT解析からEDINET主系統候補の検証へ移行した。

直近では、EDINET企業業績データ取得・正規化の隔離最小PoCを実施し、複数回の独立監査・是正を経て最終的に **適合（承認可）** となった。

本番採用、本番DB投入、自動取得、対象拡大、FChart連携は未承認。

## 直近の正式作業

### 1400 EDINET・TDnet企業業績データ基盤調査

`作業指示/20260922-1400_FAND_EDINET・TDnet企業業績データ基盤調査_作業指示書.md`

結論：
- EDINET：確定財務・訂正履歴・XBRLの主系統候補
- TDnet：速報系統候補
- FChart / IRBank：比較仮説・補助検証候補
- DB投入、API正式採用、実装導入は未実施

GitHub公開commit：
`81b07dfd50944b2ab5948a2660496ff31e84a9b3`

### 0059 EDINET最小PoC仕様確定

`作業指示/20260923-0059_FAND_EDINET企業業績データ取得・正規化最小PoC仕様確定_作業指示書.md`

独立監査：
適合（承認可）

### 0213 EDINET隔離最小PoC

`作業指示/20260923-0213_FAND_EDINET企業業績データ取得・正規化_隔離最小PoC実施_作業指示書.md`

最終結果：
- 対象：トヨタ自動車 7203、1社・1事業年度・有価証券報告書1件
- 正規化候補：14件
- hold：0件
- RAW恒久保存：なし
- APIキー / URL永続化：なし
- 本番資産参照・書込み：なし
- 単体判定、dimension/member詳細、訂正観測、source_document属性を確認
- 識別子有効期間は推測せず未確定保持
- 独立再監査：**適合（承認可）**

## 現在の未完了事項

0213成果物のGitHub参照用ミラー反映が未実施。

理由：
- ローカル `main` と `origin/main` が分岐
- 正規Workspaceに既存未コミット変更が多数存在
- 公開候補3件は未stage・未送信

## 現在の運用課題

現行 `規程/WORKFLOW/GitHub連携運用.md` では、正規Workspace外の一時worktree利用はNoriの個別明示承認が必要な例外扱い。

そのため、安全な
`origin/main` 起点の隔離worktree → 対象のみcommit → fast-forward push
を使うたびにNoriが同じ許可指示をCodexへ入力する必要がある。

Noriはこの反復入力を削減したい。

## 次工程

個別指示で毎回回避するのではなく、`GitHub連携運用.md` の最小改定を検討する。

目的：
一定条件下の隔離worktreeを **標準安全手順** として扱えるようにし、安全性を維持したままNoriの個別許可を不要にする。

想定条件：
- 正規Workspaceに未コミット変更、未追跡資産、branch分岐等がある
- 個別作業指示で公開区分が確定済み
- 送信対象を明確に限定できる
- 最新 `origin/main` 起点の隔離worktree
- 対象ファイルだけをcommit
- push直前に親commitと最新 `origin/main` の一致確認
- fast-forward pushのみ
- force push / reset / rebase / remote変更 / Git設定変更 / 認証変更は禁止
- non-fast-forward、競合、対象分離不能、公開安全性疑義時のみ停止
- 正規Workspaceの既存未コミット変更・未追跡資産には触れない

WORKFLOW改定なので、案作成 → 独立監査 → Nori正式承認 → 正式発行で進める。

## スレッド引き継ぎ

詳細：
`ChatGPT/HANDOVER/20260923_GitHub隔離worktree運用改善_引き継ぎ.md`
