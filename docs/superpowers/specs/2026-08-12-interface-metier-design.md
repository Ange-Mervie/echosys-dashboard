# Design — Étape 3 : Interface métier (ECOSYS)

Date : 2026-08-12
Projet : ECOSYS — Supervision intelligente de la pré-collecte des déchets (Alpha Transit, Douala)

## Contexte

L'application Streamlit actuelle est orientée *points de regroupement* (dataset
`dashboard/dashboard_dataset.parquet` dérivé de `orbit_dataset.xlsx`). L'étape 3
adapte le dashboard au fonctionnement réel d'Alpha Transit en ajoutant une
**interface métier** couvrant 7 entités opérationnelles :

1. Abonnements
2. Passages
3. Précollecteurs
4. Secteurs
5. Sacs / bacs
6. Collecte
7. Événements

Aucune donnée réelle n'existe pour ces entités : les données affichées sont donc
**simulées de façon réaliste**, reliées aux points/arrondissements/quartiers déjà
présents dans le projet, puis persistées dans une base SQLite locale.

## Décisions validées

| Sujet | Décision |
|---|---|
| Source de données | Données simulées réalistes (déterministes) |
| Intégration dans l'app | 1 nouvelle page "Interface métier" + 7 onglets |
| Niveau d'interaction | Lecture (KPIs, tableaux, cartes) + formulaires d'ajout persistés |
| Liens avec l'existant | Reliées aux points existants (id_point, arrondissement, quartier) |
| Persistance | Base SQLite locale `data/ecosys.db` |

## Architecture

- **`utils/metier_db.py`** — module unique responsable de la base métier :
  - `DB_PATH` = `data/ecosys.db`
  - `init_db()` : création des 7 tables si absentes (idempotent)
  - `seed_db()` : génération des données simulées si la base est vide (déterministe,
    seed numpy fixe), liée au dashboard dataset existant
  - Fonctions de lecture (retournent des `DataFrame`) et d'insertion par entité
- **`app.py`** : nouvelle page `Interface métier` ajoutée au menu de navigation,
  avec 7 onglets (`st.tabs`).
- Les fonctionnalités IA existantes (`utils/prediction.py`, page "Analyse predictive")
  restent inchangées ; la page métier s'appuie sur le même dataset dashboard pour
  les liens géographiques.

## Modèle de données (7 tables)

### 1. `secteurs`
- `id_secteur` INTEGER PK
- `nom` TEXT — arrondissement / zone (ex. "Douala 3", "Bonabéri")
- `quartiers` TEXT — liste des quartiers (CSV)
- `type_secteur` TEXT — marche | residentiel | commercial | mixte
- `nb_points` INTEGER — nb de points de regroupement rattachés
- `responsable` TEXT — nom du responsable de secteur

### 2. `abonnements`
- `id_abonnement` INTEGER PK
- `id_secteur` INTEGER FK → secteurs
- `client` TEXT — nom du client (ménage, entreprise, commerce)
- `type_abonnement` TEXT — menage | entreprise | commerce
- `frequence` TEXT — quotidien | hebdomadaire | sur_appel
- `date_debut` TEXT (ISO)
- `statut` TEXT — actif | suspendu | expire
- `montant_mensuel` REAL (FCFA)

### 3. `precollecteurs`
- `id_precollecteur` INTEGER PK
- `nom` TEXT
- `id_secteur` INTEGER FK → secteurs
- `equipement` TEXT — tricycle | chariot | pousse_pousse
- `capacite_sacs` INTEGER — nb de sacs transportables
- `disponible` INTEGER (0/1)
- `telephone` TEXT

### 4. `sacs_bacs`
- `id_conteneur` INTEGER PK
- `id_point` INTEGER — référence à un point du dashboard dataset
- `id_secteur` INTEGER FK → secteurs
- `type_conteneur` TEXT — sac_100l | bac_240l | benne
- `capacite_litres` INTEGER
- `etat` TEXT — bon | use | endommage

