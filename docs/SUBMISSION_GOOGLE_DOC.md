# CivicPulse — Project Description
### Vibe2Ship Hackathon Submission

---

## Problem Statement Selected
**Problem Statement 2: Community Hero — Hyperlocal Problem Solver**

---

## Solution Overview

CivicPulse is a multi-agent autonomous civic intelligence platform that inverts the traditional citizen-reporting model. Instead of waiting for citizens to report issues, CivicPulse's AI agent proactively discovers civic complaints from public social media signals, clusters them geospatially to validate they are real, and then lets citizens confirm issues with a single tap. When enough citizens confirm an issue, the Resolution Agent autonomously identifies the correct government authority, drafts a formal escalation letter using Gemini Pro, and sends it — all without human initiation.

**The core insight:** 90% of civic issues are never formally reported. Citizens complain on Twitter and WhatsApp, but never to the government. CivicPulse bridges this gap by discovering complaints where they already exist.

---

## Key Features

1. **Autonomous Discovery Agent** — Runs every 6 hours, scanning Twitter/X and Google Maps reviews for civic complaints using Gemini 1.5 Flash classification.

2. **Geospatial Clustering** — Uses haversine distance to cluster nearby complaints of the same category, confirming issues are real before surfacing them (reduces noise).

3. **One-Tap Citizen Confirmation** — Citizens see already-discovered issues on a map and confirm with one tap instead of filling a 5-field form. Optional photo upload.

4. **AI Photo Validation** — Gemini 1.5 Flash (multimodal) validates uploaded photos match the reported issue category, preventing false confirmations.

5. **Autonomous Resolution Agent** — Triggers when an issue reaches 5+ confirmations: identifies the responsible authority (BBMP, BMC, GHMC, etc.), drafts a formal letter with Gemini 1.5 Pro, and dispatches via email.

6. **Real-Time Impact Dashboard** — Shows live counts of discovered, confirmed, escalated, and resolved issues with citizen confirmation totals.

7. **Full Issue Lifecycle Tracking** — DISCOVERED → CONFIRMED → ESCALATED → RESOLVED with timestamps and escalation letter history.

---

## Technologies Used

| Category | Technology |
|---|---|
| Backend Framework | FastAPI (Python) |
| Task Scheduling | APScheduler |
| Frontend | React 18, Vite 5, Tailwind CSS |
| Database | SQLite (local), Firestore (production) |
| Email | SMTP via Gmail |
| Signal Source | Twitter/X API v2 |
| Maps | Google Maps JavaScript API |
| Deployment | Google AI Studio (backend), Vercel (frontend) |

---

## Google Technologies Utilized

| Google Technology | How It's Used |
|---|---|
| **Gemini 1.5 Flash** | Civic issue classification from social media text; geospatial signal analysis |
| **Gemini 1.5 Flash (Vision/Multimodal)** | Photo validation — confirms uploaded images match reported issue categories |
| **Gemini 1.5 Pro** | Drafting formal escalation letters to government authorities |
| **Google Maps JavaScript API** | Interactive map showing issue locations with color-coded status markers |
| **Google AI Studio** | Backend deployment and hosting |

---

## Architecture

```
Twitter/X API + Google Maps Reviews
           │
           ▼
[Agent 1: Discovery — Gemini 1.5 Flash]
  • Classifies civic complaints
  • Geospatial clustering (0.3km radius)
  • Confidence scoring
           │
           ▼
[Citizen App — React + Google Maps]
  • Map-first view of discovered issues
  • One-tap confirmation + photo upload
  • Gemini validates photo match
           │ (5+ confirmations)
           ▼
[Agent 3: Resolution — Gemini 1.5 Pro]
  • Identifies authority (BBMP/BMC/GHMC/PWD)
  • Drafts formal grievance letter
  • Sends email + updates tracking
```
