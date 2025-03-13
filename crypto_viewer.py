import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# Titre de l'application
st.title("Crypto Viewer 📊")

# Liste des crypto-monnaies disponibles
cryptos = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "XRP": "XRP-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD",
    "Polkadot": "DOT-USD"
}

# Interface utilisateur pour sélection de crypto et dates
col1, col2, col3 = st.columns(3)

with col1:
    selected_crypto = st.selectbox("Choisissez une crypto-monnaie", list(cryptos.keys()))

with col2:
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)
    start_date_input = st.date_input("Date de début", value=start_date)

with col3:
    end_date_input = st.date_input("Date de fin", value=end_date)

# Récupération des données
ticker_symbol = cryptos[selected_crypto]
try:
    data = yf.download(ticker_symbol, start=start_date_input, end=end_date_input)

    if data.empty:
        st.error(f"Aucune donnée disponible pour {selected_crypto} dans la période sélectionnée.")
    else:
        # Calcul des indicateurs clés (utilisation correcte des Series)
        latest_close = data['Close'].iloc[-1]
        first_close = data['Close'].iloc[0]
        variation = ((latest_close - first_close) / first_close) * 100
        latest_volume = data['Volume'].iloc[-1]

        # Affichage des indicateurs clés
        st.subheader("Indicateurs clés")

        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        with metrics_col1:
            st.metric("Prix de clôture", f"${latest_close:.2f}")

        with metrics_col2:
            st.metric("Variation", f"{variation:.2f}%", delta=f"{variation:.2f}%")

        with metrics_col3:
            # Format volume manually
            vol_str = ""
            if latest_volume >= 1e9:
                vol_str = f"{latest_volume / 1e9:.2f} G"
            elif latest_volume >= 1e6:
                vol_str = f"{latest_volume / 1e6:.2f} M"
            elif latest_volume >= 1e3:
                vol_str = f"{latest_volume / 1e3:.2f} k"
            else:
                vol_str = f"{latest_volume:.2f}"
            st.metric("Volume (dernier jour)", vol_str)

        # Tableau des données
        st.subheader("Données historiques")

        # Préparation des données pour l'affichage
        # Calculer la variation quotidienne
        data['Daily_Change'] = data['Close'].pct_change() * 100

        # Créer une copie du dataframe pour l'affichage
        display_data = data.copy()

        # Formater les colonnes une par une en utilisant .apply() sans f-strings
        display_data = pd.DataFrame(index=data.index)


        # Fonction sûre pour formater les prix
        def format_price(price):
            return f"${price:.2f}"


        # Fonction sûre pour formater la variation
        def format_change(change):
            if pd.isna(change):
                return "N/A"
            return f"{change:.2f}%"


        # Fonction sûre pour formater le volume
        def format_volume(volume):
            if volume >= 1e9:
                return f"{volume / 1e9:.2f} G"
            elif volume >= 1e6:
                return f"{volume / 1e6:.2f} M"
            elif volume >= 1e3:
                return f"{volume / 1e3:.2f} k"
            return f"{volume:.2f}"


        # Appliquer les formatages colonne par colonne
        display_data['Open'] = data['Open'].apply(format_price)
        display_data['High'] = data['High'].apply(format_price)
        display_data['Low'] = data['Low'].apply(format_price)
        display_data['Close'] = data['Close'].apply(format_price)
        display_data['Variation (%)'] = data['Daily_Change'].apply(format_change)
        display_data['Volume'] = data['Volume'].apply(format_volume)

        # Affichage du tableau avec filtres
        st.dataframe(display_data)

        # Option de téléchargement (données originales)
        csv = data.to_csv()
        st.download_button(
            label="Télécharger les données (CSV)",
            data=csv,
            file_name=f'{selected_crypto}_{start_date_input}_{end_date_input}.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
    import traceback

    st.error(traceback.format_exc())  # Afficher la trace complète pour un meilleur débogage
