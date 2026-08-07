import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="Quess Corp Attendance Intelligence", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# ADVANCED UI STYLING & HIDING STREAMLIT BRANDING
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
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-top: 1.5rem;
    }
    
    /* Calendar Box Styling */
    .calendar-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 14px;
        border: 2px solid #3b82f6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.15);
        margin-bottom: 25px;
    }

    .metric-container {
        padding: 22px;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        font-family: sans-serif;
    }
    .tile-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .tile-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    .tile-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); }
    .tile-blue { background: linear-gradient(135deg, #0061ff 0%, #60efff 100%); }
    
    .tile-title { font-size: 16px; font-weight: 700; opacity: 0.95; margin-bottom: 6px; }
    .tile-value { font-size: 36px; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: #1e3a8a; font-family: sans-serif; font-weight: 800;'>📊 Quess Corp - Daily Attendance Intelligence Portal 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 18px;'>Monitor daily workforce performance, leaves, and attendance seamlessly.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# STYLIZED CALENDAR CONTAINER WITH BORDER
# ==========================================
st.markdown('<div class="calendar-card">', unsafe_allow_html=True)
col_cal, col_up = st.columns([1, 1])

with col_cal:
    st.markdown("### 📅 Select Date Range / Target")
    selected_date = st.date_input(
        "Choose Attendance Date",
        value=datetime(2026, 8, 1).date(),
        label_visibility="collapsed"
    )

with col_up:
    st.markdown("### 📁 Quick File Backup Upload")
    uploaded_fallback_file = st.file_uploader("Upload Excel if auto-fetch fails", type=["xlsx", "xls", "csv"], label_visibility="collapsed")

st.markdown('</div>', unsafe_allow_html=True)

date_str = selected_date.strftime("%Y-%m-%d")

# Target file detection logic
target_df = None

if uploaded_fallback_file is not None:
    try:
        target_df = pd.read_excel(uploaded_fallback_file, sheet_name=0, dtype=str)
    except:
        target_df = pd.read_csv(uploaded_fallback_file, dtype=str)
else:
    # Check multiple possible naming formats in repository
    possible_files = [
        f"{date_str}.xlsx",
        f"{selected_date.strftime('%d%m%Y')}.xlsx",
        "DWD-AUH1-01082026 (1).xlsx",
        "attendance.xlsx"
    ]
    
    found_path = None
    for f in possible_files:
        if os.path.exists(f):
            found_path = f
            break
            
    if found_path:
        try:
            xls = pd.ExcelFile(found_path)
            sheet_name = 'Roster' if 'Roster' in xls.sheet_names else 0
            target_df = pd.read_excel(found_path, sheet_name=sheet_name, dtype=str)
        except Exception as e:
            st.error(f"Error loading file: {e}")

if target_df is not None and not target_df.empty:
    target_df.columns = [str(c).strip() for c in target_df.columns.tolist()]
    
    # Locate attendance column dynamically
    att_col = next((c for c in target_df.columns if 'attendance' in c.lower() or 'status' in c.lower()), None)
    
    if att_col:
        target_df[att_col] = target_df[att_col].str.strip().str.upper()
        total_present = len(target_df[target_df[att_col] == 'P'])
        total_absent = len(target_df[target_df[att_col] == 'AB'])
        total_sick = len(target_df[target_df[att_col] == 'SL'])
        total_planned = len(target_df[target_df[att_col] == 'PL'])
    else:
        total_present, total_absent, total_sick, total_planned = 0, 0, 0, 0

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # 4 METRIC TILES WITH EMOJIS & GRADIENTS
    # ==========================================
    t1, t2, t3, t4 = st.columns(4)
    
    with t1:
        st.markdown(f'''
            <div class="metric-container tile-green">
                <div class="tile-title">✅ Total Present</div>
                <div class="tile-value">{total_present}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with t2:
        st.markdown(f'''
            <div class="metric-container tile-red">
                <div class="tile-title">❌ Absent (AB)</div>
                <div class="tile-value">{total_absent}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with t3:
        st.markdown(f'''
            <div class="metric-container tile-orange">
                <div class="tile-title">💊 Sick Leave (SL)</div>
                <div class="tile-value">{total_sick}</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with t4:
        st.markdown(f'''
            <div class="metric-container tile-blue">
                <div class="tile-title">🏖️ Planned Leave (PL)</div>
                <div class="tile-value">{total_planned}</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader(f"📋 Employee Attendance Records for {selected_date.strftime('%d %b %Y')}")
    
    # Search Filter
    search_query = st.text_input("🔍 Search employee by Name, ID, or Department...")
    display_df = target_df.copy()
    
    if search_query:
        mask = display_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning(f"⚠️ No attendance file found automatically for **{date_str}**. Please upload your Excel file using the box above inside the calendar container to view live metrics!")
