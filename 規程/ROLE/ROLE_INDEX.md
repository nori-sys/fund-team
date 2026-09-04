# FUND ROLE_INDEX

## 基本原則

- 本書は現行ROLEの参照索引であり、権限を新設・拡張・確定しない。状態欄は確認日時と根拠参照を伴う索引情報であり、発効認定、現行性の確定または権限付与を行わない。
- 本書に定める通信・監査関係および新設ROLEの適用は、Noriが本運用基盤の正式発行を明示承認した後だけ開始する。既存ROLEの有効性および既存の承認済み作業指示は、本書によって変更しない。
- ROLE IDはファイル名から拡張子を除いた一意の文字列とする。索引にないROLEは実行、通信または権限の根拠にしない。

## ROLE一覧

| ROLE ID | 状態（確認日時・根拠参照） | 担当AI | 役割 | ROLEファイル |
| --- | --- | --- | --- | --- |
| `ROLE_FUND_バフェット_Advisor` | 現行（2026-09-01確認、`AGENTS.md`「ROLE・通信・記憶」） | バフェット | オーナー直属アドバイザー兼主担当AI | `規程/ROLE/ROLE_FUND_バフェット_Advisor.md` |
| `ROLE_FUND_こう_ChiefManager` | 現行（2026-09-01確認、`AGENTS.md`「ROLE・通信・記憶」） | こう | Chief Manager | `規程/ROLE/ROLE_FUND_こう_ChiefManager.md` |
| `ROLE_FUND_カズ_DataManager` | 現行（2026-09-01確認、`AGENTS.md`「ROLE・通信・記憶」） | カズ | Data Manager | `規程/ROLE/ROLE_FUND_カズ_DataManager.md` |
| `ROLE_FUND_カン_監査` | 現行（2026-09-01確認、`AGENTS.md`「ROLE・通信・記憶」） | カン | 独立監査 | `規程/ROLE/ROLE_FUND_カン_監査.md` |

## 整合規則

1. 各ROLEの具体的な責任、権限および制約は当該ROLEファイルを優先する。
2. 通信の条件、状態、正本および保存先は `規程/WORKFLOW/AI間通信運用.md` に従う。索引の記載は通信権限を拡張しない。
3. 本書またはROLEの更新、新設、廃止、通信関係の変更にはNoriの明示承認を必要とする。
