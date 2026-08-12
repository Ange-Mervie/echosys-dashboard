"""Base de donnees metier ECOSYS (SQLite).

Tables : secteurs, abonnements, precollecteurs, sacs_bacs, passages,
collectes, evenements. Toutes les fonctions acceptent un chemin de base
optionnel pour permettre les tests sans toucher a la base reelle.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "ecosys.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS secteurs (
    id_secteur INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    quartiers TEXT,
    type_secteur TEXT,
    nb_points INTEGER,
    responsable TEXT
);
CREATE TABLE IF NOT EXISTS abonnements (
    id_abonnement INTEGER PRIMARY KEY AUTOINCREMENT,
    id_secteur INTEGER NOT NULL,
    client TEXT,
    type_abonnement TEXT,
    frequence TEXT,
    date_debut TEXT,
    statut TEXT,
    montant_mensuel REAL
);
CREATE TABLE IF NOT EXISTS precollecteurs (
    id_precollecteur INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    id_secteur INTEGER NOT NULL,
    equipement TEXT,
    capacite_sacs INTEGER,
    disponible INTEGER,
    telephone TEXT
);
CREATE TABLE IF NOT EXISTS sacs_bacs (
    id_conteneur INTEGER PRIMARY KEY AUTOINCREMENT,
    id_point INTEGER,
    id_secteur INTEGER NOT NULL,
    type_conteneur TEXT,
    capacite_litres INTEGER,
    etat TEXT
);
CREATE TABLE IF NOT EXISTS passages (
    id_passage INTEGER PRIMARY KEY AUTOINCREMENT,
    id_point INTEGER,
    id_precollecteur INTEGER,
    date_passage TEXT,
    quantite_kg REAL,
    statut TEXT
);
CREATE TABLE IF NOT EXISTS collectes (
    id_collecte INTEGER PRIMARY KEY AUTOINCREMENT,
    id_point INTEGER,
    date_collecte TEXT,
    type_collecte TEXT,
    volume_litres REAL,
    id_precollecteur INTEGER,
    statut TEXT,
    duree_minutes INTEGER
);
CREATE TABLE IF NOT EXISTS evenements (
    id_evenement INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    type_evenement TEXT,
    id_secteur INTEGER,
    description TEXT,
    impact TEXT,
    statut TEXT
);
"""

SECTEUR_TYPES = {
    "Akwa": "commercial",
    "Bali": "marche",
    "Bekoko": "residentiel",
    "Bessengue": "commercial",
    "Bonaberi": "mixte",
    "Bonanjo": "commercial",
    "Cite SIC": "residentiel",
    "Deido": "mixte",
    "Grand Hangar": "marche",
    "Kotto": "mixte",
    "Logbaba": "residentiel",
    "Ndogpassi": "residentiel",
    "New Bell": "mixte",
    "Nylon": "marche",
    "PK14": "mixte",
}

INT2Q = {
    0: "Bali", 1: "Grand Hangar", 2: "Logbaba", 3: "Bekoko", 4: "Ndogpassi",
    5: "Bonaberi", 6: "Grand Hangar", 7: "Bonaberi", 8: "Logbaba", 9: "Bali",
    10: "Kotto", 11: "Logbaba", 12: "New Bell", 13: "Nylon", 14: "New Bell",
    15: "Bessengue", 16: "Bonaberi", 17: "Deido", 18: "Akwa", 19: "Logbaba",
    20: "Deido", 21: "Logbaba", 22: "New Bell", 23: "Kotto", 24: "Bessengue",
    25: "Deido", 26: "Ndogpassi", 27: "Bali", 28: "Grand Hangar", 29: "Kotto",
    30: "Bekoko", 31: "Nylon", 32: "PK14", 33: "Bali", 34: "Bonaberi",
    35: "Bekoko", 36: "New Bell", 37: "Bali", 38: "Ndogpassi", 39: "Cite SIC",
    40: "Kotto", 41: "Kotto", 42: "Bessengue", 43: "Deido", 44: "Logbaba",
    45: "Bali", 46: "PK14", 47: "Akwa", 48: "Nylon", 49: "PK14",
    50: "Bonanjo", 51: "Bali", 52: "Bessengue", 53: "New Bell", 54: "PK14",
    55: "Ndogpassi", 56: "Bonanjo", 57: "Grand Hangar", 58: "Grand Hangar",
    59: "Ndogpassi", 60: "Akwa", 61: "PK14", 62: "Bekoko", 63: "Akwa",
    64: "Bessengue", 65: "Nylon", 66: "Nylon", 67: "Akwa", 68: "Cite SIC",
    69: "Logbaba", 70: "Bonaberi", 71: "PK14", 72: "Nylon", 73: "Bonaberi",
    74: "Deido", 75: "Grand Hangar", 76: "Ndogpassi", 77: "Bonaberi",
    78: "Kotto", 79: "Cite SIC",
}

PRE_PAR_SECTEUR = {
    "Akwa": 7, "Bali": 6, "Bekoko": 7, "Bessengue": 7, "Bonaberi": 7,
    "Bonanjo": 6, "Cite SIC": 7, "Deido": 7, "Grand Hangar": 7, "Kotto": 7,
    "Logbaba": 7, "Ndogpassi": 6, "New Bell": 6, "Nylon": 7, "PK14": 7,
}


def _connect(db_path=None):
    db_path = Path(db_path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    db_path = Path(db_path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(db_path)) as conn:
        conn.executescript(SCHEMA_SQL)


def charger_table(nom_table, db_path=None):
    db_path = Path(db_path or DB_PATH)
    if not db_path.exists():
        return pd.DataFrame()
    with closing(_connect(db_path)) as conn:
        return pd.read_sql_query(f"SELECT * FROM {nom_table}", conn)


def charger_secteurs(db_path=None):
    return charger_table("secteurs", db_path)


def charger_abonnements(db_path=None):
    return charger_table("abonnements", db_path)


def charger_precollecteurs(db_path=None):
    return charger_table("precollecteurs", db_path)


def charger_sacs_bacs(db_path=None):
    return charger_table("sacs_bacs", db_path)


def charger_passages(db_path=None):
    return charger_table("passages", db_path)


def charger_collectes(db_path=None):
    return charger_table("collectes", db_path)


def charger_evenements(db_path=None):
    return charger_table("evenements", db_path)
