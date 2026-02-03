import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CONFIG (Agar tampilan lebar) ---
st.set_page_config(page_title="Airport Ops Command", layout="wide")

# URL API SCRIPT KAMU (SUDAH SAYA MASUKKAN DISINI)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyaCGCloW-SCD_XmirHWr0wMgUinOJ-e1Vqrmi81OREiSh9yoV-p7GDVXuEzjZ6JajfUg/exec"

# --- FUNGSI KONEKSI ---
def load_data(action):
    try:
        response = requests.get(f"{WEB_APP_URL}?action={action}")
        data = response.json()
        df = pd.DataFrame(data)
        
        # FIX: Paksa muncul header jika kosong
        if df.empty:
            if action == "readDirectives":
                return pd.DataFrame(columns=["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"])
            elif action == "readUnitOps":
                return pd.DataFrame(columns=["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"])
        return df
    except Exception as e:
        if action == "readDirectives":
            return pd.DataFrame(columns=["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"])
        return pd.DataFrame(columns=["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"])

def save_data(df, sheet_name):
    try:
        rows = df.values.tolist()
        payload = {"sheetName": sheet_name, "rows": rows}
        requests.post(WEB_APP_URL, json=payload)
        st.success("✅ Data berhasil tersimpan Online!")
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")

# --- LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("✈️ Portal Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if (user == "pak_kaban" and pwd == "admin123") or \
           (user.startswith("spv_") and pwd == "iwip2026"):
            st.session_state['logged_in'] = True
            st.session_state['username'] = user
            st.rerun()
        else:
            st.error("Username/Password Salah")
    st.stop()

# --- HEADER & LOGOUT ---
c1, c2 = st.columns([8, 1])
with c1:
    st.title("✈️ Airport Ops Command Center")
    st.caption(f"User: {st.session_state['username']} | Mode: Online Real-time")
with c2:
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# ==========================================
# SKENARIO 1: TAMPILAN PAK KABAN
# ==========================================
if st.session_state['username'] == "pak_kaban":
    
    # Buat 2 Tab
    tab1, tab2 = st.tabs(["📝 BERIKAN PERINTAH (DIRECTIVES)", "👀 MONITORING LAPANGAN (SPV)"])
    
    # --- TAB 1: Kaban Nulis Perintah (Bisa Edit) ---
    with tab1:
        st.info("Dashboard Arahan Pimpinan (Silakan Edit)")
        df_directives = load_data("readDirectives")
        
        edited_df = st.data_editor(
            df_directives, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "Prioritas": st.column_config.SelectboxColumn(options=["NORMAL", "PRIORITAS 🔥"]),
                "SPT": st.column_config.SelectboxColumn(options=["SPT Teknik", "SPT Ops", "SPT Admin"]),
                "Status": st.column_config.SelectboxColumn(options=["OPEN", "DONE"])
            },
            key="editor_kaban"
        )
        
        if st.button("💾 SIMPAN PERUBAHAN", key="btn_kaban"):
            save_data(edited_df, "Directives")

    # --- TAB 2: Kaban Intip Kerjaan SPV (Read Only) ---
    with tab2:
        st.warning("Monitoring Seluruh Unit (Hanya Bisa Dilihat/Read Only)")
        df_monitoring = load_data("readUnitOps")
        
        # Pakai st.dataframe() agar tidak bisa diedit
        st.dataframe(df_monitoring, use_container_width=True, hide_index=True)


# ==========================================
# SKENARIO 2: TAMPILAN SPV
# ==========================================
else:
    unit_name = st.session_state['username'].replace("spv_", "").upper()
    
    # Buat 2 Tab
    tab_spv1, tab_spv2 = st.tabs([f"🛠️ LAPORAN UNIT {unit_name}", "📜 LIHAT ARAHAN PIMPINAN"])
    
    # --- TAB 1: SPV Lapor Kerja (Bisa Edit) ---
    with tab_spv1:
        st.info(f"Update Laporan Operasional Unit: {unit_name}")
        df_ops = load_data("readUnitOps")
        
        edited_ops = st.data_editor(
            df_ops, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"]),
                "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"]),
                "Plan PIC": st.column_config.SelectboxColumn(options=["-", "SPT Teknik", "SPT Ops"])
            },
            key="editor_spv"
        )
        
        if st.button("💾 UPDATE LAPORAN", key="btn_spv"):
            save_data(edited_ops, "SPV")

    # --- TAB 2: SPV Baca Tugas Kaban (Read Only) ---
    with tab_spv2:
        st.success("Daftar Arahan Langsung dari Pak Kaban (Read Only)")
        df_baca_tugas = load_data("readDirectives")
        
        # Pakai st.dataframe() agar tidak bisa diedit
        st.dataframe(df_baca_tugas, use_container_width=True, hide_index=True)