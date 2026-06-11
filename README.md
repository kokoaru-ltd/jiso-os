# INCAGENT — Autonomous Business OS

**社長の仕事は、承認だけになる。**

やりたいことを一度だけ伝えると、AIが市場調査・広告・営業・請求まで自走する企業OS。
費用が必要なときだけ、想定ROIと撤退条件つきの「稟議」が人間に届く。

## 構成

```
apps/web        — LP・管理画面（現在: 静的LP / 予定: Next.js）
apps/engine     — /loop ワーカー（観測 → 計画 → 稟議起票 → 執行 → 答え合わせ）
packages/ringi  — 稟議エンジン（スキーマ・型定義）
packages/funnel — 8段ファネルの業種別パラメータ
docs            — アーキテクチャ
```

## 中核思想

1. **AIは訊かない** — 指示を待たず、数字を観測して次の一手を計画する
2. **金が要るときだけ稟議** — 想定ROI・POC設計・撤退条件のない申請は存在を許されない
3. **予測は必ず答え合わせ** — 試算と実測の乖離はAI自身の信用スコアになる

## インフラ

- DB: Supabase（schema: `loop` / RLS有効）
- 音声営業: ElevenLabs + Twilio
- 画像生成: gpt-image-2 / 動画生成: Seedance 2.0
- 外部スキル導入: SkillSpectorスキャン必須ゲート

運営: 合同会社ココアル
