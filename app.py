"""
Skill Wallet Capstone Project 1
Multimodal Construction Intelligence Platform
Categories: Generative AI | Real Estate Decision Support
Platform ID: 6ac4c98d1dcde6d7857c1642
"""

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime

import streamlit as st
from PIL import Image

APP_NAME = "Multimodal Construction Intelligence Platform"
APP_VERSION = "1.0.0"

# ------------------------------------------------------------------
# Gemini client (stdlib only - no SDK dependency)
# ------------------------------------------------------------------
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)


def get_api_key() -> str:
    return (
        st.session_state.get("api_key")
        or st.secrets.get("GEMINI_API_KEY", "")
    ).strip()


def call_gemini(api_key: str, parts: list, generation_config: dict | None = None) -> str:
    """Call Gemini generateContent. Returns text or raises RuntimeError."""
    body = {"contents": [{"parts": parts}]}
    if generation_config:
        body["generationConfig"] = generation_config
    req = urllib.request.Request(
        GEMINI_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError("Empty AI response")
        return candidates[0]["content"]["parts"][0]["text"]
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc


def parse_json_reply(text: str) -> dict:
    """Extract JSON object from an LLM reply, tolerating code fences."""
    cleaned = re.sub(r"```(?:json)?", "", text).strip().strip("`")
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("AI response did not contain a JSON object")
    return json.loads(match.group(0))


# ------------------------------------------------------------------
# Deterministic demo / offline engine (fallback when no API key)
# ------------------------------------------------------------------
def demo_ppe_payload(has_image: bool) -> dict:
    return {
        "safety_score": 72 if has_image else 0,
        "overall_status": "Partially Compliant" if has_image else "No Image",
        "ppe_detection": {
            "helmets": {"present": True, "count": 3, "missing": 1},
            "high_vis_vests": {"present": True, "count": 3, "missing": 1},
            "steel_toe_boots": {"present": False, "count": 1, "missing": 3},
            "safety_harnesses": {"present": True, "count": 2, "missing": 2},
        },
        "site_hazards": [
            {
                "hazard": "Worker without helmet near scaffolding",
                "severity": "High",
                "remedy": "Issue helmet immediately and enforce IS 456 gate checks",
            },
            {
                "hazard": "Loose cable across walkway",
                "severity": "Medium",
                "remedy": "Route cables overhead or use protective ramps per OSHA 1926.404",
            },
        ],
        "standards_checked": ["OSHA 29 CFR 1926", "IS 4508"],
        "summary": "Demonstration mode output. Add a Gemini API key for live multimodal analysis.",
    }


def demo_crack_payload(has_image: bool) -> dict:
    return {
        "crack_type": "Hairline",
        "severity": "Low",
        "estimated_width_mm": 0.8 if has_image else 0.0,
        "root_causes": [
            "Concrete shrinkage during curing",
            "Thermal cycling between pours",
        ],
        "recommended_repairs": [
            "Surface sealing with flexible polymer filler",
            "Monitor for widening over 30 days",
        ],
        "urgency": "Schedule within 1 month",
        "structural_integrity": "Sound - cosmetic defect only",
        "summary": "Demonstration mode output. Add a Gemini API key for live crack diagnostics.",
    }


# ------------------------------------------------------------------
# Deterministic valuation engine (Epic 3 - no AI needed)
# ------------------------------------------------------------------
COST_PER_SQFT = {
    "Residential - Apartment": {"1": 4200, "2": 2800, "3": 2100},
    "Residential - Villa": {"1": 5500, "2": 3600, "3": 2600},
    "Commercial - Office": {"1": 6200, "2": 4300, "3": 3200},
    "Commercial - Retail": {"1": 7000, "2": 4800, "3": 3500},
    "Industrial - Warehouse": {"1": 3800, "2": 2400, "3": 1800},
}

CITY_MARKET_INDEX = {"1": 1.12, "2": 0.95, "3": 0.82}

STEEL_KG_SQFT = {"Residential - Apartment": 3.6, "Residential - Villa": 4.2,
                 "Commercial - Office": 5.5, "Commercial - Retail": 5.0,
                 "Industrial - Warehouse": 6.2}
CEMENT_KG_SQFT = 40


def rupees_inr(n: float) -> str:
    if n >= 1e7:
        return f"₹ {n/1e7:,.2f} Cr"
    return f"₹ {n/1e5:,.2f} L"


def compute_valuation(structure, sqft, tier, completion: float) -> dict:
    total = sqft * COST_PER_SQFT[structure][tier]
    incurred = total * completion
    value = sqft * COST_PER_SQFT[structure][tier] * CITY_MARKET_INDEX[tier] * (0.55 + 0.45 * completion)
    appreciation = value - incurred
    steel = sqft * STEEL_KG_SQFT[structure]
    cement = sqft * CEMENT_KG_SQFT
    return {
        "total_budget": total,
        "capex_incurred": incurred,
        "market_valuation": value,
        "appreciation": appreciation,
        "steel_kg": steel,
        "cement_kg_50kg_bags": cement / 50,
        "budget_per_sqft": total / sqft,
    }


# ------------------------------------------------------------------
# Styling (modern CSS)
# ------------------------------------------------------------------
st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide")

CSS = """
<style>
    :root { --accent:#0ea5e9; --dark:#0f172a; }
    .hero {
        background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 60%,#0ea5e9 100%);
        color:#fff;border-radius:16px;padding:2rem 2.5rem;margin-bottom:1rem;
    }
    .hero h1{margin:0 0 .4rem 0;font-size:2rem;}
    .hero p{margin:.2rem 0;opacity:.88;}
    .pill{display:inline-block;padding:.3rem .8rem;border-radius:999px;
          font-size:.8rem;font-weight:600;margin-right:.4rem;}
    .pill-ok{background:#dcfce7;color:#166534;}
    .pill-warn{background:#fef9c3;color:#854d0e;}
    .pill-bad{background:#fee2e2;color:#991b1b;}
    .pill-info{background:#e0f2fe;color:#075985;}
    .card{
        background:#ffffff0d;border:1px solid #ffffff22;border-radius:14px;
        padding:1.1rem 1.3rem;margin-top:.4rem;
    }
    h2,h3,h4{color:#e2e8f0;}
    .stTabs [data-baseweb="tab-list"]{gap:.35rem;}
    .stTabs [data-baseweb="tab"]{
        border-radius:10px 10px 0 0;padding:.55rem 1.1rem;font-weight:600;
    }
    .stTabs [aria-selected="true"]{background:#0ea5e922;color:#38bdf8 !important;}
    section[data-testid="stSidebar"]{background:#0f172a;}
    section[data-testid="stSidebar"] *{color:#e2e8f0;}
    .chat-msg{padding:.7rem 1rem;border-radius:12px;margin-bottom:.5rem;max-width:95%;}
    .chat-user{background:#075985;color:#e0f2fe;margin-left:auto;}
    .chat-bot{background:#1e293b;color:#e2e8f0;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def severity_pill(level: str) -> str:
    mapping = {"LOW": ("pill-ok", "Low"), "MEDIUM": ("pill-warn", "Medium"),
               "HIGH": ("pill-bad", "High"), "CRITICAL": ("pill-bad", "Critical")}
    cls, label = mapping.get(level.upper(), ("pill-info", level or "Info"))
    return f'<span class="pill {cls}">{label}</span>'


# ------------------------------------------------------------------
# Sidebar: API key, architecture overview, navigation guide
# ------------------------------------------------------------------
with st.sidebar:
    st.header("🔐 Access")
    user_key = st.text_input(
        "Google Gemini API key",
        type="password",
        key="api_key",
        help="Leave empty to run the built-in demonstration engine. "
             "Get a free key at aistudio.google.com/apikey",
    )
    active_key = get_api_key()
    if active_key:
        st.success("Live AI mode active")
        mode_tag = '<span class="pill pill-ok">AI Mode</span>'
    else:
        st.info("Demonstration mode — deterministic offline engine")
        mode_tag = '<span class="pill pill-warn">Demo Mode</span>'

    st.divider()
    st.header("🧠 Architecture")
    st.markdown(
        """
        | Layer | Technology |
        |---|---|
        | Frontend | Streamlit (Python) |
        | AI Core | Gemini 2.5 Flash (multimodal) |
        | Vision | Gemini vision prompts |
        | Contracts | Strict JSON schemas |
        | Rendering | Pollinations AI |
        | Hosting | Streamlit Community Cloud |
        | Datastore | Stateless — none |
        """
    )
    st.divider()
    st.header("🧭 Modules")
    st.markdown(
        "1. Site Safety & PPE Audit\n"
        "2. Crack Diagnostics\n"
        "3. Planning & Valuation\n"
        "4. Assistant & Weather Advisory"
    )
    st.caption(f"Skill Wallet Capstone · Platform ID 6ac4c98d1dcde6d7857c1642 · v{APP_VERSION}")

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <h1>🏗️ {APP_NAME}</h1>
      <p>Multimodal AI decision support for construction safety, structural diagnostics,
      planning, valuation and daily site operations.</p>
      <p>{mode_tag}<span class="pill pill-info">Real Estate Decision Support</span>
      <span class="pill pill-info">Skill Wallet Capstone 1</span></p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🦺 Site Safety & PPE Audit",
        "🔎 Crack Diagnostics",
        "📐 Planning & Valuation",
        "🌤️ Assistant & Weather Advisory",
    ]
)

# ==================================================================
# Tab 1 - Site Safety & PPE Audit (Epic 2)
# ==================================================================
with tab1:
    st.subheader("Site Safety ⋅ PPE Compliance Audit")
    st.caption("Upload a construction site photo. AI audits helmets, high-vis vests, "
               "steel-toe boots and harnesses against OSHA 1926 and IS 456.")

    upload1 = st.file_uploader("Site photo (JPG / PNG)", type=["jpg", "jpeg", "png"], key="ppe")
    analyze1 = st.button("🦺 Run Safety Audit", type="primary")

    if analyze1:
        with st.spinner("Auditing site…"):
            try:
                if active_key:
                    parts = [{"text":
                        "You are a certified construction safety auditor (OSHA 29 CFR 1926 and "
                        "Indian Standards IS 456/IS 4508). Analyse this construction site photo. "
                        "Return ONLY a JSON object, no commentary, with these exact keys: "
                        '{"safety_score": <0-100 int>, "overall_status": "<string>", '
                        '"ppe_detection": {"helmets": {"present": <bool>, "count": <int>, "missing": <int>}, '
                        '"high_vis_vests": {...}, "steel_toe_boots": {...}, "safety_harnesses": {...}}, '
                        '"site_hazards": [{"hazard": "<string>", "severity": "Low|Medium|High|Critical", '
                        '"remedy": "<string>"}], '
                        '"standards_checked": ["<string>"], "summary": "<string>"}'}]
                    if upload1:
                        img = Image.open(upload1)
                        parts.append({"inline_data": {"mime_type": upload1.type,
                                                      "data": img_bytes_b64(upload1)}})
                        payload = parse_json_reply(call_gemini(active_key, parts))
                    else:
                        payload = demo_ppe_payload(False)
                else:
                    payload = demo_ppe_payload(upload1 is not None)
            except Exception as exc:
                st.error(f"Audit failed ({exc}). Showing demonstration data instead.")
                payload = demo_ppe_payload(upload1 is not None)

        score = payload.get("safety_score", 0)
        status = payload.get("overall_status", "Unknown")
        c1, c2 = st.columns([1.2, 2])
        with c1:
            st.metric("Safety Score", f"{score}/100")
        with c2:
            st.markdown(f'<div class="card"><b>Overall Status:</b> {status}</div>',
                        unsafe_allow_html=True)
        for hazard in payload.get("site_hazards", []):
            st.markdown(
                f'<div class="card">{severity_pill(hazard.get("severity",""))} '
                f'<b>{hazard.get("hazard","")}</b><br><i>Remedy: '
                f'{hazard.get("remedy","")}</i></div>',
                unsafe_allow_html=True,
            )
        with st.expander("PPE Detection Checklist"):
            st.json(payload.get("ppe_detection", {}))
        report = {"report_type": "ppe_safety_audit",
                  "generated_at": datetime.now().isoformat(),
                  "data": payload}
        st.download_button("💾 Download JSON report", json.dumps(report, indent=2),
                           "ppe_safety_report.json", "application/json")

# ==================================================================
# Tab 2 - Crack Diagnostics & Structural Integrity (Epic 2)
# ==================================================================
with tab2:
    st.subheader("Concrete Crack ⋅ Structural Diagnostics")
    st.caption("Upload a photo of cracks in concrete or masonry surfaces for AI-governed "
               "classification, root-cause analysis and engineering repairs.")

    upload2 = st.file_uploader("Surface photo (JPG / PNG)", type=["jpg", "jpeg", "png"], key="crack")
    analyze2 = st.button("🔎 Diagnose Crack", type="primary")

    if analyze2:
        with st.spinner("Running diagnostics…"):
            try:
                if active_key and upload2:
                    parts = [{"text":
                        "You are a licensed structural engineer. Analyse the crack in this photo. "
                        "Return ONLY JSON with these exact keys: "
                        '{"crack_type": "Hairline|Settlement|Structural Shear|Thermal Expansion|Spalling", '
                        '"severity": "Low|Medium|High|Critical", "estimated_width_mm": <float>, '
                        '"root_causes": ["<string>"], "recommended_repairs": ["<string> (mention epoxy '
                        'injection, re-grouting etc.)"], "urgency": "<string>", '
                        '"structural_integrity": "<string>", "summary": "<string>"}'}]
                    img = Image.open(upload2)
                    parts.append({"inline_data": {"mime_type": upload2.type,
                                                  "data": image_to_b64(upload2)}})
                    payload = parse_json_reply(call_gemini(active_key, parts))
                else:
                    payload = demo_crack_payload(upload2 is not None)
            except Exception as exc:
                st.error(f"Diagnostics failed ({exc}). Showing demonstration data instead.")
                payload = demo_crack_payload(upload2 is not None)

        col1, col2, col3 = st.columns(3)
        col1.metric("Defect Type", payload.get("crack_type", "—"))
        col2.metric("Severity", payload.get("severity", "—"))
        col3.metric("Est. Width", f'{payload.get("estimated_width_mm", 0)} mm')
        st.markdown(f'<div class="card"><b>Urgency:</b> {payload.get("urgency","")}<br>'
                    f'<b>Structural Integrity:</b> {payload.get("structural_integrity","")}</div>',
                    unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        cc1.markdown("**Root Causes**")
        cc1.markdown("<br>".join([f"• {x}" for x in payload.get("root_causes", [])]),
                     unsafe_allow_html=True)
        cc2.markdown("**Recommended Repairs**")
        cc2.markdown("<br>".join([f"• {x}" for x in payload.get("recommended_repairs", [])]),
                     unsafe_allow_html=True)
        report = {"report_type": "crack_diagnostics",
                  "generated_at": datetime.now().isoformat(),
                  "data": payload}
        st.download_button("💾 Download JSON report", json.dumps(report, indent=2),
                           "crack_diagnostics.json", "application/json")

# ==================================================================
# Tab 3 - Planning & Real Estate Valuation (Epic 3)
# ==================================================================
with tab3:
    st.subheader("Project Budget ⋅ Real Estate Valuation (INR)")
    colA, colB = st.columns(2)
    with colA:
        structure = st.selectbox("Structure type", list(COST_PER_SQFT.keys()))
        tier = st.radio("Location tier", ["1", "2", "3"],
                        captions=["Tier 1 (Metro)", "Tier 2", "Tier 3"],
                        index=0, horizontal=True)
    with colB:
        sqft = st.number_input("Built-up area (sqft)", min_value=200, max_value=100000, value=1800, step=50)
        completion = st.slider("Construction completion (%)", 0, 100, 65)

    frag = compute_valuation(structure, sqft, tier, completion / 100)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Project Budget", rupees_inr(frag["total_budget"]))
    m2.metric("CapEx Incurred", rupees_inr(frag["capex_incurred"]))
    m3.metric("Market Asset Valuation", rupees_inr(frag["market_valuation"]))
    m4.metric("Appreciation", rupees_inr(frag["appreciation"]),
              delta=("+" if frag["appreciation"] >= 0 else "") + f'{frag["appreciation"]/frag["total_budget"]*100:.0f}%')

    st.markdown("**Milestone Progress**")
    st.progress(completion / 100)
    r1, r2, r3 = st.columns(3)
    r1.metric("Steel Requirement", f'{frag["steel_kg"]:,.0f} kg')
    r2.metric("Cement Requirement", f'{frag["cement_kg_50kg_bags"]:,.0f} bags (50 kg)')
    r3.metric("Budget / sqft", f'₹ {frag["budget_per_sqft"]:,.0f}')

    st.divider()
    st.markdown("#### 🧱 Conceptual 3D Architectural Rendering")
    render_prompt = st.text_input(
        "Rendering prompt",
        value=f"Isometric 3D architectural render of a modern Indian {structure.lower()}, "
              f"{sqft:,.0f} sqft, glass and concrete facade, aerial angle, cinematic light",
    )
    if st.button("🖼️ Generate 3D Rendering"):
        url = ("https://image.pollinations.ai/prompt/"
               + urllib.parse.quote(render_prompt))
        try:
            urllib.request.urlopen(url, timeout=90)
            st.image(url, caption="Pollinations AI rendering", use_container_width=True)
        except Exception:
            st.image(url, caption="Pollinations AI rendering", use_container_width=True,
                     output_format="JPEG")

# ==================================================================
# Tab 4 - Weather Advisory + Multi-turn Assistant (Epic 5)
# ==================================================================
WEATHER = {
    "Normal": ("✅ Normal Conditions",
               ["All operations may proceed as per standard protocol.",
                "Maintain routine QA and documentation."]),
    "High Wind": ("💨 High Wind Alert",
                  ["SUSPEND crane operations above 45 km/h gusts (OSHA 1926.1431).",
                   "Secure loose materials, sheeting and formwork on upper floors.",
                   "Use tag lines; postpone heavy lifts till conditions normalise."]),
    "Heavy Rain": ("🌧️ Heavy Rain Protocol",
                   ["Pause concrete pours; protect placed concrete with curing covers (IS 456).",
                    "Isolate electrical panels; ground temporary power lines.",
                    "Ensure pumps/sullying are operational; raise worker visibility rating."]),
    "Extreme Heat": ("🔥 Extreme Heat Protocol",
                     ["Wet-cure slabs frequently; schedule pours early morning.",
                      "Enforce hydration breaks & shaded rest zones for workers.",
                      "Reschedule hot-work/welding; monitor heat-exhaustion first-aid readiness."]),
}
weather_sel = st.selectbox("Today's weather condition", list(WEATHER.keys()))
icon_title, alerts = WEATHER[weather_sel]
st.markdown(f'<div class="card"><b>{icon_title}</b></div>', unsafe_allow_html=True)
for i, alert in enumerate(alerts):
    st.warning(alert, icon="⚠" if weather_sel != "Normal" else "✅")

st.divider()
st.markdown("#### 🤖 Daily Site Assistant (multi-turn construction engineering chatbot)")

if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "assistant", "content":
            "Hello Site Engineer! Ask me about safety codes, curing, steel schedules, "
            "concrete grades, or anything on your site."}
    ]

for msg in st.session_state.chat:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-msg chat-user">🧑‍💼 {msg["content"]}</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-msg chat-bot">🤖 {msg["content"]}</div>',
                    unsafe_allow_html=True)

prompt = st.chat_input("Ask about your site…")
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    if active_key:
        parts = [{"text":
            "You are a practical construction engineering assistant for an Indian site. "
            "Answer concisely with reference codes (IS/OSHA) where useful.\n\n"
            "Conversation so far:\n" +
            "\n".join(f'{m["role"]}: {m["content"]}' for m in st.session_state.chat[-10:]),
        }]
        try:
            reply = call_gemini(active_key, parts)
        except Exception as exc:
            reply = f"AI unavailable ({exc}). Please retry or clear the key."
    else:
        reply = ("Demo mode: no Gemini API key configured. "
                 "Add one in the sidebar (or via secrets) to chat with the live AI.")
    st.session_state.chat.append({"role": "assistant", "content": reply})
    st.rerun()

st.divider()
st.caption(f"© 2026 · {APP_NAME} · Built for Skill Wallet evaluation · "
           "Stateless app — Streamlit Community Cloud ready.")


# ------------------------------------------------------------------
# helper
# ------------------------------------------------------------------
def image_to_b64(f) -> str:  # noqa: ANN001
    import base64
    return base64.b64encode(f.getvalue()).decode("utf-8")
