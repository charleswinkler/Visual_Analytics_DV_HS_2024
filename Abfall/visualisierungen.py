# Modul für Visualisierungen (z.B. Diagramme, Plots)

import plotly.express as px
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium


# --- Visualisierungsfunktionen ---
def plot_map(df):
    """Zeigt eine Karte mit Parkhäusern und Zählstellen, basierend auf dem globalen Enddatum-Filter."""
    st.write("Karte mit Parkhäusern und Zählstellen")

    # Daten für die Karte basierend auf dem globalen Enddatum filtern
    filtered_data = df[df['timestamp'] <= pd.to_datetime(st.session_state.end_date)]

    # Prüfen, ob es Daten für die Karte gibt
    if filtered_data.empty:
        st.warning("Keine Daten für das ausgewählte Enddatum verfügbar.")
        return

    # Basiskarte zentrieren auf Basel
    basel_map = folium.Map(location=[47.5596, 7.5886], zoom_start=13)

    # Markierungen für die Karte hinzufügen
    for _, row in filtered_data.iterrows():
        if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
            if row.get('source') == 'car_park':
                popup_content = f"{row['Parkhaustitel']} - Frei: {row['Anzahl freie Parkplätze']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_content,
                    tooltip=row['Parkhaustitel'],
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(basel_map)
            elif row.get('source') == 'traffic':
                popup_content = f"{row['Zählstellenname']} - Fahrzeuge: {row['Total aller Fahrzeuge']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_content,
                    tooltip=row['Zählstellenname'],
                    icon=folium.Icon(color='green', icon='stats')
                ).add_to(basel_map)

    # Karte anzeigen
    st_folium(basel_map, width=700, height=500)


def plot_traffic_line_chart(df):
    """Zeigt das Liniendiagramm der Verkehrsdichte nach Stunden an."""
    # st.write("Verkehrsdichte nach Stunden")
    if df.empty:
        st.warning("Keine Daten für die ausgewählten Filter verfügbar.")
        return

    vehicle_types = ['Motorrad', 'Personenwagen', 'Lastwagen', 'Bus']
    fig = go.Figure()
    for vehicle in vehicle_types:
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df[vehicle], mode='lines', name=vehicle))
    fig.update_layout(title="Verkehrsdichte nach Stunden", xaxis_title="Zeit", yaxis_title="Anzahl Fahrzeuge")
    st.plotly_chart(fig)


def plot_parking_occupancy(df):
    """Zeigt die Parkplatzbelegung im Zeitverlauf an."""
    # st.write("Parkplatzbelegung im Zeitverlauf")
    if df.empty:
        st.warning("Keine Daten für die ausgewählten Filter verfügbar.")
        return

    df['occupied_parking'] = df['Anzahl Plätze insgesamt'] - df['Anzahl freie Parkplätze']
    fig = px.line(df, x='timestamp', y='occupied_parking', title="Parkplatzbelegung im Zeitverlauf")
    st.plotly_chart(fig)


def plot_traffic_heatmap(df):
    """Zeigt eine Heatmap der Verkehrsdichte nach Zeit und Zählstelle an."""
    # st.write("Heatmap der Verkehrsdichte")
    if df.empty:
        st.warning("Keine Daten für die ausgewählten Filter verfügbar.")
        return

    heatmap_data = df.groupby(['Zählstellenname', 'timestamp'])['Total aller Fahrzeuge'].sum().reset_index()
    fig = px.density_heatmap(
        heatmap_data,
        x='timestamp',
        y='Zählstellenname',
        z='Total aller Fahrzeuge',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(title="Verkehrsdichte Heatmap", xaxis_title="Zeit", yaxis_title="Zählstelle")
    st.plotly_chart(fig)


def plot_vehicle_distribution(df):
    """Zeigt ein Kreisdiagramm der Fahrzeugverteilung an."""
    # st.write("Fahrzeugverteilung")
    if df.empty:
        st.warning("Keine Daten für die ausgewählten Filter verfügbar.")
        return

    vehicle_types = ['Motorrad', 'Personenwagen', 'Lastwagen', 'Bus']
    vehicle_counts = {vehicle: df[vehicle].sum() for vehicle in vehicle_types}
    fig = px.pie(values=list(vehicle_counts.values()), names=list(vehicle_counts.keys()), title="Fahrzeugverteilung")
    st.plotly_chart(fig)
