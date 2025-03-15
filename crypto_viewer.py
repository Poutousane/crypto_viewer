import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import io
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

# Titre de l'application
st.title("Finance Viewer")

# Listes des actifs disponibles
crypto_assets = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "XRP": "XRP-USD",
    "Cardano": "ADA-USD",
    "Dogecoin": "DOGE-USD",
    "Polkadot": "DOT-USD"
}

stock_assets = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta": "META",
    "NVIDIA": "NVDA",
    "JPMorgan Chase": "JPM"
}

other_assets = {
    "Or": "GC=F",
    "Argent": "SI=F",
    "Pétrole brut": "CL=F",
    "Gaz naturel": "NG=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC"
}

# Création des onglets principaux pour types d'actifs
tab1, tab2, tab3 = st.tabs(["Crypto", "Actions", "Autres"])


# Fonction pour créer un Excel exactement comme dans l'image
def create_excel(data, sheet_name="Data", ticker_symbol=None):
    output = io.BytesIO()

    # Créer un workbook openpyxl directement pour un contrôle total
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    # Définir les en-têtes des colonnes (ligne 3)
    headers = ['Date', 'Price', 'High', 'Low', 'Open', 'Volume', 'Variation (%)']

    # Ajouter les en-têtes à la ligne 3
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=3, column=col_idx, value=header)

    # Calculer la variation pour chaque jour
    data['Variation (%)'] = data['Close'].pct_change() * 100

    # Formater les données pour chaque ligne
    for row_idx, (date, row_data) in enumerate(data.iterrows(), start=4):
        # Colonne Date
        ws.cell(row=row_idx, column=1, value=date.strftime('%Y-%m-%d'))

        # Prix de clôture (Price)
        ws.cell(row=row_idx, column=2, value=float(row_data['Close']))

        # High
        ws.cell(row=row_idx, column=3, value=float(row_data['High']))

        # Low
        ws.cell(row=row_idx, column=4, value=float(row_data['Low']))

        # Open
        ws.cell(row=row_idx, column=5, value=float(row_data['Open']))

        # Volume - Formater en notation scientifique si nécessaire
        volume = float(row_data['Volume'])
        if volume >= 1e10:
            formatted_volume = f"{volume / 1e10:.2f}E+10"
        elif volume >= 1e9:
            formatted_volume = f"{volume / 1e9:.2f}E+09"
        else:
            formatted_volume = str(volume)
        ws.cell(row=row_idx, column=6, value=volume)

        # Variation
        variation = row_data['Variation (%)']
        if not pd.isna(variation):
            ws.cell(row=row_idx, column=7, value=float(variation))

    # Ajouter la ligne 1 (en-tête)
    for col_idx, header in enumerate(['', 'Price', 'High', 'Low', 'Open', 'Volume', 'Variation (%)'], start=1):
        ws.cell(row=1, column=col_idx, value=header)

    # Ajouter la ligne 2 (ticker)
    if ticker_symbol:
        for col_idx in range(2, 7):  # Colonnes B à F
            ws.cell(row=2, column=col_idx, value=ticker_symbol)

        ws.cell(row=2, column=1, value="Ticker")  # Colonne A avec 'Ticker'

    # Sauvegarder le workbook dans le BytesIO
    wb.save(output)

    processed_data = output.getvalue()
    return processed_data


# Fonction pour afficher les données pour un type d'actif
def display_asset_data(assets, tab_key):
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_asset = st.selectbox("Choisissez un actif", list(assets.keys()), key=f"select_{tab_key}")

    with col2:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        start_date_input = st.date_input("Date de début", value=start_date, key=f"start_{tab_key}")

    with col3:
        end_date_input = st.date_input("Date de fin", value=end_date, key=f"end_{tab_key}")

    # Récupération des données
    ticker_symbol = assets[selected_asset]
    try:
        data = yf.download(ticker_symbol, start=start_date_input, end=end_date_input)

        if data.empty:
            st.error(f"Aucune donnée disponible pour {selected_asset} dans la période sélectionnée.")
        else:
            # Extraction explicite des valeurs scalaires individuelles
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

            # Créer un DataFrame pour l'affichage avec l'index recréé sans l'heure
            display_data = pd.DataFrame(index=[d.date() for d in data.index])

            # Convertir les valeurs numpy en valeurs Python natives
            open_values = [float(x) for x in data['Open'].to_numpy()]
            high_values = [float(x) for x in data['High'].to_numpy()]
            low_values = [float(x) for x in data['Low'].to_numpy()]
            close_values = [float(x) for x in data['Close'].to_numpy()]

            # Formater les prix
            display_data['Open'] = [f"${x:.2f}" for x in open_values]
            display_data['High'] = [f"${x:.2f}" for x in high_values]
            display_data['Low'] = [f"${x:.2f}" for x in low_values]
            display_data['Close'] = [f"${x:.2f}" for x in close_values]

            # Formater la variation avec gestion des NaN
            daily_changes = []
            for x in data['Daily_Change'].to_numpy():
                if pd.isna(x):
                    daily_changes.append("N/A")
                else:
                    daily_changes.append(f"{float(x):.2f}%")
            display_data['Variation (%)'] = daily_changes

            # Formater le volume
            volumes = []
            for vol in data['Volume'].to_numpy():
                vol = float(vol)
                if vol >= 1e9:
                    volumes.append(f"{vol / 1e9:.2f} G")
                elif vol >= 1e6:
                    volumes.append(f"{vol / 1e6:.2f} M")
                elif vol >= 1e3:
                    volumes.append(f"{vol / 1e3:.2f} k")
                else:
                    volumes.append(f"{vol:.2f}")
            display_data['Volume'] = volumes

            # Affichage du tableau avec filtres
            st.dataframe(display_data)

            # Créer un excel avec les données, formaté exactement comme dans l'image
            excel_data = create_excel(data, f"{selected_asset}", ticker_symbol)

            st.download_button(
                label="Télécharger les données (XLSX)",
                data=excel_data,
                file_name=f'{selected_asset}_{start_date_input}_{end_date_input}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key=f"download_{tab_key}"
            )

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
        import traceback

        st.error(f"Traceback détaillé: {traceback.format_exc()}")


# Affichage des données selon l'onglet sélectionné
with tab1:
    display_asset_data(crypto_assets, "crypto")

with tab2:
    display_asset_data(stock_assets, "stock")

with tab3:
    display_asset_data(other_assets, "other")
