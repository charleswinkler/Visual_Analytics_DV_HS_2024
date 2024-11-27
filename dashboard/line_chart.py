import plotly.express as px
import streamlit as st

def plot_line_chart(df):
    """Zeigt das Liniendiagramm für die Parkhaus-Auslastung im Zeitverlauf an."""
    st.write("### Auslastung der Parkhäuser im Zeitverlauf")
    selected_parkhaus_1 = st.selectbox('Wähle das erste Parkhaus:', ['Keine Auswahl'] + sorted(df[df['Kategorie'] == 'Parkhaus']['title'].unique()), key="park1")
    selected_parkhaus_2 = st.selectbox('Wähle das zweite Parkhaus:', ['Keine Auswahl'] + sorted(df[df['Kategorie'] == 'Parkhaus']['title'].unique()), key="park2")

    fig_line = px.line()
    if selected_parkhaus_1 != 'Keine Auswahl':
        fig_line.add_scatter(
            x=df[df['title'] == selected_parkhaus_1]['published'],
            y=df[df['title'] == selected_parkhaus_1]['occupied'],
            mode='lines+markers', name=selected_parkhaus_1, line=dict(color='blue'))
    if selected_parkhaus_2 != 'Keine Auswahl':
        fig_line.add_scatter(
            x=df[df['title'] == selected_parkhaus_2]['published'],
            y=df[df['title'] == selected_parkhaus_2]['occupied'],
            mode='lines+markers', name=selected_parkhaus_2, line=dict(color='red'))
    fig_line.update_layout(title="Auslastung der Parkhäuser im Zeitverlauf", xaxis_title="Zeitpunkt", yaxis_title="Belegte Plätze")
    st.plotly_chart(fig_line)
