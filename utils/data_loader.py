"""Chargement robuste des données, du modèle et des résultats du projet EcoSys."""

import os
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]

DASHBOARD_DATA_CANDIDATES = [
    BASE_DIR / "dashboard" / "dashboard_dataset.parquet",
    BASE_DIR / "dashboard" / "dashboard_dataset.xlsx",
    BASE_DIR / "data" / "processed" / "orbit_dashboard.xlsx",
    BASE_DIR / "data" / "processed" / "dashboard_dataset.xlsx",
]

ML_DATA_CANDIDATES = [
    BASE_DIR / "data" / "processed" / "orbit_dataset_engineering.parquet",
    BASE_DIR / "data" / "processed" / "orbit_dataset_engineering.xlsx",
    BASE_DIR / "data" / "processed" / "dataset_ml.xlsx",
]

MODEL_CANDIDATES = [
    BASE_DIR / "models" / "meilleur_modele.pkl",
    BASE_DIR / "models" / "best_model.pkl",
]

METRICS_CANDIDATES = [
    BASE_DIR / "results" / "comparaison_modeles.xlsx",
]

IMPORTANCE_CANDIDATES = [
    BASE_DIR / "results" / "importance_variables.xlsx",
]

COLONNES_ESSENTIELLES = [
    "id_point",
    "date_collecte",
    "latitude",
    "longitude",
    "fillRate",
    "fillRate_predit",
    "priorite_prediction",
    "action_recommandee",
    "risque_debordement",
]


def _trouver_fichier(candidats, nom):
    """Retourne le premier fichier existant parmi les candidats."""
    for chemin in candidats:
        if chemin.exists():
            return chemin
    return None


def _lire_fichier(chemin):
    """Lit un fichier xlsx ou parquet selon son extension."""
    if chemin.suffix.lower() == ".parquet":
        return pd.read_parquet(chemin)
    return pd.read_excel(chemin, sheet_name=0)


@st.cache_data(show_spinner="Chargement des données du tableau de bord...")
def load_dashboard_data():
    """Charge le dataset opérationnel du tableau de bord."""
    chemin = _trouver_fichier(DASHBOARD_DATA_CANDIDATES, "dashboard")
    if chemin is None:
        raise FileNotFoundError(
            "Dataset du tableau de bord introuvable. "
            "Fichiers attendus : dashboard/dashboard_dataset.xlsx "
            "ou data/processed/orbit_dashboard.xlsx."
        )
    df = _lire_fichier(chemin)
    df["date_collecte"] = pd.to_datetime(df["date_collecte"], errors="coerce")
    return df


@st.cache_data(show_spinner="Chargement du dataset Machine Learning...")
def load_ml_data():
    """Charge le dataset complet utilisé pour l'entraînement (avec features)."""
    chemin = _trouver_fichier(ML_DATA_CANDIDATES, "dataset ML")
    if chemin is None:
        raise FileNotFoundError(
            "Dataset ML introuvable. Fichier attendu : "
            "data/processed/orbit_dataset_engineering.xlsx."
        )
    df = _lire_fichier(chemin)
    df["date_collecte"] = pd.to_datetime(df["date_collecte"], errors="coerce")
    return df


@st.cache_resource(show_spinner="Chargement du modèle Machine Learning...")
def load_model():
    """Charge le modèle Gradient Boosting sérialisé."""
    chemin = _trouver_fichier(MODEL_CANDIDATES, "modèle")
    if chemin is None:
        raise FileNotFoundError(
            "Modèle introuvable. Fichier attendu : models/meilleur_modele.pkl"
        )
    return joblib.load(chemin)


@st.cache_data(show_spinner="Chargement des métriques...")
def load_model_metrics():
    """Charge les métriques du modèle de référence (R², MAE, RMSE, MAPE)."""
    chemin = _trouver_fichier(METRICS_CANDIDATES, "métriques")
    if chemin is None:
        return None
    df = pd.read_excel(chemin, sheet_name=0)
    ligne_gb = df[df["Modele"].astype(str).str.contains("Gradient", na=False)]
    if ligne_gb.empty:
        ligne_gb = df.sort_values("RMSE").head(1)
    row = ligne_gb.iloc[0]
    return {
        "modele": str(row.get("Modele", "Gradient Boosting")),
        "r2": float(row.get("R2", 0.775)),
        "mae": float(row.get("MAE", 6.24)),
        "rmse": float(row.get("RMSE", 8.06)),
        "mape": float(row.get("MAPE", 0.675)),
    }


@st.cache_data(show_spinner="Chargement des importances...")
def load_feature_importance():
    """Charge les importances des variables du modèle."""
    chemin = _trouver_fichier(IMPORTANCE_CANDIDATES, "importances")
    if chemin is None:
        return None
    return pd.read_excel(chemin, sheet_name=0)


def verifier_colonnes(df, colonnes=None):
    """Retourne la liste des colonnes essentielles absentes."""
    colonnes = colonnes or COLONNES_ESSENTIELLES
    return [c for c in colonnes if c not in df.columns]
