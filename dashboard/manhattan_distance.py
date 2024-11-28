import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Funktion zur Berechnung des Manhattan-Abstands
def manhattan_distance(lat1, lon1, lat2, lon2):
    return abs(lat1 - lat2) + abs(lon1 - lon2)


# Funktion zum Clustering der Parkhäuser mit Manhattan-Abstand
def cluster_parking(df, num_clusters=5):
    # Sicherstellen, dass die Geokoordinaten existieren
    if 'Longitude' not in df.columns or 'Latitude' not in df.columns:
        raise ValueError("Der DataFrame muss die Spalten 'Longitude' und 'Latitude' enthalten.")

    # Standardisierung der geographischen Koordinaten
    scaler = StandardScaler()
    df[['Longitude', 'Latitude']] = scaler.fit_transform(df[['Longitude', 'Latitude']])

    # K-Means Clustering auf den geographischen Daten anwenden
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(df[['Longitude', 'Latitude']])

    return df


def main(df):
    """Berechnet die Manhattan-Distanzen und führt Clustering durch."""
    # Filtere die Parkhäuser mit geographischen Koordinaten
    df_parkhaus = df[df['Kategorie'] == 'Parkhaus']

    # Berechne die Manhattan-Distanzen und führe Clustering durch
    coordinates = df_parkhaus[['Latitude', 'Longitude']].values

    # Wende KMeans-Cluster-Algorithmus an (wähle eine Anzahl an Clustern)
    kmeans = KMeans(n_clusters=5, random_state=42)  # Beispiel: 5 Cluster
    df_parkhaus['Cluster'] = kmeans.fit_predict(coordinates)

    return df_parkhaus
