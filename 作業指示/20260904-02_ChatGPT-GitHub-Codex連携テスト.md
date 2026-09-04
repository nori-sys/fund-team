# ChatGPT → GitHub → Codex 連携テスト

作業ID: 20260904-02  
対象プロジェクト: ファンドチーム  
発行者: ChatGPT（チャット）  
最終承認者: Nori  
目的: ChatGPT → GitHub → Codex の一方向連携確認

## 確認用識別子

FUND-GITHUB-LINK-20260904-02

## 作業目的

GitHubを受け渡し層として利用し、ChatGPT側で発行した作業指示をCodex側が直接取得・確認できることを検証する。

今回のテストは連携成立の確認のみを目的とし、GitHub運用方式の正式導入、規程変更、自動同期、自動実行を意味しない。

## Codexへの指示

1. 作業開始前に、現行の `AGENTS.md` および `START_HERE.md` に従い、正規作業場所とGitルートを確認する。
2. 正規作業場所確認後、GitHub上の本ファイルを取得または確認する。
3. 本文中の確認用識別子 `FUND-GITHUB-LINK-20260904-02` を読み取る。
4. 本テストでは、指示内容の確認以外のWorkspace変更、規程変更、DB変更、コード変更、Git設定変更を行わない。
5. 認証情報、APIキー、token、秘密鍵等を表示・記録・変更しない。
6. 本ファイルを確認できた場合、Noriへ以下を報告する。

```text
作業ID: 20260904-02
結果: 成功 / 失敗 / 停止
確認用識別子: FUND-GITHUB-LINK-20260904-02
取得元: GitHub
対象リポジトリ: nori-sys/fund-team
対象ファイル: 作業指示/20260904-02_ChatGPT-GitHub-Codex連携テスト.md
Workspace変更: なし
未解決事項: なし / 内容を記載
```

## 合格条件

以下をすべて満たした場合、Codex側の受信確認を合格候補とする。

- GitHub上の本ファイルをCodex側から確認できる
- 確認用識別子を正しく読み取れる
- Noriによるファイルの手動受け渡しを行っていない
- 本テストのためにWorkspace内の保護対象や既存資産を変更していない
- Git設定・認証方式・remote設定を変更していない

最終的な第2段階の成功判定は、Codexからの報告内容をNoriとChatGPTが確認した後に行う。

## 今回行わないこと

- GitHub運用の正式規程化
- ChatGPTからの自動通知
- Codexの自動起動
- 自動pull
- 自動commit / push
- GitHub Actions / Webhook
- AI間通信運用の正式変更
- 会話DB連携
- Workspace構成変更
- 規程・ROLE・WORKFLOWの変更
