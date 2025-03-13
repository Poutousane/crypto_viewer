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
        # Extraction explicite des valeurs scalaires
        latest_close_value = float(data['Close'].iloc[-1])
        first_close_value = float(data['Close'].iloc[0])
        variation_value = ((latest_close_value - first_close_value) / first_close_value) * 100
        latest_volume_value = float(data['Volume'].iloc[-1])

        # Affichage des indicateurs clés
        st.subheader("Indicateurs clés")

        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        with metrics_col1:
            formatted_close = f"${latest_close_value:.2f}"
            st.metric("Prix de clôture", formatted_close)

        with metrics_col2:
            formatted_variation = f"{variation_value:.2f}%"
            formatted_delta = f"{variation_value:.2f}%"
            st.metric("Variation", formatted_variation, delta=formatted_delta)

        with metrics_col3:
            if latest_volume_value >= 1e9:
                vol_str = f"{latest_volume_value / 1e9:.2f} G"
            elif latest_volume_value >= 1e6:
                vol_str = f"{latest_volume_value / 1e6:.2f} M"
            elif latest_volume_value >= 1e3:
                vol_str = f"{latest_volume_value / 1e3:.2f} k"
            else:
                vol_str = f"{latest_volume_value:.2f}"
            st.metric("Volume (dernier jour)", vol_str)

        # Tableau des données
        st.subheader("Données historiques")

        # Calculer la variation quotidienne
        data['Daily_Change'] = data['Close'].pct_change() * 100

        # ======== MÉTHODE CORRIGÉE POUR FORMATER LE DATAFRAME ========
        # Convertir le DataFrame en dictionnaire, puis formater chaque élément individuellement
        # Cette approche évite les erreurs de pandas Series.format

        # Créer un nouveau DataFrame vide avec les mêmes index
        display_data = pd.DataFrame(index=data.index)

        # Convertir chaque colonne en une liste de chaînes formatées
        open_formatted = []
        high_formatted = []
        low_formatted = []
        close_formatted = []
        change_formatted = []
        volume_formatted = []

        # Parcourir les lignes pour un formatage personnalisé
        for idx in data.index:
            # Formater les prix
            open_formatted.append(f"${data.loc[idx, 'Open']:.2f}")
            high_formatted.append(f"${data.loc[idx, 'High']:.2f}")
            low_formatted.append(f"${data.loc[idx, 'Low']:.2f}")
            close_formatted.append(f"${data.loc[idx, 'Close']:.2f}")

            # Formater la variation avec gestion des NaN
            change = data.loc[idx, 'Daily_Change']
            if pd.isna(change):
                change_formatted.append("N/A")
            else:
                change_formatted.append(f"{change:.2f}%")

            # Formater le volume
            volume = data.loc[idx, 'Volume']
            if volume >= 1e9:
                volume_formatted.append(f"{volume / 1e9:.2f} G")
            elif volume >= 1e6:
                volume_formatted.append(f"{volume / 1e6:.2f} M")
            elif volume >= 1e3:
                volume_formatted.append(f"{volume / 1e3:.2f} k")
            else:
                volume_formatted.append(f"{volume:.2f}")

        # Ajouter les listes formatées comme nouvelles colonnes
        display_data['Open'] = open_formatted
        display_data['High'] = high_formatted
        display_data['Low'] = low_formatted
        display_data['Close'] = close_formatted
        display_data['Variation (%)'] = change_formatted
        display_data['Volume'] = volume_formatted

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

    st.error(f"Traceback détaillé: {traceback.format_exc()}")
