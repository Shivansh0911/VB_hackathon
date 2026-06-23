"""
Google Maps Places API — fetches reviews for public infrastructure locations.
Used by the discovery agent as a secondary signal source.
Falls back to empty list if MAPS_API_KEY is not set.
"""
import os
import httpx
from typing import List

# Public infrastructure place IDs for demo cities (parks, stations, roads)
DEMO_PLACES = [
    "ChIJbU60yXAWrjsR4E9-UejD3_g",  # MG Road, Bengaluru
    "ChIJ0X31pIK6vodORyl4pEXA-H8",  # Koramangala, Bengaluru
]

async def fetch_place_reviews(place_id: str, api_key: str) -> List[str]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "reviews",
                    "key": api_key,
                },
            )
            if response.status_code == 200:
                data = response.json()
                reviews = data.get("result", {}).get("reviews", [])
                return [r["text"] for r in reviews if r.get("text")]
    except Exception as e:
        print(f"[Maps] Review fetch error: {e}")
    return []

async def fetch_infrastructure_reviews(city_name: str) -> List[str]:
    api_key = os.environ.get("MAPS_API_KEY", "")
    if not api_key:
        return []

    all_reviews = []
    for place_id in DEMO_PLACES:
        reviews = await fetch_place_reviews(place_id, api_key)
        all_reviews.extend(reviews)

    return all_reviews[:20]
