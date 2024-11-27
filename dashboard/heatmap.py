import plotly.express as px
import streamlit as st

def plot_heatmap(df):
    """Zeigt eine Heatmap der Parkhaus-Auslastung an."""
    st.write("### Heatmap der Parkhaus-Auslastung")
    selected_parkhaus = st.selectbox('Wähle ein Parkhaus für Heatmap:', df[df['Kategorie'] == 'Parkhaus']['title'])
    df_parkhaus = df[df['title'] == selected_parkhaus]

    fig_heatmap = px.density_mapbox(df_parkhaus, lat='Latitude', lon='Longitude', z='occupied', radius=10,
                                    center=dict(lat=47.5596, lon=7.5886), zoom=10, mapbox_style="carto-positron")
    st.plotly_chart(fig_heatmap)
