# CivicPulse — Autonomous Community Intelligence Agent

> AI discovers civic issues from public signals. Citizens confirm with one tap. Agents automatically escalate to the right government authority.

## The Problem This Solves

90% of civic issues — potholes, broken streetlights, water leaks — are never reported to authorities. Citizens complain on Twitter and WhatsApp but never fill government forms. Traditional reporting apps don't solve this; they just digitize a form nobody uses.

CivicPulse inverts the model: **the agent already knows before you report.**

## How It Works

```
Twitter/Maps signals
       │
       ▼
[Agent 1: Discovery] — Gemini Flash classifies → geospatial clustering → Probable Issues
       │
       ▼
[App: Citizen Confirmation] — Map shows discovered issues → one-tap confirm → Gemini validates photo
       │ (5+ confirmations)
       ▼
[Agent 3: Resolution] — Gemini identifies authority → drafts formal letter → sends email → tracks
```

## Setup

### Backend

```bash
cd civicpulse
cp .env.example .env
# Fill in GEMINI_API_KEY (required)

pip install -r requirements.txt
cd backend
uvicorn main:app --reload
```

Backend runs at http://localhost:8000

API docs at http://localhost:8000/docs

### Frontend

```bash
cd frontend
cp .env.example .env
# Fill in VITE_MAPS_API_KEY (required for map)
# Set VITE_API_URL=http://localhost:8000 for local dev

npm install
npm run dev
```

Frontend runs at http://localhost:5173

## Environment Variables

### Backend (`.env`)
| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google AI Studio API key |
| `TWITTER_BEARER_TOKEN` | No | Twitter/X v2 API. Falls back to demo data if absent |
| `SMTP_USER` / `SMTP_PASS` | No | Gmail app password for email dispatch. Simulates success if absent |

### Frontend (`frontend/.env`)
| Variable | Required | Description |
|---|---|---|
| `VITE_MAPS_API_KEY` | Yes | Google Maps JavaScript API key |
| `VITE_API_URL` | Yes | Backend URL |

## Demo Flow (for judges)

1. Open the app — issues are already on the map, discovered automatically
2. Click an issue → tap "Confirm" → upload a photo → Gemini validates it
3. After 5 confirmations, watch the status change to CONFIRMED
4. Hit "Run Escalation" in the header → agent identifies authority + drafts letter
5. Issue moves to ESCALATED with the letter visible

To demo faster: use the **"Run Discovery"** button to trigger Agent 1 manually, and **"Run Escalation"** to trigger Agent 3 on any confirmed issues.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + APScheduler |
| AI (text) | Gemini 1.5 Flash |
| AI (vision) | Gemini 1.5 Flash multimodal |
| AI (drafting) | Gemini 1.5 Pro |
| Frontend | React + Vite + Tailwind CSS |
| Maps | Google Maps JavaScript API |
| Database | SQLite (hackathon) |
| Deployment | Google AI Studio + Vercel |

## Deployment (Google AI Studio)

Follow: https://ai.google.dev/gemini-api/docs/aistudio-deploying

Set all environment variables in the AI Studio deployment config.
