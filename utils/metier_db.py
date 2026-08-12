"""Base de donnees metier ECOSYS (SQLite).

Tables : secteurs, abonnements, precollecteurs, sacs_bacs, passages,
collectes, evenements. Toutes les fonctions acceptent un chemin de base
optionnel pour permettre les tests sans toucher a la base reelle.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

NOMS = [
    "Mbarga", "Ngassa", "Atangana", "Kamga", "Tchoupo", "Fokou", "Djoumessi",
    "Etoa", "Nkoulou", "Manga", "Essomba", "Nguema", "Owona", "Belinga",
    "Toukam", "Fotso", "Talla", "Mfouapon", "Ndongo", "Abena", "Beyala",
    "Ekotto", "Wandji", "Kameni", "Mballa", "Essama", "Onguene", "Sack",
    "Tatah", "Njoya",
]

PRENOMS = [
    "Jean", "Marie", "Paul", "Joseph", "Madeleine", "Andre", "Claire",
    "Simon", "Angèle", "Charles", "Emmanuel", "Viviane", "Alain", "Berthe",
    "Eric", "Francine", "Gaston", "Helene", "Igor", "Justine", "Landry",
    "Mireille", "Narcisse", "Odile", "Patrice", "Rachel", "Serge",
    "Therese", "Ulysse", "Valerie",
]

ENTREPRISES = [
    "Ets. Ndom & Fils", "SARL Belle Vue", "Boulangerie de l'Akwa",
    "Restaurant Le Rond Point", "Supermarché Baobab", "Ets. Manga Distribution",
    "Quincaillerie Bonanjo", "Hotel Rive Gauche", "Ecole La Gaiete",
    "Clinique St Jean", "Ets. Wandji Freres", "Cafe de Nylon",
    "Boutique Bessengue", "Poissonnerie Grand Hangar", "Ets. Kamga Autos",
]

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


def inserer_secteur(nom, quartiers, type_secteur, nb_points, responsable,
                    db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO secteurs (nom, quartiers, type_secteur, nb_points, responsable) "
            "VALUES (?,?,?,?,?)",
            (nom, quartiers, type_secteur, nb_points, responsable),
        )


def inserer_abonnement(id_secteur, client, type_abonnement, frequence,
                       date_debut, statut, montant_mensuel, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO abonnements (id_secteur, client, type_abonnement, frequence, "
            "date_debut, statut, montant_mensuel) VALUES (?,?,?,?,?,?,?)",
            (id_secteur, client, type_abonnement, frequence, date_debut,
             statut, montant_mensuel),
        )


def inserer_precollecteur(nom, id_secteur, equipement, capacite_sacs,
                          disponible, telephone, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO precollecteurs (nom, id_secteur, equipement, capacite_sacs, "
            "disponible, telephone) VALUES (?,?,?,?,?,?)",
            (nom, id_secteur, equipement, capacite_sacs, disponible, telephone),
        )


def inserer_conteneur(id_point, id_secteur, type_conteneur, capacite_litres,
                      etat, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO sacs_bacs (id_point, id_secteur, type_conteneur, "
            "capacite_litres, etat) VALUES (?,?,?,?,?)",
            (id_point, id_secteur, type_conteneur, capacite_litres, etat),
        )


def inserer_passage(id_point, id_precollecteur, date_passage, quantite_kg,
                    statut, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO passages (id_point, id_precollecteur, date_passage, "
            "quantite_kg, statut) VALUES (?,?,?,?,?)",
            (id_point, id_precollecteur, date_passage, quantite_kg, statut),
        )


def inserer_collecte(id_point, date_collecte, type_collecte, volume_litres,
                     id_precollecteur, statut, duree_minutes, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO collectes (id_point, date_collecte, type_collecte, "
            "volume_litres, id_precollecteur, statut, duree_minutes) "
            "VALUES (?,?,?,?,?,?,?)",
            (id_point, date_collecte, type_collecte, volume_litres,
             id_precollecteur, statut, duree_minutes),
        )


def inserer_evenement(date, type_evenement, id_secteur, description, impact,
                      statut, db_path=None):
    db_path = Path(db_path or DB_PATH)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(
            "INSERT INTO evenements (date, type_evenement, id_secteur, "
            "description, impact, statut) VALUES (?,?,?,?,?,?)",
            (date, type_evenement, id_secteur, description, impact, statut),
        )


def seed_db(db_path=None):
    """Remplit la base avec des donnees simulees deterministes.

    Retourne True si la base vient d'etre peuplee, False si elle etait
    deja remplie (idempotent).
    """
    db_path = Path(db_path or DB_PATH)
    init_db(db_path)
    with closing(_connect(db_path)) as conn:
        nb = conn.execute("SELECT COUNT(*) FROM secteurs").fetchone()[0]
    if nb > 0:
        return False

    import numpy as np

    rng = np.random.default_rng(2026)
    jour_debut = pd.Timestamp("2024-07-01")
    jour_fin = pd.Timestamp("2025-12-31")
    nb_jours = (jour_fin - jour_debut).days
    ids_secteurs = {}

    with closing(_connect(db_path)) as conn, conn:
        # ---- secteurs
        for nom, type_s in SECTEUR_TYPES.items():
            pts = [p for p, q in INT2Q.items() if q == nom]
            resp = f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"
            cur = conn.execute(
                "INSERT INTO secteurs (nom, quartiers, type_secteur, nb_points, "
                "responsable) VALUES (?,?,?,?,?)",
                (nom, nom, type_s, len(pts), resp),
            )
            ids_secteurs[nom] = cur.lastrowid

        # ---- precollecteurs
        rows = []
        for nom, n in PRE_PAR_SECTEUR.items():
            for _ in range(n):
                rows.append((
                    f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}",
                    ids_secteurs[nom],
                    str(rng.choice(["tricycle", "chariot", "pousse_pousse"],
                                   p=[0.40, 0.35, 0.25])),
                    int(rng.integers(10, 31)),
                    int(rng.integers(0, 2)),
                    f"6{rng.integers(10000000, 99999999)}",
                ))
        conn.executemany(
            "INSERT INTO precollecteurs (nom, id_secteur, equipement, "
            "capacite_sacs, disponible, telephone) VALUES (?,?,?,?,?,?)",
            rows,
        )

        # id des precollecteurs par secteur (pour passages / collectes)
        pc_par_secteur = {}
        for pc_id, sect_id in conn.execute(
            "SELECT id_precollecteur, id_secteur FROM precollecteurs"
        ).fetchall():
            pc_par_secteur.setdefault(sect_id, []).append(pc_id)

        # ---- abonnements (1000)
        rows = []
        for _ in range(1000):
            nom_secteur = str(rng.choice(list(ids_secteurs.keys())))
            sid = ids_secteurs[nom_secteur]
            type_ab = str(rng.choice(["menage", "entreprise", "commerce"],
                                     p=[0.70, 0.15, 0.15]))
            if type_ab == "menage":
                client = f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"
                montant = int(rng.integers(2500, 5001))
            elif type_ab == "entreprise":
                client = str(rng.choice(ENTREPRISES))
                montant = int(rng.integers(15000, 60001))
            else:
                client = f"{rng.choice(PRENOMS)} {rng.choice(NOMS)}"
                montant = int(rng.integers(8000, 25001))
            debut = jour_debut - pd.Timedelta(
                days=int(rng.integers(0, 700)), hours=int(rng.integers(0, 24))
            )
            rows.append((
                sid, client, type_ab,
                str(rng.choice(["quotidien", "hebdomadaire", "sur_appel"],
                               p=[0.60, 0.30, 0.10])),
                debut.strftime("%Y-%m-%d"),
                str(rng.choice(["actif", "suspendu", "expire"],
                               p=[0.75, 0.15, 0.10])),
                float(montant),
            ))
        conn.executemany(
            "INSERT INTO abonnements (id_secteur, client, type_abonnement, "
            "frequence, date_debut, statut, montant_mensuel) "
            "VALUES (?,?,?,?,?,?,?)",
            rows,
        )

        # ---- sacs_bacs (250)
        rows = []
        for _ in range(250):
            pid = int(rng.integers(0, 80))
            sid = ids_secteurs[INT2Q[pid]]
            tc = str(rng.choice(["sac_100l", "bac_240l", "benne"],
                                p=[0.30, 0.40, 0.30]))
            if tc == "benne":
                cap = int(rng.choice([1100, 1500, 5000, 10000, 30000]))
            else:
                cap = 100 if tc == "sac_100l" else 240
            rows.append((pid, sid, tc, cap,
                         str(rng.choice(["bon", "use", "endommage"],
                                        p=[0.70, 0.20, 0.10]))))
        conn.executemany(
            "INSERT INTO sacs_bacs (id_point, id_secteur, type_conteneur, "
            "capacite_litres, etat) VALUES (?,?,?,?,?)",
            rows,
        )

        # ---- passages (3000)
        rows = []
        for _ in range(3000):
            pid = int(rng.integers(0, 80))
            sid = ids_secteurs[INT2Q[pid]]
            pc = int(rng.choice(pc_par_secteur[sid]))
            d = jour_debut + pd.Timedelta(
                days=int(rng.integers(0, nb_jours + 1)),
                hours=int(rng.integers(5, 20)),
                minutes=int(rng.integers(0, 60)),
            )
            rows.append((
                pid, pc, d.strftime("%Y-%m-%d %H:%M:%S"),
                float(round(rng.uniform(10, 150), 1)),
                str(rng.choice(["realise", "retarde", "annule"],
                               p=[0.80, 0.12, 0.08])),
            ))
        conn.executemany(
            "INSERT INTO passages (id_point, id_precollecteur, date_passage, "
            "quantite_kg, statut) VALUES (?,?,?,?,?)",
            rows,
        )

        # ---- collectes (1500)
        rows = []
        for _ in range(1500):
            pid = int(rng.integers(0, 80))
            sid = ids_secteurs[INT2Q[pid]]
            pc = int(rng.choice(pc_par_secteur[sid]))
            tc = str(rng.choice(["precollecte", "principale"], p=[0.70, 0.30]))
            if tc == "precollecte":
                vol = int(rng.integers(200, 2001))
            else:
                vol = int(rng.integers(2000, 30001))
            d = jour_debut + pd.Timedelta(
                days=int(rng.integers(0, nb_jours + 1)),
                hours=int(rng.integers(6, 18)),
            )
            rows.append((
                pid, d.strftime("%Y-%m-%d %H:%M:%S"), tc, float(vol), pc,
                str(rng.choice(["realisee", "planifiee", "annulee"],
                               p=[0.75, 0.15, 0.10])),
                int(rng.integers(20, 121)),
            ))
        conn.executemany(
            "INSERT INTO collectes (id_point, date_collecte, type_collecte, "
            "volume_litres, id_precollecteur, statut, duree_minutes) "
            "VALUES (?,?,?,?,?,?,?)",
            rows,
        )

        # ---- evenements (30)
        descriptions = {
            "marche": "Journee de marche hebdomadaire",
            "fete": "Fete de quartier",
            "evenement_sportif": "Evenement sportif local",
            "incident": "Incident sur point de regroupement",
            "alerte": "Alerte debordement signalee",
        }
        types_ev = list(descriptions.keys())
        rows = []
        for _ in range(30):
            te = str(rng.choice(types_ev))
            sid = ids_secteurs[list(ids_secteurs.keys())[
                int(rng.integers(0, len(ids_secteurs)))]]
            d = jour_fin - pd.Timedelta(days=int(rng.integers(0, 365)))
            rows.append((
                d.strftime("%Y-%m-%d"), te, sid, descriptions[te],
                str(rng.choice(["haut", "moyen", "faible"],
                               p=[0.25, 0.45, 0.30])),
                str(rng.choice(["prevu", "en_cours", "termine"],
                               p=[0.25, 0.15, 0.60])),
            ))
        conn.executemany(
            "INSERT INTO evenements (date, type_evenement, id_secteur, "
            "description, impact, statut) VALUES (?,?,?,?,?,?)",
            rows,
        )
    return True


def stats_metier(db_path=None):
    db_path = Path(db_path or DB_PATH)
    stats = {
        "secteurs": 0, "abonnements": 0, "abonnements_actifs": 0,
        "precollecteurs": 0, "precollecteurs_dispo": 0,
        "conteneurs": 0, "conteneurs_endommages": 0,
        "passages": 0, "passages_retardes": 0,
        "collectes": 0, "collectes_realisees": 0,
        "evenements": 0, "evenements_haut_impact": 0,
    }
    if not db_path.exists():
        return stats
    requetes = {
        "secteurs": "SELECT COUNT(*) FROM secteurs",
        "abonnements": "SELECT COUNT(*) FROM abonnements",
        "abonnements_actifs": "SELECT COUNT(*) FROM abonnements WHERE statut='actif'",
        "precollecteurs": "SELECT COUNT(*) FROM precollecteurs",
        "precollecteurs_dispo": "SELECT COUNT(*) FROM precollecteurs WHERE disponible=1",
        "conteneurs": "SELECT COUNT(*) FROM sacs_bacs",
        "conteneurs_endommages": "SELECT COUNT(*) FROM sacs_bacs WHERE etat='endommage'",
        "passages": "SELECT COUNT(*) FROM passages",
        "passages_retardes": "SELECT COUNT(*) FROM passages WHERE statut='retarde'",
        "collectes": "SELECT COUNT(*) FROM collectes",
        "collectes_realisees": "SELECT COUNT(*) FROM collectes WHERE statut='realisee'",
        "evenements": "SELECT COUNT(*) FROM evenements",
        "evenements_haut_impact": "SELECT COUNT(*) FROM evenements WHERE impact='haut'",
    }
    with closing(_connect(db_path)) as conn:
        for cle, sql in requetes.items():
            stats[cle] = conn.execute(sql).fetchone()[0]
    return stats
