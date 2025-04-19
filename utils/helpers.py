import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from models import Indicateur, Associe, Repartition, Attribution, Charge, Parametre, Patientele, ProfessionnelSante
from utils import get_session
import base64
import os

def load_css():
    """Charge le CSS personnalisé."""
    css_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'css', 'style.css')
    with open(css_file, 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_parameter_value(key):
    """Récupère la valeur d'un paramètre depuis la base de données."""
    session = get_session()
    param = session.query(Parametre).filter_by(cle=key).first()
    session.close()
    
    if param:
        return param.valeur
    return None

def set_parameter_value(key, value, description=None):
    """Définit la valeur d'un paramètre dans la base de données."""
    session = get_session()
    param = session.query(Parametre).filter_by(cle=key).first()
    
    if param:
        param.valeur = value
        if description:
            param.description = description
    else:
        param = Parametre(cle=key, valeur=value, description=description)
        session.add(param)
    
    session.commit()
    session.close()

def calculate_indicator_points(indicateur_id, patientele=None, nombre_ps=None, taux_dossiers=None, nb_protocoles=None):
    """Calcule les points pour un indicateur donné en fonction des paramètres."""
    session = get_session()
    indicateur = session.query(Indicateur).filter_by(id=indicateur_id).first()
    session.close()
    
    if not indicateur:
        return 0
    
    # Points fixes toujours attribués si l'indicateur est validé
    points_fixes = indicateur.points_fixes if indicateur.est_valide else 0
    points_variables = 0
    
    # Calcul des points variables selon la formule de l'indicateur
    if indicateur.est_valide and indicateur.points_variables > 0:
        if "Fonction de coordination - Variable (jusqu'à 8000 patients)" in indicateur.nom:
            points_variables = 1700 * min(patientele or 0, 8000) / 4000
        
        elif "Fonction de coordination - Variable (au-delà de 8000 patients)" in indicateur.nom:
            points_variables = 1100 * max((patientele or 0) - 8000, 0) / 4000
        
        elif "Concertation pluri-professionnelle" in indicateur.nom:
            base_points = 1000
            if "avec IPA" in indicateur.nom:
                points_fixes = 200  # Points fixes supplémentaires pour IPA
            
            if patientele and taux_dossiers:
                points_variables = base_points * (patientele / 4000) * (taux_dossiers / 5)
        
        elif "SI labellisé 'Standard' (ANS) - Variable (jusqu'à 16 PS)" in indicateur.nom:
            points_variables = 200 * min(nombre_ps or 0, 16)
        
        elif "SI labellisé 'Standard' (ANS) - Variable (au-delà de 16 PS)" in indicateur.nom:
            points_variables = 150 * max((nombre_ps or 0) - 16, 0)
        
        elif "Coordination externe" in indicateur.nom or "Parcours insuffisance cardiaque" in indicateur.nom:
            points_variables = indicateur.points_variables * ((patientele or 0) / 4000)
        
        elif "Protocoles pluri-professionnels" in indicateur.nom or "Protocoles nationaux de coopération" in indicateur.nom:
            # Pour les protocoles, on multiplie par le nombre de protocoles (max 8 ou 6)
            max_protocoles = 8 if "pluri-professionnels" in indicateur.nom else 6
            points_fixes = indicateur.points_fixes * min(nb_protocoles or 0, max_protocoles)
            points_variables = 0  # Pas de points variables pour les protocoles
        
        elif "Formation de professionnels - 3e & 4e stage" in indicateur.nom:
            # Pour les stages supplémentaires (max 2)
            points_fixes = indicateur.points_fixes * min(nb_protocoles or 0, 2)
            points_variables = 0
        
        elif "Réponse aux crises sanitaires graves - Activation" in indicateur.nom:
            # 350 points si crise, 0 sinon (déjà géré par est_valide)
            points_variables = indicateur.points_variables
        
        elif "Missions de santé publique" in indicateur.nom or "Implication des usagers - Niveau 2" in indicateur.nom or "Démarche qualité" in indicateur.nom:
            # Points variables fixes pour ces indicateurs
            points_variables = indicateur.points_variables
    
    # Appliquer le prorata si défini
    total_points = (points_fixes + points_variables) * indicateur.prorata
    
    return total_points

def get_total_points_by_axe():
    """Récupère le total des points par axe."""
    session = get_session()
    indicateurs = session.query(Indicateur).all()
    session.close()
    
    # Récupérer les paramètres nécessaires pour le calcul
    patientele = int(get_parameter_value("patientele") or 4000)
    nombre_ps = int(get_parameter_value("nombre_ps") or 10)
    taux_dossiers = float(get_parameter_value("taux_dossiers") or 5) / 100  # Convertir en pourcentage
    
    # Calculer les points par axe
    axes = {}
    for indicateur in indicateurs:
        if indicateur.axe not in axes:
            axes[indicateur.axe] = {"total": 0, "valide": 0}
        
        # Calculer les points pour cet indicateur
        points = calculate_indicator_points(
            indicateur.id, 
            patientele=patientele, 
            nombre_ps=nombre_ps, 
            taux_dossiers=taux_dossiers
        )
        
        if indicateur.est_valide:
            axes[indicateur.axe]["valide"] += points
        
        # Ajouter au total potentiel (que l'indicateur soit validé ou non)
        axes[indicateur.axe]["total"] += (indicateur.points_fixes + indicateur.points_variables) * indicateur.prorata
    
    return axes

def create_pie_chart(data, title):
    """Crée un graphique en camembert avec Plotly."""
    labels = list(data.keys())
    values = [data[key]["valide"] for key in labels]
    
    fig = px.pie(
        names=labels,
        values=values,
        title=title,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.4
    )
    
    fig.update_layout(
        font=dict(family="Lato, sans-serif"),
        title_font=dict(size=20, color="#0596DE"),
        legend_title_font=dict(size=14),
        legend_font=dict(size=12),
    )
    
    return fig

def create_bar_chart(data, title):
    """Crée un graphique en barres avec Plotly."""
    labels = list(data.keys())
    valide = [data[key]["valide"] for key in labels]
    total = [data[key]["total"] for key in labels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels,
        y=valide,
        name='Points validés',
        marker_color='#0596DE'
    ))
    
    fig.add_trace(go.Bar(
        x=labels,
        y=[t-v for t, v in zip(total, valide)],
        name='Points non validés',
        marker_color='#E9ECEF'
    ))
    
    fig.update_layout(
        title=title,
        barmode='stack',
        font=dict(family="Lato, sans-serif"),
        title_font=dict(size=20, color="#0596DE"),
        legend_title_font=dict(size=14),
        legend_font=dict(size=12),
        xaxis=dict(title='Axe'),
        yaxis=dict(title='Points')
    )
    
    return fig

