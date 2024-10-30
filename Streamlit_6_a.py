# Im Terminal folgendes eingeben: streamlit run Streamlit_6_a.py

import requests
import json
import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_leaflet as dl
import dash_leaflet.express as dlx
import plotly.express as px
import plotly.graph_objects as go  # Für den Gauge-Chart
import streamlit as st
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import numpy as np

# Titel des Dashboards schreiben
st.title('Prototyp Dashboard mit Streamlit')

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Erster Datensatz einlesen
dataset1_url = f"{base_url}100014/records?apikey={api_key}"
response1 = requests.get(dataset1_url)
if response1.status_code == 200:
    dataset1 = response1.json()  # Daten in einer Variablen speichern
    print("Datensatz 1 erfolgreich geladen.")
else:
    print(f"Fehler beim Laden von Datensatz 1: {response1.status_code}")

# Zweiter Datensatz einlesen
dataset2_url = f"{base_url}100009/records?apikey={api_key}&limit=20"
response2 = requests.get(dataset2_url)
if response2.status_code == 200:
    dataset2 = response2.json()  # Daten in einer Variablen speichern
    print("Datensatz 2 erfolgreich geladen.")
else:
    print(f"Fehler beim Laden von Datensatz 2: {response2.status_code}")

# Erstellen von DataFrames aus den geladenen Datensätzen
df_1 = pd.DataFrame(dataset1['results'])
df_2 = pd.DataFrame(dataset2['results'])

# 1. Kategorie-Spalte hinzufügen:
df_1['Kategorie'] = 'Parkhaus'
df_2['Kategorie'] = 'Klima'

# 2. Umbenennen der relevanten Spalten in df_2, damit sie zu den Spalten in df_1 passen:
df_2 = df_2.rename(columns={
    'name_original': 'id2',
    'name_custom': 'title',
    'dates_max_date': 'published',
    'stadtklima_basel_link': 'link'
})

# 2. Addendum. Spalte in df_1 ebenfalls umbenennen.
df_1 = df_1.rename(columns={
    'auslastungen' : 'auslastungen in prozent'
})

# 3. Geographische Daten extrahieren und aufteilen
def extract_coordinates(row):
    geo_point = row.get('geo_point_2d')
    coords = row.get('coords')
    lon, lat = None, None
    if isinstance(geo_point, dict) and 'lon' in geo_point and 'lat' in geo_point:
        lon, lat = geo_point['lon'], geo_point['lat']
    if isinstance(coords, dict) and 'lon' in coords and 'lat' in coords:
        lon, lat = coords['lon'], coords['lat']
    return pd.Series([lon, lat])

# Anwenden der Funktion auf beide DataFrames und neue Spalten erstellen
df_1[['Longitude', 'Latitude']] = df_1.apply(extract_coordinates, axis=1)
df_2[['Longitude', 'Latitude']] = df_2.apply(extract_coordinates, axis=1)

# Entfernen der geo_point_2d Spalte
df_1 = df_1.drop(columns=['geo_point_2d', 'coords'], errors='ignore')
df_2 = df_2.drop(columns=['geo_point_2d', 'coords'], errors='ignore')

# 4. DataFrames zusammenführen:
df_3 = pd.concat([df_1, df_2], ignore_index=True)

# 5. Ausgabe der ersten Zeilen des kombinierten DataFrames zur Überprüfung
print(df_3.head())

# Daten laden in Tabelle und Überschrift
st.write('## Tabelle')
st.dataframe(df_3)
st.dataframe(df_1)
st.dataframe(df_2)

# Filtere die DataFrame nach 'Parkhaus'
df_parkhaus = df_3[df_3['Kategorie'] == 'Parkhaus']

# Dropdown-Menü für die Auswahl des Titels
selected_title = st.selectbox('Wähle ein Parkhaus:', df_parkhaus['title'])

# Werte für das gewählte Parkhaus abrufen
selected_data = df_parkhaus[df_parkhaus['title'] == selected_title].iloc[0]
total = selected_data['total']
free = selected_data['free']

# Verwendung von NumPy zur Berechnung der belegten Plätze
occupied = np.subtract(total, free)
occupied_percentage = (occupied / total) * 100

# Erstellung des Gauge-Charts
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=occupied_percentage,
    title={'text': f"Auslastung für {selected_title}"},
    number={'suffix': "%"},  # Hier wird das Prozentzeichen hinzugefügt
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
        'bar': {'color': "#fc8d62"},
        'bgcolor': "white",
        'steps': [
            {'range': [0, 50], 'color': '#66c2a5'},
            {'range': [50, 100], 'color': '#fc8d62'}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': occupied_percentage
        }
    }
))

# Diagramm in Streamlit anzeigen
st.plotly_chart(fig_gauge)

# Erstellen der Basler Stadtkarte
center_coords = [47.5596, 7.5886]  # Koordinaten für Basel
basel_map = folium.Map(location=center_coords, zoom_start=13)

# Parkhäuser als Marker hinzufügen
for _, row in df_parkhaus.iterrows():
    free = int(row['free'])
    total = int(row['total'])
    popup_text = f"{row['title']}<br>Freie Plätze: {free}<br>Gesamtplätze: {total}"
    tooltip_text = f"{row['title']} - Freie Plätze: {free} / Gesamt: {total}"

    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=popup_text,
        tooltip=tooltip_text,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(basel_map)

# Karte in Streamlit anzeigen
st.write('## Parkhäuser in Basel-Stadt')
st_folium(basel_map, width=700, height=500)


# Datumsformat konvertieren, falls nötig
df_parkhaus['published'] = pd.to_datetime(df_parkhaus['published'])

# Berechnung der belegten Plätze
df_parkhaus['occupied'] = df_parkhaus['total'] - df_parkhaus['free']

