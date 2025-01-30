import requests
import pandas as pd
import streamlit as st
import json

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Datensatz-IDs
traffic_dataset_id = "100006"
parking_dataset_id = "100014"
climate_dataset_id = "100009"


# Caching der Fetch-Daten-Funktion, die für alle Datenquellen verwendet wird
@st.cache_data
def fetch_data(dataset_id, limit=100, offset=0, order_by=None):
    """Holt die Daten für einen gegebenen Datensatz aus der API und gibt sie als DataFrame zurück"""
    url = f"{base_url}{dataset_id}/records"
    params = {
        "apikey": api_key,
        "limit": limit,
        "offset": offset,
    }
    if order_by:
        params["order_by"] = order_by

    # API-Anfrage senden
    response = requests.get(url, params=params)

    # Ausgabe der vollständigen URL und der Antwort
    print(f"Angeforderte URL: {response.url}")
    print(f"Antwort: {response.status_code}")

    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()
        # Prüfen, ob "results" existiert und nicht leer ist
        if "results" in data and data["results"]:
            return pd.DataFrame(data["results"])
        else:
            return pd.DataFrame()  # Leeres DataFrame zurückgeben
    else:
        raise Exception(f"Fehler beim Abrufen der Daten: {response.status_code}")


# Caching der Paginierungs-Funktion
@st.cache_data
def fetch_paginated_data(dataset_id, order_by, max_records=10000):
    """Holt die Daten für einen Datensatz mit Pagination und gibt sie als DataFrame zurück"""
    data = []
    offset = 0
    limit = 100  # Maximal 100 Datensätze pro Anfrage

    while offset < max_records:
        data_batch = fetch_data(dataset_id, limit=limit, offset=offset, order_by=order_by)
        if data_batch.empty:
            print(f"Keine weiteren Daten verfügbar. Abbruch bei Offset {offset}.")
            break
        data.append(data_batch)
        offset += limit

    # Kombiniere alle DataFrames in einen einzelnen DataFrame
    return pd.concat(data, ignore_index=True) if data else pd.DataFrame()


# Spezifische Caching-Funktionen für die Datensätze
@st.cache_data
def fetch_climate_data():
    """Holt die Klimadaten und gibt sie als DataFrame zurück"""
    return fetch_paginated_data(climate_dataset_id, order_by="dates_max_date desc")


@st.cache_data
def fetch_traffic_data():
    """Holt die Verkehrsdaten und gibt sie als DataFrame zurück"""
    return fetch_paginated_data(traffic_dataset_id, order_by="datetimefrom desc")


@st.cache_data
def fetch_parking_data():
    """Holt die Parkhausbelegungsdaten und gibt sie als DataFrame zurück"""
    return fetch_paginated_data(parking_dataset_id, order_by="published desc")

