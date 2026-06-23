"""
Reddit API service — free tier, application-only OAuth2.
Scrapes r/bangalore, r/mumbai, r/hyderabad for civic complaints.
Falls back to empty list if REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET not set.

Setup (free, 2 minutes):
  1. Go to https://www.reddit.com/prefs/apps
  2. Create app → type: script → redirect: http://localhost
  3. Copy client_id (under app name) and client_secret
"""
import os
import httpx
from typing import List

CITY_SUBREDDITS = {
    "Bengaluru": ["bangalore", "bengaluru"],
    "Mumbai":    ["mumbai", "bombay"],
    "Hyderabad": ["hyderabad", "telangana"],
}

CIVIC_KEYWORDS = [
    "pothole", "streetlight", "garbage", "waterlog", "water log",
    "drainage", "sewage", "footpath", "road", "BBMP", "BMC", "GHMC",
    "BESCOM", "BWSSB", "broken", "waste", "flooding", "leak", "pipe",
]

_USER_AGENT = "CivicPulse:v1.0 (civic intelligence hackathon)"


async def _get_token(client_id: str, client_secret: str) -> str:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            "https://www.reddit.com/api/v1/access_token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            headers={"User-Agent": _USER_AGENT},
        )
        if r.status_code == 200:
            return r.json().get("access_token", "")
    return ""


async def fetch_reddit_posts(city: str) -> List[str]:
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        print(f"[Reddit] No credentials — skipping {city}")
        return []

    token = await _get_token(client_id, client_secret)
    if not token:
        print(f"[Reddit] Auth failed for {city}")
        return []

    subreddits = CITY_SUBREDDITS.get(city, [])
    results = []

    query = "pothole OR garbage OR waterlogging OR streetlight OR drainage OR BBMP OR BMC OR GHMC OR broken road"

    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": _USER_AGENT,
        }
        for sub in subreddits[:1]:  # one subreddit per city keeps rate limit safe
            try:
                r = await client.get(
                    f"https://oauth.reddit.com/r/{sub}/search",
                    headers=headers,
                    params={
                        "q": query,
                        "sort": "new",
                        "limit": 25,
                        "restrict_sr": True,
                        "type": "link",
                    },
                )
                if r.status_code != 200:
                    print(f"[Reddit] r/{sub} returned {r.status_code}")
                    continue

                posts = r.json().get("data", {}).get("children", [])
                for post in posts:
                    d = post["data"]
                    title = d.get("title", "")
                    body = d.get("selftext", "")[:300]

                    # only keep posts that mention civic keywords
                    combined = (title + " " + body).lower()
                    if any(kw.lower() in combined for kw in CIVIC_KEYWORDS):
                        text = title
                        if body and body not in ("[deleted]", "[removed]", ""):
                            text += ". " + body
                        results.append(text.strip())

            except Exception as e:
                print(f"[Reddit] Error for r/{sub}: {e}")

    print(f"[Reddit] {len(results)} posts from {city}")
    return results
