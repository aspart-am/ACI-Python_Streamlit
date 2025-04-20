import streamlit as st
import pandas as pd
import re
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
            st.rerun()
    
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
    
    # Fonction pour regrouper les indicateurs similaires
    def grouper_indicateurs(indicateurs):
        groupes = {}
        for indicateur in indicateurs:
            # Extraire le nom de base (sans le niveau/seuil/variante)
            nom_base = re.sub(r' - Niveau \d+| \(\d+% médecins\)| \(avec IPA\)| \(sans IPA\)| - Variable.*| - Fixe.*| - Activation.*| - Plan.*', '', indicateur.nom)
            
            # Regrouper par nom de base
            if nom_base not in groupes:
                groupes[nom_base] = []
            groupes[nom_base].append(indicateur)
        
        return groupes
    
    # Fonction pour afficher un indicateur simple
    def afficher_indicateur_simple(indicateur, tab_index):
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
                    st.rerun()
            
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
    
    # Fonction pour afficher un groupe d'indicateurs
    def afficher_groupe_indicateurs(nom_groupe, indicateurs_groupe, tab_index):
        with st.container():
            st.subheader(nom_groupe)
            
            # Créer des options pour le menu déroulant
            options = ["Non validé"]
            id_map = {0: None}  # Pour mapper l'option sélectionnée à l'ID de l'indicateur
            
            for i, ind in enumerate(indicateurs_groupe):
                # Extraire le niveau/variante pour l'affichage
                if " - Niveau " in ind.nom:
                    niveau = ind.nom.split(" - Niveau ")[1]
                    options.append(f"Niveau {niveau}")
                elif " - Variable " in ind.nom:
                    variante = ind.nom.split(" - Variable ")[1]
                    options.append(f"Variable: {variante}")
                elif " - Fixe" in ind.nom:
                    options.append("Fixe")
                elif "(avec IPA)" in ind.nom:
                    options.append("Avec IPA")
                elif "(sans IPA)" in ind.nom:
                    options.append("Sans IPA")
                elif " médecins)" in ind.nom:
                    pourcentage = ind.nom.split("(")[1].split(" médecins")[0]
                    options.append(f"{pourcentage}")
                elif " - Plan" in ind.nom:
                    options.append("Plan")
                elif " - Activation" in ind.nom:
                    options.append("Activation")
                else:
                    options.append(ind.nom)
                
                id_map[i+1] = ind.id
            
            # Déterminer l'option sélectionnée par défaut
            option_defaut = 0
            for i, ind in enumerate(indicateurs_groupe):
                if ind.est_valide:
                    option_defaut = i+1
                    break
            
            # Afficher le menu déroulant ou les cases à cocher
            if len(indicateurs_groupe) <= 3 and all(ind.type == "socle" for ind in indicateurs_groupe):
                # Utiliser des cases à cocher pour les indicateurs socle qui vont ensemble
                selected_ids = []
                for ind in indicateurs_groupe:
                    if " - Variable " in ind.nom:
                        variante = ind.nom.split(" - Variable ")[1]
                        label = f"Variable: {variante}"
                    elif " - Fixe" in ind.nom:
                        label = "Fixe"
                    elif "(avec IPA)" in ind.nom:
                        label = "Avec IPA"
                    elif "(sans IPA)" in ind.nom:
                        label = "Sans IPA"
                    elif " - Plan" in ind.nom:
                        label = "Plan"
                    elif " - Activation" in ind.nom:
                        label = "Activation"
                    else:
                        label = ind.nom
                    
                    est_valide = st.checkbox(
                        label,
                        value=ind.est_valide,
                        key=f"check_{ind.id}"
                    )
                    
                    if est_valide != ind.est_valide:
                        session = get_session()
                        indic = session.query(Indicateur).filter_by(id=ind.id).first()
                        indic.est_valide = est_valide
                        session.commit()
                        session.close()
                        selected_ids.append(ind.id)
                
                if selected_ids:
                    st.rerun()
            else:
                # Utiliser un menu déroulant pour les indicateurs s'excluant mutuellement
                selected_option = st.selectbox(
                    "Niveau validé",
                    options=options,
                    index=option_defaut,
                    key=f"select_{nom_groupe}"
                )
                
                # Mettre à jour la base de données
                selected_id = id_map[options.index(selected_option)]
                
                if selected_id:
                    # Vérifier si le statut a changé
                    changed = False
                    session = get_session()
                    
                    for ind in indicateurs_groupe:
                        indic = session.query(Indicateur).filter_by(id=ind.id).first()
                        if ind.id == selected_id and not indic.est_valide:
                            indic.est_valide = True
                            changed = True
                        elif ind.id != selected_id and indic.est_valide:
                            indic.est_valide = False
                            changed = True
                    
                    if changed:
                        session.commit()
                        st.rerun()
                    
                    session.close()
            
            # Afficher les détails des indicateurs validés
            for ind in indicateurs_groupe:
                if ind.est_valide:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        points_fixes = ind.points_fixes
                        points_variables = ind.points_variables
                        st.write(f"**Points**: {points_fixes} fixes + {points_variables} variables")
                    
                    with col2:
                        # Calculer les points totaux
                        points_totaux = calculate_indicator_points(
                            ind.id,
                            patientele=patientele,
                            nombre_ps=nombre_ps,
                            taux_dossiers=taux_dossiers/100
                        )
                        st.write(f"**Total points**: {points_totaux:.1f}")
                    
                    with col3:
                        montant = points_totaux * valeur_point
                        st.write(f"**Montant**: {format_currency(montant)}")
                    
                    # Afficher la formule de calcul si elle existe
                    if ind.formule_calcul:
                        st.caption(f"Formule: {ind.formule_calcul}")
            
            # Ajouter un séparateur
            st.markdown("---")
    
    # Afficher les indicateurs dans chaque onglet
    for i, axe in enumerate(["Accès aux soins", "Travail en équipe & coordination", "Système d'information"]):
        with tabs[i]:
            # Séparer les indicateurs socle/prérequis des indicateurs optionnels
            indicateurs_socle = [ind for ind in indicateurs_par_axe[axe] if ind.type in ["socle", "prérequis"]]
            indicateurs_optionnels = [ind for ind in indicateurs_par_axe[axe] if ind.type == "optionnel"]
            
            # Grouper les indicateurs
            groupes_socle = grouper_indicateurs(indicateurs_socle)
            groupes_optionnels = grouper_indicateurs(indicateurs_optionnels)
            
            # Afficher les indicateurs socle/prérequis
            if indicateurs_socle:
                st.subheader("Indicateurs socle / prérequis")
                for nom_groupe, indicateurs_groupe in groupes_socle.items():
                    if len(indicateurs_groupe) > 1:
                        # Groupe d'indicateurs similaires
                        afficher_groupe_indicateurs(nom_groupe, indicateurs_groupe, i)
                    else:
                        # Indicateur unique
                        afficher_indicateur_simple(indicateurs_groupe[0], i)
            
            # Afficher les indicateurs optionnels
            if indicateurs_optionnels:
                st.subheader("Indicateurs optionnels")
                for nom_groupe, indicateurs_groupe in groupes_optionnels.items():
                    if len(indicateurs_groupe) > 1:
                        # Groupe d'indicateurs similaires
                        afficher_groupe_indicateurs(nom_groupe, indicateurs_groupe, i)
                    else:
                        # Indicateur unique
                        afficher_indicateur_simple(indicateurs_groupe[0], i)
    
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
    **Note**: Sélectionnez le niveau validé pour chaque indicateur dans les menus déroulants.
    Les points variables sont calculés en fonction des paramètres définis (patientèle, nombre de PS, etc.).
    """)
