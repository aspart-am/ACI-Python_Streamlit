import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import (
    format_currency,
    calculate_total_aci_revenue,
    calculate_charges_total,
    calculate_net_revenue,
    get_associes_repartition
)
from models import Indicateur, Associe, Repartition, Attribution
from utils import get_session

def show():
    """Affiche la page de répartition des revenus entre associés."""
    st.title("Répartition des revenus ACI")
    
    # Récupérer les données
    session = get_session()
    indicateurs = session.query(Indicateur).all()
    associes = session.query(Associe).all()
    session.close()
    
    if not associes:
        st.warning("Aucun associé n'a été ajouté. Veuillez d'abord ajouter des associés dans la page 'Gestion des associés'.")
        return
    
    # Afficher les métriques principales
    total_aci = calculate_total_aci_revenue()
    total_charges = calculate_charges_total()
    net_revenue = calculate_net_revenue()
    
    col1, col2, col3 = st.columns(3)
    
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
            label="Revenu Net à Répartir", 
            value=format_currency(net_revenue)
        )
    
    # Paramètre de pondération pour les gérants
    st.subheader("Pondération pour les gérants")
    ponderation_gerants = st.slider(
        "Coefficient de pondération pour les gérants",
        min_value=1.0,
        max_value=3.0,
        value=1.5,
        step=0.1,
        help="Les gérants recevront ce coefficient multiplié par la part d'un associé normal"
    )
    
    # Sauvegarder la pondération comme paramètre
    from utils.helpers import set_parameter_value
    set_parameter_value("ponderation_gerants", str(ponderation_gerants), "Coefficient de pondération pour les gérants")
    
    # Créer des onglets pour les différentes fonctionnalités
    tab1, tab2 = st.tabs(["Configuration de la répartition", "Résultats de la répartition"])
    
    with tab1:
        st.subheader("Configuration du mode de répartition des indicateurs")
        
        # Grouper les indicateurs par axe
        indicateurs_par_axe = {}
        for indicateur in indicateurs:
            if indicateur.axe not in indicateurs_par_axe:
                indicateurs_par_axe[indicateur.axe] = []
            indicateurs_par_axe[indicateur.axe].append(indicateur)
        
        # Créer des expanders pour chaque axe
        for axe, indicateurs_axe in indicateurs_par_axe.items():
            with st.expander(f"Axe: {axe}", expanded=False):
                for indicateur in indicateurs_axe:
                    st.markdown(f"### {indicateur.nom}")
                    
                    # Récupérer la configuration de répartition existante
                    session = get_session()
                    repartition = session.query(Repartition).filter_by(indicateur_id=indicateur.id).first()
                    
                    # Si aucune répartition n'existe, en créer une par défaut
                    if not repartition:
                        repartition = Repartition(
                            indicateur_id=indicateur.id,
                            est_commun=True,
                            mode_repartition='egalitaire'
                        )
                        session.add(repartition)
                        session.commit()
                    
                    # Stocker les valeurs avant de fermer la session
                    est_commun_value = repartition.est_commun
                    
                    # Récupérer les attributions existantes
                    attributions = session.query(Attribution).filter_by(indicateur_id=indicateur.id).all()
                    # Créer un dictionnaire des associés déjà sélectionnés
                    associes_selectionnes = [a.associe_id for a in attributions if a.pourcentage > 0]
                    session.close()
                    
                    # Option simplifié: soit tous les associés, soit des associés spécifiques
                    est_commun = st.radio(
                        "Type de répartition",
                        ["Tous les associés", "Associés spécifiques"],
                        index=0 if est_commun_value else 1,
                        key=f"type_{indicateur.id}",
                        horizontal=True
                    )
                    
                    est_commun_bool = est_commun == "Tous les associés"
                    
                    # Si la configuration a changé, mettre à jour la base de données
                    if est_commun_bool != est_commun_value:
                        session = get_session()
                        repartition = session.query(Repartition).filter_by(indicateur_id=indicateur.id).first()
                        
                        if repartition:
                            repartition.est_commun = est_commun_bool
                            # Toujours utiliser le mode égalitaire (on a supprimé l'option proportionnelle)
                            repartition.mode_repartition = 'egalitaire'
                            session.commit()
                        
                        session.close()
                    
                    # Si on a sélectionné des associés spécifiques
                    if est_commun == "Associés spécifiques":
                        st.markdown("#### Sélection des associés")
                        
                        # Créer des cases à cocher pour chaque associé
                        associes_coches = {}
                        for associe in associes:
                            est_selectionne = associe.id in associes_selectionnes
                            associes_coches[associe.id] = st.checkbox(
                                f"{associe.prenom} {associe.nom}",
                                value=est_selectionne,
                                key=f"select_{indicateur.id}_{associe.id}"
                            )
                        
                        # Bouton pour sauvegarder la sélection
                        if st.button("Sauvegarder la sélection", key=f"save_{indicateur.id}"):
                            # Vérifier qu'au moins un associé est sélectionné
                            if not any(associes_coches.values()):
                                st.error("Vous devez sélectionner au moins un associé.")
                            else:
                                session = get_session()
                                
                                # Supprimer toutes les attributions existantes
                                session.query(Attribution).filter_by(indicateur_id=indicateur.id).delete()
                                
                                # Compter combien d'associés sont sélectionnés
                                nb_selectionnes = sum(1 for est_coche in associes_coches.values() if est_coche)
                                
                                # Créer de nouvelles attributions
                                for associe_id, est_coche in associes_coches.items():
                                    pourcentage = 100 / nb_selectionnes if est_coche else 0
                                    attribution = Attribution(
                                        indicateur_id=indicateur.id,
                                        associe_id=associe_id,
                                        pourcentage=pourcentage
                                    )
                                    session.add(attribution)
                                
                                session.commit()
                                session.close()
                                
                                st.success("Sélection sauvegardée avec succès.")
                    
                    # Si tous les associés sont sélectionnés, les pourcentages sont calculés automatiquement
                    else:
                        session = get_session()
                        
                        # Supprimer les attributions existantes
                        session.query(Attribution).filter_by(indicateur_id=indicateur.id).delete()
                        
                        # Créer des attributions pour tous les associés
                        for associe in associes:
                            attribution = Attribution(
                                indicateur_id=indicateur.id,
                                associe_id=associe.id,
                                pourcentage=0  # Le pourcentage sera calculé dynamiquement
                            )
                            session.add(attribution)
                        
                        session.commit()
                        session.close()
                    
                    st.markdown("---")
    
    with tab2:
        st.subheader("Résultats de la répartition des revenus")
        
        # Récupérer la répartition des revenus entre associés
        resultats = get_associes_repartition()
        
        if not resultats:
            st.info("Aucune répartition n'a été configurée. Veuillez configurer la répartition des indicateurs dans l'onglet 'Configuration'.")
        else:
            # Créer un DataFrame pour afficher les résultats
            df_resultats = pd.DataFrame({
                "Associé": [resultats[a_id]["nom"] for a_id in resultats],
                "Fonction": [resultats[a_id]["fonction"] for a_id in resultats],
                "Gérant": ["Oui" if resultats[a_id]["est_gerant"] else "Non" for a_id in resultats],
                "Part fixe": [format_currency(resultats[a_id]["part_fixe"]) for a_id in resultats],
                "Part variable": [format_currency(resultats[a_id]["part_variable"]) for a_id in resultats],
                "Total": [format_currency(resultats[a_id]["total"]) for a_id in resultats],
                "Pourcentage": [f"{resultats[a_id]['total'] / net_revenue * 100:.1f}%" if net_revenue > 0 else "0%" for a_id in resultats]
            })
            
            # Afficher le tableau
            st.dataframe(df_resultats, use_container_width=True)
            
            # Créer un graphique en camembert pour visualiser la répartition
            fig = px.pie(
                names=[resultats[a_id]["nom"] for a_id in resultats],
                values=[resultats[a_id]["total"] for a_id in resultats],
                title="Répartition des revenus entre associés",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4
            )
            
            fig.update_layout(
                font=dict(family="Lato, sans-serif"),
                title_font=dict(size=20, color="#0596DE"),
                legend_title_font=dict(size=14),
                legend_font=dict(size=12),
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Créer un graphique en barres pour comparer part fixe et part variable
            df_barres = pd.DataFrame({
                "Associé": [resultats[a_id]["nom"] for a_id in resultats],
                "Part fixe": [resultats[a_id]["part_fixe"] for a_id in resultats],
                "Part variable": [resultats[a_id]["part_variable"] for a_id in resultats]
            })
            
            df_barres_melted = pd.melt(
                df_barres,
                id_vars=["Associé"],
                value_vars=["Part fixe", "Part variable"],
                var_name="Type de part",
                value_name="Montant (€)"
            )
            
            fig_barres = px.bar(
                df_barres_melted,
                x="Associé",
                y="Montant (€)",
                color="Type de part",
                title="Répartition part fixe / part variable par associé",
                barmode="stack",
                color_discrete_map={
                    "Part fixe": "#0596DE",
                    "Part variable": "#2D3E50"
                }
            )
            
            fig_barres.update_layout(
                font=dict(family="Lato, sans-serif"),
                title_font=dict(size=20, color="#0596DE"),
                legend_title_font=dict(size=14),
                legend_font=dict(size=12),
            )
            
            st.plotly_chart(fig_barres, use_container_width=True)
    
    # Ajouter une note explicative
    st.markdown("---")
    st.info("""
    **Note sur la répartition**:
    
    - **Tous les associés**: L'indicateur est réparti entre tous les associés, avec une pondération pour les gérants.
    - **Associés spécifiques**: Seuls les associés sélectionnés reçoivent une part de l'indicateur, répartie équitablement entre eux.
    
    La part fixe correspond aux indicateurs socle/prérequis, tandis que la part variable correspond aux indicateurs optionnels.
    
    Le coefficient de pondération des gérants multiplie leur part par rapport à un associé normal.
    """)
