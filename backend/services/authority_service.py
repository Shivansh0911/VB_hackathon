"""
Government authority lookup table for Indian cities.
Used as a fast fallback before calling Gemini for authority identification.
"""

AUTHORITY_MAP = {
    "Bengaluru": {
        "POTHOLE":        {"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Roads & Infrastructure", "email": "commissioner@bbmp.gov.in"},
        "STREETLIGHT":    {"name": "BESCOM", "full": "Bangalore Electricity Supply Company", "dept": "Street Lighting Division", "email": "cmdoffice@bescom.org"},
        "WATER_LEAKAGE":  {"name": "BWSSB", "full": "Bangalore Water Supply & Sewerage Board", "dept": "Maintenance Division", "email": "chairman@bwssb.gov.in"},
        "GARBAGE":        {"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Solid Waste Management", "email": "swm@bbmp.gov.in"},
        "DRAINAGE":       {"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Storm Water Drain Division", "email": "swd@bbmp.gov.in"},
        "BROKEN_FOOTPATH":{"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Roads & Infrastructure", "email": "commissioner@bbmp.gov.in"},
        "TREE_FALLEN":    {"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Horticulture Department", "email": "horticulture@bbmp.gov.in"},
        "ROAD_DAMAGE":    {"name": "BBMP", "full": "Bruhat Bengaluru Mahanagara Palike", "dept": "Roads & Infrastructure", "email": "commissioner@bbmp.gov.in"},
    },
    "Mumbai": {
        "POTHOLE":        {"name": "BMC", "full": "Brihanmumbai Municipal Corporation", "dept": "Roads Department", "email": "roads@mcgm.gov.in"},
        "STREETLIGHT":    {"name": "MSEDCL", "full": "Maharashtra State Electricity Distribution Co.", "dept": "Street Lighting", "email": "consumer@mahadiscom.in"},
        "WATER_LEAKAGE":  {"name": "BMC", "full": "Brihanmumbai Municipal Corporation", "dept": "Hydraulic Engineering", "email": "he@mcgm.gov.in"},
        "GARBAGE":        {"name": "BMC", "full": "Brihanmumbai Municipal Corporation", "dept": "Solid Waste Management", "email": "swm@mcgm.gov.in"},
        "DRAINAGE":       {"name": "BMC", "full": "Brihanmumbai Municipal Corporation", "dept": "Storm Water Drain", "email": "swd@mcgm.gov.in"},
        "ROAD_DAMAGE":    {"name": "BMC", "full": "Brihanmumbai Municipal Corporation", "dept": "Roads Department", "email": "roads@mcgm.gov.in"},
    },
    "Hyderabad": {
        "POTHOLE":        {"name": "GHMC", "full": "Greater Hyderabad Municipal Corporation", "dept": "Engineering Department", "email": "commissioner@ghmc.gov.in"},
        "STREETLIGHT":    {"name": "TSSPDCL", "full": "TS Southern Power Distribution Co.", "dept": "Street Lighting", "email": "ccc@tssouthernpower.com"},
        "WATER_LEAKAGE":  {"name": "HMWSSB", "full": "Hyderabad Metropolitan Water Supply & Sewerage Board", "dept": "Operations", "email": "md@hmwssb.gov.in"},
        "GARBAGE":        {"name": "GHMC", "full": "Greater Hyderabad Municipal Corporation", "dept": "Sanitation Wing", "email": "sanitation@ghmc.gov.in"},
        "ROAD_DAMAGE":    {"name": "GHMC", "full": "Greater Hyderabad Municipal Corporation", "dept": "Engineering Department", "email": "commissioner@ghmc.gov.in"},
    },
}

DEFAULT_AUTHORITY = {
    "name": "Municipal Corporation",
    "full": "Municipal Corporation",
    "dept": "Public Works Department",
    "email": "grievance@municipality.gov.in",
}

def lookup_authority(city: str, category: str) -> dict:
    city_map = AUTHORITY_MAP.get(city, {})
    auth = city_map.get(category, DEFAULT_AUTHORITY)
    return {
        "authority_name": auth["full"],
        "authority_type": "municipal",
        "department": auth["dept"],
        "email": auth["email"],
        "reasoning": f"Responsible authority for {category} issues in {city}",
    }
