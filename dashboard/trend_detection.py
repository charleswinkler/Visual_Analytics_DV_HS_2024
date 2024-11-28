import ruptures as rpt
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np


def detect_change_points(data, timestamp_column, value_column, model="rbf", penalty=10, start_date=None, end_date=None):
    """
    Detektiert Change-Points in einer Zeitreihe und analysiert Trends in den Intervallen.

    Parameters:
    - data: pd.DataFrame, der Datensatz
    - timestamp_column: str, Spaltenname mit Zeitstempeln
    - value_column: str, Spaltenname der Werte für die Analyse
    - model: str, Modell für ruptures (z. B. 'rbf', 'linear', 'l1')
    - penalty: int, Bestrafungsterm, um die Empfindlichkeit der Change-Point-Erkennung einzustellen
    - start_date: str oder None, Startdatum für die Analyse (optional)
    - end_date: str oder None, Enddatum für die Analyse (optional)

    Returns:
    - result: dict mit Change-Points, Intervallen, Trend-Slopes und Visualisierung
    """
    # Filtern des Datensatzes nach Start- und Enddatum
    if start_date:
        data = data[data[timestamp_column] >= start_date]
    if end_date:
        data = data[data[timestamp_column] <= end_date]

    # Zeitreihe vorbereiten
    data = data.dropna(subset=[timestamp_column, value_column]).copy()
    data = data.sort_values(timestamp_column)
    signal = data[value_column].values

    # Change-Point-Analyse
    algo = rpt.Pelt(model=model).fit(signal)
    change_points = algo.predict(pen=penalty)

    # Automatische Erkennung relevanter Intervalle
    intervals = [
        (data[timestamp_column].iloc[start], data[timestamp_column].iloc[end - 1])
        for start, end in zip([0] + change_points[:-1], change_points)
    ]

    # Trends innerhalb der Intervalle berechnen
    trends = []
    for start, end in zip([0] + change_points[:-1], change_points):
        segment = data.iloc[start:end]
        X = np.arange(len(segment)).reshape(-1, 1)
        y = segment[value_column].values
        model = LinearRegression().fit(X, y)
        trends.append({"slope": model.coef_[0], "start": start, "end": end})

    # Visualisierung der Change-Points
    plt.figure(figsize=(10, 6))
    rpt.display(signal, change_points, figsize=(10, 6))
    plt.title("Change-Point Detection")
    plt.xlabel("Index")
    plt.ylabel(value_column)
    plt.grid()

    # Ergebnisse zurückgeben
    return {
        "change_points": change_points,
        "intervals": intervals,
        "trends": trends,
        "plot": plt
    }
