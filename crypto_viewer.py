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
    "Solana": "SOL-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD"
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
        # Télécharger toutes les données brutes d'abord
        data = yf.download(ticker, start=start, end=end)
        return data
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
        raw_data = get_crypto_data(ticker_symbol, start_date, end_date)

        if raw_data is not None and not raw_data.empty:
            # Préparation des données après vérification de leur disponibilité
            # IMPORTANT: faire le traitement des colonnes ici, pas avant
            st.header(f"{selected_crypto} ({ticker_symbol}) - Données du {start_date} au {end_date}")

            # Calculer les métriques directement sur les colonnes d'origine
            first_price = raw_data['Close'].iloc[0]
            last_price = raw_data['Close'].iloc[-1]
            percent_change = ((last_price - first_price) / first_price) * 100
            avg_volume = raw_data['Volume'].mean()

            # Affichage des stats rapides
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            # Afficher les métriques de manière sécurisée sans formatage complexe
            metric_col1.metric("Prix actuel", f"${round(last_price, 2)}")
            metric_col2.metric("Variation de prix", f"{round(percent_change, 2)}%")
            metric_col3.metric("Volume moyen", f"{int(avg_volume)}")

            # Renommer les colonnes pour l'affichage seulement après avoir calculé les métriques
            data_display = raw_data.rename(columns={
                'Date': 'Date',
                'High': 'Prix le plus haut',
                'Low': 'Prix le plus bas',
                'Close': 'Prix de clôture',
                'Volume': 'Volume'
            })

            # Affichage d'un graphique interactif avec plotly
            st.subheader("Graphique d'évolution du prix")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=raw_data.index, y=raw_data['Close'], mode='lines', name='Prix de clôture'))
            fig.add_trace(go.Scatter(x=raw_data.index, y=raw_data['High'], mode='lines', name='Prix le plus haut',
                                     line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=raw_data.index, y=raw_data['Low'], mode='lines', name='Prix le plus bas',
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
            volume_fig.add_trace(go.Bar(x=raw_data.index, y=raw_data['Volume'], name='Volume'))
            volume_fig.update_layout(
                title=f"Volume d'échanges de {selected_crypto}",
                xaxis_title="Date",
                yaxis_title="Volume",
                hovermode="x unified"
            )
            st.plotly_chart(volume_fig, use_container_width=True)

            # Préparation des données pour l'affichage et le téléchargement
            st.subheader("Tableau de données")
            # Sélectionner et renommer les colonnes pour l'affichage
            display_cols = ['High', 'Low', 'Close', 'Volume']
            display_data = raw_data[display_cols].copy().reset_index()
            display_data.columns = ['Date', 'Prix le plus haut', 'Prix le plus bas', 'Prix de clôture', 'Volume']

            # Afficher le DataFrame
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
