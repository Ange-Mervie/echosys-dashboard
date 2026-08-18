# Use Cases — 4 profils ECHOSYS

> **Object :** Cartographier l'IA intégrée (DONNÉES → ANALYSE → PRÉDICTION → ACTION)
> pour chaque profil utilisateur, en croisant les pages existantes + onglets métier IA.

## Profils

| # | Profil | Mission | Page d'entrée |
|---|---|---|---|
| 1 | Responsable d'exploitation | Pilotage global, planification, reporting | Accueil + Supervision + Analyse predictive |
| 2 | Superviseur équipe | Gestion équipe terrain, précollecteurs, suivi passages | Interface métier → Précollecteurs + Passages |
| 3 | Agent terrain | Collecte, points prioritaires, signalements | Interface métier → Collecte + Sacs/Bacs |
| 4 | Gestionnaire client | Abonnements, relations clients | Interface métier → Abonnements |

## Use Case 1 — Responsable d'exploitation

**Contexte** : grande écran, session de pilotage quotidien.

**Flux IA :**
```
Dashboard IA (80 points)
  → Accueil KPIs (fillRate IA moyen, points urgents)
  → Supervision carte (couleurs par priorité IA)
  → Analyse predictive → simulation what-if
  → Interface métier → Événements (sur points urgents)
  → Action : planifier tournée
```

**Écrans :** Accueil, Supervision, Points prioritaires, Analyse predictive, Interface métier → Événements

**Actions :**
1. Voir le KPI "Points urgents IA" en rouge sur la bannière d'accueil
2. Sur la carte Supervision, identifier les zones rouges (fillRate prédit > 90%)
3. Dans Analyse predictive, simuler l'impact d'ajouter +3 précollecteurs
4. Dans Événements, vérifier si un événement ("fête de quartier") coïncide avec un point urgent → planifier une collecte exceptionnelle

## Use Case 2 — Superviseur équipe

**Contexte** : gestion d'équipe de 5-10 agents, répartition des tournées.

**Flux IA :**
```
Interface métier → Précollecteurs
  → KPI IA fillRate moyen par équipement
  → Tableau précollecteurs avec statut disponibilité
  → Action : réassigner équipement vers secteur urgent

Interface métier → Passages
  → Badge priorité IA sur chaque passage
  → Filtre "Priorité IA : Urgente/Élevée"
  → Suggestion IA : "Point 42 prédit urgent → collecte immédiate ?"
  → Action : créer passage + collecte
```

**Écrans :** Interface métier → Précollecteurs, Passages

**Actions :**
1. Dans Précollecteurs, voir quel équipement est disponible dans un secteur urgent
2. Dans Passages, filtrer par priorité IA pour prioriser les interventions
3. Dans le formulaire d'ajout de passage, la suggestion IA recommande "Collecte immédiate" pour un point urgent → créer le passage directement

## Use Case 3 — Agent terrain

**Contexte** : mobile ou tablette, 10-20 collectes par jour.

**Flux IA :**
```
Interface métier → Collecte
  → Liste des collectes triée par priorITE IA (urgence en premier)
  → Pour chaque point : badge priorité IA + suggestion d'action
  → Formulaire collecte → suggestion IA → bouton "Créer → collecte immédiate"

Interface métier → Sacs/Bacs
  → Col. risque_ia (critique/eleve/modere/faible)
  → KPI conteneurs critiques
  → Formulaire → suggestion IA si point urgent
```

**Écrans :** Interface métier → Collecte, Sacs/Bacs

**Actions :**
1. Sur le terrain, ouvrir l'onglet Collecte → voir la liste triée par priorité IA
2. Le point #42 affiche "badge rouge Urgente" + suggestion "Collecte immédiate"
3. Cliquer sur "Créer collecte immédiate" → formulaire pré-rempli avec l'action IA
4. Dans Sacs/Bacs, voir qu'un conteneur est "critique" → signaler l'huis clair

## Use Case 4 — Gestionnaire client

**Contexte** : fidélisation client, réclamation, facturation.

**Flux IA :**
```
Interface métier → Abonnements
  → KPI IA : fillRate moyen des points clients
  → Tableau abonnements trié par priorITE IA
  → Client dans un secteur urgent → priorité de collecte
  → Action : contanter le client du retard de collecte
```

**Écran :** Interface métier → Abonnements

**Actions :**
1. Voir le KPI "FillRate IA moyen (clients)" pour suivre la satisfaction client
2. Identifier un abonné dans un secteur "Urgente" → le contacter pour expliquer le retard
3. Filtrer les abonnements par secteur urgent → prioriser les relances

## Matrice de traçabilité IA

| IA Feature | Use Case 1 | Use Case 2 | Use Case 3 | Use Case 4 |
|---|---|---|---|---|
| `kpi_ia_secteur` | ✅ dashboard | ✅ précollecteurs | — | ✅ abonnements |
| `badge_priorite_ia` | ✅ tableau | ✅ tableau | ✅ tableau | — |
| `suggestion_action_ia` | ✅ événements | ✅ passages | ✅ collecte/sacs | — |
| `simulateur_ia` | ✅ what-if | — | — | — |
| `joindre_priorite_ia` | ✅ supervision | ✅ passages | ✅ collecte | — |
| `construire_carte_secteurs_ia` | ✅ supervision | — | — | — |
| `estimer_risque_debordement` | ✅ risque | ✅ risque | ✅ sacs/bacs | — |

## Prochaine itération (Étape D — mobile)

La page **Interface métier** est conçue pour écran de bureau (tableaux denses).
Pour les agents terrain (profil 3), une **version mobile** de l'onglet Collecte
est envisagée : liste épurée, badge priorité géant, bouton unique "J'ai collecté".