# Auswahlmöglichkeiten für den Filter vorbereiten, mit 'Keine Auswahl' als zusätzliche Option
parkhaus_options = ['Keine Auswahl'] + sorted(df_parkhaus['title'].unique().tolist())

# Auswahl der Parkhäuser mittels Filter
st.write("## Parkhaus-Auslastung")
selected_parkhaus_1 = st.selectbox(
    'Wähle das erste Parkhaus:', parkhaus_options, index=0, key='parkhaus1'
)
selected_parkhaus_2 = st.selectbox(
    'Wähle das zweite Parkhaus:', parkhaus_options, index=0, key='parkhaus2'
)

# Filter auf die ausgewählten Parkhäuser anwenden
if selected_parkhaus_1 == 'Keine Auswahl':
    df_selected_1 = pd.DataFrame()  # Leerer DataFrame, wenn nichts ausgewählt ist
else:
    df_selected_1 = df_parkhaus[df_parkhaus['title'] == selected_parkhaus_1]

if selected_parkhaus_2 == 'Keine Auswahl':
    df_selected_2 = pd.DataFrame()  # Leerer DataFrame, wenn nichts ausgewählt ist
else:
    df_selected_2 = df_parkhaus[df_parkhaus['title'] == selected_parkhaus_2]

# Liniendiagramm mit Plotly Express erstellen
fig_line = px.line()

# Daten des ersten Parkhauses hinzufügen, wenn vorhanden
if not df_selected_1.empty:
    fig_line.add_scatter(
        x=df_selected_1['published'],
        y=df_selected_1['occupied'],
        mode='lines+markers',
        name=selected_parkhaus_1,
        line=dict(color='blue')
    )

# Daten des zweiten Parkhauses hinzufügen, wenn vorhanden
if not df_selected_2.empty:
    fig_line.add_scatter(
        x=df_selected_2['published'],
        y=df_selected_2['occupied'],
        mode='lines+markers',
        name=selected_parkhaus_2,
        line=dict(color='red')
    )

# Diagramm-Einstellungen anpassen
fig_line.update_layout(
    title="Auslastung der Parkhäuser im Zeitverlauf",
    xaxis_title="Zeitpunkt",
    yaxis_title="Belegte Plätze",
    xaxis=dict(tickformat="%H:%M", title="Stündliche Intervalle")
)

# Diagramm anzeigen
st.plotly_chart(fig_line)

# Beispiel: DataFrame df_klima laden und konvertieren
df_klima = df_3[df_3['Kategorie'] == 'Klima']
df_klima['published'] = pd.to_datetime(df_klima['published'])

# Auswahlmöglichkeiten für den Filter vorbereiten, mit 'Keine Auswahl' als zusätzliche Option
klima_options = ['Keine Auswahl'] + sorted(df_klima['title'].unique().tolist())

# Titel schreiben
st.write("## Klimadaten")

# Dropdown-Filter für die Auswahl von Objekten aus der 'title'-Spalte
selected_klima_title = st.selectbox('Wähle ein Klima-Objekt:', klima_options)

# Filter anwenden, falls nicht 'Keine Auswahl' ausgewählt ist
if selected_klima_title != 'Keine Auswahl':
    df_klima_filtered = df_klima[df_klima['title'] == selected_klima_title]
else:
    df_klima_filtered = df_klima  # Zeigt alle Daten an, wenn 'Keine Auswahl' gewählt ist

# Säulendiagramm mit Plotly Express erstellen
fig_bar = px.bar(
    df_klima_filtered,
    x='published',         # X-Achse: Veröffentlichungsdatum
    y='meta_airtemp',      # Y-Achse: Temperaturdaten
    title="Klima und Temperaturen",
    labels={'published': 'Uhrzeit', 'meta_airtemp': 'Temperatur'}
)

# Diagramm anzeigen
st.plotly_chart(fig_bar)



# Konvertiere das Datum (published) in das richtige Datetime-Format
df_3['published'] = pd.to_datetime(df_3['published'])

# Erstelle neue Spalten für Datum und Stunde
df_3['date'] = df_3['published'].dt.date
df_3['hour'] = df_3['published'].dt.hour

# Heatmap-Variablen auswählen
st.title("Heatmap der Temperatur nach Datum und Uhrzeit")

# Filter für den gewünschten Zeitraum
start_date = st.date_input("Startdatum", value=df_3['date'].min())
end_date = st.date_input("Enddatum", value=df_3['date'].max())
filtered_df = df_3[(df_3['date'] >= start_date) & (df_3['date'] <= end_date) & (df_3['Kategorie'] == 'Klima')]

# Heatmap-Daten vorbereiten, gruppiert nach Titel (Klimastation), Datum und Stunde
heatmap_data = filtered_df.groupby(['title', 'date', 'hour'])['meta_airtemp'].mean().reset_index()

# Füge eine kombinierte Spalte für Datum und Stunde hinzu
heatmap_data['date_hour'] = heatmap_data['date'].astype(str) + " " + heatmap_data['hour'].astype(str) + ":00"

# Heatmap erstellen
fig_heat = px.density_heatmap(
    heatmap_data,
    x="date_hour",
    y="title",
    z="meta_airtemp",
    color_continuous_scale="Viridis",
    labels={'meta_airtemp': 'Temperatur (°C)', 'date_hour': 'Datum und Stunde', 'title': 'Klimastation'}
)
fig_heat.update_layout(
    title="Temperatur-Heatmap nach Datum, Stunde und Klimastation",
    xaxis_title="Datum und Stunde",
    yaxis_title="Klimastation",
    coloraxis_colorbar=dict(title="Temperatur (°C)"),
    xaxis_tickangle=-45
)

# Diagramm in Streamlit anzeigen
st.plotly_chart(fig_heat)