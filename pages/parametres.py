import streamlit as st
import pandas as pd
import os
import sqlite3
from datetime import datetime
from utils.helpers import get_parameter_value, set_parameter_value
from models import Parametre, Indicateur
from utils import get_session, init_db, initialize_all_data

def show():
    """Affiche la page des paramètres de l'application."""
    st.title("Paramètres de l'application")
    
    # Créer des onglets pour les différentes sections de paramètres
    tab1, tab2, tab3, tab4 = st.tabs([
        "Paramètres généraux", 
        "Gestion des données", 
        "Paramètres des indicateurs",
        "À propos"
    ])
    
    with tab1:
        st.subheader("Paramètres généraux")
        
        # Récupérer les paramètres existants
        session = get_session()
        parametres = session.query(Parametre).all()
        session.close()
        
        # Créer un dictionnaire des paramètres
        params_dict = {p.cle: p.valeur for p in parametres}
        
        # Formulaire pour les paramètres généraux
        with st.form("form_parametres_generaux"):
            # Valeur du point
            valeur_point = st.number_input(
                "Valeur du point (€)",
                min_value=0.0,
                value=float(params_dict.get("valeur_point", 7)),
                step=0.1,
                help="Valeur d'un point en euros (actuellement 7€)"
            )
            
            # Année en cours
            annee_en_cours = st.number_input(
                "Année en cours",
                min_value=2020,
                max_value=2030,
                value=int(params_dict.get("annee_en_cours", datetime.now().year)),
                step=1,
                help="Année en cours pour les calculs"
            )
            
            # Version de l'avenant
            version_avenant = st.text_input(
                "Version de l'avenant",
                value=params_dict.get("version_avenant", "Avenant 1 - Octobre 2022"),
                help="Version de l'avenant en vigueur"
            )
            
            # Patientèle
            patientele = st.number_input(
                "Patientèle",
                min_value=0,
                value=int(params_dict.get("patientele", 4000)),
                step=100,
                help="Nombre de patients de la structure"
            )
            
            # Nombre de professionnels de santé
            nombre_ps = st.number_input(
                "Nombre de professionnels de santé",
                min_value=1,
                value=int(params_dict.get("nombre_ps", 10)),
                step=1,
                help="Nombre de professionnels de santé dans la structure"
            )
            
            # Taux de dossiers pour la concertation
            taux_dossiers = st.number_input(
                "Taux de dossiers pour la concertation (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(params_dict.get("taux_dossiers", 5)),
                step=0.5,
                help="Pourcentage de dossiers pour la concertation pluri-professionnelle"
            )
            
            # Bouton pour sauvegarder les paramètres
            submitted = st.form_submit_button("Sauvegarder les paramètres")
            
            if submitted:
                # Mettre à jour les paramètres
                set_parameter_value("valeur_point", str(valeur_point))
                set_parameter_value("annee_en_cours", str(annee_en_cours))
                set_parameter_value("version_avenant", version_avenant)
                set_parameter_value("patientele", str(patientele))
                set_parameter_value("nombre_ps", str(nombre_ps))
                set_parameter_value("taux_dossiers", str(taux_dossiers))
                
                st.success("Paramètres mis à jour avec succès !")
    
    with tab2:
        st.subheader("Gestion des données")
        
        # Chemin vers le fichier de base de données
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'aci_app.db')
        
        # Afficher des informations sur la base de données
        if os.path.exists(db_path):
            # Taille de la base de données
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convertir en Mo
            
            # Nombre d'enregistrements dans chaque table
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            tables = [
                "indicateurs", 
                "associes", 
                "repartitions", 
                "attributions", 
                "charges", 
                "parametres",
                "patientele",
                "professionnels_sante"
            ]
            
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                except sqlite3.OperationalError:
                    table_counts[table] = "Table inexistante"
            
            conn.close()
            
            # Afficher les informations
            st.info(f"Taille de la base de données : {db_size:.2f} Mo")
            
            # Créer un DataFrame pour afficher les nombres d'enregistrements
            df_counts = pd.DataFrame({
                "Table": list(table_counts.keys()),
                "Nombre d'enregistrements": list(table_counts.values())
            })
            
            st.dataframe(df_counts, use_container_width=True)
        
        else:
            st.warning("La base de données n'existe pas encore. Elle sera créée au premier démarrage de l'application.")
        
        # Options de gestion de la base de données
        st.subheader("Options de gestion")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Réinitialiser la base de données
            if st.button("Réinitialiser la base de données"):
                # Demander confirmation
                if st.checkbox("Je confirme vouloir réinitialiser la base de données. Cette action est irréversible.", key="confirm_reset_db"):
                    # Supprimer la base de données existante
                    if os.path.exists(db_path):
                        os.remove(db_path)
                    
                    # Recréer la base de données
                    initialize_all_data()
                    
                    st.success("Base de données réinitialisée avec succès !")
                    st.experimental_rerun()
        
        with col2:
            # Exporter la base de données
            if st.button("Exporter la base de données"):
                if os.path.exists(db_path):
                    # Lire le contenu du fichier
                    with open(db_path, "rb") as f:
                        db_content = f.read()
                    
                    # Créer un lien de téléchargement
                    st.download_button(
                        label="Télécharger la base de données",
                        data=db_content,
                        file_name="aci_app_backup.db",
                        mime="application/octet-stream"
                    )
                else:
                    st.error("La base de données n'existe pas encore.")
        
        # Importer une base de données
        st.subheader("Importer une base de données")
        
        uploaded_file = st.file_uploader("Choisir un fichier de base de données SQLite", type="db")
        
        if uploaded_file is not None:
            # Demander confirmation
            if st.checkbox("Je confirme vouloir remplacer la base de données actuelle. Cette action est irréversible.", key="confirm_import_db"):
                # Sauvegarder le fichier importé
                with open(db_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success("Base de données importée avec succès !")
                st.experimental_rerun()
    
    with tab3:
        st.subheader("Paramètres des indicateurs")
        
        # Récupérer tous les indicateurs
        session = get_session()
        indicateurs = session.query(Indicateur).all()
        session.close()
        
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
                    
                    # Formulaire pour modifier les paramètres de l'indicateur
                    with st.form(f"form_indicateur_{indicateur.id}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            points_fixes = st.number_input(
                                "Points fixes",
                                min_value=0,
                                value=indicateur.points_fixes,
                                step=10,
                                key=f"points_fixes_{indicateur.id}"
                            )
                        
                        with col2:
                            points_variables = st.number_input(
                                "Points variables",
                                min_value=0,
                                value=indicateur.points_variables,
                                step=10,
                                key=f"points_variables_{indicateur.id}"
                            )
                        
                        formule_calcul = st.text_area(
                            "Formule de calcul",
                            value=indicateur.formule_calcul or "",
                            height=100,
                            key=f"formule_{indicateur.id}"
                        )
                        
                        prorata = st.slider(
                            "Prorata",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(indicateur.prorata),
                            step=0.05,
                            key=f"prorata_{indicateur.id}",
                            help="Prorata à appliquer aux points (entre 0 et 1)"
                        )
                        
                        # Bouton pour sauvegarder les modifications
                        submitted = st.form_submit_button("Sauvegarder")
                        
                        if submitted:
                            session = get_session()
                            indic = session.query(Indicateur).filter_by(id=indicateur.id).first()
                            
                            if indic:
                                indic.points_fixes = points_fixes
                                indic.points_variables = points_variables
                                indic.formule_calcul = formule_calcul
                                indic.prorata = prorata
                                
                                session.commit()
                                st.success(f"Indicateur '{indicateur.nom}' mis à jour avec succès !")
                            
                            session.close()
                    
                    st.markdown("---")
    
    with tab4:
        st.subheader("À propos de l'application")
        
        st.markdown("""
        ### ACI Manager

        **Version**: 1.0.0

        **Description**: Application de gestion des revenus ACI et leur répartition entre associés.

        Cette application permet de :
        - Calculer les revenus CPAM d'indicateurs ACI selon les règles conventionnelles
        - Valider les indicateurs et gérer leurs prorata
        - Répartir les sommes entre les différents associés
        - Gérer les charges de la SISA

        **Développée avec**:
        - Python
        - Streamlit
        - SQLAlchemy
        - Plotly

        **Licence**: Tous droits réservés
        """)
        
        # Afficher les informations sur la version de l'avenant
        version_avenant = get_parameter_value("version_avenant") or "Avenant 1 - Octobre 2022"
        st.info(f"Version de l'avenant en vigueur : {version_avenant}")
