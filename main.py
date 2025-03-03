import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply dark mode
st.markdown(
    """
    <style>
    .stApp {
        background-color: #2E2E2E;
        color: white;
    }
    .stSidebar {
        background-color: #2E2E2E;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin([
        'FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS',
        'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 
        'MEBEJER', 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 
        'EUGALERA', 'JATERRADO', 'LMLABRADOR'
    ])]  
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure Date is in datetime format
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Exclude 'SYSTEM' and 'system' in the Remark By column
    df = df[~df['Remark By'].str.contains('SYSTEM', case=False, na=False)]

    # --- Productivity Summary per Day ---
    def calculate_productivity_summary(df):
        summary_table = df.groupby(df['Date'].dt.date).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').count()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum')
        ).reset_index()

        # Add total row
        total_row = pd.DataFrame({
            'Date': ['Total'],
            'Total_Connected': [summary_table['Total_Connected'].sum()],
            'Total_PTP': [summary_table['Total_PTP'].sum()],
            'Total_RPC': [summary_table['Total_RPC'].sum()],
            'Total_PTP_Amount': [summary_table['Total_PTP_Amount'].sum()]
        })

        summary_table = pd.concat([summary_table, total_row], ignore_index=True)

        return summary_table

    st.write("## Productivity Summary Table")
    st.write(calculate_productivity_summary(df))

    # --- Productivity Summary per Cycle ---
    def calculate_productivity_per_cycle(df):
        cycle_summary = df.groupby('Service No.').agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').count()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum')
        ).reset_index()

        # Add total row
        total_row = pd.DataFrame({
            'Service No.': ['Total'],
            'Total_Connected': [cycle_summary['Total_Connected'].sum()],
            'Total_PTP': [cycle_summary['Total_PTP'].sum()],
            'Total_RPC': [cycle_summary['Total_RPC'].sum()],
            'Total_PTP_Amount': [cycle_summary['Total_PTP_Amount'].sum()]
        })

        cycle_summary = pd.concat([cycle_summary, total_row], ignore_index=True)

        return cycle_summary

    st.write("## Productivity Summary per Cycle")
    st.write(calculate_productivity_per_cycle(df))

    # --- Productivity Summary per Collector ---
    st.write("## Productivity Summary per Collector")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    collector_summary = filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (filtered_df.loc[x.index, 'Call Status'] == 'CONNECTED').count()),
        Total_PTP=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
        Total_RPC=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', 'sum')  # Balance Amount is unchanged
    ).reset_index()

    # Add total row
    total_row = pd.DataFrame({
        'Date': ['Total'],
        'Remark By': ['All Collectors'],
        'Total_Connected': [collector_summary['Total_Connected'].sum()],
        'Total_PTP': [collector_summary['Total_PTP'].sum()],
        'Total_RPC': [collector_summary['Total_RPC'].sum()],
        'Total_PTP_Amount': [collector_summary['Total_PTP_Amount'].sum()],
        'Balance_Amount': [collector_summary['Balance_Amount'].sum()]  # Keeping balance amount summary unchanged
    })

    collector_summary = pd.concat([collector_summary, total_row], ignore_index=True)

    st.write(collector_summary)
