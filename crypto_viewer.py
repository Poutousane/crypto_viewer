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

        # Créer un dataframe pour l'affichage avec des colonnes formatées manuellement
        display_data = []

        for idx, row in data.iterrows():
            # Calculer la variation en pourcentage par rapport au jour précédent
            prev_close = data['Close'].shift(1).loc[idx] if idx > 0 else None
            if prev_close is not None:
                daily_change_pct = ((row['Close'] - prev_close) / prev_close) * 100
                daily_change_str = f"{daily_change_pct:.2f}%"
            else:
                daily_change_str = "N/A"

            # Formater le volume
            volume = row['Volume']
            if volume >= 1e9:
                volume_str = f"{volume / 1e9:.2f} G"
            elif volume >= 1e6:
                volume_str = f"{volume / 1e6:.2f} M"
            elif volume >= 1e3:
                volume_str = f"{volume / 1e3:.2f} k"
            else:
                volume_str = f"{volume:.2f}"

            # Ajouter une ligne au tableau d'affichage
            display_data.append({
                'Date': idx.strftime('%Y-%m-%d'),
                'Open': f"${row['Open']:.2f}",
                'High': f"${row['High']:.2f}",
                'Low': f"${row['Low']:.2f}",
                'Close': f"${row['Close']:.2f}",
                'Variation (%)': daily_change_str,
                'Volume': volume_str
            })

        # Créer le dataframe d'affichage
        df_display = pd.DataFrame(display_data)

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
