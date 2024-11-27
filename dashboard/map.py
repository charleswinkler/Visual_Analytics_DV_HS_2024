import folium
import streamlit as st
from streamlit_folium import st_folium


def plot_map(df):
    """Zeigt die Karte mit den Parkhäusern an."""
    st.write("## Parkhäuser in Basel-Stadt")
    df_parkhaus = df[df['Kategorie'] == 'Parkhaus']
    basel_map = folium.Map(location=[47.5596, 7.5886], zoom_start=13)

    for _, row in df_parkhaus.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['title']}<br>Freie Plätze: {int(row['free'])}<br>Gesamtplätze: {int(row['total'])}",
            tooltip=f"{row['title']} - Freie Plätze: {int(row['free'])} / Gesamt: {int(row['total'])}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(basel_map)

    st_folium(basel_map, width=700, height=500)

