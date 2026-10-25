# 🏗️ Multimodal Construction Intelligence Platform

**Skill Wallet Capstone Project 1** · Platform ID `6ac4c98d1dcde6d7857c1642`
**Category:** Generative AI | Real Estate Decision Support

> Live Demo: **https://multimodal-construction-intelligence-jvjpieyru5jse6zpmaeq7g.streamlit.app/**
> GitHub: https://github.com/Sarthak-builds/SkillWallet-Capstones

## 📌 Overview
An intelligent decision-support system for construction professionals. It analyzes
site photos to audit PPE safety compliance, classifies concrete cracks with severity
scores, estimates construction costs and real-estate valuation in INR, and provides
weather-aware daily site protocols — all through a strict JSON data contract with a
multimodal LLM (Google Gemini 2.5 Flash).

## 🧩 Modules (Kanban Epics Coverage)

| Module | Epic | Capability |
|---|---|---|
| 🦺 Site Safety & PPE Audit | Epic 2 | Vision audit of helmets, vests, boots, harnesses vs OSHA 1926 & IS 456; safety score, hazards w/ severity + remedies, downloadable JSON report |
| 🔎 Crack Diagnostics | Epic 2 | Classifies Hairline / Settlement / Structural Shear / Thermal Expansion / Spalling; width (mm), root causes, engineering repairs, urgency |
| 📐 Planning & Valuation | Epic 3 | Budget & CapEx estimation, market valuation (Lakhs/Crores), steel/cement metrics, milestone progress, Pollinations AI 3D rendering |
| 🌤️ Assistant & Weather Advisory | Epic 5 | Weather-condition safety protocols (crane suspension, curing, electrical hazards) + multi-turn construction assistant chatbot |

Epic 4 (Multimodal AI & JSON Contracts) and Epic 6 (Interface, Testing, Cloud
Deployment) are implemented across all modules; Pre-requisites and Epic 1 are
covered by the environment spec in this README.

## 🛠 Tech Stack
- Python 3.9+ (stdlib-only Gemini calls — no heavyweight SDK)
- Streamlit (frontend + deployment)
- Google Gemini 2.5 Flash (multimodal vision + text)
- Pillow (image handling)
- Pollinations AI (conceptual 3D rendering)
- JSON data contracts · zero database dependencies (1-click cloud deploy)

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 API Key
The app works out-of-the-box in **demonstration mode** (deterministic offline engine).
For **live AI mode**, supply a Gemini API key either:
- in the sidebar field (session-only), or
- as a Streamlit Cloud secret named `GEMINI_API_KEY`
  (App → Settings → Secrets → `GEMINI_API_KEY = "AIza..."`).

Free key: https://aistudio.google.com/apikey

## 🏗 Architecture
```
Streamlit UI ──▲── Gemini 2.5 Flash (multimodal, strict JSON contracts)
   │           ▲── Deterministic demo engine (fallback, no key required)
   └────────── ▲── Valuation engine (INR, tier-aware, deterministic)
   └────────── ▲── Pollinations AI (rendering) · Stateless — no DB
```

## 🧪 Testing
All modules are guarded with exception handling; AI failures gracefully degrade to
the demonstration engine. Helper: run `streamlit run app.py` and exercise each tab
(validator scripts under each epic are inline in the app flow).

## 📄 License
MIT
