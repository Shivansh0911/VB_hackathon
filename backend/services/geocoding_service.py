"""
Neighbourhood-level coordinate lookup for Indian cities.
Matches location_hint text from Gemini against known areas → precise coords.
Falls back to city centre + small random offset only when no match found.
"""
import random
from typing import Tuple

# Known neighbourhoods with lat/lon for each city
NEIGHBOURHOODS = {
    "Bengaluru": [
        ("Indiranagar",        12.9784, 77.6408),
        ("Koramangala",        12.9352, 77.6245),
        ("BTM Layout",         12.9166, 77.6101),
        ("HSR Layout",         12.9116, 77.6389),
        ("Whitefield",         12.9698, 77.7499),
        ("Electronic City",    12.8399, 77.6770),
        ("Marathahalli",       12.9591, 77.6971),
        ("Jayanagar",          12.9250, 77.5938),
        ("JP Nagar",           12.9102, 77.5940),
        ("Bannerghatta",       12.8636, 77.5983),
        ("Bellandur",          12.9258, 77.6780),
        ("Sarjapur",           12.8584, 77.6831),
        ("Hebbal",             13.0353, 77.5972),
        ("Yelahanka",          13.1005, 77.5963),
        ("Rajajinagar",        12.9908, 77.5527),
        ("Malleshwaram",       13.0035, 77.5698),
        ("MG Road",            12.9756, 77.6097),
        ("Brigade Road",       12.9719, 77.6085),
        ("Cunningham Road",    12.9884, 77.5947),
        ("Silk Board",         12.9177, 77.6228),
        ("KR Puram",           13.0050, 77.6960),
        ("Banashankari",       12.9255, 77.5468),
        ("Vijayanagar",        12.9719, 77.5350),
        ("Peenya",             13.0290, 77.5220),
        ("80ft Road",          12.9352, 77.6245),
        ("100ft Road",         12.9784, 77.6408),
    ],
    "Mumbai": [
        ("Bandra",             19.0596, 72.8397),
        ("Andheri",            19.1136, 72.8697),
        ("Malad",              19.1874, 72.8484),
        ("Borivali",           19.2307, 72.8567),
        ("Kurla",              19.0726, 72.8794),
        ("Dadar",              19.0178, 72.8478),
        ("Worli",              19.0176, 72.8160),
        ("Powai",              19.1177, 72.9060),
        ("Thane",              19.2183, 72.9781),
        ("Navi Mumbai",        19.0330, 73.0297),
        ("Goregaon",           19.1663, 72.8526),
        ("Jogeshwari",         19.1388, 72.8491),
        ("Ghatkopar",          19.0863, 72.9081),
        ("Mulund",             19.1726, 72.9569),
        ("Chembur",            19.0626, 72.9006),
        ("SV Road",            19.1136, 72.8497),
        ("Link Road",          19.1500, 72.8500),
        ("Lokhandwala",        19.1365, 72.8264),
    ],
    "Hyderabad": [
        ("Gachibowli",         17.4401, 78.3489),
        ("Hitech City",        17.4478, 78.3762),
        ("Madhapur",           17.4432, 78.3927),
        ("Kondapur",           17.4598, 78.3612),
        ("Kukatpally",         17.4849, 78.3998),
        ("Secunderabad",       17.4399, 78.4983),
        ("Begumpet",           17.4417, 78.4688),
        ("Jubilee Hills",      17.4248, 78.4032),
        ("Banjara Hills",      17.4155, 78.4343),
        ("Ameerpet",           17.4374, 78.4481),
        ("SR Nagar",           17.4506, 78.4428),
        ("LB Nagar",           17.3469, 78.5524),
        ("Dilsukhnagar",       17.3687, 78.5245),
        ("Uppal",              17.4054, 78.5594),
        ("Miyapur",            17.4956, 78.3575),
        ("Kompally",           17.5416, 78.4718),
        ("Manikonda",          17.4070, 78.3892),
    ],
}


def _best_match(location_hint: str, city: str) -> Tuple[float, float]:
    """Return (lat, lon) for the best matching neighbourhood, or city centre offset."""
    hint_lower = location_hint.lower()
    areas = NEIGHBOURHOODS.get(city, [])

    for name, lat, lon in areas:
        if name.lower() in hint_lower:
            # Small jitter so duplicate-area issues don't stack exactly
            return (
                lat + random.uniform(-0.005, 0.005),
                lon + random.uniform(-0.005, 0.005),
            )

    # No match — return city centre with moderate offset
    city_centres = {
        "Bengaluru": (12.9716, 77.5946),
        "Mumbai":    (19.0760, 72.8777),
        "Hyderabad": (17.3850, 78.4867),
    }
    clat, clon = city_centres.get(city, (12.9716, 77.5946))
    return (
        clat + random.uniform(-0.03, 0.03),
        clon + random.uniform(-0.03, 0.03),
    )


def resolve_coordinates(location_hint: str, city: str) -> Tuple[float, float]:
    return _best_match(location_hint, city)
