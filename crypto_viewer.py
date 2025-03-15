import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import io
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import numbers

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


# Fonction pour créer un Excel avec la colonne variation formatée en pourcentage
def create_excel(data, sheet_name="Data"):
    output = io.BytesIO()

    # Formater les données pour l'export
    export_data = data.copy()

    # Calculer la variation quotidienne
    export_data['Variation (%)'] = export_data['Close'].pct_change() * 100

    # Convertir les indices en dates au format YYYY-MM-DD
    export_data.index = [d.strftime('%Y-%m-%d') for d in export_data.index]
    export_data.index.name = 'Date'

    # Réorganiser les colonnes avec Volume et Variation inversées
    export_data = export_data[['Close', 'High', 'Low', 'Open', 'Variation (%)', 'Volume']]

    # Renommer les colonnes
    export_data.columns = ['Price', 'High', 'Low', 'Open', 'Variation (%)', 'Volume']

    # Créer et configurer manuellement le fichier Excel
    workbook = Workbook()
    ws = workbook.active
    ws.title = sheet_name

    # Ajouter la ligne d'en-tête
    headers = ['Date'] + list(export_data.columns)
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(row=1, column=col_idx, value=header)

    # Ajouter les données
    for row_idx, (date_idx, row_data) in enumerate(export_data.iterrows(), start=2):
        # Ajouter la date
        ws.cell(row=row_idx, column=1, value=date_idx)

        # Ajouter les autres colonnes
        for col_idx, value in enumerate(row_data, start=2):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)

            # Pour la colonne Variation (%), appliquer le format pourcentage
            if col_idx == 6:  # 6 est l'index pour Variation (%)
                # Convertir la valeur en décimal pour le format pourcentage Excel
                if pd.notna(value):
                    cell.value = value / 100  # Convertir en décimal pour Excel
                    cell.number_format = '0.00%'  # Format pourcentage avec 2 décimales

    # Ajuster la largeur des colonnes
    for col in range(1, len(headers) + 1):
        column_letter = get_column_letter(col)
        ws.column_dimensions[column_letter].width = 15

    workbook.save(output)
    processed_data = output.getvalue()
    return processed_data


# Fonction pour créer un graphique en fonction de la périodicité (jour ou mois)
def create_chart(data, asset_name, periodicity):
    # Créer une figure avec des sous-graphiques (prix + volume)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=(f'Prix de {asset_name}', 'Volume'),
                        row_heights=[0.7, 0.3])

    # Préparer les données selon la périodicité
    if periodicity == 'Jour':
        chart_data = data
    else:  # 'Mois'
        # Rééchantilloner les données par mois
        monthly_data = data.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
        chart_data = monthly_data

    # Ajouter le graphique en chandelier pour les prix
    fig.add_trace(
        go.Candlestick(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close'],
            name='Prix'
        ),
        row=1, col=1
    )

    # Ajouter le graphique de volume
    fig.add_trace(
        go.Bar(
            x=chart_data.index,
            y=chart_data['Volume'],
            name='Volume',
            marker_color='rgba(0, 128, 255, 0.7)'
        ),
        row=2, col=1
    )

    # Mise en forme du graphique
    fig.update_layout(
        title=f'{asset_name} - Données financières ({periodicity})',
        xaxis_title='Date',
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        xaxis_rangeslider_visible=False,
        showlegend=False
    )

    # Personnalisation des axes Y
    fig.update_yaxes(title_text='Prix', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)

    return fig


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

    # Choix de la périodicité pour le graphique (jour ou mois)
    chart_periodicity = st.radio(
        "Afficher le graphique par :",
        ["Jour", "Mois"],
        horizontal=True,
        key=f"periodicity_{tab_key}"
    )

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

            # Affichage du graphique
            st.subheader("Graphique")
            fig = create_chart(data, selected_asset, chart_periodicity)
            st.plotly_chart(fig, use_container_width=True)

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

            # Créer un excel avec les colonnes inversées et le format pourcentage pour la variation
            excel_data = create_excel(data, selected_asset)

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
