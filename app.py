"""
Metal Sustainability Impact Analyzer
Greenly-style Step-by-Step Dashboard
"""

import streamlit as st
import pickle, os, numpy as np, pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Metal Sustainability Analyzer", page_icon="♻️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #f7f9f7 !important; }

/* TOP HEADER */
.top-header {
    background: #1a4731; padding: 36px 48px 28px;
    color: white; text-align: center;
}
.top-header h1 { font-size: 30px; font-weight: 700; color: white; margin: 0 0 8px; }
.top-header p  { font-size: 14px; color: rgba(255,255,255,0.75); margin: 0; }

/* SIDEBAR */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"] {
    background: #ffffff !important;
    border-right: 1px solid #e8ede8 !important;
}
.sidebar-brand {
    background: #1a4731;
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 8px;
}
.sidebar-brand .title { color: white; font-size: 15px; font-weight: 700; display:block; }
.sidebar-brand .sub   { color: rgba(255,255,255,0.65); font-size: 11px; margin-top: 3px; display:block; }

/* STEPS */
.steps-title { font-size: 12px; font-weight: 700; color: #1a2e1a;
               letter-spacing: 0.5px; text-transform: uppercase;
               padding: 16px 4px 8px; }
.step-item { display:flex; align-items:center; padding:11px 12px;
             gap:12px; border-left:3px solid transparent;
             border-radius: 0 8px 8px 0; margin-bottom:2px; }
