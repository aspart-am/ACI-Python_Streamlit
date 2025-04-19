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
                    
                    # Récupérer les attributions existantes
                    attributions = session.query(Attribution).filter_by(indicateur_id=indicateur.id).all()
                    attributions_dict = {a.associe_id: a for a in attributions}
                    session.close()
                    
                    # Formulaire pour configurer la répartition
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        est_commun = st.checkbox(
                            "Répartition commune",
                            value=repartition.est_commun,
                            key=f"commun_{indicateur.id}",
                            help="Si coché, l'indicateur est réparti entre tous les associés. Sinon, il est attribué à des associés spécifiques."
                        )
                    
                    with col2:
                        modes = {
                            'egalitaire': 'Égalitaire (parts égales)',
                            'proportionnel': 'Proportionnel au coefficient',
                            'personnalise': 'Personnalisé (pourcentages manuels)'
                        }
                        
                        mode_repartition = st.selectbox(
                            "Mode de répartition",
                            options=list(modes.keys()),
                            format_func=lambda x: modes[x],
                            index=list(modes.keys()).index(repartition.mode_repartition),
                            key=f"mode_{indicateur.id}"
                        )
                    
                    # Si la configuration a changé, mettre à jour la base de données
                    if est_commun != repartition.est_commun or mode_repartition != repartition.mode_repartition:
                        session = get_session()
                        repartition = session.query(Repartition).filter_by(indicateur_id=indicateur.id).first()
                        
                        if repartition:
                            repartition.est_commun = est_commun
                            repartition.mode_repartition = mode_repartition
                            session.commit()
                        
                        session.close()
                    
                    # Si le mode est personnalisé, afficher les pourcentages pour chaque associé
                    if mode_repartition == 'personnalise':
                        st.markdown("#### Pourcentages par associé")
                        
                        # Créer un formulaire pour les pourcentages
                        pourcentages = {}
                        total_pourcentage = 0
                        
                        for associe in associes:
                            # Récupérer le pourcentage existant ou définir 0 par défaut
                            pourcentage_existant = 0
                            if associe.id in attributions_dict:
                                pourcentage_existant = attributions_dict[associe.id].pourcentage
                            
                            pourcentage = st.slider(
                                f"{associe.prenom} {associe.nom}",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(pourcentage_existant),
                                step=1.0,
                                key=f"pct_{indicateur.id}_{associe.id}"
                            )
                            
                            pourcentages[associe.id] = pourcentage
                            total_pourcentage += pourcentage
                        
                        # Afficher le total des pourcentages
                        if total_pourcentage != 100:
                            st.warning(f"Le total des pourcentages est de {total_pourcentage}%. Il devrait être de 100%.")
                        else:
                            st.success("Le total des pourcentages est de 100%.")
                        
                        # Bouton pour sauvegarder les pourcentages
                        if st.button("Sauvegarder les pourcentages", key=f"save_{indicateur.id}"):
                            if total_pourcentage == 100:
                                session = get_session()
                                
                                # Mettre à jour ou créer les attributions
                                for associe_id, pourcentage in pourcentages.items():
                                    attribution = session.query(Attribution).filter_by(
                                        indicateur_id=indicateur.id,
                                        associe_id=associe_id
                                    ).first()
                                    
                                    if attribution:
                                        attribution.pourcentage = pourcentage
                                    else:
                                        attribution = Attribution(
                                            indicateur_id=indicateur.id,
                                            associe_id=associe_id,
                                            pourcentage=pourcentage
                                        )
                                        session.add(attribution)
                                
                                session.commit()
                                session.close()
                                
                                st.success("Pourcentages sauvegardés avec succès.")
                            else:
                                st.error("Le total des pourcentages doit être de 100% pour sauvegarder.")
                    
                    # Si le mode n'est pas personnalisé, créer des attributions par défaut
                    else:
                        session = get_session()
                        
                        # Supprimer les attributions personnalisées existantes
                        session.query(Attribution).filter_by(indicateur_id=indicateur.id).delete()
                        
                        # Créer des attributions par défaut pour tous les associés
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
                "Coefficient": [f"{resultats[a_id]['coefficient']:.2f}" for a_id in resultats],
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
    **Note sur les modes de répartition**:
    
    - **Égalitaire**: Chaque associé reçoit une part égale des revenus de l'indicateur.
    - **Proportionnel au coefficient**: La répartition est proportionnelle au coefficient de majoration de chaque associé (les gérants avec un coefficient plus élevé reçoivent une part plus importante).
    - **Personnalisé**: Vous définissez manuellement le pourcentage attribué à chaque associé.
    
    La part fixe correspond aux indicateurs socle/prérequis, tandis que la part variable correspond aux indicateurs optionnels.
    """)
