"""Interface metier ECOSYS - page Streamlit a 7 onglets."""

import datetime

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from utils.data_loader import load_dashboard_data
from utils.metier_db import (
    INT2Q,
    SECTEUR_TYPES,
    charger_abonnements,
    charger_collectes,
    charger_evenements,
    charger_passages,
    charger_precollecteurs,
    charger_sacs_bacs,
    charger_secteurs,
    init_db,
    inserer_abonnement,
    inserer_collecte,
    inserer_conteneur,
    inserer_evenement,
    inserer_passage,
    inserer_precollecteur,
    inserer_secteur,
    seed_db,
    stats_metier,
)
from utils.prediction import (
    COULEURS_PRIORITE,
    definir_priorite,
    estimer_risque_debordement,
    generer_recommandation,
    normaliser_priorite,
    simuler_prediction,
)
from utils.ui import badge_priorite, carte_kpi

COULEURS_SECTEURS = {
    q: c for q, c in zip(
        sorted(SECTEUR_TYPES.keys()),
        px.colors.qualitative.Plotly * 3,
    )
}


def assurer_base():
    init_db()
    if seed_db():
        st.success("Base metier initialisee avec les donnees simulees (data/ecosys.db).")


def joindre_priorite_ia(df, colonne_point):
    """Joint les predictions IA (fillRate_predit, priorite, risque, action) au df métier.

    Colonnes ajoutées : fillRate, fillRate_predit, priorite_prediction,
    action_recommandnee, risque_debordement.
    """
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        if "action_recommandee" in dash.columns and "action_recommandnee" not in dash.columns:
            dash = dash.rename(columns={"action_recommandee": "action_recommandnee"})
        if "action_recommandnee" not in dash.columns and "fillRate_predit" in dash.columns:
            dash["action_recommandnee"] = dash["fillRate_predit"].apply(generer_recommandation)
        cols = ["id_point", "fillRate", "fillRate_predit", "priorite_prediction",
                "action_recommandnee", "risque_debordement", "latitude", "longitude"]
        cols = [c for c in cols if c in dash.columns]
        dash = dash[cols]
        df = df.merge(
            dash, left_on=colonne_point, right_on="id_point", how="left"
        ).drop(columns="id_point", errors="ignore")
    except Exception:
        pass
    return df


def badge_priorite_ia(id_point):
    """Rend un badge priorite IA HTML pour un point. Gris si absent du dashboard."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        ligne = dash[dash["id_point"] == id_point]
        if ligne.empty:
            return '<span class="badge" style="background:#F5F7FA;color:#78909C;">IA — N/A</span>'
        priorite = str(ligne.iloc[0].get("priorite_prediction", "Faible")).strip()
        priorite = normaliser_priorite(priorite)
        badge_html = badge_priorite(priorite)
        return f'{badge_html} <span style="font-size:0.7rem;color:#8A9499;">IA</span>'
    except Exception:
        return '<span class="badge" style="background:#F5F7FA;color:#78909C;">IA — N/A</span>'


def suggestion_action_ia(id_point):
    """Suggère une action pour un point basée sur la priorite IA.

    Retourne (message, action_ia, est_urgent).
    """
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
        ligne = dash[dash["id_point"] == id_point]
        if ligne.empty:
            return "", "", False
        row = ligne.iloc[0]
        fillrate = float(row.get("fillRate_predit", 0))
        priorite = normaliser_priorite(str(row.get("priorite_prediction", "Faible")))
        action = str(row.get("action_recommandnee", generer_recommandation(fillrate)))
        est_urgent = priorite in ("Urgente", "Elevée")
        if est_urgent:
            message = f"Ce point est prédit **{priorite}**" + (
                f" (fillRate prédit {fillrate:.0f}%) → **{action}** ?"
                if fillrate > 0 else f" → **{action}** ?"
            )
        else:
            message = f"Point **{priorite.lower()}**" + (
                f" (fillRate prédit {fillrate:.0f}%) → {action}."
                if fillrate > 0 else f" → {action}."
            )
        return message, action, est_urgent
    except Exception:
        return "", "", False


# ---------------------------------------------------------------------------
# KPIs IA
# ---------------------------------------------------------------------------

_AUCUNE = {"fill_moyen_predit": 0, "nb_urgents": 0, "nb_eleves": 0, "taux_risque": 0.0}


def kpi_ia_secteur(nom_secteur):
    """Calcule les KPIs IA pour les points d’un secteur."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
    except Exception:
        return dict(_AUCUNE)
    dash["quartier"] = dash["id_point"].map(INT2Q).fillna("Inconnu")
    pts = dash[dash["quartier"] == nom_secteur]
    if pts.empty or "fillRate_predit" not in pts.columns:
        return dict(_AUCUNE)
    priorites = pts["priorite_prediction"].apply(normaliser_priorite)
    fill_moyen = float(pts["fillRate_predit"].mean())
    nb_urgents = int((priorites == "Urgente").sum())
    nb_eleves = int((priorites == "Elevée").sum())
    nb_total = len(pts)
    taux_risque = round((nb_urgents + nb_eleves) / nb_total * 100, 1) if nb_total > 0 else 0.0
    return {
        "fill_moyen_predit": round(fill_moyen, 1),
        "nb_urgents": nb_urgents,
        "nb_eleves": nb_eleves,
        "taux_risque": taux_risque,
    }


