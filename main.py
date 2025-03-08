import pandas as pd
import streamlit as st

# Function to load the data from an uploaded file
def load_data(uploaded_file):
    return pd.read_excel(uploaded_file)

# File uploader for Excel file
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Ensure 'Time' column is in datetime format
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce').dt.time

    # Create the columns layout
    col1, col2 = st.columns(2)

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
            filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
        else:
            filtered_df = df  # If no date range is selected, show all data

        # Initialize an empty DataFrame for the summary table by collector
        collector_summary = pd.DataFrame(columns=[
            'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount', 'Balance Amount'
        ])

        # Group by 'Date' and 'Remark By' (Collector)
        for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
            # Calculate the metrics
            total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

            # Add the row to the summary
            collector_summary = pd.concat([collector_summary, pd.DataFrame([{
                'Day': date,
                'Collector': collector,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'PTP Amount': ptp_amount,
                'Balance Amount': balance_amount,
            }])], ignore_index=True)

        # Add totals row at the bottom (summing up per collector)
        totals_row = {
            'Day': 'Total',
            'Collector': '',
            'Total Connected': collector_summary['Total Connected'].sum(),
            'Total PTP': collector_summary['Total PTP'].sum(),
            'Total RPC': collector_summary['Total RPC'].sum(),
            'PTP Amount': collector_summary['PTP Amount'].sum(),
            'Balance Amount': collector_summary['Balance Amount'].sum(),
        }
        collector_summary = pd.concat([collector_summary, pd.DataFrame([totals_row])], ignore_index=True)

        # Display the collector-based summary table
        st.write(collector_summary)
