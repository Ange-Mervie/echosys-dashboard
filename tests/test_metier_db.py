import sqlite3

import pandas as pd
import pytest

from utils.metier_db import (
    SECTEUR_TYPES,
    charger_abonnements,
    charger_collectes,
    charger_evenements,
    charger_passages,
    charger_precollecteurs,
    charger_sacs_bacs,
    charger_secteurs,
    init_db,
    inserer_abonnement,
    inserer_collecte,
    inserer_conteneur,
    inserer_evenement,
    inserer_passage,
    inserer_precollecteur,
    inserer_secteur,
)

TABLES = [
    "secteurs", "abonnements", "precollecteurs",
    "sacs_bacs", "passages", "collectes", "evenements",
]


@pytest.fixture()
def db(tmp_path):
    return tmp_path / "metier_test.db"


def _tables_existantes(db):
    with sqlite3.connect(str(db)) as conn:
        lignes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return {l[0] for l in lignes}


def test_init_creates_sept_tables(db):
    init_db(db)
    assert set(TABLES) <= _tables_existantes(db)


def test_charger_sans_base_retourne_vide(tmp_path):
    db = tmp_path / "absente.db"
    assert charger_secteurs(db).empty


def test_inserer_secteur(db):
    seed_db(db)
    inserer_secteur("Test", "Test", "commercial", 3, "Chef Test", db_path=db)
    df = charger_secteurs(db)
    assert (df["nom"] == "Test").any()


def test_inserer_abonnement(db):
    seed_db(db)
    avant = len(charger_abonnements(db))
    inserer_abonnement(1, "Client Test", "menage", "quotidien",
                       "2026-01-01", "actif", 3500.0, db_path=db)
    df = charger_abonnements(db)
    assert len(df) == avant + 1
    assert df.iloc[-1]["client"] == "Client Test"


def test_inserer_precollecteur(db):
    seed_db(db)
    inserer_precollecteur("Test Precollecteur", 1, "tricycle", 20, 1,
                          "699999999", db_path=db)
    assert (charger_precollecteurs(db)["nom"] == "Test Precollecteur").any()


def test_inserer_conteneur(db):
    seed_db(db)
    inserer_conteneur(3, 1, "bac_240l", 240, "bon", db_path=db)
    df = charger_sacs_bacs(db)
    assert ((df["id_point"] == 3) & (df["type_conteneur"] == "bac_240l")).any()


def test_inserer_passage(db):
    seed_db(db)
    avant = len(charger_passages(db))
    inserer_passage(3, 1, "2026-01-15 08:00:00", 45.0, "realise", db_path=db)
    assert len(charger_passages(db)) == avant + 1


def test_inserer_collecte(db):
    seed_db(db)
    avant = len(charger_collectes(db))
    inserer_collecte(3, "2026-01-15 09:00:00", "precollecte", 800.0, 1,
                     "realisee", 45, db_path=db)
    assert len(charger_collectes(db)) == avant + 1


def test_inserer_evenement(db):
    seed_db(db)
    avant = len(charger_evenements(db))
    inserer_evenement("2026-02-01", "fete", 1, "Fete test", "moyen",
                      "prevu", db_path=db)
    assert len(charger_evenements(db)) == avant + 1
