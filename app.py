import streamlit as st
import os
import sys
from utils import init_db, initialize_all_data
from utils.helpers import load_css, display_logo
from pages import dashboard, indicateurs, associes, repartition, charges, parametres

# Configuration de la page
st.set_page_config(
    page_title="ACI Manager",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chargement du CSS personnalisé
load_css()

# Initialisation de la base de données si elle n'existe pas
db_path = os.path.join(os.path.dirname(__file__), 'data', 'aci_app.db')
if not os.path.exists(db_path):
    initialize_all_data()

# Affichage du logo ou du titre
display_logo()

# Barre latérale pour la navigation
st.sidebar.title("Navigation")

# Options de navigation
pages = {
    "Tableau de bord": dashboard,
    "Gestion des indicateurs": indicateurs,
    "Gestion des associés": associes,
    "Répartition des revenus": repartition,
    "Gestion des charges": charges,
    "Paramètres": parametres
}

# Sélection de la page
selection = st.sidebar.radio("Aller à", list(pages.keys()))

# Affichage de la page sélectionnée
pages[selection].show()

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info(
    "ACI Manager - Application de gestion des revenus ACI et leur répartition entre associés."
)
