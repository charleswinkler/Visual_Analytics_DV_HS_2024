import requests
import json
import pandas as pd
from dash import Dash, html, dash_table, dcc
import plotly.express as px

# API-Schlüssel und Basis-URL
api_key = "51f70e7235b13a17eebb9f141225c45c53250d54c2035bd5c202f001"
base_url = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/"

# Erster Datensatz einlesen
dataset1_url = f"{base_url}100088/records?apikey={api_key}"
response1 = requests.get(dataset1_url)
if response1.status_code == 200:
    dataset1 = response1.json()  # Daten in einer Variablen speichern
    print("Datensatz 1 erfolgreich geladen.")
else:
    print(f"Fehler beim Laden von Datensatz 1: {response1.status_code}")

# Zweiter Datensatz einlesen
dataset2_url = f"{base_url}100009/records?apikey={api_key}&limit=20"
response2 = requests.get(dataset2_url)
if response2.status_code == 200:
    dataset2 = response2.json()  # Daten in einer Variablen speichern
    print("Datensatz 2 erfolgreich geladen.")
else:
    print(f"Fehler beim Laden von Datensatz 2: {response2.status_code}")

# Beide Datensätze als JSON-Dateien speichern
with open('dataset1.json', 'w') as f:
    json.dump(dataset1, f)

with open('dataset2.json', 'w') as f:
    json.dump(dataset2, f)

print("Datensätze wurden erfolgreich gespeichert.")

# Kombinieren der Datensätze
combined_data = dataset1['results'] + dataset2['results']
print(f"Anzahl kombinierter Datensätze: {len(combined_data)}")

# DataFrames erstellen
df_1 = pd.DataFrame(dataset1['results'])  # Nur die 'results' verwenden
df_2 = pd.DataFrame(dataset2['results'])  # Nur die 'results' verwenden

# Umwandeln von geo_point_2d in separate Spalten
if 'geo_point_2d' in df_1.columns:
    df_1['lon'] = df_1['geo_point_2d'].apply(lambda x: x['lon'] if x is not None else None)
    df_1['lat'] = df_1['geo_point_2d'].apply(lambda x: x['lat'] if x is not None else None)
    df_1 = df_1.drop(columns=['geo_point_2d'], errors='ignore')  # Optional: Ursprüngliche Spalte entfernen

# Dash-App initialisieren
app = Dash()

app.layout = [
    html.Div(children='Parkhaus Klima'),
    dash_table.DataTable(data=df_1.to_dict('records'), page_size=10),  # Hier 'records' verwenden
    dcc.Graph(figure=px.histogram(df_1, x='title', y='free'))
]

if __name__ == '__main__':
    app.run(debug=True)
