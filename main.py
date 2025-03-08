# In your existing Streamlit app

# Create time intervals based on the "Time" column
with col1:
    st.write("## Summary Table by Time Interval per Day")

    # Define time intervals (6 AM - 6:59 AM, 7 AM - 7:59 AM, etc.)
    time_bins = [
        ("12 AM - 5:59 AM", "00:00:00", "06:59:59"),
        ("6 AM - 6:59 AM", "06:00:00", "06:59:59"),
        ("7 AM - 7:59 AM", "07:00:00", "07:59:59"),
        ("8 AM - 8:59 AM", "08:00:00", "08:59:59"),
        ("9 AM - 9:59 AM", "09:00:00", "09:59:59"),
        ("10 AM - 10:59 AM", "10:00:00", "10:59:59"),
        ("11 AM - 11:59 AM", "11:00:00", "11:59:59"),
        ("12 PM - 12:59 PM", "12:00:00", "12:59:59"),
        ("1 PM - 1:59 PM", "13:00:00", "13:59:59"),
        ("2 PM - 2:59 PM", "14:00:00", "14:59:59"),
        ("3 PM - 3:59 PM", "15:00:00", "15:59:59"),
        ("4 PM - 4:59 PM", "16:00:00", "16:59:59"),
        ("5 PM - 5:59 PM", "17:00:00", "17:59:59"),
        ("6 PM - 6:59 PM", "18:00:00", "18:59:59"),
        ("7 PM - 7:59 PM", "19:00:00", "19:59:59"),
        ("8 PM - 8:59 PM", "20:00:00", "20:59:59"),
        ("9 PM - 9:59 PM", "21:00:00", "21:59:59"),
        ("10 PM - 10:59 PM", "22:00:00", "22:59:59"),
        ("11 PM - 11:59 PM", "23:00:00", "23:59:59")
    ]

    # Create a function to assign each row to a time interval
    def assign_time_interval(time_str):
        for label, start, end in time_bins:
            if start <= time_str <= end:
                return label
        return "Out of Range"  # Default if no match found

    # Apply the time interval categorization based on the "Time" column
    df['Time Interval'] = df['Time'].apply(assign_time_interval)

    # Filter data based on the selected date range or show all if no date range is selected
    if start_date and end_date:
        filtered_time_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    else:
        filtered_time_df = df  # If no date range is selected, show all data

    # Initialize an empty DataFrame for the summary table by time interval
    time_summary = pd.DataFrame(columns=[
        'Day', 'Time Interval', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
    ])

    # Group by 'Date' and 'Time Interval'
    for (date, time_interval), time_group in filtered_time_df.groupby([filtered_time_df['Date'].dt.date, 'Time Interval']):
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

    st.write(time_summary)
