import google.generativeai as genai
import os
import json
import time

_configured = False

def _ensure_configured():
    global _configured
    if not _configured:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        genai.configure(api_key=api_key)
        _configured = True

def _flash():
    _ensure_configured()
    return genai.GenerativeModel("models/gemini-2.5-flash")

def _pro():
    _ensure_configured()
    # gemini-2.5-pro requires billing — use flash (more than capable)
    return genai.GenerativeModel("models/gemini-2.5-flash")

def _generate(model, prompt_or_parts, retries: int = 2, backoff: int = 30):
    """Call generate_content with simple retry on 429 rate limit."""
    for attempt in range(retries + 1):
        try:
            return model.generate_content(prompt_or_parts)
        except Exception as e:
            msg = str(e)
            is_quota = "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower()
            if is_quota and attempt < retries:
                wait = backoff * (attempt + 1)
                print(f"[Gemini] Rate limit hit — waiting {wait}s before retry {attempt + 1}/{retries}")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini retries exhausted")

ISSUE_CATEGORIES = [
    "POTHOLE", "STREETLIGHT", "WATER_LEAKAGE", "GARBAGE",
    "BROKEN_FOOTPATH", "DRAINAGE", "TREE_FALLEN", "ROAD_DAMAGE", "OTHER",
]

def _parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())

def classify_and_extract_issues(texts: list, location_hint: str = "") -> list:
    batch_text = "\n---\n".join([f"[{i+1}] {t}" for i, t in enumerate(texts)])
    prompt = f"""You are a civic issue detection AI for Indian cities.

Analyze these social media posts and news headlines. Identify REAL civic infrastructure complaints.
Location context: {location_hint}

Posts:
{batch_text}

For each REAL civic complaint (ignore opinions, politics, general news without a specific complaint), extract:
- source_index: which post number (1-based)
- category: one of {ISSUE_CATEGORIES}
- title: short issue title (max 10 words)
- description: 1-2 sentence summary of the problem
- severity: LOW / MEDIUM / HIGH
- location_hint: any specific location mentioned (street, area, landmark)

Return ONLY a valid JSON array. If no civic issues found, return [].
Example:
[{{"source_index": 1, "category": "POTHOLE", "title": "Large pothole on MG Road", "description": "Deep pothole near metro station causing accidents.", "severity": "HIGH", "location_hint": "MG Road near metro"}}]
"""
    try:
        response = _generate(_flash(), prompt)
        return _parse_json(response.text)
    except Exception as e:
        print(f"[Gemini] classify error: {e}")
        return []

def validate_photo_for_issue(photo_base64: str, issue_category: str, issue_title: str) -> dict:
    prompt = f"""You are a civic issue photo validator.

The citizen claims this photo shows: "{issue_title}" (category: {issue_category})

Analyze the image and determine:
1. Does this photo show a real civic infrastructure problem?
2. Does it match the stated category ({issue_category})?
3. Is this clearly an outdoor/public space photo (not a stock image)?

Return ONLY valid JSON:
{{"valid": true/false, "confidence": 0-100, "reasoning": "one sentence", "detected_issue": "what you actually see"}}
"""
    try:
        image_part = {"mime_type": "image/jpeg", "data": photo_base64}
        response = _generate(_flash(), [prompt, image_part])
        return _parse_json(response.text)
    except Exception as e:
        print(f"[Gemini] vision error: {e}")
        return {"valid": True, "confidence": 50, "reasoning": "Photo validation unavailable", "detected_issue": "Unknown"}

def identify_authority(issue: dict) -> dict:
    prompt = f"""You are an expert on Indian municipal governance.

Issue details:
- Category: {issue.get('category')}
- Title: {issue.get('title')}
- Location: {issue.get('location_name', 'Unknown')}
- Description: {issue.get('description')}

Identify the most appropriate government authority to escalate this to.
Consider: municipal corporation, PWD, water board, electricity board, NHAI, etc.

Return ONLY valid JSON:
{{
  "authority_name": "Full official name",
  "authority_type": "municipal/state/central",
  "department": "specific department name",
  "email": "grievance@[authority].gov.in format",
  "reasoning": "why this authority is responsible"
}}
"""
    try:
        response = _generate(_flash(), prompt)
        return _parse_json(response.text)
    except Exception as e:
        print(f"[Gemini] authority error: {e}")
        return {
            "authority_name": "Municipal Corporation",
            "authority_type": "municipal",
            "department": "Public Works Department",
            "email": "grievance@municipality.gov.in",
            "reasoning": "Default escalation path",
        }

def draft_escalation_letter(issue: dict, authority: dict, confirmation_count: int) -> str:
    prompt = f"""Draft a formal civic grievance letter from CivicPulse (a citizen AI platform) to {authority['authority_name']}.

Issue details:
- Title: {issue['title']}
- Category: {issue['category']}
- Description: {issue['description']}
- Location: {issue.get('location_name', 'GPS: ' + str(issue['latitude']) + ', ' + str(issue['longitude']))}
- GPS Coordinates: {issue['latitude']}, {issue['longitude']}
- Citizens who confirmed this issue: {confirmation_count}
- First reported: {issue['created_at']}

Requirements:
- Professional, firm but respectful tone
- Reference the number of affected citizens
- Request specific action within 7 days
- Include GPS coordinates for field teams
- End with: "This letter was auto-generated by CivicPulse, a citizen-powered civic intelligence platform."
- Keep under 300 words

Return the letter text only, no JSON.
"""
    try:
        response = _generate(_pro(), prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini] letter error: {e}")
        # Hardcoded fallback so escalation never silently fails
        loc = issue.get('location_name', f"GPS: {issue['latitude']}, {issue['longitude']}")
        return (
            f"Dear {authority['authority_name']},\n\n"
            f"Subject: Urgent Civic Grievance — {issue['title']}\n\n"
            f"We are writing on behalf of CivicPulse to formally report: {issue['title']} "
            f"at {loc} (GPS: {issue['latitude']}, {issue['longitude']}).\n\n"
            f"This issue has been confirmed by {confirmation_count} independent citizens "
            f"and requires urgent attention.\n\n"
            f"We request your department to deploy a repair team within 7 days.\n\n"
            f"This letter was auto-generated by CivicPulse, a citizen-powered civic intelligence platform."
        )
