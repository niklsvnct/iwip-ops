import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 1. KONFIGURASI HALAMAN (WIDE & JUDUL) ---
st.set_page_config(page_title="IWIP Airport Ops", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (RAHASIA TAMPILAN PRO) ---
# Kode ini menghilangkan padding berlebih, menyembunyikan menu 'Deploy', dan merapikan font
def local_css():
    st.markdown("""
    <style>
        /* Hilangkan Padding Atas yang terlalu lebar */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        /* Style Header Tab supaya lebih tegas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px 4px 0px 0px;
            font-weight: 600;
        }
        /* Rapikan Tombol */
        .stButton>button {
            border-radius: 6px;
            height: 3em;
            font-weight: bold;
        }
        /* Sembunyikan Footer & Menu Streamlit bawaan biar bersih */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. KONEKSI DATA ---
# !!! PASTE URL GOOGLE APPS SCRIPT KAMU DI BAWAH INI !!!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyaCGCloW-SCD_XmirHWr0wMgUinOJ-e1Vqrmi81OREiSh9yoV-p7GDVXuEzjZ6JajfUg/exec"

@st.cache_data(ttl=10, show_spinner=False)
def load_data(action):
    try:
        response = requests.get(f"{WEB_APP_URL}?action={action}")
        data = response.json()
        df = pd.DataFrame(data)
        if df.empty:
            if action == "readDirectives":
                return pd.DataFrame(columns=["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"])
            elif action == "readUnitOps":
                return pd.DataFrame(columns=["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"])
        return df
    except:
        # Fallback aman
        return pd.DataFrame()

def save_data(df, sheet_name):
    try:
        rows = df.values.tolist()
        payload = {"sheetName": sheet_name, "rows": rows}
        requests.post(WEB_APP_URL, json=payload)
        st.toast("✅ Data berhasil disimpan ke Server!", icon="💾") # Pakai Toast biar elegan
        st.cache_data.clear()
        import time
        time.sleep(1) # Jeda dikit biar toast kebaca
        st.rerun()
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")

# --- 4. LOGIC LOGIN (Simpel & Tengah) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### ✈️ Airport Operations System")
        st.markdown("Silakan login untuk mengakses dashboard.")
        with st.form("login_form"):
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", type="primary")
            
            if submit:
                if (user == "pak_kaban" and pwd == "admin123") or \
                   (user.startswith("spv_") and pwd == "iwip2026"):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = user
                    st.rerun()
                else:
                    st.error("Akses Ditolak. Periksa Username/Password.")
    st.stop()

# --- 5. DASHBOARD UTAMA ---

# Header Bar (Top Bar)
col_head1, col_head2 = st.columns([6, 1])
with col_head1:
    st.markdown(f"### ✈️ IWIP Airport Command Center")
    st.caption(f"Logged in as: **{st.session_state['username'].upper()}** | {datetime.now().strftime('%d %b %Y')}")
with col_head2:
    if st.button("Logout", type="secondary"):
        st.session_state['logged_in'] = False
        st.rerun()

st.markdown("---") # Garis pemisah tipis

# ==========================================
# VIEW: PAK KABAN (EXECUTIVE DASHBOARD)
# ==========================================
if st.session_state['username'] == "pak_kaban":
    
    # 1. METRICS (KPI) - Biar terlihat dashboard mahal
    df_dir = load_data("readDirectives")
    df_ops = load_data("readUnitOps")
    
    total_tasks = len(df_dir)
    pending_tasks = len(df_dir[df_dir['Status'] == 'OPEN'])
    ops_issues = len(df_ops[df_ops['Status'].isin(['Pending', 'Stuck/Blocked'])])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Directives", total_tasks, border=True)
    m2.metric("Pending Directives", pending_tasks, delta_color="inverse", border=True)
    m3.metric("Unit Obstacles", ops_issues, delta=f"{ops_issues} Issues", delta_color="inverse", border=True)
    m4.metric("System Status", "Online", border=True)

    st.write("") # Spacer

    # 2. TABS MANAGEMENT
    tab1, tab2 = st.tabs(["📋 Directives Management", "🔍 Unit Monitoring & Intervention"])
    
    with tab1:
        st.markdown("#### Daftar Perintah Kerja (Directives)")
        
        edited_df = st.data_editor(
            df_dir, 
            num_rows="dynamic", 
            use_container_width=True,
            height=400, # Tinggi tabel fix biar rapi
            column_config={
                "Prioritas": st.column_config.SelectboxColumn(options=["NORMAL", "PRIORITAS 🔥"], width="medium"),
                "SPT": st.column_config.SelectboxColumn(options=["SPT Teknik", "SPT Ops", "SPT Admin"], width="medium"),
                "Status": st.column_config.SelectboxColumn(options=["OPEN", "DONE"], width="small"),
                "Task List": st.column_config.TextColumn(width="large")
            },
            key="editor_kaban"
        )
        
        # Tombol Simpan di kanan
        c_btn1, c_btn2 = st.columns([5, 1])
        with c_btn2:
            if st.button("Simpan Perintah", type="primary", use_container_width=True):
                save_data(edited_df, "Directives")

    with tab2:
        st.markdown("#### Status Operasional Unit (Intervention Mode)")
        
        edited_interv = st.data_editor(
            df_ops, 
            num_rows="dynamic",
            use_container_width=True,
            height=400,
            column_config={
                "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"], width="small"),
                "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"], width="medium"),
                "Plan PIC": st.column_config.SelectboxColumn(options=["-", "SPT Teknik", "SPT Ops"], width="medium"),
                "Task List": st.column_config.TextColumn(width="large")
            },
            key="editor_interv"
        )
        
        c_btn1, c_btn2 = st.columns([5, 1])
        with c_btn2:
            if st.button("Simpan Intervensi", type="primary", use_container_width=True):
                save_data(edited_interv, "SPV")

# ==========================================
# VIEW: SPV UNIT (OPERATIONAL DASHBOARD)
# ==========================================
else:
    unit_name = st.session_state['username'].replace("spv_", "").upper()
    
    # 1. SUMMARY METRICS
    df_ops = load_data("readUnitOps")
    my_tasks = df_ops
    # Filter opsional: my_tasks = df_ops[df_ops['Unit'] == unit_name] 
    
    pending_cnt = len(my_tasks[my_tasks['Status'] == 'Pending'])
    done_cnt = len(my_tasks[my_tasks['Status'] == 'Done'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Laporan Unit {unit_name}", len(my_tasks), border=True)
    m2.metric("Status Pending", pending_cnt, delta="Butuh Tindakan" if pending_cnt > 0 else "Aman", delta_color="inverse", border=True)
    m3.metric("Pekerjaan Selesai", done_cnt, border=True)
    
    st.write("")
    
    # 2. TABS
    tab_spv1, tab_spv2 = st.tabs([f"🛠️ Update Laporan {unit_name}", "📩 Inbox Arahan Pimpinan"])
    
    with tab_spv1:
        st.markdown(f"#### Form Laporan Harian: {unit_name}")
        edited_ops = st.data_editor(
            df_ops, 
            num_rows="dynamic", 
            use_container_width=True,
            height=450,
            column_config={
                "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"], width="small"),
                "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"], width="medium"),
                "Plan PIC": st.column_config.SelectboxColumn(options=["-", "SPT Teknik", "SPT Ops"], width="medium"),
                "Task List": st.column_config.TextColumn(width="large")
            },
            key="editor_spv"
        )
        
        c_btn1, c_btn2 = st.columns([5, 1])
        with c_btn2:
            if st.button("Kirim Laporan", type="primary", use_container_width=True):
                save_data(edited_ops, "SPV")

    with tab_spv2:
        st.markdown("#### Arahan Masuk (Read Only)")
        df_dir = load_data("readDirectives")
        # Menampilkan tabel statis dengan style
        st.dataframe(
            df_dir, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Prioritas": st.column_config.TextColumn(width="small"),
                "Task List": st.column_config.TextColumn(width="large"),
            }
        )