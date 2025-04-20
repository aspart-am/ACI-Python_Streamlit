import streamlit as st
import pandas as pd
from utils.helpers import format_currency
from models import Associe
from utils import get_session

def show():
    """Affiche la page de gestion des associés."""
    st.title("Gestion des associés")
    
    # Créer deux colonnes : une pour la liste des associés, une pour le formulaire
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Liste des associés")
        
        # Récupérer tous les associés
        session = get_session()
        associes = session.query(Associe).all()
        session.close()
        
        if not associes:
            st.info("Aucun associé n'a été ajouté. Utilisez le formulaire pour ajouter des associés.")
        else:
            # Créer un DataFrame pour afficher les associés
            df_associes = pd.DataFrame({
                "ID": [a.id for a in associes],
                "Nom": [a.nom for a in associes],
                "Prénom": [a.prenom for a in associes],
                "Fonction": [a.fonction for a in associes],
                "Gérant": ["Oui" if a.est_gerant else "Non" for a in associes],
                "Coefficient": [f"{a.coefficient_majoration:.2f}" for a in associes]
            })
            
            # Afficher le tableau
            st.dataframe(df_associes, use_container_width=True)
            
            # Sélection d'un associé pour modification ou suppression
            associe_id = st.selectbox(
                "Sélectionner un associé à modifier ou supprimer",
                options=[a.id for a in associes],
                format_func=lambda x: f"{next((a.prenom + ' ' + a.nom for a in associes if a.id == x), '')}"
            )
            
            # Récupérer l'associé sélectionné
            associe_selectionne = next((a for a in associes if a.id == associe_id), None)
            
            if associe_selectionne:
                # Boutons pour modifier ou supprimer
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("Modifier cet associé", key="btn_edit"):
                        # Stocker l'ID de l'associé à modifier dans la session
                        st.session_state.associe_a_modifier = associe_id
                        st.rerun()
                
                with col_delete:
                    if st.button("Supprimer cet associé", key="btn_delete"):
                        # Confirmation de suppression
                        if st.checkbox("Confirmer la suppression", key="confirm_delete"):
                            session = get_session()
                            associe = session.query(Associe).filter_by(id=associe_id).first()
                            if associe:
                                session.delete(associe)
                                session.commit()
                                st.success(f"L'associé {associe.prenom} {associe.nom} a été supprimé avec succès.")
                                st.rerun()
                            session.close()
    
    with col2:
        # Vérifier si on est en mode modification
        mode_modification = "associe_a_modifier" in st.session_state
        
        if mode_modification:
            st.subheader("Modifier un associé")
            
            # Récupérer l'associé à modifier
            session = get_session()
            associe = session.query(Associe).filter_by(id=st.session_state.associe_a_modifier).first()
            session.close()
            
            if associe:
                # Formulaire pré-rempli avec les données de l'associé
                nom = st.text_input("Nom", value=associe.nom)
                prenom = st.text_input("Prénom", value=associe.prenom)
                fonction = st.text_input("Fonction", value=associe.fonction)
                est_gerant = st.checkbox("Est gérant", value=associe.est_gerant)
                coefficient = st.number_input(
                    "Coefficient de majoration",
                    min_value=1.0,
                    max_value=5.0,
                    value=float(associe.coefficient_majoration),
                    step=0.1
                )
                
                # Boutons pour sauvegarder ou annuler
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.button("Sauvegarder", key="btn_save"):
                        session = get_session()
                        associe = session.query(Associe).filter_by(id=st.session_state.associe_a_modifier).first()
                        
                        if associe:
                            associe.nom = nom
                            associe.prenom = prenom
                            associe.fonction = fonction
                            associe.est_gerant = est_gerant
                            associe.coefficient_majoration = coefficient
                            
                            session.commit()
                            st.success(f"L'associé {prenom} {nom} a été modifié avec succès.")
                            
                            # Réinitialiser le mode modification
                            del st.session_state.associe_a_modifier
                            st.rerun()
                        
                        session.close()
                
                with col_cancel:
                    if st.button("Annuler", key="btn_cancel"):
                        # Réinitialiser le mode modification
                        del st.session_state.associe_a_modifier
                        st.rerun()
        
        else:
            st.subheader("Ajouter un nouvel associé")
            
            # Formulaire pour ajouter un nouvel associé
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            fonction = st.text_input("Fonction")
            est_gerant = st.checkbox("Est gérant")
            coefficient = st.number_input(
                "Coefficient de majoration",
                min_value=1.0,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Coefficient appliqué pour les gérants (1.0 = pas de majoration)"
            )
            
            if st.button("Ajouter", key="btn_add"):
                if nom and prenom:  # Vérifier que les champs obligatoires sont remplis
                    session = get_session()
                    
                    # Créer un nouvel associé
                    nouvel_associe = Associe(
                        nom=nom,
                        prenom=prenom,
                        fonction=fonction,
                        est_gerant=est_gerant,
                        coefficient_majoration=coefficient
                    )
                    
                    session.add(nouvel_associe)
                    session.commit()
                    session.close()
                    
                    st.success(f"L'associé {prenom} {nom} a été ajouté avec succès.")
                    st.rerun()
                else:
                    st.error("Veuillez remplir au moins les champs Nom et Prénom.")
    
    # Ajouter une note explicative
    st.markdown("---")
    st.info("""
    **Note**: Les associés ajoutés ici pourront être utilisés dans la page "Répartition des revenus" 
    pour définir comment les revenus ACI sont répartis entre eux.
    
    Le coefficient de majoration est utilisé pour les gérants et permet d'augmenter leur part 
    dans la répartition des revenus (1.0 = pas de majoration, 2.0 = part doublée, etc.).
    """)
