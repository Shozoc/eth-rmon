import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import re

st.set_page_config(page_title="ETH RMON", layout="wide", initial_sidebar_state="expanded")

# CSS
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.title("⚙️")
    
    uploaded_files = st.file_uploader("Upload .rmon / .csv", type=['csv', 'rmon'], accept_multiple_files=True)
    
    st.markdown("---")
    type_an = st.radio("Pilih Modul :", ('Bandwidth Analysis', 'Discard Analysis'))
    
    st.markdown("---")
    bandwidth_input = st.number_input(label="Kapasitas Bandwidth (Mbps):", min_value=0.0, value=0.0)
    
    st.markdown("---")
    st.caption("Developed with Streamlit")
    st.caption("Created by Alfian Bayu")

# DASHBOARD
st.title("Kalkulator Bandwith Radio NEC")
st.markdown("---")

def plotrmon_merged(files, bandwidth):
    df_list = []
    if len(files) == 1:
        files_title = files[0].name
    else:
        files_title = " + ".join([f.name for f in files])

    for file in files:
        temp_df = pd.read_csv(file, sep=",", skiprows=1)
        date_match = re.search(r'\d{8}', file.name)
        if date_match:
            date_str = date_match.group()
            temp_df['Datetime'] = pd.to_datetime(date_str + ' ' + temp_df['Time Stamp'], format='%Y%m%d %H:%M', errors='coerce')
        else:
            temp_df['Datetime'] = temp_df['Time Stamp'] + " (" + file.name + ")"
        df_list.append(temp_df)
        
    df = pd.concat(df_list, ignore_index=True)
    if pd.api.types.is_datetime64_any_dtype(df['Datetime']):
        df = df.sort_values('Datetime')
    df = df.set_index('Datetime')
    
    orig_cols = ['RX Octs', 'TX Octs']
    peak_cols = ['RX Peak Rate [Mbps]', 'TX Peak Rate [Mbps]']
    
    st.markdown(f"### Merged Data: {len(files)} File(s)")
    
    col_left, col_right = st.columns(2)
    
    # OCTETS
    with col_left:
        if all(col in df.columns for col in orig_cols):
            df[orig_cols] = df[orig_cols].replace(r'\D', '', regex=True).astype(float)
            df['Bandwidth RX (Octs)'] = df['RX Octs'].apply(lambda x: (x * 8 / 900) / 1e6)
            df['Bandwidth TX (Octs)'] = df['TX Octs'].apply(lambda x: (x * 8 / 900) / 1e6)
            
            fig_octs = go.Figure()
            fig_octs.add_trace(go.Scatter(x=df.index, y=df['Bandwidth RX (Octs)'], mode='lines', name='RX', line=dict(color='#00D2FF', width=2), fill='tozeroy'))
            fig_octs.add_trace(go.Scatter(x=df.index, y=df['Bandwidth TX (Octs)'], mode='lines', name='TX', line=dict(color='#FF007F', width=2)))
            
            fig_octs.update_layout(
                title='Bandwidth Analysis ' + files_title + '<br><sup>Calculated from TX/RX Octets</sup>',
                xaxis_title="", yaxis_title="Mbps", height=450,
                plot_bgcolor='rgba(0,0,0,0)', 
                hovermode="x unified", 
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            fig_octs.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig_octs, use_container_width=True)
            
            st.markdown("##### Receive (RX) Metrics")
            rx1, rx2, rx3 = st.columns(3)
            rx1.metric('Max RX (Mbps)', round(df["Bandwidth RX (Octs)"].max(), 2))
            rx2.metric('Min RX (Mbps)', round(df["Bandwidth RX (Octs)"].min(), 2))
            rx3.metric('RX Util (%)', (lambda x: round(x / bandwidth * 100, 2) if bandwidth > 0 else 0)(df["Bandwidth RX (Octs)"].max()))
            
            st.markdown("##### Transmit (TX) Metrics")
            tx1, tx2, tx3 = st.columns(3)
            tx1.metric('Max TX (Mbps)', round(df["Bandwidth TX (Octs)"].max(), 2))
            tx2.metric('Min TX (Mbps)', round(df["Bandwidth TX (Octs)"].min(), 2))
            tx3.metric('TX Util (%)', (lambda x: round(x / bandwidth * 100, 2) if bandwidth > 0 else 0)(df["Bandwidth TX (Octs)"].max()))
        else:
            st.warning("Data TX/RX Octets tidak ditemukan.")

    # PEAK RATE
    with col_right:
        if all(col in df.columns for col in peak_cols):
            df[peak_cols] = df[peak_cols].replace(r'[^\d\.]', '', regex=True).astype(float)
            df['Bandwidth RX (Peak)'] = df['RX Peak Rate [Mbps]']
            df['Bandwidth TX (Peak)'] = df['TX Peak Rate [Mbps]']
            
            fig_peak = go.Figure()
            fig_peak.add_trace(go.Scatter(x=df.index, y=df['Bandwidth RX (Peak)'], mode='lines', name='RX', line=dict(color='#00FF87', width=2), fill='tozeroy'))
            fig_peak.add_trace(go.Scatter(x=df.index, y=df['Bandwidth TX (Peak)'], mode='lines', name='TX', line=dict(color='#FF007F', width=2)))
            
            fig_peak.update_layout(
                title='Bandwidth Analysis ' + files_title + '<br><sup>Reported Peak Rate [Mbps]</sup>',
                xaxis_title="", yaxis_title="Mbps", height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=0, r=0, t=50, b=0)
            )
            fig_peak.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            st.plotly_chart(fig_peak, use_container_width=True)
            
            st.markdown("##### Receive (RX) Metrics")
            rx4, rx5, rx6 = st.columns(3)
            rx4.metric('Max RX (Mbps)', round(df["Bandwidth RX (Peak)"].max(), 2))
            rx5.metric('Min RX (Mbps)', round(df["Bandwidth RX (Peak)"].min(), 2))
            rx6.metric('RX Util (%)', (lambda x: round(x / bandwidth * 100, 2) if bandwidth > 0 else 0)(df["Bandwidth RX (Peak)"].max()))
            
            st.markdown("##### Transmit (TX) Metrics")
            tx4, tx5, tx6 = st.columns(3)
            tx4.metric('Max TX (Mbps)', round(df["Bandwidth TX (Peak)"].max(), 2))
            tx5.metric('Min TX (Mbps)', round(df["Bandwidth TX (Peak)"].min(), 2))
            tx6.metric('TX Util (%)', (lambda x: round(x / bandwidth * 100, 2) if bandwidth > 0 else 0)(df["Bandwidth TX (Peak)"].max()))
        else:
            st.info("Data TX/RX Peak Rate tidak ditemukan.")

