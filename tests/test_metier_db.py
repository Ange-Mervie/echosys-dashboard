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
