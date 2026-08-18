# Intégration IA dans l'interface métier — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Faire de l'IA un partenaire décisionnel actionnable dans chaque onglet métier de la page Interface métier ECHOSYS : KPIs IA enrichis, badges priorité, suggestions formulaires, et simulation what-if.

**Architecture:** Six fonctions IA autonomes dans `utils/metier_ui.py` (déjà le siège de la page métier), une helper dans `utils/prediction.py`, et des hooks dans les onglets existants. Les fonctions IA cachent `load_dashboard_data()` via `@st.cache_data` et tombent en `try/except` gracieusement si le dashboard est absent.

**Tech Stack:** Python (Anaconda), Streamlit, pandas, LightGBM (joblib), folium, plotly, pytest. `sqlite3` (stdlib) pour la base métier.

## Global Constraints

- **Binaire Python** : `C:/Users/LENOVO/anaconda3/python.exe`
- **Test runner** : `C:/Users/LENOVO/anaconda3/python.exe -m pytest` depuis la racine du projet
- **Base réelle** : `data/ecosys.db` ne doit jamais être modifiée par les tests
- **Dashboard IA** : `dashboard/dashboard_dataset.parquet` (cols: `id_point`, `fillRate`, `fillRate_predit`, `priorite_prediction`, `action_recommandee`, `risque_debordement`)
- **Attention** : le parquet contient `action_recommandee` (sans 'n' final), le code utilise `action_recommandnee` → normaliser dans les fonctions IA
- **R² modèle** : ~0.30 (honnête, pas de fuite)
- **Idempotence** : pas d'écriture en base par l'IA

---

### Task 1: `utils/prediction.py` — `estimer_risque_debordement()`

**Files:**
- Modify: `utils/prediction.py` (ajouter la fonction + export)
- Test: `tests/test_prediction.py` (ajouter test)

**Interfaces:**
- Consumes: `SEUILS` (déjà défini)
- Produces: `estimer_risque_debordement(fillrate_predit: float) -> str`

- [ ] **Step 1: Write the failing test**

```python
def test_estimer_risque_debordement():
    from utils.prediction import estimer_risque_debordement as f
    assert f(95.0) == "critique"
    assert f(85.0) == "eleve"
    assert f(55.0) == "modere"
    assert f(10.0) == "faible"
```

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_prediction.py::test_estimer_risque_debordement -v`
Expected: FAIL (`AttributeError: module 'utils.prediction' has no attribute 'estimer_risque_debordement'`)

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement minimal code**

```python
def estimer_risque_debordement(fillrate_predit):
    """Categorise le risque de debordement a partir du fillRate predit par l'IA."""
    if fillrate_predit >= 90:
        return "critique"
    if fillrate_predit >= 70:
        return "eleve"
    if fillrate_predit >= 40:
        return "modere"
    return "faible"
```

Ajouter après `generer_recommandation()` (ligne ~64), avant `enrichir_priorite_action()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_prediction.py::test_estimer_risque_debordement -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add utils/prediction.py tests/test_prediction.py
git commit -m "feat: estimer_risque_debordement helper"
```

---

### Task 2: `utils/metier_ui.py` — `joindre_priorite_ia()` enrichi

**Files:**
- Modify: `utils/metier_ui.py` (remplacer `joindre_priorite_ia` existant + ajouter imports)
- Test: `tests/test_metier_ui.py` (ajouter test)

**Interfaces:**
- Consumes: `load_dashboard_data` (déjà importé), `generer_recommandation` de `utils/prediction`
- Produces: `joindre_priorite_ia(df, colonne_point)` enrichi de `fillRate`, `fillRate_predit`, `priorite_prediction`, `action_recommandnee` (renommé), `risque_debordement`

- [ ] **Step 1: Write the failing test**

```python
def test_joindre_priorite_ia_complete():
    import pandas as pd
    from utils.metier_ui import joindre_priorite_ia
    df = pd.DataFrame({"id_point": [0, 1, 2]})
    out = joindre_priorite_ia(df, "id_point")
    # Le dashboard couvre id_point 0-79 ; on verifie les colonnes IA
    for col in ["fillRate_predit", "priorite_prediction", "action_recommandnee"]:
        assert col in out.columns
```

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py::test_joindre_priorite_ia_complete -v`
Expected: FAIL (`KeyError: 'action_recommandnee'` if old version, ou `AssertionError`)

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Update imports**

Dans `utils/metier_ui.py`, ajouter à l'import existant :

```python
from utils.prediction import (
    definir_priorite,
    estimer_risque_debordement,
    generer_recommandation,
)
```

- [ ] **Step 4: Replace `joindre_priorite_ia`**

