"""ECOSYS - Supervision intelligente de la pre-collecte des dechets.

Prototype V1 : Donnees -> KPI -> Graphiques -> Tableau -> Carte.
Lancement : streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium
import folium

from utils.data_loader import (
    load_dashboard_data,
    load_model,
    load_model_metrics,
    load_feature_importance,
    load_ml_data,
    verifier_colonnes,
)
from utils.ui import carte_kpi, injecter_css, badge_priorite, style_table
from utils.prediction import (
    ORDRE_PRIORITE,
    COULEURS_PRIORITE,
    enrichir_priorite_action,
    definir_priorite,
    generer_recommandation,
    extraire_ligne_ml,
    simuler_prediction,
    FEATURES_SIMULABLES,
    cohercer_slider,
)
from utils.metier_ui import page_metier

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="ECOSYS - Supervision intelligente de la pre-collecte",
    page_icon="\U0001F30D",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Accueil",
    "Supervision",
    "Points prioritaires",
    "Analyse predictive",
    "Interface metier",
    "Donnees",
    "A propos du systeme",
]

# ---------------------------------------------------------------------------
# Styles (design system partage, voir DESIGN.md)
# ---------------------------------------------------------------------------

injecter_css()


def afficher_entete():
    st.markdown(
        """
        <div class="pilote-banner">
            <div class="pb-titre">ECOSYS &mdash; Supervision intelligente de la pre-collecte</div>
            <div class="pb-sous">Prediction, priorisation et aide a la decision</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Chargement des donnees
# ---------------------------------------------------------------------------


@st.cache_data(ttl=3600, show_spinner=False)
def charger_donnees():
    df = load_dashboard_data()
    df = enrichir_priorite_action(df)
    df["priorite_prediction"] = df["priorite_prediction"].map(
        lambda x: str(x).strip() if isinstance(x, str) else x
    )
    if "priorite_prediction" in df.columns:
        df["priorite_prediction"] = df["priorite_prediction"].replace(
            {"élevée": "Elevée", "Élevée": "Elevée"}
        )
    return df


def charger_contexte():
    contexte = {}
    try:
        contexte["model"] = load_model()
    except FileNotFoundError as e:
        contexte["model"] = None
        st.sidebar.warning("Modele non charge : " + str(e))
    try:
        contexte["metrics"] = load_model_metrics()
    except Exception:
        contexte["metrics"] = None
    try:
        contexte["importance"] = load_feature_importance()
    except Exception:
        contexte["importance"] = None
    return contexte


# ---------------------------------------------------------------------------
# Filtres
# ---------------------------------------------------------------------------


def afficher_filtres(df):
    st.sidebar.markdown("## Filtres")

    toutes_dates = pd.to_datetime(df["date_collecte"]).dt.date
    date_min = toutes_dates.min()
    date_max = toutes_dates.max()

    date_choisie = st.sidebar.selectbox(
        "Date de collecte",
        options=[date_max] + sorted(toutes_dates.unique(), reverse=True)[:30],
        index=0,
        format_func=lambda d: d.strftime("%d/%m/%Y") if hasattr(d, "strftime") else str(d),
    )

    priorites_choisies = st.sidebar.multiselect(
        "Priorite",
        options=ORDRE_PRIORITE,
        default=ORDRE_PRIORITE,
    )

    actions_dispo = sorted(df["action_recommandee"].dropna().unique())
    actions_choisies = st.sidebar.multiselect(
        "Action recommandee", options=actions_dispo, default=actions_dispo
    )

    plage_fill = st.sidebar.slider(
        "Niveau de remplissage (%)",
        min_value=0,
        max_value=100,
        value=(0, 100),
        step=5,
    )

    return {
        "date": date_choisie,
        "priorites": priorites_choisies,
        "actions": actions_choisies,
        "plage_fill": plage_fill,
    }


