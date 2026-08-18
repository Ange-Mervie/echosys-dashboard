"""Test rapide : LightGBM 46 feats vs 46+3 feats (mêmes hyperparamètres).

Évalue sur le TEST temporel jamais vu. Si +3 feats améliore, on lance RandomizedSearchCV.
"""
import sys, warnings, time, json
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from lightgbm import LGBMRegressor

BASE_DIR = Path(__file__).resolve().parents[1]
ML_PATH = BASE_DIR / "data" / "processed" / "orbit_dataset_engineering.parquet"
MODEL_PATH = BASE_DIR / "models" / "meilleur_modele.pkl"
RESULTS_PATH = BASE_DIR / "results" / "test_3nouvelles_features.json"
DATE_SPLIT = "2025-03-15"
TARGET = "fillRate_target_t_plus_1"
LEAK_COLS = ["statut_prevu", "priorite_recommandee"]

print("=" * 60)
print("TEST : 46 feats vs 46+3 feats (LightGBM, mêmes hyperparams)")
print("=" * 60)

# 1. Load + sort
data = pd.read_parquet(ML_PATH)
data["date_collecte"] = pd.to_datetime(data["date_collecte"])
data = data.sort_values(["id_point", "date_collecte"]).reset_index(drop=True)

# 2. Compute FEATURES_46 BEFORE adding new features
FEATURES_46 = [
    c for c in data.columns
    if c not in ["id_point", "date_collecte", TARGET] + LEAK_COLS
]

# 3. Add 3 new features
print("\nAjout des 3 nouvelles features...")
data["fillRate_lag_7"] = data.groupby("id_point")["fillRate"].shift(7).fillna(data["fillRate"])
data["delta_24h_trend"] = data.groupby("id_point")["delta_fillRate_24h"].shift(1).fillna(0)
data["sat_risk_inter"] = data["indice_saturation"] * data["risque_debordement"]

NEW_FEATURES = ["fillRate_lag_7", "delta_24h_trend", "sat_risk_inter"]
FEATURES_49 = FEATURES_46 + NEW_FEATURES

# 4. Split temporel
train_data = data[data["date_collecte"] < DATE_SPLIT].copy()
test_data = data[data["date_collecte"] >= DATE_SPLIT].copy()
print(f"  TRAIN: {train_data.shape}, TEST: {test_data.shape}")

# 5. Bool → int
for df_xy in (train_data, test_data):
    bool_cols = df_xy.select_dtypes(include=["bool"]).columns
    df_xy[bool_cols] = df_xy[bool_cols].astype(int)

X_train_46 = train_data[FEATURES_46].copy()
X_test_46 = test_data[FEATURES_46].copy()
y_train = train_data[TARGET].copy()
y_test = test_data[TARGET].copy()

X_train_49 = train_data[FEATURES_49].copy()
X_test_49 = test_data[FEATURES_49].copy()

# 6. Best params from deployed model
best_params = {
    "n_estimators": 200,
    "learning_rate": 0.03,
    "max_depth": 5,
    "num_leaves": 31,
    "min_child_samples": 20,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "random_state": 42,
    "n_jobs": -1,
    "verbosity": -1,
}

def evaluate(X_train, X_test, params, label):
    m = LGBMRegressor(**params)
    t0 = time.time()
    m.fit(X_train, y_train)
    train_time = time.time() - t0
    y_pred = m.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mask = y_test != 0
    mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
    print(f"\n  [{label}] {X_train.shape[1]} features:")
    print(f"    MAE={mae:.4f}  RMSE={rmse:.4f}  MAPE={mape:.2f}%  R²={r2:.4f}")
    print(f"    Train time: {train_time:.1f}s")
    return m, r2, mae, rmse, mape, m.feature_importances_, list(X_train.columns)

# 7. Baseline (46 feats, same params)
m_46, r2_46, mae_46, rmse_46, mape_46, fi_46, cols_46 = evaluate(
    X_train_46, X_test_46, best_params, "46 feats (baseline)"
)

# 8. +3 feats
m_49, r2_49, mae_49, rmse_49, mape_49, fi_49, cols_49 = evaluate(
    X_train_49, X_test_49, best_params, "49 feats (+3)"
)

# 9. New feature importances
print("\n  Importances des 3 nouvelles features :")
for f in NEW_FEATURES:
    idx = cols_49.index(f)
    rank = np.argsort(fi_49)[::-1].tolist().index(idx) + 1
    print(f"    {f:25s} : {fi_49[idx]:4d}  (rank {rank}/{len(cols_49)})")

# 10. Compare
delta_r2 = r2_49 - r2_46
print(f"\n{'='*60}")
print(f"RÉSULTAT : R²(49) - R²(46) = {delta_r2:+.4f} ({delta_r2/r2_46*100:+.1f}%)")
print(f"R² actuel (deployé) ~ 0.299  |  R² baseline repro = {r2_46:.4f}")
print(f"R² +3 feats      = {r2_49:.4f}")
print(f"{'='*60}")

if delta_r2 > 0:
    print("OK : Les 3 nouvelles features AMELIORCENT le R2 -> lancer RandomizedSearchCV")
else:
    print("NON : Les 3 nouvelles features n'apportent pas d'amelioration du R2.")
    print("     Le signal est deja capture par fillRate_t_minus_1, delta_fillRate_24h, etc.")
    print("     Etape suivante : Feature Selection (supprimer les features inutiles).")

# 11. Save results
results = {
    "baseline": {"n_features": 46, "r2": r2_46, "mae": mae_46, "rmse": rmse_46, "mape": mape_46},
    "with_3_features": {"n_features": 49, "r2": r2_49, "mae": mae_49, "rmse": rmse_49, "mape": mape_49},
    "delta_r2": delta_r2,
    "improved": delta_r2 > 0,
    "new_feature_importances": {
        f: int(fi_49[cols_49.index(f)]) for f in NEW_FEATURES
    },
}
RESULTS_PATH.write_text(json.dumps(results, indent=2))
print(f"\n  Resultats sauvegardes : {RESULTS_PATH}")
