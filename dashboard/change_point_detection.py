import ruptures as rpt
import matplotlib.pyplot as plt
import pandas as pd

def detect_change_points(data, timestamp_column, value_column, model="rbf", penalty=10):
    """
    Detektiert Change-Points in einer Zeitreihe und gibt Ergebnisse zurück.

    Parameters:
    - data: pd.DataFrame, der Datensatz
    - timestamp_column: str, Spaltenname mit Zeitstempeln
    - value_column: str, Spaltenname der Werte für die Analyse
    - model: str, Modell für ruptures (z. B. 'rbf', 'linear', 'l1')
    - penalty: int, Bestrafungsterm, um die Empfindlichkeit der Change-Point-Erkennung einzustellen

    Returns:
    - result: dict, Ergebnisse mit Change-Points und visualisierter Zeitreihe
    """
    # Zeitreihe vorbereiten
    data = data.dropna(subset=[timestamp_column, value_column]).copy()
    data = data.sort_values(timestamp_column)
    signal = data[value_column].values

    # Change-Point-Analyse
    algo = rpt.Pelt(model=model).fit(signal)
    change_points = algo.predict(pen=penalty)

    # Visualisierung der Change-Points
    plt.figure(figsize=(10, 6))
    rpt.display(signal, change_points, figsize=(10, 6))
    plt.title("Change-Point Detection")
    plt.xlabel("Index")
    plt.ylabel(value_column)
    plt.grid()
    plt.show()

    return {
        "change_points": change_points,
        "plot": plt
    }
