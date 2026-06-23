"""
Agent 1 — Discovery Agent
Runs on schedule every 6 hours.
Pipeline: fetch signals → Gemini classifies → geospatial cluster → store new issues.
"""
import random
import asyncio
from typing import List, Dict

from services.twitter_service import fetch_tweets
from services.maps_reviews_service import fetch_infrastructure_reviews
from services.gemini_service import classify_and_extract_issues
from services.clustering_service import cluster_issues
from database import create_issue, get_all_issues

MONITOR_CITIES = [
    {
        "name": "Bengaluru",
        "lat": 12.9716, "lon": 77.5946,
        "twitter_query": "pothole OR streetlight OR garbage OR waterlogging OR #BBMP lang:en -is:retweet",
    },
    {
        "name": "Mumbai",
        "lat": 19.0760, "lon": 72.8777,
        "twitter_query": "pothole OR BMC OR waterlogging OR garbage OR streetlight lang:en -is:retweet",
    },
    {
        "name": "Hyderabad",
        "lat": 17.3850, "lon": 78.4867,
        "twitter_query": "pothole OR GHMC OR drainage OR streetlight OR garbage lang:en -is:retweet",
    },
]

def _assign_coordinates(issue: dict, city: dict) -> dict:
    issue["latitude"] = city["lat"] + random.uniform(-0.06, 0.06)
    issue["longitude"] = city["lon"] + random.uniform(-0.06, 0.06)
    issue["location_name"] = issue.get("location_hint", city["name"]) + f", {city['name']}"
    return issue

async def run_discovery(city: dict) -> int:
    print(f"[Discovery] Scanning {city['name']}...")

    # Fetch from multiple signal sources
    twitter_texts = await fetch_tweets(city["twitter_query"])
    maps_texts = await fetch_infrastructure_reviews(city["name"])
    all_texts = twitter_texts + maps_texts

    if not all_texts:
        print(f"[Discovery] No signals for {city['name']}")
        return 0

    # Classify with Gemini Flash
    raw_issues = classify_and_extract_issues(all_texts, location_hint=city["name"])
    if not raw_issues:
        print(f"[Discovery] No civic issues extracted from signals")
        return 0

    # Attach source text and coordinates
    for issue in raw_issues:
        idx = issue.get("source_index", 1) - 1
        issue["source_text"] = all_texts[idx] if idx < len(all_texts) else ""
        _assign_coordinates(issue, city)

    # Geospatial clustering — merge nearby same-category signals
    clustered = cluster_issues(raw_issues)

    # Deduplication against DB
    existing = get_all_issues()
    existing_keys = {
        (i["category"], round(i["latitude"], 3), round(i["longitude"], 3))
        for i in existing
    }

    new_count = 0
    for issue in clustered:
        key = (issue["category"], round(issue["latitude"], 3), round(issue["longitude"], 3))
        if key not in existing_keys:
            create_issue(issue)
            new_count += 1

    print(f"[Discovery] +{new_count} new issues in {city['name']}")
    return new_count

async def run_all_cities() -> dict:
    results = {}
    for i, city in enumerate(MONITOR_CITIES):
        if i > 0:
            await asyncio.sleep(15)  # stay within 5 RPM free tier
        results[city["name"]] = await run_discovery(city)
    return results
