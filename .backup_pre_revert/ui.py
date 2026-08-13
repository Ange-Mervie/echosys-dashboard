"""Composants UI partages ECOSYS.

Design system (DESIGN.md) : vert, pro, de confiance. Restreint, une seule
accentuation (le vert), la priorite etant le seul langage coloré porteur
d'information.

Les composants utilisent autant que possible les primitives natives de Streamlit
(st.metric, st.header, st.caption) pour garantir un rendu fiable et sans
balisage HTML brut. Le seul HTML injecte est la feuille de style <style> (invisible)
et les badges de priorite (pastilles colorees).
"""

import streamlit as st

from utils.prediction import COULEURS_BADGE, COULEURS_PRIORITE

CSS = """
<style>
:root {
    --vert-950: #0E3A12;
    --vert-900: #1B5E20;
    --vert-800: #2E7D32;
    --vert-700: #2E7D32;
    --vert-600: #388E3C;
    --vert-500: #43A047;
    --vert-400: #66BB6A;
    --vert-100: #C8E6C9;
    --vert-50: #E8F5E9;
    --rouge: #C62828;
    --orange: #E65100;
    --ambre: #F9A825;
    --ink: #1C2530;
    --ink-2: #3D4A55;
    --ink-3: #5B6B76;
    --surface: #FFFFFF;
    --surface-2: #F4F6F8;
    --surface-3: #E9EDF0;
    --border: #DCE2E7;
}

/* Base */
html, body, [class*="css"] {
    font-family: "Inter", system-ui, "Segoe UI", Roboto, Arial, sans-serif;
    color: var(--ink-2);
    background-color: var(--surface) !important;
}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stHeader"] { background-color: var(--surface) !important; }
[data-testid="stSidebar"] {
    background-color: var(--surface-2) !important;
    border-right: 1px solid var(--border);
}
.block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1240px; }

/* Cartes de metrique (KPI) */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.9rem 1.1rem 1rem;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
[data-testid="stMetric"]:hover { border-color: var(--vert-600); background: var(--surface-2); }
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--ink-3) !important;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-weight: 800;
    font-size: 1.7rem !important;
    letter-spacing: -0.01em;
}
[data-testid="stMetricDelta"] { color: var(--ink-3) !important; }

/* Boutons */
.stButton>button {
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--ink-2);
    font-weight: 600;
}
.stButton>button:hover { border-color: var(--vert-600); color: var(--vert-700); }
.stButton>button:focus-visible { box-shadow: 0 0 0 3px var(--vert-100); outline: none; }
[data-testid="stFormSubmitButton"]>button {
    background: var(--vert-700); border: 1px solid var(--vert-700); color: #FFFFFF;
}
[data-testid="stFormSubmitButton"]>button:hover {
    background: var(--vert-600); border-color: var(--vert-600);
}

/* Onglets */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 0; border-bottom: 1px solid var(--border); }
[data-testid="stTabs"] [data-baseweb="tab"] { color: var(--ink-3); font-weight: 600; border-bottom: 2px solid transparent; }
[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    color: var(--vert-700); border-bottom-color: var(--vert-700);
}

/* Tableaux */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
[data-testid="stDataFrame"] thead tr th {
    background: var(--surface-2); color: var(--ink-3);
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em;
    font-weight: 600; border-bottom: 1px solid var(--border);
}
[data-testid="stDataFrame"] tbody tr:hover { background: var(--surface-3); }

/* Sidebar navigation */
[data-testid="stSidebar"] [data-testid="stRadio"] label { color: var(--ink-2); }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { color: var(--vert-700); }
[data-testid="stSidebar"] [data-testid="stRadio"] [data-checked] { color: var(--vert-700); font-weight: 700; }

/* Carte folium */
.st-folium iframe, [data-testid="stIFrame"] { border: 1px solid var(--border); border-radius: 12px; }

/* Badges de priorité */
.badge { display: inline-flex; align-items: center; padding: 2px 10px; border-radius: 999px; font-weight: 700; font-size: 0.8rem; white-space: nowrap; }
.badge::before { content: ""; width: 7px; height: 7px; border-radius: 50%; margin-right: 6px; }
.badge-prio-urgente { background: #FDECEC; color: #B71C1C; }
.badge-prio-urgente::before { background: #C62828; }
.badge-prio-elevee { background: #FFF0E0; color: #B23C00; }
.badge-prio-elevee::before { background: #E65100; }
.badge-prio-moyenne { background: #FFF8E1; color: #7A5B00; }
.badge-prio-moyenne::before { background: #F9A825; }
.badge-prio-faible { background: #E8F5E9; color: #1B5E20; }
.badge-prio-faible::before { background: #2E7D32; }

/* Accessibilite */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
</style>
"""

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def injecter_css():
    st.markdown(CSS, unsafe_allow_html=True)


