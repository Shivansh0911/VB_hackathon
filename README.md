# CivicPulse — Autonomous Civic Intelligence Platform

> **AI discovers civic problems before citizens report them.**
> Citizens confirm. Agents escalate to the right authority automatically.

**Live Demo:** https://civicradar.netlify.app
**Backend API:** https://vb-hackathon.onrender.com
**API Docs:** https://vb-hackathon.onrender.com/docs

Built for **Vibe2Ship Hackathon — Problem 2: Community Hero (Hyperlocal Problem Solver)**

---

## The Idea

Every civic app today is a complaint box. Citizen opens app → fills form → submits. Nobody does it.

CivicPulse flips the model: **the AI already knows before you report.**

An autonomous Discovery Agent scans Twitter, Reddit, and Google News RSS continuously. It finds civic issues, clusters them geospatially, and puts them on the map. Citizens just confirm what the AI found. Once 5 citizens confirm, the Resolution Agent identifies the correct government authority and sends a formal escalation letter — fully automated, end to end.

---

## 3-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 1 — DISCOVERY          Runs every 6 hours via scheduler  │
│                                                                  │
│  Twitter + Reddit + Google News RSS                              │
│       ↓                                                          │
│  Gemini 2.5 Flash classifies civic signals                       │
│       ↓                                                          │
│  Haversine geospatial clustering (0.3km radius)                  │
│       ↓                                                          │
│  Neighbourhood geocoding (60+ named areas)                       │
│       ↓                                                          │
│  New issues stored → appear on map as DISCOVERED                 │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 2 — CONFIRMATION       Triggered per citizen action       │
│                                                                  │
│  Citizen clicks issue → uploads photo (optional)                 │
│       ↓                                                          │
│  Gemini Vision validates photo matches issue category            │
│       ↓                                                          │
│  Confidence score rises (+15 per confirmation)                   │
│       ↓                                                          │
│  At 5 confirmations → status moves to CONFIRMED                  │
└─────────────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 3 — RESOLUTION         Triggered on CONFIRMED status      │
│                                                                  │
│  Authority lookup table → BBMP / BMC / GHMC / BESCOM / BWSSB    │
│       ↓                                                          │
│  Gemini Pro drafts formal escalation letter                      │
│       ↓                                                          │
│  Letter + authority stored, shown in UI, logged for dispatch     │
│       ↓                                                          │
│  Issue moves to ESCALATED                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Issue stages:** `DISCOVERED → CONFIRMED → ESCALATED → RESOLVED`

---

## What Is Actually Running (Not Demo)

| Component | Status | Details |
|-----------|--------|---------|
| Google News RSS | **Live** | Queries real Indian civic headlines — BBMP potholes, GHMC drainage, BMC waterlogging. No API key. |
| Gemini 2.5 Flash — Classification | **Live** | Batch classifies all signals into structured civic issues with category, severity, location hint |
| Gemini 2.5 Flash — Photo Validation | **Live** | Multimodal: validates citizen photos match the reported issue |
| Gemini 2.5 Flash — Letter Drafting | **Live** | Generates formal 250-word escalation letter addressed to specific authority |
| Haversine Clustering | **Live** | Pure Python geospatial clustering — merges nearby same-category signals |
| Neighbourhood Geocoding | **Live** | 60+ named areas (Indiranagar, Koramangala, Bandra, Gachibowli etc.) mapped to real coordinates |
| Authority Lookup Table | **Live** | BBMP Roads, BBMP SWM, BESCOM, BWSSB, BMC, GHMC, TSSPDCL, HMWSSB — department-level emails |
| APScheduler | **Live** | Discovery runs every 6h, escalation batch every 30min — no manual trigger needed |
| Auto boot discovery | **Live** | On startup if DB empty, Bengaluru scan fires automatically |
| Fallback seed data | **Live** | Only if Gemini quota exhausted — example issues load as last resort |
| CORS protection | **Live** | Restricted to Netlify frontend URL only |
| SQL injection safe | **Live** | All queries use parameterised `?` placeholders |
| Photo size limit | **Live** | 5MB max, base64 encoded |

---

## Known Limitations & Why

