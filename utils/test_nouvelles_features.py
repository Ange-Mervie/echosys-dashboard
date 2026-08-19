"""Etape B — Test 3 features candidates (46 -> 49 features).

Ajoute 3 features au dataset ML, entraine LightGBM avec TimeSeriesSplit,
compare R2 avec le modele actuel (46 features).

Nouvelles features :
  1. fillRate_volatility_7d   — rolling std fillRate sur 7j
  2. taux_remplissage_capacity — fillRate / capacity_m3
  3. pressure_combine         — pression_citoyenne + pression_collecte
"""
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")

from utils.data_loader import load_ml_data, load_model

# 1. Charger les donnees
print("Chargement du dataset ML...")
ml = load_ml_data()
print(f"  Shape: {ml.shape}")

TARGET = "fillRate_target_t_plus_1"
COLONNES_EXCLUES = [
    "id_point", "date_collecte", "statut_prevu",
    "priorite_recommandee", TARGET,
]
model_feats_base = [c for c in ml.columns if c not in COLONNES_EXCLUES]

NEW_FEATURES = [
    "is_weekend_demain",
    "rolling_mean_7d",
    "fillRate_trend_ratio",
]
all_feats = model_feats_base + NEW_FEATURES

# 2. Ajouter les 3 nouvelles features
print("\nAjout des 3 nouvelles features...")
ml_sorted = ml.sort_values(["id_point", "date_collecte"]).reset_index(drop=True)

for feat in NEW_FEATURES:
    if feat == "fillRate_volatility_7d":
        ml_sorted[feat] = (
            ml_sorted.groupby("id_point")["fillRate"]
            .transform(lambda x: x.rolling(window=7, min_periods=1).std())
            .fillna(0)
        )
    elif feat == "taux_remplissage_capacity":
        ml_sorted[feat] = ml_sorted["fillRate"] / (ml_sorted["capacity_m3"] + 1)
    elif feat == "pressure_combine":
        ml_sorted[feat] = ml_sorted["pression_citoyenne"] + ml_sorted["pression_collecte"]
    elif feat == "is_weekend_demain":
        ml_sorted[feat] = ((ml_sorted["jour_semaine_num"] + 1) % 7 >= 5).astype(int)
    elif feat == "rolling_mean_7d":
        ml_sorted[feat] = (
            ml_sorted.groupby("id_point")["fillRate"]
            .transform(lambda x: x.rolling(window=7, min_periods=1).mean())
        )
    elif feat == "fillRate_trend_ratio":
        ml_sorted["_rm3"] = ml_sorted.groupby("id_point")["fillRate"].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        ml_sorted[feat] = ml_sorted["fillRate"] / (ml_sorted["_rm3"] + 1)
        ml_sorted.drop(columns="_rm3", inplace=True)

print(f"  Correlations avec la cible :")
for feat in NEW_FEATURES:
    corr = ml_sorted[feat].corr(ml_sorted[TARGET])
    print(f"    {feat:35s} : {corr:+.4f}")

# 3. Preparation X / y
X = ml_sorted[all_feats].copy()
y = ml_sorted[TARGET].copy()

# Convert bool columns to int (LightGBM sometimes has issues)
for col in X.columns:
    if X[col].dtype == bool:
        X[col] = X[col].astype(int)

print(f"\n  Features totales : {len(all_feats)}")
print(f"  Shape X : {X.shape}")

# 4. TimeSeriesSplit (identique au notebook)
tscv = TimeSeriesSplit(n_splits=5)

# 5. LightGBM (hyperparams fixes — version optimisee connue du commit c881ca0)
# (le RandomizedSearchCV a deja ete execute ; on reutilise les meilleurs params)
model_current = load_model()
best_params = getattr(model_current, "get_params", lambda: {})()
lgbm = LGBMRegressor(
    random_state=42,
    n_jobs=-1,
    verbosity=-1,
    **{k: v for k, v in best_params.items()
       if k in ["n_estimators", "learning_rate", "num_leaves",
                "max_depth", "min_child_samples", "subsample",
                "colsample_bytree", "reg_alpha", "reg_lambda"]}
)

print(f"\n  Hyperparams reutilises :")
for k in ["n_estimators", "learning_rate", "num_leaves", "max_depth"]:
    print(f"    {k} = {best_params.get(k, 'default')}")

# 6. Cross-validation temporel
print("\nCross-validation temporel (5 folds)...")
r2_scores = []
mae_scores = []
rmse_scores = []

for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
    X_tr, X_va = X.iloc[train_idx], X.iloc[val_idx]
    y_tr, y_va = y.iloc[train_idx], y.iloc[val_idx]
    lgbm.fit(X_tr, y_tr)
    pred = lgbm.predict(X_va)
    r2 = r2_score(y_va, pred)
    mae = mean_absolute_error(y_va, pred)
    rmse = np.sqrt(mean_squared_error(y_va, pred))
    r2_scores.append(r2)
    mae_scores.append(mae)
    rmse_scores.append(rmse)
    print(f"  Fold {fold}: R2={r2:.4f}, MAE={mae:.2f}, RMSE={rmse:.2f}")

r2_mean = np.mean(r2_scores)
r2_std = np.std(r2_scores)
mae_mean = np.mean(mae_scores)
rmse_mean = np.mean(rmse_scores)

print(f"\n=== RESULTATS (49 features) ===")
print(f"  R2 moyen : {r2_mean:.4f} (+/- {r2_std:.4f})")
print(f"  MAE moyen : {mae_mean:.2f}")
print(f"  RMSE moyen: {rmse_mean:.2f}")
print(f"  Modele actuel (46 feats) R2 ~0.295")
print(f"  Amelioration R2 : {r2_mean - 0.295:+.4f} ({(r2_mean - 0.295)/0.295*100:+.1f}%)")

# Sauvegarder les resultats
resultat = {
    "features_base": len(model_feats_base),
    "features_nouvelles": NEW_FEATURES,
    "features_totales": len(all_feats),
    "r2_mean": round(float(r2_mean), 4),
    "r2_std": round(float(r2_std), 4),
    "r2_folds": [round(float(s), 4) for s in r2_scores],
    "mae_mean": round(float(mae_mean), 4),
    "rmse_mean": round(float(rmse_mean), 4),
    "r2_actuel": 0.295,
    "amelioration_r2": round(float(r2_mean - 0.295), 4),
    "amelioration_pct": round(float((r2_mean - 0.295) / 0.295 * 100), 1),
}

with open("results/test_nouvelles_features.json", "w") as f:
    json.dump(resultat, f, indent=2)

print(f"\nResultats sauvegardes : results/test_nouvelles_features.json")
if r2_mean > 0.295:
    print("  -> Les 3 nouvelles features AMELIORENT le R2")
else:
    print("  -> Les 3 nouvelles features ne melvorent pas le R2")