def simulateur_ia(id_point, date_ref):
    """Simule un what-if : +3 précollecteurs dispo, montre l’impact sur le fill rate."""
    try:
        from utils.data_loader import load_ml_data
        from utils.prediction import extraire_ligne_ml, simuler_prediction
        ml_df = load_ml_data()
        ligne = extraire_ligne_ml(ml_df, id_point, date_ref)
        ajustements = {"nb_precollecteurs_dispo": 3}
        fill_avant, prio_avant, _, _ = simuler_prediction(ligne)
        fill_apres, prio_apres, action_apres, _ = simuler_prediction(ligne, ajustements)
        return {
            "fillrate_avant": round(float(fill_avant), 1),
            "fillrate_apres": round(float(fill_apres), 1),
            "priorite_avant": prio_avant,
            "priorite_apres": prio_apres,
            "action": action_apres,
        }
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Carte secteurs
# ---------------------------------------------------------------------------

def construire_carte_secteurs():
    try:
        dash = load_dashboard_data()
    except Exception:
        return None
    if not {"id_point", "latitude", "longitude"}.issubset(dash.columns):
        return None
    pts = (
        dash.dropna(subset=["latitude", "longitude"])
        .groupby("id_point", as_index=False)
        .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"))
    )
    pts["secteur"] = pts["id_point"].map(INT2Q).fillna("Inconnu")
    if pts.empty:
        return None
    carte = folium.Map(
        location=[pts["latitude"].mean(), pts["longitude"].mean()],
        zoom_start=12,
        control_scale=True,
    )
    for _, r in pts.iterrows():
        couleur = COULEURS_SECTEURS.get(r["secteur"], "#607D8B")
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=7,
            color=couleur,
            fill=True,
            fill_color=couleur,
            fill_opacity=0.75,
            popup=f"Point #{int(r['id_point'])} - {r['secteur']}",
            tooltip=r["secteur"],
        ).add_to(carte)
    return carte


def construire_carte_secteurs_ia():
    """Carte des secteurs avec couleur basee sur priorite IA."""
    try:
        dash = load_dashboard_data().drop_duplicates("id_point")
    except Exception:
        return None
    if not {"id_point", "latitude", "longitude", "fillRate_predit", "priorite_prediction"}.issubset(dash.columns):
        return None
    pts = dash.dropna(subset=["latitude", "longitude"]).copy()
    pts["secteur"] = pts["id_point"].map(INT2Q).fillna("Inconnu")
    pts["priorite"] = pts["priorite_prediction"].apply(normaliser_priorite)
    if pts.empty:
        return None
    carte = folium.Map(
        location=[pts["latitude"].mean(), pts["longitude"].mean()],
        zoom_start=12, control_scale=True,
    )
    for _, r in pts.iterrows():
        priorite = r["priorite"]
        couleur = COULEURS_PRIORITE.get(priorite, "#78909C")
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=7,
            color=couleur,
            fill=True,
            fill_color=couleur,
            fill_opacity=0.75,
            popup=(f"Point #{int(r['id_point'])} — {r['secteur']} — "
                   f"IA: {priorite} ({r['fillRate_predit']:.0f}%)"),
            tooltip=f"{priorite} — {r['secteur']}",
        ).add_to(carte)
    return carte


def _lignes_kpi(valeurs):
    cols = st.columns(len(valeurs))
    for col, (label, valeur, suffixe) in zip(cols, valeurs):
        with col:
            carte_kpi(label, valeur, suffixe)


