# 是正準備版 package_v2

属性参照固定と通貨比較証跡を必須化する修正版。1750用途・対象・入力2版・4対象は維持し、本番操作を許可しない。

# IRBANK 本番初回導入 実装準備 package_v2

1750正式指示・是正v2限定追補と2026-09-29 Nori限定操作・是正承認に基づく準備版。標準ライブラリのみ。旧実装を複製していない。固定2原本版・2社×2期4対象・net_profitだけを後続本番判断へ渡す。

`python -B test_package.py` は完全合成・メモリ内SQLite試験だけを実行する。readerファイル試験は呼出側が承認済み隔離領域の指定名を明示した場合だけ `file_tests` を実行する。合成DBとsidecarは保全し、自動削除しない。実原本pipelineは今回実行しない。

公開テンプレートは未結合・未稼働。実値/ID/SHA/絶対パス/ACLは非公開正本だけに記録する。`loader.create_first` にCLIはなく、指定manifest/コードSHA/正式承認参照/開始前監査/実施承認を結合した信頼済みconfigがなければ作成しない。readerリクエストからconfig・パス・SQLを受けない。

8表、全対象8ゲート、候補と採用の分離、原値保全、Decimal文字列、出典unknown/source_csv_spec_proven=falseを維持する。同一内容はNOOP、異内容/入力版不一致は停止。既存runを自動更新しない。新入力版の追記運用は本初回承認の外で、別の固定DB/版/承認が必要。

Readerは固定URI ro/immutable/query_only、SQL authorizer、Windows共有読取ハンドル、WAL/SHM/journal拒否、バイトSHA/内容/版/FK照合を用いる。合成試験の合格は本番適合を意味しない。稼働configは完了監査・Nori稼働承認後だけready。

artifact_manifestは自己参照を除く16ファイルをSHA固定し、manifest自体のSHAは公開完全パッケージに外部固定する。報告・非公開正本も相互参照し、自己ハッシュの循環を作らない。
