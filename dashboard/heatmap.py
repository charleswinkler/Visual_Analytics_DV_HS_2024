import plotly.express as px
import streamlit as st
import pandas as pd

def plot_heatmap(df):
    """Zeigt eine Heatmap der Temperatur nach Zeit und Klimastation an."""
    st.write("### Heatmap der Temperatur")

    # Datum und Zeit aus der 'published'-Spalte extrahieren
    df['published'] = pd.to_datetime(df['published'])
    df['date'] = df['published'].dt.date
    df['hour'] = df['published'].dt.hour

    # Datumsauswahl
    start_date = st.date_input("Startdatum", value=df['date'].min())
    end_date = st.date_input("Enddatum", value=df['date'].max())

    # Klimastationsauswahl
    klima_standort = st.selectbox(
        "Wähle eine Klimastation für die Heatmap:",
        ['Alle Stationen'] + sorted(df[df['Kategorie'] == 'Klima']['title'].unique())
    )

    # Filterung der Daten
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date) & (df['Kategorie'] == 'Klima')]

    if klima_standort != 'Alle Stationen':
        filtered_df = filtered_df[filtered_df['title'] == klima_standort]

    # Heatmap-Daten vorbereiten
    heatmap_data = filtered_df.groupby(['title', 'date', 'hour'])['meta_airtemp'].mean().reset_index()
    heatmap_data['date_hour'] = heatmap_data['date'].astype(str) + " " + heatmap_data['hour'].astype(str) + ":00"

    # Heatmap erstellen
    fig_heat = px.density_heatmap(
        heatmap_data,
        x="date_hour",  # Zeitachse
        y="title",      # Klimastation
        z="meta_airtemp",  # Temperatur
        color_continuous_scale="Viridis",
        labels={
            'meta_airtemp': 'Temperatur (°C)',
            'date_hour': 'Datum und Uhrzeit',
            'title': 'Klimastation'
        }
    )

    # Layout anpassen
    fig_heat.update_layout(
        title="Temperatur-Heatmap nach Zeit und Klimastation",
        xaxis_title="Datum und Uhrzeit",
        yaxis_title="Klimastation",
        xaxis_tickangle=-45
    )

    # Heatmap anzeigen
    st.plotly_chart(fig_heat)
