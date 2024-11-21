import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from io import StringIO
import streamlit as st

uploaded_files = st.file_uploader("Choose a .rmon file",type = ['csv','rmon'], key=None)

#ethrmon.plotrmon('BW Util', uploaded_files)
def plotrmon(filepath):
        df = pd.read_csv(filepath, sep=",", skiprows=1)
        #df['Time Stamp']= pd.to_timedelta(df['Time Stamp']+':00')
        df = df.set_index('Time Stamp')  
        df[['RX Octs','TX Octs','TX Queue0 Discard','TX Queue1 Discard','TX Queue2 Discard','TX Queue3 Discard']] = df[['RX Octs','TX Octs','TX Queue0 Discard','TX Queue1 Discard','TX Queue2 Discard','TX Queue3 Discard']].replace(r'\D', '',regex=True).astype(float) 
        df[['Bandwidth RX','Bandwidth TX']] = df[['RX Octs','TX Octs']].apply( lambda x : (x*8/900)/1e6)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Bandwidth RX'],
                    mode='lines',
                    name='RX Bandwidth'))
        fig.add_trace(go.Scatter(x=df.index, y=df['Bandwidth TX'],
                            mode='lines',
                            name='TX Bandwidth'))
        fig.update_layout(title='Bandwidth Analysis '+filepath.name,  
        xaxis_title="Time Stamp",
                 yaxis_title="Mbps", width=1080, height=600)
        bandwidth = st.number_input(label="Input Bandwidth :")
        col1, col2, col3,col4 = st.columns(4)
        col1.metric('Max RX',round(df["Bandwidth RX"].max(),2),delta=None)
        col2.metric('Max TX',round(df["Bandwidth TX"].max(),2),delta=None)
        col3.metric('Bandwidth TX Util (%)', (lambda x : round(x/bandwidth*100,2) if bandwidth > 0 else None)(df["Bandwidth TX"].max()),delta=None)
        col4.metric('Bandwidth RX Util (%)', (lambda x : round(x/bandwidth*100,2) if bandwidth > 0 else None)(df["Bandwidth RX"].max()),delta=None)
        return st.plotly_chart(fig)
def plotDiscard(filepath):
        df = pd.read_csv(filepath, sep=",", skiprows=1)
        #df['Time Stamp']= pd.to_timedelta(df['Time Stamp']+':00')
        df = df.set_index('Time Stamp')  
        df[['RX Octs','TX Octs','TX Queue0 Discard','TX Queue1 Discard','TX Queue2 Discard','TX Queue3 Discard']] = df[['RX Octs','TX Octs','TX Queue0 Discard','TX Queue1 Discard','TX Queue2 Discard','TX Queue3 Discard']].replace(r'\D', '',regex=True).astype(float) 
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df.index, y=df['TX Queue0 Discard'],
                    mode='lines',
                    name='Queue0 Discard'))
        fig1.add_trace(go.Scatter(x=df.index, y=df['TX Queue1 Discard'],
                    mode='lines',
                    name='Queue1 Discard'))
        fig1.add_trace(go.Scatter(x=df.index, y=df['TX Queue2 Discard'],
                    mode='lines',
                    name='Queue2 Discard'))
        fig1.add_trace(go.Scatter(x=df.index, y=df['TX Queue3 Discard'],
                    mode='lines',
                    name='Queue3 Discard'))     
        fig1.update_layout(title='Discard Analysis '+filepath.name,  
        xaxis_title="Time Stamp",
                 yaxis_title="Mbps", width=1080, height=600) 
        return st.plotly_chart(fig1)      
if uploaded_files is not None:
          # To read file as bytes:
     bytes_data = uploaded_files.getvalue()
     #st.write(bytes_data)

     # To convert to a string based IO:
     stringio = StringIO(uploaded_files.getvalue().decode("utf-8"))
     #st.write(stringio)

     # To read file as string:
     string_data = stringio.read()
     #st.write(string_data)

     # Can be used wherever a "file-like" object is accepted:

     type_an = st.radio(
           "Select :  ",
                 ('Bandwidth Analysis', 'Discard Analysis'))
     if type_an == 'Bandwidth Analysis': 
             plotrmon(uploaded_files) 
     else: 
          plotDiscard(uploaded_files)