def filtrer_donnees(df, filtres):
    mask = pd.Series(True, index=df.index)
    mask &= pd.to_datetime(df["date_collecte"]).dt.date == filtres["date"]
    if filtres["priorites"]:
        mask &= df["priorite_prediction"].isin(filtres["priorites"])
    if filtres["actions"]:
        mask &= df["action_recommandee"].isin(filtres["actions"])
    lo, hi = filtres["plage_fill"]
    mask &= df["fillRate_predit"].between(lo, hi)
    return df.loc[mask]


# ---------------------------------------------------------------------------
# KPI
# ---------------------------------------------------------------------------


def calculer_kpis(df, filtres=None):
    df_use = filtrer_donnees(df, filtres) if filtres else df
    kpis = {}
    kpis["nb_points"] = df_use["id_point"].nunique()
    kpis["fill_moyen"] = df_use["fillRate"].mean()
    kpis["fill_predit_moyen"] = df_use["fillRate_predit"].mean()
    kpis["nb_prioritaires"] = int(
        df_use["priorite_prediction"].isin(["Elevée", "Urgente"]).sum()
    )
    kpis["nb_risque"] = int(
        (df_use["risque_debordement"] >= df_use["risque_debordement"].quantile(0.9)).sum()
    )
    kpis["nb_plaintes"] = df_use["nb_plaintes"].sum()
    kpis["nb_signalements"] = df_use["nb_signalements_citoyens"].sum()
    return kpis, df_use


# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------


def graph_priorites(df_use):
    comptage = df_use["priorite_prediction"].value_counts().reindex(ORDRE_PRIORITE).fillna(0)
    fig = go.Figure(
        go.Bar(
            x=comptage.index,
            y=comptage.values,
            marker_color=[COULEURS_PRIORITE[p] for p in comptage.index],
            text=comptage.values.astype(int),
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Repartition des priorites",
        yaxis_title="Nombre de points",
        height=320,
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def graph_actuel_vs_predit(df_use):
    df_plot = df_use.dropna(subset=["fillRate", "fillRate_predit"])
    df_plot = df_plot.copy()
    df_plot["hausse"] = df_plot["fillRate_predit"] - df_plot["fillRate"]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            line=dict(color="#B0BEC5", dash="dash"),
            name="y = x (stabilite)",
            hoverinfo="skip",
        )
    )
    for p in ORDRE_PRIORITE:
        sub = df_plot[df_plot["priorite_prediction"] == p]
        if sub.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=sub["fillRate"],
                y=sub["fillRate_predit"],
                mode="markers",
                name=p,
                marker=dict(color=COULEURS_PRIORITE[p], size=9, opacity=0.85),
                customdata=sub[["id_point", "hausse"]].to_numpy(),
                hovertemplate="Point %{customdata[0]}<br>Actuel: %{x:.1f}%<br>Predit: %{y:.1f}%<br>Variation: %{customdata[1]:+.1f} pts<extra></extra>",
            )
        )
    fig.update_layout(
        title="FillRate actuel vs FillRate predit",
        xaxis_title="FillRate actuel (%)",
        yaxis_title="FillRate predit (%)",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig


def graph_hausses_fortes(df_use):
    df_plot = df_use.dropna(subset=["fillRate", "fillRate_predit"]).copy()
    df_plot["hausse"] = df_plot["fillRate_predit"] - df_plot["fillRate"]
    top = df_plot.nlargest(10, "hausse")
    if top.empty:
        return None
    fig = px.bar(
        top,
        x="hausse",
        y=top["id_point"].astype(str),
        orientation="h",
        color="priorite_prediction",
        color_discrete_map=COULEURS_PRIORITE,
        labels={"hausse": "Variation (pts)", "y": "Point"},
        title="Points avec la plus forte augmentation prevue",
        height=380,
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10))
    return fig


# ---------------------------------------------------------------------------
# Tableau
# ---------------------------------------------------------------------------


