# Data Gateway 最小レファレンス実装 作業指示書案

## 文書状態

**未承認案・実行禁止**

本書は監査適合済みの未承認案である。本書単独では、作業開始、実装資産の変更、DB接続、GitHub書込みその他の実行権限を付与しない。Noriの明示承認、ローカル正式指示書の発行、承認済み通信経路での送達・受領確認まで実装を開始しない。

## 01）目的

7203について、`daily_prices_raw` の直近100取引日OHLCVを、Data Request → Python Data Gateway → Data Response → Console Command → SOSIA FAND Consoleの経路でローカル表示する最小検証を行う。RAW価格の使用は今回の表示用選択であり、価格補正方針の正式決定ではない。

## 02）役割と権限

実行統括はChief Manager「こう」とする。Data Gatewayは新しいAI ROLEではなく、DB読取りを局所化するローカルPython機能モジュールである。Data ManagerのDB更新・品質管理、バフェットの通信・永続記憶管理、Chief Managerの統括、Noriの承認権および投資判断をData Gatewayへ移譲しない。

## 03）正式発行と開始条件

Noriが本案の正式発行を明示承認した後、ローカル正規Workspaceの `作業指示/` 配下に指定された正式文書が実在し、正規Workspace・Gitルート・ROLE・WORKFLOW・承認済み通信経路の送達受領を確認できた場合だけ着手できる。GitHub上の本案は参照用であり、実行根拠ではない。

## 04）変更許可対象

新規作成だけを許可する。

- `work/data-gateway-reference/data_gateway.py`
- `work/data-gateway-reference/export_console_data.py`
- `work/data-gateway-reference/tests/test_data_gateway.py`
- `work/data-gateway-reference/tests/fixtures/valid_request.json`
- `work/data-gateway-reference/tests/fixtures/invalid_request.json`
- `work/fund-analysis-console-prototype/data/gateway-response.js`

更新だけを許可する。

- `work/fund-analysis-console-prototype/index.html`
- `work/fund-analysis-console-prototype/market.js`

許可する新規ディレクトリは `work/data-gateway-reference/`、`work/fund-analysis-console-prototype/data/`、`成果物/20260916-01_DataGateway最小レファレンス実装/` だけとする。これらまたは生成ファイルが着手前に存在する場合は、上書き・削除・再利用をせず停止する。許可対象外のファイル・ディレクトリの作成、更新、移動、削除を禁止する。

## 05）事前基準線

着手前後に `git status --short`、許可対象パスのSHA-256、既存未コミット変更、未追跡ファイルを比較する。現行Console一式は未追跡であり、既存の `tools/fxx_sqlite/config/config.json` の変更を含む既存差分を今回の変更と混在させない。分離できない場合は停止する。

## 06）対象株価系列

対象は `daily_prices_raw` の `fchart_code = 7203` とする。使用カラムは `trade_date, open, high, low, close, volume` である。`trade_date` 降順で取得した直近100取引日を、Consoleには日付昇順で渡す。100件不足、日付重複、欠損、非有限値、負値、OHLC不整合は `DATA_SCHEMA_MISMATCH` として失敗させる。`daily_prices_adjusted` は今回使用しない。

## 07）Data Request

Data Requestはローカル処理だけに限定する。

```json
{"version":"1.0","request_id":"DR-xxxxxxxx","action":"get_price_series","symbol":"7203","timeframe":"D1","limit":100}
```

対応actionは `get_price_series` のみ、limitは100固定とする。任意SQL、任意銘柄、任意件数を受け付けない。

## 08）SQLite READ ONLYと保全

`data_gateway.py` はPython標準 `sqlite3` だけを使用し、絶対POSIXパスから構成する `file:<absolute-path-to-fund_stock.db>?mode=ro&immutable=1` を `sqlite3.connect(uri, uri=True)` で開く方式だけを使用する。通常パス接続、URI無効接続、`rw`・`rwc`、書込み可能接続、接続失敗時の代替・フォールバックを禁止する。

接続前後に `database/fund_stock.db`、`database/fund_stock.db-wal`、`database/fund_stock.db-shm`、`database/fund_stock.db-journal` の存在状態、存在時のサイズとSHA-256を同じ手順で記録・比較する。随伴3ファイルが接続前に一つでも存在すれば接続せず停止する。接続後の差異、新規作成または削除も後続処理停止条件とする。

