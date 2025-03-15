import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash
from dash import html, dcc, callback, Input, Output, State
import os
import requests
import json
from datetime import datetime, timedelta
import subprocess
import sys

# Définir les chemins des fichiers
ROOT_DIR = "/mount"
DATA_DIR = os.path.join(ROOT_DIR, "data")
ASSETS_FILE = os.path.join(DATA_DIR, "assets_list.json")
CONFIG_FILE = os.path.join(ROOT_DIR, "config.json")

# Créer les répertoires s'ils n'existent pas
os.makedirs(DATA_DIR, exist_ok=True)

# Configuration par défaut
DEFAULT_CONFIG = {
    "api_key": "YOUR_API_KEY",
    "default_timeframe": "day",
    "display_mode": "dark",
    "auto_refresh": True,
    "refresh_interval": 3600  # en secondes
}

# Couleurs pour les différents thèmes
COLORS = {
    "dark": {
        "background": "#1e1e1e",
        "text": "#ffffff",
        "accent": "#61dafb",
        "secondary": "#282c34",
        "positive": "#4caf50",
        "negative": "#f44336",
        "neutral": "#9e9e9e"
    },
    "light": {
        "background": "#f8f9fa",
        "text": "#212529",
        "accent": "#007bff",
        "secondary": "#e9ecef",
        "positive": "#28a745",
        "negative": "#dc3545",
        "neutral": "#6c757d"
    }
}


# Chargement de la configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def load_asset_list():
    if os.path.exists(ASSETS_FILE):
        with open(ASSETS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Liste minimale par défaut
        default_assets = [
            {"symbol": "BTC/USDT", "name": "Bitcoin", "category": "cryptocurrency"},
            {"symbol": "ETH/USDT", "name": "Ethereum", "category": "cryptocurrency"},
            {"symbol": "ADA/USDT", "name": "Cardano", "category": "cryptocurrency"},
            {"symbol": "DOGE/USDT", "name": "Dogecoin", "category": "cryptocurrency"}
        ]
        with open(ASSETS_FILE, 'w') as f:
            json.dump(default_assets, f, indent=4)
        return default_assets


def fetch_data(symbol, timeframe="day"):
    """
    Récupère les données historiques pour un actif donné.
    """
    # Simulation de données pour la démonstration
    # Dans une version réelle, remplacer par un appel API

    today = datetime.now()

    # Déterminer les paramètres en fonction du timeframe
    if timeframe == "day":
        days_back = 30
        interval = '1d'
    elif timeframe == "week":
        days_back = 90
        interval = '1w'
    elif timeframe == "month":
        days_back = 365
        interval = '1M'
    else:
        days_back = 30
        interval = '1d'

    # Créer un index de dates
    date_range = pd.date_range(end=today, periods=days_back)

    # Simuler des données de prix avec une tendance
    base_price = 100 + np.random.random() * 900  # Prix de base entre 100 et 1000

    if "/USDT" in symbol:
        volatility = 0.05  # Plus volatil pour les crypto
    else:
        volatility = 0.02  # Moins volatil pour les actions

    # Simuler une tendance générale
    trend = np.linspace(0, np.random.choice([-1, 1]) * 0.5, days_back)

    # Créer les prix
    closes = []
    last_close = base_price

    for i in range(days_back):
        change = np.random.normal(0, volatility) + trend[i] / days_back
        last_close = last_close * (1 + change)
        closes.append(max(last_close, 1))  # Éviter les prix négatifs

    closes = np.array(closes)

    # Créer les autres colonnes OHLC
    opens = closes * (1 + np.random.normal(0, volatility / 2, days_back))
    highs = np.maximum(opens, closes) * (1 + abs(np.random.normal(0, volatility, days_back)))
    lows = np.minimum(opens, closes) * (1 - abs(np.random.normal(0, volatility, days_back)))
    volumes = np.random.normal(base_price * 1000, base_price * 500, days_back)
    volumes = np.abs(volumes)

    # Créer le DataFrame
    data = pd.DataFrame({
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes
    }, index=date_range)

    return data


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
        name='Prix',
        hoverinfo='text',
        # Utiliser 'text' au lieu de 'hovertemplate'
        text=[
            f"Date: {d.strftime('%Y-%m-%d')}<br>" +
            f"Ouverture: {o:.2f}<br>" +
            f"Haut: {h:.2f}<br>" +
            f"Bas: {l:.2f}<br>" +
            f"Clôture: {c:.2f}"
            for d, o, h, l, c in
            zip(valid_data.index, valid_data['Open'], valid_data['High'], valid_data['Low'], valid_data['Close'])
        ]
    ))

    # Configuration du graphique pour qu'il ressemble à une image statique
    fig.update_layout(
        title='Graphique en bougies (day)',
        height=500,
        template="plotly_dark",
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='closest',
        showlegend=False
    )

    # Configurer les axes pour un aspect plus simple
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(80, 80, 80, 0.2)',
        title_text='',
        fixedrange=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(80, 80, 80, 0.2)',
        title_text='Prix',
        fixedrange=True
    )

    # Configuration avancée pour désactiver les barres d'outils et les interactions
    fig.update_layout(
        dragmode=False,
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
        hoverlabel=dict(
            bgcolor="rgba(60, 60, 60, 0.8)",
            font_size=12,
            font_family="Arial"
        )
    )

    return fig