.step-item.active  { background:#f0f7f0; border-left:3px solid #1a4731; }
.step-item.done    { background:#fafafa; }
.step-item.pending { background:#fff; }
.step-circle { width:28px; height:28px; border-radius:50%;
               display:flex; align-items:center; justify-content:center;
               font-size:12px; font-weight:700; flex-shrink:0; }
.step-circle.done    { background:#1a4731; color:white; }
.step-circle.current { background:#1a4731; color:white; }
.step-circle.pending { background:#e8ede8; color:#999; }
.step-label         { font-size:14px; font-weight:500; color:#1a2e1a; }
.step-label.pending { color:#bbb; font-weight:400; }

/* MAIN CONTENT */
.main-wrap { padding: 28px 36px; }

/* METAL CARDS */
.metal-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:16px; }
.metal-card {
    background:white; border:2px solid #e8ede8; border-radius:14px;
    padding:28px 20px; text-align:center; cursor:pointer;
    transition: all 0.2s; box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.metal-card:hover  { border-color:#1a4731; box-shadow:0 4px 16px rgba(26,71,49,0.12); }
.metal-card.sel    { border-color:#1a4731; background:#f0f7f0; }
.metal-card .icon  { font-size:36px; margin-bottom:10px; }
.metal-card .name  { font-size:16px; font-weight:700; color:#1a2e1a; margin-bottom:4px; }
.metal-card .desc  { font-size:12px; color:#888; }

/* PROCESS CARDS */
.process-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px; }
.process-card {
    background:white; border:2px solid #e8ede8; border-radius:14px;
    padding:24px; cursor:pointer;
    transition: all 0.2s; box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.process-card:hover { border-color:#1a4731; box-shadow:0 4px 16px rgba(26,71,49,0.12); }
.process-card.sel   { border-color:#1a4731; background:#f0f7f0; }
.process-card .p-icon  { font-size:32px; margin-bottom:10px; }
.process-card .p-name  { font-size:16px; font-weight:700; color:#1a2e1a; margin-bottom:6px; }
.process-card .p-desc  { font-size:13px; color:#666; line-height:1.5; }

/* SECTION CARD */
.section-card {
    background:white; border:1px solid #e8ede8; border-radius:12px;
    padding:24px; margin-bottom:20px;
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.section-card h3       { font-size:18px; font-weight:700; color:#1a2e1a; margin:0 0 4px; }
.section-card .subtitle { font-size:13px; color:#888; margin-bottom:20px; }

/* METRIC CARDS */
.metric-row { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:20px; }
.metric-card { background:white; border:1px solid #e8ede8; border-radius:12px;
               padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.metric-card-label { font-size:12px; color:#666; font-weight:500; margin-bottom:8px; }
.metric-card-value { font-size:26px; font-weight:700; line-height:1.1; margin-bottom:4px; }
.metric-card-sub   { font-size:12px; color:#888; }
.green-val  { color:#1a8a3c; }
.blue-val   { color:#2563eb; }
.purple-val { color:#7c3aed; }

/* DETAIL GRID */
.detail-grid  { display:grid; grid-template-columns:1fr 1fr; gap:28px; }
.detail-section h4       { font-size:14px; font-weight:700; margin-bottom:14px; }
.detail-section h4.green { color:#1a8a3c; }
.detail-section h4.blue  { color:#2563eb; }
.detail-section h4.amber { color:#d97706; }
.detail-row  { display:flex; justify-content:space-between;
               padding:8px 0; border-bottom:1px solid #f3f4f6;
               font-size:13px; color:#374151; }
.detail-row span:last-child { font-weight:600; color:#111; }

/* SUMMARY BOX */
.summary-box { background:#f9fafb; border:1px solid #e8ede8;
               border-radius:10px; padding:18px 22px; margin-top:20px; }
.summary-box h4 { font-size:15px; font-weight:700; margin-bottom:12px; }
.summary-row { display:flex; justify-content:space-between;
               padding:6px 0; font-size:13px; color:#374151; }
.summary-row span:last-child { font-weight:600; }

/* TIPS */
.tip-item { display:flex; gap:10px; padding:12px 0;
            border-bottom:1px solid #f3f4f6;
            font-size:13px; color:#374151; line-height:1.6; }

/* HISTORY */
.hist-row { display:flex; align-items:center; gap:14px;
            padding:10px 0; border-bottom:1px solid #f3f4f6;
            font-size:13px; color:#374151; flex-wrap:wrap; }

/* BADGE */
.badge { display:inline-block; padding:4px 12px; border-radius:50px;
         font-size:12px; font-weight:600; }
.badge-low    { background:#dcfce7; color:#16a34a; }
.badge-medium { background:#fef3c7; color:#d97706; }
.badge-high   { background:#fee2e2; color:#dc2626; }

/* NAV BUTTONS */
.nav-row { display:flex; justify-content:space-between; align-items:center;
           margin-top:24px; padding-top:20px; border-top:1px solid #e8ede8; }

/* BUTTON */
.stButton > button {
    background:#1a4731 !important; color:white !important;
    border:none !important; border-radius:8px !important;
    padding:10px 28px !important; font-weight:600 !important;
    font-size:14px !important;
}
.stButton > button:hover { background:#153d29 !important; }
/* Previous button - outline style via first button in nav row */
div[data-testid="column"]:first-child .stButton > button {
    background: white !important;
    color: #1a4731 !important;
    border: 1px solid #1a4731 !important;
}
div[data-testid="column"]:first-child .stButton > button:hover {
    background: #f0f7f0 !important;
}

div[data-testid="metric-container"] { display:none !important; }
label { color:#374151 !important; font-size:13px !important; font-weight:500 !important; }
.stSelectbox > div > div { border:1px solid #d1d5db !important;
    border-radius:8px !important; background:white !important; }
.stNumberInput > div > div > input { border:1px solid #d1d5db !important;
    border-radius:8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Load model ────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join("model", "metal_model.pkl")

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH): return None
    with open(MODEL_PATH, "rb") as f: return pickle.load(f)

payload = load_model()

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("step",1),("metal",None),("process",None),
              ("quantity",1000.0),("result",None),("history",[])]:
    if k not in st.session_state: st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
METALS = {
    "Aluminium": {"icon":"🔵","desc":"Lightweight & widely recycled"},
    "Steel":     {"icon":"⚙️","desc":"World's most recycled material"},
    "Copper":    {"icon":"🟠","desc":"Excellent electrical conductor"},
}
PROCESSES = {
    "Recycling": {"icon":"♻️","desc":"Processing already-used metal back into usable material. Much lower environmental impact."},
    "Mining":    {"icon":"⛏️","desc":"Extracting raw metal ore from the earth. Higher energy and water consumption."},
}
TIPS = {
    ("Aluminium","Mining"):    ["Aluminium mining consumes ~14,000 kWh/tonne — recycling cuts energy by 95%.",
                                "Bauxite mining causes major deforestation; prefer recycled aluminium.",
                                "Recycled aluminium uses only 5% of the energy of virgin production."],
    ("Aluminium","Recycling"): ["Excellent! Recycled aluminium is one of the most sustainable metals.",
                                "Aluminium can be recycled infinitely without losing quality.",
                                "Aim for 100% secondary aluminium to minimise footprint."],
    ("Steel","Mining"):        ["Steel accounts for ~8% of global CO₂ — recycling cuts this by 60–70%.",
                                "Switch to Electric Arc Furnace with recycled scrap to reduce water use.",
                                "Steel is the world's most recycled material — use more scrap!"],
    ("Steel","Recycling"):     ["Recycled steel uses ~60% less energy than virgin production.",
                                "Steel recycling diverts millions of tonnes from landfill yearly.",
                                "Source certified recycled steel (SCS Recycled Content standard)."],
    ("Copper","Mining"):       ["Copper mining uses 15,000–30,000 L water/tonne. Switch to recycled!",
                                "Mining grade copper ore is declining — recycling is more efficient.",
                                "Recycled copper retains 95% of the value of virgin copper."],
    ("Copper","Recycling"):    ["Recycled copper uses 85% less energy than mined copper.",
                                "Copper recycling prevents toxic mine tailings entering ecosystems.",
                                "High-grade copper scrap has the lowest processing emissions."],
}

def predict(metal_name, proc_name, qty):
    m = payload["le_metal"].transform([metal_name])[0]
    p = payload["le_process"].transform([proc_name])[0]
    r = payload["model"].predict(np.array([[m, p, qty]]))[0]
    return dict(zip(payload["targets"], r))

def get_impact(co2):
    if co2 < 300:  return "LOW",    "low"
    if co2 < 1500: return "MEDIUM", "medium"
    return "HIGH", "high"

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>
        <div class='title'>♻️ Metal LCA Analyzer</div>
        <div class='sub'>AI-Powered Sustainability Tool</div>
    </div>""", unsafe_allow_html=True)

    step = st.session_state.step
    steps_def = [
        (1, "Select Metal"),
        (2, "Configure Task"),
        (3, "Usage Parameters"),
        (4, "Results"),
        (5, "Testing"),
    ]
    st.markdown("<div class='steps-title'>Steps</div>", unsafe_allow_html=True)
    for num, label in steps_def:
        if num < step:
            circle_cls, label_cls, icon, item_cls = "done",    "",        "✓", "done"
        elif num == step:
            circle_cls, label_cls, icon, item_cls = "current", "",        str(num), "active"
        else:
            circle_cls, label_cls, icon, item_cls = "pending", "pending", str(num), "pending"
        st.markdown(f"""
        <div class='step-item {item_cls}'>
            <div class='step-circle {circle_cls}'>{icon}</div>
            <div class='step-label {label_cls}'>{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='margin:14px 0;border-color:#e8ede8'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='padding:12px 16px;background:#f0f7f0;border-radius:8px;font-size:11px;color:#555;line-height:1.8'>
        {'✅ Metal: <b>'+st.session_state.metal+'</b>' if st.session_state.metal else '⬜ Metal: not selected'}<br>
        {'✅ Process: <b>'+st.session_state.process+'</b>' if st.session_state.process else '⬜ Process: not selected'}<br>
        {'✅ Quantity: <b>'+f"{st.session_state.quantity:,.0f} kg"+'</b>' if st.session_state.quantity else '⬜ Quantity: not set'}
    </div>""", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='top-header'>
    <h1>⚡ AI-Powered Metal Sustainability Impact Analyzer</h1>
    <p>Calculate the carbon footprint and environmental impact of metal processes using Machine Learning</p>
</div>""", unsafe_allow_html=True)

if not payload:
    st.error("❌ Model not found! Please run train_model.py first.")
    st.stop()

st.markdown("<div class='main-wrap'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# STEP 1 — SELECT METAL
# ════════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown("""
    <div class='section-card'>
        <h3>Select Metal</h3>
        <div class='subtitle'>Choose the metal type you want to analyze</div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (metal, info) in enumerate(METALS.items()):
        with cols[i]:
            selected = st.session_state.metal == metal
            card_cls = "sel" if selected else ""
            st.markdown(f"""
            <div class='metal-card {card_cls}'>
                <div class='icon'>{info['icon']}</div>
                <div class='name'>{metal}</div>
                <div class='desc'>{info['desc']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {metal}", key=f"metal_{metal}"):
                st.session_state.metal = metal
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.metal:
        st.markdown(f"<div style='color:#1a4731;font-weight:600;margin-bottom:16px'>✅ Selected: {st.session_state.metal}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([6,1])
        with c2:
            if st.button("Next →", key="next1"):
                st.session_state.step = 2
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 2 — CONFIGURE TASK (Select Process)
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown(f"""
    <div class='section-card'>
        <h3>Configure Task</h3>
        <div class='subtitle'>Select the manufacturing process for <b>{st.session_state.metal}</b></div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (proc, info) in enumerate(PROCESSES.items()):
        with cols[i]:
            selected = st.session_state.process == proc
            card_cls = "sel" if selected else ""
            st.markdown(f"""
            <div class='process-card {card_cls}'>
                <div class='p-icon'>{info['icon']}</div>
                <div class='p-name'>{proc}</div>
                <div class='p-desc'>{info['desc']}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Select {proc}", key=f"proc_{proc}"):
                st.session_state.process = proc
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.process:
        st.markdown(f"<div style='color:#1a4731;font-weight:600;margin-bottom:16px'>✅ Selected: {st.session_state.process}</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,5,1])
    with c1:
        if st.button("← Previous", key="prev2"):
            st.session_state.step = 1; st.rerun()
    with c3:
        if st.session_state.process:
            if st.button("Next →", key="next2"):
                st.session_state.step = 3; st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 3 — USAGE PARAMETERS (Quantity)
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    st.markdown("""
    <div class='section-card'>
        <h3>Usage Parameters</h3>
        <div class='subtitle'>Enter the quantity to analyze</div>
    """, unsafe_allow_html=True)

    qty = st.slider("Quantity (kg)", min_value=100, max_value=10000,
                    value=int(st.session_state.quantity), step=100)
    st.session_state.quantity = float(qty)

    # Show quantity badge
    if qty < 1000:    scale, scale_cls = "Small scale", "#dcfce7"
    elif qty < 5000:  scale, scale_cls = "Medium scale", "#fef3c7"
    else:             scale, scale_cls = "Large scale",  "#fee2e2"

    st.markdown(f"""
    <div style='text-align:center;margin:10px 0 20px'>
        <span style='background:{scale_cls};padding:8px 24px;border-radius:50px;font-weight:600;font-size:15px'>
            {qty:,} kg — {scale}
        </span>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#f9fafb;border:1px solid #e8ede8;border-radius:10px;padding:18px 22px;margin-top:8px'>
        <div style='font-size:14px;font-weight:600;margin-bottom:12px'>Usage Examples</div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:20px;font-size:13px;color:#555'>
            <div>
                <div style='font-weight:600;color:#374151;margin-bottom:6px'>Daily Usage</div>
                • Personal use: 100–500 kg<br>
                • Small factory: 500–2,000 kg<br>
                • Medium plant: 2,000–5,000 kg
            </div>
            <div>
                <div style='font-weight:600;color:#374151;margin-bottom:6px'>Monthly Usage</div>
                • Enterprise: 5,000–10,000 kg<br>
                • Large scale: 10,000+ kg<br>
                • Research: 100–1,000 kg
            </div>
        </div>
    </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,5,1])
    with c1:
        if st.button("← Previous", key="prev3"):
            st.session_state.step = 2; st.rerun()
    with c3:
        if st.button("▶ Analyze", key="next3"):
            # Run prediction
            result = predict(st.session_state.metal, st.session_state.process, st.session_state.quantity)
            st.session_state.result = result
            impact_label, _ = get_impact(result["CO2(kg)"])
            st.session_state.history.insert(0, {
                "time": datetime.now().strftime("%H:%M:%S"),
                "metal": st.session_state.metal,
                "process": st.session_state.process,
                "qty": st.session_state.quantity,
                "energy": result["Energy(kwh)"],
                "water":  result["Water(liters)"],
                "co2":    result["CO2(kg)"],
                "waste":  result["Waste(kg)"],
                "impact": impact_label,
            })
            if len(st.session_state.history) > 10:
                st.session_state.history = st.session_state.history[:10]
            st.session_state.step = 4
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 4 — RESULTS
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    result  = st.session_state.result
    metal   = st.session_state.metal
    process = st.session_state.process
    qty     = st.session_state.quantity
    impact_label, impact_cls = get_impact(result["CO2(kg)"])

    # ── Animations CSS ────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes fadeSlideUp {
        from { opacity:0; transform:translateY(24px); }
        to   { opacity:1; transform:translateY(0); }
    }
    @keyframes countUp {
        from { opacity:0; transform:scale(0.8); }
        to   { opacity:1; transform:scale(1); }
    }
    @keyframes pulse {
        0%,100% { box-shadow: 0 0 0 0 rgba(26,71,49,0.15); }
        50%      { box-shadow: 0 0 0 10px rgba(26,71,49,0); }
    }
    .anim-card {
        animation: fadeSlideUp 0.5s ease both;
    }
    .anim-card:nth-child(1) { animation-delay: 0.05s; }
    .anim-card:nth-child(2) { animation-delay: 0.15s; }
    .anim-card:nth-child(3) { animation-delay: 0.25s; }
    .metric-card {
        animation: fadeSlideUp 0.5s ease both, pulse 2s ease 0.6s;
    }
    .metric-card-value {
        animation: countUp 0.6s ease both;
        animation-delay: 0.3s;
    }
    .section-card {
        animation: fadeSlideUp 0.55s ease both;
    }
    .result-badge {
        animation: fadeSlideUp 0.5s ease 0.2s both, pulse 2.5s ease 1s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Result badge banner ───────────────────────────────────────────────────
    badge_colors = {
        "low":    ("🟢","#dcfce7","#16a34a","#bbf7d0"),
        "medium": ("🟡","#fef3c7","#d97706","#fcd34d"),
        "high":   ("🔴","#fee2e2","#dc2626","#fca5a5"),
    }
    icon, bg, fg, border = badge_colors[impact_cls]
    st.markdown(f"""
    <div class='result-badge' style='background:{bg};border:1px solid {border};border-radius:14px;
         padding:18px 28px;margin-bottom:24px;display:flex;align-items:center;gap:16px'>
        <span style='font-size:36px'>{icon}</span>
        <div>
            <div style='font-size:12px;color:{fg};font-weight:700;letter-spacing:1.5px;
                 text-transform:uppercase;margin-bottom:4px'>Sustainability Rating</div>
            <div style='font-size:22px;font-weight:700;color:{fg}'>{impact_label} IMPACT</div>
            <div style='font-size:13px;color:#555;margin-top:2px'>
                {metal} · {process} · {qty:,.0f} kg processed</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Top 3 metric cards ────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    for col, delay, label, icon2, val, unit, cls in [
        (c1,"0.1s","Total Emissions",   "↗", f"{result['CO2(kg)']:,.4f}",       "kgCO₂e",   "green-val"),
        (c2,"0.2s","Per kg Emissions",  "⚡", f"{result['CO2(kg)']/qty:.6f}",    "kgCO₂e/kg","blue-val"),
        (c3,"0.3s","Total Energy",      "🔋", f"{result['Energy(kwh)']:,.2f}",   "kWh",      "purple-val"),
    ]:
        with col:
            st.markdown(f"""
            <div class='metric-card' style='animation-delay:{delay}'>
                <div class='metric-card-label'>{icon2} {label}</div>
                <div class='metric-card-value {cls}'>{val}<br>
                    <span style='font-size:15px;font-weight:500'>{unit}</span></div>
                <div class='metric-card-sub' style='margin-top:6px'>
                    {process} · {metal}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    labels = ["Energy (kWh)", "Water (L)", "CO₂ (kg)", "Waste (kg)"]
    values = [result["Energy(kwh)"], result["Water(liters)"], result["CO2(kg)"], result["Waste(kg)"]]
    colors = ["#1a8a3c","#2563eb","#d97706","#7c3aed"]

    # Shared axis style — dark readable text
    axis_style = dict(
        color="#1e293b",        # dark text
        tickfont=dict(color="#1e293b", size=11),
        title_font=dict(color="#1e293b"),
        gridcolor="#e2e8f0",
        linecolor="#cbd5e1",
        showline=True,
    )

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("<div class='section-card'><h3>Emissions Breakdown</h3><div class='subtitle'>Distribution of impact by source</div>", unsafe_allow_html=True)
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.5,
            marker=dict(colors=colors, line=dict(color="white", width=2)),
            textinfo="percent+label", textfont=dict(size=11, color="#1e293b"),
        ))
        fig_pie.update_layout(
            paper_bgcolor="white", plot_bgcolor="white",
            margin=dict(l=10,r=10,t=10,b=10), height=260, showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with ch2:
        st.markdown("<div class='section-card'><h3>Emissions by Category</h3><div class='subtitle'>Detailed breakdown of emission sources</div>", unsafe_allow_html=True)
        fig_bar = go.Figure(go.Bar(
            x=labels, y=values, marker_color=colors, marker_line_width=0,
            text=[f"{v:,.1f}" for v in values], textposition="outside",
            textfont=dict(color="#1e293b", size=10),
        ))
        fig_bar.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f8fafc",
            font=dict(color="#1e293b", family="Inter", size=12),
            xaxis=dict(**axis_style),
            yaxis=dict(**axis_style),
            margin=dict(l=10,r=10,t=30,b=10), height=260, showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Mining vs Recycling compare ───────────────────────────────────────────
    r_m = predict(metal, "Mining",    qty)
    r_r = predict(metal, "Recycling", qty)
    mkeys = ["Energy(kwh)","Water(liters)","CO2(kg)","Waste(kg)"]

    st.markdown("<div class='section-card'><h3>⚖️ Mining vs Recycling Comparison</h3><div class='subtitle'>Environmental impact for same quantity</div>", unsafe_allow_html=True)
    fig_cmp = go.Figure()
    fig_cmp.add_trace(go.Bar(
        name="Mining", x=labels, y=[r_m[k] for k in mkeys],
        marker_color="#ef4444", marker_line_width=0,
        text=[f"{r_m[k]:,.1f}" for k in mkeys], textposition="outside",
        textfont=dict(color="#1e293b", size=10),
    ))
    fig_cmp.add_trace(go.Bar(
        name="Recycling", x=labels, y=[r_r[k] for k in mkeys],
        marker_color="#1a8a3c", marker_line_width=0,
        text=[f"{r_r[k]:,.1f}" for k in mkeys], textposition="outside",
        textfont=dict(color="#1e293b", size=10),
    ))
    fig_cmp.update_layout(
        barmode="group", bargap=0.25, bargroupgap=0.08,
        paper_bgcolor="white", plot_bgcolor="#f8fafc",
        font=dict(color="#1e293b", family="Inter", size=12),
        xaxis=dict(**axis_style),
        yaxis=dict(**axis_style),
        legend=dict(bgcolor="white", bordercolor="#e2e8f0", borderwidth=1,
                    font=dict(color="#1e293b", size=12)),
        margin=dict(l=10,r=10,t=30,b=10), height=300,
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Detailed Calculation Results ──────────────────────────────────────────
    st.markdown(f"""
    <div class='section-card'>
        <h3>Detailed Calculation Results</h3>
        <div class='subtitle'>Complete breakdown of all calculations</div>
        <div class='detail-grid'>
            <div class='detail-section'>
                <h4 class='green'>Training Phase</h4>
                <div class='detail-row'><span>Energy Consumption</span><span>{result['Energy(kwh)']:,.2f} kWh</span></div>
                <div class='detail-row'><span>Emissions</span><span>{result['CO2(kg)']:,.6f} kgCO₂e</span></div>
            </div>
            <div class='detail-section'>
                <h4 class='blue'>Inference Phase</h4>
                <div class='detail-row'><span>Energy per Request</span><span>{result['Energy(kwh)']/qty:.4f} kWh</span></div>
                <div class='detail-row'><span>Total Energy</span><span>{result['Energy(kwh)']:,.2f} kWh</span></div>
                <div class='detail-row'><span>Total Emissions</span><span>{result['CO2(kg)']:,.6f} kgCO₂e</span></div>
            </div>
        </div>
        <div class='detail-grid' style='margin-top:20px'>
            <div class='detail-section'>
                <h4 class='amber'>Manufacturing</h4>
                <div class='detail-row'><span>Water Usage</span><span>{result['Water(liters)']:,.2f} liters</span></div>
                <div class='detail-row'><span>Waste Generated</span><span>{result['Waste(kg)']:,.2f} kg</span></div>
            </div>
        </div>
        <div class='summary-box'>
            <h4>Summary</h4>
            <div class='summary-row'><span>Total energy consumption</span><span>{result['Energy(kwh)']:,.2f} kWh</span></div>
            <div class='summary-row'><span>Total Carbon Emissions</span><span>{result['CO2(kg)']:,.6f} kgCO₂e</span></div>
            <div class='summary-row'><span>Emissions per kg</span><span>{result['CO2(kg)']/qty:.6f} kgCO₂e</span></div>
            <div class='summary-row'><span>Sustainability Rating</span>
                <span><span class='badge badge-{impact_cls}'>{impact_label} IMPACT</span></span></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────────────────────
    tips = TIPS.get((metal, process), ["Consider recycled materials to reduce environmental footprint."])
    tips_html = "".join([f"<div class='tip-item'><span>💡</span><span>{t}</span></div>" for t in tips])
    st.markdown(f"""
    <div class='section-card'>
        <h3>💡 Sustainability Recommendations</h3>
        <div class='subtitle'>Tips to reduce your environmental impact</div>
        {tips_html}
    </div>""", unsafe_allow_html=True)

    # ── History ───────────────────────────────────────────────────────────────
    if st.session_state.history:
        rows = "".join([f"""
        <div class='hist-row'>
            <span style='color:#888;min-width:65px'>{r['time']}</span>
            <span style='font-weight:600;min-width:80px'>{r['metal']}</span>
            <span style='min-width:80px'>{r['process']}</span>
            <span style='min-width:80px'>{r['qty']:,.0f} kg</span>
            <span>⚡ {r['energy']:,.1f} kWh</span>
            <span>🏭 {r['co2']:,.2f} kgCO₂e</span>
            <span class='badge badge-{r["impact"].lower()}'>{r['impact']}</span>
        </div>""" for r in st.session_state.history])
        st.markdown(f"""
        <div class='section-card'>
            <h3>🕑 Prediction History</h3>
            <div class='subtitle'>Last {len(st.session_state.history)} analyses</div>
            {rows}
        </div>""", unsafe_allow_html=True)

    # ── Nav buttons ───────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1,5,1])
    with c1:
        if st.button("← Previous", key="prev4"):
            st.session_state.step = 3; st.rerun()
    with c3:
        if st.button("🧪 Go to Testing →", key="goto5"):
            st.session_state.step = 5; st.rerun()

    c1b, c2b, c3b = st.columns([1,5,1])
    with c3b:
        if st.button("🔄 New Analysis", key="restart"):
            for k,v in [("step",1),("metal",None),("process",None),
                        ("quantity",1000.0),("result",None)]:
                st.session_state[k] = v
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# STEP 5 — TESTING
# ════════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 5:

    # ── Animation CSS ─────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes fadeSlideUp {
        from { opacity:0; transform:translateY(20px); }
        to   { opacity:1; transform:translateY(0); }
    }
    .test-anim { animation: fadeSlideUp 0.5s ease both; }
    .test-row-pass { background:#f0fdf4; border-left:4px solid #16a34a; }
    .test-row-fail { background:#fff7ed; border-left:4px solid #d97706; }

    .accuracy-bar-wrap {
        background:#e8ede8; border-radius:50px; height:10px;
        overflow:hidden; margin-top:6px;
    }
    .accuracy-bar-fill {
        height:100%; border-radius:50px;
        background:linear-gradient(90deg,#1a8a3c,#4ade80);
        transition: width 1s ease;
    }
    .test-card {
        background:white; border:1px solid #e8ede8; border-radius:12px;
        padding:20px; box-shadow:0 1px 4px rgba(0,0,0,0.04);
        margin-bottom:16px; animation: fadeSlideUp 0.5s ease both;
    }
    .pred-vs-actual {
        display:grid; grid-template-columns:1fr 1fr 1fr 1fr;
        gap:12px; margin-top:12px;
    }
    .pva-item {
        background:#f9fafb; border:1px solid #e8ede8;
        border-radius:10px; padding:14px; text-align:center;
    }
    .pva-label  { font-size:11px; color:#888; text-transform:uppercase;
                  letter-spacing:1px; margin-bottom:6px; }
    .pva-pred   { font-size:18px; font-weight:700; color:#1a8a3c; }
    .pva-actual { font-size:13px; color:#2563eb; margin-top:3px; font-weight:500; }
    .pva-err    { font-size:11px; color:#888; margin-top:3px; }
    .pva-acc    { font-size:12px; font-weight:600; margin-top:4px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='test-anim' style='margin-bottom:20px'>
        <h2 style='font-size:22px;font-weight:700;color:#1a2e1a;margin:0 0 4px'>
            🧪 Model Testing
        </h2>
        <p style='color:#888;font-size:13px;margin:0'>
            Test the trained AI model — enter any metal, process and quantity to compare
            predicted output vs actual dataset values
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load dataset for actual values ────────────────────────────────────────
    DATASET_PATH = os.path.join("dataset", "metal_dataset.csv")
    df_data = pd.read_csv(DATASET_PATH) if os.path.exists(DATASET_PATH) else None

    # ── Model accuracy metrics ────────────────────────────────────────────────
    if df_data is not None:
        from sklearn.metrics import mean_absolute_error, r2_score
        from sklearn.preprocessing import LabelEncoder

        df_test = df_data.copy()
        m_enc = payload["le_metal"].transform(df_test["Metal"])
        p_enc = payload["le_process"].transform(df_test["Process"])
        X_all = np.column_stack([m_enc, p_enc, df_test["Quantity(kg)"]])
        y_pred_all = payload["model"].predict(X_all)
        targets = payload["targets"]

        st.markdown("<div class='test-card'><h3 style='font-size:16px;font-weight:700;color:#1a2e1a;margin:0 0 16px'>📊 Overall Model Accuracy</h3>", unsafe_allow_html=True)
        acc_cols = st.columns(4)
        acc_labels = ["Energy(kwh)","Water(liters)","CO2(kg)","Waste(kg)"]
        acc_icons  = ["⚡","💧","🏭","🗑️"]
        for i, (col, icon, tgt) in enumerate(zip(acc_cols, acc_icons, acc_labels)):
            y_true = df_test[tgt].values
            y_pr   = y_pred_all[:, i]
            r2     = r2_score(y_true, y_pr)
            mae    = mean_absolute_error(y_true, y_pr)
            acc_pct = max(0, r2 * 100)
            bar_color = "#1a8a3c" if acc_pct >= 90 else ("#d97706" if acc_pct >= 75 else "#ef4444")
            with col:
                st.markdown(f"""
                <div style='background:#f9fafb;border:1px solid #e8ede8;border-radius:10px;padding:14px;text-align:center'>
                    <div style='font-size:20px;margin-bottom:4px'>{icon}</div>
                    <div style='font-size:11px;color:#888;text-transform:uppercase;
                         letter-spacing:1px;margin-bottom:8px'>{tgt.replace('(','<br>(')}</div>
                    <div style='font-size:22px;font-weight:700;color:{bar_color}'>{acc_pct:.1f}%</div>
                    <div class='accuracy-bar-wrap'>
                        <div class='accuracy-bar-fill' style='width:{acc_pct}%;background:{bar_color}'></div>
                    </div>
                    <div style='font-size:11px;color:#888;margin-top:6px'>MAE: {mae:,.2f}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── History-Based Process Comparison ─────────────────────────────────────
    # Find pairs: same metal + same quantity + different process in history
    history = st.session_state.get("history", [])
    compared_pairs = []
    seen = []
    for i, h1 in enumerate(history):
        for h2 in history[i+1:]:
            if (h1["metal"] == h2["metal"] and
                abs(h1["qty"] - h2["qty"]) < 50 and
                h1["process"] != h2["process"] and
                (h1["metal"], round(h1["qty"],-2)) not in seen):
                compared_pairs.append((h1, h2))
                seen.append((h1["metal"], round(h1["qty"],-2)))

    if compared_pairs:
        for h1, h2 in compared_pairs:
            if h1["process"] == "Recycling":
                h1, h2 = h2, h1
            metal_name = h1["metal"]
            qty_val    = h1["qty"]

            keys2   = ["Energy(kwh)","Water(liters)","CO2(kg)","Waste(kg)"]
            micons  = ["⚡","💧","🏭","🗑️"]
            mlabels = ["Energy (kWh)","Water (L)","CO₂ (kg)","Waste (kg)"]
            mvalues = ["energy","water","co2","waste"]

            act_m = act_r = None
            if df_data is not None:
                for proc, tag in [("Mining","m"),("Recycling","r")]:
                    sub = df_data[(df_data["Metal"]==metal_name)&(df_data["Process"]==proc)].copy()
                    if not sub.empty:
                        sub["d"] = abs(sub["Quantity(kg)"] - qty_val)
                        row = sub.loc[sub["d"].idxmin()]
                        if tag=="m": act_m = {k: row[k] for k in keys2}
                        else:        act_r  = {k: row[k] for k in keys2}

            winner    = "Mining" if h1["co2"] < h2["co2"] else "Recycling"
            loser     = "Recycling" if winner=="Mining" else "Mining"
            win_color = "#dc2626" if winner=="Mining" else "#16a34a"
            win_icon  = "⛏️" if winner=="Mining" else "♻️"
            co2_save  = abs(h1["co2"] - h2["co2"])
            co2_pct   = co2_save / max(h1["co2"], h2["co2"]) * 100

            # Build rows
            rows_html = ""
            for i, (ico, lbl, hk, dk) in enumerate(zip(micons, mlabels, mvalues, keys2)):
                vm = h1[hk]; vr = h2[hk]
                am = f"{act_m[dk]:,.2f}" if act_m else "&#8212;"
                ar = f"{act_r[dk]:,.2f}" if act_r else "&#8212;"
                cm = "#16a34a" if vm < vr else "#dc2626"
                cr = "#16a34a" if vr < vm else "#dc2626"
                bg = "#fafafa" if i%2==0 else "#ffffff"
                rows_html += (
                    f"<tr style='background:{bg};border-bottom:1px solid #f0f4f0'>"
                    f"<td style='padding:10px 14px;font-weight:600;color:#374151'>{ico} {lbl}</td>"
                    f"<td style='padding:10px 14px;text-align:right;font-weight:700;color:{cm}'>{vm:,.2f}</td>"
                    f"<td style='padding:10px 14px;text-align:right;color:#666'>{am}</td>"
                    f"<td style='padding:10px 14px;text-align:right;font-weight:700;color:{cr}'>{vr:,.2f}</td>"
                    f"<td style='padding:10px 14px;text-align:right;color:#666'>{ar}</td>"
                    f"</tr>"
                )

            html = (
                f"<div class='test-card' style='border:2px solid {win_color}33'>"
                f"<h3 style='font-size:15px;font-weight:700;color:#1a2e1a;margin:0 0 4px'>📊 History Comparison &mdash; {metal_name} at {qty_val:,.0f} kg</h3>"
                f"<p style='font-size:12px;color:#666;margin-bottom:14px'>From your prediction history &mdash; same metal, same quantity, both processes compared</p>"
                f"<div style='background:{win_color}18;border:1.5px solid {win_color}55;border-radius:10px;padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;gap:14px'>"
                f"<span style='font-size:28px'>{win_icon}</span>"
                f"<div>"
                f"<div style='font-size:11px;font-weight:700;color:{win_color};letter-spacing:1px;text-transform:uppercase;margin-bottom:3px'>&#10003; Recommended Process</div>"
                f"<div style='font-size:18px;font-weight:700;color:{win_color}'>{winner} is better for the environment</div>"
                f"<div style='font-size:12px;color:#374151;margin-top:3px'>Saves <b>{co2_save:,.2f} kgCO&#8322;e</b> ({co2_pct:.1f}% less emissions) vs {loser}</div>"
                f"</div></div>"
                f"<table style='width:100%;border-collapse:collapse;font-size:13px'>"
                f"<thead><tr style='background:#f0f7f0'>"
                f"<th style='padding:10px 14px;text-align:left;color:#1a4731;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>Metric</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#dc2626;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>&#9935; Mining (Pred)</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#888;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>Mining Actual</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#16a34a;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>&#9851; Recycling (Pred)</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#888;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>Recycling Actual</th>"
                f"</tr></thead>"
                f"<tbody>{rows_html}</tbody>"
                f"</table></div>"
            )
            st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='test-card' style='background:#fffbeb;border:1px solid #fcd34d'>
            <p style='font-size:13px;color:#92400e;margin:0'>
                💡 <b>No history comparison available yet.</b> Run analyses for the
                <b>same metal + same quantity</b> with <b>both Mining and Recycling</b>
                processes in Step 1–3, then come back here to see which process
                is better for the environment.
            </p>
        </div>""", unsafe_allow_html=True)

    # ── Manual Test Input ─────────────────────────────────────────────────────
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] label { color:#1a2e1a !important; font-weight:700 !important; font-size:14px !important; }
    div[data-baseweb="select"] > div { background:#f0f7f0 !important; border:1.5px solid #1a4731 !important; }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div { color:#1a2e1a !important; }
    div[data-baseweb="select"] * { color:#1a2e1a !important; }
    li[role="option"] { color:#1a2e1a !important; background:white !important; }
    li[role="option"]:hover { background:#f0f7f0 !important; }
    input[type="number"] { color:#1a2e1a !important; background:#f0f7f0 !important; border:1.5px solid #1a4731 !important; font-weight:700 !important; }
    </style>""", unsafe_allow_html=True)
    st.markdown("<div class='test-card'><h3 style='font-size:16px;font-weight:700;color:#1a2e1a;margin:0 0 16px'>🔬 Manual Test — Predict & Compare</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:13px;color:#666;margin-bottom:16px'>Enter values below — the model will predict and compare against the closest actual record in the dataset</p>", unsafe_allow_html=True)

    # Pre-fill from current session (metal/process/quantity selected in steps 1-3)
    metals_list    = list(METALS.keys())
    processes_list = list(PROCESSES.keys())
    default_metal   = metals_list.index(st.session_state.metal)   if st.session_state.metal   in metals_list    else 0
    default_process = processes_list.index(st.session_state.process) if st.session_state.process in processes_list else 0
    default_qty     = int(st.session_state.quantity) if st.session_state.quantity else 1000

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        test_metal = st.selectbox("🔩 Metal", metals_list, index=default_metal, key="test_metal")
    with tc2:
        test_process = st.selectbox("⚙️ Process", processes_list, index=default_process, key="test_process")
    with tc3:
        test_qty = st.number_input("⚖️ Quantity (kg)", min_value=100.0, max_value=10000.0,
                                    value=float(default_qty), step=100.0, key="test_qty")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🚀 Run Test", key="run_test"):
        # Predict
        pred = predict(test_metal, test_process, test_qty)

        # Find closest actual row from dataset
        actual_row = None
        actual_vals = None
        if df_data is not None:
            subset = df_data[
                (df_data["Metal"] == test_metal) &
                (df_data["Process"] == test_process)
            ]
            if not subset.empty:
                subset = subset.copy()
                subset["qty_diff"] = abs(subset["Quantity(kg)"] - test_qty)
                closest = subset.loc[subset["qty_diff"].idxmin()]
                actual_vals = {
                    "Energy(kwh)":    closest["Energy(kwh)"],
                    "Water(liters)":  closest["Water(liters)"],
                    "CO2(kg)":        closest["CO2(kg)"],
                    "Waste(kg)":      closest["Waste(kg)"],
                    "qty":            closest["Quantity(kg)"],
                }

        impact_label, impact_cls = get_impact(pred["CO2(kg)"])

        # ── Result banner ─────────────────────────────────────────────────────
        badge_colors = {
            "low":    ("#dcfce7","#16a34a","#bbf7d0","🟢"),
            "medium": ("#fef3c7","#d97706","#fcd34d","🟡"),
            "high":   ("#fee2e2","#dc2626","#fca5a5","🔴"),
        }
        bg,fg,border,icon = badge_colors[impact_cls]
        st.markdown(f"""
        <div class='test-anim' style='background:{bg};border:1px solid {border};border-radius:12px;
             padding:16px 22px;margin-bottom:20px;display:flex;align-items:center;gap:14px'>
            <span style='font-size:28px'>{icon}</span>
            <div>
                <div style='font-size:11px;color:{fg};font-weight:700;letter-spacing:1.5px;
                     text-transform:uppercase'>Test Result — Sustainability Rating</div>
                <div style='font-size:20px;font-weight:700;color:{fg};margin-top:2px'>
                    {impact_label} IMPACT</div>
                <div style='font-size:12px;color:#555;margin-top:2px'>
                    {test_metal} · {test_process} · {test_qty:,.0f} kg</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Predicted vs Actual ───────────────────────────────────────────────
        st.markdown("<div class='test-card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:15px;font-weight:700;color:#1a2e1a;margin:0 0 6px'>📋 Predicted vs Actual Values</h3>", unsafe_allow_html=True)

        if actual_vals:
            st.markdown(f"<p style='font-size:12px;color:#888;margin-bottom:16px'>Closest actual record found at <b>{actual_vals['qty']:,.0f} kg</b> in dataset</p>", unsafe_allow_html=True)

        icons2  = ["⚡","💧","🏭","🗑️"]
        labels2 = ["Energy (kWh)","Water (L)","CO₂ (kg)","Waste (kg)"]
        keys2   = ["Energy(kwh)","Water(liters)","CO2(kg)","Waste(kg)"]

        cols4 = st.columns(4)
        for col, ico, lbl, k in zip(cols4, icons2, labels2, keys2):
            p_val = pred[k]
            with col:
                if actual_vals:
                    a_val  = actual_vals[k]
                    err    = abs(p_val - a_val)
                    err_pct = (err / a_val * 100) if a_val != 0 else 0
                    acc_pct = max(0, 100 - err_pct)
                    acc_color = "#16a34a" if acc_pct >= 85 else ("#d97706" if acc_pct >= 65 else "#dc2626")
                    pf = "✅ PASS" if acc_pct >= 75 else "⚠️ CHECK"
                    pf_color = "#16a34a" if acc_pct >= 75 else "#d97706"
                    st.markdown(f"""
                    <div class='pva-item'>
                        <div class='pva-label'>{ico} {lbl}</div>
                        <div class='pva-pred'>{p_val:,.2f}</div>
                        <div style='font-size:10px;color:#888;margin-top:1px'>Predicted</div>
                        <div class='pva-actual'>{a_val:,.2f}</div>
                        <div style='font-size:10px;color:#888;margin-top:1px'>Actual</div>
                        <div class='pva-err'>Error: {err:,.2f} ({err_pct:.1f}%)</div>
                        <div class='pva-acc' style='color:{acc_color}'>{acc_pct:.1f}% acc</div>
                        <div style='font-size:11px;font-weight:700;color:{pf_color};margin-top:4px'>{pf}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='pva-item'>
                        <div class='pva-label'>{ico} {lbl}</div>
                        <div class='pva-pred'>{p_val:,.2f}</div>
                        <div style='font-size:11px;color:#888;margin-top:4px'>Predicted</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ── Error difference bar chart ─────────────────────────────────────────
        if actual_vals:
            pred_vals   = [pred[k] for k in keys2]
            actual_list = [actual_vals[k] for k in keys2]
            err_pcts    = [abs(pred_vals[i]-actual_list[i])/actual_list[i]*100
                           if actual_list[i]!=0 else 0 for i in range(4)]

            st.markdown("<div class='test-card'><h3 style='font-size:15px;font-weight:700;color:#1a2e1a;margin:0 0 16px'>📉 Predicted vs Actual — Chart</h3>", unsafe_allow_html=True)
            ch1, ch2 = st.columns(2)

            axis_style = dict(
                color="#1e293b", tickfont=dict(color="#1e293b", size=11),
                gridcolor="#e2e8f0", linecolor="#cbd5e1", showline=True,
            )

            with ch1:
                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Bar(name="Predicted", x=labels2, y=pred_vals,
                    marker_color="#1a8a3c", marker_line_width=0,
                    text=[f"{v:,.1f}" for v in pred_vals], textposition="outside",
                    textfont=dict(color="#1e293b", size=10)))
                fig_cmp.add_trace(go.Bar(name="Actual", x=labels2, y=actual_list,
                    marker_color="#2563eb", marker_line_width=0,
                    text=[f"{v:,.1f}" for v in actual_list], textposition="outside",
                    textfont=dict(color="#1e293b", size=10)))
                fig_cmp.update_layout(
                    barmode="group", paper_bgcolor="white", plot_bgcolor="#f8fafc",
                    font=dict(color="#1e293b", family="Inter", size=11),
                    xaxis=dict(**axis_style), yaxis=dict(**axis_style),
                    legend=dict(bgcolor="white", bordercolor="#e2e8f0",
                                font=dict(color="#1e293b")),
                    margin=dict(l=10,r=10,t=30,b=10), height=280,
                    title=dict(text="Predicted vs Actual", font=dict(color="#1e293b",size=13)),
                )
                st.plotly_chart(fig_cmp, use_container_width=True)

            with ch2:
                bar_colors = ["#16a34a" if e<15 else ("#d97706" if e<30 else "#ef4444") for e in err_pcts]
                fig_err = go.Figure(go.Bar(
                    x=labels2, y=err_pcts, marker_color=bar_colors, marker_line_width=0,
                    text=[f"{e:.1f}%" for e in err_pcts], textposition="outside",
                    textfont=dict(color="#1e293b", size=11),
                ))
                fig_err.add_hline(y=15, line_dash="dash", line_color="#d97706",
                                  annotation_text="15% threshold",
                                  annotation_font_color="#d97706")
                fig_err.update_layout(
                    paper_bgcolor="white", plot_bgcolor="#f8fafc",
                    font=dict(color="#1e293b", family="Inter", size=11),
                    xaxis=dict(**axis_style), yaxis=dict(**axis_style, title="Error %"),
                    margin=dict(l=10,r=10,t=30,b=10), height=280,
                    title=dict(text="Error % per Metric", font=dict(color="#1e293b",size=13)),
                    showlegend=False,
                )
                st.plotly_chart(fig_err, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Summary table ─────────────────────────────────────────────────────
        st.markdown(f"""
        <div class='test-card'>
            <h3 style='font-size:15px;font-weight:700;color:#1a2e1a;margin:0 0 14px'>📝 Test Summary</h3>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:13px'>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;color:#1a2e1a;font-weight:600'>Metal Tested</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;font-weight:700;color:#1a2e1a'>{test_metal}</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;color:#1a2e1a;font-weight:600'>Process</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;font-weight:700;color:#1a2e1a'>{test_process}</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;color:#1a2e1a;font-weight:600'>Quantity</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;font-weight:700;color:#1a2e1a'>{test_qty:,.0f} kg</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;color:#1a2e1a;font-weight:600'>Predicted CO₂</div>
                <div style='padding:8px 0;border-bottom:1px solid #f3f4f6;font-weight:600;color:#1a8a3c'>{pred['CO2(kg)']:,.4f} kgCO₂e</div>
                <div style='padding:8px 0;color:#1a2e1a;font-weight:600'>Sustainability Rating</div>
                <div style='padding:8px 0;font-weight:600'><span class='badge badge-{impact_cls}'>{impact_label}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Final Decision: compare with other process if in history ─────────
        hist = st.session_state.get("history", [])
        other_proc = "Recycling" if test_process == "Mining" else "Mining"
        match = next((h for h in hist
                      if h["metal"] == test_metal
                      and h["process"] == other_proc
                      and abs(h["qty"] - test_qty) < 50), None)

        if match:
            # current test pred vs matched history pred
            curr_co2  = pred["CO2(kg)"]
            other_co2 = match["co2"]
            winner    = test_process if curr_co2 < other_co2 else other_proc
            loser     = other_proc   if winner == test_process else test_process
            wc        = "#16a34a" if winner == "Recycling" else "#dc2626"
            wi        = "♻️" if winner == "Recycling" else "⛏️"
            saving    = abs(curr_co2 - other_co2)
            pct       = saving / max(curr_co2, other_co2) * 100

            # actual values for both from dataset
            keys_d  = ["Energy(kwh)","Water(liters)","CO2(kg)","Waste(kg)"]
            icons_d = ["⚡","💧","🏭","🗑️"]
            labs_d  = ["Energy (kWh)","Water (L)","CO&#8322; (kg)","Waste (kg)"]
            act_curr = act_other = None
            if df_data is not None:
                for proc, tag in [(test_process,"curr"),(other_proc,"other")]:
                    sub = df_data[(df_data["Metal"]==test_metal)&(df_data["Process"]==proc)].copy()
                    if not sub.empty:
                        sub["d"] = abs(sub["Quantity(kg)"] - test_qty)
                        row = sub.loc[sub["d"].idxmin()]
                        if tag=="curr":  act_curr  = {k: row[k] for k in keys_d}
                        else:            act_other = {k: row[k] for k in keys_d}

            # pred values for other process
            pred_other = predict(test_metal, other_proc, test_qty)

            # build rows
            rows = ""
            for i,(ico,lbl,k) in enumerate(zip(icons_d, labs_d, keys_d)):
                vc = pred[k]; vo = pred_other[k]
                ac = f"{act_curr[k]:,.2f}"  if act_curr  else "&#8212;"
                ao = f"{act_other[k]:,.2f}" if act_other else "&#8212;"
                cc = "#16a34a" if vc < vo else "#dc2626"
                co = "#16a34a" if vo < vc else "#dc2626"
                bg = "#fafafa" if i%2==0 else "#ffffff"
                rows += (
                    f"<tr style='background:{bg};border-bottom:1px solid #f0f4f0'>"
                    f"<td style='padding:10px 14px;font-weight:600;color:#374151'>{ico} {lbl}</td>"
                    f"<td style='padding:10px 14px;text-align:right;font-weight:700;color:{cc}'>{vc:,.2f}</td>"
                    f"<td style='padding:10px 14px;text-align:right;color:#555'>{ac}</td>"
                    f"<td style='padding:10px 14px;text-align:right;font-weight:700;color:{co}'>{vo:,.2f}</td>"
                    f"<td style='padding:10px 14px;text-align:right;color:#555'>{ao}</td>"
                    f"</tr>"
                )

            fd_html = (
                f"<div class='test-card' style='border:2px solid {wc}44;margin-top:16px'>"
                f"<h3 style='font-size:15px;font-weight:700;color:#1a2e1a;margin:0 0 4px'>&#9878; Final Decision &mdash; {test_metal} at {test_qty:,.0f} kg</h3>"
                f"<p style='font-size:12px;color:#666;margin-bottom:14px'>Both processes now tested &mdash; here is the environmental verdict</p>"
                f"<div style='background:{wc}18;border:2px solid {wc}55;border-radius:12px;padding:16px 20px;margin-bottom:16px;display:flex;align-items:center;gap:16px'>"
                f"<span style='font-size:36px'>{wi}</span>"
                f"<div>"
                f"<div style='font-size:11px;font-weight:700;color:{wc};letter-spacing:1.5px;text-transform:uppercase;margin-bottom:4px'>&#127381; Best Process for the Environment</div>"
                f"<div style='font-size:22px;font-weight:800;color:{wc}'>{winner}</div>"
                f"<div style='font-size:13px;color:#374151;margin-top:4px'>Produces <b>{saving:,.2f} kgCO&#8322;e less</b> ({pct:.1f}% lower emissions) than {loser}</div>"
                f"</div></div>"
                f"<table style='width:100%;border-collapse:collapse;font-size:13px'>"
                f"<thead><tr style='background:#f0f7f0'>"
                f"<th style='padding:10px 14px;text-align:left;color:#1a4731;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>Metric</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#374151;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>{test_process} Pred</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#888;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>{test_process} Actual</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#374151;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>{other_proc} Pred</th>"
                f"<th style='padding:10px 14px;text-align:right;color:#888;font-size:11px;text-transform:uppercase;border-bottom:2px solid #c6dfc8'>{other_proc} Actual</th>"
                f"</tr></thead>"
                f"<tbody>{rows}</tbody>"
                f"</table></div>"
            )
            st.markdown(fd_html, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,5,1])
    with c1:
        if st.button("← Back to Results", key="prev5"):
            st.session_state.step = 4; st.rerun()
    with c3:
        if st.button("🔄 New Analysis", key="restart5"):
            for k,v in [("step",1),("metal",None),("process",None),
                        ("quantity",1000.0),("result",None)]:
                st.session_state[k] = v
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