### Twitter / X — Search API Is Paid
Twitter's recent search API requires a paid plan ($100/month Basic) as of 2023. The free developer tier only allows posting, not searching. CivicPulse has the full Twitter integration with Bearer Token — it hits 402 CreditsDepleted because the account has no paid credits.

**What runs instead:** City-specific mock tweets mirroring real complaint patterns (BBMP/BMC/GHMC tags, real Bengaluru/Mumbai/Hyderabad locations). The full Discovery pipeline — Gemini classification, clustering, geocoding — runs on these plus real Google News RSS.

### Email Dispatch — Intentionally Not Sent
SMTP email service is fully coded (`email_service.py`). Not configured for this deployment intentionally:
- Sending AI-generated letters to real government officials based on hackathon demo data would be inappropriate
- The letter, authority identification, department routing, and escalation flow are all visible in the UI
- In production: add Gmail SMTP credentials → letters reach real inboxes

### Reddit — Optional Signal Source
Full OAuth2 integration built in `reddit_service.py`. Not configured because Google News RSS provides sufficient signal for the demo. Adding `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` (free) activates r/bangalore, r/mumbai, r/hyderabad.

### Google Maps Reviews — Paid API
Places API charges beyond the $200/month free credit. Disabled to keep the project 100% free-tier safe. Map tiles use Leaflet.js + CartoDB Dark Matter — no Google Maps API required.

### DB Resets on Render Restart
Render free tier has no persistent disk. SQLite resets on cold start. Mitigated by auto-boot discovery on startup — real data re-populates within ~20 seconds. UptimeRobot keeps the server warm so cold starts are rare.

---

## Tech Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Web framework | FastAPI | 0.111.0 |
| ASGI server | Uvicorn | 0.30.0 |
| AI / LLM | Google Gemini 2.5 Flash | via google-generativeai 0.7.2 |
| Task scheduler | APScheduler (AsyncIOScheduler) | 3.10.4 |
| Database | SQLite | built-in (Python 3.11) |
| HTTP client | httpx (async) | 0.27.0 |
| Data validation | Pydantic v2 | ≥2.7.4 |
| Auth loading | python-dotenv | 1.0.1 |
| File upload | python-multipart | 0.0.9 |
| Python version | Python | 3.11.9 |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18 |
| Build tool | Vite | 5 |
| Styling | Tailwind CSS | 3 |
| Map | Leaflet.js | 1.9.4 |
| Map tiles | CartoDB Dark Matter | Free, no key |
| HTTP | Fetch API (native) | — |
| State | React hooks (useState, useEffect, useCallback) | — |

### Infrastructure
| Component | Service | Cost |
|-----------|---------|------|
| Backend hosting | Render (Free tier) | $0 |
| Frontend hosting | Netlify (Free tier) | $0 |
| AI (Gemini) | Google AI Studio (Free tier, 5 RPM / 20 RPD) | $0 |
| Uptime monitoring | UptimeRobot (Free tier, 5-min interval) | $0 |
| Source control | GitHub | $0 |
| **Total** | | **$0/month** |

### AI Usage Summary
| Task | Model | When |
|------|-------|------|
| Classify signals into civic issues | Gemini 2.5 Flash | Discovery Agent (every 6h) |
| Validate citizen photos | Gemini 2.5 Flash (multimodal) | Confirmation Agent (per upload) |
| Identify government authority | Lookup table → Gemini fallback | Resolution Agent |
| Draft escalation letter | Gemini 2.5 Flash | Resolution Agent |

---

## Project Structure

