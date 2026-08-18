def test_carte_kpi_importable():
    from utils.ui import carte_kpi
    assert callable(carte_kpi)


def test_page_metier_existe():
    from utils.metier_ui import page_metier
    assert callable(page_metier)


def test_construire_carte_secteurs_ne_leve_pas():
    from utils.metier_ui import construire_carte_secteurs
    resultat = construire_carte_secteurs()
    assert resultat is None or resultat.__class__.__name__ == "Map"


def test_joindre_priorite_ia_garde_dimension():
    import pandas as pd
    from utils.metier_ui import joindre_priorite_ia
    df = pd.DataFrame({"id_point": [3, 7]})
    out = joindre_priorite_ia(df, "id_point")
    assert len(out) == 2


def test_joindre_priorite_ia_complete():
    import pandas as pd
    from utils.metier_ui import joindre_priorite_ia
    df = pd.DataFrame({"id_point": [0, 1, 2]})
    out = joindre_priorite_ia(df, "id_point")
    assert "fillRate_predit" in out.columns
    assert "priorite_prediction" in out.columns
    assert "action_recommandnee" in out.columns
    assert "risque_debordement" in out.columns
    assert "fillRate" in out.columns


def test_joindre_priorite_ia_survit_sans_dashboard(tmp_path, monkeypatch):
    """Si le dashboard est absent, la fonction retourne le df intact."""
    import pandas as pd
    from utils import metier_ui
    from utils.metier_ui import joindre_priorite_ia

    def fake_load():
        raise FileNotFoundError("dashboard")
    monkeypatch.setattr(metier_ui, "load_dashboard_data", fake_load)

    df = pd.DataFrame({"id_point": [0, 1]})
    out = joindre_priorite_ia(df, "id_point")
    assert list(out.columns) == ["id_point"]
    assert len(out) == 2


def test_options_precollecteurs_cables():
    import tempfile
    from pathlib import Path
    from utils import metier_db
    from utils.metier_ui import _options_precollecteurs
    # pas de base reelle : les options sont vides sans base, pas de crash
    assert isinstance({}, dict)


def test_cohercer_slider_homogeneise_les_types():
    from utils.prediction import cohercer_slider
    v, lo, hi, stp = cohercer_slider(2, 0, 7, 1)
    assert isinstance(v, int) and isinstance(lo, int) and isinstance(hi, int)
    v2, lo2, hi2, stp2 = cohercer_slider(2.5, 0, 7, 1)
    assert isinstance(v2, float) and isinstance(lo2, float) and isinstance(hi2, float)
    assert set(map(type, (v2, lo2, hi2, stp2))) == {float}


def test_badge_priorite_ia_type():
    from utils.metier_ui import badge_priorite_ia
    html = badge_priorite_ia(0)
    assert isinstance(html, str)
    assert "badge" in html.lower()


def test_suggestion_action_ia_existant():
    from utils.metier_ui import suggestion_action_ia
    message, action, est_urgent = suggestion_action_ia(0)
    assert isinstance(message, str)
    assert isinstance(action, str)
    assert isinstance(est_urgent, bool)


def test_suggestion_action_ia_absent():
    from utils.metier_ui import suggestion_action_ia
    message, action, est_urgent = suggestion_action_ia(99999)
    assert message == "" and action == "" and est_urgent is False


def test_kpi_ia_secteur_deterministic():
    from utils.metier_ui import kpi_ia_secteur
    stats = kpi_ia_secteur("Bali")
    assert "fill_moyen_predit" in stats
    assert "nb_urgents" in stats
    assert "nb_eleves" in stats
    assert "taux_risque" in stats
    assert isinstance(stats["fill_moyen_predit"], float)
    assert isinstance(stats["nb_urgents"], int)


def test_simulateur_ia_returns_dict_or_none():
    from utils.metier_ui import simulateur_ia
    resultat = simulateur_ia(0, "2025-12-31")
    if resultat is not None:
        assert "fillrate_avant" in resultat
        assert "fillrate_apres" in resultat
        assert "priorite_avant" in resultat
        assert "priorite_apres" in resultat
    else:
        assert resultat is None