### 5. `passages`
- `id_passage` INTEGER PK
- `id_point` INTEGER — référence au point du dashboard dataset
- `id_precollecteur` INTEGER FK → precollecteurs
- `date_passage` TEXT (ISO datetime)
- `quantite_kg` REAL
- `statut` TEXT — realise | retarde | annule

### 6. `collectes`
- `id_collecte` INTEGER PK
- `id_point` INTEGER — référence au point du dashboard dataset
- `date_collecte` TEXT (ISO datetime)
- `type_collecte` TEXT — precollecte | principale
- `volume_litres` REAL
- `id_precollecteur` INTEGER FK → precollecteurs
- `statut` TEXT — realisee | planifiee | annulee
- `duree_minutes` INTEGER

### 7. `evenements`
- `id_evenement` INTEGER PK
- `date` TEXT (ISO)
- `type_evenement` TEXT — marche | fete | evenement_sportif | incident | alerte
- `id_secteur` INTEGER FK → secteurs
- `description` TEXT
- `impact` TEXT — haut | moyen | faible
- `statut` TEXT — prevu | en_cours | termine

## Simulation des données

- **Secteurs** : dérivés des arrondissements/quartiers présents dans le dashboard
  dataset (valeurs uniques de `arrondissement` et `quartier`). Le dashboard dataset
  actuel contient les colonnes `arrondissement`/`quartier` dans `orbit_dataset_engineering`
  ; si absentes du parquet dashboard, fallback sur valeurs par défaut de Douala.
- **Sacs/bacs** : ~250 conteneurs attachés à des `id_point` réels du dataset.
- **Précollecteurs** : ~40, répartis par secteur.
- **Abonnements** : ~1000, répartis par secteur et type.
- **Passages** : générés sur l'horizon temporel des dates du dataset, reliés aux
  `id_point` et précollecteurs.
- **Collectes** : générées sur les dates de collecte existantes du dataset.
- **Événements** : ~30, dont des jours de marché alignés sur `is_jour_marche`
  quand la colonne est disponible.
- Génération **déterministe** (seed numpy fixe) pour reproductibilité. Lien avec la
  priorité IA de l'étape 2 lorsque possible (ex. afficher la priorité prédite des
  points liés).

## Page "Interface métier"

Nouvelle page `page_metier()` dans le menu `PAGES` de `app.py` :

- Header + description courte.
- `st.tabs` avec 7 onglets, chacun :
  - **KPIs** (3-4 cartes réutilisant le style `carte_kpi` existant)
  - **Tableau** des données avec filtres pertinents (date, secteur, statut)
  - **Formulaire d'ajout** dans un `st.expander`, persistant via SQLite
  - Messages de confirmation/erreur après insertion
- **Onglet Secteurs** : en plus, une vue carte (folium) positionnant les secteurs
  ou les points associés.
- **Onglet Passages / Collectes** : chronologie + filtre par priorité IA (lien
  étape 2) quand le point existe dans le dashboard dataset.
- **Onglet Événements** : tri par date/impact, mise en évidence des impacts hauts.

## Gestion des erreurs

- Si le dashboard dataset est introuvable → `seed_db()` produit un seed minimal
  basé sur des valeurs par défaut de Douala et affiche un avertissement dans l'app.
- Toute lecture/insertion SQL est enveloppée dans `try/except` avec message clair
  dans l'UI (pas d'exception non maîtrisée).
- `init_db()` et `seed_db()` sont idempotents et reproductibles.

## Vérification / tests

- `init_db()` + `seed_db()` exécutés deux fois → aucun doublon, base cohérente.
- Chaque table lisible et non vide après seed.
- Insertion via formulaire → nouvelle ligne présente à la prochaine lecture.
- `streamlit run app.py` démarre sans erreur ; page "Interface métier" affiche les
  7 onglets.
