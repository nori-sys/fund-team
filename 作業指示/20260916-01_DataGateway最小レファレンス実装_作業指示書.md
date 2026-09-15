# Data Gateway 最小レファレンス実装 作業指示書

作業ID: `20260916-01`
対象プロジェクト: `FUND`
実行担当: Chief Manager「こう」
承認者: Nori

## 01）目的

SOSIA FANDにおける将来の

**ChatGPT → GitHub → Data Gateway → 株価DB → SOSIA FAND Console**

連携の基礎となる、ローカル側の最小経路を検証する。

今回の検証範囲は、

**Data Request → Data Gateway → 株価DB → Console Command → SOSIA FAND Console**

とする。

ChatGPTからGitHubへの自動要求送信、GitHub監視、自動起動は今回の対象外とする。

検証対象は、

**「トヨタ自動車（7203）の日足チャートをSOSIA FAND Consoleへ表示する」**

の1ケースに限定する。

## 02）実行担当

Chief Manager「こう」

必要に応じて補助エージェントを使用してよい。

Data Gatewayは新しいAI ROLEではなく、株価DBへ安全にアクセスするための**機能・サービス層**として実装する。

## 03）事前確認

作業開始前に以下を確認する。

1. `AGENTS.md`
2. `START_HERE.md`
3. 適用される現行ROLE・WORKFLOW
4. 正規WorkspaceおよびGitルート
5. `database/fund_stock.db` の存在
6. SOSIA FAND Consoleの現行構造
7. 株価DBの現行スキーマ
8. 既存未コミット変更

既存資産との衝突、正規Workspace不一致、重大な未コミット変更その他の安全上の問題がある場合は停止してNoriへ報告する。

## 04）実装対象

### A. Data Request

SQLを直接渡さず、要求内容を構造化して受け付ける。

最低限以下を扱う。

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

今回対応する `action` は `get_price_series` のみとする。

### B. Data Gateway

Data Requestを解釈し、`fund_stock.db` から必要な情報を取得する。

Data Gatewayは原則として**読み取り専用**とする。

SQL、テーブル名、カラム構造その他のDB固有処理はGateway内部へ隠蔽し、要求側がDBスキーマを直接指定しない構造とする。

### C. Data Response

最低限、処理結果を追跡できる形式を実装する。

成功例：

```json
{
  "version": "1.0",
  "request_id": "DR-xxxxxxxx",
  "status": "success",
  "symbol": "7203",
  "timeframe": "D1",
  "count": 100
}
```

株価系列そのものは、Console表示に必要な範囲でローカル処理する。

大量の株価データをGitHubへ保存することは行わない。

### D. Console Command

Data Gateway側とConsole側の境界を明確にするため、表示要求を構造化する。

最低限：

```json
{
  "version": "1.0",
  "command_id": "CC-xxxxxxxx",
  "action": "show_chart",
  "symbol": "7203",
  "timeframe": "D1",
  "bars": 100
}
```

### E. SOSIA FAND Console

既存Consoleの構造を確認し、必要最小限の変更で7203の日足チャートを表示する。

既存機能を利用できる場合は新規実装を避ける。

変更が必要な場合も、本検証に直接必要な範囲だけとする。

大規模リファクタリングや既存画面構成の再設計は行わない。

## 05）エラー処理

最低限、以下を識別できるようにする。

- `SYMBOL_NOT_FOUND`
- `DATA_NOT_FOUND`
- `INVALID_REQUEST`
- `DB_ERROR`
- `UNSUPPORTED`

不明な情報を推測・補完して正常応答として扱わない。

エラー発生時も `request_id` を保持し、要求との対応関係を追跡できるようにする。

## 06）許可する変更

Noriが本作業指示を承認した場合、今回の目的達成に必要な範囲に限り、

- Data Gateway試作コードの新規作成
- Gateway用テストコードの作成
- Request / Response / Console Commandの試験用ファイル作成
- SOSIA FAND Consoleの必要最小限のコード変更

を許可する。

変更対象ファイルは作業完了報告で明示する。

## 07）禁止事項

以下を行わない。

- `fund_stock.db` の更新・削除・スキーマ変更
- FChart原本の変更
- データ補正方式の変更
- ROLE・WORKFLOW・入口文書の変更
- 永続記憶運用の変更
- AI間通信運用の変更
- GitHub Actions導入
- Webhook導入
- GitHub常時監視
- Codex自動起動
- ChatGPTからGatewayへの自動送信
- MCP導入
- OpenAI APIまたは新規有料サービス導入
- 投資判断・売買評価
- RSI等の追加インジケータ実装
- 今回の目的に不要な大規模リファクタリング
- 既存未コミット変更の上書きまたは混入

## 08）GitHubの扱い

今回、GitHubをData Requestの自動搬送経路として正式運用しない。

将来想定する

```text
ChatGPT
   ↓
GitHub
   ↓
Data Gateway
```

部分は、今回のローカル検証成功後に別工程として検証する。

`Gateway/requests/`、`Gateway/responses/`、`Gateway/commands/` などのGitHub上の保存場所も、今回は正式確定しない。

## 09）検証シナリオ

入力：

```text
トヨタ自動車（7203）
日足
直近100本
チャート表示
```

確認する経路：

```text
Data Request
     ↓
Data Gateway
     ↓
fund_stock.db
     ↓
Data Response
     ↓
Console Command
     ↓
SOSIA FAND Console
```

確認項目：

1. Data Requestを正しく解釈できる
2. 7203を対象として認識できる
3. DBを読み取り専用で参照できる
4. 日足100本を取得できる
5. Data Responseを生成できる
6. Console Commandへ受け渡せる
7. Consoleへチャート表示できる
8. Request ID等で処理経路を追跡できる
9. DBおよび既存資産が変更されていない

## 10）安全確認

実行前後で最低限、

- `fund_stock.db` の変更有無
- FChart原本の変更有無
- 既存コードへの意図しない変更
- 既存未コミット変更への影響

を確認する。

DBについては読み取り専用接続または同等の安全措置を採用する。

## 11）成果物

最低限、以下を提出する。

- Data Gateway試作コード
- Request実例
- Response実例
- Console Command実例
- Console表示結果
- 変更ファイル一覧
- 検証結果
- DB非変更確認結果
- 既存資産保全確認結果
- 問題点・制約
- 次段階への改善候補
- 作業完了報告書

## 12）報告経路

本作業に限り、Chief Manager「こう」は結果を**Noriへ直接報告する**。

これは旧バフェットROLEまたは既存AI間通信運用の恒久変更を意味しない。

Codex側バフェットROLEが再設計対象となっているため、本検証で旧バフェットを新たな通信・記憶管理主体として利用しない。

## 13）技術検証の完了条件

次のすべてを満たした場合、本作業の技術検証を完了候補とする。

- 7203の日足100本を取得できる
- Data RequestからConsole Commandまで追跡できる
- SOSIA FAND Consoleにチャート表示できる
- `fund_stock.db` を変更していない
- FChart原本を変更していない
- 既存資産を毀損していない
- 実施内容と検証結果が報告されている

最終的な完了承認はNoriが行う。

## 14）本作業後に判断する事項

今回の結果を確認してから、次を判断する。

1. Data Gatewayの正式採用
2. Gatewayインターフェース仕様の正式化
3. GitHub上のGateway保存領域
4. ChatGPT → GitHub → Gateway連携
5. GitHub監視方式
6. ChatGPTのGitHub書込み権限
7. ソロスROLE
8. AI間通信・永続記憶管理の新しい責任主体
9. RSI・移動平均・スクリーニング等への機能拡張

今回はこれらを確定しない。
