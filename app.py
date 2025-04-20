import streamlit as st
import os
import sys
from utils import init_db, initialize_all_data
from utils.helpers import load_css, display_logo
from pages import dashboard, indicateurs, associes, repartition, charges, parametres

# Configuration de la page - désactiver la barre latérale vide par défaut
st.set_page_config(
    page_title="ACI Manager",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Masquer la barre latérale avec les fichiers Python
st.markdown("""
<style>
    /* Masquage de la barre du navigateur de fichiers */
    section.main-file-navigation,
    div[data-testid="stFileNavigationToggle"],
    div[data-testid="stFileBrowser"],
    div.css-1ay57l1,
    div.st-emotion-cache-1ay57l1,
    div.st-emotion-cache-1cypcdb,
    div.css-1544g2n,
    div.st-emotion-cache-1544g2n {
        display: none !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Forcer le thème clair
st.markdown("""
    <style>
    :root {
        --background-color: #FFFFFF;
        --secondary-background-color: #f9fafb;
        --primary-color: #006deb;
        --text-color: #2d3e50;
    }
    </style>
""", unsafe_allow_html=True)

# Style Doctolib pour l'en-tête et la navigation
st.markdown("""
    <style>
    /* En-tête de style Doctolib */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #edf0f2;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    
    .sidebar-header {
        background-color: #006deb;
        color: white;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-header h1 {
        color: white !important;
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        letter-spacing: -0.2px;
    }
    
    .sidebar-nav {
        padding: 0 1rem;
    }
    
    .sidebar-separator {
        height: 1px;
        background-color: #edf0f2;
        margin: 1.5rem 0;
    }
    
    /* Doctolib notification badge */
    .badge-notification {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 18px;
        height: 18px;
        padding: 0 6px;
        font-size: 12px;
        font-weight: 600;
        line-height: 1;
        color: white;
        background-color: #ff4050;
        border-radius: 12px;
        margin-left: 8px;
    }
    
    /* Hover effects */
    .stRadio > div > div > label:hover {
        background-color: rgba(0, 109, 235, 0.05);
        border-radius: 8px;
    }
    
    /* Éliminer les espaces vides dans la barre latérale */
    [data-testid="stSidebar"] .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Amélioration des éléments radio */
    .stRadio > div {
        gap: 0 !important;
    }
    
    .stRadio > div > div > label {
        padding: 0.5rem 0.75rem !important;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > div > label[data-baseweb="radio"] > div:first-child {
        margin-right: 12px !important;
    }
    
    .stRadio > div > div > label > div:last-child {
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Désactiver les éléments d'interface Streamlit par défaut avec CSS
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none !important;}
    section[data-testid="stSidebar"] > div {z-index: 1;}
    
    /* Masquer complètement la barre de navigation de pages */
    [data-testid="stAppViewBlockContainer"] > div:first-child {display: none !important;}
    .st-emotion-cache-uf99v8 {display: none !important;}
    .st-emotion-cache-16txtl3 {display: none !important;}
    .st-emotion-cache-z5fcl4 {display: none !important;}
    
    /* Classes alternatives qui peuvent être utilisées */
    nav {display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    
    /* Masquer la barre latérale avec les fichiers du projet */
    .main-file-navigation {display: none !important;}
    .css-1544g2n {display: none !important;}
    .st-emotion-cache-1544g2n {display: none !important;}
    [data-testid="stFileBrowser"] {display: none !important;}
    .st-emotion-cache-1cypcdb {display: none !important;}
    .st-emotion-cache-1ay57l1 {display: none !important;}
    
    /* Élimine tout espace à gauche */
    .main .block-container {padding-left: 2rem !important;}
    
    /* Force le mode clair */
    .stApp {
        background-color: white;
    }
    .css-6qob1r {
        background-color: white;
    }
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Chargement du CSS personnalisé
load_css()

# Initialisation de la base de données si elle n'existe pas
db_path = os.path.join(os.path.dirname(__file__), 'data', 'aci_app.db')
if not os.path.exists(db_path):
    initialize_all_data()

# En-tête de navigation personnalisé style Doctolib
st.sidebar.markdown('<div class="sidebar-header"><h1>ACI Manager</h1></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)

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
selection = st.sidebar.radio("", list(pages.keys()), label_visibility="collapsed")

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Affichage de la page sélectionnée
pages[selection].show()

# Pied de page
st.sidebar.markdown('<div class="sidebar-separator"></div>', unsafe_allow_html=True)
st.sidebar.info(
    "ACI Manager - Application de gestion des revenus ACI et leur répartition entre associés."
)
