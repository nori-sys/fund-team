# CURRENT_CONTEXT

## 現在の状態

SOSIA FANDは基盤整備を終え、本来のシステム設計・改善へ戻っている。
現在の重点テーマはデータ基盤であり、企業業績データ基盤の再調査を開始する直前。

## 役割

- Nori: オーナー・最終意思決定者
- ChatGPT側「チャット」: SOSIA FANDシステム構築アドバイザー
- Codex側: 実装・検証・データ処理・分析その他の実作業
- カン: 独立監査担当
- GitHub: 共有・履歴・参照用ミラー層
- ローカルWorkspace: 規程、実装、重要資産の正本

## 開発方針

SOSIA FANDは「完成してから使う」のではなく、「使いながら育てる」システムとして進める。
実銘柄での問い合わせ・分析を開発と並行して行い、実運用で見つかった不足を次の改善要件へ反映する。
土台は堅く、機能は柔軟にする考え方を重視する。
この考え方の正式な「システム設計原則」文書化は保留中。

## データ基盤の現状

- 日足株価DB: 構築・差分更新・整合性検証済み
- 銘柄マスター: 利用可能。UNKNOWN調査実施済み
- 週足: 日足から生成・差分更新可能
- 月足: 正式仕様化・実装済み
- Data Gateway: 1D / 1W / 1M READ ONLYで利用可能
- 株式分割補正: `kenri.ini` を情報源として特定済みだが、完全仕様は未確定
- 企業業績データ: 初期解析まで。正式SQLite化は未完了
- FX・マクロ等: 未着手

## 企業業績データ基盤

過去解析対象:
- `C:\fchart\gyoseki\kigyo.dat`
- `C:\fchart\gyoseki\kigyo2.dat`
- `C:\fchart\gyoseki\kigyo3.dat`
- `C:\fchart\gyoseki\Zaimu.dat`
- `C:\fchart\kabu.lst`

過去成果物:
- `作業履歴/20260722-01/`

既知:
- kigyo.dat: 823 byte × 10,462 record
- kigyo2.dat / kigyo3.dat: 330 byte × 10,462 record
- Zaimu.dat: 正確な構造未確定
- 財務項目名、単位、倍率、小数点位置、欠損表現は未確定
- 正式SQLite投入は保留

## 現在の作業指示案

GitHub:
`ChatGPT/作業指示案/20260920-1406_FAND_企業業績データ基盤再調査_作業指示書案.md`

commit:
`2b4c27078608aa634f540ddf9c0e0c4163c2ad15`

内容:
- kigyo.dat / kigyo2.dat / kigyo3.dat / Zaimu.dat / kabu.lst の再調査
- 銘柄対応関係の再確認
- 構造・項目候補・Zaimu.datの追加調査
- 正式SQLite化可能範囲と保留範囲の分離
- Data Gateway連携に必要な前提整理
- 本作業では正式SQLite実装、Data Gateway、Console等は変更しない

Noriは作業内容を承認済み。

## 正規Workspaceパス問題

正しい正規Workspace:
`E:\AI ワークスペース\CODEX\ファンドチーム_Workspace`

実際の `git rev-parse --show-toplevel`、ローカル `AGENTS.md`、`START_HERE.md` は一致確認済み。
`ファンドチーム\_Workspace` のように表示変形する現象は、貼り付け・Markdown等のエスケープ処理の可能性が高い。
実体のGitルート・正式文書には問題なし。

再発防止:
- 個別Codex指示では正規Workspace絶対パスを原則再記載しない
- 正規Workspaceは正式入口文書と実際のGitルート確認結果を基準とする

## 作業指示書案作成基準 改定

正式文書:
`ChatGPT/運用/作業指示書案作成基準.md`

今回追加:
- 正式文書で定義済みの正規Workspace絶対パスは個別作業指示へ原則再記載しない
- 正規Workspaceの確認は入口文書および実際のGitルート確認結果を基準とする
- 作成時確認に「必要性なく絶対パスを再記載していない」を追加

GitHub commit:
`caafcd96d9846d5ae4ac3ee820116623c844b7b0`

GitHub blob:
`914aa27693ac8a78ede9a02a58e7095120cc3627`

ローカル正本へ同期済み。
ローカルSHA-256:
`750FC77225D1B97B29ABC50E536DE80FCA9707E73F2E3723EFCF4DCD32C16883`

GitHub対象コミットとの正規化本文比較: True
他資産への非干渉確認済み。

## Data Gateway

Data Gateway可変Request化 Phase 2修正版は実装・検証・独立監査まで完了済み。
Gatewayは `1D / 1W / 1M` READ ONLY。
月足生成・差分更新・Payload契約・DB保全を検証済み。
カン最終監査: `適合（承認可）`。
未決事項なし。

## 次スレッド

次に行うこと:
企業業績データ基盤の再調査をCodexで再開する。

注意:
- 正規Workspace絶対パスを貼り付け指示へ再掲しない
- Gitルートと正式入口文書を基準に開始条件を判定する
- 過去の仮説を確定事項として扱わない
- FChart原本・既存SQLite・Data Gateway・Console等を本調査で変更しない