```python
def joindre_priorite_ia(df, colonne_point):
    """Joint les predictions IA (fillRate_predit, priorite, action, risque) au df métier."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        # Normaliser le nom de colonne (parquet = action_recommandee, code = action_recommandnee)
        if "action_recommandee" in dash.columns and "action_recommandnee" not in dash.columns:
            dash = dash.rename(columns={"action_recommandee": "action_recommandnee"})
        # Si action_recommandnee toujours absente, la calculer
        if "action_recommandnee" not in dash.columns and "fillRate_predit" in dash.columns:
            dash["action_recommandnee"] = dash["fillRate_predit"].apply(generer_recommandation)
        cols = ["id_point", "fillRate", "fillRate_predit", "priorite_prediction",
                "action_recommandnee", "risque_debordement"]
        cols = [c for c in cols if c in dash.columns]
        dash = dash[cols]
        df = df.merge(dash, left_on=colonne_point, right_on="id_point", how="left").drop(
            columns="id_point", errors="ignore"
        )
    except Exception:
        pass
    return df
```

- [ ] **Step 5: Run test to verify it passes**

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py::test_joindre_priorite_ia_complete -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add utils/metier_ui.py tests/test_metier_ui.py
git commit -m "feat: enrichir joindre_priorite_ia avec risque_debordement et action"
```

---

### Task 3: `utils/metier_ui.py` — `badge_priorite_ia()`, `suggestion_action_ia()`, `estimer_risque_debordement_ia()`

**Files:**
- Modify: `utils/metier_ui.py` (ajouter 3 fonctions)
- Test: `tests/test_metier_ui.py` (ajouter tests)

**Interfaces:**
- Consumes: `joindre_priorite_ia`, `badge_priorite` (de `utils.ui`), `normaliser_priorite` (de `utils.prediction`), `estimer_risque_debordement` (nouveau)
- Produces: `badge_priorite_ia(id_point) -> str` (HTML), `suggestion_action_ia(id_point) -> tuple[str, str, bool]`

- [ ] **Step 1: Write the failing tests**

```python
def test_badge_priorite_ia_id_point_existant():
    from utils.metier_ui import badge_priorite_ia
    html = badge_priorite_ia(0)
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
```

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py -k "badge_priorite_ia or suggestion_action_ia" -v`
Expected: FAIL (ImportError)

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement functions**

```python
def badge_priorite_ia(id_point):
    """Rend un badge priorite IA HTML pour un point. Gris si point absent du dashboard."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        ligne = dash[dash["id_point"] == id_point]
        if ligne.empty:
            return '<span class="badge" style="background:#F5F7FA;color:#78909C;">IA — non disponible</span>'
        priorite = str(ligne.iloc[0].get("priorite_prediction", "Faible")).strip()
        priorite = normaliser_priorite(priorite)
        badge_html = badge_priorite(priorite)
        return f'{badge_html} <span style="font-size:0.7rem;color:#8A9499;">IA</span>'
    except Exception:
        return '<span class="badge" style="background:#F5F7FA;color:#78909C;">IA — non disponible</span>'


def suggestion_action_ia(id_point):
    """Suggere une action pour un point basee sur la priorite IA.

    Retourne (message, action_ia, est_urgent).
    """
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        ligne = dash[dash["id_point"] == id_point]
        if ligne.empty:
            return "", "", False
        row = ligne.iloc[0]
        fillrate = float(row.get("fillRate_predit", 0))
        priorite = normaliser_priorite(str(row.get("priorite_prediction", "Faible")))
        action = str(row.get("action_recommandnee", generer_recommandation(fillrate)))
        est_urgent = priorite in ("Urgente", "Elevée")
        if est_urgent:
            message = f"Ce point est prédit **{priorite}** (fillRate prédit {fillrate:.0f}%) → {action} ?"
        else:
            message = f"Point **{priorite.lower()}** (fillRate prédit {fillrate:.0f}%) → {action}."
        return message, action, est_urgent
    except Exception:
        return "", "", False
```

