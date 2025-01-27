import time
import matplotlib.pyplot as plt
import numpy as np

# Die measure_performance-Funktion für genauere Zeitmessung
def measure_performance(func, *args, **kwargs):
    """
    Misst die Ausführungszeit einer Funktion.

    Parameters:
        func: Die Funktion, deren Performanz getestet werden soll.
        *args, **kwargs: Argumente, die an die Funktion übergeben werden.

    Returns:
        tuple: Die gemessene Ausführungszeit in Sekunden und das Ergebnis der Funktion.
    """
    start_time = time.perf_counter()  # Startzeitpunkt
    result = func(*args, **kwargs)   # Ausführung der Funktion
    end_time = time.perf_counter()   # Endzeitpunkt

    duration = end_time - start_time
    return duration, result          # Rückgabe der Dauer und des Ergebnisses




def run_performance_test(repetitions, func, *args, **kwargs):
    """
    Führt mehrere Performanztests durch und speichert die Ergebnisse.

    Parameters:
        repetitions: Anzahl der Wiederholungen des Tests.
        func: Die Funktion, deren Performanz getestet werden soll.
        *args, **kwargs: Argumente, die an die Funktion übergeben werden.

    Returns:
        list: Eine Liste der Ladezeiten der jeweiligen Wiederholungen.
    """
    times = []
    for _ in range(repetitions):
        execution_time = measure_performance(func, *args, **kwargs)
        times.append(execution_time)
        print(f"Test {_ + 1}: {execution_time:.4f} Sekunden")

    return times


# Annahme: Die Daten in performance_data sind dictionaries, die 'load_time' enthalten
def plot_performance_curve(performance_data):
    times = []
    timestamps = []

    # Extrahiert Ladezeiten und Zeitstempel aus den Performance-Daten
    for entry in performance_data:
        times.append(entry['load_time'])
        timestamps.append(entry['timestamp'].strftime('%H:%M:%S'))  # Formatierung des Zeitstempels

    if not times:
        print("Keine Ladezeiten vorhanden.")
        return

    # Erstelle den Plot
    fig, ax = plt.subplots()

    # Ladezeiten plotten
    ax.plot(np.arange(1, len(times) + 1), times, marker='o', color='b', linestyle='-', linewidth=2, markersize=5)

    # Achsenbeschriftungen und Titel
    ax.set_title('Performanzkurve')
    ax.set_xlabel('Wiederholung')
    ax.set_ylabel('Ladezeit (Sekunden)')

    # Zeitstempel als xticks
    ax.set_xticks(np.arange(1, len(timestamps) + 1))  # x-Achse als Wiederholung (Nummern)
    ax.set_xticklabels(timestamps, rotation=45, ha='right')  # Zeitstempel als Beschriftungen

    # Grid und Layout
    ax.grid(True)
    plt.tight_layout()  # Für bessere Lesbarkeit der x-Beschriftungen

    # Plot anzeigen
    plt.show()