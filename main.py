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
        'JATERRADO', 'LMLABRADOR', 'EASORIANO'
    ]
    
    df = df[~df['Remark By'].isin(excluded_names)]  # Exclude rows with specified names
    return df

# ------------------- FILE UPLOADER -------------------
uploaded_file = st.sidebar.file_uploader("📂 Upload Daily Remark File", type="xlsx")

# ------------------- MAIN LOGIC -------------------
if uploaded_file:
    df = load_data(uploaded_file)

    # ------------------- PRODUCTIVITY SUMMARY TABLE -------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Productivity Summary Table")

    def calculate_productivity_summary(df):
        """Generates a productivity summary grouped by date."""
        df_filtered = df[df['Remark By'].str.upper() != "SYSTEM"]
        summary = df_filtered.groupby(df_filtered['Date'].dt.date).agg(
            Total_Connected=('Account No.', lambda x: (df_filtered.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df_filtered.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df_filtered.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df_filtered.loc[x.index, 'Balance'][df_filtered.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        # Add total row
        total_row = summary.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        summary = pd.concat([summary, total_row.to_frame().T], ignore_index=True)

        return summary

    st.dataframe(calculate_productivity_summary(df), width=1500)
    st.markdown('</div>', unsafe_allow_html=True)
