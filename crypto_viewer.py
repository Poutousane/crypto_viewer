import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go

# Configuration de la page Streamlit
st.set_page_config(page_title="Crypto Data Viewer", layout="wide")
st.title("Visualisation de données de cryptocurrencies")

# Dictionnaire des cryptos disponibles
crypto_dict = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD"
}

# Paramètres de sélection en haut de la page
st.header("Paramètres de recherche")
col1, col2, col3 = st.columns(3)

# Sélection de la crypto
with col1:
    selected_crypto = st.selectbox(
        "Choisissez une crypto-monnaie:",
        list(crypto_dict.keys())
    )

# Date par défaut (1 an en arrière)
default_start_date = date.today() - timedelta(days=365)
default_end_date = date.today()

# Sélection de dates
with col2:
    start_date = st.date_input("Date de début", default_start_date)

with col3:
    end_date = st.date_input("Date de fin", default_end_date)

# Vérification des dates
if start_date > end_date:
    st.error("La date de début doit être antérieure à la date de fin.")
    st.stop()


# Fonction pour récupérer les données
@st.cache_data
def get_crypto_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        # Sélection des colonnes souhaitées et renommage pour plus de clarté
        selected_columns = data[['High', 'Low', 'Close', 'Volume']]
        selected_columns = selected_columns.rename(columns={
            'High': 'Prix le plus haut',
            'Low': 'Prix le plus bas',
            'Close': 'Prix de clôture',
            'Volume': 'Volume'
        })
        return selected_columns
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return None


# Bouton pour lancer le chargement
load_button = st.button("Charger les données", type="primary")

# Séparateur
st.markdown("---")

# Affichage des données si le bouton est cliqué
if load_button:
    with st.spinner('Chargement des données en cours...'):
        ticker_symbol = crypto_dict[selected_crypto]
        data = get_crypto_data(ticker_symbol, start_date, end_date)

        if data is not None and not data.empty:
            st.header(f"{selected_crypto} ({ticker_symbol}) - Données du {start_date} au {end_date}")

            # Affichage des stats rapides
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            # Calculer les valeurs de début et de fin pour la période
            first_price = data['Prix de clôture'].iloc[0]
            last_price = data['Prix de clôture'].iloc[-1]
            percent_change = ((last_price - first_price) / first_price) * 100

            # Correction du formatage des métriques
            metric_col1.metric("Prix actuel", f"${last_price:.2f}")
            metric_col2.metric("Variation de prix", f"{percent_change:.2f}%")
            metric_col3.metric("Volume moyen", f"{data['Volume'].mean():.0f}")

            # Affichage d'un graphique interactif avec plotly
            st.subheader("Graphique d'évolution du prix")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=data.index, y=data['Prix de clôture'], mode='lines', name='Prix de clôture'))
            fig.add_trace(go.Scatter(x=data.index, y=data['Prix le plus haut'], mode='lines', name='Prix le plus haut',
                                     line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=data.index, y=data['Prix le plus bas'], mode='lines', name='Prix le plus bas',
                                     line=dict(dash='dot')))
            fig.update_layout(
                title=f"Évolution du prix de {selected_crypto}",
                xaxis_title="Date",
                yaxis_title="Prix (USD)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Afficher le volume
            st.subheader("Volume d'échanges")
            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'))
            volume_fig.update_layout(
                title=f"Volume d'échanges de {selected_crypto}",
                xaxis_title="Date",
                yaxis_title="Volume",
                hovermode="x unified"
            )
            st.plotly_chart(volume_fig, use_container_width=True)

            # Affichage du tableau de données avec les colonnes sélectionnées
            st.subheader("Tableau de données")
            # Réinitialiser l'index pour afficher la date comme une colonne
            display_data = data.reset_index()
            display_data = display_data.rename(columns={'Date': 'Date'})
            st.dataframe(display_data, use_container_width=True)

            # Option pour télécharger les données
            csv = display_data.to_csv(index=False)
            st.download_button(
                label="Télécharger les données en CSV",
                data=csv,
                file_name=f'{selected_crypto}_{start_date}_to_{end_date}.csv',
                mime='text/csv',
            )

        else:
            st.warning("Aucune donnée disponible pour cette période.")

# Footer
st.markdown("---")
st.info("Données fournies par Yahoo Finance.")