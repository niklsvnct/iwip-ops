import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Airport Ops Command", layout="wide")

# !!! PASTE URL WEB APP SCRIPT KAMU DISINI !!!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyaCGCloW-SCD_XmirHWr0wMgUinOJ-e1Vqrmi81OREiSh9yoV-p7GDVXuEzjZ6JajfUg/exec"

# --- FUNGSI KONEKSI ---
def load_data(action):
    try:
        response = requests.get(f"{WEB_APP_URL}?action={action}")
        data = response.json()
        df = pd.DataFrame(data)
        
        # --- FIX PENTING: PAKSA MUNCULKAN HEADER JIKA KOSONG ---
        if df.empty:
            if action == "readDirectives":
                # Sesuai kolom di Sheet Directives
                return pd.DataFrame(columns=["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"])
            elif action == "readUnitOps":
                # Sesuai kolom di Sheet SPV
                return pd.DataFrame(columns=["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"])
        return df
    except Exception as e:
        # Jika error koneksi, tampilkan tabel kosong tapi ada header
        if action == "readDirectives":
            return pd.DataFrame(columns=["No", "Task List", "SPT", "Prioritas", "Waktu", "Status"])
        return pd.DataFrame(columns=["No", "Unit", "Task List", "PR", "Status", "Last PIC", "Plan PIC", "Penjelasan"])

def save_data(df, sheet_name):
    try:
        # Pastikan kolom terurut rapi sebelum dikirim
        rows = df.values.tolist()
        payload = {
            "sheetName": sheet_name,
            "rows": rows
        }
        requests.post(WEB_APP_URL, json=payload)
        st.success("✅ Data berhasil tersimpan Online ke Google Sheet!")
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

# --- TAMPILAN PAK KABAN ---
if st.session_state['username'] == "pak_kaban":
    st.info("Directives Dashboard")
    
    # Load Data
    df_directives = load_data("readDirectives")
    
    # Editor Tabel
    edited_df = st.data_editor(
        df_directives, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Prioritas": st.column_config.SelectboxColumn(options=["NORMAL", "PRIORITAS 🔥"]),
            "SPT": st.column_config.SelectboxColumn(options=["SPT Teknik", "SPT Ops", "SPT Admin"]),
            "Status": st.column_config.SelectboxColumn(options=["OPEN", "DONE"])
        }
    )
    
    if st.button("💾 SIMPAN PERUBAHAN"):
        save_data(edited_df, "Directives")

# --- TAMPILAN SPV ---
else:
    unit_name = st.session_state['username'].replace("spv_", "").upper()
    st.info(f"Unit Operations Dashboard: {unit_name}")
    
    # Note: Di Apps Script nanti ganti nama sheet jadi 'SPV' ya!
    df_ops = load_data("readUnitOps")
    
    # Editor Tabel
    edited_ops = st.data_editor(
        df_ops, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Unit": st.column_config.SelectboxColumn(options=["ATC", "AVSEC", "PK-PPK", "TEKNIK"]),
            "Status": st.column_config.SelectboxColumn(options=["On Progress", "Pending", "Stuck/Blocked", "Done"]),
            "Plan PIC": st.column_config.SelectboxColumn(options=["-", "SPT Teknik", "SPT Ops"])
        }
    )
    
    if st.button("💾 UPDATE LAPORAN"):
        # Auto Timestamp
        # edited_ops['Waktu'] = datetime.now().strftime("%Y-%m-%d %H:%M") # Opsional
        save_data(edited_ops, "SPV")