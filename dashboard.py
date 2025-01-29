import time
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st


# Leere Liste zur Speicherung der Performance-Daten
# Diese muss in main.py ebenfalls vorhanden sein
performance_data = []


# Funktion zur Messung der Performance
def measure_performance(action, func, *args, **kwargs):
    """
    Misst die Ausführungszeit einer Funktion und speichert die Daten in der Performance-Liste.

    Parameters:
    action (str): Bezeichnung der Aktion, die durchgeführt wird.
    func (callable): Die Funktion, deren Performance gemessen wird.
    *args, **kwargs: Die Argumente und Keyword-Argumente, die an die Funktion übergeben werden.

    Returns:
    result: Das Ergebnis der ausgeführten Funktion.
    """
    try:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)  # Führt die Funktion aus
        end_time = time.perf_counter()

        load_time = end_time - start_time  # Berechnet die Ladezeit
        timestamp = datetime.now()  # Erfasst den aktuellen Zeitstempel

        # Speichern der Performance-Daten
        performance_data.append({
            'action': action,
            'load_time': load_time,
            'timestamp': timestamp,
            'function': func.__name__,  # Speichert den Funktionsnamen
            'args': args,  # Speichert die übergebenen Argumente
            'kwargs': kwargs  # Speichert die übergebenen Keyword-Argumente
        })

        return result
    except Exception as e:
        # Falls ein Fehler auftritt, wird dies ebenfalls protokolliert
        performance_data.append({
            'action': action,
            'load_time': None,
            'timestamp': datetime.now(),
            'error': str(e)  # Fehlernachricht wird gespeichert
        })
        raise e


# Funktion zur Darstellung der Performance-Daten als Performance-Kurve
def plot_performance_curve():
    """
    Zeichnet eine Performance-Kurve basierend auf den gesammelten Performance-Daten.
    """
    if not performance_data:
        print("Keine Performance-Daten vorhanden.")
        return

    # Extrahieren der Ladezeiten und Zeitstempel
    timestamps = [data['timestamp'] for data in performance_data]
    load_times = [data['load_time'] for data in performance_data]

    # Überprüfen, ob genug Daten vorhanden sind
    if len(load_times) > 1:
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, load_times, marker='o', color='b', label="Ladezeit")
        plt.xlabel('Zeit')
        plt.ylabel('Ladezeit (Sekunden)')
        plt.title('Performance-Kurve: Ausführungszeit der Funktionen')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.legend()
        plt.show()
    else:
        print("Nicht genügend Performance-Daten für eine Kurve vorhanden.")

### --------- ###
import streamlit as st


# Beispiel-Funktionen, die in den Tabs angezeigt werden können
def function_1():
    st.write("Dies ist Funktion 1.")


def function_2():
    st.write("Dies ist Funktion 2.")


def function_3():
    st.write("Dies ist Funktion 3.")


# Layout-Funktion
def create_dashboard(tabs_config):
    """
    Erstellt ein dynamisches Dashboard mit Tabs, Spalten und Funktionen.

    Parameters:
    tabs_config (list): Eine Liste von Dictionaries, die die Tabs und deren Inhalt beschreiben.
    """
    # Setze die Tabs
    tab_names = [tab['name'] for tab in tabs_config]
    selected_tab = st.sidebar.radio("Wähle ein Tab:", tab_names)

    # Durchlaufe alle Tabs und deren Konfiguration
    for tab in tabs_config:
        if selected_tab == tab['name']:
            st.title(f"Dashboard - {tab['name']}")

            # Spalten erstellen
            num_columns = tab.get('columns', 1)  # Standard ist 1 Spalte, falls nicht angegeben
            cols = st.columns(num_columns)

            # Funktionsaufrufe in die Spalten einfügen
            for i, func in enumerate(tab['functions']):
                with cols[i % num_columns]:  # Verteile die Funktionen auf die Spalten
                    func()

            # Zusätzliche Container oder Expander, falls gewünscht
            if 'expanders' in tab:
                for expander in tab['expanders']:
                    with st.expander(expander['title']):  # Nutze st.expander statt st.beta_expander
                        expander['function']()


# Konfiguration des Dashboards (z.B. 3 Tabs)
tabs_config = [
    {
        'name': 'Tab 1',
        'functions': [function_1, function_2],
        'columns': 2,  # 2 Spalten
        'expanders': [
            {'title': 'Expander 1', 'function': function_3},
        ]
    },
    {
        'name': 'Tab 2',
        'functions': [function_2, function_3],
        'columns': 1,  # 1 Spalte
    },
    {
        'name': 'Tab 3',
        'functions': [function_1],
        'columns': 1,  # 1 Spalte
    },
]

# Erstelle das Dashboard basierend auf der Konfiguration
# create_dashboard(tabs_config)

def display_data_in_expanders(traffic_data, parking_data, climate_data, filtered_data):
    """
    Funktion, die die verschiedenen DataFrames in Streamlit Expandern anzeigt.

    Args:
    traffic_data (DataFrame): Original Verkehrsdaten
    parking_data (DataFrame): Original Parkhausdaten
    climate_data (DataFrame): Original Klimadaten
    filtered_data (DataFrame): Gefilterte Daten, die immer angezeigt werden
    """
    # Expander für Verkehrsdaten
    with st.expander("Verkehrsdaten anzeigen", expanded=False):
        st.dataframe(traffic_data)

    # Expander für Parkhausdaten
    with st.expander("Parkhausdaten anzeigen", expanded=False):
        st.dataframe(parking_data)

    # Expander für Klimadaten
    with st.expander("Wetterdaten anzeigen", expanded=False):
        st.dataframe(climate_data)

    # Zeigt die gefilterten Daten unterhalb der Expanders
    st.dataframe(filtered_data)

