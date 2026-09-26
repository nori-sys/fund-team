# CURRENT_CONTEXT

## 現在の最優先状態

Codex側3文書の承認依頼一括化改定は正式更新・監査・GitHub同期まで完了した。

正式更新済み：
1. `AGENTS.md`
2. `規程/ROLE/ROLE_FUND_こう_ChiefManager.md`
3. `規程/WORKFLOW/監査運用.md`

GitHub commit：
`c6055c562c57fd714c075d7bc22d0bed7f6bfd67`

3文書ともカン反映後独立監査「適合（承認可）」、GitHub版とローカル正本はblob一致、未解決事項なし。

## IRBANK / 0217 現在位置

1115作業は、公開本体とGit管理外の非公開付属書から成る1件の正式指示として発行済み。

公開正式指示：
`作業指示/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_作業指示書.md`

GitHub commit：
- 正式指示書：`ae8b320bb7b0c56644e43961971181b0693c1728`
- 途中報告：`a99d688919bbf8cceaad56e585c05198b5bc69f1`

カンの正式発行後・GitHub反映後監査はいずれも「適合（承認可）」。

IRBANK専用4子領域：
- `incoming`
- `current`
- `archive`
- `evidence`

上記4領域は作成済み。Codex実行主体には読取・実行のみを許可するACLを設定。親階層と既存年別フォルダのACLは変更前後一致。

## sandbox / ACL確認結果

Noriが、IR BANK配下にフォルダが作成されたことからCodexの書込み権限を懸念したため確認した。

確認結果：
- sandbox mode：`workspace-write`
- writable root：
  - `E:\AI ワークスペース\CODEX\ファンドチーム_Workspace`
  - Codex visualization領域
  - sandbox一時領域
- `D:\投資・トレード\株式\株式データ` とその配下は writable root に含まれない。
- 4子領域の作成は、Noriの明示承認後に `sandbox_permissions: require_escalated` で実行。
- 審査役 `auto_review` により、そのコマンド限りのsandbox外実行が許可された。
- 実行主体は履歴上 `KING\nori`。
- 現在の通常Codex実行主体は `KING\CodexSandboxOffline`。
- 現在、通常のsandbox内実行ではDドライブ対象へ書込み不可。
- writable rootや恒久設定は変更されていない。

結論：
今回のフォルダ作成は恒久的な書込み権限拡大ではなく、明示承認された一時的なsandbox外実行によるもの。通常時のsandbox境界は維持されている。

今後、高リスクまたはsandbox外操作の承認時には、何を作成・変更するか、どの操作がsandbox外か、一時か恒久かを承認前に明示する運用を重視する。

## IRBANK開始前ゲート

現時点は「要修正（Noriの手動入力待ち）」。

未了：
1. IRBANK個別許諾メール原文・添付の配置と照合
2. 非実データ `read_test_1115.txt` の配置と読取試験

そのため、実データ利用と0217再開は停止中。
EDINET・FChartの未解消条件も維持。

## Noriの次の手動作業

今は次の①②だけ実施する。

① 許諾原文一式
`D:\投資・トレード\株式\株式データ\IR BANK\evidence`
へIRBANK個別許諾メールの原文＋添付一式を、元形式・元ファイル名のまま配置する。

② 読取試験
`D:\投資・トレード\株式\株式データ\IR BANK\current\read_test_1115.txt`
を配置する。
内容は個人情報・IRBANK実データ・認証情報を含まない単純なダミーテキストでよい。

①②完了後、Codexへ以下で再開：
「①許諾原文一式と②read_test_1115.txtの配置が完了しました。照合・読取試験・カンの開始前再監査を再開してください。」

③ IRBANK手動取得（最大4企業年度）は、開始前監査適合後に実施する。現時点ではまだ取得・配置しない。

対象予定：
- トヨタ自動車株式会社 2024年3月期
- トヨタ自動車株式会社 2025年3月期
- 株式会社日立製作所 2024年3月期
- 株式会社日立製作所 2025年3月期

## 前段のデータ基盤状態

20260926-0217：
- EDINET取得 0書類・0件
- FChart原本内容アクセス 0 byte
- IRBANKデータ取得・保存0件
- accepted生成、hold解除、654候補展開、本番資産変更なし

0217は、IRBANK開始前ゲート適合後もIRBANK停止条件だけを再判定する。
EDINET・FChart未解消条件を維持し、IRBANK適合だけで三者実数値比較可能とは判定しない。

## スレッド引き継ぎ

詳細：
`ChatGPT/HANDOVER/20260926_IRBANK開始前ゲート_Nori手動入力待ち_引き継ぎ.md`