## 09）Payload契約

成功時の `gateway-response.js` は、次のPayloadだけを保持する。

```json
{"response":{"version":"1.0","request_id":"DR-xxxxxxxx","status":"success","symbol":"7203","timeframe":"D1","count":100,"data":[]},"command":{"version":"1.0","command_id":"CC-xxxxxxxx","request_id":"DR-xxxxxxxx","action":"show_chart","series":[]}}
```

`command.request_id` は `response.request_id` と一致し、`command.series` は `response.data` と同じ100件のOHLCV配列とする。失敗Responseには `version, request_id, status, error_code, message` を含め、Console Commandを生成しない。エラーコードは `SYMBOL_NOT_FOUND`、`DATA_NOT_FOUND`、`INVALID_REQUEST`、`DB_ERROR`、`UNSUPPORTED`、`DATA_SCHEMA_MISMATCH`、`READ_ONLY_FAILED` とする。

## 10）ローカル生成ファイルとConsole

`export_console_data.py` はPayloadをUTF-8の `window.__DATA_GATEWAY_PAYLOAD__ = <JSON>;` 一文だけとして、`work/fund-analysis-console-prototype/data/gateway-response.js` に排他的な新規作成で出力する。JSON直列化だけを用い、DB値の文字列連結を禁止する。途中失敗、既存検知、出力検証失敗時は上書き・削除・再利用・再実行をせず停止する。

静的Browser Consoleは `index.html` がこの生成ファイルを読込み、`market.js` がPayload・Response・Console Command・request_id・系列を完全検証した場合だけ描画する。失敗時は既存message UIへerror codeとmessageを表示し、チャート更新、DB再照会、サンプル系列へのフォールバックを行わない。常駐プロセス、HTTPサーバー、ソケット、ポート待受けを実装しない。

## 11）証跡・成果物・報告

実データを含めてよい保存先は生成された `gateway-response.js` だけとする。成果物、通信記録、原報告には価格値を転記せず、ハッシュ、件数、日付範囲、変更一覧、テスト結果だけを記録する。fixtureと成果物内のRequest/Response例は合成・非機密データだけを用いる。実データ、生成ファイル、成果物をGitHubへ送信してはならない。

原報告はChief Manager ROLEに従いバフェットへ提出する。緊急時またはバフェット利用不能時だけNoriへ直接報告する。AI間通信の採番・記録は適用・個別承認された通信経路がある場合だけ行う。

## 12）禁止事項

DB更新・削除・schema変更、FChart原本変更、ROLE・WORKFLOW・入口文書変更、投資判断、追加指標、大規模リファクタリング、外部API・外部ネットワーク通信、MCP・OpenAI API、GitHub書込み、Git add/stage/commit/push、GitHub Actions、Webhook、監視、自動起動を禁止する。

## 13）停止条件

正規WorkspaceまたはGitルート不一致、正式指示未確認、既存変更との分離不能、許可対象外の差分、DBまたは随伴ファイル差異、READ ONLY接続不能、系列・Payload・Console契約不整合、生成失敗、外部通信の必要性、公開安全性の疑義を検知した場合は停止して報告する。

## 14）完了条件

7203のRAW OHLCV 100件を日付昇順で取得し、書込み不能READ ONLY接続、Payload追跡、Console表示、DB・随伴ファイル不変、許可対象外変更なし、既存変更非毀損、必要なローカル証跡保存をすべて確認できた場合だけ技術検証完了候補とする。最終完了承認はNoriが行う。

## 15）修正履歴と監査

初回監査で報告経路、DB保全、変更範囲、価格系列、Console契約を是正対象とした。読取り専用事前調査でRAW系列、静的Console構成、`mode=ro&immutable=1`、既存未追跡資産を確認した。最終修正版はDB URI、随伴ファイル保全、排他的生成、Payload契約、保存先、停止条件を固定した。

カンによる最終独立再監査判定は **適合（承認可）** である。この判定は正式発行、実装開始、DB操作、通信開始または作業全体完了を承認しない。
