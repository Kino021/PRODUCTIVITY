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

# Remove title from the page by hiding it via CSS
st.markdown("""
    <style>
        .css-1v0mbdj {display: none;}
    </style>
""", unsafe_allow_html=True)

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

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Upload Daily Remark File", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)

    def calculate_productivity_summary(df):
        productivity_table = pd.DataFrame(columns=[
            'Day', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
        ])

        total_connected_all = total_ptp_all = total_rpc_all = total_ptp_amount_all = total_balance_all = 0

        for date, group in df.groupby(df['Date'].dt.date):
            total_connected = group[group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = group[group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = group[group['Status'].str.contains('PTP', na=False) & (group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance = group[group['Status'].str.contains('PTP', na=False) & (group['Balance'] != 0)]['Balance'].sum()

            productivity_table = pd.concat([productivity_table, pd.DataFrame([{
                'Day': date,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Balance Amount': total_balance
            }])], ignore_index=True)

            total_connected_all += total_connected
            total_ptp_all += total_ptp
            total_rpc_all += total_rpc
            total_ptp_amount_all += total_ptp_amount
            total_balance_all += total_balance

        productivity_table = pd.concat([productivity_table, pd.DataFrame([{
            'Day': 'Total',
            'Total Connected': total_connected_all,
            'Total PTP': total_ptp_all,
            'Total RPC': total_rpc_all,
            'Total PTP Amount': total_ptp_amount_all,
            'Balance Amount': total_balance_all
        }])], ignore_index=True)

        return productivity_table

    st.write("## Productivity Summary Table")
    st.write(calculate_productivity_summary(df))

    def calculate_productivity_per_cycle(df):
        cycle_productivity_table = pd.DataFrame(columns=[
            'Cycle (Service No.)', 'Total Connected', 'Total PTP', 'Total RPC', 'Total PTP Amount', 'Balance Amount'
        ])

        total_connected_all = total_ptp_all = total_rpc_all = total_ptp_amount_all = total_balance_all = 0

        for service_no, cycle_group in df.groupby('Service No.'):
            total_connected = cycle_group[cycle_group['Call Status'] == 'CONNECTED']['Account No.'].count()
            total_ptp = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['Account No.'].nunique()
            total_rpc = cycle_group[cycle_group['Status'].str.contains('RPC', na=False)]['Account No.'].nunique()
            total_ptp_amount = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['PTP Amount'] != 0)]['PTP Amount'].sum()
            total_balance = cycle_group[cycle_group['Status'].str.contains('PTP', na=False) & (cycle_group['Balance'] != 0)]['Balance'].sum()

            cycle_productivity_table = pd.concat([cycle_productivity_table, pd.DataFrame([{
                'Cycle (Service No.)': service_no,
                'Total Connected': total_connected,
                'Total PTP': total_ptp,
                'Total RPC': total_rpc,
                'Total PTP Amount': total_ptp_amount,
                'Balance Amount': total_balance
            }])], ignore_index=True)

            total_connected_all += total_connected
            total_ptp_all += total_ptp
            total_rpc_all += total_rpc
            total_ptp_amount_all += total_ptp_amount
            total_balance_all += total_balance

        cycle_productivity_table = pd.concat([cycle_productivity_table, pd.DataFrame([{
            'Cycle (Service No.)': 'Total',
            'Total Connected': total_connected_all,
            'Total PTP': total_ptp_all,
            'Total RPC': total_rpc_all,
            'Total PTP Amount': total_ptp_amount_all,
            'Balance Amount': total_balance_all
        }])], ignore_index=True)

        return cycle_productivity_table

    st.write("## Productivity Summary per Cycle (Service No.)")
    st.write(calculate_productivity_per_cycle(df))
