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
    
    # Convert Date & Time columns to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time  # Convert time to proper format
    
    # Filter out specific "Remark By" values
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
        'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR'
    ])]  
    return df

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Function to calculate productivity summary
    def calculate_productivity_summary(df):
        productivity_table = pd.DataFrame(columns=['Day', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount'])

        for date, group in df.groupby(df['Date'].dt.date):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()

            productivity_table = pd.concat([productivity_table, pd.DataFrame([{
                'Day': date,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
            }])], ignore_index=True)

        return productivity_table

    # Display the productivity summary
    st.write("## Productivity Summary Table")
    st.write(calculate_productivity_summary(df))

    # Function to calculate productivity per time slot
    def calculate_productivity_per_time_slot(df):
        df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour  # Extract hour from Time column

        # Define time slots
        bins = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
        labels = [
            '8:00-9:00 AM', '9:01-10:00 AM', '10:01-11:00 AM', '11:01-12:00 PM', 
            '12:01-1:00 PM', '1:01-2:00 PM', '2:01-3:00 PM', '3:01-4:00 PM', 
            '4:01-5:00 PM', '5:01-6:00 PM', '6:01-7:00 PM', '7:01-8:00 PM', '8:01-9:00 PM'
        ]

        df['Time Slot'] = pd.cut(df['Hour'], bins=bins, labels=labels, right=False)

        # Aggregate data based on time slot
        time_productivity_table = df.groupby(['Date', 'Time Slot']).agg(
            Total_Connected=('Account No.', lambda x: (df['Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: ((df['Status'].str.contains('PTP', na=False)) & (df['PTP Amount'] != 0)).sum()),
            Total_RPC=('Account No.', lambda x: (df['Status'].str.contains('RPC', na=False)).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum')
        ).reset_index()

        return time_productivity_table

    # Display the productivity per time slot
    st.write("## Productivity Summary by Time Slot")
    st.write(calculate_productivity_per_time_slot(df))

    # --- Productivity Summary by Collector ---
    st.write("## Productivity Summary by Collector per Day")
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    collector_productivity_summary = filtered_df.groupby(['Date', 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (filtered_df['Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: ((filtered_df['Status'].str.contains('PTP', na=False)) & (filtered_df['PTP Amount'] != 0)).sum()),
        Total_RPC=('Account No.', lambda x: (filtered_df['Status'].str.contains('RPC', na=False)).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum')
    ).reset_index()

    st.write(collector_productivity_summary)
