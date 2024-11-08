import os
import pandas as pd
import numpy as np 
import streamlit as st
from PIL import Image
from datetime import datetime
from modules import clean_code, order_metrics, order_share_by_week, orders_by_week, traffic_order_city, traffic_order_share, country_maps

# Import dataset
df = pd.read_csv('../dataset/train.csv')

# Limpando o DataFrame:
df1 = clean_code(df)

# Visão empresa --------------------------------------------------------------------------

st.set_page_config(layout='wide')

#======================================================================
# Sidebar layout
#======================================================================

st.header("Marketplace - Visão Cliente", divider=True)

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Vião Geográfica'])

with tab1:
    with st.container():
        # Order metric
        st.header('Orders by Day', divider=True)
        fig = order_metrics(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share', divider=True)
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic Order City', divider=True)
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    with st.container():
        st.header('Orders by Week', divider=True)
        fig = orders_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)     

    with st.container():
        st.header('Order Share by Week', divider=True)
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header('Country maps', divider=True)
    country_maps(df1)
