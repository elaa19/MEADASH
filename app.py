import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import pytz # Standard in Streamlit environments

# --- 1. CONFIG & SETTINGS ---
st.set_page_config(page_title="MEDINA COMMAND CENTER", layout="wide", initial_sidebar_state="collapsed")

# SET TIMEZONE TO TUNISIA
local_tz = pytz.timezone('Africa/Tunis')

# Define target times in local timezone
START_TIME = local_tz.localize(datetime(2026, 4, 3, 14,45, 0, 0))
END_TIME = local_tz.localize(datetime(2026, 4, 3, 17, 0, 0))

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSecPqsX3fiOFwv9YnIU2-3EGTJeZx5wMxjoEZ2UYk-JJ8iRjgc-hXl5MRv3U5UWKCtzBIlhtqJUKsG/pub?gid=0&single=true&output=csv"

LOGO_URL = "logo.png" 
FALLBACK_LOGO = "https://upload.wikimedia.org/wikipedia/commons/b/bd/AIESEC_Logo.png"

MOTIVATION = [
    "WE GOT THIS.", "MEDINA GOT THIS.", "APRIL IS OURS.", 
    "MEDINA IS LOUDER.", "MEDINA BACKS MEDINA.", "WATCH MEDINA WORK.",
    "WE DON'T MISS.", "MEDINA MAKES NOISE."
]

if 'last_count' not in st.session_state:
    st.session_state.last_count = 0

