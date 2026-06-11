#!/usr/bin/env python3
"""
INCAGENT — X (Twitter) thread poster for @incagentai
Usage:
  pip install requests-oauthlib
  export X_API_KEY=... X_API_SECRET=... X_ACCESS_TOKEN=... X_ACCESS_SECRET=...
  python scripts/post_to_x.py            # posts the launch thread
  python scripts/post_to_x.py --dry-run  # prints without posting
Keys: developer.x.com app attached to @incagentai, permission "Read and Write".
"""
import os, sys, json, time

POSTS = [
    # --- EN launch thread (@incagentai) ---
    (
        "We're building an OS where AI runs the company and the human only "
        "stamps approvals.\n\n"
        "Tell it what you want once. It researches, runs ads, makes sales "
        "calls, sends invoices \u2014 24/7.\n\n"
        "Needs money? It files a RINGI: budget, projected ROI, kill "
        "condition. You tap approve."
    ),
    (
        "It's live, not a deck:\n"
        "\u2713 Hourly autonomous loop with real approval logs\n"
        "\u2713 It caught a missed KPI and filed its own spend request "
        "(\u00a520k ad POC, 382% ROI, auto-stop at CPA \u00a56k)\n"
        "\u2713 Approve \u2192 execute \u2192 Slack, fully logged\n"
        "\u2713 Every forecast audited vs actuals"
    ),
    (
        "The AI doesn't get a wallet. It gets a budget ceiling.\n\n"
        "Approved amount = hard API spend limit. \u00a50 moves without a human "
        "stamp.\n\n"
        "Building in public from Tokyo. Decisions, numbers, failures \u2014 all of "
        "it. Follow along. \U0001f3ef\n\n#buildinpublic #AIagents"
    ),
    # --- JA single post (appended to thread) ---
    (
        "\u65e5\u672c\u8a9e\u7248\uff1a\u793e\u9577\u306e\u4ed5\u4e8b\u304c\u300c\u627f\u8a8d\u3060\u3051\u300d\u306b\u306a\u308bOS\u3092\u4f5c\u3063\u3066\u3044\u307e\u3059\u3002"
        "AI\u304c\u5e02\u5834\u8abf\u67fb\u30fb\u5e83\u544a\u30fb\u55b6\u696d\u96fb\u8a71\u30fb\u8acb\u6c42\u307e\u3067\u81ea\u8d70\u3057\u3001"
        "\u91d1\u304c\u8981\u308b\u3068\u304d\u3060\u3051\u300c\u7a1f\u8b70\u300d\uff08\u60f3\u5b9aROI\u30fb\u64a4\u9000\u6761\u4ef6\u4ed8\u304d\uff09\u304c\u5c4a\u304f\u3002"
        "\u672c\u756a\u7a3c\u50cd\u4e2d\u3002\u9032\u6357\u306f\u5168\u90e8\u6652\u3057\u307e\u3059\u3002"
    ),
]

def main():
    dry = "--dry-run" in sys.argv
    if dry:
        for i, p in enumerate(POSTS, 1):
            print(f"--- post {i} ({len(p)} chars) ---\n{p}\n")
        return

    from requests_oauthlib import OAuth1Session
    keys = [os.environ.get(k) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    if not all(keys):
        sys.exit("Missing env vars: X_API_KEY X_API_SECRET X_ACCESS_TOKEN X_ACCESS_SECRET")
    x = OAuth1Session(keys[0], keys[1], keys[2], keys[3])

    prev_id = None
    for i, text in enumerate(POSTS, 1):
        payload = {"text": text}
        if prev_id:
            payload["reply"] = {"in_reply_to_tweet_id": prev_id}
        r = x.post("https://api.x.com/2/tweets", json=payload)
        if r.status_code != 201:
            sys.exit(f"post {i} failed: {r.status_code} {r.text}")
        prev_id = r.json()["data"]["id"]
        print(f"posted {i}/{len(POSTS)}: https://x.com/incagentai/status/{prev_id}")
        time.sleep(2)

if __name__ == "__main__":
    main()
