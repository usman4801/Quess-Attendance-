import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Quesscorp Attendance Intelligence", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for Filtering
if 'view_filter' not in st.session_state:
    st.session_state.view_filter = 'ALL'

# ==========================================
# ADVANCED UI STYLING & HIDING BRANDING
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
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        text-align: center;
    }

    .metric-container {
        padding: 20px 10px;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
        font-family: sans-serif;
        margin-bottom: 10px;
    }
    .tile-green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .tile-red { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
    .tile-orange { background: linear-gradient(135deg, #f12711 0%, #f5af19 100%); }
    .tile-blue { background: linear-gradient(135deg, #0061ff 0%, #60efff 100%); }
    .tile-gray { background: linear-gradient(135deg, #606c88 0%, #3f4c6b 100%); }
    
    .tile-title { font-size: 15px; font-weight: 700; opacity: 0.95; margin-bottom: 6px; }
    .tile-value { font-size: 32px; font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 style='text-align: center; color: #1e3a8a; font-family: sans-serif; font-weight: 800;'>📊 Quesscorp - Daily Attendance Intelligence Portal 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4b5563; font-size: 18px;'>Monitor daily workforce performance, leaves, and attendance seamlessly.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# CALENDAR SELECTION CONTAINER
# ==========================================
st.markdown('<div class="calendar-card">', unsafe_allow_html=True)
st.markdown("### 📅 Select Attendance Date")
selected_date = st.date_input(
    "Choose Attendance Date",
    value=datetime(2026, 8, 1).date(),
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

date_str = selected_date.strftime("%Y-%m-%d")

# Target file detection logic
possible_files = [
    f"{date_str}.xlsx",
    f"{date_str}.xlsx.xlsx", 
    f"{selected_date.strftime('%d%m%Y')}.xlsx",
    "2026-08-01.xlsx",
    "2026-08-01.xlsx.xlsx"
]

target_df = None
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
        total_off = len(target_df[target_df[att_col] == 'OFF'])
    else:
        total_present, total_absent, total_sick, total_planned, total_off = 0, 0, 0, 0, 0

    # ==========================================
    # PROMINENT DATE BANNER
    # ==========================================
    st.markdown(f"""
        <div style="background-color: #e0f2fe; padding: 15px; border-radius: 10px; border-left: 6px solid #0284c7; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="margin:0; color: #0369a1; text-align: center;">📅 Showing Data For: {selected_date.strftime('%d %B %Y')}</h2>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 5 METRIC TILES
    # ==========================================
    t1, t2, t3, t4, t5 = st.columns(5)
    
    with t1:
        st.markdown(f'''
            <div class="metric-container tile-green">
                <div class="tile-title">✅ Present</div>
                <div class="tile-value">{total_present}</div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("👁️ View Present", use_container_width=True): st.session_state.view_filter = 'P'
        
    with t2:
        st.markdown(f'''
            <div class="metric-container tile-red">
                <div class="tile-title">❌ Absent (AB)</div>
                <div class="tile-value">{total_absent}</div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("👁️ View Absent", use_container_width=True): st.session_state.view_filter = 'AB'
        
    with t3:
        st.markdown(f'''
            <div class="metric-container tile-orange">
                <div class="tile-title">💊 Sick (SL)</div>
                <div class="tile-value">{total_sick}</div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("👁️ View Sick", use_container_width=True): st.session_state.view_filter = 'SL'
        
    with t4:
        st.markdown(f'''
            <div class="metric-container tile-blue">
                <div class="tile-title">🏖️ Planned (PL)</div>
                <div class="tile-value">{total_planned}</div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("👁️ View Planned", use_container_width=True): st.session_state.view_filter = 'PL'

    with t5:
        st.markdown(f'''
            <div class="metric-container tile-gray">
                <div class="tile-title">💤 OFF</div>
                <div class="tile-value">{total_off}</div>
            </div>
        ''', unsafe_allow_html=True)
        if st.button("👁️ View OFF", use_container_width=True): st.session_state.view_filter = 'OFF'

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ==========================================
    # DATA FILTERING & TABLE DISPLAY
    # ==========================================
    display_df = target_df.copy()
    
    # Insert Date Column
    formatted_display_date = selected_date.strftime('%d-%b-%Y')
    display_df.insert(0, 'Date', formatted_display_date)
    
    # Apply View Filter
    if st.session_state.view_filter != 'ALL':
        display_df = display_df[display_df[att_col] == st.session_state.view_filter]
        
        col_info, col_btn = st.columns([8, 2])
        with col_info:
            st.info(f"🔎 Currently showing only **{st.session_state.view_filter}** records.")
        with col_btn:
            if st.button("🔄 View All Records", use_container_width=True):
                st.session_state.view_filter = 'ALL'
                st.rerun()

    st.subheader(f"📋 Employee Attendance Records")
    
    # Search Filter
    search_query = st.text_input("🔍 Search employee by Name, ID, or Department...")
    
    if search_query:
        mask = display_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ==========================================
    # DOWNLOAD BUTTON
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Convert dataframe to CSV format
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    
    # Center the download button
    d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
    with d_col2:
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv_data,
            file_name=f"Quesscorp_Attendance_{date_str}.csv",
            mime='text/csv',
            use_container_width=True
        )

else:
    st.warning(f"⚠️ No attendance file found for **{date_str}**. Make sure your Excel file is uploaded in your GitHub repository.")
