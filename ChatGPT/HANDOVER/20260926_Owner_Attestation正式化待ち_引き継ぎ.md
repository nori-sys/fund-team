# SOSIA FAND 司令 引き継ぎ

作成日：2026-09-26

## 現在の最優先

Owner Attestation方式をSOSIA FAND全体へ正式導入し、IRBANK個別ゲートと整合させて開始前ゲートを再判定する。

Noriはこの一括方針を正式承認済み。

## Owner Attestation案

GitHub main 発行済み：
- ChatGPT/規程案/20260926_Owner_Attestation方式導入_全体改定案.md
- ChatGPT/規程案/20260926_AGENTS_Owner_Attestation_改定案.md
- ChatGPT/規程案/ROLE/20260926_ROLE_FUND_こう_Owner_Attestation_改定案.md
- ChatGPT/規程案/WORKFLOW/20260926_監査運用_Owner_Attestation_改定案.md

Codexが是正し、カン独立再監査で4文書とも「適合（承認可）」。

最終是正版：
- ChatGPT/規程案/20260926_Owner_Attestation方式導入_全体改定案_こう監査是正案.md
- ChatGPT/規程案/20260926_AGENTS_Owner_Attestation_改定案_こう監査是正案.md
- ChatGPT/規程案/ROLE/20260926_ROLE_FUND_こう_Owner_Attestation_改定案_こう監査是正案.md
- ChatGPT/規程案/WORKFLOW/20260926_監査運用_Owner_Attestation_改定案_こう監査是正案.md

## Noriの正式承認内容

次を一括で進める。

1. AGENTS.md
2. 規程/ROLE/ROLE_FUND_こう_ChiefManager.md
3. 規程/WORKFLOW/監査運用.md

へOwner Attestation方式を正式反映する。

全体改定案は設計・監査記録として保全する。

同時に、
- 1115公開本体 v2
- 規程/WORKFLOW/IRBANK手動取得データ運用.md
- 必要に応じて1115非公開付属書 v2

を最小改定し、Owner Attestation成立後は、既にNoriが受容した同一の不確実性だけを理由に再停止しないよう整合させる。

正式反映後、カン独立再監査、Owner Attestation適用、IRBANK開始前ゲート再判定まで進める。

## 今回のIRBANK Owner Attestation

Noriは今回のIRBANK利用について、利用許諾を得ており、この用途で利用可能と判断することを明示している。

SOSIA FAND内部では、この申告を許諾ゲートの最終判断として扱う方針。

同じ許諾不確実性について追加証拠、追加申告、再確認を反復要求しない。

## 維持する安全条件

- Nori本人による手動取得のみ
- Codexによる直接取得、自動取得、スクレイピング禁止
- Codex読取専用
- ACL、Git非公開、公開禁止条件維持
- 認証情報、個人情報、機密情報の保護
- 恒久的権限拡大禁止
- 不可逆変更・重要資産変更は別途承認
- EDINET・FChart側の未解消停止条件維持
- accepted生成、hold解除、654候補展開、本番DB・コード・設定変更禁止

## 1115 v2 現状

正式反映済み：
- 作業指示/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_v2_作業指示書.md
- 規程/WORKFLOW/IRBANK手動取得データ運用.md
- 作業指示/非公開/20260926-1115_FAND_IRBANK手動取得運用導入・0217再開_非公開付属書_v2.md

公開2文書GitHub commit：
6643ce788b120577b41400680f2e41549bbe74c2

## 新スレッド開始点

前スレッド末尾で、Owner Attestation正式反映、IRBANK個別整合、再監査、開始前ゲート再判定まで一括実施するCodex貼付用指示文を作成済み。

その実行結果は前スレッドではまだ受領していない。

新スレッドでは、Codex実行結果が来ているか確認し、未実行なら前スレッド末尾の正式指示を使用する。