def get_logo_base64():
    """Retourne le logo en base64 pour l'affichage dans Streamlit."""
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
    
    # Si le logo n'existe pas, retourner None
    if not os.path.exists(logo_path):
        return None
    
    with open(logo_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    return encoded_string

def display_logo():
    """Affiche le logo dans l'application Streamlit."""
    logo_base64 = get_logo_base64()
    
    if logo_base64:
        st.markdown(
            f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" width="200">',
            unsafe_allow_html=True
        )
    else:
        # Afficher un titre stylisé si pas de logo
        st.markdown(
            '<h1 style="color:#0596DE; font-family:Lato, sans-serif;">ACI Manager</h1>',
            unsafe_allow_html=True
        )

def format_currency(amount):
    """Formate un montant en euros."""
    return f"{amount:,.2f} €".replace(",", " ").replace(".", ",")

def calculate_total_aci_revenue():
    """Calcule le revenu total ACI en euros."""
    session = get_session()
    indicateurs = session.query(Indicateur).all()
    session.close()
    
    # Récupérer les paramètres nécessaires pour le calcul
    patientele = int(get_parameter_value("patientele") or 4000)
    nombre_ps = int(get_parameter_value("nombre_ps") or 10)
    taux_dossiers = float(get_parameter_value("taux_dossiers") or 5) / 100
    valeur_point = float(get_parameter_value("valeur_point") or 7)
    
    # Calculer les points totaux
    total_points = 0
    for indicateur in indicateurs:
        if indicateur.est_valide:
            points = calculate_indicator_points(
                indicateur.id, 
                patientele=patientele, 
                nombre_ps=nombre_ps, 
                taux_dossiers=taux_dossiers
            )
            total_points += points
    
    # Convertir en euros
    total_euros = total_points * valeur_point
    
    return total_euros

def calculate_charges_total():
    """Calcule le total des charges."""
    session = get_session()
    charges = session.query(Charge).all()
    session.close()
    
    total_charges = sum(charge.montant for charge in charges)
    return total_charges

def calculate_net_revenue():
    """Calcule le revenu net après déduction des charges."""
    total_aci = calculate_total_aci_revenue()
    total_charges = calculate_charges_total()
    
    return total_aci - total_charges

def get_associes_repartition():
    """Récupère la répartition des revenus entre associés."""
    session = get_session()
    associes = session.query(Associe).all()
    attributions = session.query(Attribution).all()
    indicateurs = {i.id: i for i in session.query(Indicateur).all()}
    session.close()
    
    # Calculer le revenu total ACI
    total_aci = calculate_total_aci_revenue()
    total_charges = calculate_charges_total()
    net_revenue = total_aci - total_charges
    
    # Initialiser les résultats
    resultats = {}
    for associe in associes:
        resultats[associe.id] = {
            "nom": f"{associe.prenom} {associe.nom}",
            "fonction": associe.fonction,
            "est_gerant": associe.est_gerant,
            "coefficient": associe.coefficient_majoration,
            "part_fixe": 0,
            "part_variable": 0,
            "total": 0
        }
    
    # Calculer la part de chaque associé
    for attribution in attributions:
        if attribution.indicateur_id in indicateurs and indicateurs[attribution.indicateur_id].est_valide:
            indicateur = indicateurs[attribution.indicateur_id]
            
            # Récupérer la répartition de cet indicateur
            session = get_session()
            repartition = session.query(Repartition).filter_by(indicateur_id=indicateur.id).first()
            session.close()
            
            # Calculer la valeur de cet indicateur
            patientele = int(get_parameter_value("patientele") or 4000)
            nombre_ps = int(get_parameter_value("nombre_ps") or 10)
            taux_dossiers = float(get_parameter_value("taux_dossiers") or 5) / 100
            valeur_point = float(get_parameter_value("valeur_point") or 7)
            
            points = calculate_indicator_points(
                indicateur.id, 
                patientele=patientele, 
                nombre_ps=nombre_ps, 
                taux_dossiers=taux_dossiers
            )
            
            valeur_euros = points * valeur_point
            
            # Répartir selon le mode de répartition
            if repartition and repartition.est_commun:
                # Répartition commune entre tous les associés
                if repartition.mode_repartition == 'egalitaire':
                    part_associe = valeur_euros / len(associes)
                    if indicateur.type == 'socle' or indicateur.type == 'prérequis':
                        resultats[attribution.associe_id]["part_fixe"] += part_associe
                    else:
                        resultats[attribution.associe_id]["part_variable"] += part_associe
                
                elif repartition.mode_repartition == 'proportionnel':
                    # Répartition proportionnelle au coefficient de majoration
                    total_coefficients = sum(a.coefficient_majoration for a in associes)
                    part_associe = valeur_euros * (resultats[attribution.associe_id]["coefficient"] / total_coefficients)
                    
                    if indicateur.type == 'socle' or indicateur.type == 'prérequis':
                        resultats[attribution.associe_id]["part_fixe"] += part_associe
                    else:
                        resultats[attribution.associe_id]["part_variable"] += part_associe
            
            else:
                # Répartition personnalisée selon les pourcentages d'attribution
                part_associe = valeur_euros * (attribution.pourcentage / 100)
                
                if indicateur.type == 'socle' or indicateur.type == 'prérequis':
                    resultats[attribution.associe_id]["part_fixe"] += part_associe
                else:
                    resultats[attribution.associe_id]["part_variable"] += part_associe
    
    # Calculer les totaux
    for associe_id in resultats:
        resultats[associe_id]["total"] = resultats[associe_id]["part_fixe"] + resultats[associe_id]["part_variable"]
    
    return resultats
