# CURRENT_CONTEXT

## 現在の状態

20260926-0000「FAND EDINET・FChart・IRBANK三者突合による許容差採用条件検証」は完了。
- 固定8セルは全てhold維持
- 新規accepted 0
- 実数値比較0組
- GitHub公開7文書 commit：a8e8c2add75e5319e29550cd82c8918e8ffa78cf

20260926-0114「FAND EDINET・FChart・IRBANK三者比較成立条件未確定事項解消」も完了承認済み。
- 固定8セルは全て実数値比較開始不可
- EDINET、FChart、IRBANKそれぞれに前提条件未確定が残った
- カン最終監査は適合（承認可）

20260926-0217「FAND 固定8セル三者比較・最小追加証拠取得」は正式発行・開始前ゲート適合まで進んだが停止条件に到達。
- EDINET取得 0書類・0件
- FChart原本内容アクセス 0 byte
- IRBANKは利用条件確認のみ、データ取得・保存0件
- 固定8セルは比較開始不可のまま
- accepted生成、hold解除、654候補展開、本番資産変更なし
- カン最終独立監査は適合（承認可）

## IRBANK個別許諾

NoriがIRBANK運営事務局から個別許諾を取得。

許諾範囲：
- Noriによる手動ダウンロード・社内保存：可
- OpenAI Codex等のAIによる読取り・比較・分析：可
- 法人内部の投資分析利用：可
- 自動取得・スクレイピング：禁止
- 原データ・加工データの二次配布・外部公開：禁止
- AIモデル学習用データセット利用：禁止

許諾メールは非公開証拠として扱い、Public GitHubへ送信しない。

## Nori確定方針：IRBANK手動取得運用

恒久保存先：

D:\投資・トレード\株式\株式データ\IR BANK

Workspace内の `資産/外部データ/IRBANK/` は採用しない。

運用：
- IRBANK取得はNoriが手動実施
- CodexはIRBANKへ直接接続・自動取得しない
- Codexは保存済みファイルを読取専用で使用
- 原データ・加工データ・許諾証拠をGitHubへ送信しない

提案ACL：
- SYSTEM：Full Control
- Administrators：Full Control
- KING\nori：Full Control
- KING\CodexSandboxOffline：Read & Execute
- 継承停止

Codexには書込み・変更権限を与えない。

許諾証拠候補：
D:\投資・トレード\株式\株式データ\IR BANK\evidence

## 現在の未承認2案

### WORKFLOW案
ChatGPT/規程案/WORKFLOW/IRBANK手動取得データ運用_案.md

最新版commit：
45187b5372299420a925e179375fb98396a3f86a

### 作業指示書案
ChatGPT/作業指示案/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_作業指示書案.md

最新版commit：
489d8b858e0a3a935016653c882e97a0e43030be

両案にはDドライブ保存先、4主体ACL、Codex Read & Execute、許諾証拠非公開保管、Git管理外確認を反映済み。

## 次工程

Noriは、Dドライブ外部非公開領域＋Codex読取専用ACLの設計で、上記2案をカン再監査へ進めることを承認済み。

次に確認すること：
1. CodexがGitHub最新版2案を取得したか
2. カン再監査結果
3. WORKFLOW案の最終判定
4. 1115作業指示書案の最終判定
5. 是正内容
6. 正式承認前に残るNori判断事項
7. 外部保存先の絶対パス・実体・ACL・Git管理外・Codex読取権限の設計が適合したか
8. 個別許諾証拠の非公開保管方法が適合したか

まだ未承認・未実施：
- WORKFLOW正式発行
- 1115正式発行
- 外部保存先のACL設定・利用開始
- IRBANKデータ移動・読取り開始
- 0217作業再開
- EDINET追加取得
- FChart追加調査
- accepted生成
- hold解除
- 654候補展開
- 0.5％閾値の本番採用

## スレッド引き継ぎ

詳細：
ChatGPT/HANDOVER/20260926-1226_IRBANK手動取得運用_監査再開前_引き継ぎ.md
