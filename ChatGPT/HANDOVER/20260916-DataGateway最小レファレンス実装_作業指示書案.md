# Data Gateway 最小レファレンス実装 作業指示書案

## 文書状態

**未承認案・実行禁止**

本書は監査およびNori承認前の作業指示書案である。

本書単独では作業開始、ファイル変更、DB参照、GitHub書込みその他の実行権限を付与しない。

---

## 01）目的

SOSIA FANDにおける将来の

**ChatGPT → GitHub → Data Gateway → 株価DB → SOSIA FAND Console**

連携の基礎となる、ローカル側の最小経路を検証する。

今回の検証対象は、

**Data Request → Data Gateway → 株価DB → Data Response → Console Command → SOSIA FAND Console**

とする。

ChatGPTからGitHubへの自動要求送信、GitHub監視、自動起動は対象外とする。

検証ケースは、

**トヨタ自動車（7203）の直近100営業日の日足OHLCVを取得し、SOSIA FAND Consoleへチャート表示する**

1ケースに限定する。

---

## 02）実行担当

実行統括はChief Manager「こう」とする。

必要に応じ、現行ROLEおよび承認済み作業指示の範囲で補助エージェントを使用できる。

Data Gatewayは新しいAI ROLEではない。

株価DBへの読み取り処理を局所化する**ローカル機能モジュール**として扱う。

Data Gatewayへ以下の責任・権限を移譲しない。

- Data ManagerのDB更新・データ品質管理責任
- バフェットの現行通信・永続記憶管理責任
- Chief Managerの実行統括責任
- Noriの承認権
- 投資判断または分析判断

---

## 03）正式発行と作業開始条件

本案が監査で「適合（承認可）」となり、Noriが明示承認した後にのみ正式発行できる。

正式発行時は、ローカル正規Workspaceの

`作業指示/`

配下へ承認済み正式文書として保存する。

以下のすべてを確認するまで作業を開始しない。

1. Noriの明示承認
2. ローカル正式作業指示の実在
3. 正規Workspace確認
4. Gitルート確認
5. 承認済み作業指示の内容確認
6. 現行ROLE・WORKFLOWとの整合確認
7. 承認済み通信経路による送達・受領確認

GitHub上の本案または参照用ミラーだけを実行根拠としてはならない。

---

## 04）事前確認と基準線

着手前に以下を確認し、基準線として記録する。

- `AGENTS.md`
- `START_HERE.md`
- 適用ROLE・WORKFLOW
- 正規Workspace
- Gitルート
- `git status`
- 既存未コミット変更一覧
- 未追跡ファイル一覧
- `database/fund_stock.db` の実在
- `fund_stock.db` のSHA-256
- DB関連WAL/SHM等の有無
- SOSIA FAND Consoleの現行ファイル
- Console関連の既存未コミット・未追跡変更
- 株価DBの対象テーブル・カラム
- 対象系列が本作業の仕様に適合すること

既存未コミット変更と今回の変更を安全に分離できない場合は停止する。

---

## 05）対象株価系列

今回使用する系列は、DB内に既に存在し、仕様を確認できる**日足OHLCV**に限定する。

最低限、以下を使用する。

- 銘柄コード
- 日付
- Open
- High
- Low
- Close
- Volume

対象：

`7203`

足種：

`D1`

件数：

**直近100営業日**

並び順：

DB取得後、Consoleへは**日付昇順**で渡す。

基準日はDBに存在する最新営業日とする。

### 価格補正

RAW価格・調整済み価格のどちらを採用するかは、既存DBの実在テーブルと現行仕様を確認して決定する。

どちらを使用するか既存仕様から一意に確定できない場合は、DB接続処理を開始せず停止し、Noriへ判断を求める。

推測で補正方式を選択しない。

欠損または異常値を検出した場合も補完せずエラーとして扱う。

---

## 06）Data Request

今回はローカルのインプロセス処理として扱う。

常駐プロセス、HTTPサーバー、ソケット通信、ポート待受けは実装しない。

最低限のRequest：

```json
{
  "version": "1.0",
  "request_id": "DR-xxxxxxxx",
  "action": "get_price_series",
  "symbol": "7203",
  "timeframe": "D1",
  "limit": 100
}
```

対応actionは、

`get_price_series`

のみとする。

`limit` は今回100固定とし、汎用的な任意件数対応は実装しない。

---

## 07）Data Gateway

Data Gatewayはローカルのインプロセスモジュールとして実装する。

SQL、テーブル名、カラム構造その他のDB固有処理をGateway内部へ隠蔽する。

要求側から任意SQLを受け付けない。

DB接続は**技術的に書込み不能なREAD ONLY方式を必須**とする。

通常の読み書き可能接続で「書かない運用」とすることは禁止する。

READ ONLY接続を実現できない場合は停止する。

---

## 08）DB安全条件

DB参照では次を必須とする。

- DB本体を書込み不能で開く
- DB更新を行わない
- schema変更を行わない
- transactionによる書込みを行わない
- WAL/SHMその他の副作用ファイルを新規作成しない
- DBコピーを勝手に作成しない
- DB内容を外部送信しない

実行前後で、

`database/fund_stock.db`

のSHA-256を比較する。

WAL/SHM等についても実行前後の有無を確認する。

差異を検出した場合は技術検証を失敗として停止し、原因を報告する。

---

## 09）Data Response

成功Responseには最低限以下を含める。

```json
{
  "version": "1.0",
  "request_id": "DR-xxxxxxxx",
  "status": "success",
  "symbol": "7203",
  "timeframe": "D1",
  "count": 100,
  "data": [
    {
      "date": "YYYY-MM-DD",
      "open": 0,
      "high": 0,
      "low": 0,
      "close": 0,
      "volume": 0
    }
  ]
}
```

