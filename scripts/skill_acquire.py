#!/usr/bin/env python3
"""
INCAGENT — Capability Acquisition Loop
能力不足を検知 → カタログ検索 → 簡易セキュリティスキャン → 取り込み(local cache) → audit
使い方: python scripts/skill_acquire.py "請求書 PDF を作る"
"""
import json, sys, os, re, urllib.request, hashlib

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG=os.path.join(ROOT,"packages/skills/registry/catalog.json")
CACHE=os.path.join(ROOT,"packages/skills/cache")
os.makedirs(CACHE,exist_ok=True)

# 簡易スキャン: SkillSpector思想の軽量版（取り込み前ゲート）
DANGER=[r"curl\s+[^|]+\|\s*(ba)?sh", r"rm\s+-rf\s+/", r"eval\(", r"base64\s+-d.*\|.*sh",
        r"\.ssh/", r"AWS_SECRET", r"exfiltrat", r"reverse shell", r"/etc/passwd"]
def scan(text):
    hits=[p for p in DANGER if re.search(p,text,re.I)]
    score=100-len(hits)*25
    return max(0,score), hits

def need_to_keywords(need):
    return [w for w in re.split(r"[\s　]+", need.lower()) if w]

def search(need):
    cat=json.load(open(CATALOG))
    kw=need_to_keywords(need)
    # 日本語→英語の薄いマップ（実運用ではLLMが担う）
    hint={"請求":"pdf docx","pdf":"pdf","スライド":"pptx","プレゼン":"pptx","表":"xlsx",
          "スプレッド":"xlsx","文書":"docx","ワード":"docx","デザイン":"frontend-design canvas",
          "ブランド":"brand","api":"claude-api","mcp":"mcp","テスト":"webapp-testing","アート":"art"}
    expanded=" ".join(kw)+" "+" ".join(hint.get(k,"") for k in kw)
    scored=[]
    for s in cat:
        hay=(s["name"]+" "+s["description"]).lower()
        sc=sum(1 for t in expanded.split() if t and t in hay)
        if sc: scored.append((sc,s))
    return [s for _,s in sorted(scored,key=lambda x:-x[0])]

def acquire(need, auto_threshold=75):
    print(f"[need] {need}")
    cands=search(need)
    if not cands:
        print("  no matching skill in catalog -> escalate to human"); return
    top=cands[0]
    url=f"https://raw.githubusercontent.com/anthropics/skills/main/{top['path']}"
    try:
        txt=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"incagent"})).read().decode("utf-8","ignore")
    except Exception as e:
        print(f"  fetch failed: {e}"); return
    score,hits=scan(txt)
    print(f"  match: {top['name']} (source: {top['source']})")
    print(f"  security scan: {score}/100  {'OK' if not hits else 'FLAGS:'+str(hits)}")
    if score>=auto_threshold:
        dest=os.path.join(CACHE,top["name"]+".SKILL.md")
        open(dest,"w").write(txt)
        sha=hashlib.sha256(txt.encode()).hexdigest()[:16]
        print(f"  -> AUTO-ACQUIRED to cache (sha {sha})")
        print(f"  -> audit_log: skill_acquired name={top['name']} score={score}")
    else:
        print(f"  -> QUARANTINED, human approval required (scan {score} < {auto_threshold})")

if __name__=="__main__":
    acquire(sys.argv[1] if len(sys.argv)>1 else "請求書 PDF を作る")