def _options_precollecteurs():
    df = charger_precollecteurs()
    return {
        f"{int(r['id_precollecteur'])} - {r['nom']}": int(r["id_precollecteur"])
        for _, r in df.iterrows()
    }


def _options_secteurs():
    df = charger_secteurs()
    return {
        f"{int(r['id_secteur'])} - {r['nom']}": int(r["id_secteur"])
        for _, r in df.iterrows()
    }


# ---------------------------------------------------------------------------
# Onglets
# ---------------------------------------------------------------------------


def onglet_secteurs(stats):
    df = charger_secteurs()
    if df.empty:
        st.info("Aucun secteur. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Secteurs", f"{stats['secteurs']}", ""),
        ("Points couverts", f"{int(df['nb_points'].sum())}", ""),
        ("Responsables", f"{df['responsable'].nunique()}", ""),
    ])

    # KPIs IA — secteur avec le plus de points
    nom_ref = df.iloc[0]["nom"]
    kpi_ia = kpi_ia_secteur(nom_ref)
    c1, c2, c3 = st.columns(3)
    with c1:
        carte_kpi("FillRate IA moyen", f"{kpi_ia['fill_moyen_predit']:.1f}", "%",
                  sous_texte=f"sur {nom_ref}")
    with c2:
        carte_kpi("Points urgents IA", f"{kpi_ia['nb_urgents']}", "")
    with c3:
        carte_kpi("Taux de risque IA", f"{kpi_ia['taux_risque']:.0f}", "%")

    st.markdown("#### Carte des secteurs (points de regroupement)")
    carte = construire_carte_secteurs_ia()
    if carte is not None:
        st_folium(carte, width="100%", height=420)
    else:
        st.info("Carte indisponible (points non geolocalisables).")

    st.markdown("#### Repartition par type")
    rep = df["type_secteur"].value_counts().reset_index()
    rep.columns = ["type_secteur", "nombre"]
    fig = px.bar(rep, x="type_secteur", y="nombre",
                 title="Nombre de secteurs par type", color="type_secteur")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Liste des secteurs")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un secteur")
    with st.form("form_secteur"):
        nom = st.text_input("Nom du secteur")
        type_s = st.selectbox("Type", ["marche", "residentiel", "commercial", "mixte"])
        nb_pts = st.number_input("Nombre de points", 0, 100, 1)
        responsable = st.text_input("Responsable")
        if st.form_submit_button("Enregistrer"):
            if not nom.strip():
                st.warning("Le nom est requis.")
            else:
                inserer_secteur(nom.strip(), nom.strip(), type_s, int(nb_pts),
                                responsable.strip())
                st.success(f"Secteur '{nom.strip()}' ajoute.")
                st.rerun()


def onglet_abonnements(stats):
    df = charger_abonnements()
    if df.empty:
        st.info("Aucun abonnement. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Abonnements", f"{stats['abonnements']:,}", ""),
        ("Actifs", f"{stats['abonnements_actifs']:,}", ""),
        ("Montant moyen", f"{df['montant_mensuel'].mean():,.0f}", "FCFA"),
    ])

    rep = df["type_abonnement"].value_counts().reset_index()
    rep.columns = ["type_abonnement", "nombre"]
    fig = px.pie(rep, names="type_abonnement", values="nombre",
                 title="Abonnements par type")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Liste des abonnements")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un abonnement")
    with st.form("form_abonnement"):
        options_s = _options_secteurs()
        col1, col2 = st.columns(2)
        with col1:
            secteur = st.selectbox("Secteur", list(options_s.keys()))
            client = st.text_input("Client")
            type_ab = st.selectbox("Type", ["menage", "entreprise", "commerce"])
        with col2:
            frequence = st.selectbox("Frequence",
                                     ["quotidien", "hebdomadaire", "sur_appel"])
            debut = st.date_input("Date de debut", value=datetime.date.today().replace(day=1))
            statut = st.selectbox("Statut", ["actif", "suspendu", "expire"])
            montant = st.number_input("Montant mensuel (FCFA)", 0.0, 500000.0, 5000.0)
        if st.form_submit_button("Enregistrer"):
            if not client.strip():
                st.warning("Le nom du client est requis.")
            else:
                inserer_abonnement(options_s[secteur], client.strip(), type_ab,
                                   frequence, debut.strftime("%Y-%m-%d"), statut,
                                   float(montant))
                st.success("Abonnement ajoute.")
                st.rerun()


