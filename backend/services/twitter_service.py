"""
Twitter/X API v2 service.
Falls back to realistic mock data if TWITTER_BEARER_TOKEN is not set.
"""
import os
import httpx
from typing import List

MOCK_TWEETS = [
    "The pothole on Indiranagar 100ft road is back again!! Almost fell off my bike. @BBMP please fix #Bengaluru",
    "Streetlight near Koramangala 5th block not working since 3 days. Very dark and unsafe at night #BBMP",
    "Water leaking from underground pipe on HSR layout sector 2 main road. Huge wastage happening daily",
    "Same pothole on Indiranagar 100ft road got me again! When will @BBMP fix this? Third complaint",
    "Garbage not collected in BTM layout for 4 days. Stinking badly. Where is BBMP? #SwachhBharat",
    "The footpath on MG Road is completely broken near the bus stop. Senior citizens can't walk.",
    "Another day, another pothole on Indiranagar road. Count: 3 complaints this week. Nothing happens.",
    "Broken streetlight on Whitefield main road since a week. Very dangerous at night. @BBMP please act",
    "Sewage overflow near Electronic City Phase 1 flyover. Unbearable smell. Residents suffering. @BBMP",
    "Large tree fallen on road near Hebbal junction blocking one lane. @BBMP please send team ASAP",
    "Road damage on Sarjapur outer ring road — huge potholes forming craters after last week's rain",
    "Water board pipe burst on 80ft road Koramangala. Road flooded and traffic jammed for hours today",
    "@BMC Mumbai waterlogging on Andheri Link road again. 3rd time this month. Nothing is being fixed.",
    "Streetlights not working on SV Road Bandra for past 2 weeks. Very dangerous after dark. @MumbaiPolice",
    "GHMC fix the broken road near Gachibowli circle please! Pothole took out my tyre this morning",
]

async def fetch_tweets(query: str, max_results: int = 20) -> List[str]:
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")

    if not bearer_token:
        print("[Twitter] No token — using mock data")
        return MOCK_TWEETS

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {bearer_token}"},
                params={
                    "query": query,
                    "max_results": min(max_results, 100),
                    "tweet.fields": "geo,created_at,author_id",
                    "-is": "retweet",
                },
            )
            if response.status_code == 200:
                data = response.json()
                return [t["text"] for t in data.get("data", [])]
            else:
                print(f"[Twitter] API error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"[Twitter] Request failed: {e}")

    return MOCK_TWEETS