def plotDiscard(files):
    df_list = []
    if len(files) == 1:
        files_title = files[0].name
    else:
        files_title = " + ".join([f.name for f in files])

    for file in files:
        temp_df = pd.read_csv(file, sep=",", skiprows=1)
        date_match = re.search(r'\d{8}', file.name)
        if date_match:
            date_str = date_match.group()
            temp_df['Datetime'] = pd.to_datetime(date_str + ' ' + temp_df['Time Stamp'], format='%Y%m%d %H:%M', errors='coerce')
        else:
            temp_df['Datetime'] = temp_df['Time Stamp'] + " (" + file.name + ")"
        df_list.append(temp_df)
        
    df = pd.concat(df_list, ignore_index=True)
    if pd.api.types.is_datetime64_any_dtype(df['Datetime']):
        df = df.sort_values('Datetime')
    df = df.set_index('Datetime')
    
    discard_cols = ['TX Queue0 Discard', 'TX Queue1 Discard', 'TX Queue2 Discard', 'TX Queue3 Discard']
    if all(col in df.columns for col in discard_cols):
        df[discard_cols] = df[discard_cols].replace(r'\D', '', regex=True).astype(float) 
        
        st.markdown(f"### Discard Analysis: {len(files)} File(s)")
        
        fig1 = go.Figure()
        colors = ['#FF4B4B', '#FFAA00', '#00D2FF', '#00FF87']
        for i, col in enumerate(discard_cols):
            fig1.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col.replace('TX ', ''), line=dict(color=colors[i], width=2)))
        
        fig1.update_layout(
            title='Discard Analysis ' + files_title, 
            xaxis_title="", yaxis_title="Mbps", height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        ) 
        fig1.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("Kolom antrean Discard tidak lengkap di file yang diupload.")

if uploaded_files:
    if type_an == 'Bandwidth Analysis': 
        plotrmon_merged(uploaded_files, bandwidth_input) 
    else: 
        plotDiscard(uploaded_files)
else:
    st.info("👈 Upload file .rmon atau .csv pada panel di sebelah kiri untuk memulai kalkulasi.")