> 正式発行：Noriの第5群正式承認（2026-09-30受領）に基づき、カン独立案監査の適合（承認可）・阻害0後に新規発行。
> 監査案v2 SHA-256：e1992b688afb0ec9ba85d4fe35c3ead753e4f6f6f9fe14ed2ac84e2f22960511
> 以下は監査適合案の本文と完全一致する。第6群は未承認。

# 第5群 初回実施専用 実施指示案 v2

## 目的・承認
Noriの2026-09-30受領「Nori正式承認。第5群『初回実施』を承認します」を操作・本指示の監査後正式発行の根拠とする。発言日時と受領日を混同しない。固定済み2入力版、固定4企業年度、net_profitのみ、新専用業績DBの初回実施を行う。第4群の正式指示とファイルACL限定追補、監査適合済み完全パッケージv2の対象、版、権利、禁止を維持する。

## 読取・入力固定
非公開位置・SID・値・入力SHAは公開本文へ転記しない。既存0830非公開付属書の既存隔離領域とproduction_prep_rights_inventory_v2.jsonのproduction_proposalを、保存先・固定主体・権限・固定DB名の唯一の位置索引とする。権利台帳の入力manifest、target_scope、metric_mapping、selection_policy、configの第4群配置版とprep v2版を照合する。既存7証跡、旧版・第4群証跡は必要な版・根拠・不変確認に限り読取る。原CSV2版はSHA全体読取とheader_record及び固定4元位置までの解析だけ。指定外個票抽出・PoC・EDINET固定8セル・取得は行わない。

## 新規成果物・保存先
公開の共通基点は成果物/作業履歴/20260929-1750_FAND_IRBANK本番初回導入_実装準備/。
新規公開準備3ファイル：group5_runner_v2.py、test_group5_runner_v2.py、20260930_第5群初回実施_実施指示案_v2.md。
正式指示1ファイル：作業指示/20260930_FAND_IRBANK本番初回導入_第5群初回実施_実施指示書_v1.md。
公開報告1ファイル：共通基点の20260930_第5群初回実施_作業報告書_v1.md。
非公開新規4ファイル：production_proposal.path直下のproduction_execution_config_g5_v1.json、およびproduction_proposal.evidence_path直下のgroup5_prestart_gate_v1.json、group5_execution_evidence_v1.json、group5_completion_audit_v1.json。
DB新規1ファイル：production_proposal.assetsで固定済みの予約DB名のみ。
準備v1の3ファイルは要修正履歴として保全し、準備v2の3ファイルを新規保存する。保存済み版は全て保全し、既存・同名を上書きしない。是正が必要なら、同じ用途・同じ保存親・同じ対象の次連番新規版とし、承認範囲を拡大しない。DB本体は次連番にしない。固定DB名の衝突又は実施失敗後は止め、再実施・退避・削除を推測で実施しない。新規親領域は作らない。

## 実装経路の明示
既存package_v2/first_load_procedure.md第5項のloader.create_first呼出は、本第5群に限り新規group5_runner_v2.first_loadから固定loader.loadへの呼出とする。本指示はその限定経路を明示的に定め、既存4実装・DDL・配置済みconfig等は変更しない。全体transactionは専用DBの8表DDL・全投入を一つのBEGIN IMMEDIATEからcommitまでで実施する。CheckedConnection.commit内で現物必須検証を実施してから実commitし、例外は固定loaderのrollbackへ伝播する。
原CSV2版の共有読取専用ロック（書込・削除共有禁止）を抽出前からcommit後検証・閉鎖・原本SHA再照合まで保持する。全体SHA/サイズ・ヘッダー一致、指定元位置の企業・期間一致を検証する。指定位置までのCSV走査の非対象行は結果・証跡へ転記しない。
DBと新規非公開文書はCREATE_NEWで排他作成し、作成の最初から第4群追補の固定4ACE・主体/権限/AllowDeny・保護DACL・ファイルInheritanceFlags/PropagationFlags=Noneを適用する。親・既存配置・旧版のACLは変更しない。通常実行トークンと制限sandboxトークンを区別し、必要な実行権限はACL拡大で代替しない。

