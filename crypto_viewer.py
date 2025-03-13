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
        # Calcul des indicateurs clés
        latest_close = float(data['Close'].iloc[-1])
        first_close = float(data['Close'].iloc[0])
        variation = ((latest_close - first_close) / first_close) * 100
        latest_volume = float(data['Volume'].iloc[-1])

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

        # Calculer la variation quotidienne
        data['Daily Change'] = data['Close'].pct_change() * 100

        # Créer un dataframe d'affichage simplifié
        df_display = pd.DataFrame()
        df_display['Open'] = [f"${x:.2f}" for x in data['Open']]
        df_display['High'] = [f"${x:.2f}" for x in data['High']]
        df_display['Low'] = [f"${x:.2f}" for x in data['Low']]
        df_display['Close'] = [f"${x:.2f}" for x in data['Close']]

        # Formater la variation
        df_display['Variation (%)'] = ["N/A" if pd.isna(x) else f"{x:.2f}%" for x in data['Daily Change']]

        # Formater le volume manuellement
        volume_formatted = []
        for vol in data['Volume']:
            if vol >= 1e9:
                volume_formatted.append(f"{vol / 1e9:.2f} G")
            elif vol >= 1e6:
                volume_formatted.append(f"{vol / 1e6:.2f} M")
            elif vol >= 1e3:
                volume_formatted.append(f"{vol / 1e3:.2f} k")
            else:
                volume_formatted.append(f"{vol:.2f}")
        df_display['Volume'] = volume_formatted

        # Conserver l'index de dates
        df_display.index = data.index

        # Affichage du tableau avec filtres
        st.dataframe(df_display)

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
