"""Composants UI partages ECOSYS.

CSS du design system (DESIGN.md) injecte une seule fois via injecter_css().
"""

import streamlit as st

from utils.prediction import COULEURS_BADGE, COULEURS_PRIORITE

CSS = """
<style>
:root {
    --vert-950: #0E3A12;
    --vert-900: #1B5E20;
    --vert-700: #2E7D32;
    --vert-600: #388E3C;
    --vert-100: #C8E6C9;
    --vert-50: #E8F5E9;
    --ink: #1C2530;
    --ink-2: #3D4A55;
    --ink-3: #5B6B76;
    --surface: #FFFFFF;
    --surface-2: #F4F6F8;
    --surface-3: #E9EDF0;
    --border: #DCE2E7;
    --space-1: 0.5rem;
    --space-2: 1rem;
    --space-3: 1.5rem;
    --space-4: 2rem;
}

/* ------------------------------------------------------------------ */
/* Base                                                               */
/* ------------------------------------------------------------------ */

html, body, [class*="css"] {
    font-family: "Inter", system-ui, "Segoe UI", Roboto, Arial, sans-serif;
    color: var(--ink-2);
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}
[data-testid="stSidebar"] {
    background-color: var(--surface-2);
    border-right: 1px solid var(--border);
}
[data-testid="stHeader"] {
    background: transparent;
}
h1 {
    color: var(--vert-700);
    font-weight: 700;
    text-wrap: balance;
}
h2, h3 {
    color: var(--ink);
    font-weight: 700;
    text-wrap: balance;
}
p {
    color: var(--ink-2);
}

/* ------------------------------------------------------------------ */
/* KPI card                                                           */
/* ------------------------------------------------------------------ */

.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: var(--space-2) var(--space-3);
}
.kpi-label {
    font-size: 0.72rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
}
.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--vert-700);
    margin-top: 0.2rem;
    line-height: 1.1;
}
.kpi-suffix {
    font-size: 0.9rem;
    color: var(--ink-3);
    font-weight: 500;
}
.kpi-sous {
    font-size: 0.85rem;
    color: var(--ink-3);
    margin-top: 0.2rem;
}

/* ------------------------------------------------------------------ */
/* Banniere                                                           */
/* ------------------------------------------------------------------ */

.pilote-banner {
    background: linear-gradient(120deg, var(--vert-900) 0%, var(--vert-700) 55%, var(--vert-600) 100%);
    color: #FFFFFF;
    padding: 1.2rem 1.5rem;
    border-radius: 12px;
    margin-bottom: var(--space-3);
}
.pilote-banner .pb-titre {
    font-size: 1.6rem;
    font-weight: 800;
}
.pilote-banner .pb-sous {
    font-size: 1rem;
    font-weight: 600;
    color: #FFFFFF;
}

/* ------------------------------------------------------------------ */
/* Badges de priorite                                                 */
/* ------------------------------------------------------------------ */

.badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.8rem;
    white-space: nowrap;
}
.badge::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 6px;
}
.badge-prio-urgente { background: #FDECEC; color: #B71C1C; }
.badge-prio-urgente::before { background: #C62828; }
.badge-prio-elevee { background: #FFF0E0; color: #B23C00; }
.badge-prio-elevee::before { background: #E65100; }
.badge-prio-moyenne { background: #FFF8E1; color: #7A5B00; }
.badge-prio-moyenne::before { background: #F9A825; }
.badge-prio-faible { background: #E8F5E9; color: #1B5E20; }
.badge-prio-faible::before { background: #2E7D32; }

/* ------------------------------------------------------------------ */
/* Boutons                                                            */
/* ------------------------------------------------------------------ */

.stButton>button {
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--ink-2);
    font-weight: 600;
}
.stButton>button:hover {
    border-color: var(--vert-600);
    color: var(--vert-700);
}
.stButton>button:focus-visible {
    box-shadow: 0 0 0 3px var(--vert-100);
    outline: none;
}
[data-testid="stFormSubmitButton"]>button {
    background: var(--vert-700);
    border: 1px solid var(--vert-700);
    color: #FFFFFF;
}
[data-testid="stFormSubmitButton"]>button:hover {
    background: var(--vert-600);
    border-color: var(--vert-600);
    color: #FFFFFF;
}

/* ------------------------------------------------------------------ */
/* Onglets                                                            */
/* ------------------------------------------------------------------ */

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--ink-3);
    font-weight: 600;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: var(--vert-700);
    border-bottom-color: var(--vert-700);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--vert-700);
}

/* ------------------------------------------------------------------ */
/* Tableaux                                                           */
/* ------------------------------------------------------------------ */

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stDataFrame"] thead tr th {
    background: var(--surface-2);
    color: var(--ink-3);
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
    border-bottom: 1px solid var(--border);
}
[data-testid="stDataFrame"] tbody tr:hover {
    background: var(--surface-3);
}

/* ------------------------------------------------------------------ */
/* Sidebar / radio de navigation                                      */
/* ------------------------------------------------------------------ */

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: var(--ink-2);
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: var(--vert-700);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked] {
    color: var(--vert-700);
    font-weight: 700;
}

/* ------------------------------------------------------------------ */
/* Metriques Streamlit (Analyse predictive)                           */
/* ------------------------------------------------------------------ */

[data-testid="stMetricValue"] {
    color: var(--vert-700);
    font-weight: 700;
}

/* ------------------------------------------------------------------ */
/* Pipeline IA (page Analyse predictive)                              */
/* ------------------------------------------------------------------ */

.etape-pipeline {
    background: var(--vert-50);
    border: 1px solid var(--vert-100);
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
    height: 100%;
}
.etape-pipeline .et-titre {
    font-size: 0.75rem;
    color: var(--vert-700);
    text-transform: uppercase;
    font-weight: 700;
}
.etape-pipeline .et-valeur {
    font-weight: 700;
    color: var(--vert-700);
    font-size: 0.95rem;
    margin-top: 0.3rem;
}

/* ------------------------------------------------------------------ */
/* Carte folium                                                       */
/* ------------------------------------------------------------------ */

.st-folium iframe, [data-testid="stIFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
}

/* ------------------------------------------------------------------ */
/* Accessibilite : mouvement reduit                                   */
/* ------------------------------------------------------------------ */

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
}
</style>
"""