def create_indicator(title, value, change_value=None, is_percentage=False, prefix="", suffix=""):
    """
    Crée un élément d'indicateur pour afficher une valeur avec éventuellement un changement.
    """
    value_str = f"{prefix}{value:,.2f}{suffix}"
    color_class = ""
    change_element = ""

    if change_value is not None:
        if is_percentage:
            change_str = f"{change_value:+.2f}%"
        else:
            change_str = f"{prefix}{change_value:+,.2f}{suffix}"

        if change_value > 0:
            color_class = "positive"
            change_element = f"<span class='change {color_class}'>▲ {change_str}</span>"
        elif change_value < 0:
            color_class = "negative"
            change_element = f"<span class='change {color_class}'>▼ {change_str}</span>"
        else:
            color_class = "neutral"
            change_element = f"<span class='change {color_class}'>{change_str}</span>"

    return html.Div(
        className=f"indicator",
        children=[
            html.Div(title, className="indicator-title"),
            html.Div([
                html.Span(value_str, className="indicator-value"),
                html.Div([html.Span(change_element)], dangerously_allow_html=True)
            ])
        ]
    )


def display_asset_data(data, selected_asset):
    """
    Crée l'affichage complet pour un actif sélectionné.
    """
    # En cas de données vides ou insuffisantes
    if data.empty or len(data) <= 1:
        return html.Div(
            className="asset-container",
            children=[
                html.Div(
                    className="error-message",
                    children=["Données insuffisantes pour cet actif."]
                )
            ]
        )

    # Extraction des valeurs pour les indicateurs clés
    latest_close_value = float(data['Close'].iloc[-1])
    first_close_value = float(data['Close'].iloc[0])
    variation_value = ((latest_close_value - first_close_value) / first_close_value) * 100
    latest_volume_value = float(data['Volume'].iloc[-1])

    # Création des indicateurs
    indicators_row = html.Div(
        className="indicators-row",
        children=[
            create_indicator("Dernier Prix", latest_close_value, prefix="$"),
            create_indicator("Variation", variation_value, is_percentage=True),
            create_indicator("Volume", latest_volume_value, prefix="$")
        ]
    )

    # Création du graphique
    simple_chart = create_simple_candlestick_chart(data, selected_asset)

    # Combinaison des éléments dans un conteneur
    return html.Div(
        className="asset-container",
        children=[
            html.H2(selected_asset, className="asset-title"),
            indicators_row,
            dcc.Graph(
                figure=simple_chart,
                config={'displayModeBar': False, 'staticPlot': True},
                className="asset-chart"
            )
        ]
    )


