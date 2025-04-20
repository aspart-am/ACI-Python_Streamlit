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
            "nom": "Amplitude horaires complète (8h-20h + samedi matin)",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 800,
            "points_variables": 0,
            "formule_calcul": "800 points si ouverture 8h-20h lun-ven + samedi matin",
            "prorata": 1.0,
            "description": "Amplitude complète : 800 points si la MSP est ouverte de 8h à 20h du lundi au vendredi et le samedi matin."
        },
        {
            "nom": "Amplitude horaires réduite (10h-12h)",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 740,
            "points_variables": 0,
            "formule_calcul": "740 points si ouverture 10h-12h lun-ven + samedi matin",
            "prorata": 1.0,
            "description": "Amplitude réduite : 740 points si ouverture 10h-12h du lundi au vendredi + samedi matin."
        },
        {
            "nom": "Amplitude horaires réduite (8h-10h)",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 650,
            "points_variables": 0,
            "formule_calcul": "650 points si ouverture 8h-10h lun-ven + samedi matin",
            "prorata": 1.0,
            "description": "Amplitude réduite : 650 points si ouverture 8h-10h du lundi au vendredi + samedi matin."
        },
        {
            "nom": "Amplitude horaires sans samedi matin",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 680,
            "points_variables": 0,
            "formule_calcul": "680 points si fermeture le samedi matin",
            "prorata": 1.0,
            "description": "Amplitude réduite : 680 points si fermeture le samedi matin."
        },
        {
            "nom": "Fermeture limitée (≤ 3 semaines/an)",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 780,
            "points_variables": 0,
            "formule_calcul": "780 points si fermeture limitée à ≤ 3 semaines/an",
            "prorata": 1.0,
            "description": "Amplitude réduite : 780 points si fermeture limitée à ≤ 3 semaines/an."
        },
        {
            "nom": "Réponse aux crises sanitaires - Plan",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points si la MSP dispose d'un plan formalisé",
            "prorata": 1.0,
            "description": "Plan de préparation : 100 points si la MSP dispose d'un plan formalisé pour répondre aux crises sanitaires."
        },
        {
            "nom": "Réponse aux crises sanitaires - Actions",
            "axe": "Accès aux soins",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 350,
            "formule_calcul": "350 × patientele/4000 si le plan est actif",
            "prorata": 1.0,
            "description": "Actions complémentaires : 350 points proratisés selon la patientèle si le plan est actif et des actions spécifiques sont menées."
        },
        {
            "nom": "Diversité de services - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": "300 points fixes",
            "prorata": 1.0,
            "description": "300 points pour le niveau 1 (ex. une profession médicale ou pharmacien en plus...)"
        },
        {
            "nom": "Diversité de services - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": "300 points fixes",
            "prorata": 1.0,
            "description": "300 points pour le niveau 2 (ex. 3 professions paramédicales différentes...)"
        },
        {
            "nom": "Spécialistes vacataires - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": "300 points fixes - accès ponctuel à un spécialiste extérieur",
            "prorata": 1.0,
            "description": "300 points niveau 1 (accès ponctuel à un spécialiste extérieur)"
        },
        {
            "nom": "Spécialistes vacataires - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 300,
            "points_variables": 0,
            "formule_calcul": "300 points fixes - au moins 2,5 jours de consultations par semaine",
            "prorata": 1.0,
            "description": "300 points niveau 2 (au moins 2,5 jours de consultations par semaine)"
        },
        {
            "nom": "Médecin CST - Individuel",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": "200 points si au moins un médecin a signé un CST",
            "prorata": 1.0,
            "description": "200 points si au moins un médecin de la MSP a signé un Contrat de Solidarité Territoriale (CST)"
        },
        {
            "nom": "Médecin CST - Collectif",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points supplémentaires si ≥ 50% des médecins s'engagent",
            "prorata": 1.0,
            "description": "100 points supplémentaires si ≥ 50% des médecins de la structure s'engagent dans un CST"
        },
        {
            "nom": "Missions de santé publique (1ère mission)",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 350,
            "formule_calcul": "350 × patientele/4000",
            "prorata": 1.0,
            "description": "350 points pour la première mission, proratisés selon la patientèle"
        },
        {
            "nom": "Missions de santé publique (2ème mission)",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 350,
            "formule_calcul": "350 × patientele/4000",
            "prorata": 1.0,
            "description": "350 points pour la deuxième mission, proratisés selon la patientèle"
        },
        {
            "nom": "Missions de santé publique (Bonus)",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": "200 points bonus si ≥ 2 missions réalisées",
            "prorata": 1.0,
            "description": "200 points bonus dès que ≥ 2 missions sont réalisées"
        },
        {
            "nom": "Implication des usagers - Niveau 1",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": "200 points fixes (mise en place d'outils de participation)",
            "prorata": 1.0,
            "description": "200 points niveau 1 (mise en place d'outils de participation)"
        },
        {
            "nom": "Implication des usagers - Niveau 2",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 300,
            "formule_calcul": "300 × patientele/4000",
            "prorata": 1.0,
            "description": "300 points niveau 2 proratisés selon la patientèle"
        },
        {
            "nom": "Soins non programmés & SAS - 100% médecins",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 200,
            "points_variables": 0,
            "formule_calcul": "200 points si tous les médecins participent",
            "prorata": 1.0,
            "description": "200 points niveau 1 (tous les médecins participent au dispositif SAS)"
        },
        {
            "nom": "Soins non programmés & SAS - 50% médecins",
            "axe": "Accès aux soins",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points si ≥ 50% des médecins participent",
            "prorata": 1.0,
            "description": "100 points niveau 2 (≥ 50% des médecins participent au dispositif SAS)"
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
            "formule_calcul": "1000 points si une fonction de coordination est identifiée",
            "prorata": 1.0,
            "description": "Coordination formalisée : 1000 points si une fonction de coordination est identifiée (temps et fiche de poste)."
        },
        {
            "nom": "Fonction de coordination - Variable",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 1700,
            "formule_calcul": "1700 × patientele/4000",
            "prorata": 1.0,
            "description": "Part variable : 1700 points proratisés selon le nombre de patients, afin d'encourager l'augmentation de la patientèle."
        },
        {
            "nom": "Protocoles pluri-professionnels (standard)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points par protocole (max 8)",
            "prorata": 1.0,
            "description": "Protocoles établis : 100 points par protocole, jusqu'à un maximum de 8 (soit 800 points maximum)."
        },
        {
            "nom": "Protocoles pluri-professionnels (avec IPA)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 140,
            "points_variables": 0,
            "formule_calcul": "140 points par protocole (100 + 40 si un IPA est intégré, max 8)",
            "prorata": 1.0,
            "description": "Intégration d'un IPA : 40 points supplémentaires par protocole si un infirmier en pratique avancée est intégré."
        },
        {
            "nom": "Concertation pluri-professionnelle (RCP)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 1000,
            "formule_calcul": "1000 × patientele/4000 si au moins 6 réunions par an",
            "prorata": 1.0,
            "description": "Réunions RCP : 1000 points proratisés si au moins 6 réunions par an sont tenues."
        },
        {
            "nom": "Concertation pluri-professionnelle (Compte-rendu)",
            "axe": "Travail en équipe & coordination",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 points proratisés si compte-rendu formalisé",
            "prorata": 1.0,
            "description": "Étude de situations spécifiques : 200 points proratisés si ces réunions donnent lieu à au moins un compte-rendu formalisé."
        },
        {
            "nom": "Formation de professionnels - 2 stages",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 450,
            "points_variables": 0,
            "formule_calcul": "450 points si ≥ 2 stages/an réalisés",
            "prorata": 1.0,
            "description": "450 points si ≥ 2 stages/an réalisés pour former des jeunes professionnels"
        },
        {
            "nom": "Formation de professionnels - 3e stage",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 225,
            "points_variables": 0,
            "formule_calcul": "225 points supplémentaires pour un 3e stage",
            "prorata": 1.0,
            "description": "225 points supplémentaires pour un 3e stage de formation"
        },
        {
            "nom": "Formation de professionnels - 4e stage",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 225,
            "points_variables": 0,
            "formule_calcul": "225 points supplémentaires pour un 4e stage",
            "prorata": 1.0,
            "description": "225 points supplémentaires pour un 4e stage de formation"
        },
        {
            "nom": "Transmission des données de santé",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 × patientele/4000 si procédure formalisée en place",
            "prorata": 1.0,
            "description": "200 points proratisés selon la patientèle si une procédure formalisée est en place"
        },
        {
            "nom": "Démarche qualité - Niveau 1",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points fixes (diagnostic de maturité)",
            "prorata": 1.0,
            "description": "100 points niveau 1 (diagnostic de maturité)"
        },
        {
            "nom": "Démarche qualité - Niveau 2",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 points proratisés selon la patientèle",
            "prorata": 1.0,
            "description": "200 points niveau 2 proratisés selon la patientèle"
        },
        {
            "nom": "Démarche qualité - Niveau 3",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 300,
            "formule_calcul": "300 points proratisés selon la patientèle",
            "prorata": 1.0,
            "description": "300 points niveau 3 proratisés selon la patientèle"
        },
        {
            "nom": "Protocoles nationaux de coopération",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points fixes",
            "prorata": 1.0,
            "description": "100 points fixes pour les protocoles de coopération non programmée"
        },
        {
            "nom": "Parcours insuffisance cardiaque",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 0,
            "points_variables": 100,
            "formule_calcul": "100 × patientele/4000",
            "prorata": 1.0,
            "description": "100 points proratisés selon la patientèle pour le parcours insuffisance cardiaque"
        },
        {
            "nom": "Parcours surpoids/obésité enfant",
            "axe": "Travail en équipe & coordination",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points fixes",
            "prorata": 1.0,
            "description": "100 points fixes pour le parcours surpoids/obésité de l'enfant"
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
            "formule_calcul": "500 points si dossier patient informatisé labellisé",
            "prorata": 1.0,
            "description": "Labellisation standard : 500 points si la MSP utilise un dossier patient informatisé labellisé."
        },
        {
            "nom": "SI labellisé 'Standard' (ANS) - Variable 16 premiers PS",
            "axe": "Système d'information",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 200,
            "formule_calcul": "200 points pour chacun des 16 premiers professionnels équipés",
            "prorata": 1.0,
            "description": "Part variable équipement : 200 points pour chacun des 16 premiers professionnels équipés"
        },
        {
            "nom": "SI labellisé 'Standard' (ANS) - Variable PS supplémentaires",
            "axe": "Système d'information",
            "type": "socle",
            "points_fixes": 0,
            "points_variables": 150,
            "formule_calcul": "150 points pour chaque professionnel supplémentaire",
            "prorata": 1.0,
            "description": "Part variable équipement : 150 points pour chaque professionnel supplémentaire"
        },
        {
            "nom": "SI 'Avancé'",
            "axe": "Système d'information",
            "type": "optionnel",
            "points_fixes": 100,
            "points_variables": 0,
            "formule_calcul": "100 points fixes pour un niveau labellisé avancé",
            "prorata": 1.0,
            "description": "100 points fixes pour un niveau labellisé 'avancé'"
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
