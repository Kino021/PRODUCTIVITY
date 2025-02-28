import streamlit as st
import pandas as pd

# Page configuration
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

# Remove title from the page by hiding it via CSS
st.markdown("""
    <style>
        .css-1v0mbdj {display: none;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR'])]  # Exclude specific Remark By
    return df

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    # Load the filtered data (we'll not display the raw data anymore)
    df = load_data(uploaded_file)

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

    # --- Calculate Productivity per Cycle ---
    def calculate_productivity_per_cycle(df):
        cycle_productivity_table = pd.DataFrame(columns=[
            'Cycle (Service No.)', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Total Balance'
        ])
        
        total_connected_all_cycle = 0
        total_ptp_all_cycle = 0
        total_rpc_all_cycle = 0
        total_ptp_amount_all_cycle = 0
        total_balance_all_cycle = 0  # For the total balance

        # Group by Service No. (cycle)
        for service_no, cycle_group in df.groupby('Service No.'):
            total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            
            # Sum Balance only for PTP statuses
            total_balance = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['Balance'] != 0)]['Balance'].sum()

            # Adding the cycle-level productivity data
            cycle_productivity_table = pd.concat([cycle_productivity_table, pd.DataFrame([{
                'Cycle (Service No.)': service_no,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Total Balance': total_balance,  # Only sum the total balance for PTP
            }])], ignore_index=True)

            # Update overall totals for cycles
            total_connected_all_cycle += total_connected
            total_ptp_all_cycle += total_ptp
            total_rpc_all_cycle += total_rpc
            total_ptp_amount_all_cycle += total_ptp_amount
            total_balance_all_cycle += total_balance  # Update total balance for cycles

        # Add a row with total values for cycles
        cycle_productivity_table = pd.concat([cycle_productivity_table, pd.DataFrame([{
            'Cycle (Service No.)': 'Total',
            'Total Connected': total_connected_all_cycle,
            'Total PTP': total_ptp_all_cycle,
            'Total RPC': total_rpc_all_cycle,
            'Total PTP Amount': total_ptp_amount_all_cycle,
            'Total Balance': total_balance_all_cycle,  # Add total balance for cycles
        }])], ignore_index=True)

        return cycle_productivity_table

    # Display the productivity per cycle summary
    st.write("## Productivity Summary per Cycle (Service No.)")
    cycle_productivity_summary = calculate_productivity_per_cycle(df)
    st.write(cycle_productivity_summary)

    col5, col6 = st.columns(2)

    with col5:
        st.write("## Productivity Summary by Collector per Day")
        
        # Add date filter
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

        filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

        collector_productivity_summary = pd.DataFrame(columns=[
            'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
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
                'Balance Amount': total_balance_amount,  # Corrected this part
            }])], ignore_index=True)

            # Update overall totals for collectors
            total_connected_all_collector += total_connected
            total_ptp_all_collector += total_ptp
            total_rpc_all_collector += total_rpc
            total_ptp_amount_all_collector += total_ptp_amount
            total_balance_amount_all_collector += total_balance_amount  # Fixed

        # Add a row with total values for the collector summary
        collector_productivity_summary = pd.concat([collector_productivity_summary, pd.DataFrame([{
            'Day': 'Total',
            'Collector': 'All Collectors',
            'Total Connected': total_connected_all_collector,
            'Total PTP': total_ptp_all_collector,
            'Total RPC': total_rpc_all_collector,
            'Total PTP Amount': total_ptp_amount_all_collector,
            'Balance Amount': total_balance_amount_all_collector,  # Corrected here
        }])], ignore_index=True)

        st.write(collector_productivity_summary)
