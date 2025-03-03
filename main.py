import streamlit as st
import pandas as pd
import re

# ------------------- PAGE CONFIGURATION -------------------
st.set_page_config(
    layout="wide", 
    page_title="Productivity Dashboard", 
    page_icon="📊", 
    initial_sidebar_state="expanded"
)

# ------------------- GLOBAL STYLING -------------------
st.markdown("""
    <style>
        /* Sidebar styling */
        .stSidebar {
            background-color: black !important;
            padding: 20px;
        }
        .stSidebar .stFileUploader, .stSidebar div {
            color: white !important;
        }

        /* Header Styling */
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(to right, #FFD700, #FFA500);
            color: white;
            font-size: 24px;
            border-radius: 10px;
            font-weight: bold;
        }

        /* Card Design */
        .card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- HEADER -------------------
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)

# ------------------- DATA LOADING FUNCTION -------------------
@st.cache_data
def load_data(uploaded_file):
    """Loads the uploaded Excel file, converts Date column, and excludes specific names."""
    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date is in datetime format
    
    # Names to exclude
    excluded_names = [
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'RALOPE', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER',
        'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'JMBORROMEO', 'EUGALERA', 
        'JATERRADO', 'LMLABRADOR', 'SYSTEM'
    ]
    
    df = df[~df['Remark By'].isin(excluded_names)]  # Exclude rows with specified names
    return df

# ------------------- FILE UPLOADER -------------------
uploaded_file = st.midbar.file_uploader("📂 Upload Daily Remark File", type="xlsx")

# ------------------- MAIN LOGIC -------------------
if uploaded_file:
    df = load_data(uploaded_file)

    # ------------------- PRODUCTIVITY SUMMARY TABLE -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Productivity Summary Table")

    def calculate_productivity_summary(df):
        """Generates a productivity summary grouped by date."""
        summary = df.groupby(df['Date'].dt.date).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        # Add total row
        total_row = summary.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        summary = pd.concat([summary, total_row.to_frame().T], ignore_index=True)

        return summary

    st.dataframe(calculate_productivity_summary(df), width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- PRODUCTIVITY SUMMARY PER CYCLE -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📆 Productivity Summary per Cycle (Grouped by Date)")

    def extract_two_digit_cycle(value):
        """Extracts a two-digit cycle number from the 'Service No.' field."""
        match = re.findall(r'\b\d{2}\b', str(value))
        return match[0] if match else "NO IDENTIFIER OF CYCLE"

    def calculate_productivity_per_cycle(df):
        """Calculates productivity summary grouped by Date and Cycle."""
        df['Service No.'] = df['Service No.'].astype(str)
        df['Cycle'] = df['Service No.'].apply(extract_two_digit_cycle)

        cycle_summary = df.groupby([df['Date'].dt.date, 'Cycle']).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        # Add total row
        total_row = cycle_summary.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        total_row['Cycle'] = 'ALL CYCLES'
        cycle_summary = pd.concat([cycle_summary, total_row.to_frame().T], ignore_index=True)

        return cycle_summary

    st.dataframe(calculate_productivity_per_cycle(df), width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # ------------------- PRODUCTIVITY SUMMARY PER COLLECTOR -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 Productivity Summary per Collector")

    # Date range selection
    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input(
        "📅 Select date range", 
        [min_date, max_date], 
        min_value=min_date, 
        max_value=max_date
    )

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    # Exclude system-generated remarks
    filtered_df = filtered_df[~filtered_df['Remark By'].str.upper().isin(["SYSTEM"])]

    def calculate_productivity_per_collector(df):
        """Generates a productivity summary grouped by Date and Collector."""
        collector_summary = df.groupby([df['Date'].dt.date, 'Remark By']).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        # Add total row
        total_row = collector_summary.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        total_row['Remark By'] = 'ALL COLLECTORS'
        collector_summary = pd.concat([collector_summary, total_row.to_frame().T], ignore_index=True)

        return collector_summary

    st.dataframe(calculate_productivity_per_collector(filtered_df), width=1500)
    st.markdown('</div>', unsafe_allow_html=True)
