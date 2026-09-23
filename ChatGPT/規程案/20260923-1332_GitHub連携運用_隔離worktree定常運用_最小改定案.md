# GitHub連携運用.md 隔離worktree定常運用・最小改定案

> 状態：未承認案  
> 対象：`規程/WORKFLOW/GitHub連携運用.md`  
> 目的：隔離worktreeを一定条件下で標準安全手順として利用可能にし、Noriによる毎回の個別許可を不要にする。

## 1. 改定目的

正規Workspaceに既存未commit変更、未追跡資産又はbranch分岐が存在する場合でも、それらへ干渉せず、公開対象だけを安全にGitHubへ反映できるようにする。

これまでNoriの個別明示承認を必要としていた隔離worktree方式を、所定条件を満たす場合の定常的な安全手順として扱う。

## 2. 改定方針

改定範囲は必要最小限とする。

現行 `規程/WORKFLOW/GitHub連携運用.md` のうち、「GitHub操作の承認経路」→「書込み」にある隔離worktreeの例外扱い部分だけを改定し、次の既存原則は維持する。

- GitHubは参照用ミラーであり正本ではない。
- 公開禁止情報の規定を維持する。
- 個別作業指示による公開区分を維持する。
- force push等の高リスク操作の禁止・承認条件を維持する。
- remote、Git設定及び認証方式の変更制限を維持する。
- non-fast-forward、競合及び公開安全性疑義時の停止を維持する。
- 正規Workspace及び既存資産の保護を維持する。
- commit ID、送信対象、公開安全性等の記録義務を維持する。
- Noriによる正式規程の最終承認権限を維持する。

## 3. 改定対象

### 現行記載

既存未commit変更、未追跡ファイル又は別作業の変更があるWorkspaceでは、これらを安易な `pull`、`merge`、`rebase`、`reset` 又は `stash` で処理しない。定常手順では正規Workspace外の一時worktreeを利用しない。Noriが対象worktreeを明示承認した個別例外では、worktree内で正本又は保全対象を更新せず、対象変更だけを安全に分離できる場合に限る。non-fast-forward、競合又は分岐を検知した場合は、対象変更だけを安全に分離できない限り停止する。

### 改定案

既存未commit変更、未追跡ファイル又は別作業の変更があるWorkspaceでは、これらを安易な `pull`、`merge`、`rebase`、`reset` 又は `stash` で処理しない。

GitHubへの送信対象を明確に限定でき、かつ公開条件が確定している場合は、正規Workspaceの既存変更及び保全対象へ干渉しないため、最新 `origin/main` を起点とする隔離worktreeを定常的な安全手順として利用できる。

隔離worktreeを利用する場合は、次をすべて満たさなければならない。

1. 正規Workspace、対象リポジトリ、remote及び最新 `origin/main` を確認する。
2. 個別作業指示又は承認済み運用によりGitHub送信対象及び公開区分が確定している。
3. 隔離worktreeは最新 `origin/main` を起点として作成する。
4. 送信対象ファイルだけを隔離worktreeへ反映し、commit対象を限定する。
5. 正規Workspaceの既存未commit変更、未追跡資産、別作業資産、正本又は保全対象を変更しない。
6. commit前にstage対象と公開安全性を確認する。
7. push直前に、送信commitの親commitと最新 `origin/main` の一致を確認する。
8. GitHub `main` への反映はfast-forwardとなる場合だけ実施する。
9. force push、reset、rebase、remote変更、Git設定変更又は認証変更を行わない。
10. 作業終了後、隔離worktreeの一時資産が正規Workspace又は成果物として残存しないことを確認する。

non-fast-forward、競合、対象変更の安全な分離不能、公開安全性への疑義又は前記条件を満たせない状態を検知した場合はpushせず停止し、Noriへ報告する。

上記条件を満たす隔離worktreeの利用については、個別のworktree作成許可を追加でNoriへ求める必要はない。

## 4. 改定による運用効果

- Noriが毎回同じ隔離worktree許可をCodexへ入力する必要がなくなる。
- 正規Workspaceに未commit変更や分岐がある場合でも、それらへ触れずに公開対象だけを分離できる。
- `origin/main` 起点、対象限定commit、push直前確認、fast-forward限定により、履歴破壊や誤混入のリスクを抑制できる。
- high-risk操作は引き続きNori承認が必要であり、権限拡大にはならない。

## 5. 変更しない事項

本改定では、以下は変更しない。

- GitHubの位置付け
- 公開禁止情報
- 公開区分
- 正本管理
- 正式発行手順
- 監査手順
- 高リスク操作の承認条件
- Noriの最終承認権限

## 6. 承認状態

本書は未承認案であり、正式WORKFLOWを変更しない。

正式反映は、独立監査で「適合（承認可）」となった後、Noriの正式承認を受け、正式発行手順に従って行う。
