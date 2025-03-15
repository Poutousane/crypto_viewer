import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import io
from openpyxl import Workbook
import matplotlib.dates as mdates

# Configuration de page
st.set_page_config(layout="wide", page_title="Finance Viewer")

# Titre de l'application
st.title("📊 Finance Viewer")

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
    "JPMorgan Chase": "JPM",
    "Coca-Cola": "KO",
    "Disney": "DIS"
}

other_assets = {
    "Or": "GC=F",
    "Argent": "SI=F",
    "Pétrole brut": "CL=F",
    "Gaz naturel": "NG=F",
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "S&P 500": "^GSPC",
    "Dow Jones": "^DJI",
    "NASDAQ": "^IXIC"
}


# Fonction pour rééchantillonner les données
def resample_data(data, period):
    if period == 'Jour':
        return data
    elif period == 'Semaine':
        return data.resample('W').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })
    elif period == 'Mois':
        return data.resample('M').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        })


# Fonction pour créer un Excel
def create_excel(data, sheet_name="Data"):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    data.to_excel(writer, sheet_name=sheet_name)
    writer.close()
    processed_data = output.getvalue()
    return processed_data


# Fonction principale d'affichage des données financières
def display_financial_data(asset_dict, asset_type):
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_asset = st.selectbox(f"Choisissez un{' ' + asset_type if asset_type else ''}", list(asset_dict.keys()))

    with col2:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        start_date_input = st.date_input("Date de début", value=start_date, key=f"start_{asset_type}")

    with col3:
        end_date_input = st.date_input("Date de fin", value=end_date, key=f"end_{asset_type}")

    # Récupération des données
    ticker_symbol = asset_dict[selected_asset]
    try:
        # Ajouter 1 jour à la date de fin pour l'inclure dans les données
        end_date_inclusive = end_date_input + timedelta(days=1)
        data = yf.download(ticker_symbol, start=start_date_input, end=end_date_inclusive)

        if data.empty:
            st.error(f"Aucune donnée disponible pour {selected_asset} dans la période sélectionnée.")
        else:
            # Extraction explicite des valeurs scalaires individuelles
            latest_close_value = float(data['Close'].iloc[-1])
            first_close_value = float(data['Close'].iloc[0])
            variation_value = ((latest_close_value - first_close_value) / first_close_value) * 100

            # Pour les actifs sans volume (comme certaines devises)
            has_volume = 'Volume' in data.columns and not data['Volume'].isnull().all()

            # Affichage des indicateurs clés
            st.subheader("Indicateurs clés")

            if has_volume:
                metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                latest_volume_value = float(data['Volume'].iloc[-1])
            else:
                metrics_col1, metrics_col2 = st.columns(2)

            with metrics_col1:
                unit = "$" if asset_type in ["crypto", "action"] or selected_asset in ["Or", "Argent", "Pétrole brut",
                                                                                       "Gaz naturel"] else ""
                formatted_close = f"{unit}{latest_close_value:.2f}"
                st.metric("Prix de clôture", formatted_close)

            with metrics_col2:
                formatted_variation = f"{variation_value:.2f}%"
                formatted_delta = f"{variation_value:.2f}%"
                st.metric("Variation", formatted_variation, delta=formatted_delta)

            if has_volume:
                with metrics_col3:
                    latest_volume_value = float(data['Volume'].iloc[-1])
                    if latest_volume_value >= 1e9:
                        vol_str = f"{latest_volume_value / 1e9:.2f} G"
                    elif latest_volume_value >= 1e6:
                        vol_str = f"{latest_volume_value / 1e6:.2f} M"
                    elif latest_volume_value >= 1e3:
                        vol_str = f"{latest_volume_value / 1e3:.2f} k"
                    else:
                        vol_str = f"{latest_volume_value:.2f}"
                    st.metric("Volume (dernier jour)", vol_str)

            # Création des onglets
            tab1, tab2 = st.tabs(["📋 Tableau", "📈 Graphes"])

            with tab1:
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
                unit = "$" if asset_type in ["crypto", "action"] or selected_asset in ["Or", "Argent", "Pétrole brut",
                                                                                       "Gaz naturel"] else ""
                display_data['Open'] = [f"{unit}{x:.2f}" for x in open_values]
                display_data['High'] = [f"{unit}{x:.2f}" for x in high_values]
                display_data['Low'] = [f"{unit}{x:.2f}" for x in low_values]
                display_data['Close'] = [f"{unit}{x:.2f}" for x in close_values]

                # Formater la variation avec gestion des NaN
                daily_changes = []
                for x in data['Daily_Change'].to_numpy():
                    if pd.isna(x):
                        daily_changes.append("N/A")
                    else:
                        daily_changes.append(f"{float(x):.2f}%")
                display_data['Variation (%)'] = daily_changes

                # Formater le volume si disponible
                if has_volume:
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

                # Option de téléchargement en XLSX
                # Préparer les données pour l'export (sans la colonne Daily_Change)
                export_data = data.drop('Daily_Change', axis=1, errors='ignore').copy()

                # Créer un excel avec les données
                excel_data = create_excel(export_data, f"{selected_asset}")

                st.download_button(
                    label="📥 Télécharger les données (XLSX)",
                    data=excel_data,
                    file_name=f'{selected_asset}_{start_date_input}_{end_date_input}.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key=f"download_{asset_type}"
                )

            with tab2:
                # Sélectionner la période d'affichage
                period = st.radio("Période d'affichage", ["Jour", "Semaine", "Mois"], horizontal=True,
                                  key=f"period_{asset_type}")

                # Rééchantillonner les données selon la période choisie
                resampled_data = resample_data(data, period)

                # Créer le graphique avec matplotlib
                fig, ax = plt.subplots(figsize=(12, 6))

                # Tracer les prix de clôture
                ax.plot(resampled_data.index, resampled_data['Close'], 'b-', label='Prix de clôture')

                # Configurer le graphique
                unit = "$" if asset_type in ["crypto", "action"] or selected_asset in ["Or", "Argent", "Pétrole brut",
                                                                                       "Gaz naturel"] else ""
                ax.set_title(f'Évolution du prix de {selected_asset} ({period.lower()})', fontsize=16)
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel(f'Prix ({unit})', fontsize=12)
                ax.grid(True, linestyle='--', alpha=0.7)

                # Formatter l'axe des X pour n'afficher que la date sans l'heure
                date_format = mdates.DateFormatter('%Y-%m-%d')
                ax.xaxis.set_major_formatter(date_format)
                plt.xticks(rotation=45)

                # Ajuster automatiquement les paramètres du graphique
                fig.tight_layout()

                # Afficher la légende
                ax.legend()

                # Afficher le graphique dans Streamlit
                st.pyplot(fig)

                # Option pour afficher un graphique en chandelier (OHLC)
                if st.checkbox("Afficher le graphique en chandelier (OHLC)", key=f"ohlc_{asset_type}"):
                    from mplfinance.original_flavor import candlestick_ohlc

                    # Créer un nouveau graphique
                    fig, ax = plt.subplots(figsize=(12, 6))

                    # Préparer les données pour le graphique en chandelier
                    ohlc = resampled_data[['Open', 'High', 'Low', 'Close']].copy()

                    # Convertir l'index en dates numériques pour matplotlib
                    ohlc_dates = mdates.date2num(ohlc.index.to_pydatetime())
                    ohlc_values = list(zip(ohlc_dates,
                                           ohlc['Open'].values,
                                           ohlc['High'].values,
                                           ohlc['Low'].values,
                                           ohlc['Close'].values))

                    # Créer le graphique en chandelier
                    candlestick_ohlc(ax, ohlc_values, width=0.6, colorup='g', colordown='r')

                    # Configurer le graphique
                    ax.set_title(f'Graphique OHLC de {selected_asset} ({period.lower()})', fontsize=16)
                    ax.set_xlabel('Date', fontsize=12)
                    ax.set_ylabel(f'Prix ({unit})', fontsize=12)

                    # Formatter l'axe des X pour afficher les dates
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    plt.xticks(rotation=45)

                    # Ajuster automatiquement les paramètres du graphique
                    fig.tight_layout()

                    # Afficher le graphique dans Streamlit
                    st.pyplot(fig)

    except Exception as e:
        st.error(f"Une erreur s'est produite lors de la récupération des données : {e}")
        import traceback
        st.error(f"Traceback détaillé: {traceback.format_exc()}")


# Création des onglets principaux pour les types d'actifs
asset_tab1, asset_tab2, asset_tab3 = st.tabs(["💰 Cryptomonnaies", "📈 Actions", "🌍 Autres actifs"])

# Affichage des données selon l'onglet sélectionné
with asset_tab1:
    display_financial_data(crypto_assets, "crypto")

with asset_tab2:
    display_financial_data(stock_assets, "action")

with asset_tab3:
    display_financial_data(other_assets, "autre")
