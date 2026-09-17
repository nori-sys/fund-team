# CURRENT_CONTEXT

## 現在の目的

SOSIA FANDを、ChatGPTとCodexの長所を併用するAI組織としてレファレンス設計し、最小実装から検証・改善する。

Data Gateway可変Request化 Phase 2修正版は、実装・検証・独立監査まで完了した。カンの最終独立監査は `適合（承認可）`、未決事項なし。次の主要テーマは、ChatGPT→Codexの作業指示とCodex→ChatGPTの作業報告をGitHub経由で標準化し、他プロジェクトへ展開可能な共通WORKFLOWとして規定すること。

## 確定・合意した方向

- 対象リポジトリは `nori-sys/fund-team`、branchは `main`。
- ChatGPT側の「チャット」は、Nori直属のSOSIA FANDシステム構築アドバイザー。
- NoriをChatGPTとCodex間の途中中継役にしない方向で運用を改善する。
- Codex向け作業指示は目的型とし、承認済み範囲内では `こう → カン → こう修正 → カン再監査` を `適合（承認可）` まで自律反復する。
- カンは独立監査担当として起案・実装・是正を行わない。
- `適合（承認可）` はNoriの正式承認を代替しない。
- Data GatewayはREAD ONLYを維持する。
- GitHubは共有・参照・受け渡し層であり、ローカルWorkspace正本を置き換えない。
- 自動監視、自動検知、自動起動、Webhook、GitHub Actions、APIサーバー、常駐化、MCPは現段階では未導入。起動はNoriの明示指示による手動トリガーを維持する。

## Data Gateway Phase 2修正版 完了結果

正式指示:

`作業指示/20260917-0947_SOSIA_FAND_DataGateway可変Request化_Phase2_修正版_作業指示書.md`

承認済み月足仕様:

`成果物/20260917-0947_SOSIA_FAND_月足1M_正式仕様.md`

実装・検証結果:

- `monthly_prices` 追加
- `timeframes` に `1M` 定義追加
- `1M` は `daily_prices_raw` から暦月単位で生成
- OHLCVは承認済み月足仕様どおり
- 月足差分生成は `BEGIN IMMEDIATE`
- SQLite `CURRENT_TIMESTAMP` を `run_upper_bound` として固定
- 差分境界は `last_generated_at <= imported_at < run_upper_bound`
- UPSERTとウォーターマーク更新は同一トランザクションで成功時のみcommit
- Gatewayは `1D / 1W / 1M` を固定SQLマッピングでREAD ONLY参照
- 任意SQL・任意テーブル指定不可
- 週足・月足Payloadは `date=period_start`、`period_end`、`source_daily_max_date` を返す
- 暫定月は `source_daily_max_date < period_end` で判別可能
- 月足生成件数 `824,859`
- RAW日足の銘柄・暦月グループ数と月足件数が一致
- `daily_prices_raw` と `weekly_prices` は生成前バックアップとの差分0
- 7203の2026年8月は完了月、9月は暫定月として確認
- Gateway正常系・異常系検証成功
- 再生成時の月足全列差分0、影響月0件
- 一時fixtureで新規日足後、影響月のみ差分再生成を確認
- WAL / SHM / journal 不在
- 最終DB SHA-256: `A53327824BF40A10A07D194CB55FF1BEBAD7C98B44B1C1965BDA0A3E3D7E8644`
- カン最終独立監査: `適合（承認可）`
- 未決事項なし

Codexは、正式指示に保存先・公開範囲指定がなかったため、作業報告書のGitHub書込みは実施していない。

## 作業指示書・作業報告書の共通運用検討

Noriとチャットは、今後、Codexの作業結果をチャット本文で手動転送するのではなく、GitHub上の作業報告書としてCodexが保存し、ChatGPTが直接読む運用へ移行する方針で合意した。

基本フロー:

`ChatGPT → GitHub作業指示書 → Codex → GitHub作業報告書 → ChatGPTレビュー`

この運用はSOSIA FAND固有ではなく、他プロジェクトでも共通利用する前提で、`規程/WORKFLOW/指示書・報告書運用.md` として規定する方針。

### 命名責任

- 指示書の起点はChatGPTが作成する指示書案。
- 指示書案の時点でファイル名を決定する。
- Codex側で監査・修正して `承認可` まで整え、Nori承認後に正式指示書とする。
- 指示書・作業報告書の命名責任は原則ChatGPT側に置く。
- Codexは対応する作業指示書の基底名を継承して作業報告書を作成する。

### プロジェクトID

- プロジェクトIDはNoriが各プロジェクトごとに付与する。
- SOSIA FANDのプロジェクトIDは `FAND`。

### 現時点の命名案

作業指示書:

`YYYYMMDD-HHMM_プロジェクトID_件名_作業指示書.md`

例:

`20260917-2322_FAND_DataGateway_Phase2_作業指示書.md`

1通目の作業報告書:

`YYYYMMDD-HHMM_プロジェクトID_件名_作業報告書.md`

例:

`20260917-2322_FAND_DataGateway_Phase2_作業報告書.md`

同一作業指示に対する2通目以降の作業報告書:

`YYYYMMDD-HHMM-NN_プロジェクトID_件名_作業報告書.md`

例:

`20260917-2322-02_FAND_DataGateway_Phase2_作業報告書.md`

`20260917-2322-03_FAND_DataGateway_Phase2_作業報告書.md`

`-NN` は作業番号ではなく、同一作業指示に対する第2報以降の報告連番とする方向。差戻し、再監査、追加修正により作業指示書と報告書が1対1にならないことを前提とする。

### 次に決めること

配置フォルダを決める。

検討対象:

- 指示書案の配置先
- 正式作業指示書の配置先
- 作業報告書の配置先
- 差戻し・再報告時の配置と履歴保持
- 他プロジェクト共通で使えるフォルダ構成
- 既存 `作業指示/`、`成果物/`、`作業履歴/`、`ChatGPT/作業指示案/` との整合

配置フォルダ決定後、`規程/WORKFLOW/指示書・報告書運用.md` の規程案を作成し、既存 `GitHub連携運用.md`、`フォルダ構成運用.md` 等との整合確認・必要な改定範囲を整理する。

## 注意事項

- GitHub上の規程文書はローカルWorkspace正本の参照用ミラー。
- 正式規程・ROLE・WORKFLOW変更にはNori承認が必要。
- 現時点の「指示書・報告書運用」は検討中であり、正式規程ではない。
- 配置フォルダはまだ未決定。
