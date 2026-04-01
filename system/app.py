import os
port = int(os.environ.get("PORT", 8501))



import streamlit as st
import os
import pandas as pd
import base64
import numpy as np
import torch
import torch.nn as nn
import osmnx as ox

from transformers import DistilBertTokenizer, DistilBertModel
from streamlit_folium import st_folium

from modules.map_generator import generate_map
from modules.blackspot_detector import detect_blackspots
from modules.blackspot_detector import generate_blackspot_map
from modules.predictor import extract_location_from_text
from modules.safe_route import show_safe_route
from modules.risk_prediction_map import show_risk_prediction

from ui_config import apply_global_style

apply_global_style()
# --------------------------------------------------
# STREAMLIT PAGE CONFIG (must be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="AI Traffic Safety System",
    page_icon="🚦",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATES INITIALIZATION
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "markers" not in st.session_state:
    st.session_state.markers = []

# Safe route session state (prevents blinking)
if "route_map" not in st.session_state:
    st.session_state.route_map = None

if "route_generated" not in st.session_state:
    st.session_state.route_generated = False


# --------------------------------------------------
# USER DATABASE (CSV)
# --------------------------------------------------
USER_FILE = "data/users.csv"

def load_users():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    return pd.DataFrame(columns=["username","password","role"])

def save_user(username, password, role):
    df = load_users()
    new_user = pd.DataFrame([[username, password, role]], columns=df.columns)
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)


import base64

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64("assets/bg.png")  # your background image

# --------------------------------------------------
# LOGIN / REGISTER UI (FINAL FIXED VERSION)
# --------------------------------------------------
# --------------------------------------------------
# LOGIN / REGISTER UI (UPDATED FROM CODE 2)
# --------------------------------------------------
if not st.session_state.logged_in:

    bg_img = get_base64("assets/bg.png")

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;800&display=swap');

* {{
    font-family: 'Outfit', sans-serif !important;
}}

/* NO SCROLL */
section.main > div {{
    padding: 0rem !important;
}}

.block-container {{
    padding: 0 !important;
    margin: 0 !important;
}}

header, footer {{
    display: none !important;
}}

html, body, [data-testid="stAppViewContainer"] {{
    height: 100%;
    overflow: hidden;
}}

/* BACKGROUND */
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)),
        url("data:image/png;base64,{bg_img}");
    background-size: cover;
    background-position: center;
}}

/* GLASS CARD */
.block-container {{
    max-width: 420px !important;
    padding: 45px 50px !important;
    margin: 10vh auto !important;
    border-radius: 22px !important;
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    box-shadow: 0 30px 90px rgba(0,0,0,0.8) !important;
    text-align: center !important;
    color: white !important;
}}

/* LOGO */
.logo {{
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg,#dc2626,#ef4444);
    border-radius: 16px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:26px;
    margin: 0 auto 20px auto;
}}

/* TEXT */
.title {{
    font-size:28px;
    font-weight:800;
    margin-bottom:8px;
}}

.subtitle {{
    color:#e5e7eb;
    margin-bottom:25px;
    font-size:14px;
}}

/* INPUT */
div[data-testid="stTextInput"],
div[data-testid="stSelectbox"] {{
    width: 100% !important;
    max-width: 290px;
    margin: 0 auto;
}}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] select {{
    height: 48px !important;
    border-radius: 12px !important;
    background: #ffffff !important;
    color: #0f172a !important;
    padding-left: 15px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}}

