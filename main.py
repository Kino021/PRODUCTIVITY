import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply global styling
st.markdown(
    """
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

    /* Dataframe Styling */
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# HEADER
st.markdown('<div class="header">📊 PRODUCTIVITY DASHBOARD</div>', unsafe_allow_html=True)

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

uploaded_file = st.sidebar.file_uploader("📂 Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    # Exclude 'SYSTEM' and 'system' in the Remark By column
    df = df[~df['Remark By'].str.contains('SYSTEM', case=False, na=False)]

    # --- Productivity Summary Table ---
    def calculate_productivity_summary(df):
        summary_table = df.groupby(df['Date'].dt.date).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        total_row = summary_table.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        summary_table = pd.concat([summary_table, total_row.to_frame().T], ignore_index=True)

        return summary_table

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## 📊 Productivity Summary Table")
    st.dataframe(calculate_productivity_summary(df), width=1500)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Productivity Summary per Cycle (Grouped by Date) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## 📆 Productivity Summary per Cycle (Grouped by Date)")

    def calculate_productivity_per_cycle(df):
        df['Service No.'] = df['Service No.'].astype(str)
        df['Cycle'] = df['Service No.'].apply(lambda x: x if x.isnumeric() else "NO IDENTIFIER OF CYCLE")
        
        cycle_summary = df.groupby([df['Date'].dt.date, 'Cycle']).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        return cycle_summary

    cycle_summary = calculate_productivity_per_cycle(df)
    unique_dates = cycle_summary['Date'].unique()
    
    for i in range(0, len(unique_dates), 2):
        cols = st.columns(2)
        with cols[0]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"### 📅 Date: {unique_dates[i]}")
            st.dataframe(cycle_summary[cycle_summary['Date'] == unique_dates[i]], width=700)
            st.markdown('</div>', unsafe_allow_html=True)
        if i + 1 < len(unique_dates):
            with cols[1]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"### 📅 Date: {unique_dates[i + 1]}")
                st.dataframe(cycle_summary[cycle_summary['Date'] == unique_dates[i + 1]], width=700)
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---")  # Spacer for clarity
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Productivity Summary per Collector ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("## 👤 Productivity Summary per Collector")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input("📅 Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    collector_summary = filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (filtered_df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
        Total_RPC=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', lambda x: filtered_df.loc[x.index, 'Balance'][filtered_df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
    ).reset_index()

    st.dataframe(collector_summary, width=1500)
    st.markdown('</div>', unsafe_allow_html=True)
