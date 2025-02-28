import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .reportview-container {
        background: #2E2E2E;
        color: white;
    }
    .sidebar .sidebar-content {
        background: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Daily Remark Summary - Productivity Only')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR'])]  # Exclude specific Remark By
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Function to calculate productivity summary
    def calculate_productivity_summary(df):
        productivity_table = pd.DataFrame(columns=[
            'Day', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount'
        ])
        
        total_connected_all = 0
        total_ptp_all = 0
        total_rpc_all = 0
        total_ptp_amount_all = 0

        for date, group in df.groupby(df['Date'].dt.date):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()

            # Adding the summary data to the dataframe
            productivity_table = pd.concat([productivity_table, pd.DataFrame([{
                'Day': date,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
            }])], ignore_index=True)

            # Update overall totals
            total_connected_all += total_connected
            total_ptp_all += total_ptp
            total_rpc_all += total_rpc
            total_ptp_amount_all += total_ptp_amount

        # Add a row with total values
        productivity_table = pd.concat([productivity_table, pd.DataFrame([{
            'Day': 'Total',
            'Total Connected': total_connected_all,
            'Total PTP': total_ptp_all,
            'Total RPC': total_rpc_all,
            'Total PTP Amount': total_ptp_amount_all,
        }])], ignore_index=True)

        return productivity_table

    # Display the productivity summary
    st.write("## Productivity Summary Table")
    productivity_summary_table = calculate_productivity_summary(df)
    st.write(productivity_summary_table)

    col5, col6 = st.columns(2)

    with col5:
        st.write("## Productivity Summary by Collector per Day")
        
        # Add date filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        collector_productivity_summary = pd.DataFrame(columns=[
            'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount'
        ])
        
        total_connected_all_collector = 0
        total_ptp_all_collector = 0
        total_rpc_all_collector = 0
        total_ptp_amount_all_collector = 0
        total_balance_amount_all_collector = 0

        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

            # Adding the collector's productivity data
            collector_productivity_summary = pd.concat([collector_productivity_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

            # Update overall totals for collectors
            total_connected_all_collector += total_connected
            total_ptp_all_collector += total_ptp
            total_rpc_all_collector += total_rpc
            total_ptp_amount_all_collector += total_ptp_amount
            total_balance_amount_all_collector += total_ptp_amount
            

        # Add a row with total values for the collector summary
        collector_productivity_summary = pd.concat([collector_productivity_summary, pd.DataFrame([{
            'Day': 'Total',
            'Collector': 'All Collectors',
            'Total Connected': total_connected_all_collector,
            'Total PTP': total_ptp_all_collector,
            'Total RPC': total_rpc_all_collector,
            'Total PTP Amount': total_ptp_amount_all_collector,
            'Balance Amount: total_ total_balance_amount_all_collector,
        }])], ignore_index=True)

        st.write(collector_productivity_summary)
