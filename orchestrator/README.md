# INCAGENT Dev Pipeline (automated)
Opus(PM) → Fable(Architect) → Sonnet(piping) → Codex(impl) を1コマンドで。

## 使い方
    export ANTHROPIC_API_KEY=... OPENAI_API_KEY=...
    pip install anthropic openai
    python orchestrator/pipeline.py --task-file refactor-instructions.md --dry-run
    python orchestrator/pipeline.py "D1 を完遂しろ"           # Codex直前で確認
    python orchestrator/pipeline.py "D1 を完遂しろ" --auto-codex  # 無人実行

各段の出力は orchestrator/artifacts/ に時刻付きで保存（監査可能）。
土管(Sonnet)の出力は GOAL_SCHEMA 固定構造から整形されるので、Codexは常に同じ形を受け取る。
Codex実行は「金とコードが動くフェーズ」なので既定で人間確認を挟む（INCAGENTの稟議思想）。
