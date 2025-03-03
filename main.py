import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Function to load and clean data
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # Convert "Time" column to datetime (handle missing values)
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')  # 'coerce' turns invalid values into NaT
    df = df.dropna(subset=['Time'])  # Drop rows with NaT time

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
    row_time_str = row_time.strftime('%H:%M:%S')  # Convert to string
    for label, (start, end) in time_intervals.items():
        if start <= row_time_str <= end:
            return label
    return "Outside Hours"

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file:
    df = load_data(uploaded_file)

    # Apply time classification
    df['Time Interval'] = df['Time'].apply(classify_time)

    # Calculate Productivity Summary per Time Interval
    productivity_per_time = df.groupby('Time Interval').agg({
        'Account No.': 'count',
        'PTP Amount': 'sum',
        'Balance': 'sum',
        'Status': lambda x: (x.str.contains('PTP', na=False)).sum(),  # Total PTP count
    }).reset_index()

    # Debugging step: Print column names
    st.write("DEBUG: Columns in productivity_per_time →", productivity_per_time.columns.tolist())

    # Rename Columns (match the exact number of columns in the dataframe)
    productivity_per_time.columns = [
        'Time Interval', 'Total Connected', 'Total PTP Amount', 'Balance Amount', 'Total PTP'
    ]

    # Display the table
    st.write("## Productivity Summary Per Time Interval")
    st.write(productivity_per_time)
