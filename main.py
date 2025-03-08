import pandas as pd
import streamlit as st

# Set up the page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode styling
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

# Sample data loading function (replace with your actual data loading logic)
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

# File uploader for Excel file
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Create the columns layout
    col1, col2 = st.columns(2)

    with col2:
        st.write("## Per Collector Summary")

        # Define a function to calculate performance metrics for each group
        def calculate_metrics(group):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = group[group['Status'].str.contains('PTP', na=False) & (group['Balance'] != 0)]['Balance'].sum()
            return total_connected, total_ptp, total_rpc, ptp_amount, balance_amount

        # Per Collector Summary
        collector_summary = df.groupby('Collector').apply(lambda group: pd.Series(calculate_metrics(group), index=[
            'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])).reset_index()

        # Show the summary in Streamlit
        st.write(collector_summary)
