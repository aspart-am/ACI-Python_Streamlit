# ACI Manager

Application web pour le calcul et la répartition des revenus CPAM d'indicateurs ACI entre associés d'une SISA.

## Fonctionnalités

- **Calcul des revenus ACI** : Calcul automatique des points et des revenus selon les règles conventionnelles
- **Validation des indicateurs** : Interface pour valider/invalider chaque indicateur et calculer les points correspondants
- **Répartition des revenus** : Configuration flexible de la répartition des revenus entre associés
- **Gestion des charges** : Saisie et catégorisation des charges de la SISA
- **Tableau de bord** : Visualisation des revenus, charges et répartition avec graphiques
- **Paramètres personnalisables** : Configuration des paramètres de calcul et des indicateurs

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/ACI-Python_Streamlit.git
   cd ACI-Python_Streamlit
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'application :
   ```bash
   streamlit run app.py
   ```

L'application sera accessible à l'adresse http://localhost:8501 dans votre navigateur.

## Structure de l'application

L'application est organisée en plusieurs modules :

- **Tableau de bord** : Vue d'ensemble des revenus ACI, charges et points validés
- **Gestion des indicateurs** : Validation et configuration des indicateurs ACI
- **Gestion des associés** : Ajout, modification et suppression des associés
- **Répartition des revenus** : Configuration de la répartition des revenus entre associés
- **Gestion des charges** : Saisie et catégorisation des charges de la SISA
- **Paramètres** : Configuration des paramètres de l'application

## Utilisation

### Première utilisation

1. Accédez à l'application via http://localhost:8501
2. Commencez par ajouter des associés dans la page "Gestion des associés"
3. Configurez les paramètres de calcul (patientèle, nombre de PS, etc.) dans la page "Paramètres"
4. Validez les indicateurs ACI dans la page "Gestion des indicateurs"
5. Configurez la répartition des revenus dans la page "Répartition des revenus"
6. Ajoutez les charges de la SISA dans la page "Gestion des charges"
7. Consultez les résultats dans le "Tableau de bord"

### Sauvegarde et restauration des données

L'application utilise une base de données SQLite pour stocker les données. Vous pouvez :

- Exporter la base de données depuis la page "Paramètres > Gestion des données"
- Importer une base de données précédemment exportée
- Réinitialiser la base de données si nécessaire

## Règles de calcul des indicateurs ACI

Les règles de calcul des indicateurs ACI sont basées sur l'Avenant 1 d'Octobre 2022 :

- Chaque indicateur délivre des points (fixes et/ou variables)
- La valeur d'un point est de 7 EUR
- Les indicateurs sont organisés en trois axes :
  1. Accès aux soins
  2. Travail en équipe & coordination
  3. Système d'information
- Les indicateurs socle/prérequis doivent être atteints pour percevoir la rémunération

Pour plus de détails sur les règles de calcul, consultez la documentation officielle de l'Assurance Maladie.

## Licence

Tous droits réservés.
