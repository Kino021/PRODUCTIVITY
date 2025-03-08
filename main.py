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
        st.write("## Full Data Summary")

        # Define time intervals (6 AM - 6:59 AM, 7 AM - 7:59 AM, etc.)
        time_bins = [
            ("6 AM - 6:59 AM", pd.to_datetime("06:00:00").time(), pd.to_datetime("06:59:59").time()),
            ("7 AM - 7:59 AM", pd.to_datetime("07:00:00").time(), pd.to_datetime("07:59:59").time()),
            ("8 AM - 8:59 AM", pd.to_datetime("08:00:00").time(), pd.to_datetime("08:59:59").time()),
            ("9 AM - 9:59 AM", pd.to_datetime("09:00:00").time(), pd.to_datetime("09:59:59").time()),
            ("10 AM - 10:59 AM", pd.to_datetime("10:00:00").time(), pd.to_datetime("10:59:59").time()),
            ("11 AM - 11:59 AM", pd.to_datetime("11:00:00").time(), pd.to_datetime("11:59:59").time()),
            ("12 PM - 12:59 PM", pd.to_datetime("12:00:00").time(), pd.to_datetime("12:59:59").time()),
            ("1 PM - 1:59 PM", pd.to_datetime("13:00:00").time(), pd.to_datetime("13:59:59").time()),
            ("2 PM - 2:59 PM", pd.to_datetime("14:00:00").time(), pd.to_datetime("14:59:59").time()),
            ("3 PM - 3:59 PM", pd.to_datetime("15:00:00").time(), pd.to_datetime("15:59:59").time()),
            ("4 PM - 4:59 PM", pd.to_datetime("16:00:00").time(), pd.to_datetime("16:59:59").time()),
            ("5 PM - 5:59 PM", pd.to_datetime("17:00:00").time(), pd.to_datetime("17:59:59").time()),
            ("6 PM - 6:59 PM", pd.to_datetime("18:00:00").time(), pd.to_datetime("18:59:59").time()),
            ("7 PM - 7:59 PM", pd.to_datetime("19:00:00").time(), pd.to_datetime("19:59:59").time()),
            ("8 PM - 8:59 PM", pd.to_datetime("20:00:00").time(), pd.to_datetime("20:59:59").time()),
            ("9 PM - 9:59 PM", pd.to_datetime("21:00:00").time(), pd.to_datetime("21:59:59").time()),
            ("10 PM - 10:59 PM", pd.to_datetime("22:00:00").time(), pd.to_datetime("22:59:59").time()),
            ("11 PM - 11:59 PM", pd.to_datetime("23:00:00").time(), pd.to_datetime("23:59:59").time())
        ]

        # Create a dictionary to map time intervals to sortable integers
        time_interval_sort_order = {time[0]: i for i, time in enumerate(time_bins)}

        # Function to categorize the time into the intervals
        def categorize_time_interval(time_obj):
            if pd.isna(time_obj):
                return "Invalid Time"
            if isinstance(time_obj, pd.Timestamp):
                time_obj = time_obj.time()
            for label, start, end in time_bins:
                if start <= time_obj <= end:
                    return label
            return "Out of Range"

        # Apply categorization based on the existing "Time" column
        df['Time Interval'] = df['Time'].apply(categorize_time_interval)

        # Define a function to calculate performance metrics for each group
        def calculate_metrics(group):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = group[group['Status'].str.contains('PTP', na=False) & (group['Balance'] != 0)]['Balance'].sum()
            return total_connected, total_ptp, total_rpc, ptp_amount, balance_amount

        # Per Collector Summary
        st.write("### Summary per Collector")
        collector_summary = df.groupby('Collector').apply(lambda group: pd.Series(calculate_metrics(group), index=[
            'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])).reset_index()
        st.write(collector_summary)

        # Per Cycle Summary
        st.write("### Summary per Cycle")
        cycle_summary = df.groupby('Service No.').apply(lambda group: pd.Series(calculate_metrics(group), index=[
            'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])).reset_index()
        st.write(cycle_summary)

        # Per Time Interval Summary
        st.write("### Summary per Time Interval")
        time_interval_summary = df.groupby('Time Interval').apply(lambda group: pd.Series(calculate_metrics(group), index=[
            'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])).reset_index()
        st.write(time_interval_summary)

        # Per Time and Collector Summary
        st.write("### Summary per Time Interval and Collector")
        time_collector_summary = df.groupby(['Time Interval', 'Collector']).apply(lambda group: pd.Series(calculate_metrics(group), index=[
            'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'])).reset_index()
        st.write(time_collector_summary)
