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
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                                   'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                                   'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 'JATERRADO', 
                                   'LMLABRADOR', 'EASORIANO'])]  # Exclude specific users
    return df

# ------------------- FUNCTION TO GENERATE COLLECTOR SUMMARY -------------------
def generate_collector_summary(df):
    collector_summary = pd.DataFrame(columns=[
        'Date', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])
    
    df = df[df['Status'] != 'PTP FF UP']  # Exclude certain statuses

    for (date, collector), collector_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Remark By']):
        total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = collector_group[
            (collector_group['Status'].str.contains('PTP', na=False)) & 
            (collector_group['PTP Amount'] != 0) & 
            (collector_group['Balance'] != 0)
        ]['Balance'].sum()

        collector_summary = pd.concat([collector_summary, pd.DataFrame([{
            'Date': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    return collector_summary

# ------------------- FUNCTION TO GENERATE CYCLE SUMMARY -------------------
def generate_cycle_summary(df):
    cycle_summary_by_date = {}

    df = df[df['Status'] != 'PTP FF UP']

    for (date, cycle), cycle_group in df[~df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([df['Date'].dt.date, 'Service No.']):
        total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].count()
        ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = cycle_group[
            (cycle_group['Status'].str.contains('PTP', na=False)) & 
            (cycle_group['PTP Amount'] != 0) & 
            (cycle_group['Balance'] != 0)
        ]['Balance'].sum()

        cycle_summary = pd.DataFrame([{
            'Date': date,
            'Cycle': cycle,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])

        if date in cycle_summary_by_date:
            cycle_summary_by_date[date] = pd.concat([cycle_summary_by_date[date], cycle_summary], ignore_index=True)
        else:
            cycle_summary_by_date[date] = cycle_summary

    return cycle_summary_by_date

# ------------------- MAIN APP LOGIC -------------------
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Display the title for Collector Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY COLLECTOR</div>', unsafe_allow_html=True)
    collector_summary = generate_collector_summary(df)
    st.dataframe(collector_summary)

    # Display the title for Cycle Summary
    st.markdown('<div class="category-title">📋 PRODUCTIVITY BY CYCLE (Separated per Date)</div>', unsafe_allow_html=True)
    cycle_summary_by_date = generate_cycle_summary(df)

    for date, summary in cycle_summary_by_date.items():
        st.markdown(f'**Date: {date}**')
        st.dataframe(summary)
