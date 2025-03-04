import streamlit as st
import pandas as pd

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Dashboard", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# ------------------- GLOBAL STYLING -------------------
st.markdown("""
    <style>
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #FFD700, #FFA500);
            color: white;
            font-size: 24px;
            border-radius: 10px;
            font-weight: bold;
        }
        .category-title {
            font-size: 20px;
            font-weight: bold;
            margin-top: 30px;
            color: #FF8C00;
        }
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)

# ------------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("Upload your data file", type=["xlsx"])

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time']).dt.hour  # Extract only the hour for time-based summaries
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
        'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
        'LMLABRADOR', 'EASORIANO'
    ])]  # Exclude specific users
    return df

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    collector_summary = df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (df['Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: (df['Status'].str.contains('PTP', na=False) & (df['PTP Amount'] != 0)).sum()),
        Total_RPC=('Account No.', lambda x: (df['Status'].str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

    return collector_summary.rename(columns={"Remark By": "Collector"})

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    cycle_summary = df.groupby(['Date', 'Service No.']).agg(
        Total_Connected=('Account No.', lambda x: (df['Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: (df['Status'].str.contains('PTP', na=False) & (df['PTP Amount'] != 0)).sum()),
        Total_RPC=('Account No.', lambda x: (df['Status'].str.contains('RPC', na=False)).sum()),
        PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')
    ).reset_index()

    return cycle_summary.rename(columns={"Service No.": "Cycle"})

# ------------------- FUNCTION TO GENERATE HOURLY PTP SUMMARY -------------------
def generate_hourly_ptp_summary(df):
    hourly_summary = df[df['Status'].str.contains('PTP', na=False) & (df['PTP Amount'] != 0)]
    
    hourly_ptp_summary = hourly_summary.groupby(['Date', 'Time']).agg(
        Total_PTP=('Account No.', 'nunique'),
        PTP_Amount=('PTP Amount', 'sum')
    ).reset_index()

    return hourly_ptp_summary

# ------------------- DISPLAY DATA IF FILE IS UPLOADED -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)

    # --- Collector Summary ---
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    collector_summary = generate_collector_summary(df)
    st.write(collector_summary)

    # --- Cycle Summary ---
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE</div>', unsafe_allow_html=True)
    cycle_summary = generate_cycle_summary(df)
    st.write(cycle_summary)

    # --- Hourly PTP Summary ---
    st.markdown('<div class="category-title">⏳ HOURLY PTP SUMMARY</div>', unsafe_allow_html=True)
    hourly_ptp_summary = generate_hourly_ptp_summary(df)
    st.write(hourly_ptp_summary)