```
civicpulse/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, lifespan, auto-boot discovery
│   ├── database.py                # SQLite — issues, confirmations, escalations tables
│   ├── scheduler.py               # APScheduler — discovery 6h, escalation 30min
│   ├── seed_data.py               # Fallback example data (only if Gemini quota exhausted)
│   ├── agents/
│   │   ├── discovery_agent.py     # Agent 1 — multi-source fetch + Gemini classify + cluster
│   │   ├── confirmation_agent.py  # Agent 2 — Gemini Vision photo validation
│   │   └── resolution_agent.py    # Agent 3 — authority lookup + letter draft + email
│   ├── services/
│   │   ├── gemini_service.py      # Gemini 2.5 Flash — classify, vision, letter, retry logic
│   │   ├── twitter_service.py     # Twitter v2 API + city mock fallback
│   │   ├── reddit_service.py      # Reddit OAuth2 (optional)
│   │   ├── news_rss_service.py    # Google News RSS — live, no auth
│   │   ├── maps_reviews_service.py# Google Maps Reviews (disabled — paid)
│   │   ├── geocoding_service.py   # Neighbourhood coordinate lookup (60+ areas)
│   │   ├── clustering_service.py  # Haversine geospatial clustering
│   │   ├── authority_service.py   # BBMP/BMC/GHMC/BESCOM/BWSSB lookup table
│   │   └── email_service.py       # SMTP dispatch (gracefully skips if unconfigured)
│   └── routers/
│       ├── issues.py              # GET /api/issues, GET /api/issues/:id
│       ├── confirmations.py       # POST /api/confirm/:id (photo upload)
│       └── admin.py               # POST /api/admin/trigger-discovery, trigger-escalation
└── frontend/
    └── src/
        ├── App.jsx                # Main layout, filter tabs, admin controls
        ├── components/
        │   ├── MapView.jsx        # Leaflet map, circle markers, popups, fly-to
        │   ├── IssueCard.jsx      # Issue list item, confidence bar, expand detail
        │   ├── ConfirmModal.jsx   # Photo upload + Gemini validation result
        │   ├── ImpactDashboard.jsx# Stats bar, pipeline visual
        │   ├── EscalationLog.jsx  # Shows generated letter and authority
        │   └── StatusBadge.jsx    # Colour-coded status pill
        ├── hooks/
        │   └── useIssues.js       # Parallel fetch issues + stats, reload helper
        └── utils/
            └── api.js             # All API calls, VITE_API_URL base
```

---

## Cities & Authorities

| City | Issues Monitored | Authorities |
|------|-----------------|-------------|
| **Bengaluru** | Potholes, Streetlights, Water Leaks, Garbage, Drainage, Footpaths, Road Damage | BBMP (Roads, SWM, SWD, Horticulture), BESCOM, BWSSB |
| **Mumbai** | Potholes, Waterlogging, Garbage, Streetlights, Road Damage | BMC (Roads, Hydraulic, SWM, SWD), MSEDCL |
| **Hyderabad** | Potholes, Streetlights, Water Leaks, Garbage, Road Damage | GHMC (Engineering, Sanitation), TSSPDCL, HMWSSB |

---

## Environment Variables

### Required
| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google AI Studio — free at aistudio.google.com |

### Required on Render
| Variable | Value |
|----------|-------|
| `FRONTEND_URL` | `https://civicradar.netlify.app` |

### Optional
| Variable | Effect if missing |
|----------|------------------|
| `TWITTER_BEARER_TOKEN` | City mock tweets used |
| `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` | Reddit source skipped |
| `SMTP_USER` + `SMTP_PASS` | Letter shown in UI, not emailed |

---

## Local Development

```bash
# Backend
cd civicpulse
cp .env.example .env        # add GEMINI_API_KEY
pip install -r requirements.txt
cd backend
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (interactive API)

# Frontend
cd civicpulse/frontend
cp .env.example .env        # VITE_API_URL=http://localhost:8000
npm install
npm run dev
# → http://localhost:5173
```

---

## Future Improvements

| Feature | What it adds |
|---------|-------------|
| Twitter paid plan | Real tweet search ($100/month) — architecture ready |
| Live SMTP email | Letters actually reach government inboxes — code built, needs credentials |
| Telegram bot | Citizens report via chat, get notified on escalation — completely free |
| Reddit credentials | r/bangalore, r/mumbai, r/hyderabad signal — free OAuth2 |
| Google Maps Reviews | Infrastructure-level signal — needs paid key |
| Resolution tracking | Follow up with authorities, close issues when fixed |
| More cities | Delhi (MCD), Chennai (GCC), Pune (PMC) — lookup table extensible |
| PostgreSQL | Replace SQLite for concurrent writes at scale (Supabase free tier) |
| Push notifications | Notify citizens when their confirmed issue escalates |
| WhatsApp | Meta charges per conversation — not free |
