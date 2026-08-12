# Product

## Register

product

## Users

- Responsables d'exploitation d'Alpha Transit (régie de pré-collecte des déchets de Douala).
- Agents terrain / superviseurs qui surveillent les points de regroupement, priorisent les collectes et réagissent aux signalements citoyens.
- Contexte : bureaux, écrans de grande taille, session de pilotage quotidien. Le travail se fait « en flux » : un regard sur les KPIs, un tri par priorité, une décision.

## Product Purpose

ECOSYS est un système intelligent de supervision de la pré-collecte des déchets : il combine
un modèle de Machine Learning (Gradient Boosting) qui prédit le taux de remplissage futur de
chaque point de regroupement (`fillRate_predit`) avec un moteur de règles métier qui en déduit
une priorité (Faible → Urgente) et une action recommandée. L'interface doit rendre l'état
opérationnel lisible en quelques secondes et transformer la prédiction en décision d'action.

Succès = l'opérateur sait en un coup d'œil *quoi collecter, où, et dans quel ordre*, et peut
simuler des scénarios (« what-if ») pour mesurer l'impact avant d'engager une tournée.

## Brand Personality

Vert, pro, de confiance.

- Autorité municipale sobre : le vert évoque l'environnement et la propreté, sans en faire un
  produit « écolo-marketing ».
- Confiance opérationnelle : données denses, hiérarchie claire, aucun effet de vitrine.
- Ton des libellés : français neutre, sans accents (convention technique du projet), orienté action.

## Anti-references

- **Dashboard « generic SaaS » fade** : cartes grises identiques, icônes génériques, accent bleu
  par défaut, tout est « propre » et rien n'est prioritaire. Interdit.
- **App mobile grand public** : pastilles lumineuses, cartoonesque, animations ludiques. Interdit.
- **PowerBI/Excel brut** : tableaux denses sans hiérarchie, chartjunk, couleurs de défaut. Interdit.

## Design Principles

1. **L'urgence se lit en 1 seconde** — la priorité (Urgente/Elevée) est le signal visuel dominant
   de chaque écran ; le reste est discret.
2. **La donnée d'abord, la décoration ensuite** — chaque pixel coloré doit porter une information
   (état, priorité, alerte). Aucune couleur décorative.
3. **Un seul langage visuel** — le même vocabulaire de composants (KPI, boutons, cartes, tableaux)
   partout dans l'app, y compris l'interface métier à 7 onglets.
4. **Densité utile, pas densité par défaut** — les tableaux et KPIs servent le pilotage ; on
   tolère la densité quand elle fait gagner du temps, jamais le bruit.
5. **Prévisible et fiable** — interactions standard, feedback immédiat, aucune surprise de mise en
   page ; l'outil disparaît dans la tâche.

## Accessibility & Inclusion

- WCAG AA : contraste ≥ 4.5:1 pour le texte courant, ≥ 3:1 pour le texte large.
- Ne pas reposer la lecture des priorités sur la seule couleur : coupler à un libellé texte et
  à une hiérarchie (poids, badge), car certains opérateurs peuvent avoir une déficience de
  vision des couleurs.
- Respecter `prefers-reduced-motion` : les transitions doivent avoir une variante sans animation.
- Champs de formulaire et contrôles avec états focus / hover / active explicites.
