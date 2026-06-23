from typing import List, Dict
import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))

def cluster_issues(raw_issues: List[Dict], radius_km: float = 0.3) -> List[Dict]:
    if not raw_issues:
        return []

    clusters = []
    used = set()

    for i, issue in enumerate(raw_issues):
        if i in used:
            continue

        cluster_members = [issue]
        used.add(i)

        for j, other in enumerate(raw_issues):
            if j in used or j == i:
                continue
            if other["category"] != issue["category"]:
                continue
            dist = haversine_distance_km(
                issue["latitude"], issue["longitude"],
                other["latitude"], other["longitude"],
            )
            if dist <= radius_km:
                cluster_members.append(other)
                used.add(j)

        merged = cluster_members[0].copy()
        merged["source_signals"] = [m.get("source_text", "") for m in cluster_members]
        merged["confidence_score"] = min(10 + (len(cluster_members) - 1) * 20, 80)
        merged["cluster_size"] = len(cluster_members)

        clusters.append(merged)

    return sorted(clusters, key=lambda x: x["confidence_score"], reverse=True)