def tableau_operationnel(df_use):
    colonnes = [
        "id_point",
        "fillRate",
        "fillRate_predit",
        "risque_debordement",
        "priorite_prediction",
        "action_recommandee",
        "nb_signalements_citoyens",
        "nb_plaintes",
    ]
    colonnes = [c for c in colonnes if c in df_use.columns]
    table = df_use[colonnes].copy()
    ordre_map = {p: i for i, p in enumerate(ORDRE_PRIORITE)}
    table["_ord"] = table["priorite_prediction"].map(ordre_map).fillna(9)
    table = table.sort_values(["_ord", "fillRate_predit"], ascending=[True, False]).drop(columns="_ord")

    styled = (
        table.style.format(
            {
                "fillRate": "{:.1f}%",
                "fillRate_predit": "{:.1f}%",
                "risque_debordement": "{:,.0f}",
            },
            na_rep="-",
        )
        .map(style_table, subset=["priorite_prediction"])
        .set_properties(**{"font-size": "0.9rem"})
    )
    return styled


# ---------------------------------------------------------------------------
# Carte
# ---------------------------------------------------------------------------


def construire_carte(df_use):
    df_map = df_use.dropna(subset=["latitude", "longitude"]).copy()
    if df_map.empty:
        return None

    lat_centre = df_map["latitude"].mean()
    lon_centre = df_map["longitude"].mean()

    carte = folium.Map(location=[lat_centre, lon_centre], zoom_start=12, control_scale=True)

    for _, row in df_map.iterrows():
        couleur = COULEURS_PRIORITE.get(row["priorite_prediction"], "#78909C")
        html_popup = f"""
        <div style="font-family:sans-serif; font-size:13px; width:260px;">
            <b>Point #{int(row['id_point'])}</b><br>
            FillRate actuel : <b>{row['fillRate']:.1f}%</b><br>
            FillRate predit : <b>{row['fillRate_predit']:.1f}%</b><br>
            Risque de debordement : <b>{row['risque_debordement']:,.0f}</b><br>
            Priorite : <span style="color:{couleur}; font-weight:700;">{row['priorite_prediction']}</span><br>
            Action : <b>{row['action_recommandee']}</b><br>
            Signalements : {row.get('nb_signalements_citoyens', '-')} | Plaintes : {row.get('nb_plaintes', '-')}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=8,
            color=couleur,
            fill=True,
            fill_color=couleur,
            fill_opacity=0.75,
            popup=folium.Popup(html_popup, max_width=300),
            tooltip=f"Point #{int(row['id_point'])} - {row['priorite_prediction']}",
        ).add_to(carte)

    return carte


def afficher_legende():
    cols = st.columns(len(COULEURS_PRIORITE))
    for col, (label, _) in zip(cols, COULEURS_PRIORITE.items()):
        with col:
            st.markdown(badge_priorite(label), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def page_accueil(df, filtres):
    kpis, df_use = calculer_kpis(df, filtres)

    st.subheader("Tableau de bord global")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        carte_kpi("Points suivis", f"{kpis['nb_points']:,}", sous_texte=f"{df['id_point'].nunique():,} au total")
    with c2:
        carte_kpi("FillRate actuel moyen", f"{kpis['fill_moyen']:.1f}", "%")
    with c3:
        carte_kpi("FillRate predit moyen", f"{kpis['fill_predit_moyen']:.1f}", "%")
    with c4:
        carte_kpi("Points prioritaires", f"{kpis['nb_prioritaires']:,}", sous_texte="Elevee ou Urgente")

    c5, c6, c7 = st.columns(3)
    with c5:
        carte_kpi("Points a risque", f"{kpis['nb_risque']:,}", sous_texte="Top 10% du risque de debordement")
    with c6:
        carte_kpi("Plaintes citoyens", f"{kpis['nb_plaintes']:,}")
    with c7:
        carte_kpi("Signalements citoyens", f"{kpis['nb_signalements']:,}")

    st.markdown("---")
    col_graph, col_table = st.columns([1.3, 1])
    with col_graph:
        st.plotly_chart(graph_priorites(df_use), use_container_width=True)
    with col_table:
        st.markdown("### Top 5 points a surveiller")
        st.dataframe(
            df_use.sort_values(
                "fillRate_predit", ascending=False
            )[["id_point", "fillRate_predit", "priorite_prediction", "action_recommandee"]]
            .head(5)
            .style.map(style_table, subset=["priorite_prediction"]),
            use_container_width=True,
            hide_index=True,
        )


def page_supervision(df, filtres):
    kpis, df_use = calculer_kpis(df, filtres)
    st.subheader("Supervision des points de regroupement")

    if df_use.empty:
        st.warning("Aucun point ne correspond aux filtres pour cette date.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        carte_kpi("Points suivis", f"{kpis['nb_points']:,}")
    with c2:
        carte_kpi("FillRate actuel moyen", f"{kpis['fill_moyen']:.1f}", "%")
    with c3:
        carte_kpi("FillRate predit moyen", f"{kpis['fill_predit_moyen']:.1f}", "%")
    with c4:
        carte_kpi("Points prioritaires", f"{kpis['nb_prioritaires']:,}")

    st.markdown("### Carte intelligente des points de regroupement")
    afficher_legende()
    carte = construire_carte(df_use)
    if carte is None:
        st.info("Aucun point geolocalisable.")
    else:
        st_folium(carte, width="100%", height=500)

    st.markdown("### Analyse actuel vs predit")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(graph_actuel_vs_predit(df_use), use_container_width=True)
    with col2:
        fig_h = graph_hausses_fortes(df_use)
        if fig_h is not None:
            st.plotly_chart(fig_h, use_container_width=True)

    st.markdown("### Tableau operationnel")
    st.dataframe(tableau_operationnel(df_use), use_container_width=True, hide_index=True)


def page_prioritaires(df, filtres):
    _, df_use = calculer_kpis(df, filtres)
    st.subheader("Points necessitant une intervention")

    df_prio = df_use[df_use["priorite_prediction"].isin(["Elevée", "Urgente"])].copy()
    if df_prio.empty:
        st.success("Aucun point prioritaire pour la periode selectionnee.")
        return

    ordre_map = {p: i for i, p in enumerate(ORDRE_PRIORITE)}
    df_prio["_ord"] = df_prio["priorite_prediction"].map(ordre_map)
    df_prio = df_prio.sort_values(["_ord", "fillRate_predit"], ascending=[True, False]).drop(columns="_ord")

    st.markdown(f"**{len(df_prio)} point(s)** classés Elevee ou Urgente.")
    top10 = df_prio.head(10)
    st.dataframe(
        top10[["id_point", "fillRate", "fillRate_predit", "risque_debordement", "priorite_prediction", "action_recommandee"]]
        .style.map(style_table, subset=["priorite_prediction"])
        .format({"fillRate": "{:.1f}%", "fillRate_predit": "{:.1f}%", "risque_debordement": "{:,.0f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Les 10 points les plus critiques")
    carte = construire_carte(top10)
    if carte is not None:
        st_folium(carte, width="100%", height=450)


def page_analyse_predictive(contexte):
    st.subheader("Analyse predictive - le modele de Machine Learning")

    st.markdown(
        """
        Le modele estime le niveau de remplissage futur d'un point
        a partir des informations disponibles au moment de la prediction.
        """
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Variable cible")
        st.markdown("`fillRate_target_t_plus_1` : taux de remplissage du point le lendemain.")
        st.markdown("### Modele")
        st.markdown("**Gradient Boosting** - modele de reference actuel (regression supervisee).")

    with c2:
        st.markdown("### Performances du modele")
        if contexte.get("metrics"):
            m = contexte["metrics"]
            a, b = st.columns(2)
            a.metric("R²", f"{m['r2']:.3f}")
            b.metric("RMSE", f"{m['rmse']:.2f}")
            a.metric("MAE", f"{m['mae']:.2f}")
            b.metric("MAPE", f"{m['mape']:.3f}")
        else:
            st.info("Métriques non disponibles : fichier results/comparaison_modeles.xlsx introuvable.")
            a, b = st.columns(2)
            a.metric("R²", "0.775")
            b.metric("RMSE", "8.06")
            a.metric("MAE", "6.24")

    st.markdown("---")
    st.markdown("### Simulation IA interactive")

    if contexte.get("model") is None:
        st.warning("Le modele n'est pas disponible, la simulation est desactivee.")
    else:
        try:
            ml_df = load_ml_data()
        except FileNotFoundError as e:
            st.error(str(e))
            ml_df = None

        if ml_df is not None:
            st.markdown(
                "Choisissez un point et une date, puis ajustez les parametres "
                "operationnels pour observer l'impact sur la prediction."
            )

            points_ml = sorted(ml_df["id_point"].unique())
            dates_ml = sorted(ml_df["date_collecte"].unique(), reverse=True)

            col_p, col_d = st.columns(2)
            with col_p:
                point_sel = st.selectbox("Point de regroupement", options=points_ml)
            with col_d:
                date_sel = st.selectbox(
                    "Date de la prediction",
                    options=dates_ml,
                    index=0,
                    format_func=lambda d: d.strftime("%d/%m/%Y"),
                )

            try:
                ligne_ml = extraire_ligne_ml(ml_df, point_sel, date_sel)
                base_predit, base_priorite, base_action, _ = simuler_prediction(ligne_ml)

                st.markdown("#### Parametres operationnels (scenario)")
                ajustements = {}
                with st.expander("Ajuster les parametres (what-if)", expanded=True):
                    for colonne, (mini, maxi, pas) in FEATURES_SIMULABLES.items():
                        if colonne in ligne_ml.index:
                            valeur_slider, mini_s, maxi_s, pas_s = cohercer_slider(
                                ligne_ml[colonne], mini, maxi, pas
                            )
                            ajustements[colonne] = st.slider(
                                colonne,
                                min_value=mini_s,
                                max_value=maxi_s,
                                value=valeur_slider,
                                step=pas_s,
                            )

                predit, priorite, action, _ = simuler_prediction(ligne_ml, ajustements)

                st.markdown("#### Resultat de la prediction IA")
                rc1, rc2, rc3, rc4 = st.columns(4)
                with rc1:
                    carte_kpi("FillRate actuel", f"{ligne_ml['fillRate']:.1f}", "%")
                with rc2:
                    carte_kpi(
                        "FillRate predit (IA)",
                        f"{predit:.1f}",
                        "%",
                        sous_texte=f"reference : {base_predit:.1f}%",
                    )
                couleur = COULEURS_PRIORITE.get(priorite, "#78909C")
                with rc3:
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-label">Priorite predite</div>
                            <div class="kpi-value" style="color:{couleur};">{badge_priorite(priorite)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with rc4:
                    st.markdown(
                        f"""
                        <div class="kpi-card">
                            <div class="kpi-label">Action recommandee</div>
                            <div class="kpi-value" style="font-size:1.1rem; color:var(--vert-700);">{action}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("#### Pipeline IA : de la donnee a l'action")
                etapes = [
                    ("1. Modele", "Gradient Boosting"),
                    ("2. Prediction", f"{predit:.1f}%"),
                    ("3. Priorite", badge_priorite(priorite)),
                    ("4. Action", action),
                ]
                cols_etapes = st.columns(len(etapes))
                for col, (titre, valeur) in zip(cols_etapes, etapes):
                    with col:
                        st.markdown(
                            f"""
                            <div class="etape-pipeline">
                                <div class="et-titre">{titre}</div>
                                <div class="et-valeur">{valeur}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                st.markdown("---")

            except ValueError as e:
                st.warning(str(e))

    st.markdown("### Distinction importante")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            #### PREDICTION ML
            Le modele **Gradient Boosting** estime `fillRate_predit`.
            C'est un apprentissage statistique sur les donnees historiques.
            """
        )
    with col2:
        st.markdown(
            """
            #### DECISION / PRIORISATION METIER
            La priorite et l'action recommandee sont obtenues par des **regles simples** :
            - predit < 40 % → Faible / Surveillance simple
            - predit < 70 % → Moyenne / Collecte sous 48h
            - predit < 90 % → Elevee / Collecte aujourd'hui
            - predit >= 90 % → Urgente / Collecte immediate
            """
        )

    if contexte.get("importance") is not None:
        st.markdown("### Importance des variables (top 10)")
        imp = contexte["importance"].head(10)
        fig = px.bar(
            imp,
            x="Importance",
            y="Variable",
            orientation="h",
            title="Variables les plus influentes sur la prediction",
        )
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)


