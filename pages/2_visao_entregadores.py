# Librarys

import pandas as pd
import os 
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static, st_folium
from haversine import haversine, Unit
import streamlit as st
from datetime import datetime
from PIL import Image
from modules import clean_code, top_delivers


# Import dataset

df = pd.read_csv('dataset/train.csv')

# Limpeza de dados --------------------------------------------------------------------------
df1 = clean_code(df)

# Visão empresa --------------------------------------------------------------------------

#======================================================================
# Sidebar layout
#======================================================================

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

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # Maior idade entre os entregadores
            max_age = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', max_age)

        with col2:
            # Menor idade entre os entregadores
            min_age = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', min_age)

        with col3:
            # Melhor condição de veículos
            max_condition = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', max_condition)

        with col4:
            # Pior condição de veículos
            min_condition = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', min_condition)

    with st.container():
        st.markdown('---')
        st.title('Avaliações')

        col1, col2 = st.columns(2, gap='small')
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                         .groupby(['Delivery_person_ID'])
                         .mean()
                         .reset_index())

            st.dataframe(df_aux)

        with col2:
            st.markdown('##### Avaliação média por trânsito')

            avg_std_by_traffic = (df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                         .groupby(['Road_traffic_density'])
                         .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            
            # Mudando o nome das colunas
            avg_std_by_traffic.columns = ['delivery_mean', 'delivery_std']
            # Index resetado 
            avg_std_by_traffic.reset_index()
            st.dataframe(avg_std_by_traffic)

            st.markdown('##### Avaliação média por clima')

            avg_std_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                         .groupby(['Weatherconditions'])
                         .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            # Mudando o nome das colunas
            avg_std_by_weather.columns = ['delivery_mean', 'delivery_std']
            # Index resetado 
            avg_std_by_weather.reset_index()
            st.dataframe(avg_std_by_weather)

    with st.container():
        st.markdown('---')
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc= True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc= False)
            st.dataframe(df3)

            
            