def onglet_precollecteurs(stats):
    df = charger_precollecteurs()
    if df.empty:
        st.info("Aucun precollecteur. Lancez l'initialisation de la base.")
        return
    dispo = df["disponible"].astype(int).sum() if "disponible" in df else 0
    _lignes_kpi([
        ("Precollecteurs", f"{stats['precollecteurs']:,}", ""),
        ("Disponibles", f"{dispo:,}", ""),
        ("Sacs transportables (moy.)", f"{df['capacite_sacs'].mean():.0f}", ""),
    ])

    rep = df["equipement"].value_counts().reset_index()
    rep.columns = ["equipement", "nombre"]
    fig = px.bar(rep, x="equipement", y="nombre", title="Precollecteurs par equipement")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Liste des precollecteurs")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un precollecteur")
    with st.form("form_precollecteur"):
        options_s = _options_secteurs()
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom")
            secteur = st.selectbox("Secteur", list(options_s.keys()))
        with col2:
            equipement = st.selectbox("Equipement",
                                      ["tricycle", "chariot", "pousse_pousse"])
            cap_sacs = st.number_input("Capacite (sacs)", 5, 50, 15)
            tel = st.text_input("Telephone")
        statut = st.radio("Disponible", ["oui", "non"], horizontal=True)
        if st.form_submit_button("Enregistrer"):
            if not nom.strip():
                st.warning("Le nom est requis.")
            else:
                inserer_precollecteur(nom.strip(), options_s[secteur], equipement,
                                      int(cap_sacs), 1 if statut == "oui" else 0,
                                      tel.strip())
                st.success("Precollecteur ajoute.")
                st.rerun()


def onglet_sacs_bacs(stats):
    df = charger_sacs_bacs()
    if df.empty:
        st.info("Aucun conteneur. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Conteneurs", f"{stats['conteneurs']:,}", ""),
        ("Endommages", f"{stats['conteneurs_endommages']:,}", ""),
        ("Capacite moyenne", f"{df['capacite_litres'].mean():,.0f}", "L"),
    ])

    # IA — rejoindre priorite IA et risque
    df_ia = joindre_priorite_ia(df, "id_point")
    if "fillRate_predit" in df_ia.columns:
        df_ia["risque_ia"] = df_ia["fillRate_predit"].apply(
            lambda v: estimer_risque_debordement(v) if pd.notna(v) else "faible"
        )
        nb_critique = int((df_ia["risque_ia"] == "critique").sum()) if "risque_ia" in df_ia else 0
        nb_eleve = int((df_ia["risque_ia"] == "eleve").sum()) if "risque_ia" in df_ia else 0
        c1, c2 = st.columns(2)
        with c1:
            carte_kpi("Conteneurs critiques (IA)", f"{nb_critique}", "")
        with c2:
            carte_kpi("Conteneurs haut risque (IA)", f"{nb_eleve}", "")

        st.markdown("#### Liste des sacs / bacs — avec priorite IA")
        cols_aff = ["id_conteneur", "id_point", "type_conteneur", "capacite_litres",
                    "etat", "fillRate_predit", "priorite_prediction", "risque_ia"]
        cols_aff = [c for c in cols_aff if c in df_ia.columns]
        st.dataframe(df_ia[cols_aff], use_container_width=True, hide_index=True)
    else:
        st.info("Priorite IA non disponible (dashboard absent).")
        st.markdown("#### Liste des sacs / bacs")
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un conteneur")
    with st.form("form_conteneur"):
        options_s = _options_secteurs()
        col1, col2 = st.columns(2)
        with col1:
            point = st.number_input("Point de regroupement (id)", 0, 79, 0)
            secteur = st.selectbox("Secteur", list(options_s.keys()))
        with col2:
            type_c = st.selectbox("Type", ["sac_100l", "bac_240l", "benne"])
            etat = st.selectbox("Etat", ["bon", "use", "endommage"])
        # suggestion IA
        msg, action_ia, urgent = suggestion_action_ia(int(point))
        if msg:
            if urgent:
                st.warning(msg)
            else:
                st.info(msg)
        if st.form_submit_button("Enregistrer"):
            cap = {"sac_100l": 100, "bac_240l": 240,
                   "benne": 1100}.get(type_c, 100)
            inserer_conteneur(int(point), options_s[secteur], type_c, cap, etat)
            st.success("Conteneur ajoute.")
            st.rerun()


