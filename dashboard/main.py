import streamlit as st
from data_loader import load_data
from map import plot_map
from gauge import plot_gauge
from line_chart import plot_line_chart
from bar_chart import plot_bar_chart
from heatmap import plot_heatmap
import pandas as pd
from utils import extract_coordinates, filter_by_date
from trend_detection import detect_change_points
from manhattan_distance import main as manhattan_main
from map_cluster import plot_map_with_clusters


# Titel des Dashboards
st.title('Prototyp Dashboard mit Streamlit')

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Datensätze einlesen
df_1 = pd.DataFrame(load_data("100014", api_key, base_url))
df_2 = pd.DataFrame(load_data("100009", api_key, base_url))

# Verarbeiten der Daten
df_1['Kategorie'] = 'Parkhaus'
df_2['Kategorie'] = 'Klima'
df_1 = df_1.rename(columns={'auslastungen': 'auslastungen in prozent'})
df_2 = df_2.rename(columns={
    'name_original': 'id2', 'name_custom': 'title',
    'dates_max_date': 'published', 'stadtklima_basel_link': 'link'
})

# Geokoordinaten extrahieren und den DataFrame erweitern
df_1[['Longitude', 'Latitude']] = df_1.apply(extract_coordinates, axis=1)
df_2[['Longitude', 'Latitude']] = df_2.apply(extract_coordinates, axis=1)
df_1.drop(columns=['geo_point_2d', 'coords'], errors='ignore', inplace=True)
df_2.drop(columns=['geo_point_2d', 'coords'], errors='ignore', inplace=True)

# DataFrames zusammenführen
df_3 = pd.concat([df_1, df_2], ignore_index=True)

# Optional: Sicherstellen, dass Longitude und Latitude existieren
if 'Longitude' not in df_3.columns or 'Latitude' not in df_3.columns:
    st.warning("Die Daten enthalten keine gültigen Geokoordinaten. Die Karte wird nicht angezeigt.")

# Gesamtdaten-Tabelle anzeigen
st.write('## Gesamtdaten-Tabelle')
st.dataframe(df_3)

# Karte mit Parkhäusern
plot_map(df_3)

# Diagramme unter der Karte in zwei Spalten
col1, col2 = st.columns(2)

with col1:
    plot_gauge(df_3)
    plot_line_chart(df_3)

with col2:
    plot_bar_chart(df_3)
    plot_heatmap(df_3)

# Sicherstellen, dass die 'published'-Spalte datetime ist (und ggf. Zeitzone entfernen)
df_3['published'] = pd.to_datetime(df_3['published'], errors='coerce').dt.tz_localize(None)  # Entferne Zeitzone

# Datumsauswahl für Trendanalyse (konvertiere die Eingabedaten in datetime)
start_date = pd.to_datetime(
    st.date_input("Startdatum", value=df_3['published'].min().date(), key="start_date_input")
).tz_localize(None)
end_date = pd.to_datetime(
    st.date_input("Enddatum", value=df_3['published'].max().date(), key="end_date_input")
).tz_localize(None)

# Filtere den DataFrame nach dem Zeitraum
filtered_df = df_3[(df_3['published'] >= start_date) & (df_3['published'] <= end_date)]

# Change-Point-Analyse und Trendanalyse durchführen
change_point_result = detect_change_points(
    filtered_df,
    timestamp_column='published',
    value_column='auslastungen in prozent',
    model="rbf",  # Modelltyp für Change-Point-Analyse
    penalty=10,    # Empfindlichkeit
    start_date=start_date,  # Nutzerdefiniertes Startdatum
    end_date=end_date       # Nutzerdefiniertes Enddatum
)

# Ergebnisse der Change-Point-Analyse anzeigen
st.write("### Ergebnisse der Change-Point-Analyse")
st.write(f"Change-Points: {change_point_result['change_points']}")
st.write(f"Relevante Intervalle: {change_point_result['intervals']}")

# Zeige die Trends in den Intervallen
st.write("### Trends in den Intervallen")
for trend in change_point_result['trends']:
    st.write(f"Intervall: {trend['start']} - {trend['end']}, Steigung: {trend['slope']}")

# Visualisierung der Change-Points
st.pyplot(change_point_result['plot'])

# Manhattan-Abstand und Clustering der Parkhäuser durchführen
clustered_df = manhattan_main(df_3)  # Clustering direkt auf df_3 anwenden

# Karte mit Parkhäusern und Clustern anzeigen
st.write("## Parkhäuser in Basel-Stadt mit Clustern")
plot_map_with_clusters(clustered_df)  # Verwende das neue Modul zur Kartendarstellung
