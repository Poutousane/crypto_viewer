import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
import locale
import numpy as np

# Configuration pour l'affichage des nombres avec séparateurs de milliers
try:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')  # Pour format français
except:
    locale.setlocale(locale.LC_ALL, '')  # Utilise le locale par défaut

# Configuration de la page Streamlit
st.set_page_config(page_title="Crypto Data Viewer", layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': "Visualiseur de données crypto | v1.0"})

# Application d'un thème personnalisé
st.markdown("""
<style>
    .metric-container {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-label {
        font-size: 14px;
        color: #CCCCCC;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    .metric-delta {
        font-size: 14px;
        margin-top: 5px;
    }
    .positive {
        color: #4CAF50;
    }
    .negative {
        color: #F44336;
    }
    .header-container {
        background-color: #2C2C2C;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .chart-container {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    div.block-container {padding-top: 2rem;}
    div[data-testid="stMetricValue"] > div {font-size: 1.8rem !important;}
    div[data-testid="stMetricLabel"] {font-size: 1.1rem !important;}
    div.stMarkdown p {font-size: 1.1rem;}
    .css-1offfwp {border-radius: 8px !important;}
</style>
""", unsafe_allow_html=True)

# Titre principal avec style amélioré
st.markdown("""
<div class="header-container">
    <h1 style="color: white; text-align: center;">📊 Visualisation de Données Crypto</h1>
    <p style="color: #CCCCCC; text-align: center;">Explorez et analysez les tendances des cryptomonnaies</p>
</div>
""", unsafe_allow_html=True)

# Dictionnaire des cryptos disponibles avec leurs logos
crypto_dict = {
    "Bitcoin": {"ticker": "BTC-USD", "color": "#F7931A", "logo": "₿"},
    "Ethereum": {"ticker": "ETH-USD", "color": "#627EEA", "logo": "Ξ"},
    "Solana": {"ticker": "SOL-USD", "color": "#14F195", "logo": "◎"},
    "Cardano": {"ticker": "ADA-USD", "color": "#0033AD", "logo": "₳"},
    "Dogecoin": {"ticker": "DOGE-USD", "color": "#C2A633", "logo": "Ð"}
}


col1, col2, col3 = st.columns([1, 1, 1])

# Sélection de la crypto avec prévisualisation du logo et couleur
with col1:
    selected_crypto = st.selectbox(
        "Choisissez une crypto-monnaie:",
        list(crypto_dict.keys())
    )
    crypto_logo = crypto_dict[selected_crypto]["logo"]
    crypto_color = crypto_dict[selected_crypto]["color"]
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px;">
        <span style="font-size: 40px; color: {crypto_color};">{crypto_logo}</span>
    </div>
    """, unsafe_allow_html=True)

# Date par défaut (1 an en arrière)
default_start_date = date.today() - timedelta(days=365)
default_end_date = date.today()

# Sélection de dates
with col2:
    start_date = st.date_input("Date de début", default_start_date)

with col3:
    end_date = st.date_input("Date de fin", default_end_date)

    # Boutons periods rapides
    st.write("Périodes rapides:")
    period_cols = st.columns(4)

    if period_cols[0].button("7J"):
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

    if period_cols[1].button("1M"):
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()

    if period_cols[2].button("3M"):
        start_date = date.today() - timedelta(days=90)
        end_date = date.today()

    if period_cols[3].button("1A"):
        start_date = date.today() - timedelta(days=365)
        end_date = date.today()

# Vérification des dates
if start_date > end_date:
    st.error("⚠️ La date de début doit être antérieure à la date de fin.")
    st.stop()


# Fonction pour récupérer les données
@st.cache_data
def get_crypto_data(ticker, start, end):
    try:
        # Télécharger toutes les données brutes d'abord
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {e}")
        return None


# Fonction pour formater les grands nombres
def format_large_number(num):
    # Vérifier si num est une Series pandas et le convertir si nécessaire
    if isinstance(num, pd.Series):
        if num.empty:
            return "N/A"
        num = num.iloc[0]  # Prendre la première valeur

    # Vérifier si num est NaN
    if pd.isna(num):
        return "N/A"

    # Maintenant traiter la valeur numérique
    if num >= 1e9:
        return f"{num / 1e9:.2f} G"
    elif num >= 1e6:
        return f"{num / 1e6:.2f} M"
    elif num >= 1e3:
        return f"{num / 1e3:.2f} k"
    else:
        return f"{num:.2f}"


# Bouton pour lancer le chargement
col_button = st.columns([3, 1, 3])
with col_button[1]:
    load_button = st.button("📥 Charger les données", type="primary", use_container_width=True)

# Séparateur
st.markdown("<hr style='margin: 30px 0; border-color: #444444;'>", unsafe_allow_html=True)

# Affichage des données si le bouton est cliqué
if load_button:
    with st.spinner('⏳ Chargement des données en cours...'):
        ticker_symbol = crypto_dict[selected_crypto]["ticker"]
        raw_data = get_crypto_data(ticker_symbol, start_date, end_date)

        if raw_data is not None and not raw_data.empty:
            # Titre de section avec informations
            st.markdown(f"""
            <div style="background-color: {crypto_color}22; border-left: 5px solid {crypto_color}; padding: 15px; border-radius: 5px; margin-bottom: 25px;">
                <h2 style="color: white; margin: 0;">{crypto_logo} {selected_crypto} ({ticker_symbol})</h2>
                <p style="margin: 5px 0 0 0; color: #CCCCCC;">Données du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Calculer les métriques directement sur les colonnes d'origine
            first_price = raw_data['Close'].iloc[0]
            last_price = raw_data['Close'].iloc[-1]
            percent_change = ((last_price - first_price) / first_price) * 100
            avg_volume = raw_data['Volume'].mean()
            highest_price = raw_data['High'].max()
            lowest_price = raw_data['Low'].min()

            # Affichage des stats rapides avec style amélioré
            metric_cols = st.columns(4)

            # Prix actuel formaté correctement
            formatted_price = "$%.2f" % last_price
            metric_cols[0].markdown("""
            <div class="metric-container">
                <div class="metric-label">Prix actuel</div>
                <div class="metric-value">%s</div>
            </div>
            """ % formatted_price, unsafe_allow_html=True)

            # Variation avec couleur selon positif/négatif

            # Convertir percent_change en valeur simple si c'est une Series
            if isinstance(percent_change, pd.Series):
                if pd.isna(percent_change).any():
                    change_color = "neutral"  # ou une autre valeur par défaut
                    percent_change_value = 0  # valeur par défaut
                else:
                    percent_change_value = percent_change.iloc[0]  # prendre la première valeur
                    change_color = "positive" if percent_change_value >= 0 else "negative"
            else:
                # Si c'est déjà une valeur simple
                if pd.isna(percent_change):
                    change_color = "neutral"  # ou une autre valeur par défaut
                    percent_change_value = 0  # valeur par défaut
                else:
                    percent_change_value = percent_change
                    change_color = "positive" if percent_change_value >= 0 else "negative"

            change_symbol = "+" if percent_change_value >= 0 else ""
            metric_cols[1].markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Variation de prix</div>
                <div class="metric-value {change_color}">{change_symbol}{percent_change_value:.2f}%</div>
                <div class="metric-delta {change_color}">Depuis le {start_date.strftime('%d/%m/%Y')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Volume moyen
            metric_cols[2].markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Volume moyen</div>
                <div class="metric-value">{format_large_number(avg_volume)}</div>
            </div>
            """, unsafe_allow_html=True)

            # Fourchette de prix
            metric_cols[3].markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Fourchette de prix</div>
                <div class="metric-value">${lowest_price:,.2f} - ${highest_price:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Tableau résumé des statistiques
            st.markdown("""
            <div style="margin: 30px 0 20px 0;">
                <h3 style="color: white;">📊 Résumé statistique</h3>
            </div>
            """, unsafe_allow_html=True)

            stats_df = pd.DataFrame({
                'Statistique': ['Prix d\'ouverture', 'Prix de clôture', 'Prix le plus haut', 'Prix le plus bas',
                                'Volume total', 'Volume moyen', 'Variation absolue', 'Variation en %'],
                'Valeur': [
                    f"${raw_data['Open'].iloc[0]:,.2f}",
                    f"${raw_data['Close'].iloc[-1]:,.2f}",
                    f"${raw_data['High'].max():,.2f}",
                    f"${raw_data['Low'].min():,.2f}",
                    f"{format_large_number(raw_data['Volume'].sum())}",
                    f"{format_large_number(raw_data['Volume'].mean())}",
                    f"${(last_price - first_price):,.2f}",
                    f"{change_symbol}{percent_change:.2f}%"
                ]
            })

            # Afficher le tableau de statistiques
            st.dataframe(stats_df, use_container_width=True,
                         column_config={
                             "Statistique": st.column_config.TextColumn("Statistique"),
                             "Valeur": st.column_config.TextColumn("Valeur")
                         },
                         hide_index=True)

            # Affichage d'un graphique interactif avec plotly amélioré
            st.markdown("""
            <div style="margin: 30px 0 20px 0;">
                <h3 style="color: white;">📈 Graphique d'évolution du prix</h3>
            </div>
            """, unsafe_allow_html=True)

            # Graphique en bougie avec ajout des moyennes mobiles
            fig = go.Figure()

            # Ajouter chandelier
            fig.add_trace(go.Candlestick(
                x=raw_data.index,
                open=raw_data['Open'],
                high=raw_data['High'],
                low=raw_data['Low'],
                close=raw_data['Close'],
                name="Chandelier",
                increasing=dict(line=dict(color=crypto_color)),
                decreasing=dict(line=dict(color='#F44336')),
                increasing_fillcolor=f"{crypto_color}80",
                decreasing_fillcolor='rgba(244, 67, 54, 0.5)'
            ))

            # Calculer et ajouter les moyennes mobiles
            raw_data['MA20'] = raw_data['Close'].rolling(window=20).mean()
            raw_data['MA50'] = raw_data['Close'].rolling(window=50).mean()

            fig.add_trace(go.Scatter(
                x=raw_data.index,
                y=raw_data['MA20'],
                mode='lines',
                name='Moyenne Mobile 20j',
                line=dict(color='#FFD700', width=1.5)
            ))

            fig.add_trace(go.Scatter(
                x=raw_data.index,
                y=raw_data['MA50'],
                mode='lines',
                name='Moyenne Mobile 50j',
                line=dict(color='#1E90FF', width=1.5)
            ))

            # Configuration avancée du graphique
            fig.update_layout(
                title=f"Évolution du prix de {selected_crypto} ({ticker_symbol})",
                xaxis_title="Date",
                yaxis_title="Prix (USD)",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,1)',
                font=dict(color='white')
            )

            # Grille et axes pour meilleure lisibilité
            fig.update_xaxes(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.3)',
                tickfont=dict(size=12)
            )

            fig.update_yaxes(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.3)',
                tickprefix='$',
                tickfont=dict(size=12)
            )

            # Afficher le graphique principal
            st.plotly_chart(fig, use_container_width=True)

            # Graphique de volume amélioré
            st.markdown("""
            <div style="margin: 30px 0 20px 0;">
                <h3 style="color: white;">📊 Volume d'échanges</h3>
            </div>
            """, unsafe_allow_html=True)

            # Couleurs de volume basées sur la tendance du prix
            colors = ['#4CAF50' if raw_data['Close'].iloc[i] > raw_data['Open'].iloc[i] else '#F44336'
                      for i in range(len(raw_data))]

            volume_fig = go.Figure()
            volume_fig.add_trace(go.Bar(
                x=raw_data.index,
                y=raw_data['Volume'],
                name='Volume',
                marker_color=colors
            ))

            # Ajouter une moyenne mobile du volume
            raw_data['VolMA20'] = raw_data['Volume'].rolling(window=20).mean()
            volume_fig.add_trace(go.Scatter(
                x=raw_data.index,
                y=raw_data['VolMA20'],
                mode='lines',
                name='Volume MM 20j',
                line=dict(color='#FFD700', width=2)
            ))

            # Configuration du graphique de volume
            volume_fig.update_layout(
                title=f"Volume d'échanges de {selected_crypto}",
                xaxis_title="Date",
                yaxis_title="Volume",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(l=0, r=0, t=50, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(30,30,30,1)',
                font=dict(color='white')
            )

            volume_fig.update_xaxes(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.3)',
                tickfont=dict(size=12)
            )

            volume_fig.update_yaxes(
                showgrid=True,
                gridcolor='rgba(80, 80, 80, 0.3)',
                tickfont=dict(size=12)
            )

            # Afficher le graphique de volume
            st.plotly_chart(volume_fig, use_container_width=True)

            # Affichage du tableau de données
            st.markdown("""
            <div style="margin: 30px 0 20px 0;">
                <h3 style="color: white;">📋 Tableau de données</h3>
            </div>
            """, unsafe_allow_html=True)

            # Préparation des données pour l'affichage et le téléchargement
            display_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            display_data = raw_data[display_cols].copy().reset_index()
            display_data.columns = ['Date', 'Ouverture', 'Plus haut', 'Plus bas', 'Clôture', 'Volume']

            # Formater les colonnes numériques
            for col in ['Ouverture', 'Plus haut', 'Plus bas', 'Clôture']:
                display_data[col] = display_data[col].map('${:,.2f}'.format)

            # Formater les volumes
            display_data['Volume'] = display_data['Volume'].apply(lambda x: format_large_number(x))

            # Afficher le DataFrame avec style
            st.dataframe(
                display_data,
                use_container_width=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                    "Ouverture": "Ouverture",
                    "Plus haut": "Plus haut",
                    "Plus bas": "Plus bas",
                    "Clôture": "Clôture",
                    "Volume": "Volume"
                },
                hide_index=True
            )

            # Option pour télécharger les données
            raw_display = raw_data.reset_index()

            # Préparation des données pour le téléchargement
            download_data = raw_display.copy()
            # Convertir la date en format lisible
            download_data['Date'] = download_data['Date'].dt.strftime('%Y-%m-%d')

            csv = download_data.to_csv(index=False)

            st.download_button(
                label="📥 Télécharger les données en CSV",
                data=csv,
                file_name=f'{selected_crypto}_{start_date}_to_{end_date}.csv',
                mime='text/csv',
                help="Télécharger toutes les données au format CSV"
            )

        else:
            st.warning("⚠️ Aucune donnée disponible pour cette période. Essayez de modifier les dates.")

# Footer
st.markdown("<hr style='margin: 30px 0; border-color: #444444;'>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #888888; font-size: 0.8em;">
    <p>📊 Données fournies par Yahoo Finance | Application créée avec Streamlit | &copy; 2023</p>
</div>
""", unsafe_allow_html=True)
