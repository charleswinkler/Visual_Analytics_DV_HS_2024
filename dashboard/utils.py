import pandas as pd

def extract_coordinates(row):
    """Extrahiert die Geokoordinaten (Longitude, Latitude) aus einer Zeile."""
    geo_point = row.get('geo_point_2d')
    coords = row.get('coords')
    lon, lat = (geo_point or coords or {}).get('lon'), (geo_point or coords or {}).get('lat')
    return pd.Series([lon, lat])
