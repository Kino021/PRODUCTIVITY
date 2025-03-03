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
        Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
        Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
    ).reset_index()

    st.dataframe(summary, width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- PRODUCTIVITY SUMMARY PER CYCLE -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📆 Productivity Summary per Cycle (Grouped by Date)")

    df['Cycle'] = df['Service No.'].astype(str)
    cycle_summary = df.groupby([df['Date'].dt.date, 'Cycle']).agg(
        Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
        Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
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

   collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
            }])], ignore_index=True)
        
        st.write(collector_summary)
    with col6:
        st.write("## Claim Paid Summary Table")

        # Add date filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date ranges", [min_date, max_date], min_value=min_date, max_value=max_date)

        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        cp_collector_summary = pd.DataFrame(columns=[
            'Day', 'Collector', 'Total Claim Paid','Claim Paid Amount','Balance Amount'
        ])
        
        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            claim_paid_count = collector_group[collector_group['Reason For Default'].str.contains('CURED', na=False) ]['Account No.'].nunique()
            claim_paid_amount = collector_group[collector_group['Reason For Default'].str.contains('CURED', na=False)]['Claim Paid Amount'].sum()
            balance_amount = collector_group[collector_group['Reason For Default'].str.contains('CURED', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()
            
            
            cp_collector_summary = pd.concat([cp_collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Claim Paid': claim_paid_count,
                'Claim Paid Amount': claim_paid_amount,
                'Balance Amount': balance_amount
            }])], ignore_index=True)
        
        st.write(cp_collector_summary)
