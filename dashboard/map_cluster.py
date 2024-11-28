import folium
import streamlit as st
from streamlit_folium import st_folium


def plot_map_with_clusters(df):
    """Zeigt die Karte mit den Parkhäusern und deren Clustern an."""
    # st.write("## hier einen Titel einführen, wenn erwünscht")

    # Filtere nur die Parkhäuser aus
    df_parkhaus = df[df['Kategorie'] == 'Parkhaus']

    # Basiskarte von Basel-Stadt erstellen
    basel_map = folium.Map(location=[47.5596, 7.5886], zoom_start=13)

    # Clusterfarben definieren (für eine maximale Anzahl von 5 Clustern)
    cluster_colors = {
        0: 'blue',
        1: 'green',
        2: 'red',
        3: 'purple',
        4: 'orange'
    }

    # Iteriere durch die Parkhäuser und füge Marker hinzu
    for _, row in df_parkhaus.iterrows():
        cluster = row['Cluster']  # Cluster-ID
        color = cluster_colors.get(cluster, 'gray')  # Standardfarbe: Grau, wenn Cluster nicht vorhanden

        # Marker für das Parkhaus hinzufügen
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['title']}<br>Freie Plätze: {int(row['free'])}<br>Gesamtplätze: {int(row['total'])}",
            tooltip=f"{row['title']} - Freie Plätze: {int(row['free'])} / Gesamt: {int(row['total'])}",
            icon=folium.Icon(color=color, icon='info-sign')
        ).add_to(basel_map)

    # Karte in Streamlit anzeigen
    st_folium(basel_map, width=700, height=500)
