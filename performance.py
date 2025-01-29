import time
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st
import functools
import pandas as pd

# Leere Liste zur Speicherung der Performance-Daten
performance_data = []

### --------- ###

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

# Beispiel für die Konfiguration von Tabs
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

# Funktion zum Anzeigen von Daten in Expandern
def display_data_in_expanders(traffic_data, parking_data, climate_data, filtered_data):
    """
    Funktion, die die verschiedenen DataFrames in Streamlit Expandern anzeigt.
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


### PERFORMANCE MESSUNG ###

# Funktion zur Messung der Performance einer Funktion
def measure_performance(action, func, *args, **kwargs):
    """
    Misst die Ausführungszeit einer Funktion und speichert die Daten in der Performance-Liste.
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


# Dekorator zur Messung der Performance für jede Funktion
def performance_decorator(action):
    """
    Ein Dekorator zur Messung der Performance einer Funktion,
    wobei st.set_page_config() explizit ausgeschlossen wird.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Überprüfe, ob die Funktion st.set_page_config() ist
            if func.__name__ == 'set_page_config':
                # Wenn es st.set_page_config ist, überspringe die Messung
                return func(*args, **kwargs)

            # Ansonsten messe die Performance
            return measure_performance(action, func, *args, **kwargs)
        return wrapper
    return decorator


### BEISPIELFUNKTIONEN ###

# Beispiel-Funktion zur Visualisierung der Parkhausbelegung nach Wochentagen
@performance_decorator("Visualisierung der Parkhausbelegung")
def plot_parking_by_weekday(df):
    """
    Beispiel für eine Visualisierung der Parkhausbelegung nach Wochentagen.
    """
    st.write("Wochentagsdiagramm")
    # Hier kannst du das Diagramm für Parkhausbelegung nach Wochentag erstellen.

# Beispiel-Funktion für die Karten-Darstellung
@performance_decorator("Karten-Darstellung")
def plot_map(df):
    """
    Erstelle eine Karte (hier ein Platzhalter).
    """
    st.write("Map is generated.")
    # Hier kannst du die Logik zur Kartenerstellung hinzufügen.

# Funktion zur Darstellung der Performance-Daten als Performance-Kurve
def old_plot_performance_curve():
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



def smoothed_plot_performance_curve():
    """
    Zeichnet eine Performance-Kurve basierend auf den gesammelten Performance-Daten.
    Verbesserungen: Zeitstempel-Formatierung, Sortierung, Trendlinie, visuelle Optimierung.
    """
    if not performance_data:
        st.write("Keine Performance-Daten vorhanden.")
        return

    # In DataFrame umwandeln, falls notwendig
    df = pd.DataFrame(performance_data)

    # Zeitstempel konvertieren und sortieren
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Gleitenden Durchschnitt berechnen (Fenstergröße = 5)
    df["smoothed"] = df["load_time"].rolling(window=5, min_periods=1).mean()

    # Plot erstellen
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["load_time"], marker="o", linestyle="--", color="b", alpha=0.6, label="Ladezeit")
    plt.plot(df["timestamp"], df["smoothed"], linestyle="-", color="r", linewidth=2,
             label="Trend (Gleitender Durchschnitt)")

    # Achsenbeschriftung & Titel
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Ladezeit (Sekunden)")
    plt.title("Performance-Kurve: Ausführungszeit der Funktionen")

    # Layout-Verbesserungen
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Plot anzeigen
    plt.figure()
    st.pyplot(plt)

def plot_performance_curve():
    """
    Zeichnet eine Performance-Kurve basierend auf den gesammelten Performance-Daten.
    """
    if not performance_data:
        st.write("Keine Performance-Daten vorhanden.")
        return

    # In DataFrame umwandeln
    df = pd.DataFrame(performance_data)

    # Zeitstempel konvertieren und sortieren
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Plot erstellen
    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["load_time"], marker="o", linestyle="--", color="b", alpha=0.6, label="Ladezeit")

    # Achsenbeschriftung & Titel
    plt.xlabel("Zeitpunkt")
    plt.ylabel("Ladezeit (Sekunden)")
    plt.title("Performance-Kurve: Ausführungszeit der Funktionen")

    # Layout-Verbesserungen
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Plot anzeigen
    st.pyplot(plt)
