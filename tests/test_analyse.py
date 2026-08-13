import pandas as pd


def _df_echelle():
    return pd.DataFrame(
        {
            "id_point": [0, 1, 2, 3],
            "fillRate": [50.0, 60.0, 70.0, 80.0],
            "fillRate_predit": [60.0, 75.0, 95.0, 95.0],
            "priorite_prediction": ["Moyenne", "Elevée", "Urgente", "Urgente"],
            "risque_debordement": [100.0, 250.0, 900.0, 500.0],
            "nb_signalements_citoyens": [0, 1, 4, 2],
            "nb_plaintes": [0, 0, 2, 1],
        }
    )


def test_analyser_priorites_repartit():
    from utils.analyse import analyser_priorites
    lignes = analyser_priorites(_df_echelle())
    assert any("Urgente" in l for l in lignes)
    assert any("3" in l for l in lignes)


def test_analyser_tendance_capture_hausse():
    from utils.analyse import analyser_tendance
    lignes = analyser_tendance(_df_echelle())
    assert any("+1" in l or "+" in l for l in lignes)


def test_analyser_points_critiques_trouve_pire():
    from utils.analyse import analyser_points_critiques
    lignes = analyser_points_critiques(_df_echelle())
    assert lignes and "900" in lignes[0]


def test_generer_synthese_sur_vide():
    from utils.analyse import generer_synthese
    out = generer_synthese(pd.DataFrame())
    assert out and out[0][1] == "Aucune donnee sur la periode filtree : ajuster les filtres."


def test_generer_synthese_contient_contexte():
    from utils.analyse import generer_synthese
    out = generer_synthese(_df_echelle())
    assert out
    types = {t for t, _ in out}
    assert types & {"alert", "info", "ok"}