def create_layout():
    """
    Crée la mise en page de l'application.
    """
    # Chargement des actifs et de la configuration
    assets_list = load_asset_list()
    config = load_config()

    # Boutons de sélection des actifs
    asset_buttons = []

    # Groupés par catégorie
    categories = {}
    for asset in assets_list:
        category = asset.get("category", "other")
        if category not in categories:
            categories[category] = []
        categories[category].append(asset)

    # Création des boutons regroupés par catégorie
    for category, assets in categories.items():
        category_div = html.Div(
            className="asset-category",
            children=[
                html.H3(category.capitalize(), className="category-title"),
                html.Div(
                    className="asset-buttons",
                    children=[
                        html.Button(
                            asset["name"],
                            id={"type": "asset-button", "index": asset["symbol"]},
                            className="asset-button",
                            n_clicks=0
                        ) for asset in assets
                    ]
                )
            ]
        )
        asset_buttons.append(category_div)

    # Sélection d'intervalle de temps
    timeframe_selector = html.Div(
        className="timeframe-selector",
        children=[
            html.Label("Intervalle de Temps", className="selector-label"),
            dcc.Dropdown(
                id="timeframe-dropdown",
                options=[
                    {'label': 'Journalier', 'value': 'day'},
                    {'label': 'Hebdomadaire', 'value': 'week'},
                    {'label': 'Mensuel', 'value': 'month'}
                ],
                value=config["default_timeframe"],
                clearable=False,
                className="timeframe-dropdown"
            )
        ]
    )

    # Zone principale d'affichage
    display_area = html.Div(
        id="display-area",
        className="display-area",
        children=[
            html.Div(
                className="welcome-message",
                children=[
                    html.H2("Bienvenue sur Crypto Viewer"),
                    html.P("Sélectionnez un actif dans la liste de gauche pour afficher ses informations.")
                ]
            )
        ]
    )

    # Indicateur de mise à jour
    update_info = html.Div(
        id="update-info",
        className="update-info",
        children=f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Bouton de rechargement
    reload_button = html.Button(
        "⟳ Recharger",
        id="reload-button",
        className="reload-button",
        n_clicks=0
    )

    # Options footer
    footer = html.Div(
        className="footer",
        children=[
            update_info,
            reload_button
        ]
    )

    # Assemblage de la mise en page
    layout = html.Div(
        className=f"app-container {config['display_mode']}",
        children=[
            html.Div(
                className="sidebar",
                children=[
                    html.H1("Crypto Viewer", className="app-title"),
                    html.Div(
                        className="sidebar-content",
                        children=asset_buttons
                    ),
                    timeframe_selector
                ]
            ),
            html.Div(
                className="main-content",
                children=[
                    display_area,
                    footer
                ]
            ),
            # Store pour stocker l'actif actuel
            dcc.Store(id="current-asset", data=None),
            # Interval pour le rafraîchissement automatique
            dcc.Interval(
                id="refresh-interval",
                interval=config["refresh_interval"] * 1000,  # en millisecondes
                disabled=not config["auto_refresh"]
            )
        ]
    )

    return layout


# Création de l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Définition du titre de l'application
app.title = "Crypto Viewer"

# Configuration du layout initial
app.layout = create_layout()


# Callbacks pour l'interactivité
@app.callback(
    [Output("display-area", "children"), Output("current-asset", "data")],
    [Input({"type": "asset-button", "index": dash.dependencies.ALL}, "n_clicks"),
     Input("reload-button", "n_clicks"),
     Input("refresh-interval", "n_ticks"),
     Input("timeframe-dropdown", "value")],
    [State("current-asset", "data")]
)
def update_display(asset_clicks, reload_clicks, refresh_ticks, timeframe, current_asset):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    selected_asset = current_asset

    # Vérifier si c'est un bouton d'actif qui a été cliqué
    if "asset-button" in trigger_id:
        # Obtenir l'index de l'actif à partir du déclencheur
        button_dict = json.loads(trigger_id)
        if button_dict.get("type") == "asset-button":
            selected_asset = button_dict.get("index")

    # Si aucun actif n'est sélectionné, ne rien faire
    if not selected_asset:
        return dash.no_update, dash.no_update

    # Récupérer les données pour l'actif
    data = fetch_data(selected_asset, timeframe)

    # Afficher les données de l'actif
    return display_asset_data(data, selected_asset), selected_asset


@app.callback(
    Output("update-info", "children"),
    [Input("reload-button", "n_clicks"),
     Input("refresh-interval", "n_ticks")]
)
def update_refresh_time(reload_clicks, refresh_ticks):
    return f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


# Lancement de l'application
if __name__ == "__main__":
    try:
        # Lancer le serveur
        app.run_server(debug=True, host='0.0.0.0', port=8050)
    except Exception as e:
        print(f"Une erreur s'est produite lors du lancement: {e}")
        sys.exit(1)
