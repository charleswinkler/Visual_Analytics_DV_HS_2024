import requests
import json
import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input
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

# Erstellen von DataFrames aus den geladenen Datensätzen
df_1 = pd.DataFrame(dataset1['results'])
df_2 = pd.DataFrame(dataset2['results'])

# 1. Kategorie-Spalte hinzufügen:
df_1['Kategorie'] = 'Parkhaus'
df_2['Kategorie'] = 'Klima'

# 2. Umbenennen der relevanten Spalten in df_2, damit sie zu den Spalten in df_1 passen:
df_2 = df_2.rename(columns={
    'name_original': 'id2',
    'name_custom': 'title',
    'dates_max_date': 'published',
    'stadtklima_basel_link': 'link'
})

# 3. Geographische Daten extrahieren und aufteilen
def extract_coordinates(row):
    # Überprüfen und Extrahieren von geo_point_2d
    geo_point = row.get('geo_point_2d')
    coords = row.get('coords')

    # Standardwerte für Longitude und Latitude
    lon, lat = None, None

    # Wenn geo_point_2d vorhanden ist
    if isinstance(geo_point, dict) and 'lon' in geo_point and 'lat' in geo_point:
        lon, lat = geo_point['lon'], geo_point['lat']

    # Wenn coords vorhanden ist
    if isinstance(coords, dict) and 'lon' in coords and 'lat' in coords:
        lon, lat = coords['lon'], coords['lat']

    return pd.Series([lon, lat])

# Anwenden der Funktion auf beide DataFrames und neue Spalten erstellen
df_1[['Longitude', 'Latitude']] = df_1.apply(extract_coordinates, axis=1)
df_2[['Longitude', 'Latitude']] = df_2.apply(extract_coordinates, axis=1)

# Entfernen der geo_point_2d Spalte
df_1 = df_1.drop(columns=['geo_point_2d', 'coords'], errors='ignore')
df_2 = df_2.drop(columns=['geo_point_2d', 'coords'], errors='ignore')

# 4. DataFrames zusammenführen:
df_3 = pd.concat([df_1, df_2], ignore_index=True)

# 5. Ausgabe der ersten Zeilen des kombinierten DataFrames zur Überprüfung
print(df_3.head())

# Beispiel wie du die Daten in deiner Dash App verwenden kannst
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Parkhaus Klima'),
    dash_table.DataTable(data=df_3.to_dict('records'), page_size=10),
    html.Hr(),
    dcc.RadioItems(options=[{'label': 'Free', 'value': 'free'}, {'label': 'Total', 'value': 'total'}], value='free',
                   id='controls-and-radio-item'),
    dcc.Graph(figure={}, id='controls-and-graph'),
    html.H4(children='Parkhaus und Klima 2024'),
    dash_table.DataTable(data=df_3.to_dict('records'), page_size=10)
])

@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df_3, x='title', y=col_chosen)
    return fig

if __name__ == '__main__':
    app.run(debug=True)
