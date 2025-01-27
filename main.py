# Import der benötigten Bibliotheken
import pandas as pd
import streamlit as st
from api import fetch_traffic_data, fetch_parking_data
import json
from datetime import datetime
import numpy as np
import time
from performancetest import run_performance_test, plot_performance_curve # Importiere Performance-Test-Funktionen
import seaborn as sns
import matplotlib.pyplot as plt
from analyse import berechne_korrelation, visualisiere_korrelation
from visualisierungen import plot_map, plot_vehicle_distribution, plot_traffic_line_chart, plot_traffic_heatmap, \
    plot_parking_occupancy

# Seitenkonfiguration
st.set_page_config(
    page_title="Streamlit Dashboard für Visual Analytics",
    layout="wide"
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Liste, um die erfassten Performanzdaten zu speichern
performance_data = []

# Tabs
tabs = st.tabs(['Visualisierungen', 'Tabellen', 'Korrelationsversuch', 'Performanzanzeige'])

### Hilfsfunktionen
# Funktion zur Messung der Performance
def measure_performance(action, func, *args, **kwargs):
    start_time = time.perf_counter()
    result = func(*args, **kwargs)  # Führt die übergebene Funktion aus
    end_time = time.perf_counter()
    load_time = end_time - start_time
    timestamp = datetime.now()  # Erfasst den aktuellen Zeitstempel
    performance_data.append({
        'action': action,
        'load_time': load_time,
        'timestamp': timestamp  # Fügt den Zeitstempel hinzu
    })
    st.write(f"{action} hat {load_time:.2f} Sekunden gedauert.")  # Zeigt die Ladezeit im Streamlit Dashboard an
    return result

# Geo-Daten umwandeln
def convert_geo_point_to_str(geo_point_dict):
    try:
        return json.dumps(geo_point_dict)
    except Exception as e:
        st.warning(f"Fehler beim Konvertieren der Geo-Daten: {e}")
        return None

# Geo-Daten splitten
def split_geo_point(geo_point):
    try:
        if isinstance(geo_point, str):
            geo_point = json.loads(geo_point)
        if isinstance(geo_point, dict):
            return geo_point.get('lon'), geo_point.get('lat')
    except Exception as e:
        st.warning(f"Fehler beim Verarbeiten der Geo-Daten: {e}")
    return None, None

# Anpassen der Zuweisung für fehlende Zeitfelder
def fill_missing_fields_from_published(row):
    if pd.isna(row['hourfrom']) or pd.isna(row['timefrom']):
        if 'published' in row and not pd.isna(row['published']):
            published_datetime = pd.to_datetime(row['published'])
            row['hourfrom'] = published_datetime.hour
            row['timefrom'] = published_datetime.strftime('%H:%M')
            row['date'] = published_datetime.date()
            row['year'] = published_datetime.year
            row['month'] = published_datetime.month
            row['day'] = published_datetime.day
            row['weekday'] = published_datetime.weekday() + 1
    return row

def render_dashboard_data():
    # Beispiel: Hier würdest du die Daten laden und darstellen
    st.write("Daten werden geladen...")
    time.sleep(1)  # Simuliert das Laden der Daten
    st.write("Daten sind nun sichtbar.")

### Daten erstellen und bearbeiten
# Daten abrufen und Performanz messen
traffic_data = measure_performance("Laden der Verkehrsdaten aus der API", fetch_traffic_data)
parking_data = measure_performance("Laden der Parkhausdaten aus der API", fetch_parking_data)

# Kopien der Originaltabellen
traffic_original = traffic_data.copy()
parking_original = parking_data.copy()

# Längengrad und Breitengrad extrahieren
parking_data['geo_point_2d'] = parking_data['geo_point_2d'].apply(lambda x: convert_geo_point_to_str(x) if isinstance(x, dict) else x)
parking_data['source'] = 'car_park'

traffic_data['geo_point_2d'] = traffic_data['geo_point_2d'].apply(lambda x: convert_geo_point_to_str(x) if isinstance(x, dict) else x)
traffic_data['source'] = 'traffic'

# Tabellen anpassen
traffic_data.rename(columns={'total': 'Total aller Fahrzeuge'}, inplace=True)
parking_data.rename(columns={
    'total': 'Anzahl Plätze insgesamt',
    'free': 'Anzahl freie Parkplätze',
    'auslastungen': 'Anteil belegter Parkplätze in Prozent',
    'title': 'Parkhaustitel'}, inplace=True)

# Tabellen kombinieren
combined_data = pd.concat([traffic_data, parking_data], ignore_index=True)

# Anwendung von fill_missing_fields_from_published
combined_data = combined_data.apply(fill_missing_fields_from_published, axis=1).copy()

# Geo-Daten splitten und direkt zuweisen mit .loc
combined_data.loc[:, 'longitude'], combined_data.loc[:, 'latitude'] = zip(
    *combined_data['geo_point_2d'].apply(split_geo_point)
)

# Spalten bereinigen und umbenennen
combined_data = combined_data.drop(columns=[
    'datetimefrom', 'datetimeto', 'lanecode', 'valuesapproved',
    'valuesedited', 'traffictype', 'timeto', 'dayofyear',
    'timefrom', 'zst_id', 'id', 'id2', 'sitecode',
    'name', 'link', 'published', 'geo_point_2d'
])

combined_data.rename(columns={
    'zst_nr': 'Zählstellennummer',
    'sitename': 'Zählstellenname',
    'directionname': 'Richtung/Strassenseite',
    'lanename': 'Spurnummer',
    'mr': 'Motorrad',
    'pw': 'Personenwagen',
    'pw0': 'Personenwagen mit Anhänger',
    'lief': 'Lieferwagen',
    'lief0': 'Lieferwagen mit Anhänger',
    'lief_aufl': 'Lieferwagen mit Aufflieger',
    'lw': 'Lastwagen',
    'lw0': 'Lastwagen mit Anhänger',
    'sattelzug': 'Sattelzug',
    'bus': 'Bus',
    'andere': 'Nicht klassifizierbare Fahrzeuge',
    'year': 'Jahr',
    'month': 'Monat',
    'day': 'Tag',
    'weekday': 'Wochentag',
    'hourfrom': 'Stunde',
    'date': 'Datum',
    'address': 'Adresse'
}, inplace=True)

# Datentypen
combined_data.loc[:, ['Jahr', 'Monat', 'Tag', 'Stunde']] = combined_data[['Jahr', 'Monat', 'Tag', 'Stunde']].astype(int)

# Datum und Zeitstempel konvertieren
combined_data.loc[:, 'Datum'] = pd.to_datetime(combined_data['Datum'], format='%d.%m.%Y').dt.date
combined_data.loc[:, 'timestamp'] = pd.to_datetime(combined_data['Datum'].astype(str) + ' ' + combined_data['Stunde'].astype(str) + ':00')

# --- Sidebar: Globale Filter für Start- und Enddatum ---
with st.sidebar:
    st.header("Globale Filter")
    st.markdown("### Zeitraum auswählen:")

    if 'start_date' not in st.session_state:
        st.session_state.start_date = combined_data['timestamp'].min()
    if 'end_date' not in st.session_state:
        st.session_state.end_date = combined_data['timestamp'].max()

    start_date = st.date_input("Startdatum auswählen", value=st.session_state.start_date)
    end_date = st.date_input("Enddatum auswählen", value=st.session_state.end_date)
    st.session_state.start_date, st.session_state.end_date = start_date, end_date

    st.markdown("---")
    st.info("Die ausgewählten Filter gelten für alle Visualisierungen und Tabellen.")

# Performanz messen beim Filtern der Daten
filtered_data = measure_performance("Filtern der Daten nach Datum", lambda: combined_data[
    (combined_data['timestamp'] >= pd.to_datetime(start_date)) &
    (combined_data['timestamp'] <= pd.to_datetime(end_date))
])


# --- Tab 1: Tabellen ---
with tabs[1]:
    st.subheader("Original- und kombinierte Tabellen")
    with st.expander("Verkehrsdaten anzeigen", expanded=False):
        st.dataframe(traffic_original)
    with st.expander('Parkhausdaten anzeigen'):
        st.dataframe(parking_original)
    st.subheader("Kombinierte Daten")
    st.dataframe(filtered_data)

# --- Tab 0: Visualisierungen ---
with tabs[0]:
    st.write('#### Visualisierungen zur Verkehrsdichte und Parkhäusern in Basel-Stadt')

    # Aufteilen der Seite in zwei Spalten (links: Karte, rechts: Visualisierungen)
    col1, col2 = st.columns([0.4, 0.6])  # Linke Spalte 40%, rechte Spalte 60%

    with col1:
        # Die Karte auf der linken Seite
        measure_performance('Erstellung der Karte', plot_map, filtered_data)

    with col2:
        # Die rechte Spalte wird in zwei Reihen unterteilt
        # Erste Reihe (oben)
        col3, col4 = st.columns([0.5, 0.5])  # Jede Visualisierung nimmt 50% der Breite der rechten Spalte

        with col3:
            # Diagramm oben links
            measure_performance('Erstellung des Verkehrslinien-Diagramms', plot_traffic_line_chart, filtered_data)
        with col4:
            # Diagramm oben rechts
            measure_performance('Erstellung der Verkehrsdichte-Karte', plot_traffic_heatmap, filtered_data)

        # Zweite Reihe (unten)
        col5, col6 = st.columns([0.5, 0.5])  # Jede Visualisierung nimmt 50% der Breite der rechten Spalte

        with col5:
            # Diagramm unten links
            measure_performance('Erstellung der Fahrzeugverteilung', plot_vehicle_distribution, filtered_data)
        with col6:
            # Diagramm unten rechts
            measure_performance('Erstellung der Parkhausauslastung', plot_parking_occupancy, filtered_data)

# --- Tab 2: Analysen ---
with tabs[2]:  # Tab für die Analyse
    st.subheader("Analyse der Korrelation zwischen Verkehr und Parkhausauslastung")

    # Entfernen der Zeilen mit NaN-Werten in den relevanten Spalten
    filtered_data_clean = filtered_data.dropna(subset=['Total aller Fahrzeuge', 'Anteil belegter Parkplätze in Prozent'])

    # Überprüfen, ob es genügend Variabilität in den Daten gibt
    if filtered_data_clean.empty:
        st.warning("Es sind keine gültigen Daten für die Berechnung der Korrelation vorhanden (alle Daten enthalten NaN-Werte).")
    else:
        if filtered_data_clean['Total aller Fahrzeuge'].nunique() > 1 and filtered_data_clean['Anteil belegter Parkplätze in Prozent'].nunique() > 1:
            # Berechnung der Korrelation
            korrelation = berechne_korrelation(
                filtered_data_clean,
                x_col='Total aller Fahrzeuge',
                y_col='Anteil belegter Parkplätze in Prozent'
            )

            # Anzeige der Korrelation
            st.write(f"Die berechnete Korrelation zwischen Verkehr und Parkhausauslastung beträgt: **{korrelation:.2f}**")

            # Visualisierung der Korrelation
            visualisiere_korrelation(filtered_data_clean, x_col='Total aller Fahrzeuge', y_col='Anteil belegter Parkplätze in Prozent')

        else:
            st.warning("Eine der Spalten enthält nur konstante Werte oder zu viele fehlende Daten. Korrelation kann nicht berechnet werden.")

        # Pearson Korrelation
        korrelation_pearson = filtered_data_clean['Total aller Fahrzeuge'].corr(
            filtered_data_clean['Anteil belegter Parkplätze in Prozent'], method='pearson')

        # Spearman Korrelation
        korrelation_spearman = filtered_data_clean['Total aller Fahrzeuge'].corr(
            filtered_data_clean['Anteil belegter Parkplätze in Prozent'], method='spearman')

        # Kendall Tau Korrelation
        korrelation_kendall = filtered_data_clean['Total aller Fahrzeuge'].corr(
            filtered_data_clean['Anteil belegter Parkplätze in Prozent'], method='kendall')

        # Anzeige der Korrelationen
        st.write(f"Pearson Korrelation: {korrelation_pearson:.2f}")
        st.write(f"Spearman Korrelation: {korrelation_spearman:.2f}")
        st.write(f"Kendall Tau Korrelation: {korrelation_kendall:.2f}")

    # Visualisierungen Tab
    st.write('#### Visualisierungen zur Verkehrsdichte und Parkhausbelegung')

    # Aufteilen der Seite in zwei Spalten (links und rechts)
    col1, col2 = st.columns(2)  # 2 Spalten erstellen

    with col1:
        # Erste Reihe in der ersten Spalte
        st.subheader('Streudiagramm: Total aller Fahrzeuge vs. Anteil belegter Parkplätze in Prozent')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=filtered_data_clean, x='Total aller Fahrzeuge', y='Anteil belegter Parkplätze in Prozent', ax=ax)
        ax.set_title('Scatter Plot: Total aller Fahrzeuge vs. Anteil belegter Parkplätze in Prozent')
        ax.set_xlabel('Total aller Fahrzeuge')
        ax.set_ylabel('Anteil belegter Parkplätze in Prozent')
        st.pyplot(fig)

        # Zweite Reihe in der ersten Spalte
        st.subheader('Korrelation Heatmap')
        corr_matrix = filtered_data_clean.corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
        ax.set_title('Korrelation zwischen den numerischen Variablen')
        st.pyplot(fig)

    with col2:
        # Erste Reihe in der zweiten Spalte
        st.subheader('Boxplot: Verteilung der totalen Fahrzeuganzahl')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=filtered_data_clean, x='Total aller Fahrzeuge', ax=ax)
        ax.set_title('Boxplot: Verteilung der totalen Fahrzeuganzahl')
        st.pyplot(fig)  # Streamlit Plot

        # Zweite Reihe in der zweiten Spalte
        st.subheader('Violin Plot: Verteilung des Anteils belegter Parkplätze')
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.violinplot(data=filtered_data_clean, x='Anteil belegter Parkplätze in Prozent', ax=ax)
        ax.set_title('Violin Plot: Verteilung des Anteils belegter Parkplätze')
        st.pyplot(fig)  # Streamlit Plot

# --- Tab 3: Performanz ---
# Beispiel-Funktion für das Testen der Ladezeit: Rendern eines Teils des Dashboards
with tabs[3]:
    st.title("Dashboard Performanztest")

    # Performanztest durchführen
    if st.button("Performanztest starten"):
        repetitions = 10  # Anzahl der Wiederholungen des Tests
        st.write(f"Starte Performanztest mit {repetitions} Wiederholungen...")

        # Test durchführen
        times = run_performance_test(repetitions, render_dashboard_data)

        # Performanzkurve zeichnen
        st.write("Performanzkurve:")
        plot_performance_curve(times)

    # Performanzdaten anzeigen
    st.subheader("Erfasste Performanzdaten")

    if performance_data:
        performance_df = pd.DataFrame(performance_data)
        st.dataframe(performance_df)
    else:
        st.write("Es wurden noch keine Performanzdaten erfasst.")
    # Performanzkurve zeichnen
    st.subheader("Performanzkurve")
    plot_performance_curve(performance_data)

    # Tabelle mit den Performanzdaten
    performance_df = pd.DataFrame(performance_data)
    st.dataframe(performance_df)

    # Performanzkurve zeichnen
    st.subheader("Performanzkurve")
    plot_performance_curve(performance_data)




