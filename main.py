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

# Sample data loading function (you can replace it with your actual data loading logic)
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

    with col1:
        st.write("## Summary Table by Time Interval per Day")

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

        # Function to categorize the time into the intervals
        def categorize_time_interval(time_obj):
            # Handle cases where time_obj is NaT (invalid or missing)
            if pd.isna(time_obj):
                return "Invalid Time"
            
            # Ensure the input time is in the correct format (datetime.time)
            if isinstance(time_obj, pd.Timestamp):
                time_obj = time_obj.time()
                
            for label, start, end in time_bins:
                # Compare time objects
                if start <= time_obj <= end:
                    return label
            return "Out of Range"  # For times outside the specified intervals

        # Apply categorization based on the existing "Time" column
        df['Time Interval'] = df['Time'].apply(categorize_time_interval)

        # Initialize an empty DataFrame for the summary table by time interval
        time_summary = pd.DataFrame(columns=[
            'Day', 'Time Interval', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
        ])

        # Filter the data (if necessary based on the selected date range, etc.)
        filtered_df = df  # Use the whole DataFrame or filter based on your criteria

        # Group by 'Date' and 'Time Interval'
        for (date, time_interval), time_group in filtered_df.groupby([filtered_df['Date'].dt.date, 'Time Interval']):
            # Calculate the metrics
            total_connected = time_group[time_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = time_group[time_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = time_group[time_group['Status'].str.contains('PTP', na=False) & (time_group['Balance'] != 0)]['Balance'].sum()

            # Add the row to the summary
            time_summary = pd.concat([time_summary, pd.DataFrame([{
                'Day': date,
                'Time Interval': time_interval,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

        # Add totals row at the bottom for time-based summary
        totals_row_time = {
            'Day': 'Total',
            'Time Interval': '',
            'Total Connected': time_summary['Total Connected'].sum(),
            'Total PTP': time_summary['Total PTP'].sum(),
            'Total RPC': time_summary['Total RPC'].sum(),
            'PTP Amount': time_summary['PTP Amount'].sum(),
            'Balance Amount': time_summary['Balance Amount'].sum(),
        }
        time_summary = pd.concat([time_summary, pd.DataFrame([totals_row_time])], ignore_index=True)

        # Display the time summary table
        st.write(time_summary)

    with col2:
        st.write("## Summary Table by Time Interval per Cycle")

        # Initialize an empty DataFrame for the summary table by time interval per cycle
        cycle_time_summary = pd.DataFrame(columns=[
            'Cycle', 'Time Interval', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
        ])

        # Group by 'Service No.' (Cycle) and 'Time Interval'
        for (cycle, time_interval), cycle_time_group in df.groupby(['Service No.', 'Time Interval']):
            # Calculate the metrics
            total_connected = cycle_time_group[cycle_time_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = cycle_time_group[cycle_time_group['Status'].str.contains('PTP', na=False) & (cycle_time_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = cycle_time_group[cycle_time_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = cycle_time_group[cycle_time_group['Status'].str.contains('PTP', na=False) & (cycle_time_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = cycle_time_group[cycle_time_group['Status'].str.contains('PTP', na=False) & (cycle_time_group['Balance'] != 0)]['Balance'].sum()

            # Add the row to the summary
            cycle_time_summary = pd.concat([cycle_time_summary, pd.DataFrame([{
                'Cycle': cycle,
                'Time Interval': time_interval,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

        # Add totals row at the bottom for cycle-based summary
        totals_row_cycle = {
            'Cycle': 'Total',
            'Time Interval': '',
            'Total Connected': cycle_time_summary['Total Connected'].sum(),
            'Total PTP': cycle_time_summary['Total PTP'].sum(),
            'Total RPC': cycle_time_summary['Total RPC'].sum(),
            'PTP Amount': cycle_time_summary['PTP Amount'].sum(),
            'Balance Amount': cycle_time_summary['Balance Amount'].sum(),
        }
        cycle_time_summary = pd.concat([cycle_time_summary, pd.DataFrame([totals_row_cycle])], ignore_index=True)

        # Display the cycle time summary table
        st.write(cycle_time_summary)
