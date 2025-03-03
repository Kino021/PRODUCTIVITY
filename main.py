import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="PRODUCTIVITY", page_icon="📊", initial_sidebar_state="expanded")

# Apply blue background for the main app and red for the sidebar
st.markdown(
    """
    <style>
    .stApp {
        background-color: #CCE5FF;
        color: black;
    }
    .stSidebar {
        background-color: #FFCCCC;
    }
    .spacer {
        height: 30px;
    }
    .full-width {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .two-column {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
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

    # --- Productivity Summary Table ---
    def calculate_productivity_summary(df):
        summary_table = df.groupby(df['Date'].dt.date).agg(
            Total_Connected=('Account No.', lambda x: (df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
            Total_PTP=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
            Total_RPC=('Account No.', lambda x: df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
            Total_PTP_Amount=('PTP Amount', 'sum'),
            Balance_Amount=('Balance', lambda x: df.loc[x.index, 'Balance'][df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
        ).reset_index()

        # Add total row
        total_row = summary_table.sum(numeric_only=True)
        total_row['Date'] = 'Total'
        summary_table = pd.concat([summary_table, total_row.to_frame().T], ignore_index=True)

        return summary_table

    st.write("## Productivity Summary Table")
    st.dataframe(calculate_productivity_summary(df), width=1500)

    # --- Productivity Summary per Cycle (Grouped by Date in Two Columns) ---
    st.write("## Productivity Summary per Cycle (Grouped by Date)")
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
            st.write(f"### Date: {unique_dates[i]}")
            st.dataframe(cycle_summary[cycle_summary['Date'] == unique_dates[i]], width=700)
        if i + 1 < len(unique_dates):
            with cols[1]:
                st.write(f"### Date: {unique_dates[i + 1]}")
                st.dataframe(cycle_summary[cycle_summary['Date'] == unique_dates[i + 1]], width=700)
        st.markdown("---")  # Spacer for clarity

    # --- Productivity Summary per Collector ---
    st.write("## Productivity Summary per Collector")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    start_date, end_date = st.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]

    collector_summary = filtered_df.groupby([filtered_df['Date'].dt.date, 'Remark By']).agg(
        Total_Connected=('Account No.', lambda x: (filtered_df.loc[x.index, 'Call Status'] == 'CONNECTED').sum()),
        Total_PTP=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('PTP', na=False).sum()),
        Total_RPC=('Account No.', lambda x: filtered_df.loc[x.index, 'Status'].str.contains('RPC', na=False).sum()),
        Total_PTP_Amount=('PTP Amount', 'sum'),
        Balance_Amount=('Balance', lambda x: filtered_df.loc[x.index, 'Balance'][filtered_df.loc[x.index, 'Status'].str.contains('PTP', na=False)].sum())
    ).reset_index()

    # Add total row
    total_row = collector_summary.sum(numeric_only=True)
    total_row['Date'] = 'Total'
    total_row['Remark By'] = 'All Collectors'
    collector_summary = pd.concat([collector_summary, total_row.to_frame().T], ignore_index=True)

    st.dataframe(collector_summary, width=1500)