# --- 2. CSS STYLING ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Montserrat:wght@400;700&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, #001f3f 0%, #000b1a 100%);
        color: #ffffff;
    }}

    .header-container {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 50px;
        padding: 20px 0;
    }}

    .header-title {{
        color: #ffffff;
        text-shadow: 0 0 20px #ffffff;
        font-size: 5rem;
        line-height: 0.9;
        font-family: 'Orbitron', sans-serif;
        margin: 0;
        white-space: nowrap;
    }}

    .timer-box {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        border-left: 4px solid rgba(255,255,255,0.3);
        padding-left: 50px;
    }}

    .header-timer {{
        font-family: 'Orbitron', sans-serif;
        font-size: 7rem !important; 
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }}

    .timer-label {{
        color: #ffffff;
        font-weight: bold;
        letter-spacing: 4px;
        font-size: 1.2rem;
        margin-bottom: 5px;
        text-transform: uppercase;
        opacity: 0.8;
    }}

    .total-card, .dept-card {{
        background-color: #ffffff !important;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
        border: 4px solid #ffffff;
    }}
    
    .total-card h3, .dept-card h2 {{ 
        color: #001f3f !important; 
        font-family: 'Orbitron', sans-serif; 
        font-weight: 700; 
    }}

    .num-contacted {{ color: #001f3f !important; font-family: 'Orbitron'; font-size: 6rem; line-height: 1; font-weight: 700; }}
    .num-accepted {{ color: #007bff !important; font-family: 'Orbitron'; font-size: 6rem; line-height: 1; font-weight: 700; }}
    .num-approved {{ color: #10b981 !important; font-family: 'Orbitron'; font-size: 6rem; line-height: 1; font-weight: 700; }}

    .dept-card h2 {{ font-size: 2.5rem; margin-bottom: 10px; }}
    .dept-num {{ font-size: 3.5rem !important; }}
    .stat-label {{ color: #4b5563 !important; font-weight: 700; font-size: 1.1rem; text-transform: uppercase; font-family: 'Montserrat'; }}
    .dept-card hr {{ border: 1px solid #eee; margin: 15px 0; }}

    .motivation-text {{
        font-family: 'Montserrat', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        color: #007bff;
        text-align: center;
        text-transform: uppercase;
        animation: pulseText 3s infinite;
    }}

    @keyframes pulseText {{
        0% {{ opacity: 0.2; transform: scale(0.95); }}
        50% {{ opacity: 1; transform: scale(1); }}
        100% {{ opacity: 0.2; transform: scale(0.95); }}
    }}

    .celebration-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #001f3f;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ALIGNED HEADER (TIMEZONE FIXED) ---
now = datetime.now(local_tz)

if now < START_TIME:
    diff = START_TIME - now
    label, color = "STARTING IN", "#007bff"
elif START_TIME <= now <= END_TIME:
    diff = END_TIME - now
    label, color = "TIME REMAINING", "#FF4B4B"
else:
    label, color, diff = "MISSION COMPLETE", "#28a745", None

if diff:
    ts = int(diff.total_seconds())
    h, rem = divmod(ts, 3600)
    m, s = divmod(rem, 60)
    time_str = f"{h:02d}:{m:02d}:{s:02d}"
else:
    time_str = "00:00:00"

col_img, col_text = st.columns([1, 6])

with col_img:
    try:
        st.image(LOGO_URL, use_column_width=True)
    except:
        st.image(FALLBACK_LOGO, use_column_width=True)

with col_text:
    st.markdown(f"""
        <div class="header-container">
            <div class="header-title">MEDINA<br>WAR ROOM</div>
            <div class="timer-box">
                <div class="timer-label" style="color:{color};">{label}</div>
                <div class="header-timer" style="color:{color};">{time_str}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
try:
    raw_df = pd.read_csv(f"{CSV_URL}&t={time.time()}")
    raw_df.columns = [str(c).strip().lower() for c in raw_df.columns]
    for col in raw_df.columns:
        raw_df[col] = raw_df[col].astype(str).str.strip()

    COL_DEPT = 'department'
    COL_STATUS = 'status'
    COL_NAME = 'ep name'

    # CELEBRATION
    if len(raw_df) > st.session_state.last_count and st.session_state.last_count != 0:
        latest = raw_df.iloc[-1]
        if latest[COL_STATUS].lower() == "approved":
            st.markdown(f"""
                <div class="celebration-overlay">
                    <h1 style="font-size:10rem; color:#FFD700; font-family:Orbitron;">NEW APPROVAL!</h1>
                    <h2 style="font-size:7rem; color:white; font-family:Montserrat;">{latest[COL_DEPT].upper()}</h2>
                    <h3 style="font-size:5rem; color:#007bff; font-family:Montserrat;">{latest[COL_NAME].upper()}</h3>
                    <h1 style="font-size:15rem;">🏆🥇🏆</h1>
                </div>
            """, unsafe_allow_html=True)
            st.balloons()
            time.sleep(10)
            st.rerun()

    st.session_state.last_count = len(raw_df)

    # GLOBAL TOTALS
    total_con = len(raw_df)
    total_acc = len(raw_df[raw_df[COL_STATUS].str.lower() == "accepted"])
    total_app = len(raw_df[raw_df[COL_STATUS].str.lower() == "approved"])

    st.write("<br>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="total-card"><h3>TOTAL CONTACTED</h3><p class="num-contacted">{total_con}</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="total-card"><h3>TOTAL ACCEPTED</h3><p class="num-accepted">{total_acc}</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="total-card"><h3>TOTAL APPROVALS</h3><p class="num-approved">{total_app}</p></div>', unsafe_allow_html=True)

    # DEPARTMENT STANDINGS
    st.write("<br>", unsafe_allow_html=True)
    d_cols = st.columns(4)
    for i, d in enumerate(['OGT', 'OGV', 'IGT', 'IGV']):
        with d_cols[i]:
            d_df = raw_df[raw_df[COL_DEPT].str.upper() == d]
            apps = len(d_df[d_df[COL_STATUS].str.lower() == 'approved'])
            accs = len(d_df[d_df[COL_STATUS].str.lower() == 'accepted'])
            cons = len(d_df)
            
            st.markdown(f"""
                <div class="dept-card">
                    <h2>{d}</h2>
                    <hr>
                    <p class="stat-label">Approvals</p>
                    <p class="num-approved dept-num">{apps}</p>
                    <hr>
                    <p class="stat-label">Accepted</p>
                    <p class="num-accepted dept-num">{accs}</p>
                    <hr>
                    <p class="stat-label">Contacted</p>
                    <p class="num-contacted dept-num">{cons}</p>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info(f"🛰️ RE-SYNCING COMMAND CENTER...")

# --- 5. THE MEDINA TICKER ---
st.write("<br><br>", unsafe_allow_html=True)
quote = random.choice(MOTIVATION)
st.markdown(f'<div class="motivation-text">{quote}</div>', unsafe_allow_html=True)

time.sleep(1)
st.rerun()