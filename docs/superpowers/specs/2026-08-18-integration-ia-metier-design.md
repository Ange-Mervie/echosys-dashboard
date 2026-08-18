# Design — Intégration IA dans l'interface métier (ECOSYS)

Date : 2026-08-18
Projet : ECHOSYS — Supervision intelligente de la pré-collecte des déchets

## Contexte

L'application ECOSYS dispose de deux systèmes aujourd'hui découpés :
1. **Modèle ML** (`models/meilleur_modele.pkl`, LightGBM, 46 features, R² ~0.30) → prédit
   `fillRate_predit`, `priorite_prediction`, `action_recommandnee` pour chaque `id_point`.
2. **Interface métier** (`utils/metier_ui.py`, 7 onglets SQLite) → gère les entités opérationnelles
   (secteurs, abonnements, précollecteurs, sacs/bacs, passages, collectes, événements).

L'intégration IA existe **uniquement** dans l'onglet Passages via `joindre_priorite_ia()`.
Le reste des onglets ignore complètement les prédictions.

## Objectif

Faire de l'IA un partenaire décisionnel **actionnable** dans chaque onglet métier :
KPIs enrichis, badges priorité IA, suggestions formulaires, et simulation what-if.

## Décisions validées

| Sujet | Décision |
|---|---|
| Source IA | Dashboard parquet existant (`dashboard/dashboard_dataset.parquet`) |
| Jointure | `id_point` (business ↔ IA) |
| Level d'interaction | KPI + badge + suggestion + what-if → action |
| Idempotence | Pas d'écriture en base par l'IA (lecture seule) |

## Architecture

### Fichiers concernés

| Fichier | Modification |
|---|---|
| `utils/metier_ui.py` | + fonctions IA : `joindre_priorite_ia()` enrichi, `badge_priorite_ia()`, `kpi_ia_secteur()`, `suggestion_action_ia()`, `simulateur_ia()` |
| `utils/prediction.py` | + `estimer_risque_debordement(fillrate_predit)` |
| `tests/test_metier_ui.py` | + tests IA |
| `app.py` | Aucun (page_metier déjà intégrée) |

### Nouveaux composants

#### 1. `estimer_risque_debordement(fillrate_predit) -> str`
```
fillrate >= 90 → "critique"
fillrate >= 70 → "eleve"
fillrate >= 40 → "modere"
sinon → "faible"
```

#### 2. `joindre_priorite_ia(df, colonne_point)` (enrichi)
- Ajoute `fillRate_predit`, `priorite_prediction`, `action_recommandnee`,
  `risque_debordement`, `fillRate` (actuel).
- Utilise `load_dashboard_data()` déjà mis en cache.
- `try/except` : retourne df inchangé si dashboard absent.

#### 3. `badge_priorite_ia(id_point) -> str (HTML)`
- Retourne un badge couleur ECHOSYS (`badge_priorite` depuis `utils/ui.py`)
  avec la priorité IA du point, ou un texte gris si absent.

#### 4. `kpi_ia_secteur(nom_secteur) -> dict`
- Calcule sur les points du secteur : `fill_moyen_predit`, `nb_urgents`,
  `nb_eleves`, `taux_risque`.
- Utilise `INT2Q` (id_point → quartier) et `SECTEUR_TYPES` (quartier → type)
  pour faire le lien point → secteur par nom.

#### 5. `suggestion_action_ia(id_point) -> tuple[str, str, bool]`
- Retourne : `(message_suggestion, action_ia, est_urgent)`.
- `message_suggestion` : texte lisible (ex. "Ce point est prédit Urgente (95% de remplissage) → créer une collecte immédiate ?")
- `action_ia` : valeur de `action_recommandnee` du dashboard (ex. "Collecte immédiate").
- `est_urgent` : True si priorité IA dans `["Urgente", "Elevée"]`.
- Si point absent du dashboard → `("", "", False)`.

#### 6. `simulateur_ia(id_point, date_ref) -> dict | None`
- Charge la ligne ML via `extraire_ligne_ml()` (depuis `utils/prediction.py`).
- Simule un scénario what-if : augmente `nb_precollecteurs_dispo` de +3 (ajustement
  configurable, valeur fixe pour la V1).
- Utilise `simuler_prediction(ligne_ml, ajustements)` pour recalculer.
- Retourne : `{fillrate_avant, fillrate_apres, priorite_avant, priorite_apres, action}`.
- Si la ligne ML n'existe pas pour ce point/date → retourne `None`.

## Modifications par onglet

### Secteurs (read)
- KPI IA : fill rate moyen prédit, points urgents, % risque élevé
- Carte : couleur des markers basée sur priorité IA

### Abonnements (read)
- KPI IA : fill rate moyen prédit des points du secteur, abonnements urgents
- Tri par priorité IA dans le tableau

### Précollecteurs (read + form)
- KPI IA : fill rate moyen prédit par équipement / secteur

### Sacs/Bacs (read + form)
- Col. `risque_debordement` (critique/élevé/modéré/faible)
- Badge priorité IA sur chaque ligne
- KPI : conteneurs en risque critique

### Passages (read + form) — **déjà partiel**
- Badge priorité IA dans le tableau (existant → renforcer)

### Collectes (read + form) — **formulaire enrichi**
- Suggestion IA dans le formulaire : "Le point X est urgent → collecte immédiate ?"
- Bouton what-if : simule l'impact d'une collecte sur le fill rate

### Événements (read)
- KPI IA : nombre d'événements haute impact sur points urgents

## Gestion des erreurs

- Dashboard IA absent → tous les composants IA affichent un `st.info` gris.
- Point non trouvé dans le dashboard → badge "IA non disponible".
- Simulation impossible (pas de ligne ML) → message "Simulation désactivée pour ce point".

## Tests

| Test | Vérification |
|---|---|
| `test_joindre_priorite_ia_complete` | DF enrichi de `fillRate_predit`, `risque_debordement`, `action_recommandnee` |
| `test_estimer_risque_debordement` | Mapping correct fillrate → risque |
| `test_suggestion_action_ia` | Point urgent → message + `est_urgent=True` |
| `test_kpi_ia_secteur` | KPIs agrégés cohérents avec dashboard |
| `test_simulateur_ia` | Simulation → fill rate modifié + différence affichée |

## Scope exclu (YAGNI)

- Pas de ré-entraînement depuis l'UI métier.
- Pas d'écriture de prédictions en base SQLite.
- Pas de page IA dédiée dans l'onglet Interface métier (l'existant
  "Analyse predictive" gère cela).
