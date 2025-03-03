import streamlit as st
import pandas as pd
import re

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

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 'LMLABRADOR', 'EASORIANO'])]
    return df

# ------------------- FILE UPLOADER -------------------
uploaded_file = st.sidebar.file_uploader("📂 Upload Daily Remark File", type="xlsx")

if uploaded_file:
    df = load_data(uploaded_file)
    
    # ------------------- PRODUCTIVITY SUMMARY -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Productivity Summary Table")

    summary = df.groupby(df['Date'].dt.date).agg(
        Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] > 0)).sum()),  # Added condition to check PTP Amount
        Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),  # Corrected indentation here
        Total_PTP_Amount=('PTP Amount', lambda x: x[x > 0].sum()),  # Summing only PTP Amount > 0
        Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] > 0)].sum())  # Added condition to check PTP Amount
    ).reset_index()

    st.dataframe(summary, width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- PRODUCTIVITY SUMMARY PER CYCLE -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📆 Productivity Summary per Cycle (Grouped by Date)")

    df['Cycle'] = df['Service No.'].astype(str)
    cycle_summary = df.groupby([df['Date'].dt.date, 'Cycle']).agg(
        Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] > 0)).sum()),  # Added condition to check PTP Amount
        Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),  # Corrected indentation here
        Total_PTP_Amount=('PTP Amount', lambda x: x[x > 0].sum()),  # Summing only PTP Amount > 0
        Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False) & (df.loc[x.index, 'PTP Amount'] > 0)].sum())  # Added condition to check PTP Amount
    ).reset_index()

    st.dataframe(cycle_summary, width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- PRODUCTIVITY SUMMARY PER COLLECTOR -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 Productivity Summary per Collector")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input("📅 Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    filtered_df = filtered_df[~filtered_df['Remark By'].str.upper().isin(["SYSTEM"])]

    collector_summary = pd.DataFrame()

    for (date, collector), collector_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']):
        total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] > 0)]['Account No.'].nunique()  # Added condition to check PTP Amount
        total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
        ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] > 0)]['PTP Amount'].sum()  # Summing only PTP Amount > 0
        balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0) & (collector_group['PTP Amount'] > 0)]['Balance'].sum()  # Added condition to check PTP Amount
        
        collector_summary = pd.concat([collector_summary, pd.DataFrame([{
            'Day': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    st.dataframe(collector_summary, width=1500)
    st.markdown('</div>', unsafe_allow_html=True)
