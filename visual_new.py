import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from folium.plugins import MarkerCluster
from geopy.distance import geodesic
import plotly.express as px
from datetime import datetime


#### ---------- ###

# Zeitfilter
def filter_data_by_datetime(data, start_date, end_date, start_hour, end_hour):
    # Sicherstellen, dass Datum und Stunde korrekt sind
    data['Datum'] = pd.to_datetime(data['Datum'], errors='coerce')
    data = data.dropna(subset=['Datum', 'Stunde'])  # Fehlende Werte entfernen
    data['Stunde'] = data['Stunde'].astype(int)

    # Nur das Datum behalten (keine Uhrzeit)
    data['Datum'] = data['Datum'].dt.date

    # Datum filtern
    date_filtered = data[(data['Datum'] >= start_date) & (data['Datum'] <= end_date)]

    # Zeitfilter: Wenn über Mitternacht geht, zwei Bereiche kombinieren
    if start_hour <= end_hour:
        time_filtered = date_filtered[(date_filtered['Stunde'] >= start_hour) & (date_filtered['Stunde'] <= end_hour)]
    else:
        time_filtered = date_filtered[(date_filtered['Stunde'] >= start_hour) | (date_filtered['Stunde'] <= end_hour)]

    return time_filtered


#### ---------- ###

def plot_map(df):
    """Zeigt eine Karte mit Parkhäusern, Verkehrszählstellen und Klimastationen für das ausgewählte Datum und die Stunde."""
    st.write("Karte mit Parkhäusern, Verkehrszählstellen und Klimastationen")

    # Start- und Endzeit berechnen
    selected_date = st.session_state.selected_date
    start_hour, end_hour = st.session_state.selected_hour

    if start_hour <= end_hour:
        start_datetime = datetime.combine(selected_date, datetime.min.time()) + pd.Timedelta(hours=start_hour)
        end_datetime = datetime.combine(selected_date, datetime.min.time()) + pd.Timedelta(hours=end_hour)
    else:
        start_datetime = datetime.combine(selected_date, datetime.min.time()) + pd.Timedelta(hours=start_hour)
        end_datetime = datetime.combine(selected_date, datetime.min.time()) + pd.Timedelta(hours=23)  # Bis Mitternacht

    st.write("Startzeit:", start_datetime, "Endzeit:", end_datetime)

    # Filter nach dem Zeitraum
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    filtered_data = df[(df['timestamp'] >= start_datetime) & (df['timestamp'] <= end_datetime)]

    # Sidebar-Optionen für die Anzeige der Marker
    st.sidebar.header("Marker anzeigen für Karte:")
    show_car_parks = st.sidebar.checkbox("Parkhäuser anzeigen", value=True)
    show_traffic_stations = st.sidebar.checkbox("Verkehrszählstationen anzeigen", value=True)
    show_weather_stations = st.sidebar.checkbox("Wetterstationen anzeigen", value=True)

    # Neue Sidebar-Option für Kartenansicht
    cluster_view = st.sidebar.radio("Kartenansicht", ["Clusteransicht", "Normalansicht"], index=0)

    # Warnung, falls keine Checkbox aktiv
    if not (show_car_parks or show_traffic_stations or show_weather_stations):
        st.warning("Bitte mindestens eine Datenquelle auswählen.")
        return

    if filtered_data.empty:
        st.warning("Keine Daten für die ausgewählte Stunde verfügbar.")
        return

    # Basiskarte zentrieren auf Basel
    basel_map = folium.Map(location=[47.5596, 7.5886], zoom_start=13)

    # Falls Clusteransicht aktiviert ist, erstelle MarkerCluster
    marker_group = MarkerCluster().add_to(basel_map) if cluster_view == "Clusteransicht" else basel_map

    # Markierungen für die Karte hinzufügen
    for _, row in filtered_data.iterrows():
        if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
            # Parkhäuser anzeigen, wenn ausgewählt
            if show_car_parks and row.get('source') == 'car_park':
                popup_content = f"{row['Parkhaustitel']} - Frei: {row['Anzahl freie Parkplätze']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_content,
                    tooltip=row['Parkhaustitel'],
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(marker_group)

            # Verkehrszählstationen anzeigen, wenn ausgewählt
            elif show_traffic_stations and row.get('source') == 'traffic':
                popup_content = f"{row['Zählstellenname']} - Fahrzeuge: {row['Total aller Fahrzeuge']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_content,
                    tooltip=row['Zählstellenname'],
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(marker_group)

            # Wetterstationen anzeigen, wenn ausgewählt
            elif show_weather_stations and row.get('source') == 'weather':
                popup_content = f"{row['Name der Wetterstation']} - Lufttemperatur: {row['Lufttemperatur in Celsius']}°C"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_content,
                    tooltip=row['Name der Wetterstation'],
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(marker_group)

    # Karte anzeigen
    st_folium(basel_map, width=700, height=500)


#### ---------- ###

