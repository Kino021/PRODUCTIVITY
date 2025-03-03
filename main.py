import streamlit as st
import pandas as pd

# Set up page configuration
st.set_page_config(layout="wide", page_title="PL XDAYS REPORT", page_icon="📊", initial_sidebar_state="expanded")

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

st.title('Daily Remark Summary')

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_excel(uploaded_file)
    df = df[~df['Remark By'].isin(['FGPANGANIBAN', 'KPILUSTRISIMO', 'BLRUIZ', 'MMMEJIA', 'SAHERNANDEZ', 'GPRAMOS'
                                   , 'JGCELIZ', 'JRELEMINO', 'HVDIGNOS', 'SPMADRID', 'DRTORRALBA', 'RRCARLIT', 'MEBEJER'
                                   , 'DASANTOS', 'SEMIJARES', 'GMCARIAN', 'RRRECTO', 'EASORIANO', 'EUGALERA','JATERRADO','LMLABRADOR'])]  
    return df

uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    st.write(df)

    # Updated function to calculate and display productivity
    def calculate_productivity_summary(df):
        productivity_table = pd.DataFrame(columns=[
            'Day', 'Accounts', 'Total Dialed', 'Penetration Rate (%)', 'Connected #', 
            'Connected Rate (%)', 'Connected Accounts', 'PTP Accounts', 'PTP Rate', 'Call Drop #', 'Call Drop Ratio'
        ])

        for date, group in df.groupby(df['Date'].dt.date):
            accounts = group[group['Remark'] != 'Broken Promise']['Account No.'].nunique()
            total_dialed = group[group['Remark'] != 'Broken Promise']['Account No.'].count()

            connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            connected_rate = (connected / total_dialed * 100) if total_dialed != 0 else None
            connected_accounts = group[group['Call Status'] == 'CONNECTED']['Account No.'].nunique()

            penetration_rate = (total_dialed / accounts * 100) if accounts != 0 else None

            ptp_accounts = group[(group['Status'].str.contains('PTP', na=False)) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            ptp_rate = (ptp_accounts / connected_accounts * 100) if connected_accounts != 0 else None

            call_drop_count = group[group['Call Status'] == 'DROPPED']['Account No.'].count()
            call_drop_ratio = (call_drop_count / connected * 100) if connected != 0 else None

            productivity_table = pd.concat([productivity_table, pd.DataFrame([{
                'Day': date,
                'Accounts': accounts,
                'Total Dialed': total_dialed,
                'Penetration Rate (%)': f"{round(penetration_rate)}%" if penetration_rate is not None else None,
                'Connected #': connected,
                'Connected Rate (%)': f"{round(connected_rate)}%" if connected_rate is not None else None,
                'Connected Accounts': connected_accounts,
                'PTP Accounts': ptp_accounts,
                'PTP Rate': f"{round(ptp_rate)}%" if ptp_rate is not None else None,
                'Call Drop #': call_drop_count,
                'Call Drop Ratio': f"{round(call_drop_ratio)}%" if call_drop_ratio is not None else None,
            }])], ignore_index=True)

        return productivity_table

    # Show productivity summary table with a refined look
    st.write("## Overall Productivity Summary")
    productivity_summary = calculate_productivity_summary(df)
    st.dataframe(productivity_summary.style.format({
        'Penetration Rate (%)': '{:.2f}%',
        'Connected Rate (%)': '{:.2f}%',
        'PTP Rate': '{:.2f}%',
        'Call Drop Ratio': '{:.2f}%'
    }).background_gradient(cmap='coolwarm', axis=0), width=1400)

    # Table by date range filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    st.write(f"### Filtered Data from {start_date} to {end_date}")
    st.dataframe(filtered_df)

    # Display detailed table by Collector per Day
    st.write("## Summary Table by Collector per Day")
    collector_summary = pd.DataFrame(columns=[
        'Day', 'Collector', 'Total Connected', 'Total PTP', 'Total RPC', 'PTP Amount'
    ])

    for (date, collector), collector_group in filtered_df[~filtered_df['Remark By'].str.upper().isin(['SYSTEM'])].groupby([filtered_df['Date'].dt.date, 'Remark By']):
        total_connected = collector_group[collector_group['Call Status'] == 'CONNECTED']['Account No.'].count()
        total_ptp = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['Account No.'].nunique()
        total_rpc = collector_group[collector_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
        ptp_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['PTP Amount'] != 0)]['PTP Amount'].sum()
        balance_amount = collector_group[collector_group['Status'].str.contains('PTP', na=False) & (collector_group['Balance'] != 0)]['Balance'].sum()

        collector_summary = pd.concat([collector_summary, pd.DataFrame([{
            'Day': date,
            'Collector': collector,
            'Total Connected': total_connected,
            'Total PTP': total_ptp,
            'Total RPC': total_rpc,
            'PTP Amount': ptp_amount,
            'Balance Amount': balance_amount,
        }])], ignore_index=True)

    st.dataframe(collector_summary.style.format({
        'PTP Amount': '₹ {:.2f}',
        'Balance Amount': '₹ {:.2f}'
    }).background_gradient(cmap='viridis', axis=0), width=1400)
