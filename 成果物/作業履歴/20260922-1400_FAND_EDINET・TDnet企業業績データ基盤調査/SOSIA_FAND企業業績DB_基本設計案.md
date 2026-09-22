# SOSIA FAND企業業績DB 基本設計案

## 位置付けと非実施境界

本書は論理設計の検討案であり、正式仕様・採用判断・DBスキーマ・API・実装ではない。`database/fund_stock.db`、バックアップ、ログ、FChart原本、設定および実装コードは読取り・変更とも行っていない。外部原文RAWも保存しない。

## 想定取得フロー（将来候補）

1. Nori承認済みの利用条件・認証・契約を前提に、公式ソースから書類一覧/インデックスだけを取得候補として受け付ける。
2. 受信ごとに source、公式URL、document_id、開示/提出日時、取得時刻、条件確認結果、取得方式、ファイル種別、ハッシュ（許される場合のみ）をRAWメタデータとして記録する。外部原文本体は本設計の保存対象外である。
3. 書類識別、企業識別、有効期間、会計期間、連結範囲、会計基準、通貨/単位、実績/予想を検証し、検証不能なレコードは正規化せず隔離する。
4. 検証済みのメタデータだけを正規化候補に変換し、訂正関係を評価する。DB投入・自動更新は本作業の範囲外である。

## 論理モデル（未採用）

|論理表|主なキー/属性|目的|
|---|---|---|
|`source_document`|`source_document_key`、source、official_url、document_id、disclosed_or_submitted_at、retrieved_at、terms_check_status、raw_metadata_hash|出典と取得条件の追跡。原文本体は保持しない|
|`entity_identifier`|`entity_key`、identifier_type、identifier_value、valid_from/to|証券コード、EDINETコード、法人番号等を型別・有効期間付きで保持。相互対応は確認済みの根拠がある場合だけ登録|
|`financial_fact`|`fact_key`、entity_key、source_document_key、period_end、period_type、consolidation_scope、accounting_standard、metric、value、unit、actual_forecast_flag|指標の意味・単位・文脈を欠落させず正規化|
|`document_revision`|`source_document_key`、prior_document_key、revision_type、observed_at、selection_status|訂正・削除・差替の関係と採用候補状態を追跡|

訂正優先は、同一の比較軸（企業、期間、連結範囲、会計基準、指標、実績/予想）に限り、公式に確認できる訂正関係がある最新訂正版を候補にする。元レコードを上書き・削除しない。訂正関係、同一性又は指標定義が未確定なら `selection_status=hold` 相当として人手判断へ回す。

## FChart株価DBとの関係

FChart株価DBは保全対象であり、結合・参照・変更をしていない。将来、企業業績側の `entity_identifier` と株価側の識別子を結合候補として評価しても、証券コードだけで企業同一性を推定しない。市場、銘柄、有効期間、法人・EDINET識別子および根拠を確認したマッピングを別途承認してから、読取り専用の論理結合を検討する。物理的なDB統合・外部キー追加・価格データ更新は別承認が必要である。

## 実装PoCの境界

実装PoCは未着手である。再開には、Noriが (1) ソース別利用条件と契約/認証、(2) 取得対象・頻度・件数、(3) RAWの定義と保存期間、(4) 正規化・訂正優先規則、(5) FChart株価DBとの接続権限、(6) 実装・DB変更・公開可否を承認した別指示が必要である。
