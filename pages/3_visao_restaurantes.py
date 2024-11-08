# Librarys

import pandas as pd
import os 
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static, st_folium
from haversine import haversine, Unit
import streamlit as st
from datetime import datetime
from PIL import Image
from modules import clean_code, distance, avg_std_time_delivery, avg_std_time_bar, avg_std_time_sunburst


# Import dataset

df = pd.read_csv('dataset/train.csv')


# Limpeza de dados --------------------------------------------------------------------------

df1 = clean_code(df)

# Visão empresa --------------------------------------------------------------------------

#======================================================================
# Sidebar layout
#======================================================================

st.set_page_config(layout='wide')

st.header("Marketplace - Visão Entregadores", divider=True)

image = Image.open('logo.png')
st.sidebar.image(image, width=240)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown('---')

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
        'Até qual valor?',
        value= datetime(2022, 2, 23),
        min_value= datetime(2022, 2, 11),
        max_value= datetime(2022, 4, 6),
        format='DD-MM-YYYY'
)

st.sidebar.markdown('---')

traffic_option = st.sidebar.multiselect(
        'Quais as condições de trânsito?',
        ['Low', 'Medium', 'High', 'Jam'],
        default= ['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('---')
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas,:]

#Filtro de trânsito

linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_option)
df1 = df1.loc[linhas_selecionadas,:]

#======================================================================
# Layout no streamlit
#======================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-','-'])

with tab1:
    with st.container():
        st.subheader('Overall Metrics', divider='green')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)

        with col2:
            avg_distance = distance(df1, graph=False)
            col2.metric('Distância média', avg_distance)  

        with col3:
            time_mean = avg_std_time_delivery(df1, op='avg_time', festival='Yes')
            col3.metric('AVG Time Festival', time_mean)

        with col4:
            time_mean = avg_std_time_delivery(df1, op='std_time', festival='Yes')
            col4.metric('STD Time Festival', time_mean)

        with col5:
            time_mean = avg_std_time_delivery(df1, op='avg_time', festival='No')
            col5.metric('AVG Time', time_mean)

        with col6:
            time_mean = avg_std_time_delivery(df1, op='std_time', festival='No')    
            col6.metric('STD Time', time_mean)
    st.markdown('---')

    with st.container():
        col1, col2 = st.columns(2, gap='large')
        
        with col1:
            st.markdown('##### Tempo médio e devio padrão de entrega por cidade')
            fig = avg_std_time_bar(df1)
            st.plotly_chart(fig) 
            
        with col2:
            st.markdown('##### Tempo médio por cidade e tipo de pedido')
            time_mean_std = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
            time_mean_std.columns = ['time_mean','time_std']
            time_mean_std = time_mean_std.reset_index()

            st.dataframe(time_mean_std, hide_index=True, use_container_width=True)
    st.markdown('---')
    
    with st.container():
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('##### Distância média dos restaurantes ao local de entrega')
            fig = distance(df1, graph=True)
            st.plotly_chart(fig, use_container_width= True)

        with col2:
            st.markdown('##### Tempo médio e devio padrão de entrega por cidade e tipo de tráfego')
            fig = avg_std_time_sunburst(df1)
            st.plotly_chart(fig, use_container_width= True)

            