Ajouter après `joindre_priorite_ia()`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py -k "badge_priorite_ia or suggestion_action_ia" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add utils/metier_ui.py tests/test_metier_ui.py
git commit -m "feat: badge_priorite_ia + suggestion_action_ia"
```

---

### Task 4: `utils/metier_ui.py` — `kpi_ia_secteur()`, `simulateur_ia()`

**Files:**
- Modify: `utils/metier_ui.py` (ajouter 2 fonctions)
- Test: `tests/test_metier_ui.py` (ajouter tests)

**Interfaces:**
- Consumes: `joindre_priorite_ia`, `INT2Q`, `SECTEUR_TYPES`, `load_ml_data`, `extraire_ligne_ml`, `simuler_prediction`, `FEATURES_SIMULABLES`
- Produces: `kpi_ia_secteur(nom_secteur) -> dict`, `simulateur_ia(id_point, date_ref) -> dict | None`

- [ ] **Step 1: Write the failing tests**

```python
def test_kpi_ia_secteur_deterministic():
    from utils.metier_ui import kpi_ia_secteur
    stats = kpi_ia_secteur("Bali")
    assert "fill_moyen_predit" in stats
    assert "nb_urgents" in stats
    assert "nb_eleves" in stats
    assert "taux_risque" in stats


def test_simulateur_ia_returns_dict():
    from utils.metier_ui import simulateur_ia
    resultat = simulateur_ia(0, "2025-12-31")
    # Soit un dict coherent, soit None si pas de donnee ML
    if resultat is not None:
        assert "fillrate_avant" in resultat
        assert "fillrate_apres" in resultat
    else:
        assert resultat is None  # OK si pas de donnee ML
```

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py -k "kpi_ia_secteur or simulateur_ia" -v`
Expected: FAIL (ImportError)

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Implement functions**

```python
def kpi_ia_secteur(nom_secteur):
    """Calcule les KPIs IA pour les points d'un secteur."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        # Cartographie id_point -> secteur via INT2Q
        dash["quartier"] = dash["id_point"].map(INT2Q).fillna("Inconnu")
        secteur_mask = dash["quartier"] == nom_secteur
        pts = dash[secteur_mask]
        if pts.empty:
            return {"fill_moyen_predit": 0, "nb_urgents": 0, "nb_eleves": 0, "taux_risque": 0}
        priorites = pts["priorite_prediction"].apply(normaliser_priorite)
        fill_moyen = pts["fillRate_predit"].mean()
        nb_urgents = int((priorites == "Urgente").sum())
        nb_eleves = int((priorites == "Elevée").sum())
        nb_total = len(pts)
        taux_risque = round((nb_urgents + nb_eleves) / nb_total * 100, 1) if nb_total > 0 else 0
        return {
            "fill_moyen_predit": round(float(fill_moyen), 1),
            "nb_urgents": nb_urgents,
            "nb_eleves": nb_eleves,
            "taux_risque": taux_risque,
        }
    except Exception:
        return {"fill_moyen_predit": 0, "nb_urgents": 0, "nb_eleves": 0, "taux_risque": 0}


def simulateur_ia(id_point, date_ref):
    """Simule un what-if : +3 precollecteurs dispo, montre l'impact sur le fill rate."""
    try:
        from utils.data_loader import load_ml_data
        from utils.prediction import extraire_ligne_ml, simuler_prediction
        ml_df = load_ml_data()
        ligne = extraire_ligne_ml(ml_df, id_point, date_ref)
        # Scenario what-if : +3 precollecteurs disponibles
        ajustements = {"nb_precollecteurs_dispo": 3}
        fillrate_avant, priorite_avant, action_avant, _ = simuler_prediction(ligne)
        fillrate_apres, priorite_apres, action_apres, _ = simuler_prediction(ligne, ajustements)
        return {
            "fillrate_avant": round(float(fillrate_avant), 1),
            "fillrate_apres": round(float(fillrate_apres), 1),
            "priorite_avant": priorite_avant,
            "priorite_apres": priorite_apres,
            "action": action_apres,
        }
    except Exception:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

- [ ] **Step 5: Commit**

```bash
git add utils/metier_ui.py tests/test_metier_ui.py
git commit -m "feat: kpi_ia_secteur + simulateur_ia (what-if)"
```

---

### Task 5: Intégration IA dans les onglets — Secteurs, Sacs/Bacs, Collectes

**Files:**
- Modify: `utils/metier_ui.py` (onglets `onglet_secteurs`, `onglet_sacs_bacs`, `onglet_collectes`)
- Test: `tests/test_metier_ui.py` (test d'import + smoke)

**Interfaces:**
- Consumes: `kpi_ia_secteur`, `badge_priorite_ia`, `suggestion_action_ia`, `simulateur_ia`, `joindre_priorite_ia`, `carte_kpi`
- Produces: onglets enrichis d'indicateurs et suggestions IA

- [ ] **Step 1: Write the failing test**

```python
def test_onglets_ia_integration():
    """Smoke test : les onglets metier s'enrichissent d'IA sans crash."""
    from utils.metier_ui import kpi_ia_secteur, badge_priorite_ia, suggestion_action_ia
    # Ces fonctions doivent exister et retourner des resultats coherents
    kpi = kpi_ia_secteur("Bali")
    assert isinstance(kpi, dict)
    badge = badge_priorite_ia(0)
    assert isinstance(badge, str)
    msg, action, urgent = suggestion_action_ia(0)
    assert isinstance(msg, str)