def onglet_passages(stats):
    df = charger_passages()
    if df.empty:
        st.info("Aucun passage. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Passages", f"{stats['passages']:,}", ""),
        ("Retardes", f"{stats['passages_retardes']:,}", ""),
        ("Quantite totale", f"{df['quantite_kg'].sum():,.0f}", "kg"),
    ])

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date_passage"])
    mensuel = temp.set_index("date")["quantite_kg"].resample("ME").sum().reset_index()
    fig = px.bar(mensuel, x="date", y="quantite_kg",
                 title="Quantite collectee par mois (passages)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Filtres")
    f1, f2 = st.columns(2)
    with f1:
        pt = st.selectbox("Point",
                          ["Tous"] + [str(p) for p in sorted(df["id_point"].unique())])
    with f2:
        statut_f = st.selectbox("Statut", ["Tous", "realise", "retarde", "annule"])
    vue = df.copy()
    if pt != "Tous":
        vue = vue[vue["id_point"] == int(pt)]
    if statut_f != "Tous":
        vue = vue[vue["statut"] == statut_f]
    vue["date_passage"] = pd.to_datetime(vue["date_passage"])
    vue = vue.sort_values("date_passage", ascending=False)
    vue = joindre_priorite_ia(vue, "id_point")
    st.dataframe(vue, use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un passage")
    with st.form("form_passage"):
        options_pc = _options_precollecteurs()
        col1, col2 = st.columns(2)
        with col1:
            point = st.selectbox("Point",
                                 [str(p) for p in sorted(df["id_point"].unique())])
            precollecteur = st.selectbox("Precollecteur", list(options_pc.keys()))
        with col2:
            date_j = st.date_input("Date")
            heure = st.time_input("Heure", value=datetime.time(8, 0))
        qte = st.number_input("Quantite (kg)", 0.0, 1000.0, 50.0, 1.0)
        statut_p = st.selectbox("Statut du passage", ["realise", "retarde", "annule"])
        if st.form_submit_button("Enregistrer"):
            d = datetime.datetime.combine(date_j, heure)
            inserer_passage(int(point), options_pc[precollecteur],
                            d.strftime("%Y-%m-%d %H:%M:%S"), float(qte), statut_p)
            st.success("Passage ajoute.")
            st.rerun()


def onglet_collectes(stats):
    df = charger_collectes()
    if df.empty:
        st.info("Aucune collecte. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Collectes", f"{stats['collectes']:,}", ""),
        ("Realisees", f"{stats['collectes_realisees']:,}", ""),
        ("Volume total", f"{df['volume_litres'].sum():,.0f}", "L"),
    ])

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date_collecte"])
    mensuel = temp.set_index("date")["volume_litres"].resample("ME").sum().reset_index()
    fig = px.bar(mensuel, x="date", y="volume_litres",
                 title="Volume collecte par mois")
    st.plotly_chart(fig, use_container_width=True)

    rep = df["type_collecte"].value_counts().reset_index()
    rep.columns = ["type_collecte", "nombre"]
    fig2 = px.pie(rep, names="type_collecte", values="nombre",
                  title="Collectes : precollecte vs principale")
    st.plotly_chart(fig2, use_container_width=True)

    # IA — enrichir le tableau avec priorite IA
    df_ia = joindre_priorite_ia(df, "id_point")
    st.markdown("#### Liste des collectes — avec priorite IA")
    if "priorite_prediction" in df_ia.columns:
        st.dataframe(
            df_ia.sort_values("date_collecte", ascending=False),
            use_container_width=True, hide_index=True,
        )
    else:
        st.dataframe(
            df.sort_values("date_collecte", ascending=False),
            use_container_width=True, hide_index=True,
        )

    st.markdown("#### Ajouter une collecte")
    with st.form("form_collecte"):
        options_pc = _options_precollecteurs()
        col1, col2 = st.columns(2)
        with col1:
            point = st.selectbox("Point",
                                 [str(p) for p in sorted(df["id_point"].unique())])
            precollecteur = st.selectbox("Precollecteur", list(options_pc.keys()))
        with col2:
            date_j = st.date_input("Date de collecte")
            heure = st.time_input("Heure de collecte", value=datetime.time(8, 0))
        type_c = st.selectbox("Type", ["precollecte", "principale"])
        vol = st.number_input("Volume (litres)", 0.0, 50000.0, 1000.0)
        duree = st.number_input("Duree (minutes)", 5, 300, 45)
        statut_c = st.selectbox("Statut", ["realisee", "planifiee", "annulee"])
        # IA — suggestion + what-if
        id_pt = int(point)
        msg, action_ia, urgent = suggestion_action_ia(id_pt)
        if msg:
            if urgent:
                st.warning(msg)
            else:
                st.info(msg)
        sim = simulateur_ia(id_pt, date_j.strftime("%Y-%m-%d"))
        if sim:
            st.markdown("##### Simulation IA (what-if : +3 precollecteurs dispo)")
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                carte_kpi("FillRate avant", f"{sim['fillrate_avant']:.1f}", "%")
            with s2:
                carte_kpi("FillRate après", f"{sim['fillrate_apres']:.1f}", "%",
                          sous_texte=f"delta: {sim['fillrate_apres'] - sim['fillrate_avant']:+.1f}%")
            with s3:
                st.markdown(badge_priorite(sim["priorite_avant"]), unsafe_allow_html=True)
            with s4:
                st.markdown(badge_priorite(sim["priorite_apres"]), unsafe_allow_html=True)
        if st.form_submit_button("Enregistrer"):
            d = datetime.datetime.combine(date_j, heure)
            inserer_collecte(id_pt, d.strftime("%Y-%m-%d %H:%M:%S"), type_c,
                             float(vol), options_pc[precollecteur], statut_c,
                             int(duree))
            st.success("Collecte ajoutee.")
            st.rerun()