失敗Responseには最低限、

- version
- request_id
- status
- error_code
- message

を含める。

エラーコード：

- `SYMBOL_NOT_FOUND`
- `DATA_NOT_FOUND`
- `INVALID_REQUEST`
- `DB_ERROR`
- `UNSUPPORTED`
- `DATA_SCHEMA_MISMATCH`
- `READ_ONLY_FAILED`

---

## 10）Console Command

Consoleへの表示要求は次の形式を基本とする。

```json
{
  "version": "1.0",
  "command_id": "CC-xxxxxxxx",
  "request_id": "DR-xxxxxxxx",
  "action": "show_chart",
  "symbol": "7203",
  "timeframe": "D1",
  "bars": 100
}
```

Request IDを保持し、元のData Requestまで追跡できるようにする。

---

## 11）試験データと保存

Request / Response / Console Commandを恒久的な通信ファイルとして運用しない。

今回の検証では、

- 実行時オブジェクト
- テストfixture

としてのみ扱う。

テストfixtureを保存する場合は、今回の実装専用ディレクトリ内に限定する。

GitHubへ株価系列データを保存しない。

---

## 12）変更許可対象

正式発行前に、Codexは既存Console構成を調査し、**実際に変更が必要な具体的ファイルパスを確定する**。

正式作業指示には、以下を具体的に列挙する。

- Data Gateway新規ファイル
- テストファイル
- fixture保存場所
- Console変更対象ファイル

正式指示に列挙されていないファイルを変更してはならない。

Console対象ファイルに既存未コミット変更が存在し、安全に分離できない場合は変更せず停止する。

---

## 13）外部通信・GitHub

本検証中は以下を禁止する。

- GitHub書込み
- Git commit
- Git push
- GitHub Actions
- Webhook
- GitHub監視
- 外部API
- 外部ネットワーク通信
- OpenAI API
- MCP
- 外部ストレージへのデータ保存

必要になった場合は作業を停止し、別途承認を求める。

---

## 14）その他の禁止事項

以下を行わない。

- `fund_stock.db` の更新・削除・schema変更
- FChart原本の変更
- データ補正方式の変更
- ROLE変更
- WORKFLOW変更
- 入口文書変更
- AI間通信運用変更
- 永続記憶運用変更
- 投資判断
- 売買評価
- RSI等の追加指標実装
- 大規模リファクタリング
- 既存未コミット変更の上書き・混入

---

## 15）報告経路

報告経路は現行ROLEおよびAI間通信運用に従う。

本作業指示によって、恒久的または一時的な独自の報告経路を新設しない。

現行ROLE・AI間通信運用との不整合により報告不能となる場合は、独自判断でNori直接報告へ切り替えず、停止条件として扱う。

---

## 16）検証シナリオ

入力：

```text
symbol: 7203
timeframe: D1
limit: 100
action: show_chart
```

確認経路：

```text
Data Request
     ↓
Data Gateway
     ↓
fund_stock.db（READ ONLY）
     ↓
Data Response
     ↓
Console Command
     ↓
SOSIA FAND Console
```

確認事項：

1. Request検証
2. 7203認識
3. READ ONLY接続成功
4. 指定系列の取得
5. 100営業日取得
6. OHLCV項目確認
7. 日付昇順への整列
8. Response生成
9. Console Command生成
10. Console表示
11. request_idによる追跡
12. DB非変更確認
13. 許可対象外ファイル非変更確認

---

## 17）明示的停止条件

以下のいずれかを検出した場合は停止する。

- 正規WorkspaceまたはGitルート不一致
- 承認済み正式指示を確認できない
- 許可対象ファイルを確定できない
- 既存変更を安全に分離できない
- DBをREAD ONLYで開けない
- DB schemaが想定と一致しない
- RAW/調整済み系列を一意に決定できない
- DBハッシュが実行前後で変化した
- WAL/SHM等の想定外ファイルが生成された
- Consoleインターフェースが想定と一致しない
- 許可対象外ファイル変更が必要になった
- FChart原本への影響を否定できない
- 外部通信が必要になった
- 公開安全性に疑義が生じた

---

## 18）成果物

最低限以下を提出する。

- Data Gateway試作コード
- テストコード
- Request実例
- Response実例
- Console Command実例
- Console表示確認結果
- 変更ファイル一覧
- 着手前Git差分一覧
- 完了後Git差分一覧
- DB実行前SHA-256
- DB実行後SHA-256
- WAL/SHM等確認結果
- テスト結果
- 未実施事項
- 問題点
- 制約
- 次段階への改善候補
- 作業完了原報告

---

## 19）技術検証完了条件

以下をすべて満たした場合に技術検証完了候補とする。

- 7203の日足100営業日OHLCVを取得できた
- READ ONLY接続が技術的に保証されている
- RequestからConsoleまで追跡可能
- Consoleへチャートを表示できた
- テスト結果が保存されている
- DBハッシュが実行前後で一致した
- WAL/SHM等の想定外副作用がない
- FChart原本を変更していない
- 許可対象外ファイルを変更していない
- 既存変更を毀損していない
- 必要な証跡が提出されている

最終完了承認はNoriが行う。

---

## 20）本作業後に判断する事項

今回の技術検証後に、別途判断する。

1. Data Gateway正式採用
2. Gateway API仕様
3. GitHub Gateway領域
4. ChatGPT → GitHub → Gateway連携
5. GitHub監視
6. ChatGPTのGitHub書込み範囲
7. ソロスROLE
8. AI間通信・永続記憶管理の再設計
9. RSI等の指標対応
10. スクリーニング機能
11. 常駐サービス化またはAPI化

これらは今回確定しない。
