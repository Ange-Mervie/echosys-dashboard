# Product

## Register

product

## Users

- Responsables d'exploitation d'Alpha Transit (régie de pré-collecte des déchets de Douala).
- Agents terrain / superviseurs qui surveillent les points de regroupement, priorisent les collectes et réagissent aux signalements citoyens.
- Contexte : bureaux, écrans de grande taille, session de pilotage quotidien. Le travail se fait « en flux » : un regard sur les KPIs, un tri par priorité, une décision.

## Product Purpose

ECHOSYS est un système intelligent de supervision de la pré-collecte des déchets : il combine
un modèle de Machine Learning (Gradient Boosting) qui prédit le taux de remplissage futur de
chaque point de regroupement (`fillRate_predit`) avec un moteur de règles métier qui en déduit
une priorité (Faible → Urgente) et une action recommandée. L'interface doit rendre l'état
opérationnel lisible en quelques secondes et transformer la prédiction en décision d'action.

Succès = l'opérateur sait en un coup d'œil *quoi collecter, où, et dans quel ordre*, et peut
simuler des scénarios (« what-if ») pour mesurer l'impact avant d'engager une tournée.

## Brand Identity — ECHOSYS

**Nom** : ECHOSYS
**Sous-titre** : Gestion intelligente de la pré-collecte des déchets

### Couleurs du logo

| Couleur | Hex | Symbolisme |
|---|---|---|
| Bleu marine | `#063B70` | Technologie, données, intelligence artificielle |
| Bleu technologique | `#159FE3` | Innovation, prédiction IA |
| Vert écologique | `#19B84A` | Environnement, collecte, développement durable |
| Vert clair | `#7ED957` | Éléments positifs, succès |
| Orange alerte | `#F5A623` | Attention, priorité élevée |
| Rouge urgence | `#E53935` | Urgence, risque critique |

### Personnalité

- **Professionnelle et technologique** : le bleu dominant évoque la donnée, l'IA et la fiabilité.
- **Écologique** : le vert rappelle la mission environnementale de collecte des déchets.
- **Institutionnelle** : design épuré, adapté à une présentation devant une entreprise ou une institution publique.
- **Orientée Action** : chaque écran raconte une histoire simple DONNÉES → ANALYSE → PRÉDICTION → ACTION.

### Application mobile et dashboard

L'application mobile et le dashboard partagent la même identité visuelle ECHOSYS, créant une
cohérence entre les deux interfaces pour les opérateurs d'Alpha Transit.

## Design Principles

1. **L'urgence se lit en 1 seconde** — la priorité (Urgente/Élevée) est le signal visuel dominant
   de chaque écran ; le reste est discret.
2. **La donnée d'abord, la décoration ensuite** — chaque pixel coloré doit porter une information
   (état, priorité, alerte). Aucune couleur décorative.
3. **Un seul langage visuel** — le même vocabulaire de composants (KPI, boutons, cartes, tableaux)
   partout dans l'app, y compris l'interface métier à 7 onglets.
4. **Densité utile, pas densité par défaut** — les tableaux et KPIs servent le pilotage ; on
   tolère la densité quand elle fait gagner du temps, jamais le bruit.
5. **Prévisible et fiable** — interactions standard, feedback immédiat, aucune surprise de mise en
   page ; l'outil disparaît dans la tâche.
6. **Identité ECHOSYS** — le design reflète les couleurs du logo ECHOSYS (bleu, vert, orange, rouge),
   créant une cohérence avec l'application mobile et renforçant l'identité technologique et écologique.

## Anti-references

- **Dashboard « generic SaaS » fade** : cartes grises identiques, icônes génériques, accent bleu
  par défaut, tout est « propre » et rien n'est prioritaire. Interdit.
- **App mobile grand public** : pastilles lumineuses, cartoonesque, animations ludiques. Interdit.
- **PowerBI/Excel brut** : tableaux denses sans hiérarchie, chartjunk, couleurs de défaut. Interdit.

## Accessibility & Inclusion

- WCAG AA : contraste ≥ 4.5:1 pour le texte courant, ≥ 3:1 pour le texte large.
- Ne pas reposer la lecture des priorités sur la seule couleur : coupler à un libellé texte et
  à une hiérarchie (poids, badge), car certains opérateurs peuvent avoir une déficience de
  vision des couleurs.
- Respecter `prefers-reduced-motion` : les transitions doivent avoir une variante sans animation.
- Champs de formulaire et contrôles avec états focus / hover / active explicites.
- Les couleurs ECHOSYS sont choisies pour leur contraste suffisant : bleu marine sur blanc,
  rouge sur fond clair, orange sur fond foncé.

## Hiérarchie de lecture

```
📊 DONNÉES (collecte historique + en temps réel)
        ↓
🔍 ANALYSE (tableaux, graphiques, tendances)
        ↓
🤖 PRÉDICTION IA (Gradient Boosting → fillRate_predit)
        ↓
🎯 PRIORISATION (règles métier → Urgente/Élevée/Moyenne/Faible)
        ↓
⚡ ACTION (collecte immédiate, planification, surveillance)
```

Un responsable non spécialiste en Data doit pouvoir comprendre le système en moins d'une minute.
