import os
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Chemin vers le fichier de base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'aci_app.db')

# Création du moteur SQLAlchemy
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

def init_db():
    """Initialise la base de données et crée les tables si elles n'existent pas."""
    Base.metadata.create_all(engine)
    print("Base de données initialisée avec succès.")

def get_session():
    """Retourne une session de base de données."""
    return Session()

def execute_query(query, params=None):
    """Exécute une requête SQL brute."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    
    return result
