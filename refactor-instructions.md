# refactor-instructions.md

`/goal` で実装担当モデル（Codex / Opus 等）に渡す指示書。
**この指示書に書かれたことだけを、書かれた順に完遂すること。証拠なく大きな削除・全面書き換えをしないこと。**

---

## Objective

INCAGENT（自律経営OS）のコードベースについて、**既存の本番稼働挙動を一切壊さずに**、最大の構造的負債である「ロジックの実体がリポジトリに存在しない（本番DBにしか無い）」状態を解消し、`git clone` だけでシステムを再現・再デプロイできる状態にする。あわせて死コードの整理と秘密情報の取り扱いを是正する。**見た目の綺麗さは目的ではない。再現性と安全性が目的。**

---

## Project Understanding（証拠ベース）

- **何をするものか**: 目標・予算・権限を渡すと、市場調査→施策提案→（費用が要れば）稟議起票→人間承認→実行→実測→次の打ち手、を回す自律経営OS。費用の発生する行動は必ず承認を要する（README.md, docs/COMPANY_STRATEGY.md）。
- **主要ワークフロー**: 「OSが稟議(approval request)を起票 → Slackへ通知 → 人間がコンソールで承認 → 次のループ周回で executing へ遷移 → 監査ログ記録」。
- **エントリーポイント（実際に動いているもの）**:
  - Supabase Edge Functions: `signup` / `ringi` / `loop-tick`（いずれも本番デプロイ済み・稼働中）
  - pg_cron ジョブ `jiso-loop-tick`（毎時0分に loop-tick を叩く・**本番で生きている**）
  - 静的: `apps/web/public/index.html`（LP）, `apps/console/ringi.html` / `ringi-en.html`（承認UI）
  - CLIスクリプト: `scripts/{post_to_x,freelancer_worker,render_ringi_card,skill_acquire}.py`
- **主要モジュールと責務**:
  - `packages/ringi/migrations/*.sql` … DBスキーマ（`loop`スキーマ）とRPC・トリガーの**記録**
  - DB側RPC関数（本番に存在）: `jiso_signup` `jiso_ringi_list` `jiso_ringi_decide` `jiso_loop_tick` `jiso_check_secret`
  - DB側トリガー（本番に存在）: 稟議起票/状態遷移/人間タスクで Slack 通知
  - `packages/funnel/industry-params.json` … 業種別ファネル係数
  - `packages/persona/kondo-model.md` … エージェント共通の判断原則
  - `packages/skills/` … スキル自己取得（catalog + skill_acquire.py + cache）
- **データの流れ**: Edge Function → `public.jiso_*` RPC（SECURITY DEFINER）→ `"loop"` スキーマのテーブル。`"loop"` スキーマは PostgREST 非公開のため、外部からは必ずRPC経由でしか触れない。
- **外部依存**: Supabase（DB/Edge/cron/pg_net）, Slack Incoming Webhook, GitHub, （未接続）X API / OpenAI image / Freelancer API。
- **検証コマンド（現状）**: 自動テストは**存在しない**。型チェック/lint/CIも**未設定**。Pythonスクリプトは `--dry-run` を持つものがある（post_to_x.py）。

---

## Behaviors To Preserve（絶対に壊してはいけない）

1. **本番DBの稟議データと状態遷移**: `"loop".ringi` の `status`（pending→approved→executing 等）の遷移ロジックと制約。
2. **RPC経由のアクセス境界**: anon/authenticated から `"loop"` スキーマや `jiso_*` 関数を実行できない現在の権限設計（service_role のみ実行可）。
3. **Slack通知の発火**: 起票🔴/承認🟢/執行▶️/却下⛔/人間タスク👤 の各トリガー。文面は英語が現行。
4. **予算ガード**: `"loop".config` の `budget_cap_yen`(=100000) と `phase_gate`。OSがこれを超える/飛ばす挙動を新たに生んではならない。
5. **cron `jiso-loop-tick`**: 毎時稼働。停止・再定義する変更は禁止（後述のStop and Ask対象）。
6. **承認シークレット認証**: `ringi` / `loop-tick` Edge Function の `x-jiso-secret` チェック。

---

## Non-Negotiables