def entete_app(contexte=None):
    """Barre d'en-tete sobre (marque + contexte operationnel).

    contexte : chaine Markdown native (pas de HTML brut).
    """
    st.markdown(":green[**ECOSYS**]  ·  Supervision de la pré-collecte — Douala")
    if contexte:
        st.markdown(contexte)
    st.divider()


def entete_page(titre, description=None):
    st.markdown(f"## {titre}")
    if description:
        st.caption(description)


def titre_section(titre, compteur=None):
    if compteur:
        st.subheader(f"{titre}  ·  {compteur}")
    else:
        st.subheader(titre)


def bande_kpi(items):
    """Grille de cartes KPI via st.metric (rendu natif, sans HTML brut).

    items : liste de dict {label, valeur, suffixe, sous, accent}.
    """
    cols = st.columns(len(items))
    for col, it in zip(cols, items):
        with col:
            valeur = str(it.get("valeur", ""))
            if it.get("suffixe"):
                valeur = f"{valeur} {it['suffixe']}"
            st.metric(label=it["label"], value=valeur)
            if it.get("sous"):
                st.caption(it["sous"])


def carte_kpi(libelle, valeur, suffixe="", sous_texte=None):
    valeur = f"{valeur}"
    if suffixe:
        valeur = f"{valeur} {suffixe}"
    st.metric(label=libelle, value=valeur)
    if sous_texte:
        st.caption(sous_texte)


def badge_priorite(priorite):
    """Rend un badge HTML de priorité. Priorité inconnue -> neutre."""
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


def afficher_figure(fig, titre=None, hauteur=None, key=None):
    """Habille et rend une figure Plotly de façon cohérente."""
    affiche_titre = titre is not None or (fig.layout.title.text is not None)
    if titre is not None and fig.layout.title.text is None:
        fig.update_layout(title=titre)
    fig.update_layout(
        height=hauteur,
        margin=dict(l=10, r=10, t=46 if affiche_titre else 10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color="#3D4A55", size=13),
        title=dict(font=dict(size=14, color="#1C2530", weight=600)),
        xaxis=dict(gridcolor="#E9EDF0", zerolinecolor="#DCE2E7"),
        yaxis=dict(gridcolor="#E9EDF0", zerolinecolor="#DCE2E7"),
        hoverlabel=dict(bgcolor="#1C2530", bordercolor="#1C2530", font=dict(color="#FFFFFF", size=12)),
        colorway=["#2E7D32", "#388E3C", "#43A047", "#C62828", "#E65100", "#F9A825"],
        legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG, key=key)


def stepper(etapes):
    """Cheminement horizontal (ex. pipeline IA) via colonnes natives."""
    cols = st.columns(len(etapes))
    for col, (titre, valeur) in zip(cols, etapes):
        with col:
            st.markdown(f"**{titre}**")
            st.markdown(valeur)


def synthese_operationnelle(insights):
    """Carte de synthese analytique (texte colore natif, sans HTML brut).

    insights : liste de tuples (type, texte) avec type in alert|info|ok.
    """
    couleur = {"alert": "red", "info": "green", "ok": "blue"}
    for typ, texte in insights:
        st.markdown(f"- :{couleur.get(typ, 'blue')}[{texte}]")


def style_table(priorite):
    """Styler pandas : colorie une cellule de priorité comme un badge."""
    couleurs = COULEURS_BADGE.get(priorite)
    if couleurs is None:
        return f"color: {COULEURS_PRIORITE.get(priorite, '#3D4A55')}; font-weight: 700;"
    return f"background-color: {couleurs['fond']}; color: {couleurs['texte']}; font-weight: 700;"
