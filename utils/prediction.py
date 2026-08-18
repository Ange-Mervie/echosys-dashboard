"""Prédiction ML et logique métier de priorisation / recommandation.

Deux niveaux distincts :
- PRÉDICTION ML : le modèle estime fillRate_predit (remplissage futur).
- DÉCISION MÉTIER : des règles simples transforment cette prédiction
  en priorité (priorite_prediction) et en action recommandée.
"""

import numpy as np
import pandas as pd

from utils.data_loader import load_model

ORDRE_PRIORITE = ["Urgente", "Elevée", "Moyenne", "Faible"]
COULEURS_PRIORITE = {
    "Urgente": "#C62828",
    "Elevée": "#E65100",
    "Moyenne": "#F9A825",
    "Faible": "#2E7D32",
}
COULEURS_BADGE = {
    "Urgente": {"fond": "#FDECEC", "texte": "#B71C1C"},
    "Elevée": {"fond": "#FFF0E0", "texte": "#B23C00"},
    "Moyenne": {"fond": "#FFF8E1", "texte": "#7A5B00"},
    "Faible": {"fond": "#E8F5E9", "texte": "#1B5E20"},
}

SEUILS = {"faible": 40, "moyenne": 70, "elevee": 90}


def normaliser_priorite(valeur):
    """Normalise les valeurs de priorité (gère les accents / casse)."""
    if not isinstance(valeur, str):
        return "Faible"
    v = valeur.strip().lower().replace("é", "e")
    if v == "urgente":
        return "Urgente"
    if v == "élevée" or v == "elevée" or v == "elevee":
        return "Elevée"
    if v == "moyenne":
        return "Moyenne"
    return "Faible"


def definir_priorite(fillrate):
    """Règle métier : priorité à partir du fillRate prédit."""
    if fillrate >= SEUILS["elevee"]:
        return "Urgente"
    if fillrate >= SEUILS["moyenne"]:
        return "Elevée"
    if fillrate >= SEUILS["faible"]:
        return "Moyenne"
    return "Faible"


def generer_recommandation(fillrate):
    """Règle métier : action recommandée à partir du fillRate prédit."""
    if fillrate >= SEUILS["elevee"]:
        return "Collecte immédiate"
    if fillrate >= SEUILS["moyenne"]:
        return "Planifier une collecte aujourd'hui"
    if fillrate >= SEUILS["faible"]:
        return "Programmer une collecte sous 48 heures"
    return "Surveillance simple"


def estimer_risque_debordement(fillrate_predit):
    """Catégorise le risque de débordement à partir du fillRate prédit par l'IA."""
    if fillrate_predit >= 90:
        return "critique"
    if fillrate_predit >= 70:
        return "eleve"
    if fillrate_predit >= 40:
        return "modere"
    return "faible"


def enrichir_priorite_action(df):
    """Ajoute priorite_prediction et action_recommandee si absents."""
    if "priorite_prediction" not in df.columns and "fillRate_predit" in df.columns:
        df["priorite_prediction"] = df["fillRate_predit"].apply(definir_priorite)
    if "action_recommandee" not in df.columns and "fillRate_predit" in df.columns:
        df["action_recommandee"] = df["fillRate_predit"].apply(generer_recommandation)
    return df


def predire_fillrate(df):
    """Applique le modèle ML pour prédire le fillRate futur.

    Le modèle attend exactement les colonnes utilisées à l'entraînement.
    Les colonnes manquantes sont signalées explicitement.
    """
    modele = load_model()
    colonnes_modele = list(modele.feature_names_in_)
    manquantes = [c for c in colonnes_modele if c not in df.columns]
    if manquantes:
        raise ValueError(
            "Colonnes manquantes pour la prédiction : " + ", ".join(manquantes[:8])
        )
    return modele.predict(df[colonnes_modele])


FEATURES_SIMULABLES = {
    "nb_precollecteurs_dispo": (0, 7, 1),
    "jours_depuis_derniere_collecte": (0, 14, 1),
    "nb_signalements_citoyens": (0, 6, 1),
    "nb_plaintes": (0, 3, 1),
    "capacity_m3": (5, 30, 1),
}


def cohercer_slider(valeur_initiale, mini, maxi, pas):
    """Homogénéise les types d'un slider Streamlit (int vs float).

    Streamlit exige que `value`, `min_value`, `max_value` et `step` soient
    du même type. Les valeurs métier sont des entiers (np.int64) tandis que
    les bornes de FEATURES_SIMULABLES sont des int : on renvoie donc des int
    quand la valeur est entière, sinon des float pour tout le groupe.
    """
    if float(valeur_initiale).is_integer():
        return int(valeur_initiale), int(mini), int(maxi), int(pas)
    return float(valeur_initiale), float(mini), float(maxi), float(pas)


def extraire_ligne_ml(ml_df, id_point, date_collecte):
    """Retourne la ligne de features ML correspondant à un point et une date."""
    date_collecte = pd.to_datetime(date_collecte)
    selection = ml_df[
        (ml_df["id_point"] == id_point) & (ml_df["date_collecte"] == date_collecte)
    ]
    if selection.empty:
        raise ValueError(
            f"Aucune donnée ML pour le point {id_point} à la date {date_collecte.date()}."
        )
    return selection.iloc[0]


def simuler_prediction(ligne_ml, ajustements=None):
    """Simule la prédiction IA sur une ligne ML, avec ajustements éventuels.

    ajustements : dict {nom_colonne: nouvelle_valeur} appliqué avant la prédiction.

    Retourne : (fillrate_predit, priorite, action, ligne_ajustee)
    """
    ligne = ligne_ml.copy()
    if ajustements:
        for colonne, valeur in ajustements.items():
            if colonne in ligne.index:
                ligne[colonne] = valeur

    colonnes_modele = list(load_model().feature_names_in_)
    manquantes = [c for c in colonnes_modele if c not in ligne.index]
    if manquantes:
        raise ValueError("Colonnes manquantes : " + ", ".join(manquantes))

    X = pd.DataFrame([ligne[colonnes_modele]])
    fillrate_predit = float(load_model().predict(X)[0])
    priorite = definir_priorite(fillrate_predit)
    action = generer_recommandation(fillrate_predit)
    return fillrate_predit, priorite, action, ligne
