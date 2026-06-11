#!/usr/bin/env python3
"""
INCAGENT — Freelancer.com auto-intake worker
Finds matching projects, scores them, drafts a personalized bid,
then either sends it to Slack for approval (default) or submits it (AUTO_BID=1).

Setup:
  1. Create account at freelancer.com, then an app at developers.freelancer.com
  2. export FREELANCER_TOKEN=<oauth token>
  3. export SLACK_WEBHOOK=<your slack webhook>   (optional but recommended)
  4. pip install requests
Run:
  python scripts/freelancer_worker.py --dry-run   # search + score only
  python scripts/freelancer_worker.py             # search + draft -> Slack
  AUTO_BID=1 python scripts/freelancer_worker.py  # search + submit bids directly
"""
import os, sys, json, time, requests

API = "https://www.freelancer.com/api"
TOKEN = os.environ.get("FREELANCER_TOKEN", "")
SLACK = os.environ.get("SLACK_WEBHOOK", "")
AUTO_BID = os.environ.get("AUTO_BID") == "1"

# --- What INCAGENT can actually deliver (our two productized services) ---
SERVICES = {
    "lead_list": {
        "keywords": ["lead generation", "lead list", "prospect list", "b2b leads", "contact list"],
        "min_budget_usd": 30, "our_price_usd": 70, "days": 3,
        "pitch": (
            "Hi! I run an AI-powered business OS that produces verified B2B lead lists. "
            "You'll get {n} companies as CSV: company / website / contact form or phone / "
            "1-line personalization note per lead, sorted by likelihood to respond, "
            "plus 3 ready-to-send outreach templates (form / email / call script). "
            "Built from public sources only, compliant with anti-spam law. "
            "Delivery in 72h. First revision free."
        ),
    },
    "market_research": {
        "keywords": ["market research", "competitor analysis", "business analysis", "swot"],
        "min_budget_usd": 30, "our_price_usd": 60, "days": 2,
        "pitch": (
            "Hi! I deliver an AI-driven business diagnosis: your funnel mapped across 8 stages "
            "(awareness->trust->contact->negotiation->order->delivery->invoice->repeat), "
            "the exact stage where revenue is leaking, benchmarked against industry rates, "
            "plus 3 action proposals each with estimated cost, projected ROI and a kill condition "
            "- decision-ready documents, not vague advice. ~4,000 words, 48h delivery."
        ),
    },
}

def slack(text):
    if SLACK:
        requests.post(SLACK, json={"text": text}, timeout=10)

def search(keywords, limit=10):
    r = requests.get(
        f"{API}/projects/0.1/projects/active/",
        params={"query": " ".join(keywords[:2]), "limit": limit,
                "full_description": "true", "job_details": "true", "compact": "true"},
        headers={"freelancer-oauth-v1": TOKEN}, timeout=20)
    r.raise_for_status()
    return r.json().get("result", {}).get("projects", [])

def score(p, svc):
    """0-100: keyword match + budget fit + freshness"""
    text = (p.get("title", "") + " " + (p.get("description") or "")).lower()
    kw = sum(20 for k in svc["keywords"] if k in text)
    budget = (p.get("budget") or {})
    bmin = budget.get("minimum") or 0
    bfit = 30 if bmin >= svc["min_budget_usd"] else 10 if bmin > 0 else 0
    fresh = 20 if (time.time() - (p.get("time_submitted") or 0)) < 6 * 3600 else 5
    return min(100, kw + bfit + fresh)

def my_user_id():
    r = requests.get(f"{API}/users/0.1/self/", headers={"freelancer-oauth-v1": TOKEN}, timeout=20)
    r.raise_for_status()
    return r.json()["result"]["id"]

def place_bid(project, svc, uid):
    r = requests.post(f"{API}/projects/0.1/bids/", headers={"freelancer-oauth-v1": TOKEN}, json={
        "project_id": project["id"], "bidder_id": uid,
        "amount": svc["our_price_usd"], "period": svc["days"],
        "milestone_percentage": 100,
        "description": svc["pitch"].format(n=100),
    }, timeout=20)
    return r.status_code, r.text[:300]

def main():
    dry = "--dry-run" in sys.argv
    if not TOKEN and not dry:
        sys.exit("Set FREELANCER_TOKEN (developers.freelancer.com)")
    uid = None
    for name, svc in SERVICES.items():
        try:
            projects = search(svc["keywords"]) if TOKEN else []
        except Exception as e:
            print(f"[{name}] search failed: {e}"); continue
        ranked = sorted(((score(p, svc), p) for p in projects), key=lambda x: -x[0])
        for s, p in ranked[:3]:
            if s < 50:
                continue
            url = f"https://www.freelancer.com/projects/{p.get('seo_url','')}"
            line = f"[{name}] score={s} ${ (p.get('budget') or {}).get('minimum') } | {p['title'][:70]} | {url}"
            print(line)
            if dry:
                continue
            if AUTO_BID:
                uid = uid or my_user_id()
                code, body = place_bid(p, svc, uid)
                slack(f":dart: *INCAGENT bid submitted* ({code})\n{line}\nPrice: ${svc['our_price_usd']} / {svc['days']}d")
                print("bid:", code, body)
            else:
                slack(f":raising_hand: *INCAGENT found a job match* (score {s})\n*{p['title'][:80]}*\n{url}\n"
                      f"Proposed: ${svc['our_price_usd']} / {svc['days']} days\n"
                      f"Draft bid:\n>{svc['pitch'].format(n=100)[:400]}\n"
                      f"Reply APPROVE in thread or run with AUTO_BID=1 to submit.")
    print("done")

if __name__ == "__main__":
    main()
