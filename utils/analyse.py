"""Analyse operationnelle ECOSYS.

Fonctions pures qui transforment un DataFrame filtre en phrases d'analyse
concretes (insights) : ce qu'un analyste data ecrirait apres lecture des
chiffres. Aucune dependance Streamlit - testable unitairement.
"""

import pandas as pd

SEUIL_URGENCE = 90.0
SEUIL_HAUSSE = 5.0


def _taux(df, colonne):
    """Part (en %) des lignes ou la colonne booleenne est True."""
    if df.empty or colonne not in df.columns:
        return 0.0
    return float(df[colonne].astype(bool).mean() * 100)


def analyser_priorites(df):
    """Repartition des priorites sur la periode filtree."""
    if df.empty or "priorite_prediction" not in df.columns:
        return []
    lignes = []
    total = len(df)
    urgente = int((df["priorite_prediction"] == "Urgente").sum())
    elevee = int((df["priorite_prediction"] == "Elevée").sum())
    part_urgente = urgente / total * 100 if total else 0.0
    part_elevee = elevee / total * 100 if total else 0.0

    if urgente or elevee:
        lignes.append(
            f"{urgente + elevee} point(s) ({part_urgente + part_elevee:.0f}%) sont en "
            f"priorite Elevee ou Urgente, dont {urgente} en situation Urgente "
            f"({part_urgente:.0f}%)."
        )
        if part_urgente > 30:
            lignes.append(
                "Plus d'un tiers des points sont en urgence : prevoir une "
                "mobilisation immediate des precollecteurs disponibles."
            )
    else:
        lignes.append("Aucun point en priorite Elevee ou Urgente sur la periode : "
                      "la charge est sous controle.")
    return lignes


def analyser_tendance(df):
    """Tendance du remplissage : actuel vs predit."""
    if df.empty or not {"fillRate", "fillRate_predit"}.issubset(df.columns):
        return []
    lignes = []
    actuel = df["fillRate"].mean()
    predit = df["fillRate_predit"].mean()
    ecart = predit - actuel

    lignes.append(
        f"Le remplissage moyen passe de {actuel:.1f}% a {predit:.1f}% en "
        f"projection (variation {ecart:+.1f} pt)."
    )
    if ecart > SEUIL_HAUSSE:
        hausses = int((df["fillRate_predit"] - df["fillRate"] > SEUIL_HAUSSE).sum())
        lignes.append(
            f"{hausses} point(s) affichent une hausse prevue de plus de "
            f"{SEUIL_HAUSSE:.0f} pts : anticiper les collectes avant le debordement."
        )
    elif ecart < -SEUIL_HAUSSE:
        lignes.append(
            "La tendance est a la baisse : la pression sur les points diminue, "
            "les tournees peuvent etre maintenues au rythme actuel."
        )
    return lignes


def analyser_points_critiques(df):
    """Points les plus exposes au risque de debordement."""
    if df.empty or "risque_debordement" not in df.columns:
        return []
    lignes = []
    pire = df.loc[df["risque_debordement"].idxmax()]
    lignes.append(
        f"Le point #{int(pire['id_point'])} concentre le risque de debordement "
        f"le plus eleve ({pire['risque_debordement']:,.0f}) avec un remplissage "
        f"projete a {pire.get('fillRate_predit', float('nan')):.1f}%."
    )
    return lignes


def analyser_pression_citoyenne(df):
    """Signalements et plaintes citoyens : points les plus signales."""
    if df.empty:
        return []
    lignes = []
    signalements = int(df["nb_signalements_citoyens"].sum()) if "nb_signalements_citoyens" in df else 0
    plaintes = int(df["nb_plaintes"].sum()) if "nb_plaintes" in df else 0
    if signalements or plaintes:
        top_sig = df.nlargest(1, "nb_signalements_citoyens") if "nb_signalements_citoyens" in df else None
        ligne = f"{signalements} signalement(s) citoyen(s) et {plaintes} plainte(s) recus."
        if top_sig is not None and int(top_sig.iloc[0]["nb_signalements_citoyens"]) > 0:
            ligne += (
                f" Le point #{int(top_sig.iloc[0]['id_point'])} est le plus "
                f"signale ({int(top_sig.iloc[0]['nb_signalements_citoyens'])} signalement(s))."
            )
        lignes.append(ligne)
    return lignes


def generer_synthese(df):
    """Synthese operationnelle complete : liste de phrases d'analyse.

    Chaque element est un tuple (type, texte) ou type est
    'alerte' | 'info' | 'ok' pour orienter l'affichage.
    """
    if df.empty:
        return [("info", "Aucune donnee sur la periode filtree : ajuster les filtres.")]
    total = len(df)
    nb_points = int(df["id_point"].nunique())
    synthese = [
        ("info", f"Analyse portant sur {total} enregistrement(s), {nb_points} point(s) de regroupement.")
    ]
    synthese += [("alert", t) for t in analyser_priorites(df)]
    synthese += [("info", t) for t in analyser_tendance(df)]
    synthese += [("alert", t) for t in analyser_points_critiques(df)]
    synthese += [("info", t) for t in analyser_pression_citoyenne(df)]
    return synthese
