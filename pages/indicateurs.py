import streamlit as st
import pandas as pd
from utils.helpers import (
    calculate_indicator_points,
    format_currency,
    get_parameter_value,
    set_parameter_value
)
from models import Indicateur
from utils import get_session

def show():
    """Affiche la page de gestion des indicateurs."""
    st.title("Gestion des indicateurs ACI")
    
    # Récupérer les paramètres nécessaires
    valeur_point = float(get_parameter_value("valeur_point") or 7)
    patientele = int(get_parameter_value("patientele") or 4000)
    nombre_ps = int(get_parameter_value("nombre_ps") or 10)
    taux_dossiers = float(get_parameter_value("taux_dossiers") or 5)
    
    # Formulaire pour mettre à jour les paramètres
    with st.expander("Paramètres de calcul", expanded=False):
        st.subheader("Paramètres de calcul")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            new_patientele = st.number_input(
                "Patientèle",
                min_value=0,
                value=patientele,
                step=100,
                help="Nombre de patients de la structure"
            )
        
        with col2:
            new_nombre_ps = st.number_input(
                "Nombre de PS",
                min_value=1,
                value=nombre_ps,
                step=1,
                help="Nombre de professionnels de santé"
            )
        
        with col3:
            new_taux_dossiers = st.number_input(
                "Taux de dossiers (%)",
                min_value=0.0,
                max_value=100.0,
                value=taux_dossiers,
                step=0.5,
                help="Pourcentage de dossiers pour la concertation pluri-professionnelle"
            )
        
        with col4:
            new_valeur_point = st.number_input(
                "Valeur du point (€)",
                min_value=0.0,
                value=valeur_point,
                step=0.1,
                help="Valeur d'un point en euros"
            )
        
        if st.button("Mettre à jour les paramètres"):
            set_parameter_value("patientele", str(new_patientele))
            set_parameter_value("nombre_ps", str(new_nombre_ps))
            set_parameter_value("taux_dossiers", str(new_taux_dossiers))
            set_parameter_value("valeur_point", str(new_valeur_point))
            st.success("Paramètres mis à jour avec succès !")
            st.experimental_rerun()
    
    # Créer des onglets pour chaque axe
    tabs = st.tabs([
        "Accès aux soins", 
        "Travail en équipe & coordination", 
        "Système d'information"
    ])
    
    # Récupérer tous les indicateurs
    session = get_session()
    indicateurs = session.query(Indicateur).all()
    session.close()
    
    # Grouper les indicateurs par axe
    indicateurs_par_axe = {
        "Accès aux soins": [],
        "Travail en équipe & coordination": [],
        "Système d'information": []
    }
    
    for indicateur in indicateurs:
        if indicateur.axe in indicateurs_par_axe:
            indicateurs_par_axe[indicateur.axe].append(indicateur)
    
    # Fonction pour afficher un indicateur
    def afficher_indicateur(indicateur, tab_index):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                est_valide = st.checkbox(
                    f"{indicateur.nom}",
                    value=indicateur.est_valide,
                    key=f"check_{indicateur.id}"
                )
                
                if est_valide != indicateur.est_valide:
                    session = get_session()
                    indic = session.query(Indicateur).filter_by(id=indicateur.id).first()
                    indic.est_valide = est_valide
                    session.commit()
                    session.close()
                    st.experimental_rerun()
            
            with col2:
                points_fixes = indicateur.points_fixes
                st.write(f"**Points fixes**: {points_fixes}")
            
            with col3:
                points_variables = indicateur.points_variables
                st.write(f"**Points variables**: {points_variables}")
            
            with col4:
                # Calculer les points totaux pour cet indicateur
                points_totaux = calculate_indicator_points(
                    indicateur.id,
                    patientele=patientele,
                    nombre_ps=nombre_ps,
                    taux_dossiers=taux_dossiers/100  # Convertir en pourcentage
                )
                
                montant = points_totaux * valeur_point if indicateur.est_valide else 0
                st.write(f"**Montant**: {format_currency(montant)}")
            
            # Afficher la formule de calcul si elle existe
            if indicateur.formule_calcul:
                st.caption(f"Formule: {indicateur.formule_calcul}")
            
            # Ajouter un séparateur
            st.markdown("---")
    
    # Afficher les indicateurs dans chaque onglet
    for i, axe in enumerate(["Accès aux soins", "Travail en équipe & coordination", "Système d'information"]):
        with tabs[i]:
            # Séparer les indicateurs socle/prérequis des indicateurs optionnels
            indicateurs_socle = [ind for ind in indicateurs_par_axe[axe] if ind.type in ["socle", "prérequis"]]
            indicateurs_optionnels = [ind for ind in indicateurs_par_axe[axe] if ind.type == "optionnel"]
            
            # Afficher les indicateurs socle/prérequis
            if indicateurs_socle:
                st.subheader("Indicateurs socle / prérequis")
                for indicateur in indicateurs_socle:
                    afficher_indicateur(indicateur, i)
            
            # Afficher les indicateurs optionnels
            if indicateurs_optionnels:
                st.subheader("Indicateurs optionnels")
                for indicateur in indicateurs_optionnels:
                    afficher_indicateur(indicateur, i)
    
    # Afficher un résumé des points
    st.subheader("Résumé des points validés")
    
    # Calculer les points totaux par axe
    points_par_axe = {}
    for axe in indicateurs_par_axe:
        points_par_axe[axe] = {
            "total": 0,
            "valide": 0
        }
        
        for indicateur in indicateurs_par_axe[axe]:
            points = calculate_indicator_points(
                indicateur.id,
                patientele=patientele,
                nombre_ps=nombre_ps,
                taux_dossiers=taux_dossiers/100
            )
            
            if indicateur.est_valide:
                points_par_axe[axe]["valide"] += points
            
            points_par_axe[axe]["total"] += (indicateur.points_fixes + indicateur.points_variables) * indicateur.prorata
    
    # Créer un DataFrame pour afficher les données
    df_resume = pd.DataFrame({
        "Axe": list(points_par_axe.keys()),
        "Points validés": [axe["valide"] for axe in points_par_axe.values()],
        "Points potentiels": [axe["total"] for axe in points_par_axe.values()],
        "Taux de validation": [
            f"{axe['valide'] / axe['total'] * 100:.1f}%" if axe['total'] > 0 else "0%" 
            for axe in points_par_axe.values()
        ],
        "Montant (€)": [
            format_currency(axe["valide"] * valeur_point) 
            for axe in points_par_axe.values()
        ]
    })
    
    # Ajouter une ligne de total
    total_row = pd.DataFrame({
        "Axe": ["Total"],
        "Points validés": [sum(axe["valide"] for axe in points_par_axe.values())],
        "Points potentiels": [sum(axe["total"] for axe in points_par_axe.values())],
        "Taux de validation": [
            f"{sum(axe['valide'] for axe in points_par_axe.values()) / sum(axe['total'] for axe in points_par_axe.values()) * 100:.1f}%" 
            if sum(axe['total'] for axe in points_par_axe.values()) > 0 else "0%"
        ],
        "Montant (€)": [
            format_currency(sum(axe["valide"] for axe in points_par_axe.values()) * valeur_point)
        ]
    })
    
    df_resume = pd.concat([df_resume, total_row], ignore_index=True)
    
    # Afficher le tableau
    st.dataframe(df_resume, use_container_width=True)
    
    # Ajouter une note explicative
    st.info("""
    **Note**: Cochez les indicateurs validés pour calculer les points correspondants.
    Les points variables sont calculés en fonction des paramètres définis (patientèle, nombre de PS, etc.).
    """)