def plot_parking_heatmap(df):
    """Erstellt eine Heatmap, die den Anteil belegter Parkplätze nach Wochentag und Stunde zeigt."""

    # Gruppieren der Daten nach Wochentag und Stunde und Berechnen des durchschnittlichen Anteils belegter Parkplätze
    df['Wochentag'] = df['Wochentag'].astype(str)  # Falls Wochentag als Integer vorliegt
    heatmap_data = df.pivot_table(index='Stunde', columns='Wochentag', values='Anteil belegter Parkplätze in Prozent',
                                  aggfunc='mean')

    # Heatmap erstellen
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".2f", linewidths=0.5)
    plt.title("Heatmap: Anteil belegter Parkplätze nach Wochentag und Stunde")
    st.pyplot(plt)

#### ---------- ###

def plot_parking_by_weekday(df):
    """Erstellt ein Balkendiagramm, das die durchschnittliche Parkhausbelegung nach Wochentag zeigt."""

    # Gruppieren der Daten nach Wochentag und Berechnen des durchschnittlichen Anteils belegter Parkplätze
    parkhaus_by_weekday = df.groupby('Wochentag')['Anteil belegter Parkplätze in Prozent'].mean()

    # Balkendiagramm erstellen
    plt.figure(figsize=(10, 6))
    parkhaus_by_weekday.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Durchschnittliche Parkhausbelegung nach Wochentag')
    plt.xlabel('Wochentag')
    plt.ylabel('Durchschnittlicher Anteil belegter Parkplätze in %')
    st.pyplot(plt)

#### ---------- ###

def plot_parking_vs_traffic(df):
    """Erstellt ein Scatterplot, das die Parkhausbelegung im Vergleich zur Anzahl der Fahrzeuge an Verkehrszählstationen zeigt."""

    # Scatterplot erstellen
    plt.figure(figsize=(10, 6))
    plt.scatter(df['Total aller Fahrzeuge'], df['Anteil belegter Parkplätze in Prozent'], alpha=0.5, color='green')
    plt.title('Parkhausbelegung vs. Verkehrszählstation')
    plt.xlabel('Anzahl Fahrzeuge (Verkehrszählstation)')
    plt.ylabel('Anteil belegter Parkplätze in %')
    st.pyplot(plt)

#### ---------- ###

def plot_parking_temperature_gauge(df):
    """Erstellt ein Gauge-Diagramm, das den Zusammenhang zwischen Temperatur und Parkhausbelegung zeigt."""

    # Berechnung des mittleren Anteils belegter Parkplätze bei unterschiedlichen Temperaturen
    avg_parking_by_temp = df.groupby('Lufttemperatur in Celsius')['Anteil belegter Parkplätze in Prozent'].mean()

    # Gauge-Diagramm erstellen
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_parking_by_temp.mean(),
        title={'text': "Durchschnittliche Parkhausbelegung bei Temperatur"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "green"},
               'steps': [{'range': [0, 50], 'color': "lightgray"},
                         {'range': [50, 75], 'color': "yellow"},
                         {'range': [75, 100], 'color': "red"}]}
    ))

    fig.update_layout(height=400)
    st.plotly_chart(fig)

#### ---------- ###

def plot_parking_by_hour(df):
    """Erstellt ein Liniendiagramm, das die durchschnittliche Parkhausbelegung nach Stunde des Tages zeigt."""

    # Gruppieren der Daten nach Stunde und Berechnen des durchschnittlichen Anteils belegter Parkplätze
    parkhaus_by_hour = df.groupby('Stunde')['Anteil belegter Parkplätze in Prozent'].mean()

    # Liniendiagramm erstellen
    plt.figure(figsize=(10, 6))
    parkhaus_by_hour.plot(kind='line', color='blue', marker='o')
    plt.title('Durchschnittliche Parkhausbelegung nach Stunde des Tages')
    plt.xlabel('Stunde des Tages')
    plt.ylabel('Durchschnittlicher Anteil belegter Parkplätze in %')
    st.pyplot(plt)

#### ---------- ###

def plot_3d_scatter(df):
    """
    Erstellt eine 3D-Streudiagramm mit den drei Variablen für das ausgewählte Datum und die Stunde.

    :param df: Das DataFrame, das die relevanten Variablen enthält.
    """
    # Filter nach ausgewähltem Datum und Stunde
    filtered_data = df[(df['timestamp'].dt.date == st.session_state.selected_date) &
                       (df['timestamp'].dt.hour == st.session_state.selected_hour[0])]

    fig = px.scatter_3d(filtered_data,
                        x='Anteil belegter Parkplätze in Prozent',
                        y='Total aller Fahrzeuge',
                        z='Lufttemperatur in Celsius',
                        color='Regen in 1 h',  # Farbe als vierte Dimension
                        title="3D-Visualisierung von Parkhausbelegung, Verkehrsdichte und Klimadaten")
    st.plotly_chart(fig)