def page_donnees(df):
    st.subheader("Donnees du systeme")
    st.markdown(f"**{len(df):,} enregistrements** - **{df['id_point'].nunique()} points** - "
                f"du {pd.to_datetime(df['date_collecte']).min().date()} au {pd.to_datetime(df['date_collecte']).max().date()}")

    manquantes = verifier_colonnes(df)
    if manquantes:
        st.warning("Colonnes absentes : " + ", ".join(manquantes))

    onglet1, onglet2 = st.tabs(["Apercu", "Statistiques"])
    with onglet1:
        st.dataframe(df.head(1000), use_container_width=True, hide_index=True)
    with onglet2:
        colonnes_num = df.select_dtypes(include=[np.number]).columns
        st.dataframe(df[colonnes_num].describe().T, use_container_width=True)


def page_apropos():
    st.subheader("A propos du systeme")

    st.markdown(
        """
        **ECOSYS / ALPHA TRANSIT** est un systeme intelligent de gestion
        de la pre-collecte des dechets pour la ville de Douala.

        ### Flux de traitement

        ```
        Donnees de collecte (historiques + actuelles)
                    |
                    v
        Modele Machine Learning (Gradient Boosting)
                    |
                    v
        FillRate futur predit  (fillRate_predit)
                    |
                    v
        Moteur de priorisation (regles metier)
                    |
                    v
        Action recommandee (collecte, planification, surveillance)
                    |
                    v
        Tableau de bord (visualisation et aide a la decision)
        ```

        ### Architecture

        ```
        app.py                 Tableau de bord Streamlit
        utils/data_loader.py   Chargement des donnees, modele et metriques
        utils/prediction.py    Prediction ML + regles de priorisation
        models/                Modele Gradient Boosting entraine
        data/                  Datasets (collecte, ML)
        results/               Metriques et importances de variables
        ```
        """
    )

    st.markdown(
        """
        ### Evolutions prevues
        Le systeme pourra etre etendu avec :
        donnees reelles Alpha Transit, frequence des passages, formules
        d'abonnement, nombre de menages, poids collecte, meteo reelle,
        evenements speciaux, optimisation des tournees, suivi HYSACAM,
        module financier et donnees en temps reel.
        """
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    afficher_entete()

    try:
        df = charger_donnees()
    except FileNotFoundError as e:
        st.error(str(e))
        st.info("Verifiez que le fichier de donnees est bien present dans le projet.")
        st.stop()

    contexte = charger_contexte()

    with st.sidebar:
        st.markdown("## Navigation")
        page = st.radio("Choisir une page", PAGES, label_visibility="collapsed")

    filtres = afficher_filtres(df)

    if page == "Accueil":
        page_accueil(df, filtres)
    elif page == "Supervision":
        page_supervision(df, filtres)
    elif page == "Points prioritaires":
        page_prioritaires(df, filtres)
    elif page == "Analyse predictive":
        page_analyse_predictive(contexte)
    elif page == "Interface metier":
        page_metier()
    elif page == "Donnees":
        page_donnees(df)
    elif page == "A propos du systeme":
        page_apropos()


if __name__ == "__main__":
    main()