- 本番Supabaseプロジェクト `wckfqfjzpmjkznhnfaqb` に対し、**破壊的SQL（DROP/DELETE/TRUNCATE/ALTER...DROP）を実行しない**。スキーマは追加・冪等化のみ。
- 既存の公開挙動（Edge Function の I/F、RPCのシグネチャ）を変更しない。
- `"loop"` は plpgsql 予約語と衝突する。**関数本体でスキーマを参照する箇所は必ず `"loop"` と二重引用符付き**で書く（無引用は過去に2度バグを生んでいる）。
- 秘密情報（admin_secret, Slack webhook, 各APIキー）を新たにコードへ平文で書かない。
- 無関係な整形・命名変更・「ついで」のリファクタを混ぜない。

---

## Stop And Ask Conditions（実装を止めて人間に質問する）

1. **loop.ts と jiso_loop_tick() のどちらを正とするか**: 現在ループの実体はSQL関数 `jiso_loop_tick()`。`apps/engine/src/loop.ts` は全関数が空スタブの死コード。**「TS側を正として実装を移すのか／TSを削除してSQLを正とするのか」はプロダクト判断**。勝手に決めず確認する。
2. **cron停止を伴う変更**が必要になった場合（スキーマ名 `loop`→別名へのリネーム等）。本番の自走が止まるため必ず確認。
3. **`config` テーブルの秘密情報をEdge Function環境変数へ移す**際、移行中に認証が切れる可能性。切替手順の承認を取る。
4. テストが書かれた結果、**実装の現挙動とテスト期待が矛盾**した場合、どちらを正とするか確認。
5. スキーマ名 `loop` のリネーム可否（予約語衝突の恒久解だが、本番テーブル・RPC・cron・Edge Functionの全同時変更が必要なため高リスク）。

---

## Baseline Commands

> 現状CIなし。まず以下を「現状の事実」として記録してから着手する。

```bash
git status                          # 未コミット変更の有無を必ず最初に確認
find . -type f -not -path './.git/*' | sort
python3 -c "import ast,glob; [ast.parse(open(f).read()) for f in glob.glob('scripts/*.py')]"  # py構文チェック
python3 scripts/post_to_x.py --dry-run
python3 scripts/freelancer_worker.py --dry-run
python3 scripts/skill_acquire.py "プレゼン スライド 作成"
```

本フェーズで導入すべきbaseline（なければ追加）: `package.json` に tsc（loop.ts用）、Python は `python -m py_compile`、SQLは適用前に**ローカル/ブランチDBでのdry-run**。

---

## Debt Map

### D1. ロジックの実体がリポジトリに無い（最優先・実装可）
- **根拠**: `packages/ringi/migrations/0002_rpc_layer.sql` `0003_slack_notify.sql` `0004_execution_layer.sql` は中身がコメントのみ。実体のRPC関数・トリガー定義は本番DBにしか存在しない。
- **なぜ負債か**: `git clone` でシステムを再現できない。DB障害＝復旧不能。レビュー不能。
- **影響範囲**: 全システムの再現性・DR。
- **変更リスク**: 低（**新規ファイルにDBの現定義を書き起こすだけ。本番DBには触らない**）。
- **改善案**: 本番に適用済みの `jiso_*` 関数・トリガーの**現定義を冪等な `CREATE OR REPLACE` 形式でmigrationファイルに書き起こす**。Supabaseのマイグレーション履歴/関数定義(`pg_get_functiondef`)をソースオブトゥルースとして転記。
- **検証方法**: 別のSupabaseブランチ/ローカルに migration を端から適用し、`jiso_loop_tick()` 実行→pending稟議が起票されることを確認。
- **判断**: **今実装してよい**（本番に触れず、ファイル追加のみ）。

### D2. loop.ts が死コード（要確認）
- **根拠**: `apps/engine/src/loop.ts` の observe/planAction/execute 等が全て空 `return [] / {}`。実ループは `jiso_loop_tick()`。
- **なぜ負債か**: 動かないコードがリポジトリの「顔」。二重定義で混乱を生む。
- **変更リスク**: 中（プロダクト判断が絡む）。
- **改善案**: Stop and Ask #1 で方針確定後に、(a)TSを正とし実装移管、または(b)TSを `docs/` へ参考として退避しSQLを正と明記。
- **判断**: **提案に留める**。方針確定まで実装しない。

