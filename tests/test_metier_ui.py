def test_carte_kpi_importable():
    from utils.ui import carte_kpi
    assert callable(carte_kpi)


def test_page_metier_existe():
    from utils.metier_ui import page_metier
    assert callable(page_metier)
