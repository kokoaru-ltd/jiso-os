# Capability Acquisition（自己拡張）
能力が足りないとき、OSが自分でスキルを拾って取り込む。
- registry/catalog.json : anthropics/skills の17スキルをインデックス化
- scripts/skill_acquire.py : 能力要求 → カタログ検索 → セキュリティスキャン → 自動取込 or 隔離
- cache/ : 取り込み済みスキル

## ゲート（SkillSpector思想の軽量版）
危険パターン(curl|sh, rm -rf, eval, 認証情報吸出し 等)を検出しスコア化。
75点以上=自動取込 / 未満=人間承認待ち隔離。全取込はaudit_logに記録。
