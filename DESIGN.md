# ECHOSYS — Design System

> Identité visuelle ECHOSYS — Gestion intelligente de la pré-collecte des déchets.
> Contraintes : WCAG AA (contraste ≥ 4.5:1), ne jamais reposer une décision sur la seule couleur,
> respecter `prefers-reduced-motion`.

## 1. Principes

1. **L'urgence se lit en 1 seconde** — les couleurs de priorité sont le seul langage coloré porteur
   d'information ; tout le reste reste sobre.
2. **La donnée d'abord** — KPIs denses et lisibles, pas de décor ; chaque pixel coloré porte un état.
3. **Un seul vocabulaire** — mêmes composants (KPI, badges, boutons, tableaux) sur les 7 pages,
   y compris l'interface métier.
4. **Contraste AA par défaut** — texte du corps en gris-bleu foncé, jamais de gris clair « élégant ».
5. **Identité ECHOSYS** — le design reflète les couleurs du logo ECHOSYS :
   - **Bleu marine** (#063B70) : technologie, données, intelligence artificielle
   - **Bleu technologique** (#159FE3) : innovation, prédiction IA
   - **Vert écologique** (#19B84A) : environnement, collecte, développement durable
   - **Orange alerte** (#F5A623) : attention, priorité élevée
   - **Rouge urgence** (#E53935) : urgence, risque critique

## 2. Couleur

### Palette ECHOSYS

| Token | Hex | Usage |
|---|---|---|
| `--echosys-bleu-marine` | `#063B70` | Couleur principale, sidebar, titres |
| `--echosys-bleu-tech` | `#159FE3` | Technologie, IA, prédiction |
| `--echosys-vert` | `#19B84A` | Environnement, collecte |
| `--echosys-vert-clair` | `#7ED957` | Éléments positifs, succès |
| `--echosys-orange` | `#F5A623` | Avertissement, priorité élevée |
| `--echosys-rouge` | `#E53935` | Urggence, alerte critique |
| `--echosys-gris` | `#F5F7FA` | Arrière-plan général |
| `--echosys-blanc` | `#FFFFFF` | Fond principal, cartes |

### Rampes bleu ECHOSYS

| Token | Hex | Usage |
|---|---|---|
| `--bleu-950` | `#031D38` | Texte profond |
| `--bleu-900` | `#063B70` | Sidebar, en-tête |
| `--bleu-800` | `#0A5AA3` | Éléments actifs |
| `--bleu-700` | `#159FE3` | Liens, accents |
| `--bleu-600` | `#3DB5E8` | Survols |
| `--bleu-500` | `#65CBED` | Éléments légers |
| `--bleu-400` | `#8DDDF2` | Accents très clairs |
| `--bleu-100` | `#D4EFF9` | Fonds teintés |
| `--bleu-50` | `#EDF7FC` | Fonds très clairs |

### Rampes vert ECHOSYS

| Token | Hex | Usage |
|---|---|---|
| `--vert-950` | `#0B5C1F` | Texte profond |
| `--vert-900` | `#127A2C` | Vert foncé |
| `--vert-800` | `#19B84A` | Vert principal |
| `--vert-700` | `#19B84A` | Vert principal |
| `--vert-600` | `#45C76A` | Survols |
| `--vert-500` | `#7ED957` | Vert clair |
| `--vert-400` | `#9DE37A` | Accents |
| `--vert-100` | `#D4F2C6` | Fonds teintés |
| `--vert-50` | `#EDFAE7` | Fonds très clairs |

### Neutres

| Token | Hex | Usage |
|---|---|---|
| `--ink` | `#1C2530` | Titres, texte principal |
| `--ink-2` | `#3D4A55` | Corps de texte |
| `--ink-3` | `#5B6B76` | Texte secondaire |
| `--surface` | `#FFFFFF` | Fond principal |
| `--surface-2` | `#F5F7FA` | Sidebar, panneaux |
| `--surface-3` | `#E9EDF0` | Survols |
| `--border` | `#DCE2E7` | Bordures |

### Priorités (sémantique — le seul langage coloré du système)

| Priorité | Couleur | Hex | Teinte de fond | Texte sur badge |
|---|---|---|---|---|
| Urgente | rouge ECHOSYS | `#E53935` | `#FFEBEE` | `#C62828` |
| Élevée | orange ECHOSYS | `#F5A623` | `#FFF3E0` | `#E65100` |
| Moyenne | vert ECHOSYS | `#19B84A` | `#E8F5E9` | `#1B5E20` |
| Faible | bleu ECHOSYS | `#159FE3` | `#E3F2FD` | `#0D47A1` |

Chaque priorité est **toujours** rendue comme badge : fond teinté + texte foncé contrasté + libellé.
Jamais une couleur seule. Les couleurs sont inspirées du logo ECHOSYS.

## 3. Typographie

- Police : `"Inter", system-ui, "Segoe UI", Roboto, Arial, sans-serif`
- Échelle fixe (rem), ratio serré ~1.2 :
  - Titre principal : 30–34 px
  - Titres de sections : 20–24 px
  - KPI : 28–32 px
  - Texte normal : 14–15 px
  - Texte secondaire : 13–14 px
- Corps : `--ink-2` ; titres : `--ink` (h1 en `--echosys-bleu-marine`)
- `text-wrap: balance` sur h1–h3
- Longueur de ligne : 65–75ch pour le prose ; tableaux denses tolérés

## 4. Composants

### En-tête applicatif
- Logo ECHOSYS (dégradé bleu marine → bleu tech) + nom en `--echosys-bleu-marine`
- Sous-titre : "Gestion intelligente de la pré-collecte des déchets"
- Tag : "Supervision générale · date"
- Arrière-plan : `--echosys-gris`

### Sidebar
- Dégradé vertical bleu marine → bleu 950
- Navigation radio avec fond actif bleu 800
- Texte : bleu 100 → blanc au survol
- Filtres dans une section identifiée

### Bandeau de KPI
- Une seule rangée `border: 1px solid var(--border)`, rayon 12px
- KPI principaux : fond bleu tech pour les données
- KPI alertes : fond rouge/orange uniquement si nécessaire
- Valeur en `--ink` 1.5rem 800

### Badges de priorité
- `display:inline-flex; padding: 2px 10px; border-radius: 999px; font-weight: 700; font-size: 0.8rem;`
- Fond = teinte, texte = couleur foncée
- Classes `.badge-prio-urgente .badge-prio-elevee .badge-prio-moyenne .badge-prio-faible`

### Boutons
- Primaire : fond `--echosys-bleu-marine`, texte blanc, rayon 8px
- Hover : fond `--echosys-bleu-tech`
- Secondaire : fond blanc, bordure `--border`

### Tableaux
- En-tête : fond `--bleu-900`, texte blanc
- Lignes : blanc, survol `--bleu-50`
- Bordure basse en-tête : `--echosys-bleu-tech`

### Onglets
- Fond onglets : `--surface-2`
- Actif : texte `--echosys-bleu-marine` + barre basse `--echosys-bleu-tech`
- Hover : fond blanc

### Carte (folium)
- Bordure : `1px solid var(--border)`
- Rayon : 12px
- Ombre discrète

## 5. Layout

- Largeur maximale du contenu : 1240px, centré
- Arrière-plan général : `#F5F7FA`
- Sidebar : dégradé bleu marine
- Espacement régulier, coins légèrement arrondis
- Ombre discrète sur les cartes
- `prefers-reduced-motion: reduce` → aucune animation

## 6. Hiérarchie visuelle

```
DONNÉES → ANALYSE → PRÉDICTION IA → PRIORISATION → ACTION
```

Un responsable non spécialiste en Data doit pouvoir comprendre le système en moins d'une minute.
