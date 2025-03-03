import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Function to load and clean data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 
        'GPRAMOS', 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 
        'RRCARLIT', 'MEBEJER', 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 
        'EASORIANO', 'EUGALERA', 'JATERRADO', 'LMLABRADOR'
    ])]  # Exclude specific "Remark By"
    
    # Convert "Time" column to datetime format
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.time  # Ensures it's time-based
    return df

# Define Time Intervals
time_intervals = {
    '6:00 AM - 8:00 AM': ('06:00:00', '08:00:00'),
    '8:01 AM - 9:00 AM': ('08:01:00', '09:00:00'),
    '9:01 AM - 10:00 AM': ('09:01:00', '10:00:00'),
    '10:01 AM - 12:00 PM': ('10:01:00', '12:00:00'),
    '12:01 PM - 2:00 PM': ('12:01:00', '14:00:00'),
    '2:01 PM - 4:00 PM': ('14:01:00', '16:00:00'),
    '4:01 PM - 6:00 PM': ('16:01:00', '18:00:00'),
    '6:01 PM - 8:00 PM': ('18:01:00', '20:00:00')
}

# Function to classify time into intervals
def classify_time(row_time):
    for label, (start, end) in time_intervals.items():
        if start <= row_time.strftime('%H:%M:%S') <= end:
            return label
    return "Outside Hours"

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file:
    df = load_data(uploaded_file)

    # Classify each entry into a time interval
    df['Time Interval'] = df['Time'].apply(classify_time)

    # Calculate Productivity Summary per Time Interval
    productivity_per_time = df.groupby('Time Interval').agg({
        'Account No.': 'count',
        'Status': lambda x: (x.str.contains('PTP', na=False) & df['PTP Amount'].ne(0)).sum(),
        'Status': lambda x: (x.str.contains('RPC', na=False)).sum(),
        'PTP Amount': 'sum',
        'Balance': 'sum'
    }).reset_index()

    # Rename Columns
    productivity_per_time.columns = [
        'Time Interval', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
    ]

    # Display the table
    st.write("## Productivity Summary Per Time Interval")
    st.write(productivity_per_time)
