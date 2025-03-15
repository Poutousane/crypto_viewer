import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import io
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import plotly.graph_objects as go

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


# Fonction pour créer un graphique en bougies simplifié (style image)
def create_simple_candlestick_chart(data, asset_name):
    # Vérifier si les données sont valides
    if data.empty or len(data) <= 1:
        fig = go.Figure()
        fig.add_annotation(
            text="Données insuffisantes pour afficher le graphique",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=500, template="plotly_dark")
        return fig

    # Nettoyage des données
    valid_data = data[['Open', 'High', 'Low', 'Close']].dropna()

    if len(valid_data) <= 1:
        fig = go.Figure()
        fig.add_annotation(
            text="Données insuffisantes après nettoyage",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig.update_layout(height=500, template="plotly_dark")
        return fig

    # Création d'un graphique en bougies simple
    fig = go.Figure()

    # Ajouter les bougies
    fig.add_trace(go.Candlestick(
        x=valid_data.index,
        open=valid_data['Open'],
        high=valid_data['High'],
        low=valid_data['Low'],
        close=valid_data['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name='Prix'
    ))

    # Configuration du graphique pour qu'il ressemble à une image statique
    fig.update_layout(
        title='Graphique en bougies (day)',
        height=500,
        template="plotly_dark",
        margin=dict(l=40, r=40, t=60, b=40),
        # Désactiver toutes les interactions sauf le survol
        hovermode='closest',
        # Désactiver la légende
        showlegend=False
    )

    # Configurer les axes pour un aspect plus simple
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(80, 80, 80, 0.2)',
        title_text='',
        # Désactiver les zooms et panoramiques
        fixedrange=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(80, 80, 80, 0.2)',
        title_text='Prix',
        # Désactiver les zooms et panoramiques
        fixedrange=True
    )

    # Configuration avancée pour désactiver les barres d'outils et les interactions
    fig.update_layout(
        # Désactiver les interactions
        dragmode=False,
        # Désactiver les options de la barre d'outils
        modebar=dict(
            remove=[
                'zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale',
                'toImage', 'sendDataToCloud', 'toggleHover', 'resetViews',
                'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian',
                'select2d', 'lasso2d'
            ]
        ),
        modebar_orientation='v',
        modebar_remove=[
            'zoom', 'pan', 'select', 'lasso', 'autoScale', 'resetScale',
            'toImage', 'sendDataToCloud', 'toggleHover', 'resetViews',
            'toggleSpikelines', 'hoverCompareCartesian', 'hoverClosestCartesian'
        ]
    )

    # S'assurer que l'échelle y est appropriée
    price_range = valid_data['High'].max() - valid_data['Low'].min()
    padding = price_range * 0.1  # Ajouter 10% d'espace
    fig.update_yaxes(range=[valid_data['Low'].min() - padding, valid_data['High'].max() + padding])

    # Supprimer le rangeslider (barre de navigation en bas)
    fig.update_layout(xaxis_rangeslider_visible=False)

    # Configurer l'infobulle pour qu'elle soit simple mais informative
    fig.update_traces(
        hoverinfo='all',
        hoverlabel=dict(
            bgcolor="rgba(60, 60, 60, 0.8)",
            font_size=12,
            font_family="Arial"
        ),
        hovertemplate=(
                "<b>Date:</b> %{x|%Y-%m-%d}<br>" +
                "<b>Ouverture:</b> %{open:.2f}<br>" +
                "<b>Haut:</b> %{high:.2f}<br>" +
                "<b>Bas:</b> %{low:.2f}<br>" +
                "<b>Clôture:</b> %{close:.2f}<extra></extra>"
        )
    )

    return fig


# Fonction pour créer un Excel
def create_excel(data, sheet_name="Data"):
    output = io.BytesIO()

    # Formater les données pour l'export
    export_data = data.copy()

    # Calculer la variation quotidienne
    export_data['Variation (%)'] = export_data['Close'].pct_change() * 100

    # Convertir les indices en dates au format YYYY-MM-DD
    export_data.index = [d.strftime('%Y-%m-%d') for d in export_data.index]
    export_data.index.name = 'Date'

    # Réorganiser les colonnes
    export_data = export_data[['Close', 'High', 'Low', 'Open', 'Variation (%)', 'Volume']]

    # Renommer les colonnes
    export_data.columns = ['Price', 'High', 'Low', 'Open', 'Variation (%)', 'Volume']

    # Créer et configurer le fichier Excel
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
        data = yf.download(ticker_symbol, start=start_date_input, end=end_date_input, interval="1d")

        if data.empty:
            st.error(f"Aucune donnée disponible pour {selected_asset} dans la période sélectionnée.")
        else:
            # S'assurer que les données ne sont pas vides
            if not data.empty and len(data) > 0:
                # Extraction des valeurs pour les indicateurs clés
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

                # Affichage du graphique simplifié
                st.subheader("Graphique")

                # Créer le graphique en bougies simplifié (style image)
                simple_chart = create_simple_candlestick_chart(data, selected_asset)

                # Afficher le graphique
                st.plotly_chart(simple_chart, use_container_width=True, config={
                    'displayModeBar': False,  # Masquer la barre de mode
                    'staticPlot': False,  # Désactiver toutes les interactions sauf le survol
                    'scrollZoom': False  # Désactiver le zoom par défilement
                })

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
            else:
                st.error(f"Aucune donnée n'a été récupérée pour {selected_asset}.")

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
