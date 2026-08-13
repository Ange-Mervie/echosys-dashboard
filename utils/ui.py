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
    --bleu-marine: #0A1628;
    --bleu-navy: #0F2035;
    --bleu-900: #1A3A5C;
    --bleu-700: #1565C0;
    --bleu-500: #1E88E5;
    --bleu-100: #E3F2FD;
    --ink: #1A2332;
    --ink-2: #374151;
    --ink-3: #6B7280;
    --surface: #FFFFFF;
    --surface-2: #F8FAFC;
    --surface-3: #F1F5F9;
    --border: #E2E8F0;
    --border-light: #F1F5F9;
    --space-1: 0.5rem;
    --space-2: 1rem;
    --space-3: 1.5rem;
    --space-4: 2rem;
    --radius: 10px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.05), 0 2px 4px rgba(0,0,0,0.04);
}

/* Base */
html, body, [class*="css"] {
    font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    color: var(--ink-2);
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2.5rem;
    max-width: 1240px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bleu-marine) 0%, var(--bleu-navy) 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
    color: #FFFFFF !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #CBD5E1 !important;
    font-size: 0.88rem;
    padding: 6px 10px;
    border-radius: 6px;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: #FFFFFF !important;
    background: rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked] {
    color: #FFFFFF !important;
    font-weight: 700;
    background: rgba(21, 101, 192, 0.4) !important;
    border-radius: 8px;
    padding: 6px 10px;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {
    color: #94A3B8 !important;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"],
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.12) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span,
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] span {
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] [role="listbox"] div,
[data-testid="stSidebar"] [data-baseweb="select"] [role="option"] {
    color: #1A2332 !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {
    background: var(--bleu-500) !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
    margin: 0.8rem 0;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small {
    color: #94A3B8 !important;
}
[data-testid="stSidebar"] [data-testid="stCaption"] {
    color: #94A3B8 !important;
}

/* Titres */
h1 {
    color: var(--ink) !important;
    font-weight: 800;
    letter-spacing: -0.02em;
    text-wrap: balance;
}
h2, h3 {
    color: var(--ink) !important;
    font-weight: 700;
    letter-spacing: -0.01em;
    text-wrap: balance;
}

/* KPI card */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
    min-height: 90px;
}
.kpi-card:hover {
    border-color: var(--bleu-500);
    box-shadow: var(--shadow-md);
}
.kpi-label {
    font-size: 0.7rem;
    color: var(--ink-3);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.kpi-suffix {
    font-size: 0.85rem;
    color: var(--ink-3);
    font-weight: 600;
}
.kpi-sous {
    font-size: 0.78rem;
    color: var(--ink-3);
    margin-top: 0.25rem;
}

/* Banniere */
.pilote-banner {
    background: linear-gradient(135deg, var(--bleu-marine) 0%, var(--bleu-900) 50%, var(--bleu-700) 100%);
    color: #FFFFFF;
    padding: 1.2rem 1.6rem;
    border-radius: var(--radius);
    margin-bottom: var(--space-3);
    box-shadow: var(--shadow-md);
}
.pilote-banner .pb-titre {
    font-size: 1.35rem;
    font-weight: 800;
    letter-spacing: -0.01em;
}
.pilote-banner .pb-sous {
    font-size: 0.9rem;
    font-weight: 500;
    color: rgba(255,255,255,0.8);
    margin-top: 0.15rem;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.78rem;
    white-space: nowrap;
}
.badge::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-right: 6px;
    flex-shrink: 0;
}
.badge-prio-urgente { background: #FDECEC; color: #B71C1C; }
.badge-prio-urgente::before { background: #C62828; }
.badge-prio-elevee { background: #FFF0E0; color: #B23C00; }
.badge-prio-elevee::before { background: #E65100; }
.badge-prio-moyenne { background: #FFF8E1; color: #7A5B00; }
.badge-prio-moyenne::before { background: #F9A825; }
.badge-prio-faible { background: #E8F5E9; color: #1B5E20; }
.badge-prio-faible::before { background: #2E7D32; }

/* Boutons */
.stButton>button {
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--ink-2);
    font-weight: 600;
    font-size: 0.85rem;
    transition: all 0.15s ease;
}
.stButton>button:hover {
    border-color: var(--bleu-500);
    color: var(--bleu-700);
    box-shadow: var(--shadow);
}
.stButton>button:focus-visible {
    box-shadow: 0 0 0 3px var(--bleu-100);
    outline: none;
}
[data-testid="stFormSubmitButton"]>button {
    background: var(--bleu-700);
    border: 1px solid var(--bleu-700);
    color: #FFFFFF;
}
[data-testid="stFormSubmitButton"]>button:hover {
    background: var(--bleu-500);
    border-color: var(--bleu-500);
    color: #FFFFFF;
}

/* Onglets */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--surface-2);
    border-radius: 8px;
    padding: 4px 4px 0 4px;
    border: none;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--ink-3);
    font-weight: 600;
    font-size: 0.85rem;
    border-bottom: 2px solid transparent;
    border-radius: 6px 6px 0 0;
    transition: all 0.15s ease;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--ink);
    background: var(--surface);
}
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: var(--bleu-700);
    border-bottom-color: var(--bleu-700);
    background: var(--surface);
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--bleu-700);
}

/* Tableaux */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}
[data-testid="stDataFrame"] thead tr th {
    background: var(--ink) !important;
    color: #FFFFFF !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
    border-bottom: 2px solid var(--bleu-500) !important;
    padding: 10px 12px !important;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background: var(--bleu-100);
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) {
    background: var(--surface-2);
}

/* Metriques Streamlit */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.8rem 1rem;
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetric"]:hover {
    border-color: var(--bleu-500);
    box-shadow: var(--shadow);
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink-3) !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-weight: 800;
    font-size: 1.5rem !important;
}

/* Pipeline IA */
.etape-pipeline {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.8rem;
    text-align: center;
    height: 100%;
}
.etape-pipeline .et-titre {
    font-size: 0.72rem;
    color: var(--bleu-700);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.etape-pipeline .et-valeur {
    font-weight: 700;
    color: var(--ink);
    font-size: 0.9rem;
    margin-top: 0.3rem;
}

/* Carte folium */
.st-folium iframe, [data-testid="stIFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

/* Separateur invisible (remplace les ---) */
.section-spacer {
    height: 1.2rem;
}

/* Accessibilite */
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


def section_spacer(height=1.2):
    """Espace vertical fluide entre sections (remplace les separateurs)."""
    st.markdown(f'<div class="section-spacer" style="height:{height}rem"></div>', unsafe_allow_html=True)


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
