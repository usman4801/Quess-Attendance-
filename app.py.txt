import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Quess Attendance Dashboard", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# CUSTOM STYLING & METRIC CARDS
# ==========================================
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    
    .block-container {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 2.5rem;
        border-radius: 14px;
        box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.08);
        margin-top: 1rem;
    }
    .metric-container {
        padding: 20px;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        font-family: sans-serif;
    }
    .tile-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .tile-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    .tile-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); }
    .tile-blue { background: linear-gradient(135deg, #0061ff 0%, #60efff 100%); }
    
    .tile-title { font-size: 15px; font-weight: 600; opacity: 0.95; margin-bottom: 8px; }
    .tile-value { font-size: 32px; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📋 Quess Corp - Daily Attendance Dashboard")
st.markdown("---")

# ==========================================
# MAIN PAGE DATE PICKER (NO SIDEBAR UPLOADER)
# ==========================================
col_date, _ = st.columns([4, 6])
with col_date:
    selected_date = st.date_input(
        "📅 Select Attendance Date",
        value=datetime(2026, 8, 1).date()  # Aapke sample ke mutabiq default date
    )

date_str = selected_date.strftime("%Y-%m-%d")

# File search logic (e.g., matching YYYY-MM-DD.xlsx or similar naming convention)
# Aap apni files ko date ke mutabiq repository mein rakh sakte hain, jaise "2026-08-01.xlsx"
possible_filenames = [
    f"{date_str}.xlsx",
    f"{selected_date.strftime('%d%m%Y')}.xlsx",
    "DWD-AUH1-01082026 (1).xlsx"  # Fallback for testing with your exact uploaded sample name
]

target_file = None
for fname in possible_filenames:
    if os.path.exists(fname):
        target_file = fname
        break

if target_file:
    try:
        # Sheet check: 'Roster' sheet agar mojood ho toh wohi read karein ge
        xls = pd.ExcelFile(target_file)
        sheet_to_load = 'Roster' if 'Roster' in xls.sheet_names else 0
        df = pd.read_excel(target_file, sheet_name=sheet_to_load, dtype=str)
        
        # Clean columns
        df.columns = [str(c).strip() for c in df.columns.tolist()]
        
        # Find attendance column dynamically if named slightly different
        att_col = next((c for c in df.columns if 'attendance' in c.lower() or 'status' in c.lower()), None)
        
        if att_col:
            # Standardize attendance values (uppercase)
            df[att_col] = df[att_col].str.strip().str.upper()
            
            total_present = len(df[df[att_col] == 'P'])
            total_absent = len(df[df[att_col] == 'AB'])
            total_sick = len(df[df[att_col] == 'SL'])
            total_planned = len(df[df[att_col] == 'PL'])
        else:
            total_present, total_absent, total_sick, total_planned = 0, 0, 0, 0

        st.markdown("<br>", unsafe_allow_html=True)
        
        # ==========================================
        # 4 METRIC TILES
        # ==========================================
        t1, t2, t3, t4 = st.columns(4)
        
        with t1:
            st.markdown(f'''
                <div class="metric-container tile-green">
                    <div class="tile-title">Total Present</div>
                    <div class="tile-value">{total_present}</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with t2:
            st.markdown(f'''
                <div class="metric-container tile-red">
                    <div class="tile-title">Absent (AB)</div>
                    <div class="tile-value">{total_absent}</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with t3:
            st.markdown(f'''
                <div class="metric-container tile-orange">
                    <div class="tile-title">Sick Leave (SL)</div>
                    <div class="tile-value">{total_sick}</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with t4:
            st.markdown(f'''
                <div class="metric-container tile-blue">
                    <div class="tile-title">Planned Leave (PL)</div>
                    <div class="tile-value">{total_planned}</div>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.subheader(f"📊 Detailed Attendance Records ({selected_date.strftime('%d %b %Y')})")
        
        # Search filter
        search_query = st.text_input("🔍 Search Employee by Name, ID, or AMZ ID...")
        display_df = df.copy()
        
        if search_query:
            # Search across text columns
            mask = display_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            display_df = display_df[mask]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"⚠️ Error reading the attendance file: {e}")
else:
    st.warning(f"⚠️ No attendance file found for **{date_str}**. Please ensure the file is uploaded to your repository with the correct date format.")
