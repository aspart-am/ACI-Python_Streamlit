from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from utils.db_config import Base
import datetime

class Indicateur(Base):
    """Modèle pour les indicateurs ACI."""
    __tablename__ = 'indicateurs'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(255), nullable=False)
    axe = Column(String(50), nullable=False)  # 'Accès aux soins', 'Travail en équipe', 'Système d'information'
    type = Column(String(50), nullable=False)  # 'socle', 'prérequis', 'optionnel'
    points_fixes = Column(Integer, default=0)
    points_variables = Column(Integer, default=0)
    formule_calcul = Column(Text)  # Formule de calcul pour les points variables
    est_valide = Column(Boolean, default=False)
    prorata = Column(Float, default=1.0)  # Prorata à appliquer (entre 0 et 1)
    
    # Relations
    attributions = relationship("Attribution", back_populates="indicateur")
    repartition = relationship("Repartition", back_populates="indicateur", uselist=False)
    
    def __repr__(self):
        return f"<Indicateur(id={self.id}, nom='{self.nom}', axe='{self.axe}', type='{self.type}')>"

class Associe(Base):
    """Modèle pour les associés de la SISA."""
    __tablename__ = 'associes'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    fonction = Column(String(100))
    est_gerant = Column(Boolean, default=False)
    coefficient_majoration = Column(Float, default=1.0)  # Coefficient pour les gérants
    
    # Relations
    attributions = relationship("Attribution", back_populates="associe")
    
    def __repr__(self):
        return f"<Associe(id={self.id}, nom='{self.nom}', prenom='{self.prenom}', fonction='{self.fonction}')>"

class Repartition(Base):
    """Modèle pour définir le mode de répartition d'un indicateur."""
    __tablename__ = 'repartitions'
    
    id = Column(Integer, primary_key=True)
    indicateur_id = Column(Integer, ForeignKey('indicateurs.id'), nullable=False)
    est_commun = Column(Boolean, default=True)  # Si True, partagé entre tous les associés
    mode_repartition = Column(String(50), default='egalitaire')  # 'egalitaire', 'proportionnel', 'personnalise'
    
    # Relations
    indicateur = relationship("Indicateur", back_populates="repartition")
    
    def __repr__(self):
        return f"<Repartition(id={self.id}, indicateur_id={self.indicateur_id}, est_commun={self.est_commun})>"

class Attribution(Base):
    """Modèle pour l'attribution des indicateurs aux associés."""
    __tablename__ = 'attributions'
    
    id = Column(Integer, primary_key=True)
    associe_id = Column(Integer, ForeignKey('associes.id'), nullable=False)
    indicateur_id = Column(Integer, ForeignKey('indicateurs.id'), nullable=False)
    pourcentage = Column(Float, default=0.0)  # Pourcentage attribué à cet associé pour cet indicateur
    
    # Relations
    associe = relationship("Associe", back_populates="attributions")
    indicateur = relationship("Indicateur", back_populates="attributions")
    
    def __repr__(self):
        return f"<Attribution(id={self.id}, associe_id={self.associe_id}, indicateur_id={self.indicateur_id}, pourcentage={self.pourcentage})>"

class Charge(Base):
    """Modèle pour les charges de la SISA."""
    __tablename__ = 'charges'
    
    id = Column(Integer, primary_key=True)
    libelle = Column(String(255), nullable=False)
    montant = Column(Float, nullable=False)
    categorie = Column(String(100))
    date_saisie = Column(Date, default=datetime.datetime.now().date())
    
    def __repr__(self):
        return f"<Charge(id={self.id}, libelle='{self.libelle}', montant={self.montant}, categorie='{self.categorie}')>"

class Parametre(Base):
    """Modèle pour les paramètres système."""
    __tablename__ = 'parametres'
    
    id = Column(Integer, primary_key=True)
    cle = Column(String(100), nullable=False, unique=True)
    valeur = Column(String(255), nullable=False)
    description = Column(Text)
    
    def __repr__(self):
        return f"<Parametre(id={self.id}, cle='{self.cle}', valeur='{self.valeur}')>"

class Patientele(Base):
    """Modèle pour stocker les données de patientèle."""
    __tablename__ = 'patientele'
    
    id = Column(Integer, primary_key=True)
    annee = Column(Integer, nullable=False)
    nombre_patients = Column(Integer, nullable=False)
    date_mise_a_jour = Column(Date, default=datetime.datetime.now().date())
    
    def __repr__(self):
        return f"<Patientele(id={self.id}, annee={self.annee}, nombre_patients={self.nombre_patients})>"

class ProfessionnelSante(Base):
    """Modèle pour les professionnels de santé de la structure."""
    __tablename__ = 'professionnels_sante'
    
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    profession = Column(String(100), nullable=False)
    date_arrivee = Column(Date)
    date_depart = Column(Date)
    est_actif = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ProfessionnelSante(id={self.id}, nom='{self.nom}', prenom='{self.prenom}', profession='{self.profession}')>"