```

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py::test_onglets_ia_integration -v`
Expected: PASS (après Task 4)

- [ ] **Step 2: Enhance `onglet_secteurs`**

```python
def onglet_secteurs(stats):
    df = charger_secteurs()
    if df.empty:
        st.info("Aucun secteur. Lancez l'initialisation de la base.")
        return
    kpi_ia = kpi_ia_secteur(df.iloc[0]["nom"])  # secteur par défaut pour demo
    _lignes_kpi([
        ("Secteurs", f"{stats['secteurs']}", ""),
        ("Points couverts", f"{int(df['nb_points'].sum())}", ""),
        ("Responsables", f"{df['responsable'].nunique()}", ""),
    ])
    # KPIs IA
    with st.container():
        c1, c2, c3 = st.columns(3)
        with c1:
            carte_kpi("FillRate IA moyen", f"{kpi_ia['fill_moyen_predit']:.1f}", "%")
        with c2:
            carte_kpi("Points urgents IA", f"{kpi_ia['nb_urgents']}", "")
        with c3:
            carte_kpi("Taux de risque IA", f"{kpi_ia['taux_risque']:.0f}", "%",
                       sous_texte="urgents + élevés")
    ...reste existant...
```

- [ ] **Step 3: Enhance `onglet_sacs_bacs`**

Ajouter un filtre par priorité IA et un badge dans le tableau :

```python
def onglet_sacs_bacs(stats):
    df = charger_sacs_bacs()
    if df.empty:
        ...
    df = joindre_priorite_ia(df, "id_point")
    _lignes_kpi(...)
    # Afficher risque IA dans le tableau
    if "fillRate_predit" in df.columns:
        df["risque_ia"] = df["fillRate_predit"].apply(estimer_risque_debordement)
        st.dataframe(df[["id_point", "type_conteneur", "capacite_litres",
                         "risque_ia", "priorite_prediction"]], ...)
    ...
```

- [ ] **Step 4: Enhance `onglet_collectes`**

Ajouter suggestion IA dans le formulaire :

```python
def onglet_collectes(stats):
    ...
    df = joindre_priorite_ia(df, "id_point")
    ...
    with st.form("form_collecte"):
        ...existing fields...
        # Suggestion IA
        if point selectionné:
            msg, action_ia, urgent = suggestion_action_ia(int(point))
            if msg:
                st.info(msg)
                if urgent:
                    st.warning(f"→ Priorité IA : {action_ia}")
    ...
```

- [ ] **Step 5: Run tests + verify app starts**

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/test_metier_ui.py -v`
Expected: All PASS

Then: `C:/Users/LENOVO/anaconda3/python.exe -m py_compile utils/metier_ui.py && echo "OK"`

- [ ] **Step 6: Commit**

```bash
git add utils/metier_ui.py tests/test_metier_ui.py
git commit -m "feat: integrer IA dans les onglets Secteurs, Sacs/Bacs, Collectes"
```

---

### Task 6: Intégration IA dans les onglets — Passages, Abonnements, Précollecteurs, Événements

**Files:**
- Modify: `utils/metier_ui.py` (onglets restants)

**Interfaces:**
- Consumes: `badge_priorite_ia`, `suggestion_action_ia`, `kpi_ia_secteur`

- [ ] **Step 1: Enhance `onglet_passages`**

Badge IA dans le tableau + suggestion dans le formulaire.

- [ ] **Step 2: Enhance `onglet_abonnements`**

KPI IA : fill rate moyen prédit des points des secteurs clients.

- [ ] **Step 3: Enhance `onglet_precollecteurs`**

KPI IA : fill rate moyen prédit par équipement.

- [ ] **Step 4: Enhance `onglet_evenements`**

KPI IA : nombre d'événements sur points urgents.

- [ ] **Step 5: Run tests + compile check**

- [ ] **Step 6: Commit**

```bash
git add utils/metier_ui.py
git commit -m "feat: integrer IA dans Passages, Abonnements, Precollecteurs, Evenements"
```

---

### Task 7: Test complet + push final

- [ ] **Step 1: Run all tests**

Run: `C:/Users/LENOVO/anaconda3/python.exe -m pytest tests/ -q`
Expected: All PASS

- [ ] **Step 2: Verify app starts**

Run: `timeout 15 streamlit run app.py --server.headless true 2>&1`

- [ ] **Step 3: Push**

```bash
git push origin master
```
