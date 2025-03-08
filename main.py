import streamlit as st
import pandas as pd

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

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    
    # Filter out specific users based on 'Remark By'
    exclude_users = ['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
                     'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
                     'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR']
    # Exclude rows where the 'Remark By' column contains any of the above users
    df = df[~df['Remark By'].isin(exclude_users)]
    
    return df

# File uploader for Excel file
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    # Load the data from the uploaded file
    df = load_data(uploaded_file)

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Create the columns layout
    col1, col2 = st.columns(2)

    with col1:
        st.write("## Summary Table by Collector per Day")

        # Group the data by Collector and generate the summary table
        collector_summary = pd.DataFrame(columns=[
            'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
        ])

        # Grouping data by Collector (assuming 'Collector' is the name of the collector column)
        for collector, collector_group in df.groupby('Collector'):
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

            collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

        # Add total row for the summary table by Collector
        totals_row_collector = {
            'Collector': 'Total',
            'Total Connected': collector_summary['Total Connected'].sum(),
            'Total PTP': collector_summary['Total PTP'].sum(),
            'Total RPC': collector_summary['Total RPC'].sum(),
            'PTP Amount': collector_summary['PTP Amount'].sum(),
            'Balance Amount': collector_summary['Balance Amount'].sum(),
        }
        collector_summary = pd.concat([collector_summary, pd.DataFrame([totals_row_collector])], ignore_index=True)

        # Display the collector summary table
        st.write(collector_summary)

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
        for cycle, cycle_group in df.groupby('Service No.'):
            st.write(f"### Summary Table for Cycle: {cycle}")

            # Initialize an empty DataFrame for the summary table by time interval
            cycle_time_summary = pd.DataFrame(columns=[
                'Cycle', 'Time Interval', 'Total Calls', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
            ])

            # Group by Time Interval within the current cycle
            for time_interval, time_interval_group in cycle_group.groupby('Time Interval'):
                # Calculate the metrics for the current time interval and cycle
                total_calls = time_interval_group['Account No.'].count()
                total_connected = time_interval_group[time_interval_group['Call Status'] == 'CONNECTED']['Account No.'].count()
                total_ptp = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['PTP Amount'] != 0)]['Account No.'].nunique()
                total_rpc = time_interval_group[time_interval_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
                ptp_amount = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['PTP Amount'] != 0)]['PTP Amount'].sum()
                balance_amount = time_interval_group[time_interval_group['Status'].str.contains('PTP', na=False) & (time_interval_group['Balance'] != 0)]['Balance'].sum()

                # Add the row to the summary
                cycle_time_summary = pd.concat([cycle_time_summary, pd.DataFrame([{
                    'Cycle': cycle,
                    'Time Interval': time_interval,
                    'Total Calls': total_calls,
                    'Total Connected': total_connected,
                    'Total PTP': total_ptp,
                    'Total RPC': total_rpc,
                    'PTP Amount': ptp_amount,
                    'Balance Amount': balance_amount,
                }])], ignore_index=True)

            # Sort by the time interval to ensure the correct order
            cycle_time_summary['Time Interval'] = pd.Categorical(
                cycle_time_summary['Time Interval'], categories=time_interval_sort_order.keys(), ordered=True)
            cycle_time_summary = cycle_time_summary.sort_values('Time Interval')

            # Add totals row at the bottom for cycle-based summary
            totals_row_cycle = {
                'Cycle': cycle,
                'Time Interval': 'Total',
                'Total Calls': cycle_time_summary['Total Calls'].sum(),
                'Total Connected': cycle_time_summary['Total Connected'].sum(),
                'Total PTP': cycle_time_summary['Total PTP'].sum(),
                'Total RPC': cycle_time_summary['Total RPC'].sum(),
                'PTP Amount': cycle_time_summary['PTP Amount'].sum(),
                'Balance Amount': cycle_time_summary['Balance Amount'].sum(),
            }
            cycle_time_summary = pd.concat([cycle_time_summary, pd.DataFrame([totals_row_cycle])], ignore_index=True)

            # Display the cycle-based summary table
            st.write(cycle_time_summary)
