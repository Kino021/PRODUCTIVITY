import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode styling
st.markdown(
    """
    <style>
    .main {
        background-color: #2E2E2E;
        color: white;
    }
    .stSidebar {
        background-color: #2E2E2E;
    }
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data(uploaded_file):
    """Loads Excel file and filters out specific users."""
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Convert to datetime

        excluded_users = [
            'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ',
            'GPRAMOS', 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA',
            'RRCARLIT', 'MEBEJER', 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO',
            'EASORIANO', 'EUGALERA', 'JATERRADO', 'LMLABRADOR'
        ]
        df = df[~df['Remark By'].isin(excluded_users)]
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Function to calculate productivity summary
    def calculate_productivity_summary(df):
        """Computes daily productivity summary."""
        productivity_table = pd.DataFrame(columns=[
            'Day', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
        ])

        total_connected_all = 0
        total_ptp_all = 0
        total_rpc_all = 0
        total_ptp_amount_all = 0
        total_balance_amount_all = 0

        for date, group in df.groupby(df['Date'].dt.date):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance_amount = group[group['Status'].str.contains('PTP', na=False) & (group['Balance'] != 0)]['Balance'].sum()

            # Append data to DataFrame
            productivity_table = pd.concat([productivity_table, pd.DataFrame([{
                'Day': date,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Balance Amount': total_balance_amount
            }])], ignore_index=True)

            # Update totals
            total_connected_all += total_connected
            total_ptp_all += total_ptp
            total_rpc_all += total_rpc
            total_ptp_amount_all += total_ptp_amount
            total_balance_amount_all += total_balance_amount

        # Add total row
        productivity_table = pd.concat([productivity_table, pd.DataFrame([{
            'Day': 'Total',
            'Total Connected': total_connected_all,
            'Total PTP': total_ptp_all,
            'Total RPC': total_rpc_all,
            'Total PTP Amount': total_ptp_amount_all,
            'Balance Amount': total_balance_amount_all
        }])], ignore_index=True)

        return productivity_table

    # Display the productivity summary
    st.write("## Productivity Summary Table")
    productivity_summary_table = calculate_productivity_summary(df)
    st.write(productivity_summary_table)

    # --- Calculate Productivity per Cycle ---
    def calculate_productivity_per_cycle(df):
        """Computes productivity per Service No. (Cycle)."""
        cycle_productivity_table = pd.DataFrame(columns=[
            'Cycle (Service No.)', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
        ])

        for service_no, cycle_group in df.groupby('Service No.'):
            total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['Balance'] != 0)]['Balance'].sum()

            # Append data to DataFrame
            cycle_productivity_table = pd.concat([cycle_productivity_table, pd.DataFrame([{
                'Cycle (Service No.)': service_no,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Balance Amount': total_balance_amount
            }])], ignore_index=True)

        return cycle_productivity_table

    # Display the productivity per cycle summary
    st.write("## Productivity Summary per Cycle (Service No.)")
    cycle_productivity_summary = calculate_productivity_per_cycle(df)
    st.write(cycle_productivity_summary)

    # --- Productivity Summary by Collector per Day ---
    st.write("## Productivity Summary by Collector per Day")

    # Add date filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    # Group by Date & Collector
    collector_summary = filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']).agg({
        'Account No.': 'count',
        'PTP Amount': 'sum',
        'Balance': 'sum'
    }).reset_index()

    collector_summary.columns = ['Day', 'Collector', 'Total Connected', 'Total PTP Amount', 'Balance Amount']
    
    st.write(collector_summary)