## 実行configと開始前ゲート
旧production_config_v1.jsonを保全し、新configは既存manifest/4実装SHA/spec_digest/固定DB名を維持する。version production-prep/2、mode production、production_approved/deployment_approved/first_load_approved trueは今回の固定初回用途だけ。承認参照・正式指示SHA・runner版/SHA・開始前監査参照・作成時SDDLを新規固定する。ready=false、completion_audit_ref=null、activation_approval_ref=nullを維持し、本番readerの利用は開始しない。
開始前こう自己検証とカン独立監査を必須とする。固定DB/sidecar不存在、入力2版SHA/サイズ、固定4対象、core4/DDL/manifest、Group4固定9配置の不変、dir3/fileの固定ACL/実効アクセス/reparseなし、Git除外/未追跡/未staged、元証跡/旧版不変、原本ロック成立・書込共有拒否を確認する。
group5_prestart_gateは適合（承認可）・阻害0を記録し、configと正式指示/runnerのSHA、入力版、ACL/Git確認結果及びカンの独立判定を非公開保存する。未充足ならDB作成前停止する。実行直前にも同じ条件を再照合し、経時変化で失効させる。

## 必須現物検証
8表集合完全一致、source_batch2/run_source2/processing_run1/entity2/selection_policy1、staging4/validation32/adoption_candidate4、全4 pass・全32 pass、hold/reject0、G01～G08理由/版一致、FK0、integrity ok、主キー/重複/型/対象/用途、原値とDecimal文字列の再計算一致、固定根拠JSON一致、意味属性unknown保持、倍率1/JPY、source_csv_spec_proven=false、承認spec・抽出records・policyから独立再計算したrun/input digest一致、content digest一致をcommit前と後に確認する。候補4はaccepted・投資判断・公開データ採用の承認ではない。
閉鎖後DB SHAを固定し、sidecar0とDB限定ACL/Gitを再確認する。原本、旧版、第4群各配置/証跡は開始前後SHA・ACL/metadataで比較する。既存保護DBは内容を読まずmetadataのみ、内容SHA確認と称さない。既存価格Gateway/FChart/設定/コードは対象外、不変は操作集合限定と必要metadataで説明する。

## 失敗・バックアップ・禁止
新DB名不存在のため既存本番資産のバックアップは作らない。今回のrollbackは未committransactionのみ。失敗した専用DB等は「未完了・正式成果ではない」と記録して保全し、成功報告へ流用しない。commit後の具体的不適合も停止、ready=falseを維持する。実体backup・復旧・削除・改名・上書きは禁止。
第6群、稼働、全対象展開、定期更新、価格結合、投資判断利用は未承認。既存DB/保護親/原本/既存資産/ACLを変更しない。新規取得なし。

## 自己検証・独立監査・公開区分
新runnerの合成メモリ試験（commit前失敗でDDL含むrollback、改ざん拒否、固定元位置境界、SHA/企業期間拒否、全run_idの同時改ざんでもcommit前拒否・DDL rollback）を実施する。実原本PoC再実施なし。
案・新runnerについてカン独立監査適合後、監査案一致を確認しNoriの今回条件付き正式発行承認で新規発行する。配置後開始前監査→初回実施→こう自己検証→カン第5群完了監査（第6群稼働監査と別）を行う。非公開現物は内部比較だけで扱い、外部表示は固定bool/count/enumのみ。カンは実装・是正・書込を行わず独立読取判定する。
公開5文書/コードは非公開値・位置・SID・入力SHA・認証・旧資産禁止情報を含まない一般手順/集約結果だけとし、公開安全性を照合する。GitHub送信は正式指示/報告の承認済み標準ミラー条件を満たす範囲に限り、非公開4文書/DB/inputを送信しない。任意のrunner公開は行わない。
完了報告は実装/DDL/runner版とハッシュ、固定入力版照合、4/32/4/8現物結果、ACL/Git/不変、DB非公開hash保存、監査適否/阻害数、未承認第6操作、残存リスクを一括提示する。第6判断はNoriに残す。
