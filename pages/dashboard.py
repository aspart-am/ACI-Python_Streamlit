import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import (
    get_total_points_by_axe, 
    create_pie_chart, 
    create_bar_chart, 
    calculate_total_aci_revenue, 
    calculate_charges_total, 
    calculate_net_revenue,
    format_currency,
    get_parameter_value
)

def show():
    """Affiche le tableau de bord principal."""
    st.title("Tableau de bord")
    
    # Récupérer les données des points par axe
    axes_data = get_total_points_by_axe()
    
    # Récupérer les paramètres
    valeur_point = float(get_parameter_value("valeur_point") or 7)
    patientele = int(get_parameter_value("patientele") or 4000)
    nombre_ps = int(get_parameter_value("nombre_ps") or 10)
    
    # Calculer les revenus
    total_aci = calculate_total_aci_revenue()
    total_charges = calculate_charges_total()
    net_revenue = calculate_net_revenue()
    
    # Afficher les métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Revenu ACI Total", 
            value=format_currency(total_aci)
        )
    
    with col2:
        st.metric(
            label="Total des Charges", 
            value=format_currency(total_charges)
        )
    
    with col3:
        st.metric(
            label="Revenu Net", 
            value=format_currency(net_revenue)
        )
    
    with col4:
        # Calculer le total des points validés
        total_points_valides = sum(axe["valide"] for axe in axes_data.values())
        st.metric(
            label="Points Validés", 
            value=f"{int(total_points_valides)} pts"
        )
    
    # Afficher les informations sur la structure
    st.subheader("Informations sur la structure")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.info(f"**Patientèle**: {patientele} patients")
    
    with info_col2:
        st.info(f"**Professionnels de santé**: {nombre_ps} PS")
    
    with info_col3:
        st.info(f"**Valeur du point**: {valeur_point} €")
    
    # Créer les graphiques
    st.subheader("Répartition des points par axe")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Graphique en camembert
        pie_chart = create_pie_chart(
            axes_data, 
            "Répartition des points validés par axe"
        )
        st.plotly_chart(pie_chart, use_container_width=True)
    
    with chart_col2:
        # Graphique en barres
        bar_chart = create_bar_chart(
            axes_data, 
            "Points validés vs. Points potentiels par axe"
        )
        st.plotly_chart(bar_chart, use_container_width=True)
    
    # Tableau récapitulatif des points par axe
    st.subheader("Détail des points par axe")
    
    # Créer un DataFrame pour afficher les données
    df_axes = pd.DataFrame({
        "Axe": list(axes_data.keys()),
        "Points validés": [axe["valide"] for axe in axes_data.values()],
        "Points potentiels": [axe["total"] for axe in axes_data.values()],
        "Taux de validation": [
            f"{axe['valide'] / axe['total'] * 100:.1f}%" if axe['total'] > 0 else "0%" 
            for axe in axes_data.values()
        ],
        "Montant (€)": [
            format_currency(axe["valide"] * valeur_point) 
            for axe in axes_data.values()
        ]
    })
    
    # Ajouter une ligne de total
    total_row = pd.DataFrame({
        "Axe": ["Total"],
        "Points validés": [sum(axe["valide"] for axe in axes_data.values())],
        "Points potentiels": [sum(axe["total"] for axe in axes_data.values())],
        "Taux de validation": [
            f"{sum(axe['valide'] for axe in axes_data.values()) / sum(axe['total'] for axe in axes_data.values()) * 100:.1f}%" 
            if sum(axe['total'] for axe in axes_data.values()) > 0 else "0%"
        ],
        "Montant (€)": [
            format_currency(sum(axe["valide"] for axe in axes_data.values()) * valeur_point)
        ]
    })
    
    df_axes = pd.concat([df_axes, total_row], ignore_index=True)
    
    # Afficher le tableau
    st.dataframe(df_axes, use_container_width=True)
    
    # Ajouter une note explicative
    st.markdown("""
    **Note**: Ce tableau de bord présente une vue d'ensemble des revenus ACI de la structure.
    Pour plus de détails sur chaque indicateur, veuillez consulter la page "Gestion des indicateurs".
    """)
