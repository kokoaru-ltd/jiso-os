#!/usr/bin/env python3
"""
INCAGENT Dev Pipeline — Opus(PM) -> Fable(Architect) -> Sonnet(piping) -> Codex(impl)
1コマンドで、開発タスクを計画->設計->整形->実装まで自動で流す。

Setup:
  export ANTHROPIC_API_KEY=...
  export OPENAI_API_KEY=...          # Codex SDK 用
  pip install anthropic openai
Run:
  python orchestrator/pipeline.py "refactor-instructions.md の D1 を完遂しろ"
  python orchestrator/pipeline.py --task-file refactor-instructions.md
  python orchestrator/pipeline.py "..." --dry-run   # 計画/設計/整形だけ。実装はしない
  python orchestrator/pipeline.py "..." --auto-codex # Codexまで自動実行（既定はCodex直前で停止し確認）

設計思想（INCAGENTと同じ）:
  - 各段の出力は artifacts/ に保存（監査可能）
  - Codex実行＝コードと金が動く"実行フェーズ"なので、既定では人間確認を挟む（稟議思想）
  - --auto-codex を付けたときだけ無人実行
"""
import os, sys, json, subprocess, datetime, pathlib, argparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = ROOT / "orchestrator" / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

MODELS = {
    "pm":     "claude-opus-4-8",
    "arch":   "claude-fable-5",
    "pipe":   "claude-sonnet-4-6",
}

# ---- 固定スキーマ（土管の出力契約。Codexが必ず同じ構造で受け取る） ----
GOAL_SCHEMA = """{
  "objective": "string",
  "non_negotiables": ["string"],
  "stop_and_ask": ["string"],
  "baseline_commands": ["string"],
  "phases": [{"name":"string","steps":["string"],"verify":["string"]}],
  "out_of_scope": ["string"]
}"""

PM_PROMPT = """You are the Project Manager (Opus). Read the task and the repo context.
Output ONLY the goal definition in plain prose: what must be achieved, priorities,
and what "done" means. Do not design implementation. Be concrete and evidence-based.
Task:
{task}

Repo context (file list + key docs):
{context}
"""

ARCH_PROMPT = """You are the Senior Architect (Fable). Turn the PM's goal into an
implementation plan. Output ONLY valid JSON matching this schema exactly, no prose,
no markdown fences:
{schema}

Rules: phases must be small and safe-ordered. Preserve existing production behavior.
This repo has landmines: schema name "loop" is a plpgsql reserved word (must be quoted),
RPC/trigger bodies live only in the live DB, and an hourly cron is running in prod.
Never propose destructive SQL on the production DB.

PM goal:
{pm}
"""

PIPE_PROMPT = """You are the piping layer (Sonnet). Take the architect's JSON and emit
the final, self-contained instruction string that will be handed to Codex via /goal.
Keep ALL constraints. Output ONLY the instruction text (no JSON, no commentary).
Begin with: "Complete exactly the following, in order, stopping to ask on any
stop_and_ask condition:".

Architect JSON:
{arch}
"""

def anthropic_call(model, prompt):
    from anthropic import Anthropic
    client = Anthropic()  # reads ANTHROPIC_API_KEY
    msg = client.messages.create(
        model=model, max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

def repo_context():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    docs = ""
    for f in ["README.md", "refactor-instructions.md", "docs/ARCHITECTURE.md"]:
        p = ROOT / f
        if p.exists():
            docs += f"\n--- {f} ---\n" + p.read_text()[:2500]
    return f"FILES:\n{files}\nKEY DOCS:{docs}"

def save(name, text):
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    p = ART / f"{ts}-{name}.txt"
    p.write_text(text)
    print(f"  saved: {p.relative_to(ROOT)}")
    return p

def run_codex(goal_text):
    """Codex CLI (codex exec) または SDK で実装を実行"""
    # CLI 優先（codex exec が非対話実行）。無ければ SDK へフォールバック。
    if subprocess.run(["which", "codex"], capture_output=True).returncode == 0:
        print("  -> codex exec")
        return subprocess.call(["codex", "exec", goal_text], cwd=ROOT)
    try:
        from openai import OpenAI
        client = OpenAI()
        print("  -> Codex via OpenAI Responses API (codex model)")
        r = client.responses.create(model="gpt-5.5-codex", input=goal_text)
        print(r.output_text[:2000])
        return 0
    except Exception as e:
        print(f"  codex unavailable: {e}\n  -> goal saved; run manually: codex exec \"$(cat <goalfile>)\"")
        return 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", nargs="?", default="")
    ap.add_argument("--task-file")
    ap.add_argument("--dry-run", action="store_true", help="plan/design/pipe only; skip Codex")
    ap.add_argument("--auto-codex", action="store_true", help="run Codex without human confirm")
    a = ap.parse_args()
    task = pathlib.Path(a.task_file).read_text() if a.task_file else a.task
    if not task:
        sys.exit("Provide a task string or --task-file")

    print("[1/4] PM (Opus) planning…")
    pm = anthropic_call(MODELS["pm"], PM_PROMPT.format(task=task, context=repo_context()))
    save("1-pm-goal", pm)

    print("[2/4] Architect (Fable) designing…")
    arch = anthropic_call(MODELS["arch"], ARCH_PROMPT.format(schema=GOAL_SCHEMA, pm=pm))
    save("2-arch-plan", arch)
    try:
        json.loads(arch); print("  arch JSON: valid")
    except Exception:
        print("  arch JSON: INVALID — review before proceeding")

    print("[3/4] Piping (Sonnet) formatting for Codex…")
    goal = anthropic_call(MODELS["pipe"], PIPE_PROMPT.format(arch=arch))
    goalfile = save("3-codex-goal", goal)

    if a.dry_run:
        print("\n[dry-run] stopping before Codex. Goal file ready:", goalfile)
        return
    if not a.auto_codex:
        print("\n[4/4] Codex execution is the 'spend/act' phase.")
        if input("  Proceed to run Codex now? [y/N] ").strip().lower() != "y":
            print("  Held. Run later: codex exec \"$(cat %s)\"" % goalfile)
            return
    print("[4/4] Codex implementing…")
    rc = run_codex(goal)
    print(f"  codex exit={rc}")

if __name__ == "__main__":
    main()
