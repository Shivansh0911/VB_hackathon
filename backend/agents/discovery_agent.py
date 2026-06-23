"""
Agent 1 — Discovery Agent
Runs on schedule every 6 hours.
Pipeline: fetch signals (Twitter + Reddit + Google News) → Gemini classifies
          → geospatial cluster → deduplicate → store new issues.
"""
import random
import asyncio
from typing import List, Dict

from services.twitter_service import fetch_tweets
from services.reddit_service import fetch_reddit_posts
from services.news_rss_service import fetch_news_headlines
from services.maps_reviews_service import fetch_infrastructure_reviews
from services.gemini_service import classify_and_extract_issues
from services.clustering_service import cluster_issues
from database import create_issue, get_all_issues

MONITOR_CITIES = [
    {
        "name": "Bengaluru",
        "lat": 12.9716, "lon": 77.5946,
        "twitter_query": "(pothole OR streetlight OR garbage OR waterlogging OR BBMP OR BWSSB OR BESCOM) lang:en -is:retweet",
        "reddit_subreddit": "bangalore",
    },
    {
        "name": "Mumbai",
        "lat": 19.0760, "lon": 72.8777,
        "twitter_query": "(pothole OR BMC OR waterlogging OR garbage OR streetlight OR drainage) lang:en -is:retweet",
        "reddit_subreddit": "mumbai",
    },
    {
        "name": "Hyderabad",
        "lat": 17.3850, "lon": 78.4867,
        "twitter_query": "(pothole OR GHMC OR drainage OR streetlight OR garbage OR waterlogging) lang:en -is:retweet",
        "reddit_subreddit": "hyderabad",
    },
]


def _assign_coordinates(issue: dict, city: dict) -> dict:
    issue["latitude"] = city["lat"] + random.uniform(-0.06, 0.06)
    issue["longitude"] = city["lon"] + random.uniform(-0.06, 0.06)
    issue["location_name"] = issue.get("location_hint", city["name"]) + f", {city['name']}"
    return issue


async def run_discovery(city: dict) -> int:
    print(f"[Discovery] Scanning {city['name']} — Twitter + Reddit + News RSS...")

    # Fetch from all three signal sources in parallel
    twitter_texts, reddit_texts, news_texts, maps_texts = await asyncio.gather(
        fetch_tweets(city["twitter_query"], city=city["name"]),
        fetch_reddit_posts(city["name"]),
        fetch_news_headlines(city["name"]),
        fetch_infrastructure_reviews(city["name"]),
        return_exceptions=True,
    )

    # Flatten, ignore any source that errored
    all_texts: List[str] = []
    for source in [twitter_texts, reddit_texts, news_texts, maps_texts]:
        if isinstance(source, list):
            all_texts.extend(source)

    # Deduplicate texts before sending to Gemini
    seen = set()
    unique_texts = []
    for t in all_texts:
        key = t.strip().lower()[:80]
        if key not in seen:
            seen.add(key)
            unique_texts.append(t.strip())

    print(f"[Discovery] {city['name']}: {len(unique_texts)} unique signals "
          f"(twitter={len(twitter_texts) if isinstance(twitter_texts, list) else 0}, "
          f"reddit={len(reddit_texts) if isinstance(reddit_texts, list) else 0}, "
          f"news={len(news_texts) if isinstance(news_texts, list) else 0})")

    if not unique_texts:
        print(f"[Discovery] No signals for {city['name']}")
        return 0

    # Classify with Gemini Flash (batch all signals in one call)
    raw_issues = classify_and_extract_issues(unique_texts, location_hint=city["name"])
    if not raw_issues:
        print(f"[Discovery] No civic issues extracted for {city['name']}")
        return 0

    # Attach source text and city coordinates
    for issue in raw_issues:
        idx = issue.get("source_index", 1) - 1
        issue["source_text"] = unique_texts[idx] if 0 <= idx < len(unique_texts) else ""
        _assign_coordinates(issue, city)

    # Geospatial clustering — merge nearby same-category signals
    clustered = cluster_issues(raw_issues)

    # Deduplicate against existing DB issues
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

    print(f"[Discovery] +{new_count} new issues stored for {city['name']}")
    return new_count


async def run_all_cities() -> dict:
    results = {}
    for i, city in enumerate(MONITOR_CITIES):
        if i > 0:
            await asyncio.sleep(15)  # stay within Gemini 5 RPM free tier
        results[city["name"]] = await run_discovery(city)
    return results
