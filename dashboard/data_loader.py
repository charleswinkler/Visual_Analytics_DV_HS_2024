import requests
import pandas as pd
from utils import extract_coordinates

def load_data(dataset_id, api_key, base_url):
    """Lädt die Daten von der API."""
    url = f"{base_url}{dataset_id}/records?apikey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        raise Exception(f"Fehler beim Laden des Datensatzes {dataset_id}")

def load_and_process_data(api_key, base_url, dataset_ids):
    """Lädt und verarbeitet die Daten aus verschiedenen Datensätzen."""
    all_data = []
    for dataset_id in dataset_ids:
        data = load_data(dataset_id, api_key, base_url)
        df = pd.DataFrame(data)
        df['Kategorie'] = dataset_id
        df[['Longitude', 'Latitude']] = df.apply(extract_coordinates, axis=1)
        all_data.append(df)
    final_df = pd.concat(all_data, ignore_index=True)
    return final_df
