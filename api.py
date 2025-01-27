import requests
import pandas as pd
import streamlit as st

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Datensatz-IDs für Verkehrsdaten und Parkhausbelegung
traffic_dataset_id = "100006"
parking_dataset_id = "100014"


@st.cache_data
def fetch_data(dataset_id, limit=100, offset=0, order_by=None):
    """Holt die Daten für einen gegebenen Datensatz aus der API und gibt sie als DataFrame zurück"""
    url = f"{base_url}{dataset_id}/records"
    params = {
        'apikey': api_key,
        'limit': limit,  # Anzahl der Datensätze pro Anfrage
        'offset': offset  # Offset für Pagination
    }

    if order_by:
        params['order_by'] = order_by  # Sortierung nach Spalte

    # API-Anfrage senden
    response = requests.get(url, params=params)

    # Ausgabe der vollständigen URL und der Antwort
    print(f"Angeforderte URL: {response.url}")
    print(f"Antwort: {response.status_code}")

    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data['results'])  # 'results' enthält die eigentlichen Datensätze
    else:
        raise Exception(f"Fehler beim Abrufen der Daten: {response.status_code}")


@st.cache_data
def fetch_traffic_data():
    """Holt die Verkehrsdaten und gibt sie als DataFrame zurück, sortiert von neu nach alt"""
    traffic_data = []

    # Pagination-Parameter initialisieren
    offset = 0
    limit = 100  # Anzahl der Datensätze pro Anfrage
    max_records = 10000  # Maximal abzurufende Datensätze

    while True:
        # Abrufen der Daten mit Sortierung von neu nach alt
        traffic_data_batch = fetch_data(
            traffic_dataset_id,
            limit=limit,
            offset=offset,
            order_by='datetimefrom desc'  # Sortierung absteigend nach datetimefrom
        )

        if traffic_data_batch.empty:
            break  # Stoppe, wenn keine weiteren Daten verfügbar sind

        traffic_data.append(traffic_data_batch)
        offset += limit  # Erhöhe den Offset für die nächste Anfrage

        if offset >= max_records:  # Begrenzung auf maximal 10.000 Datensätze
            break

    # Kombiniere alle DataFrames in einen einzelnen DataFrame
    return pd.concat(traffic_data, ignore_index=True)


@st.cache_data
def fetch_parking_data():
    """Holt die Parkhausbelegungsdaten und gibt sie als DataFrame zurück, sortiert von neu nach alt"""
    parking_data = []

    # Pagination-Parameter initialisieren
    offset = 0
    limit = 100  # Anzahl der Datensätze pro Anfrage
    max_records = 10000  # Maximal abzurufende Datensätze

    while True:
        # Abrufen der Daten mit Sortierung von neu nach alt
        parking_data_batch = fetch_data(
            parking_dataset_id,
            limit=limit,
            offset=offset,
            order_by='published desc'  # Sortierung absteigend nach published
        )

        if parking_data_batch.empty:
            break  # Stoppe, wenn keine weiteren Daten verfügbar sind

        parking_data.append(parking_data_batch)
        offset += limit  # Erhöhe den Offset für die nächste Anfrage

        if offset >= max_records:  # Begrenzung auf maximal 10.000 Datensätze
            break

    # Kombiniere alle DataFrames in einen einzelnen DataFrame
    return pd.concat(parking_data, ignore_index=True)

