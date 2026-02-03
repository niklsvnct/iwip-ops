import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# --- 1. KONFIGURASI HALAMAN (WIDE & JUDUL) ---
st.set_page_config(page_title="Airport Ops Command", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (BOOTSTRAP STYLE LOOK-ALIKE) ---
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* GLOBAL FONT & COLOR */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa; /* Abu-abu sangat muda (Background Website) */
            color: #212529;
        }
        
        /* HILANGKAN ELEMENT BAWAAN STREAMLIT */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 95% !important;
        }

        /* CARD STYLE (Kotak Putih) */
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            border: 1px solid #dee2e6;
            margin-bottom: 15px;
        }

        /* HEADER STYLE */
        h1, h2, h3 {
            font-weight: 700 !important;
            color: #0d6efd; /* Bootstrap Primary Blue */
        }
        
        /* METRIC CARDS (Kotak Angka) */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            text-align: center;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #6c757d;
            font-weight: 600;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #212529;
        }

        /* TABS STYLE (Navigasi) */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            padding-bottom: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            background-color: white;
            border: 1px solid #dee2e6;
            color: #495057;
            padding: 0 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0d6efd !important; /* Biru Aktif */
            color: white !important;
            border-color: #0d6efd !important;
        }

        /* BUTTONS (Mirip Bootstrap) */
        div.stButton > button {
            border-radius: 50px; /* Pill Shape */
            font-weight: 600;
            border: none;
            padding: 0.5rem 1.5rem;
            transition: all 0.3s;
        }
        /* Tombol Primary (Simpan) */
        div.stButton > button[kind="primary"] {
            background-color: #0d6efd;
            color: white;
            box-shadow: 0 4px 6px rgba(13, 110, 253, 0.2);
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #0b5ed7;
            box-shadow: 0 6px 8px rgba(13, 110, 253, 0.3);
        }
        /* Tombol Secondary (Logout) */
        div.stButton > button[kind="secondary"] {
            background-color: #f8f9fa;
            color: #dc3545; /* Merah untuk Logout */
            border: 1px solid #dee2e6;
        }
        div.stButton > button[kind="secondary"]:hover {
            background-color: #dc3545;
            color: white;
        }

        /* TOAST NOTIFICATION */
        .stToast {
            background-color: #198754 !important; /* Success Green */
            color: white !important;
            border-radius: 8px;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. KONEKSI DATA ---
# !!! PASTE URL GOOGLE APPS SCRIPT KAMU DI SINI !!!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyaCGCloW-SCD_XmirHWr0wMgUinOJ-e1Vqrmi81OREiSh9yoV-p7GDVXuEzjZ6JajfUg/exec"

@st.cache_data(ttl=10, show_spinner=False)
def load_data(action):
    try:
        response = requests.get(f"{WEB_APP_URL}?action={action}")
        data = response.json()
        df = pd.DataFrame(data)
        
        # ANTI-CRASH SYSTEM
        if action == "readDirectives":
            required_cols = ["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            df = df[required_cols] # Urutkan kolom
            
        elif action == "readUnitOps":
            required_cols = ["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"]
            for col in required_cols:
                if col not in df.columns:
                    df[col] = ""
            df = df[required_cols]
            
        return df
    except:
        return pd.DataFrame() # Return kosong jika error

def save_data(df, sheet_name):
    try:
        rows = df.values.tolist()
        payload = {"sheetName": sheet_name, "rows": rows}
        requests.post(WEB_APP_URL, json=payload)
        st.toast("Data Saved Successfully!", icon="✅")
        st.cache_data.clear()
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to save: {e}")

# --- 4. LOGIC LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    # Tampilan Login Center yang Bersih
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #212529;'>✈️ Airport Ops Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d;'>Command Center Management System</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="e.g. pak_kaban")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("Sign In to Dashboard", type="primary", use_container_width=True)
            
            if submit:
                if (user == "pak_kaban" and pwd == "admin123") or \
                   (user.startswith("spv_") and pwd == "iwip2026"):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# --- 5. DASHBOARD UTAMA (BOOTSTRAP STYLE) ---

# Top Bar (Header)
c_head1, c_head2 = st.columns([8, 1])
with c_head1:
    user_display = st.session_state['username'].replace("spv_", "").upper()
    if user_display == "PAK_KABAN": user_display = "HEAD OF AIRPORT"
    
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 10px;'>
        <div style='background-color: #0d6efd; color: white; padding: 10px; border-radius: 8px;'>✈️</div>
        <div>
            <h3 style='margin:0; font-size: 1.5rem; color: #212529;'>IWIP Command Center</h3>
            <span style='color: #6c757d; font-size: 0.9rem;'>Welcome back, <b>{user_display}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c_head2:
    if st.button("Logout", type="secondary"):
        st.session_state['logged_in'] = False
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# VIEW: PAK KABAN (HEAD OF AIRPORT)
# ==========================================
if st.session_state['username'] == "pak_kaban":
    
    # 1. STATISTICS CARDS (Clean Layout)
    df_dir = load_data("readDirectives") # Ini Sheet 1
    
    # Hitung Statistik
    total_orders = len(df_dir)
    try:
        pending_orders = len(df_dir[df_dir['Status'] == 'OPEN'])
    except:
        pending_orders = 0
    
    # Menghapus "Unit Obstacles", fokus ke Orders saja
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Orders", total_orders)
    m2.metric("Pending Orders", pending_orders, delta="Needs Action" if pending_orders > 0 else "All Clear", delta_color="inverse")
    m3.metric("System Status", "Online", delta="Real-time")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MAIN CONTENT (TABS)
    tab1, tab2 = st.tabs(["📋 ORDERS MANAGEMENT", "📡 UNIT MONITORING"])
    
    with tab1:
        st.markdown("#### Manage Orders")
        st.caption("Assign tasks and priorities to SPT.")
        
        # Tabel Editor Orders
        edited_df = st.data_editor(
            df_dir, 
            num_rows="dynamic", 
            use_container_width=True,
            height=400,
            column_config={
                "Prioritas": st.column_config.SelectboxColumn(
                    "Priority Level",
                    options=["NORMAL", "PRIORITAS 🔥"], 
                    width="medium",
                    help="Set urgency level"
                ),
                "SPT": st.column_config.SelectboxColumn(
                    "Assign To (SPT)",
                    options=["SPT Teknik", "SPT Ops", "SPT Admin"], 
                    width="medium"
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Current Status",
                    options=["OPEN", "DONE"], 
                    width="small"
                ),
                "Task List": st.column_config.TextColumn(
                    "Order Description",
                    width="large",
                    required=True
                )
            },
            key="editor_kaban"
        )
        
        col_act1, col_act2 = st.columns([5, 1])
        with col_act2:
            if st.button("Save Orders", type="primary", use_container_width=True):
                save_data(edited_df, "Directives")

    with tab2:
        st.markdown("#### Unit Operational Status")
        st.caption("Monitor and intervene in unit operations.")
        
        df_ops = load_data("readUnitOps") # Load Sheet SPV
        
        edited_interv = st.data_editor(
            df_ops, 
            num_rows="dynamic",
            use_container_width=True,
            height=400,
            column_config={
                "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"], width="small"),
                "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"], width="medium"),
                "Plan PIC": st.column_config.SelectboxColumn("Escalation (Plan PIC)", options=["-", "SPT Teknik", "SPT Ops"], width="medium"),
                "Task List": st.column_config.TextColumn("Activity / Issue", width="large")
            },
            key="editor_interv"
        )
        
        col_act1, col_act2 = st.columns([5, 1])
        with col_act2:
            if st.button("Save Changes", type="primary", use_container_width=True):
                save_data(edited_interv, "SPV")

