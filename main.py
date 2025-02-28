import streamlit as st
import pandas as pd

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

st.title('Daily Remark Summary - Productivity Only')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR'])]  # Exclude specific Remark By
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Function to calculate the summary (your existing summary calculation function)
    def calculate_summary(group, type_column, filter_value=None):
        if filter_value:
            group = group[group['Status'].str.contains(filter_value, na=False)]
        
        summary_data = group.groupby([type_column]).agg(
            Total_Connected=('Account No.', 'count'),
            Total_PTP=('PTP Amount', 'sum'),
            Total_RPC=('RPC Amount', 'sum')
        ).reset_index()
        
        return summary_data

    # Extract the first two characters from the 'Card No.' to create new grouping columns
    df['Card No. Prefix'] = df['Card No.'].str[:2]

    col3, col4 = st.columns(2)

    with col3:
        st.write("## Summary Table by Cycle Predictive")
        for cycle, cycle_group in df.groupby('Card No. Prefix'):  # Group by the first 2 letters/numbers of 'Card No.'
            st.write(f"Cycle: {cycle}")
            summary_table = calculate_summary(cycle_group, 'Predictive', 'SYSTEM')
            st.write(summary_table)

    with col4:
        st.write("## Summary Table by Cycle Manual")
        for manual_cycle, manual_cycle_group in df.groupby('Card No. Prefix'):  # Group by the first 2 letters/numbers of 'Card No.'
            st.write(f"Cycle: {manual_cycle}")
            summary_table = calculate_summary(manual_cycle_group, 'Outgoing')
            st.write(summary_table)
