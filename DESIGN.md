# ECOSYS — Design System

> Documenté via `$impeccable init`. Register : **product**. Personnalité : vert, pro, de confiance.
> Contraintes : WCAG AA (contraste ≥ 4.5:1), ne jamais reposer une décision sur la seule couleur,
> respecter `prefers-reduced-motion`. Anti-référence : « generic SaaS fade ».

## 1. Principes

1. **L'urgence se lit en 1 seconde** — les couleurs de priorité sont le seul langage coloré porteur
   d'information ; tout le reste reste sobre.
2. **La donnée d'abord** — KPIs denses et lisibles, pas de décor ; chaque pixel coloré porte un état.
3. **Un seul vocabulaire** — mêmes composants (KPI, badges, boutons, tableaux) sur les 7 pages,
   y compris l'interface métier.
4. **Contraste AA par défaut** — texte du corps en gris-bleu foncé, jamais de gris clair « élégant ».

## 2. Couleur

### Rampes

| Token | OKLCH | Hex | Usage |
|---|---|---|---|
| `--vert-950` | `oklch(0.28 0.07 150)` | `#0E3A12` | texte / fond d'en-tête profond |
| `--vert-900` | `oklch(0.39 0.10 150)` | `#1B5E20` | marque primaire, titres, barre active |
| `--vert-700` | `oklch(0.50 0.10 150)` | `#2E7D32` | marque secondaire, actions |
| `--vert-600` | `oklch(0.58 0.10 150)` | `#388E3C` | survols, éléments positifs |
| `--vert-100` | `oklch(0.91 0.05 150)` | `#C8E6C9` | fonds teintés success |
| `--vert-50` | `oklch(0.96 0.02 150)` | `#E8F5E9` | fonds teintés light |

| Token | OKLCH | Hex | Usage |
|---|---|---|---|
| `--ink` | `oklch(0.24 0.02 235)` | `#1C2530` | titres, texte principal |
| `--ink-2` | `oklch(0.36 0.02 235)` | `#3D4A55` | corps de texte (≥ 4.5:1 sur blanc) |
| `--ink-3` | `oklch(0.47 0.02 235)` | `#5B6B76` | texte secondaire (≥ 4.5:1 sur blanc) |
| `--surface` | `oklch(1 0 0)` | `#FFFFFF` | fond principal |
| `--surface-2` | `oklch(0.97 0.004 235)` | `#F4F6F8` | sidebar, panneaux |
| `--surface-3` | `oklch(0.92 0.006 235)` | `#E9EDF0` | survols, lignes paires |
| `--border` | `oklch(0.88 0.006 235)` | `#DCE2E7` | bordures |

### Priorités (sémantique — le seul langage coloré du système)

| Priorité | Couleur | Hex | Teinte de fond | Texte sur badge |
|---|---|---|---|---|
| Urgente | rouge profond | `#C62828` | `#FDECEC` | `#B71C1C` |
| Elevée | orange profond | `#E65100` | `#FFF0E0` | `#B23C00` |
| Moyenne | ambre | `#F9A825` | `#FFF8E1` | `#7A5B00` |
| Faible | vert | `#2E7D32` | `#E8F5E9` | `#1B5E20` |

Chaque priorité est **toujours** rendue comme badge : fond teinté + texte foncé contrasté + libellé.
Jamais une couleur seule. `Elevée` passe du rouge clair au **orange profond** pour se distinguer
nettement d'`Urgente` (facilite le daltonisme rouge-vert).

## 3. Typographie

- Une seule famille : `"Inter", system-ui, "Segoe UI", Roboto, Arial, sans-serif`.
- Échelle fixe (rem), ratio serré ~1.2 : base 1rem (16px), h1 1.75rem, h2 1.4rem, h3 1.15rem.
- Corps : `--ink-2` ; titres : `--ink` (h1 en `--vert-900`).
- `text-wrap: balance` sur h1–h3.
- Longueur de ligne : 65–75ch pour le prose ; tableaux denses tolérés.

## 4. Composants

### KPI card
- Fond blanc, `border: 1px solid var(--border)`, rayon 12px, **pas** d'ombre large ni de
  side-stripe. Hiérarchie portée par la typo : label 0.72rem uppercase (gris-bleu), valeur
  1.6rem 700 (`--vert-900`), suffixe 0.9rem. Option : pastille teintée de priorité.

### Badge de priorité
- `display:inline-flex; padding:2px 10px; border-radius:999px; font-weight:700; font-size:0.8rem;`
  fond = teinte, texte = couleur foncée. Classes `.prio-urgente .prio-elevee .prio-moyenne .prio-faible`.

### Bannière
- Fond `linear-gradient(120deg, #0E3A12, #1B5E20 55%, #2E7D32)`, texte blanc, rayon 12px.
  Sous-titre en blanc/opacité 0.9 (≥ 4.5:1 sur fond vert foncé).

### Boutons
- Primaire (soumettre) : fond `--vert-700`, texte blanc, rayon 8px, hover `--vert-600`, focus
  visible `box-shadow 0 0 0 3px var(--vert-100)`.
- Secondaire (défaut Streamlit) : fond blanc, bordure `--border`, texte `--ink-2`.

### Tableaux (`st.dataframe`)
- En-tête : `--surface-2`, texte `--ink-3` 0.72rem uppercase, bordure basse `--border`.
- Lignes : blanc, hover `--surface-3`. Aucun style par ligne sauf les badges de priorité.

### Onglets (`st.tabs`)
- Actif : texte `--vert-900` + barre basse 2px `--vert-700`. Inactif : `--ink-3`.

### Carte (folium)
- Conteneur : `border: 1px solid var(--border); border-radius: 12px; overflow: hidden;`.

## 5. Layout

- Largeur maximale du contenu : 1240px, centré.
- Sidebar : fond `--surface-2`, navigation radio avec sélection en `--vert-900` gras.
- Espacement : `--space-1: 0.5rem; --space-2: 1rem; --space-3: 1.5rem; --space-4: 2rem;`
  rythme alterné (jamais d'espacement uniforme partout).
- `prefers-reduced-motion: reduce` → aucune animation (transitions supprimées).

## 6. Implémentation Streamlit

- CSS injecté une seule fois via `utils/ui.py` (`injecter_css()`), appelé en tête de `main()`.
- Sélecteurs ciblés : `.block-container`, `[data-testid="stSidebar"]`, `[data-testid="stHeader"]`,
  `[data-testid="stMetric"]`, `[data-testid="stDataFrame"]`, `[data-testid="stTabs"]`,
  `.stButton>button`, `[data-testid="stRadio"]` (navigation), `.stForm`.
- Les couleurs de priorité sont centralisées dans `utils/prediction.py::COULEURS_PRIORITE`
  (+ `COULEURS_BADGE` pour les fonds/texte des badges).
- `utils/ui.py` expose aussi `badge_priorite(priorite)` et `style_table` (Styler pandas).
