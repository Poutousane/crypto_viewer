import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
import openpyxl

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


# Fonction pour créer un Excel
def create_excel(data, ticker_symbol):
    output = io.BytesIO()

    # Préparer les données
    export_data = data.copy()

    # Calculer la variation
    export_data['Variation (%)'] = export_data['Close'].pct_change() * 100

    # Créer un classeur Excel avec openpyxl
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    # Ajouter les en-têtes de colonnes
    headers = ["Price", "High", "Low", "Open", "Volume", "Variation (%)"]

    # Ajouter une ligne pour le numéro
    for col in range(1, 8):
        ws.cell(row=1, column=col).value = get_column_letter(col)
        ws.cell(row=1, column=col).font = Font(bold=True)
        ws.cell(row=1, column=col).fill = PatternFill(start_color="000000", end_color="000000", fill_type="solid")
        ws.cell(row=1, column=col).font = Font(color="FFFFFF", bold=True)
        ws.cell(row=1, column=col).alignment = Alignment(horizontal="center")

    # Première ligne: headers
    for col, header in enumerate(headers, start=2):
        ws.cell(row=2, column=col).value = header
        ws.cell(row=2, column=col).font = Font(bold=True)
        ws.cell(row=2, column=col).alignment = Alignment(horizontal="center")

    # Ligne pour Ticker
    ws.cell(row=2, column=1).value = "Ticker"
    ws.cell(row=2, column=1).font = Font(bold=True)
    ws.cell(row=2, column=1).alignment = Alignment(horizontal="center")

    # Ligne pour les Ticker values
    for col in range(2, 7):
        ws.cell(row=3, column=col).value = ticker_symbol
        ws.cell(row=3, column=col).alignment = Alignment(horizontal="center")

    # Ligne pour Date
    ws.cell(row=3, column=1).value = "Date"
    ws.cell(row=3, column=1).font = Font(bold=True)

    # Recréer les en-têtes dans la 3ème ligne
    for col, header in enumerate(headers, start=2):
        ws.cell(row=4, column=col).value = header
        ws.cell(row=4, column=col).font = Font(bold=True)
        ws.cell(row=4, column=col).alignment = Alignment(horizontal="center")

    # Ajouter les données
    start_row = 5
    for i, (idx, row) in enumerate(export_data.iterrows(), start=start_row):
        date_str = idx.strftime('%Y-%m-%d')
        ws.cell(row=i, column=1).value = date_str

        # Price (Close)
        ws.cell(row=i, column=2).value = float(row["Close"])
        ws.cell(row=i, column=2).number_format = "#,##0.00"

        # High
        ws.cell(row=i, column=3).value = float(row["High"])
        ws.cell(row=i, column=3).number_format = "#,##0.00"

        # Low
        ws.cell(row=i, column=4).value = float(row["Low"])
        ws.cell(row=i, column=4).number_format = "#,##0.00"

        # Open
        ws.cell(row=i, column=5).value = float(row["Open"])
        ws.cell(row=i, column=5).number_format = "#,##0.00"

        # Volume - format comme notation scientifique
        vol = float(row["Volume"])
        ws.cell(row=i, column=6).value = vol
        ws.cell(row=i, column=6).number_format = "0.00E+00"

        # Variation
        variation = row["Variation (%)"]
        if not pd.isna(variation):
            ws.cell(row=i, column=7).value = variation / 100  # Excel affiche en pourcentage avec le format
            ws.cell(row=i, column=7).number_format = "0.000000000"

    # Ajuster la largeur des colonnes
    for col in range(1, 8):
        ws.column_dimensions[get_column_letter(col)].width = 15

    # Enregistrer le fichier Excel
    wb.save(output)
    return output.getvalue()


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

            # Créer un excel avec le format spécifique
            excel_data = create_excel(data, ticker_symbol)

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