### D3. 秘密情報が config テーブルに平文（実装可・要切替承認）
- **根拠**: `"loop".config` に `admin_secret` と `slack_webhook_url` が平文。
- **改善案**: Edge Function の環境変数（Supabase secrets）へ移し、RPC/トリガーは関数引数か `vault` 参照に変更。切替時の無停止手順を用意。
- **変更リスク**: 中（認証断の可能性）→ Stop and Ask #3。
- **判断**: **安全網（テスト）作成後に実装可**。切替手順は承認を取る。

### D4. スキーマ名 `loop` が予約語衝突（提案のみ）
- **根拠**: 過去にFORループ・配列リテラルで2度の構文事故。回避のため全箇所 `"loop"` 引用符付きで運用中。
- **改善案**: 恒久解は `jiso` 等へリネームだが、本番テーブル/RPC/cron/Edge Functionの同時移行が必要。
- **判断**: **提案に留める**（Stop and Ask #5）。当面は「引用符付き必須」をlint的に担保するのみ実装可。

### D5. 自動テスト・CI・型チェックが皆無（実装可）
- **根拠**: テストファイル/CI設定なし。
- **改善案**: 後述 Phase 2 で最小の安全網（スクリプトのsmokeテスト、RPCのSQLテスト、tscによるloop.tsの型確認）を追加。
- **判断**: **今実装してよい**（既存挙動を変えない追加のみ）。

### D6. ファイル散在の軽微な不整合（実装可・低優先）
- **根拠**: `scripts/__pycache__/*.pyc` がコミットされている。`.gitignore` に `__pycache__/` 追記漏れ。
- **改善案**: `.gitignore` に追加し追跡解除（`git rm --cached`）。
- **判断**: **今実装してよい**（安全）。

---

## Implementation Phases（小さく安全な順）

**Phase 0 — 現状確認**: `git status` で未コミット変更の有無を確認。Baseline Commands を実行し結果を記録。

**Phase 1 — 安全網（D5の最小版）**: 既存挙動を変えずにテストだけ追加。
- Pythonスクリプトの `--dry-run` smokeテスト
- `jiso_*` RPCの期待I/Oを記述したSQLテスト（pgTAP or 単純なassert SQL）。本番ではなくブランチ/ローカルDBで。

**Phase 2 — D1（最優先・安全な書き起こし）**: 本番DBの現関数・トリガー定義を冪等migrationに転記。本番には適用しない。ブランチDBで全適用→loop-tick動作確認。

**Phase 3 — D6（安全な整理）**: `.gitignore` 整備、`*.pyc` の追跡解除。

**Phase 4 — D3（秘密情報移行）**: Phase 1の安全網が通ることを確認後、環境変数化。無停止切替手順を承認のうえ実施。

**Phase 5 — 提案のみ（D2/D4）**: loop.ts の扱い・スキーマリネームは設計提案書として出力。**実装しない**。

---

## Verification Requirements

- 各フェーズ後に Baseline Commands を再実行し、結果を before/after で記録。
- D1検証: 別DB（Supabaseブランチ推奨）に全migrationを順に適用→ `select jiso_loop_tick();` が成功し pending 稟議が起票されること。
- 本番DBに対する破壊的操作は**ゼロ**であることをログで示す。
- Slackトリガーの文面・発火条件が変わっていないことを差分で確認。

---

## Reporting Format

各フェーズごとに以下を報告:
1. 実行したコマンドと結果（before/after）
2. 変更したファイル一覧と変更理由（1行ずつ）
3. 触れていない既存挙動の確認
4. 次フェーズに進んでよいか、Stop and Ask に該当しないか

最後に: 実行コマンド全ログ、残った提案（D2/D4）、未解決の質問。

---

## Out-of-scope Items

- 新機能の追加（受注→納品の実生産、請求書自動発行、X/Freelancer/OpenAIの実接続）。これらは別タスク。
- LP/コンソールのデザイン変更。
- スキーマ `loop` のリネーム実装（提案のみ）。
- 本番cronの停止・再定義。
- ブランド名・文言の変更。

---

## 実装制約（厳守）

- 最初に `git status`。未コミット変更と自分の変更を混ぜない。
- 編集前にbaseline検証結果を記録。
- 変更は小さく戻しやすい単位。無関係な整形をしない。
- 既存挙動を勝手に変えない。正しさが不明なら止めて質問（Stop and Ask）。
- 各フェーズで検証。最後に実行コマンドと結果を報告。
- 本番Supabaseへの破壊的SQL禁止。スキーマ参照は `"loop"` 引用符付き必須。