# Caching der Bereinigungs- und Umbenennungsfunktion
@st.cache_data
def clean_and_rename_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bereinigt und benennt die Spalten eines DataFrames und konvertiert Datentypen.
    """
    # Spalten umbenennen
    df = df.rename(columns={
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
        'address': 'Adresse',
        'meta_airtemp': 'Lufttemperatur in Celsius',
        'meta_rain_1h_val': 'Regen in 1 h',
        'meta_rain24h_sum': 'Regen in 24 h',
        'meta_rain48h_sum': 'Regen in 48 h',
        'name_custom': 'Name der Wetterstation'
    })

    # Datentypen anpassen
    df.loc[:, ['Jahr', 'Monat', 'Tag', 'Stunde']] = df[['Jahr', 'Monat', 'Tag', 'Stunde']].astype(int)

    # Datum und Zeitstempel konvertieren
    df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y').dt.date
    df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce') 
    df['Datum'] = df['Datum'].dt.date  # Entfernt die Uhrzeit
    df['timestamp'] = pd.to_datetime(df['Datum'].astype(str) + ' ' + df['Stunde'].astype(str) + ':00')

    return df


# Caching der Geo-Datenfunktionen
@st.cache_data
def convert_geo_point_to_str(geo_point_dict):
    try:
        return json.dumps(geo_point_dict)
    except Exception as e:
        st.warning(f"Fehler beim Konvertieren der Geo-Daten: {e}")
        return None


@st.cache_data
def split_geo_point(geo_point):
    try:
        if isinstance(geo_point, str):
            geo_point = json.loads(geo_point)
        if isinstance(geo_point, dict):
            return geo_point.get('lon'), geo_point.get('lat')
    except Exception as e:
        st.warning(f"Fehler beim Verarbeiten der Geo-Daten: {e}")
    return None, None


# Caching der Funktion zum Ausfüllen fehlender Zeitfelder
@st.cache_data
def fill_missing_fields_from_dates(row):
    """
    Füllt die fehlenden Zeitfelder (hourfrom, timefrom, date, year, month, day, weekday)
    basierend auf den Feldern 'published' oder 'dates_max_date'.
    """
    # Überprüfen, ob die Spalten 'hourfrom' und 'timefrom' existieren
    if pd.isna(row.get('hourfrom')) or pd.isna(row.get('timefrom')):
        # Prüfen, ob 'published' vorhanden ist und nicht leer
        if 'published' in row and not pd.isna(row['published']):
            published_datetime = pd.to_datetime(row['published'])
            row['hourfrom'] = published_datetime.hour
            row['timefrom'] = published_datetime.strftime('%H:%M')
            row['date'] = published_datetime.date()
            row['year'] = published_datetime.year
            row['month'] = published_datetime.month
            row['day'] = published_datetime.day
            row['weekday'] = published_datetime.weekday() + 1
        # Wenn 'published' nicht vorhanden ist, 'dates_max_date' verwenden
        elif 'dates_max_date' in row and not pd.isna(row['dates_max_date']):
            dates_max_datetime = pd.to_datetime(row['dates_max_date'])
            row['hourfrom'] = dates_max_datetime.hour
            row['timefrom'] = dates_max_datetime.strftime('%H:%M')
            row['date'] = dates_max_datetime.date()
            row['year'] = dates_max_datetime.year
            row['month'] = dates_max_datetime.month
            row['day'] = dates_max_datetime.day
            row['weekday'] = dates_max_datetime.weekday() + 1
    return row

# Diese Funktion übernimmt dann alles
@st.cache_data
def load_and_preprocess_data():
    # Daten abrufen
    traffic_data = fetch_traffic_data()
    parking_data = fetch_parking_data()
    climate_data = fetch_climate_data()

    # Weitere Verarbeitung
    traffic_data['source'] = 'traffic'
    parking_data['source'] = 'car_park'
    climate_data['source'] = 'climate'

    # Geo-Daten konvertieren (Funktion wird aufgerufen)
    traffic_data['geo_point_2d'] = traffic_data['geo_point_2d'].apply(
        lambda x: convert_geo_point_to_str(x) if isinstance(x, dict) else x)
    parking_data['geo_point_2d'] = parking_data['geo_point_2d'].apply(
        lambda x: convert_geo_point_to_str(x) if isinstance(x, dict) else x)
    climate_data['geo_point_2d'] = climate_data['coords'].apply(
        lambda x: convert_geo_point_to_str(x) if isinstance(x, dict) else x)

    # Split Geo-Point-Daten in separate Spalten (Longitude, Latitude)
    traffic_data[['longitude', 'latitude']] = traffic_data['geo_point_2d'].apply(split_geo_point).apply(pd.Series)
    parking_data[['longitude', 'latitude']] = parking_data['geo_point_2d'].apply(split_geo_point).apply(pd.Series)
    climate_data[['longitude', 'latitude']] = climate_data['geo_point_2d'].apply(split_geo_point).apply(pd.Series)

    # Fehlende Zeitfelder auffüllen (Funktion wird aufgerufen)
    traffic_data = traffic_data.apply(fill_missing_fields_from_dates, axis=1)
    parking_data = parking_data.apply(fill_missing_fields_from_dates, axis=1)
    climate_data = climate_data.apply(fill_missing_fields_from_dates, axis=1)

    # Bereinigen und Umbenennen der Spalten (Funktion wird aufgerufen)
    traffic_data = clean_and_rename_data(traffic_data)
    parking_data = clean_and_rename_data(parking_data)
    climate_data = clean_and_rename_data(climate_data)

    # Spalten umbenennen, speziell für Verkehrsdaten und Parkhausdaten
    traffic_data.rename(columns={'total': 'Total aller Fahrzeuge'}, inplace=True)
    parking_data.rename(columns={
        'total': 'Anzahl Plätze insgesamt',
        'free': 'Anzahl freie Parkplätze',
        'auslastungen': 'Anteil belegter Parkplätze in Prozent',
        'title': 'Parkhaustitel'}, inplace=True)

    # Die finalen DataFrames zurückgeben
    return traffic_data, parking_data, climate_data
