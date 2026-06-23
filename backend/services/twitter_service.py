"""
Twitter/X API v2 service — free Bearer Token tier.
Falls back to city-specific mock data if TWITTER_BEARER_TOKEN not set.

Get free Bearer Token (2 min):
  1. developer.twitter.com → sign up
  2. Create a project + app (free)
  3. Keys & Tokens → Bearer Token → copy it
"""
import os
import httpx
from typing import List

# Realistic mock tweets keyed by city — used when Bearer Token not set
MOCK_TWEETS = {
    "Bengaluru": [
        "The pothole on Indiranagar 100ft road is back again!! Almost fell off my bike. @BBMP please fix #Bengaluru",
        "Streetlight near Koramangala 5th block not working since 3 days. Very dark and unsafe at night #BBMP",
        "Water leaking from underground pipe on HSR layout sector 2 main road. Huge wastage happening daily",
        "Same pothole on Indiranagar 100ft road got me again! When will @BBMP fix this? Third complaint this week",
        "Garbage not collected in BTM layout for 4 days. Stinking badly. Where is BBMP? #SwachhBharat",
        "The footpath on MG Road is completely broken near the bus stop. Senior citizens struggling to walk.",
        "Another day, another pothole on Indiranagar road. 3 complaints this week, nothing happens. @BBMP",
        "Sewage overflow near Electronic City Phase 1 flyover. Unbearable smell. Residents suffering. @BBMP",
        "Large tree fallen on road near Hebbal junction blocking one lane. @BBMP please send team ASAP",
        "Water board pipe burst on 80ft road Koramangala. Road flooded and traffic jam for hours today",
    ],
    "Mumbai": [
        "@BMC Mumbai waterlogging on Andheri Link road again. 3rd time this month. Nothing is being fixed.",
        "Streetlights not working on SV Road Bandra for past 2 weeks. Very dangerous after dark.",
        "Potholes on station road Bandra west are getting worse after rain. @BMC please fix ASAP",
        "Garbage not collected in Malad west for 3 days. Overflowing bins everywhere. @BMC_Mumbai",
        "Drainage blocked near Kurla station — waterlogging during every rain. Same issue every year! @BMC",
        "Road repair work incomplete in Andheri east — half the road dug up for weeks, no update @BMC",
    ],
    "Hyderabad": [
        "GHMC fix the broken road near Gachibowli circle please! Pothole took out my tyre this morning",
        "Streetlights not working on Madhapur main road for 10 days. Complaints ignored. @GHMC_HYD",
        "Waterlogging near Hitech City every single rain. Drains never cleared. @GHMC_HYD do something",
        "Garbage pile near Kondapur junction not cleared for 5 days. Health hazard. @GHMC_HYD",
        "Road damage near Kukatpally housing board is terrible. Craters forming after rain. @GHMC_HYD",
    ],
}

_DEFAULT_MOCK = [tweet for tweets in MOCK_TWEETS.values() for tweet in tweets]


async def fetch_tweets(query: str, city: str = "", max_results: int = 20) -> List[str]:
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")

    if not bearer_token:
        print(f"[Twitter] No token — using mock data for {city or 'all cities'}")
        return MOCK_TWEETS.get(city, _DEFAULT_MOCK)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers={"Authorization": f"Bearer {bearer_token}"},
                params={
                    "query": query,
                    "max_results": max(10, min(max_results, 100)),
                    "tweet.fields": "created_at,author_id",
                },
            )
            if response.status_code == 200:
                data = response.json()
                tweets = [t["text"] for t in data.get("data", [])]
                print(f"[Twitter] {len(tweets)} live tweets for {city}")
                return tweets
            else:
                print(f"[Twitter] API {response.status_code}: {response.text[:150]}")
    except Exception as e:
        print(f"[Twitter] Request failed: {e}")

    return MOCK_TWEETS.get(city, _DEFAULT_MOCK)
