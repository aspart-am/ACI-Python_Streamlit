from models.models import Indicateur, Parametre
from utils.db_config import get_session, init_db

def init_parametres():
    """Initialise les paramètres par défaut."""
    session = get_session()
    
    parametres = [
        {"cle": "valeur_point", "valeur": "7", "description": "Valeur d'un point en euros"},
        {"cle": "annee_en_cours", "valeur": "2023", "description": "Année en cours pour les calculs"},
        {"cle": "version_avenant", "valeur": "Avenant 1 - Octobre 2022", "description": "Version de l'avenant en vigueur"}
    ]
    
    for param in parametres:
        # Vérifier si le paramètre existe déjà
        existing = session.query(Parametre).filter_by(cle=param["cle"]).first()
        if not existing:
            session.add(Parametre(**param))
    
    session.commit()
    session.close()

def init_indicateurs():
    """Initialise les indicateurs ACI avec les valeurs par défaut."""
    session = get_session()
    
    # Axe 1: Accès aux soins
    indicateurs_axe1 = [
        {
            "nom": "Horaires d'ouverture + soins non programmés",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 800,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Réponse aux crises sanitaires graves - Plan",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Réponse aux crises sanitaires graves - Activation",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 350,
            "formule_calcul": "350 si crise, 0 sinon"
        },
        {
            "nom": "Diversité de services (associés) - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Diversité de services (associés) - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Spécialistes vacataires - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Spécialistes vacataires - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Médecin CSTM",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Missions de santé publique (sans IPA)",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 700,
            "formule_calcul": "Jusqu'à 700 points variables selon la mission"
        },
        {
            "nom": "Missions de santé publique (avec IPA)",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 700,
            "formule_calcul": "200 points fixes + jusqu'à 700 points variables selon la mission"
        },
        {
            "nom": "Implication des usagers - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Implication des usagers - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 300,
            "formule_calcul": "300 points variables"
        },
        {
            "nom": "Soins non programmés & SAS - 50% médecins",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Soins non programmés & SAS - 100% médecins",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": None
        }
    ]
    
    # Axe 2: Travail en équipe & coordination
    indicateurs_axe2 = [
        {
            "nom": "Fonction de coordination - Fixe",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 1000,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Fonction de coordination - Variable (jusqu'à 8000 patients)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 1700,
            "formule_calcul": "1700 * min(patientele, 8000) / 4000"
        },
        {
            "nom": "Fonction de coordination - Variable (au-delà de 8000 patients)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 1100,
            "formule_calcul": "1100 * max(patientele - 8000, 0) / 4000"
        },
        {
            "nom": "Protocoles pluri-professionnels (sans IPA)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points par protocole (max 8)"
        },
        {
            "nom": "Protocoles pluri-professionnels (avec IPA)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 140,
            "points_variables": 0,
            "formule_calcul": "140 points par protocole (max 8)"
        },
        {
            "nom": "Concertation pluri-professionnelle (sans IPA)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 1000,
            "formule_calcul": "1000 * (patientele/4000) * (taux_dossiers/5%)"
        },
        {
            "nom": "Concertation pluri-professionnelle (avec IPA)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 200,
            "points_variables": 1000,
            "formule_calcul": "200 + 1000 * (patientele/4000) * (taux_dossiers/5%)"
        },
        {
            "nom": "Formation de professionnels - 2 stages",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 450,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Formation de professionnels - 3e & 4e stage",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 225,
            "points_variables": 0,
            "formule_calcul": "225 points par stage supplémentaire (max 2)"
        },
        {
            "nom": "Coordination externe",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 * (patientele/4000)"
        },
        {
            "nom": "Démarche qualité - Niveau 1",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "Démarche qualité - Niveau 2",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 points variables"
        },
        {
            "nom": "Démarche qualité - Niveau 3",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 300,
            "formule_calcul": "300 points variables"
        },
        {
            "nom": "Protocoles nationaux de coopération",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points par protocole (max 6)"
        },
        {
            "nom": "Parcours insuffisance cardiaque",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 100,
            "formule_calcul": "100 * (patientele/4000)"
        },
        {
            "nom": "Parcours surpoids/obésité enfant",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points (condition mission santé publique)"
        }
    ]
    
    # Axe 3: Système d'information
    indicateurs_axe3 = [
        {
            "nom": "SI labellisé 'Standard' (ANS) - Fixe",
            "axe": "Système d'information",
            "type": "socle",
            "points_fixes": 500,
            "points_variables": 0,
            "formule_calcul": None
        },
        {
            "nom": "SI labellisé 'Standard' (ANS) - Variable (jusqu'à 16 PS)",
            "axe": "Système d'information",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 * min(nombre_PS, 16)"
        },
        {
            "nom": "SI labellisé 'Standard' (ANS) - Variable (au-delà de 16 PS)",
            "axe": "Système d'information",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 150,
            "formule_calcul": "150 * max(nombre_PS - 16, 0)"
        },
        {
            "nom": "SI 'Avancé'",
            "axe": "Système d'information",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points (cumulable, prorata temporis)"
        }
    ]
    
    # Ajouter tous les indicateurs à la base de données
    all_indicateurs = indicateurs_axe1 + indicateurs_axe2 + indicateurs_axe3
    
    for indic in all_indicateurs:
        # Vérifier si l'indicateur existe déjà
        existing = session.query(Indicateur).filter_by(nom=indic["nom"]).first()
        if not existing:
            session.add(Indicateur(**indic))
    
    session.commit()
    session.close()

def initialize_all_data():
    """Initialise toutes les données par défaut."""
    init_db()
    init_parametres()
    init_indicateurs()
    print("Toutes les données ont été initialisées avec succès.")

if __name__ == "__main__":
    initialize_all_data()