def onglet_evenements(stats):
    df = charger_evenements()
    if df.empty:
        st.info("Aucun evenement. Lancez l'initialisation de la base.")
        return
    _lignes_kpi([
        ("Evenements", f"{stats['evenements']:,}", ""),
        ("Haut impact", f"{stats['evenements_haut_impact']:,}", ""),
        ("Types", f"{df['type_evenement'].nunique()}", ""),
    ])

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date"])
    fig = px.timeline(temp.sort_values("date"),
                      x_start="date", x_end="date",
                      y="type_evenement", color="impact",
                      title="Evenements sur la periode")
    fig.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Liste des evenements")
    st.dataframe(df.sort_values("date", ascending=False),
                 use_container_width=True, hide_index=True)

    st.markdown("#### Ajouter un evenement")
    with st.form("form_evenement"):
        options_s = _options_secteurs()
        col1, col2 = st.columns(2)
        with col1:
            date_j = st.date_input("Date de l'evenement")
            type_e = st.selectbox("Type",
                                  ["marche", "fete", "evenement_sportif",
                                   "incident", "alerte"])
        with col2:
            secteur = st.selectbox("Secteur", list(options_s.keys()))
            impact = st.selectbox("Impact", ["haut", "moyen", "faible"])
        description = st.text_area("Description")
        statut_e = st.selectbox("Statut", ["prevu", "en_cours", "termine"])
        if st.form_submit_button("Enregistrer"):
            if not description.strip():
                st.warning("La description est requise.")
            else:
                inserer_evenement(date_j.strftime("%Y-%m-%d"), type_e,
                                  options_s[secteur], description.strip(),
                                  impact, statut_e)
                st.success("Evenement ajoute.")
                st.rerun()


# ---------------------------------------------------------------------------
# Page principale
# ---------------------------------------------------------------------------


def page_metier():
    st.subheader("Interface metier - fonctionnement Alpha Transit")
    st.markdown(
        "Vue operationnelle : abonnements, passages, precollecteurs, "
        "secteurs, sacs/bacs, collectes et evenements. Les donnees simulees "
        "sont liees aux points de regroupement et a la prediction IA."
    )
    assurer_base()
    stats = stats_metier()

    (t1, t2, t3, t4, t5, t6, t7) = st.tabs([
        "Secteurs", "Abonnements", "Precollecteurs", "Sacs / Bacs",
        "Passages", "Collecte", "Evenements",
    ])
    with t1:
        onglet_secteurs(stats)
    with t2:
        onglet_abonnements(stats)
    with t3:
        onglet_precollecteurs(stats)
    with t4:
        onglet_sacs_bacs(stats)
    with t5:
        onglet_passages(stats)
    with t6:
        onglet_collectes(stats)
    with t7:
        onglet_evenements(stats)
