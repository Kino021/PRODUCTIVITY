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

    # Ensure 'Time' column is in datetime format and handle errors
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time
    else:
        st.error("The 'Time' column is missing or has an invalid format.")
        st.stop()

    # Ensure necessary columns exist
    required_columns = ['Time', 'Service No.', 'Call Status', 'Account No.', 'Status', 'PTP Amount', 'Balance', 'Date', 'Remark By']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            st.stop()

    # Create the columns layout
    col1, col2 = st.columns(2)

    with col2:
        st.write("## Summary Table by Time Interval per Cycle")

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

        # Group the data by Cycle (Service No.) and generate separate tables
        summary_data = []  # Store summary data in a list for better performance
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"### Summary Table for Cycle: {cycle}")

            # Group by Time Interval within the current cycle
            for time_interval, time_interval_group in cycle_group.groupby('Time Interval'):
                # Calculate the metrics for the current time interval and cycle
                total_connected = time_interval_group[time_interval_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                total_ptp = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['PTP Amount'] != 0)]['Account No.'].nunique()
                total_rpc = time_interval_group[time_interval_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
                ptp_amount = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['PTP Amount'] != 0)]['PTP Amount'].sum()
                balance_amount = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['Balance'] != 0)]['Balance'].sum()

                # Add the row to the summary
                summary_data.append({
                    'Cycle': cycle,
                    'Time Interval': time_interval,
                    'Total Connected': total_connected,
                    'Total PTP': total_ptp,
                    'Total RPC': total_rpc,
                    'PTP Amount': ptp_amount,
                    'Balance Amount': balance_amount,
                })

        # Convert summary data to DataFrame
        cycle_time_summary = pd.DataFrame(summary_data)

        # Sort by the time interval to ensure the correct order
        cycle_time_summary['Time Interval'] = pd.Categorical(
            cycle_time_summary['Time Interval'], categories=time_interval_sort_order.keys(), ordered=True)
        cycle_time_summary = cycle_time_summary.sort_values('Time Interval')

        # Add totals row at the bottom for cycle-based summary
        totals_row_cycle = {
            'Cycle': 'Total',
            'Time Interval': 'Total',
            'Total Connected': cycle_time_summary['Total Connected'].sum(),
            'Total PTP': cycle_time_summary['Total PTP'].sum(),
            'Total RPC': cycle_time_summary['Total RPC'].sum(),
            'PTP Amount': cycle_time_summary['PTP Amount'].sum(),
            'Balance Amount': cycle_time_summary['Balance Amount'].sum(),
        }
        cycle_time_summary = pd.concat([cycle_time_summary, pd.DataFrame([totals_row_cycle])], ignore_index=True)

        # Display the cycle-based summary table
        st.write(cycle_time_summary)

    with col1:
        st.write("## Summary Table by Collector per Day")

        # Add date filter for Collector Table
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()

        try:
            # Add date range selection for Collector table
            start_date, end_date = st.date_input("Select date range for Collector", [min_date, max_date], min_value=min_date, max_value=max_date)
        except ValueError:
            start_date, end_date = None, None

        # Filter data based on the selected date range or show all if no date range is selected
        if start_date and end_date:
            filtered_data = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
        else:
            filtered_data = df

        # Group by Collector (Remark By) and generate summary
        collector_summary = []
        for collector, collector_group in filtered_data.groupby('Remark By'):
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

            collector_summary.append({
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            })

        # Convert to DataFrame and display
        collector_summary_df = pd.DataFrame(collector_summary)
        st.write(collector_summary_df)
