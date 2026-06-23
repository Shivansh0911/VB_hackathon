"""
Google News RSS service — completely free, zero authentication.
Fetches real news headlines about civic issues in Indian cities.
No API key, no rate limit concerns, just RSS parsing.
"""
import httpx
import xml.etree.ElementTree as ET
from typing import List
from urllib.parse import quote_plus

# City-specific search queries — returns real Indian news about civic issues
CITY_QUERIES = {
    "Bengaluru": [
        "BBMP pothole Bengaluru",
        "BESCOM streetlight Bangalore",
        "BWSSB water leak Bengaluru",
        "garbage Bangalore civic BBMP",
        "Bengaluru road damage flooding",
    ],
    "Mumbai": [
        "BMC pothole Mumbai",
        "Mumbai waterlogging drainage",
        "garbage Mumbai civic BMC",
        "Mumbai road damage streetlight",
    ],
    "Hyderabad": [
        "GHMC pothole Hyderabad",
        "Hyderabad waterlogging drainage",
        "garbage Hyderabad GHMC civic",
        "Hyderabad road damage streetlight",
    ],
}

_BASE_URL = "https://news.google.com/rss/search"


def _parse_rss(xml_bytes: bytes) -> List[str]:
    try:
        root = ET.fromstring(xml_bytes)
        items = root.findall(".//item")
        texts = []
        for item in items[:6]:
            title = item.findtext("title", "").strip()
            # strip source suffix like " - Times of India"
            if " - " in title:
                title = title.rsplit(" - ", 1)[0].strip()
            if title and len(title) > 20:
                texts.append(title)
        return texts
    except Exception:
        return []


async def fetch_news_headlines(city: str) -> List[str]:
    queries = CITY_QUERIES.get(city, [])
    if not queries:
        return []

    results = []
    try:
        async with httpx.AsyncClient(
            timeout=8.0,
            headers={"User-Agent": "Mozilla/5.0 (compatible; CivicPulse/1.0)"},
            follow_redirects=True,
        ) as client:
            for q in queries[:3]:  # 3 queries per city max
                url = f"{_BASE_URL}?q={quote_plus(q)}&hl=en-IN&gl=IN&ceid=IN:en"
                try:
                    r = await client.get(url)
                    if r.status_code == 200:
                        results.extend(_parse_rss(r.content))
                except Exception as e:
                    print(f"[News RSS] Query '{q}' failed: {e}")
    except Exception as e:
        print(f"[News RSS] Client error: {e}")

    # deduplicate
    seen = set()
    unique = []
    for t in results:
        if t not in seen:
            seen.add(t)
            unique.append(t)

    print(f"[News RSS] {len(unique)} headlines from {city}")
    return unique
