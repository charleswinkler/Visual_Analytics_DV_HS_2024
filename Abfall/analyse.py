import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def berechne_korrelation(data, x_col, y_col):
    """
    Berechnet die Korrelation zwischen zwei Spalten in einem DataFrame.

    Args:
        data (pd.DataFrame): Der DataFrame mit den Daten.
        x_col (str): Der Name der Spalte für die x-Werte (z. B. Verkehrszahlen).
        y_col (str): Der Name der Spalte für die y-Werte (z. B. Parkhausauslastung).

    Returns:
        float: Der Korrelationswert.
    """
    if x_col not in data.columns or y_col not in data.columns:
        raise ValueError(f"Eine der Spalten {x_col} oder {y_col} fehlt im DataFrame.")
    return data[x_col].corr(data[y_col])


def visualisiere_korrelation(data, x_col, y_col):
    """
    Visualisiert die Korrelation zwischen zwei Spalten als Scatterplot mit Regressionslinie.

    Args:
        data (pd.DataFrame): Der DataFrame mit den Daten.
        x_col (str): Der Name der Spalte für die x-Werte.
        y_col (str): Der Name der Spalte für die y-Werte.
    """
    plt.figure(figsize=(10, 6))
    sns.regplot(
        x=x_col,
        y=y_col,
        data=data,
        scatter_kws={'alpha': 0.5},
        line_kws={'color': 'red'}
    )
    plt.title(f'Korrelation zwischen {x_col} und {y_col}')
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