# ==========================================
# VIEW: SPV UNIT (OPERATIONAL)
# ==========================================
else:
    unit_name = st.session_state['username'].replace("spv_", "").upper()
    
    # Simple Header for SPV
    st.info(f"📍 You are managing dashboard for: **UNIT {unit_name}**")
    
    tab_spv1, tab_spv2 = st.tabs([f"🛠️ UPDATE {unit_name} REPORT", "📩 INBOX ORDERS"])
    
    with tab_spv1:
        st.markdown(f"#### Daily Report: {unit_name}")
        
        df_ops = load_data("readUnitOps")
        
        edited_ops = st.data_editor(
            df_ops, 
            num_rows="dynamic", 
            use_container_width=True,
            height=450,
            column_config={
                "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"], width="small"),
                "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"], width="medium"),
                "Plan PIC": st.column_config.SelectboxColumn("Escalation", options=["-", "SPT Teknik", "SPT Ops"], width="medium"),
                "Task List": st.column_config.TextColumn("Activity Description", width="large")
            },
            key="editor_spv"
        )
        
        col_act1, col_act2 = st.columns([5, 1])
        with col_act2:
            if st.button("Submit Report", type="primary", use_container_width=True):
                save_data(edited_ops, "SPV")

    with tab_spv2:
        st.markdown("#### Incoming Orders (Read Only)")
        st.caption("Orders from Head of Airport.")
        
        df_dir = load_data("readDirectives")
        
        # Tampilkan tabel statis (Read Only)
        st.dataframe(
            df_dir, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Prioritas": st.column_config.TextColumn("Priority", width="small"),
                "Task List": st.column_config.TextColumn("Order Description", width="large"),
                "Status": st.column_config.TextColumn("Status", width="small"),
            }
        )