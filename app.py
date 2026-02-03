import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="Airport Ops Command", layout="wide")

# !!! PASTE URL DARI TAHAP 1 DISINI (DIBAGIAN DALAM KUTIP) !!!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyaCGCloW-SCD_XmirHWr0wMgUinOJ-e1Vqrmi81OREiSh9yoV-p7GDVXuEzjZ6JajfUg/exec"

# --- FUNGSI KONEKSI KE JEMBATAN ---
def load_data(action):
    try:
        response = requests.get(f"{WEB_APP_URL}?action={action}")
        data = response.json()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return pd.DataFrame()

def save_data(df, sheet_name):
    try:
        # Konversi DataFrame ke List of Lists untuk dikirim ke Google Sheet
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
        # Password sederhana hardcoded
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
    
    # Load Data dari Google Sheet
    df_directives = load_data("readDirectives")
    
    # Tampilkan Editor
    edited_df = st.data_editor(df_directives, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 SIMPAN PERUBAHAN"):
        save_data(edited_df, "Directives")

# --- TAMPILAN SPV ---
else:
    unit_name = st.session_state['username'].replace("spv_", "").upper()
    st.info(f"Unit Operations Dashboard: {unit_name}")
    
    # Load Data dari Google Sheet
    df_ops = load_data("readUnitOps")
    
    # Filter dan Editor
    edited_ops = st.data_editor(df_ops, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 UPDATE LAPORAN"):
        # Update Timestamp manual di code biar simple
        edited_ops['Updated_At'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        save_data(edited_ops, "UnitOps")