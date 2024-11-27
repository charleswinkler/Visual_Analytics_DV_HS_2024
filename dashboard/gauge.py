import plotly.graph_objects as go
import streamlit as st

def plot_gauge(df):
    """Zeigt das Gauge-Diagramm für die Auslastung des Parkhauses an."""
    st.write("### Auslastung des ausgewählten Parkhauses")
    selected_title = st.selectbox('Wähle ein Parkhaus:', df[df['Kategorie'] == 'Parkhaus']['title'])
    selected_data = df[df['title'] == selected_title].iloc[0]
    occupied_percentage = ((selected_data['total'] - selected_data['free']) / selected_data['total']) * 100

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=occupied_percentage,
        title={'text': f"Auslastung für {selected_title}"},
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#ff0000"},
            'steps': [{'range': [0, 50], 'color': '#66c2a5'}, {'range': [50, 100], 'color': '#fc8d62'}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': occupied_percentage}
        }
    ))
    st.plotly_chart(fig_gauge)
