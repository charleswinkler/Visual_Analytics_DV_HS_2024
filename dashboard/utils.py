import pandas as pd
import streamlit as st

def extract_coordinates(row):
    geo_point = row.get('geo_point_2d')
    coords = row.get('coords')
    lon, lat = (geo_point or coords or {}).get('lon'), (geo_point or coords or {}).get('lat')
    return pd.Series([lon, lat])

def filter_by_date(df, date_column, default_start=None, default_end=None, key_prefix=""):
    """
    Filtert einen DataFrame basierend auf der Datumsauswahl des Benutzers.

    :param df: Der DataFrame, der gefiltert werden soll
    :param date_column: Die Spalte mit Datumseinträgen
    :param default_start: Standard-Startdatum (falls keine Benutzerangabe)
    :param default_end: Standard-Enddatum (falls keine Benutzerangabe)
    :param key_prefix: Präfix für die Streamlit-Schlüssel (bei mehrfacher Nutzung)
    :return: Gefilterter DataFrame und die ausgewählten Start-/Enddaten
    """
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce').dt.tz_localize(None)

    if default_start is None:
        default_start = df[date_column].min().date()
    if default_end is None:
        default_end = df[date_column].max().date()

    start_date = pd.to_datetime(
        st.date_input(f"{key_prefix}Startdatum", value=default_start, key=f"{key_prefix}_start_date_input")
    ).tz_localize(None)
    end_date = pd.to_datetime(
        st.date_input(f"{key_prefix}Enddatum", value=default_end, key=f"{key_prefix}_end_date_input")
    ).tz_localize(None)

    filtered_df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
    return filtered_df, start_date, end_date

