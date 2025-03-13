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

# Paramètres de sélection dans une boîte stylisée
st.markdown("""
<div style="background-color: #2C2C2C; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
    <h2 style="color: white; font-size: 1.5em; margin-bottom: 15px;">🔍 Paramètres de recherche</h2>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])

# Sélection de la crypto avec prévisualisation du logo et couleur
with col1:
    selected_crypto = st.selectbox(
        "Choisissez une crypto-monnaie:",
        list(crypto_dict.keys()) Peugeot 2008, Mazda CX-3, Mitsubishi ASX: Kleine Grobiane - AUTO MOTOR UND SPORT
 The second in a three-part series of podcasts unpacking the IPCC Special Report on Global Warming of 1.5°C.
In this episode, we explore the key 1.5°C pathways identified by the IPCC, and what they'll mean for the global economic and social transition.
We unpack key issues including the role of CO2 removal and negative emissions, the 'hard to decarbonise' sectors, and the need to ensure a just transition for workers and communities.
Guest: Dr Joeri Rogelj, coordinating lead author on the IPCC Special Report on Global Warming of 1.5°C, Climate Science Lead at Climate Analytics beyond 1.5, and Research Scholar at the International Institute for Applied Systems Analysis.
 "This is an important question around the costs and the benefits of mitigation. So what the report clearly says is that limiting warming to 1.5 degrees Celsius would require global greenhouse gas emissions to peak now and to be reduced by about 45% by 2030 compared to the 2010 levels, and this 45% reduction by 2030 is then required to be followed by a further reduction to net zero emissions, so they fully compensate all the remaining emissions by 2050. So this indeed means, as you already indicated, unprecedented rates of emission reductions in all sectors, and this implies obviously transitions at a scale and at a pace that we haven't seen in the past. These required transitions would necessarily come with investments."
 "So these investments would be very large. We're talking about investments of the order of 1.5 to 3% of global GDP that would have to be invested globally. But at the same time, this will bring benefits in the short term and the long term. So a part of these economic benefits on the short term are for instance, savings due to reduced air pollution, and also savings due to the reduced health impacts that kind of follow from the reduced air pollution. And these savings also occur in the near term, and these savings can be very substantial in some regions. We've also included in the report some numerical examples of some of these avoided health damages, like for instance, looking at air pollution and limiting warming to 1.5 degrees Celsius, and we would save for instance, 100 to 200 million premature deaths over the 21st century, just by the reduced air pollution which comes along in these mitigation scenarios. And we also note that this is just the start of the benefits. So these health benefits from reducing air pollution do not yet take into account the benefits from for instance, avoiding pollution of water, or other impacts on land. This also doesn't take into account the potential, the avoided climate damages, the reduced risks from extreme heat or from heavy precipitation events, or large scale singular events."
 "So in the report, we clearly say that limiting global warming to 1.5 degrees Celsius means that the available global carbon budget, which is the amount of carbon dioxide that can still be released into the atmosphere without exceeding 1.5 degrees, is already being used up at a very high rate, and this leaves a very small window of opportunity that is very quickly being closed. So at current rates, the budget for 1.5 degrees Celsius would be entirely gone within ten to 14 years, and this really means that we need to take action massively straight away. So the report clearly says that we need to have global emissions peaking right now, and then declining very rapidly in the decades after that."
 "If you start with the mitigation action today, there is a benefit of doing that. There are benefits of starting early, and these are not only in terms of a smoother implementation of the required transitions, but also in terms of the costs, the economic costs of doing so. And I think here's an important point to add: we have a lot of focus on the economic costs for mitigating emissions, but there's also an economic cost of not doing so. Economic cost that we would incur because of climate damages, in the way of lives that are lost, properties that are damaged, etc. And all these costs that come with climate impacts are not yet included in the mitigation costs that are assessed in these models."
 "So negative emissions, or CO2 removal technologies, are a very important contribution, or have a very important contribution in limiting and achieving our most ambitious climate targets in the long run. This is not a question of replacing mitigation with negative emissions, this is a question of not only achieving a balance between remaining greenhouse gas emissions, and removing them from the atmosphere, but also later on potentially removing more from the atmosphere than is being emitted. And so this is a necessity from a physical perspective. If you're looking long-term at our climate targets, we see that all of these pathways towards 1.5 or 2 degrees Celsius either rely on, or would be strongly helped, if these technologies come into play and can be upskilled at a sufficient level. In the pathways that we've assessed in the IPCC report, all of them use some form of carbon dioxide removal, and yet they're very diverse in the methods they use. So there's always a portfolio of different CO2 removal methods. Some of them include afforestation and reforestation, so the planting of trees and protection of degraded land; at the same time, we also see technologies that really act on the global-scale so-called BECCS, bioenergy with carbon capture and storage come into play. "
 "So this is a set of questions that clearly have quite a lot of attention, both in the literature and in the public debate. The IPCC in general doesn't make any value judgements on these issues. As scientists, we're trying to distil the available knowledge and the factual basis of the available literature in this space. And when it comes to these pathways, what we clearly show is the scale of the challenge, and the scale of the changes that would be required from all actors and all sectors. And we clearly indicate the synergies and trade-offs that would be involved when implementing these kinds of systemic changes. And some of these changes would indeed need to happen in sectors which produce and use coal and oil and gas. And while we don't make explicit value judgements in terms of which kind of pathway is to be preferred, we clearly highlight that the transition has to happen, but at the same time, it's important to engage the population that works in these sectors, if we want to make this transition a smooth one. So there are elements in our literature that describe policies that can enable a just and smooth transition, and it's these kind of policies that the literature has documented as being really key to make these ambitious transitions work out in the end."
 "So we also have important information about options to decarbonise heavy industry and heavy transport in the report. And many of these options are today, indeed not at the level where they would immediately enter markets where they can compete with incumbent technologies. But this is why we have dedicated an entire section to the enabling conditions for this transition to happen. And these enabling conditions set out the space in which technological innovation and diffusion of these technologies can be accelerated. So more specifically for heavy industry, for example, there are options available that range from electrification of these processes; switching to hydrogen, for example; a further deployment of carbon capture and storage; and with these technologies, the different sectors could reach carbon neutrality, but they need to be developed, they need to mature, they need to be made available at a large scale. But all of this obviously takes time, but at the same time, I have to say that the literature has a very optimistic outlook on these developments."
 "Another very important question is one of cost. So what are the costs of these transitions, but also what are the investments that would be required to make these transitions happen? So to give an idea, pathways that limit warming to 1.5 degrees Celsius would imply higher upfront investments in the energy supply sector compared to where we're going now, and these increases would be, for example, about 1.5 to 3% of global GDP in investments that are required on average for the upfront investment costs. At the same time, when we look at the overall mitigation costs and we take into account these upfront investment costs, estimates for the costs of limiting warming to 1.5 degrees Celsius, compared for example to a baseline without new climate policies at all, the cost would be around 3% of global GDP in 2050. But very importantly, there's a need to put these numbers into context, and there are two further points that I want to add. One, these costs are only the mitigation costs. These are not the entire costs and benefits. So the avoided climate damages that would follow from limiting warming to 1.5 degrees Celsius, compared to higher levels of warming, they are not reflected in these estimates. So that's one aspect that we need to take into account. And a second aspect is that these are just the global costs. There's obviously a lot of variation in these costs across regions, and there might be regions where it's much more challenging and much more costly to implement these transitions, and this means that questions of equity and fairness play a very important role and are a crucial enabler to move to making 1.5 degrees happen."
 "In the report, we also assess the implications of policy strength and timing in our different climate pathways. Essentially, this means that we are assuming that we either can achieve immediate and full cooperation across all nations and all individuals in the world, which is generally the ideal scenario, and we can start immediately today, which I think we know is extremely optimistic. But there are also scenarios where for instance, we delay the strengthening of policies for about a decade, so we assume that the world basically continues with the level of policies that were implemented in 2020, until 2030. And we can also have scenarios that where we call them in the report, middle of the road scenarios, where some of the barriers to the technological, or institutional, or behavioural transformations are overcome, but others are not. Essentially, what these scenarios clearly show is that the more of these barriers and constraints we can overcome, the easier it will be to limit warming to 1.5, 2, or actually any temperature level. But because we are facing these massive and very rapid required changes, any delay in terms of implementing climate policies will make it harder, could lead to a higher reliance on CO2 removal measures in the long run,
and also will lead to higher cumulative emissions of CO2, which from the physical perspective of the climate system means that it will also lead to a higher committed warming and thus a higher risk of climate change impacts."
 "Compared to the relatively simple message that the carbon budget for 1.5 degrees will be exhausted within ten to 14 years, the reason to have all these different pathways is that the world is not a simple place. The world isn't following or hasn't been following these idealized pathways, and by having these scenarios, we actually can inform policy makers about potential options, risks, synergies, and trade-offs for more realistic evolutions that take into account the potential evolution of technological innovation, of policy preferences related to issues of equality across the world, different policies for agriculture and forestry, etc. So the scenarios are showing these options in a more realistic, or comprehensive, way than a simple model of the economy and climate can do. And one of the key advantages is really to look at the sensitivity of certain assumptions, so for instance, if we assume a scenario where everyone has a more sustainable diet with less meat, we can then look at how
much easier or harder it would then be to limit warming to 1.5 degrees Celsius."
 "I think one conclusion from the IPCC report is that no single measure, no single actor, can make 1.5 degrees happen. It really is a level of ambition that would require all actors and all sectors to contribute fully to the challenge. At the same time, I think when individuals are thinking about what they can do, there are few aspects that can be highlighted. First of all, I think in many places, and for many individuals, the carbon footprint, so to say, of an individual is driven by a couple
of factors. In high income and high consumption settings, that's very often mobility, how we move around; that's related to our diets; and also obviously our housing, and how we heat our homes or cool them in hot environments. And with all these kind of changes, we know that by shifting to more sustainable options for these activities, you can make a very large or a very distinctive change in your individual carbon footprint."
 "So in the report, we clearly highlight that, as shown by that 42% by 2030 reduction, there's a very clear need for further strengthening of climate policies across the world. And this in a context where climate action is a global public good, which means that when an individual actor incurs the cost of its action, the entire global community benefits. And this means that there's a question of how these costs of mitigation are distributed across the world, and there's a question of equity that's involved. But at the same time, there's also a very clear understanding that there's a lot of benefits from these changes, both in the kind of mitigation benefits or climate change avoidance benefits, but there are also these non-climate benefits related to sustainable development aspects. But from a scientific perspective, the literature very clearly shows that the more comprehensive and deeper the changes that we can achieve in the short term, the easier it would be to avoid these overshoots and to a lot of the climate
damages that come along with these overshoots."
