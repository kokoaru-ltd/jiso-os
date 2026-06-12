# INCAGENT — セッション引き継ぎ手順（新チャットの冒頭にこれを貼る）

## このプロジェクトは何か
自律経営OS「INCAGENT」（国内名: 自走）。やりたいことを一度伝えると、AIが市場調査・営業・請求まで自走し、
費用が要るときだけ「APPROVAL REQUEST（稟議）」が人間のSlackに届く。承認するまで1円も動かない。
運営: 合同会社ココアル（代表 近藤）。海外ブランド INCAGENT / @incagentai、国内 @kondo_ceollc。

## 現在の到達点（本番稼働・テスト済み）
- 稟議エンジン: 起票→Slack通知→承認→執行遷移→監査ログ（全部DBで動く）
- 毎時cronで自走ループが回る（人間不要で観測→稟議起票）
- 予算上限¥10万＋フェーズゲート（構造的に超過不能）
- Stripe決済: checkout→入金検知→売上記録→Slack通知（E2E済み）
- Slack通知は全部英語（APPROVAL REQUEST = 稟議）
- DB実データから投稿画像を自己描画
- スキル自己取得ループ（anthropic/skills 17個をカタログ化、セキュリティスキャン付き）
- 4モデル開発パイプライン（Opus→Fable→Sonnet→Codex）orchestrator/pipeline.py

## インフラ（実体の場所）
- GitHub: github.com/kokoaru-ltd/incagent-os （※旧名 jiso-os。リネーム未完了なら旧名でclone）
- Supabase: project_id = wckfqfjzpmjkznhnfaqb（アポトレールα内の "loop" スキーマに同居）
- Slack: Incoming Webhook 設定済み・稼働中
- 本番Edge Functions: signup / ringi / loop-tick / checkout / stripe-webhook
- admin secret: 136e79310a29a79c0f1c45c2e835bf403597b29c718a7218（loop.config保管）

## 重要な設計ルール（壊すと事故る）
- スキーマ名 "loop" は plpgsql 予約語。関数内では必ず "loop" と二重引用符付きで参照
- RPC/トリガーの実体は本番DBにのみ存在（migrationファイルは記録のみ＝負債D1）
- 本番cron稼働中。破壊的SQL禁止
- 秘密情報はチャットに貼らない。APIキーは最小権限・短期限・使用後失効

## 次にやること（このセッションで止まっていたこと）
**路線確定: 英語・Freelancer.comで仕事を受けて初売上を立てる**
（マーケット出品の経営診断はレビューゼロ新規には不利と判断。Freelancerは案件に入札する方式で勝てる）

売る物 = OSが人手ゼロで完納できる仕事: リスト作成 / 市場調査 / データ整形

### 最優先で作るもの: 納品物ジェネレーター（未実装の核心）
「受注→OSがCSV/レポートを実際に自動生成→納品→入金」のループ。
これが動けば「自走する会社」が主張でなく事実になる。

## 事前準備の状態（ユーザー側）
- [x] .env に OPENAI_API_KEY と X4本（X_API_KEY/SECRET/ACCESS_TOKEN/ACCESS_SECRET）記載済み
- [x] .env に FREELANCER_TOKEN 記載済み
- [ ] 許可ドメイン追加（claude.ai/settings/capabilities）:
      www.freelancer.com / api.x.com / api.twitter.com / upload.twitter.com / api.openai.com
      → これが済んでいれば新チャットのClaudeが直接 入札/投稿/画像生成できる
- [ ] GitHubリポジトリのリネーム jiso-os→incagent-os（Web/Settingsで。Administration権限要）

## 新チャットでの最初のコマンド
```
git clone https://github.com/kokoaru-ltd/incagent-os.git   # 旧名なら jiso-os
cd incagent-os
# .env は手元のローカルにある。新チャットのClaude環境で動かすなら環境変数で渡す
```

## 動かすスクリプト
- scripts/freelancer_worker.py … 案件検索→採点→提案下書き→Slack承認（--dry-run可）
- scripts/post_to_x.py … @incagentai 投稿（--dry-run可）
- scripts/render_ringi_card.py … 稟議カード画像を自己描画
- scripts/skill_acquire.py … スキル自己取得
- orchestrator/pipeline.py … 4モデル開発パイプライン

## ユーザー（近藤）の方針メモ
- 結論から・数字で・前置き不要。クレジット消費以外の先払い現金は避ける
- 「動作の実演」より「実売上1円」を優先。仕事が回って自動化されることが最重要
- 回答は日本語
