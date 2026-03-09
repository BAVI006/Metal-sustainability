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
        if st.button("🔄 New Analysis", key="restart"):
            for k,v in [("step",1),("metal",None),("process",None),
                        ("quantity",1000.0),("result",None)]:
                st.session_state[k] = v
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)