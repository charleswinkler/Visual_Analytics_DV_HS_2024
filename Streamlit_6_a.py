import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np

# Im Terminal folgendes eingeben: streamlit run Streamlit_6_a.py

# Titel des Dashboards
st.title('Prototyp Dashboard mit Streamlit')

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Datensätze laden
def load_data(dataset_id, api_key):
    url = f"{base_url}{dataset_id}/records?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        st.error(f"Fehler beim Laden von Datensatz {dataset_id}")
        return []

# Datensätze einlesen und in DataFrames konvertieren
df_1 = pd.DataFrame(load_data("100014", api_key))
df_2 = pd.DataFrame(load_data("100009", api_key))

# Kategorien hinzufügen und Spalten umbenennen
df_1['Kategorie'] = 'Parkhaus'
df_2['Kategorie'] = 'Klima'
df_1 = df_1.rename(columns={'auslastungen': 'auslastungen in prozent'})
df_2 = df_2.rename(columns={
    'name_original': 'id2', 'name_custom': 'title',
    'dates_max_date': 'published', 'stadtklima_basel_link': 'link'
})

# Geokoordinaten extrahieren
def extract_coordinates(row):
    geo_point = row.get('geo_point_2d')
    coords = row.get('coords')
    lon, lat = (geo_point or coords or {}).get('lon'), (geo_point or coords or {}).get('lat')
    return pd.Series([lon, lat])

df_1[['Longitude', 'Latitude']] = df_1.apply(extract_coordinates, axis=1)
df_2[['Longitude', 'Latitude']] = df_2.apply(extract_coordinates, axis=1)
df_1.drop(columns=['geo_point_2d', 'coords'], errors='ignore', inplace=True)
df_2.drop(columns=['geo_point_2d', 'coords'], errors='ignore', inplace=True)

# DataFrames zusammenführen
df_3 = pd.concat([df_1, df_2], ignore_index=True)

# Tabelle anzeigen
st.write('## Gesamtdaten-Tabelle')
st.dataframe(df_3)

# Parkhaus-Auswahl und Gauge-Chart
df_parkhaus = df_3[df_3['Kategorie'] == 'Parkhaus']
selected_title = st.selectbox('Wähle ein Parkhaus:', df_parkhaus['title'])
selected_data = df_parkhaus[df_parkhaus['title'] == selected_title].iloc[0]
occupied_percentage = ((selected_data['total'] - selected_data['free']) / selected_data['total']) * 100

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number", value=occupied_percentage,
    title={'text': f"Auslastung für {selected_title}"},
    number={'suffix': "%"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "#ff0000"},
        'steps': [{'range': [0, 50], 'color': '#66c2a5'}, {'range': [50, 100], 'color': '#fc8d62'}],
        'threshold': {'line': {'color': "red", 'width': 4}, 'value': occupied_percentage}
    }
))
st.plotly_chart(fig_gauge)

# Parkhaus-Standorte auf Karte anzeigen
st.write('## Parkhäuser in Basel-Stadt')
basel_map = folium.Map(location=[47.5596, 7.5886], zoom_start=13)
for _, row in df_parkhaus.iterrows():
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"{row['title']}<br>Freie Plätze: {int(row['free'])}<br>Gesamtplätze: {int(row['total'])}",
        tooltip=f"{row['title']} - Freie Plätze: {int(row['free'])} / Gesamt: {int(row['total'])}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(basel_map)
st_folium(basel_map, width=700, height=500)

# Parkhaus-Auslastung im Zeitverlauf
df_parkhaus['published'] = pd.to_datetime(df_parkhaus['published'])
df_parkhaus['occupied'] = df_parkhaus['total'] - df_parkhaus['free']
st.write("## Parkhaus-Auslastung im Zeitverlauf")

selected_parkhaus_1 = st.selectbox('Wähle das erste Parkhaus:', ['Keine Auswahl'] + sorted(df_parkhaus['title'].unique()))
selected_parkhaus_2 = st.selectbox('Wähle das zweite Parkhaus:', ['Keine Auswahl'] + sorted(df_parkhaus['title'].unique()))

fig_line = px.line()
if selected_parkhaus_1 != 'Keine Auswahl':
    fig_line.add_scatter(x=df_parkhaus[df_parkhaus['title'] == selected_parkhaus_1]['published'],
                         y=df_parkhaus[df_parkhaus['title'] == selected_parkhaus_1]['occupied'],
                         mode='lines+markers', name=selected_parkhaus_1, line=dict(color='blue'))
if selected_parkhaus_2 != 'Keine Auswahl':
    fig_line.add_scatter(x=df_parkhaus[df_parkhaus['title'] == selected_parkhaus_2]['published'],
                         y=df_parkhaus[df_parkhaus['title'] == selected_parkhaus_2]['occupied'],
                         mode='lines+markers', name=selected_parkhaus_2, line=dict(color='red'))
fig_line.update_layout(title="Auslastung der Parkhäuser im Zeitverlauf", xaxis_title="Zeitpunkt", yaxis_title="Belegte Plätze")
st.plotly_chart(fig_line)

# Klimadaten und Säulendiagramm
st.write("## Klimadaten")
df_klima = df_3[df_3['Kategorie'] == 'Klima']
df_klima['published'] = pd.to_datetime(df_klima['published'])
selected_klima_title = st.selectbox('Wähle ein Klima-Objekt:', ['Keine Auswahl'] + sorted(df_klima['title'].unique()))
df_klima_filtered = df_klima if selected_klima_title == 'Keine Auswahl' else df_klima[df_klima['title'] == selected_klima_title]

fig_bar = px.bar(df_klima_filtered, x='published', y='meta_airtemp', title="Klima und Temperaturen", labels={'published': 'Uhrzeit', 'meta_airtemp': 'Temperatur'})
st.plotly_chart(fig_bar)

# Heatmap für Temperaturdaten
st.write("## Heatmap der Temperatur nach Datum und Uhrzeit")
df_3['published'] = pd.to_datetime(df_3['published'])
df_3['date'] = df_3['published'].dt.date
df_3['hour'] = df_3['published'].dt.hour

start_date = st.date_input("Startdatum", value=df_3['date'].min())
end_date = st.date_input("Enddatum", value=df_3['date'].max())
filtered_df = df_3[(df_3['date'] >= start_date) & (df_3['date'] <= end_date) & (df_3['Kategorie'] == 'Klima')]

heatmap_data = filtered_df.groupby(['title', 'date', 'hour'])['meta_airtemp'].mean().reset_index()
heatmap_data['date_hour'] = heatmap_data['date'].astype(str) + " " + heatmap_data['hour'].astype(str) + ":00"

fig_heat = px.density_heatmap(heatmap_data, x="date_hour", y="title", z="meta_airtemp", color_continuous_scale="Viridis",
                              labels={'meta_airtemp': 'Temperatur (°C)', 'date_hour': 'Datum und Stunde', 'title': 'Klimastation'})
fig_heat.update_layout(title="Temperatur-Heatmap nach Datum, Stunde und Klimastation", xaxis_title="Datum und Stunde", yaxis_title="Klimastation", xaxis_tickangle=-45)
st.plotly_chart(fig_heat)
