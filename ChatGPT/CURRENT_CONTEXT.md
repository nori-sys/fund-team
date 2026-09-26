# CURRENT_CONTEXT

## 現在の最優先状態

Owner Attestation方式をSOSIA FAND全体へ正式導入し、IRBANK個別ゲートと整合させて開始前ゲートを再判定する。

Noriはこの一括方針を正式承認済み。

## Owner Attestation方式

目的：
- Noriが人間判断事項を明示的に判断した後、同一の未確認事項・証拠不足について追加質問を反復しない。
- 不明事項は推測せず、Nori判断により受容されたことを記録する。
- 新たな具体的禁止事実、前提との重大な矛盾、技術的安全条件不適合が判明した場合のみ再停止する。

自動解除しないもの：
- 外部送信・公開禁止
- 恒久的権限拡大
- 不可逆変更
- 重要資産変更
- 資金移動・契約締結
- 正式規程・ROLE・WORKFLOW変更等に必要な別途承認

## 発行済みOwner Attestation案

GitHub main：
1. ChatGPT/規程案/20260926_Owner_Attestation方式導入_全体改定案.md
2. ChatGPT/規程案/20260926_AGENTS_Owner_Attestation_改定案.md
3. ChatGPT/規程案/ROLE/20260926_ROLE_FUND_こう_Owner_Attestation_改定案.md
4. ChatGPT/規程案/WORKFLOW/20260926_監査運用_Owner_Attestation_改定案.md

Codexが是正し、カン独立再監査で4文書とも「適合（承認可）」。

最終是正版：
- ChatGPT/規程案/20260926_Owner_Attestation方式導入_全体改定案_こう監査是正案.md
- ChatGPT/規程案/20260926_AGENTS_Owner_Attestation_改定案_こう監査是正案.md
- ChatGPT/規程案/ROLE/20260926_ROLE_FUND_こう_Owner_Attestation_改定案_こう監査是正案.md
- ChatGPT/規程案/WORKFLOW/20260926_監査運用_Owner_Attestation_改定案_こう監査是正案.md

## Noriの最新正式判断

Noriは「1」を選択し、次を一括実施する方針を正式承認した。

- AGENTS.md
- 規程/ROLE/ROLE_FUND_こう_ChiefManager.md
- 規程/WORKFLOW/監査運用.md

へOwner Attestation方式を正式反映。

全体改定案は設計・監査記録として保全。

同時に、
- 1115公開本体 v2
- 規程/WORKFLOW/IRBANK手動取得データ運用.md
- 必要に応じて1115非公開付属書 v2

を最小整合し、Owner Attestation成立後は既受容の同一不確実性だけで再停止しないようにする。

その後、
- カン独立再監査
- 今回のOwner Attestation適用
- IRBANK開始前ゲート再判定
- 公開対象正式文書のみGitHubミラー反映
まで一括で進める。

## 今回のIRBANK Owner Attestation

Noriは今回のIRBANK利用について、利用許諾を得ており、この用途で利用可能と判断することを明示している。

SOSIA FAND内部では、この申告を許諾ゲートの最終判断として扱う方針。

同一の許諾不確実性について追加証拠・追加申告・再確認を反復要求しない。

## IRBANK / 1115 現在位置

1115はv2へ正式改定済み。

正式反映済み：
- 作業指示/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_v2_作業指示書.md
- 規程/WORKFLOW/IRBANK手動取得データ運用.md
- 作業指示/非公開/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_非公開付属書_v2.md

公開2文書GitHub commit：
6643ce788b120577b41400680f2e41549bbe74c2

IRBANK専用4子領域は作成済み。
Codex通常実行主体は読取・実行のみ。
read_test_1115.txt は通常Codex実行主体で読取成功済み。

原チャット、スクリーンショット、メール原文等は残っていない。
現存するのはNori本人が先方チャットから転記したテキスト。

## 維持する安全条件

- Nori本人による手動取得のみ
- CodexによるIRBANKサイト直接取得、自動取得、スクレイピング禁止
- Codex読取専用
- ACL、Git非公開、公開禁止条件維持
- 認証情報、個人情報、機密情報保護
- 恒久的権限拡大禁止
- 不可逆変更・重要資産変更は別途承認
- EDINET・FChart未解消停止条件維持
- accepted生成禁止
- hold解除禁止
- 654候補展開禁止
- 本番DB・コード・設定変更禁止

## 次のアクション

前スレッド末尾で、次をCodexへ一括実施させる正式指示文を作成済み。

1. Owner Attestation方式を3正式文書へ正式反映
2. 1115 v2 / IRBANK WORKFLOW / 必要に応じ非公開付属書を最小整合
3. 今回のOwner Attestationを適用
4. カン独立再監査
5. IRBANK開始前ゲート再判定
6. 公開対象正式文書のみGitHubミラー反映
7. 正式反映先、commit、監査結果、Attestation適用結果、ゲート最終判定、Nori次作業、0217再開可否を報告

このCodex実行結果は前スレッドではまだ受領していない。

## スレッド引き継ぎ

詳細：
ChatGPT/HANDOVER/20260926_Owner_Attestation正式化待ち_引き継ぎ.md