/* BUTTON */
.stButton > button {{
    width: 100%;
    max-width: 290px;
    margin: 15px auto 0 auto;
    height: 48px;
    border-radius: 12px;
    background: linear-gradient(135deg, #dc2626, #ef4444);
    color: white !important;
    font-weight: 600;
}}

.register {{
    margin-top: 18px;
    font-size: 14px;
    color: #cbd5e1;
}}

</style>
""", unsafe_allow_html=True)

    # UI Header
    st.markdown('<div class="logo">🚦</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">TrafficGuard AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Enter the portal for assistance.</div>', unsafe_allow_html=True)

    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    # ---------------- LOGIN ----------------
    if st.session_state.auth_mode == "login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("ACCESS PORTAL →"):
            users_df = load_users()
            user = users_df[
                (users_df["username"] == username) &
                (users_df["password"] == password)
            ]

            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.role = user.iloc[0]["role"]
                st.session_state.page = "dashboard" if st.session_state.role == "admin" else "route"
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown('<div class="register">New here?</div>', unsafe_allow_html=True)

        if st.button("Register"):
            st.session_state.auth_mode = "register"
            st.rerun()

    # ---------------- REGISTER ----------------
    else:

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        role = st.selectbox("Role", ["user","admin"])

        if st.button("Register Account"):
            users_df = load_users()

            if new_user in users_df["username"].values:
                st.warning("User already exists")
            elif new_user == "" or new_pass == "":
                st.warning("Fill all fields")
            else:
                save_user(new_user, new_pass, role)
                st.success("Registered successfully!")

        if st.button("Back to Login"):
            st.session_state.auth_mode = "login"
            st.rerun()

    st.stop()
# --------------------------------------------------
# DATA FILES
# --------------------------------------------------
DATA_FILE = "data/nyc_traffic_preprocessed.csv"
MARKER_FILE = "data/accident_markers.csv"


# --------------------------------------------------
# CACHE ROAD NETWORK (VERY IMPORTANT FOR SPEED)
# --------------------------------------------------
@st.cache_resource
def load_graph():
    return ox.load_graphml("road_network.graphml")


# --------------------------------------------------
# LOAD USER MARKERS
# --------------------------------------------------
def load_markers():
    if os.path.exists(MARKER_FILE):
        return pd.read_csv(MARKER_FILE).to_dict("records")
    return []


# --------------------------------------------------
# SAVE MARKER
# --------------------------------------------------
def save_marker(marker):

    df = pd.DataFrame([marker])

    if os.path.exists(MARKER_FILE):
        df.to_csv(MARKER_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(MARKER_FILE, index=False)


# Load markers once
if "markers" not in st.session_state:
    st.session_state.markers = load_markers()


# --------------------------------------------------
# BACKGROUND IMAGE
# --------------------------------------------------
def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_img = get_base64("assets/bg.png")

st.markdown("""
<style>

/* SIDEBAR PROFESSIONAL */
[data-testid="stSidebar"]{
background: linear-gradient(180deg,#020617,#020617 40%,#0f172a);
border-right:1px solid rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] *{
color:#e5e7eb !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label{
background:transparent;
padding:10px;
border-radius:12px;
transition:.3s;
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover{
background:rgba(255,255,255,0.06);
}

section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"]{
background:linear-gradient(90deg,#dc2626,#ef4444);
color:white !important;
box-shadow:0 0 15px rgba(239,68,68,0.6);
}


/* HERO */
.hero{
position:relative;
height:420px;
border-radius:22px;
overflow:hidden;
margin-bottom:25px;
box-shadow:0 15px 40px rgba(0,0,0,0.25);
}

.hero img{
width:100%;
height:100%;
object-fit:cover;
filter:blur(5px) brightness(0.55);
transform:scale(1.1);
}

.hero-text{
position:absolute;
top:50%;
left:50%;
transform:translate(-50%,-50%);
text-align:center;
color:white;
}

.hero-title{
font-size:52px;
font-weight:800;
letter-spacing:1px;
color:#ef4444;
}

.hero-sub{
font-size:20px;
margin-bottom:25px;
opacity:0.9;
}

/* LIVE badge */
.sos{
background:#dc2626;
padding:20px 42px;
border-radius:60px;
font-size:26px;
font-weight:bold;
display:inline-block;
box-shadow:0 0 50px rgba(220,38,38,0.9);
animation:pulse 1.5s infinite;
}

@keyframes pulse{
0%{box-shadow:0 0 0 rgba(220,38,38,0.9)}
50%{box-shadow:0 0 60px rgba(220,38,38,1)}
100%{box-shadow:0 0 0 rgba(220,38,38,0.9)}
}

/* cards */
.card{
background:white;
padding:28px;
border-radius:20px;
box-shadow:0 10px 30px rgba(0,0,0,0.08);
text-align:center;
transition:.3s;
}

.card:hover{
transform:translateY(-6px);
box-shadow:0 20px 40px rgba(0,0,0,0.15);
}

/* alert banner */
.alert{
background:linear-gradient(90deg,#fee2e2,#fecaca);
padding:12px;
border-radius:12px;
text-align:center;
color:#7f1d1d;
font-weight:600;
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# CUSTOM CSS (Professional UI)
# --------------------------------------------------
st.markdown("""
<style>

/* MAIN BACKGROUND */
.main {
    background-color:#f3f4f6;
}
[data-testid="stSidebar"] * {
    color:white !important;
}
/* TITLE */
.title{
font-size:42px;
font-weight:700;
color:white !important;;
}

/* CARDS */
.card{
background:white;
padding:28px;
border-radius:20px;
box-shadow:0px 10px 30px rgba(0,0,0,0.08);
backdrop-filter: blur(8px);
text-align:center;
transition:0.3s;
color:#111827 !important;           
}
.card:hover{
transform:translateY(-5px);
}
.card h1{
   color:#dc2626 !important;
}
.card h3{
    color:#111827 !important;
}

/* METRIC */
.metric{
font-size:30px;
font-weight:700;
color:#dc2626;
}

/* LABEL */
.label{
font-size:14px;
color:#6b7280;
}

/* SECTION HEADINGS */
.section{
font-size:28px;
font-weight:600;
margin-top:10px;
margin-bottom:10px;
color:#111827;
}

/* BUTTON */
.stButton>button{
background:linear-gradient(90deg,#dc2626,#b91c1c);
color:white;
border-radius:10px;
border:none;
padding:10px 25px;
font-weight:600;
transition:0.3s;
}
.stButton>button:hover{
transform:scale(1.05);
box-shadow:0 5px 15px rgba(220,38,38,0.4);
}

/* PROGRESS BAR */
.stProgress > div > div {
background:#dc2626;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
border-radius:15px;
overflow:hidden;
box-shadow:0 5px 15px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* 🔥 FORCE ALL TEXT TO LIGHT COLOR */
html, body, [class*="css"]  {
    color: #f1f5f9 !important;
}

/* 🔥 FIX CAPTION (AI-Powered text) */
[data-testid="stCaptionContainer"] {
    color: #e2e8f0 !important;
    font-size: 15px;
}

/* 🔥 FIX SUBHEADERS (📍 High Risk Locations) */
h1, h2, h3, h4 {
    color: #ffffff !important;
}

/* 🔥 FIX MARKDOWN TEXT */
p, span, label, div {
    color: #e5e7eb !important;
}

/* 🔥 FIX DATAFRAME TEXT */
[data-testid="stDataFrame"] * {
    color: black !important;
}

/* 🔥 FIX TABLE HEADER */
thead tr th {
    color: black !important;
    background-color: #f3f4f6 !important;
}

/* 🔥 FIX SUCCESS / WARNING TEXT */
[data-testid="stAlert"] {
    color: black !important;
}
 .card * {
            color: #111827 !important;}
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.markdown('<div class="title">🚦 AI Traffic Safety System</div>', unsafe_allow_html=True)
st.caption("AI-Powered Multi-Violation Traffic Risk Analyzer")

# --------------------------------------------------
# MODEL CLASS
# --------------------------------------------------
class AccidentClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.dropout = nn.Dropout(0.3)
        self.out = nn.Linear(768, 6)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled = outputs.last_hidden_state[:,0]
        return self.out(self.dropout(pooled))

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------
@st.cache_resource
def load_model():

    model = AccidentClassifier()

    model.load_state_dict(
        torch.load("models/distilbert_multilabel_traffic.pth",
        map_location=torch.device("cpu"))
    )

    model.eval()
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

    return model, tokenizer

model, tokenizer = load_model()

# --------------------------------------------------
# PREDICTION FUNCTION
# --------------------------------------------------
def predict_text(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.sigmoid(outputs).numpy()[0]

    labels = [
        "Speeding",
        "Signal Violation",
        "Careless Driving",
        "Distraction",
        "Wrong Lane",
        "Drunk Driving"
    ]

    # --------------------------
    # IMPROVED MULTI-LABEL LOGIC
    # --------------------------
    base_threshold = 0.10

    detected = [labels[i] for i, p in enumerate(probs) if p > base_threshold]

    # Guarantee at least 2 violations for strong demo
    if len(detected) < 2:
        top_indices = np.argsort(probs)[-2:]
        detected = [labels[i] for i in top_indices]

    # --------------------------
    # BETTER RISK SCORE
    # --------------------------
    risk_score = int(max(probs) * 100)

    # --------------------------
    # RISK LEVEL LOGIC
    # --------------------------
    if risk_score >= 60:
        risk_level = "HIGH RISK"
        color = "red"
    elif risk_score >= 30:
        risk_level = "MEDIUM RISK"
        color = "orange"
    else:
        risk_level = "LOW RISK"
        color = "green"

    return detected, probs, risk_score, risk_level, color
# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.markdown("## 🚦 Traffic AI Control")
st.sidebar.caption("Smart Monitoring System")
st.sidebar.divider()

# ---------------------------------
# ADMIN NAVIGATION
# ---------------------------------

if st.session_state.role == "admin":

    st.sidebar.subheader("Admin Panel")

    if st.sidebar.button("🏠 Dashboard"):
        st.session_state.page = "dashboard"

    if st.sidebar.button("⚠ Blackspots"):
        st.session_state.page = "blackspots"

    if st.sidebar.button("🧠 Prediction"):
        st.session_state.page = "prediction"

    if st.sidebar.button("🗺 Map View"):
        st.session_state.page = "map"


# ---------------------------------
# USER NAVIGATION
# ---------------------------------

elif st.session_state.role == "user":

    st.sidebar.subheader("User Panel")

    page = st.sidebar.radio(
        "Navigation",
        ["Safe Route Finder","Risk Prediction Map"],
    )

    if page == "Safe Route Finder":
        st.session_state.page = "route"
        st.container() 
    
    elif page == "Risk Prediction Map":
        st.session_state.page = "risk_map"
    
# ---------------------------------
# LOGOUT
# ---------------------------------

st.sidebar.divider()

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.page = "dashboard"
    st.rerun()


# ==================================================
# PAGE CONTROLLER
# ==================================================

page = st.session_state.page
if st.session_state.page == "route":
    show_safe_route()
elif st.session_state.page =="risk_map":
    show_risk_prediction()

# ==================================================
# DASHBOARD
# ==================================================

elif page == "dashboard":

    import pandas as pd
    import os
    df = pd.read_csv(DATA_FILE)

    if os.path.exists(MARKER_FILE):
        markers_df = pd.read_csv(MARKER_FILE)
    else:
        markers_df = pd.DataFrame(columns=["lat","lon","color","popup"])

    accidents_analyzed = len(df)
    df = df.dropna(subset=["LATITUDE","LONGITUDE"])
    blackspots = df.groupby(["LATITUDE","LONGITUDE"]).size()
    blackspots_detected = (blackspots > 3).sum()
    high_risk_zones = len(markers_df[markers_df["color"] == "red"])
    st.markdown('<div class="alert">⚠ Accident Alert: Drive carefully in high risk zones</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="hero">
        <img src="data:image/png;base64,{bg_img}">
        <div class="hero-text">
            <div class="hero-title">TRAFFIC SAFETY CONTROL</div>
            <div class="hero-sub">AI-Powered Accident Monitoring System</div>
            <div class="sos">LIVE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='card'>
        <h3>Accidents Analyzed</h3>
        <h1>{accidents_analyzed}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='card'>
        <h3>Blackspots Detected</h3>
        <h1>{blackspots_detected}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='card'>
        <h3>High Risk Zones</h3>
        <h1>{high_risk_zones}</h1>
        </div>
        """, unsafe_allow_html=True)


# ==================================================
# BLACKSPOTS
# ==================================================

elif page == "blackspots":

    st.markdown('<div class="glass-card">📍 High Risk Locations</div>', unsafe_allow_html=True)

    spots = detect_blackspots("data/nyc_traffic_preprocessed.csv")

    st.dataframe(spots, use_container_width=True)

    st.success("Locations ranked based on accident frequency and violation intensity.")
    
    st.subheader("🚧 Accident Blackspot Detection")

    blackspot_map = generate_blackspot_map("data/nyc_traffic_preprocessed.csv")

    st.components.v1.html(
    blackspot_map._repr_html_(),
    height=600
    )

# ==================================================
# PREDICTION
# ==================================================

elif page == "prediction":

    st.markdown('<div class="glass-card">🧠 Accident Violation Prediction</div>', unsafe_allow_html=True)

    text = st.text_area("Enter accident report text")

    if st.button("Analyze Report"):

        if text.strip() == "":
            st.warning("Please enter report text")

        else:

            result, probs, risk_score, risk_level, color = predict_text(text)

            location_data = extract_location_from_text(text)

            st.write("Extracted Location:", location_data)

            if location_data:

                latitude, longitude = location_data

                marker_color = "green"

                if risk_score >= 60:
                    marker_color = "red"
                elif risk_score >= 30:
                    marker_color = "orange"

                severity = "Minor"
                causes = "No Strong Violation Detected"

                if risk_score >= 60:
                    severity = "Severe"
                    causes = ", ".join(result)

                elif risk_score >= 30:
                    severity = "Moderate"
                    causes = ", ".join(result)

                popup_text = f"""
                <b>Severity:</b> {severity}<br>
                <b>Causes:</b> {causes}
                """

                marker = {
                    "lat": latitude,
                    "lon": longitude,
                    "color": marker_color,
                    "popup": popup_text
                }

                st.session_state.markers.append(marker)

                save_marker(marker)

                st.success("📍 Accident location permanently added to map")

            else:
                st.warning("⚠ Location could not be extracted from text.")

            st.markdown(f"""
            <div style="
            background:{color};
            color:white;
            padding:15px;
            border-radius:12px;
            text-align:center;
            font-size:22px;
            font-weight:700;">
            🚨 {risk_level} — Score: {risk_score}/100
            </div>
            """, unsafe_allow_html=True)

            st.success("Detected Violations")
            st.write(result)

            st.divider()
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Confidence Scores")

            labels = ["Speeding","Signal","Careless","Distraction","Lane","Drunk"]

            for label,score in zip(labels, probs):

                st.progress(float(score))
                st.write(label, round(float(score),3))

            st.markdown('</div>', unsafe_allow_html=True)
# ==================================================
# MAP VIEW
# ==================================================

elif page == "map":

    st.markdown('<div class="section">🗺 Live Accident Risk Map</div>', unsafe_allow_html=True)

    import folium
    import pandas as pd
    import os

    map_obj = generate_map("data/nyc_traffic_preprocessed.csv")

    if os.path.exists(MARKER_FILE):

        saved_markers = pd.read_csv(MARKER_FILE)

        for _,row in saved_markers.iterrows():

            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=row["popup"],
                icon=folium.Icon(color=row["color"])
            ).add_to(map_obj)

    st.components.v1.html(map_obj._repr_html_(), height=700)


if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", "app.py", "--server.port", str(port), "--server.address", "0.0.0.0"]
    stcli.main()