def injecter_css():
    st.markdown(CSS, unsafe_allow_html=True)


def badge_priorite(priorite):
    """Rend un badge HTML de priorite. Priorite inconnue -> neutre."""
    priorite = str(priorite).strip()
    classes = {
        "Urgente": "badge-prio-urgente",
        "Elevée": "badge-prio-elevee",
        "Moyenne": "badge-prio-moyenne",
        "Faible": "badge-prio-faible",
    }
    classe = classes.get(priorite)
    if classe is None:
        return f'<span class="badge" style="background:#EEF1F4;color:{COULEURS_PRIORITE.get(priorite, "#5B6B76")};">{priorite}</span>'
    return f'<span class="badge {classe}">{priorite}</span>'


def carte_kpi(libelle, valeur, suffixe="", sous_texte=None):
    sous = f'<div class="kpi-sous">{sous_texte}</div>' if sous_texte else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{libelle}</div>
            <div class="kpi-value">{valeur}<span class="kpi-suffix"> {suffixe}</span></div>
            {sous}
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_table(priorite):
    """Styler pandas : colorie une cellule de priorite comme un badge."""
    couleurs = COULEURS_BADGE.get(priorite)
    if couleurs is None:
        return f"color: {COULEURS_PRIORITE.get(priorite, '#3D4A55')}; font-weight: 700;"
    return f"background-color: {couleurs['fond']}; color: {couleurs['texte']}; font-weight: 700;"
