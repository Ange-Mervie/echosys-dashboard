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
