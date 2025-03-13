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


# Fonction pour formater les grands nombres
def format_large_number(num):
    try:
        # Si c'est une series pandas, extraire la valeur correctement
        if hasattr(num, 'iloc'):
            num = num.iloc[0]

        num = float(num)
        if np.isnan(num):
            return "N/A"
        if num >= 1e9:
            return f"{num / 1e9:.2f} G"
        elif num >= 1e6:
            return f"{num / 1e6:.2f} M"
        elif num >= 1e3:
            return f"{num / 1e3:.2f} k"
        else:
            return f"{num:.2f}"
    except:
        return "N/A"


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
            st.metric("Volume (dernier jour)", format_large_number(latest_volume))

        # Tableau des données
        st.subheader("Données historiques")

        # Ajout d'une colonne de variation journalière
        data['Variation (%)'] = data['Close'].pct_change() * 100

        # Formatage des colonnes pour l'affichage
        df_display = data.copy()

        # Création d'un tableau formaté pour l'affichage
        df_display_formatted = pd.DataFrame()
        df_display_formatted.index = df_display.index

        # Formatage spécifique pour chaque colonne
        df_display_formatted['Open'] = df_display['Open'].apply(lambda x: f"${x:.2f}")
        df_display_formatted['High'] = df_display['High'].apply(lambda x: f"${x:.2f}")
        df_display_formatted['Low'] = df_display['Low'].apply(lambda x: f"${x:.2f}")
        df_display_formatted['Close'] = df_display['Close'].apply(lambda x: f"${x:.2f}")

        # Formatage du volume
        volumes = []
        for vol in df_display['Volume']:
            volumes.append(format_large_number(vol))
        df_display_formatted['Volume'] = volumes

        # Formatage de la variation
        df_display_formatted['Variation (%)'] = df_display['Variation (%)'].apply(
            lambda x: f"{x:.2f}%" if not pd.isna(x) else "N/A"
        )

        # Affichage du tableau avec filtres
        st.dataframe(df_display_formatted)

        # Option de téléchargement
        csv = data.to_csv()
        st.download_button(
            label="Télécharger les données (CSV)",
            data=csv,
            file_name=f'{selected_crypto}_{start_date_input}_{end_date_input}.csv',
            mime='text/csv',
        )

except Exception as e:
    st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
