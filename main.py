import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .stApp {
        background-color: #2E2E2E;
        color: white;
    }
    .stSidebar {
        background-color: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 
        'MEBEJER', 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 
        'EUGALERA', 'JATERRADO', 'LMLABRADOR'
    ])]  
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date is in datetime format
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # --- Productivity Summary per Day ---
    def calculate_productivity_summary(df):
        summary_table = pd.DataFrame(columns=[
            'Day', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount'
        ])
        totals = {'Total Connected': 0, 'Total PTP': 0, 'Total RPC': 0, 'Total PTP Amount': 0}

        for date, group in df.groupby(df['Date'].dt.date):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()

            summary_table = pd.concat([summary_table, pd.DataFrame([{
                'Day': date,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount
            }])], ignore_index=True)

            totals['Total Connected'] += total_connected
            totals['Total PTP'] += total_ptp
            totals['Total RPC'] += total_rpc
            totals['Total PTP Amount'] += total_ptp_amount

        summary_table = pd.concat([summary_table, pd.DataFrame([{**{'Day': 'Total'}, **totals}])], ignore_index=True)
        return summary_table

    st.write("## Productivity Summary Table")
    st.write(calculate_productivity_summary(df))

    # --- Productivity Summary per Cycle ---
    def calculate_productivity_per_cycle(df):
        cycle_summary = pd.DataFrame(columns=[
            'Cycle (Service No.)', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount'
        ])
        totals = {'Total Connected': 0, 'Total PTP': 0, 'Total RPC': 0, 'Total PTP Amount': 0}

        for service_no, group in df.groupby('Service No.'):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()

            cycle_summary = pd.concat([cycle_summary, pd.DataFrame([{
                'Cycle (Service No.)': service_no,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount
            }])], ignore_index=True)

            totals['Total Connected'] += total_connected
            totals['Total PTP'] += total_ptp
            totals['Total RPC'] += total_rpc
            totals['Total PTP Amount'] += total_ptp_amount

        cycle_summary = pd.concat([cycle_summary, pd.DataFrame([{**{'Cycle (Service No.)': 'Total'}, **totals}])], ignore_index=True)
        return cycle_summary

    st.write("## Productivity Summary per Cycle")
    st.write(calculate_productivity_per_cycle(df))

    # --- Productivity Summary per Collector ---
    st.write("## Productivity Summary per Collector")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    collector_summary = pd.DataFrame(columns=[
        'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
    ])
    totals = {'Total Connected': 0, 'Total PTP': 0, 'Total RPC': 0, 'Total PTP Amount': 0, 'Balance Amount': 0}

    for (date, collector), group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']):
        total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
        total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()
        total_balance = group[group['Status'].str.contains('PTP', na=False) & (group['Balance'] != 0)]['Balance'].sum()

        collector_summary = pd.concat([collector_summary, pd.DataFrame([{
            'Day': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'Total PTP Amount': total_ptp_amount,
            'Balance Amount': total_balance
        }])], ignore_index=True)

        totals['Total Connected'] += total_connected
        totals['Total PTP'] += total_ptp
        totals['Total RPC'] += total_rpc
        totals['Total PTP Amount'] += total_ptp_amount
        totals['Balance Amount'] += total_balance

    collector_summary = pd.concat([collector_summary, pd.DataFrame([{**{'Day': 'Total', 'Collector': 'All Collectors'}, **totals}])], ignore_index=True)

    st.write(collector_summary)
