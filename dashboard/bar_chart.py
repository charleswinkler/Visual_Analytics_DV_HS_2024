import plotly.express as px
import streamlit as st

def plot_bar_chart(df):
    """Zeigt das Balkendiagramm für die Klima-Temperaturen an."""
    st.write("### Klima-Temperaturverlauf")
    df_klima = df[df['Kategorie'] == 'Klima']
    selected_klima_title = st.selectbox('Wähle ein Klima-Objekt:', ['Keine Auswahl'] + sorted(df_klima['title'].unique()))
    df_klima_filtered = df_klima if selected_klima_title == 'Keine Auswahl' else df_klima[df_klima['title'] == selected_klima_title]

    fig_bar = px.bar(df_klima_filtered, x='published', y='meta_airtemp', title="Klima und Temperaturen",
                     labels={'published': 'Uhrzeit', 'meta_airtemp': 'Temperatur'})
    st.plotly_chart(fig_bar)
