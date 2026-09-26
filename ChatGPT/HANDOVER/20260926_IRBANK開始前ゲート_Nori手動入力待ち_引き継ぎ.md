# SOSIA FAND 司令 引き継ぎ

作成日：2026-09-26

## 1. 現在の最優先作業

IRBANK手動取得運用導入・0217再開の開始前ゲートを完了させる。

Codex側3文書の承認依頼一括化改定は正式更新・監査・GitHub同期まで完了済みで、未解決事項なし。

正式更新3文書：
- `AGENTS.md`
- `規程/ROLE/ROLE_FUND_こう_ChiefManager.md`
- `規程/WORKFLOW/監査運用.md`

GitHub commit：
`c6055c562c57fd714c075d7bc22d0bed7f6bfd67`

## 2. 1115正式発行

1115は、公開本体とGit管理外の非公開付属書から成る1件の正式指示として発行済み。

公開正式指示：
`作業指示/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_作業指示書.md`

GitHub反映：
- 正式指示書 commit：`ae8b320bb7b0c56644e43961971181b0693c1728`
- 途中報告 commit：`a99d688919bbf8cceaad56e585c05198b5bc69f1`

非公開付属書、許諾原文、実データはGitHub送信していない。

カンの正式発行後監査、GitHub反映後監査はいずれも「適合（承認可）」。

## 3. IRBANK専用領域

作成済み4子領域：
- `incoming`
- `current`
- `archive`
- `evidence`

親：
`D:\投資・トレード\株式\株式データ\IR BANK`

Codex実行主体には4子領域で読取・実行のみ許可。
親階層および既存年別フォルダのACLは変更前後一致。

## 4. sandbox外実行に関する確認

Noriが「Dドライブ配下に勝手にフォルダが作られた」と不安を感じたため、実行履歴・設定・ACLを確認した。

確認済み事実：
- sandbox mode：`workspace-write`
- writable rootにDドライブ対象は含まれない。
- 4子領域作成時は、Noriの明示承認後に `require_escalated` で実行。
- `auto_review` により、そのコマンド限りのsandbox外実行が許可された。
- 作成操作はPowerShellの `New-Item -ItemType Directory`、続けて `Set-Acl`。
- 実行主体は履歴上 `KING\nori`。
- 通常の現在実行主体 `KING\CodexSandboxOffline` は4子領域で読取・実行のみ。
- writable rootや恒久設定は変更されていない。
- 通常sandbox内実行ではDドライブへ書込み不可。

結論：
CodexにDドライブへの恒久書込み権限が付与されたわけではない。今回の作成は、Noriが承認した一時的なsandbox外実行によるもの。

今後の運用上の注意：
高リスクまたはsandbox外操作を承認する前に、
- 何を作成・変更するか
- どの操作がsandbox外で実行されるか
- 一時権限か恒久変更か
を明示してNoriが理解できる形にする。

## 5. IRBANK開始前ゲートの状態

現在判定：
「要修正（Noriの手動入力待ち）」

未了：
1. IRBANK個別許諾メール原文・添付の配置と照合
2. 非実データ `read_test_1115.txt` の配置と読取試験

実データ利用と0217再開は停止中。
EDINET・FChart未解消条件も維持。

## 6. Noriの次の作業

今は①②だけ行う。

### ① 許諾原文
`D:\投資・トレード\株式\株式データ\IR BANK\evidence`
へ、IRBANK個別許諾メール原文と添付一式を、元形式・元ファイル名を保って配置する。

### ② 読取試験
`D:\投資・トレード\株式\株式データ\IR BANK\current\read_test_1115.txt`
を配置する。

内容例：
```text
IRBANK read test
1115
This file contains no personal information and no investment data.
```

個人情報、IRBANK実データ、認証情報を含めない。

①②完了後、Codexへ次を伝える：
「①許諾原文一式と②read_test_1115.txtの配置が完了しました。照合・読取試験・カンの開始前再監査を再開してください。」

## 7. 次工程

開始前再監査が「適合（承認可）」になった後、Nori本人がIRBANKを手動取得する。

最大4企業年度対象：
- C1-FY2024：トヨタ自動車株式会社 2024年3月期
- C1-FY2025：トヨタ自動車株式会社 2025年3月期
- C2-FY2024：株式会社日立製作所 2024年3月期
- C2-FY2025：株式会社日立製作所 2025年3月期

現時点では③の取得・配置はまだ行わない。

## 8. 0217再開時の制約

IRBANK開始条件が成立しても、再判定するのは0217のIRBANK停止条件だけ。

維持：
- EDINET未解消条件
- FChart未解消条件
- accepted生成禁止
- hold解除禁止
- 654候補展開禁止
- 本番DB・コード・設定変更禁止

IRBANK適合だけで三者実数値比較可能と判定しない。
