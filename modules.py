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

#------------------------
# Funções
#------------------------

def clean_code (df1):

    """ Esta função realiza uma limpeza de dados adequada a esse DataFrame:
    
    Modificações realizadas (Em ordem):

    * Remoção dos espaços em branco (apenas das colunas do tipo object)
    * Padronização das colunas 'Time_taken(min)' e 'Weatherconditions', removendo a string '(min) ' e 'conditions ' respectivamente.
    * Substituindo as linhas que tenham valor igual 'NaN' pela respectiva moda da coluna 
        **OBS: 
               - Não faz média entre múltiplas modas, considera apenas o primeiro valor de moda da Series.
               - A coluna 'Time_Orderd' permanece com valores 'NaN' já que é uma timestamp e não seria razoável
                 substituir esses valores por uma moda (inclusive a moda seria o próprio valor 'NaN'), ou eliminar a
                 informação das outras colunas apenas por isso.
    * Modificação dos tipos de dados de algumas colunas.

    Input: DataFrame
    Output: DataFrame        

    """
    for col in df1.select_dtypes(include='object').columns:
        df1.loc[:, col] = df1.loc[:, col].str.strip()

        df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] if '(min) ' in x else x)
        df1['Weatherconditions'] = df1['Weatherconditions'].apply( lambda x: x.split('conditions ')[1] if 'conditions ' in x else x)

    cols_with_nan_String = df1.columns[(df1.map(lambda x: isinstance(x, str) and 'NaN' in x)).any()]
    
    for col in cols_with_nan_String:
        mode_value = df1[col].mode()[0]
        df1[col] = df1[col].replace('NaN', mode_value)

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = "%d-%m-%Y", dayfirst=True)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def top_delivers(df1, top_asc):
            
    df2 = (df1.loc[:, ['Time_taken(min)','Delivery_person_ID', 'City']]
            .groupby(['City', 'Delivery_person_ID'])
            .mean()
            .sort_values(['City', 'Time_taken(min)'], ascending= top_asc)
            .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop= True)

    return df3

def distance(df1, graph):

    """
    Esta função calcula a distância média entre os restaurantes e os pontos de entrega.

    * Parâmetros:
        - df1: DataFrame de origem dos dados.
        - graph: Parâmetro bool, se definido como:
            * True: Retorna um gráfico de pizza agrupado pela coluna 'City'.
            * False: Retorna apenas o valor da distância média.
    """

    if graph == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 
                'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'], 
                                                                    x['Restaurant_longitude']),
                                                                    (x['Delivery_location_latitude'],
                                                                    x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df1['distance'].mean(), 2)

        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 
                'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'], 
                                                                    x['Restaurant_longitude']),
                                                                    (x['Delivery_location_latitude'],
                                                                    x['Delivery_location_longitude'])), axis=1)
    
        distance_avg = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=distance_avg['City'], values= distance_avg['distance'], pull=[0, 0.1, 0])])

        return fig

    

def avg_std_time_delivery(df1, op, festival):
    """ 
    Esta função calcula a média e o desvio padrão do tempo de entrega, considerando se houve ou não festival.
        Parâmetros:
            - df1: DataFrame com os dados necessários
            - op: Operação desejada, escolha apenas entre a média e o desvio padrão, utilizando as strings
                - 'avg_time': Para o cálculo da média
                - 'std_time': Para o cálculo do desvio padrão
            - festival: Filtro que define se houve festival, escola apenas entre as strings 'Yes' ou 'No'.
    """
    time_mean = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    time_mean.columns = ['avg_time', 'std_time']
    time_mean = time_mean.reset_index()

    time_mean = np.round(time_mean.loc[time_mean['Festival'] == festival, op], 2)

    return time_mean

# Gráficos:

def order_metrics(df1):
    """ 
    Esta função cria um gráfico em barras das colunas 'ID' e 'Order_Date' agrupadas por 'Order_Date'.
    
    """
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x = 'Order_Date', y = 'ID')

    return fig

def traffic_order_share(df1):
    """ 
    Esta função cria um gráfico de pizza percentual dos tipos de densidade de trânsito.
    
    """
    df1_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                    .groupby(['Road_traffic_density'])
                    .count()
                    .reset_index())
    df1_aux['Traffic_percent'] = df1_aux['ID'] / df1_aux['ID'].sum() 
    fig = px.pie(df1_aux, values = 'Traffic_percent', names = 'Road_traffic_density')

    return fig

def traffic_order_city(df1):
    """ 
    Esta função cria um gráfico de bolhas do volume de pedidos por cidade e tipo de tráfego.
    
    """
    df1_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .count()
                .reset_index())
    fig = px.scatter(df1_aux, x= 'City', y= 'Road_traffic_density', size= 'ID', color= 'City')

    return fig

def orders_by_week(df1):
    """ 
    Esta função cria um gráfico de linha do total de pedidos por semana, onde o eixo x são as semanas do ano e o eixo y o número de pedidos.
    
    """
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    cols = ['ID', 'Week_of_year']
    df_aux = df1.loc[:, cols].groupby(['Week_of_year']).count().reset_index()
    fig = px.line(df_aux, x = 'Week_of_year', y = 'ID')

    return fig

def order_share_by_week(df1):
    """ 
    Esta função cria um gráfico de linha da quantidade de pedidos por entregador por semana.
    
    """
    df_aux01 = (df1.loc[:, ['ID', 'Week_of_year']]
                   .groupby('Week_of_year')
                   .count()
                   .reset_index())
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'Week_of_year']]
                   .groupby(['Week_of_year'])
                   .nunique()
                   .reset_index())
    df_aux = pd.merge(df_aux01, df_aux02, how= 'inner')
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x= 'Week_of_year', y= 'Order_by_delivery')

    return fig

def country_maps(df1):
    """ 
    Esta função cria um mapa do local de interesse, marcando os pontos de localização central de cada cidade por tipo de tráfego.
    
    """
    df_aux = (df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                .groupby(['City', 'Road_traffic_density'])
                .median()
                .reset_index())

    m = folium.Map(location=(18.584190,76.021782), zoom_start=6)

    for index, row in df_aux.iterrows():
        folium.Marker(location= [row['Delivery_location_latitude'], 
                                row['Delivery_location_longitude']], 
                                popup= row[['City', 'Road_traffic_density']]).add_to(m)

    st_folium(m, use_container_width=True)

def avg_std_time_bar(df1):
    time_mean_std = df1.loc[:, ['Time_taken(min)', 'City']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    time_mean_std.columns = ['time_mean','time_std']
    time_mean_std = time_mean_std.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(name='Control', x= time_mean_std['City'], y= time_mean_std['time_mean'], error_y= dict(type= 'data', array= time_mean_std['time_std'])))
    fig.update_layout(barmode= 'group')

    return fig

def avg_dist_pie(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1)

    distance_avg = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

    fig = go.Figure(data=[go.Pie(labels=distance_avg['City'], values= distance_avg['distance'], pull=[0, 0.1, 0])])

    return fig

def avg_std_time_sunburst(df1):
    time_mean_std = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    time_mean_std.columns = ['time_mean','time_std']
    time_mean_std = time_mean_std.reset_index()

    fig = px.sunburst(time_mean_std, path=['City', 'Road_traffic_density'], 
        values='time_mean', color='time_std', 
        color_continuous_scale='RdBu', 
        color_continuous_midpoint=np.average(time_mean_std['time_std']))
    
    return fig