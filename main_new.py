import streamlit as st
from datetime import datetime
import pandas as pd
from duckdb.duckdb import dtype

from visual_new import *
from api_new import *
from dashboard import *

### -------- ###

# Seitenkonfiguration
st.set_page_config(
    page_title="Streamlit Dashboard für Visual Analytics",
    layout="wide"
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

### -------- ###

# Sicherstellen, dass 'selected_date' und 'selected_hour' im session_state existieren
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.today().date()

if 'selected_hour' not in st.session_state:
    st.session_state.selected_hour = (datetime.today().hour, datetime.today().hour)

# Datumsauswahl (Startdatum und Enddatum)
start_date = st.sidebar.date_input("Startdatum", datetime.today())
end_date = st.sidebar.date_input("Enddatum", datetime.today())

# Zusätzliche Stundenoptionen (Slider für Start- und Endstunden)
start_hour = st.sidebar.slider("Startstunde", 0, 23, st.session_state.selected_hour[0], 1)
end_hour = st.sidebar.slider("Endstunde", 0, 23, st.session_state.selected_hour[1], 1)

# Update session_state nach der Auswahl
st.session_state.selected_date = start_date  # Nur das Startdatum speichern
st.session_state.selected_hour = (start_hour, end_hour)  # Stunden als Tupel speichern

### -------- ###

# Performance-Messung (optional, je nach Bedarf)
st.sidebar.checkbox("Performance messen", value=False, key="measure_performance")

### -------- ###

# Daten holen und filtern
traffic_data, parking_data, climate_data = load_and_preprocess_data()

### -------- ###

combined_data = pd.concat([traffic_data, parking_data, climate_data])
# Zusammenführen der gefilterten DataFrames

# Konvertiere Datum und Stunde in die richtigen Datentypen
combined_data['Datum'] = pd.to_datetime(combined_data['Datum'], errors='coerce')
combined_data['Stunde'] = pd.to_numeric(combined_data['Stunde'], errors='coerce')

# Filter für das Datum und die Stunde anwenden
filtered_data = filter_data_by_datetime(combined_data, start_date, end_date, start_hour, end_hour)

### -------- ###

# Titel der App
st.title("Dashboard Parkhaus")

# Tabs im Dashboard
tabs_config = [
    {
        'name': 'Visualisierungen',
        'functions': [plot_map(filtered_data),
                      plot_parking_heatmap(filtered_data),
                      plot_parking_by_weekday(filtered_data),
                      plot_parking_vs_traffic(filtered_data),
                      plot_parking_by_hour(filtered_data),
                      plot_3d_scatter(filtered_data)],
        'columns': 2
    },
    {
        'name': 'Tabellen',
        'functions': [display_data_in_expanders(traffic_data, parking_data, climate_data, filtered_data)],
        'columns': 1
    },
    {
        'name': 'Performanz',
        'functions': [measure_performance('Datenladen', fetch_traffic_data)],
        'columns': 1
    },
]

# Dashboard anzeigen
create_dashboard(tabs_config)

# Optional: Performance messen, falls Checkbox aktiviert
if st.sidebar.session_state.get("measure_performance"):
    st.write("Performance-Messung erfolgt...")
    # Hier könntest du z.B. eine Funktion einfügen, die die Ladezeit von spezifischen Funktionen misst
    # measure_performance("Traffic Data Loading", fetch_traffic_data)
