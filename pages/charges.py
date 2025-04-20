import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.helpers import format_currency, calculate_charges_total
from models import Charge
from utils import get_session

def show():
    """Affiche la page de gestion des charges."""
    st.title("Gestion des charges SISA")
    
    # Créer deux colonnes : une pour la liste des charges, une pour le formulaire
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Liste des charges")
        
        # Récupérer toutes les charges
        session = get_session()
        charges = session.query(Charge).all()
        session.close()
        
        # Calculer le total des charges
        total_charges = calculate_charges_total()
        
        # Afficher le total des charges
        st.metric(
            label="Total des charges", 
            value=format_currency(total_charges)
        )
        
        if not charges:
            st.info("Aucune charge n'a été ajoutée. Utilisez le formulaire pour ajouter des charges.")
        else:
            # Créer un DataFrame pour afficher les charges
            df_charges = pd.DataFrame({
                "ID": [c.id for c in charges],
                "Libellé": [c.libelle for c in charges],
                "Montant": [format_currency(c.montant) for c in charges],
                "Catégorie": [c.categorie for c in charges],
                "Date": [c.date_saisie.strftime("%d/%m/%Y") if c.date_saisie else "" for c in charges]
            })
            
            # Afficher le tableau
            st.dataframe(df_charges, use_container_width=True)
            
            # Créer un graphique en camembert pour visualiser la répartition des charges par catégorie
            if len(charges) > 0:
                # Grouper les charges par catégorie
                charges_par_categorie = {}
                for charge in charges:
                    categorie = charge.categorie or "Non catégorisé"
                    if categorie not in charges_par_categorie:
                        charges_par_categorie[categorie] = 0
                    charges_par_categorie[categorie] += charge.montant
                
                # Créer le graphique
                fig = px.pie(
                    names=list(charges_par_categorie.keys()),
                    values=list(charges_par_categorie.values()),
                    title="Répartition des charges par catégorie",
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
            
            # Sélection d'une charge pour modification ou suppression
            charge_id = st.selectbox(
                "Sélectionner une charge à modifier ou supprimer",
                options=[c.id for c in charges],
                format_func=lambda x: f"{next((c.libelle for c in charges if c.id == x), '')} - {format_currency(next((c.montant for c in charges if c.id == x), 0))}"
            )
            
            # Récupérer la charge sélectionnée
            charge_selectionnee = next((c for c in charges if c.id == charge_id), None)
            
            if charge_selectionnee:
                # Boutons pour modifier ou supprimer
                col_edit, col_delete = st.columns(2)
                
                with col_edit:
                    if st.button("Modifier cette charge", key="btn_edit_charge"):
                        # Stocker l'ID de la charge à modifier dans la session
                        st.session_state.charge_a_modifier = charge_id
                        st.rerun()
                
                with col_delete:
                    if st.button("Supprimer cette charge", key="btn_delete_charge"):
                        # Confirmation de suppression
                        if st.checkbox("Confirmer la suppression", key="confirm_delete_charge"):
                            session = get_session()
                            charge = session.query(Charge).filter_by(id=charge_id).first()
                            if charge:
                                session.delete(charge)
                                session.commit()
                                st.success(f"La charge '{charge.libelle}' a été supprimée avec succès.")
                                st.rerun()
                            session.close()
    
    with col2:
        # Vérifier si on est en mode modification
        mode_modification = "charge_a_modifier" in st.session_state
        
        if mode_modification:
            st.subheader("Modifier une charge")
            
            # Récupérer la charge à modifier
            session = get_session()
            charge = session.query(Charge).filter_by(id=st.session_state.charge_a_modifier).first()
            session.close()
            
            if charge:
                # Formulaire pré-rempli avec les données de la charge
                libelle = st.text_input("Libellé", value=charge.libelle)
                montant = st.number_input(
                    "Montant (€)",
                    min_value=0.0,
                    value=float(charge.montant),
                    step=10.0
                )
                
                # Liste des catégories prédéfinies
                categories = [
                    "Loyer et charges",
                    "Salaires et charges sociales",
                    "Fournitures",
                    "Matériel médical",
                    "Informatique",
                    "Assurances",
                    "Frais bancaires",
                    "Honoraires",
                    "Impôts et taxes",
                    "Autres"
                ]
                
                categorie = st.selectbox(
                    "Catégorie",
                    options=categories,
                    index=categories.index(charge.categorie) if charge.categorie in categories else 0
                )
                
                date_saisie = st.date_input(
                    "Date",
                    value=charge.date_saisie if charge.date_saisie else datetime.now().date()
                )
                
                # Boutons pour sauvegarder ou annuler
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    if st.button("Sauvegarder", key="btn_save_charge"):
                        session = get_session()
                        charge = session.query(Charge).filter_by(id=st.session_state.charge_a_modifier).first()
                        
                        if charge:
                            charge.libelle = libelle
                            charge.montant = montant
                            charge.categorie = categorie
                            charge.date_saisie = date_saisie
                            
                            session.commit()
                            st.success(f"La charge '{libelle}' a été modifiée avec succès.")
                            
                            # Réinitialiser le mode modification
                            del st.session_state.charge_a_modifier
                            st.rerun()
                        
                        session.close()
                
                with col_cancel:
                    if st.button("Annuler", key="btn_cancel_charge"):
                        # Réinitialiser le mode modification
                        del st.session_state.charge_a_modifier
                        st.rerun()
        
        else:
            st.subheader("Ajouter une nouvelle charge")
            
            # Formulaire pour ajouter une nouvelle charge
            libelle = st.text_input("Libellé")
            montant = st.number_input(
                "Montant (€)",
                min_value=0.0,
                value=0.0,
                step=10.0
            )
            
            # Liste des catégories prédéfinies
            categories = [
                "Loyer et charges",
                "Salaires et charges sociales",
                "Fournitures",
                "Matériel médical",
                "Informatique",
                "Assurances",
                "Frais bancaires",
                "Honoraires",
                "Impôts et taxes",
                "Autres"
            ]
            
            categorie = st.selectbox("Catégorie", options=categories)
            date_saisie = st.date_input("Date", value=datetime.now().date())
            
            if st.button("Ajouter", key="btn_add_charge"):
                if libelle and montant > 0:  # Vérifier que les champs obligatoires sont remplis
                    session = get_session()
                    
                    # Créer une nouvelle charge
                    nouvelle_charge = Charge(
                        libelle=libelle,
                        montant=montant,
                        categorie=categorie,
                        date_saisie=date_saisie
                    )
                    
                    session.add(nouvelle_charge)
                    session.commit()
                    session.close()
                    
                    st.success(f"La charge '{libelle}' a été ajoutée avec succès.")
                    st.rerun()
                else:
                    st.error("Veuillez remplir le libellé et saisir un montant supérieur à 0.")
        
        # Ajouter un formulaire pour l'import de charges depuis un fichier CSV
        st.markdown("---")
        st.subheader("Import de charges")
        
        st.info("""
        Vous pouvez importer des charges depuis un fichier CSV.
        Le fichier doit contenir les colonnes suivantes :
        - libelle
        - montant
        - categorie (optionnel)
        - date_saisie (optionnel, format JJ/MM/AAAA)
        """)
        
        uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
        
        if uploaded_file is not None:
            try:
                # Lire le fichier CSV
                df = pd.read_csv(uploaded_file, sep=",")
                
                # Vérifier que les colonnes obligatoires sont présentes
                if "libelle" not in df.columns or "montant" not in df.columns:
                    st.error("Le fichier CSV doit contenir au moins les colonnes 'libelle' et 'montant'.")
                else:
                    # Afficher un aperçu du fichier
                    st.write("Aperçu du fichier :")
                    st.dataframe(df.head())
                    
                    # Bouton pour confirmer l'import
                    if st.button("Importer les charges"):
                        session = get_session()
                        
                        # Parcourir les lignes du DataFrame
                        for _, row in df.iterrows():
                            # Créer une nouvelle charge
                            nouvelle_charge = Charge(
                                libelle=row["libelle"],
                                montant=float(row["montant"]),
                                categorie=row["categorie"] if "categorie" in df.columns and pd.notna(row["categorie"]) else "Autres",
                                date_saisie=datetime.strptime(row["date_saisie"], "%d/%m/%Y").date() if "date_saisie" in df.columns and pd.notna(row["date_saisie"]) else datetime.now().date()
                            )
                            
                            session.add(nouvelle_charge)
                        
                        session.commit()
                        session.close()
                        
                        st.success(f"{len(df)} charges ont été importées avec succès.")
                        st.rerun()
            
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'import : {str(e)}")
    
    # Ajouter une note explicative
    st.markdown("---")
    st.info("""
    **Note**: Les charges saisies ici seront déduites du montant total des revenus ACI 
    pour calculer le revenu net à répartir entre les associés.
    
    Vous pouvez catégoriser les charges pour mieux visualiser leur répartition.
    """)
