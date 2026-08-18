"""Feature Selection Experiment.

Mesure la contribution reelle des features faibles en les supprimant progressivement.
Seules les features avec importance = 0 seront candidates a la suppression definitive.
"""
import sys, warnings, time, json
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, ".")

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from lightgbm import LGBMRegressor
from utils.data_loader import load_model

BASE_DIR = Path(__file__).resolve().parents[1]
ML_PATH = BASE_DIR / "data" / "processed" / "orbit_dataset_engineering.parquet"
IMPORTANCE_PATH = BASE_DIR / "results" / "importance_variables.xlsx"
RESULTS_PATH = BASE_DIR / "results" / "feature_selection_experiment.json"
DATE_SPLIT = "2025-03-15"
TARGET = "fillRate_target_t_plus_1"
LEAK_COLS = ["statut_prevu", "priorite_recommandee"]

# Same hyperparameters as deployed model
PARAMS = {
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

print("=" * 70)
print("EXPERIMENT : Feature Selection (suppression progressive des features faibles)")
print("=" * 70)

# Load
data = pd.read_parquet(ML_PATH)
data["date_collecte"] = pd.to_datetime(data["date_collecte"])

imp = pd.read_excel(IMPORTANCE_PATH, sheet_name=0)
imp_sorted = imp.sort_values("Importance").reset_index(drop=True)

train_data = data[data["date_collecte"] < DATE_SPLIT].copy()
test_data = data[data["date_collecte"] >= DATE_SPLIT].copy()

FEATURES_46 = [
    c for c in data.columns
    if c not in ["id_point", "date_collecte", TARGET] + LEAK_COLS
]
y_train = train_data[TARGET].copy()
y_test = test_data[TARGET].copy()

for df_xy in (train_data, test_data):
    bool_cols = df_xy.select_dtypes(include=["bool"]).columns
    df_xy[bool_cols] = df_xy[bool_cols].astype(int)

# Baseline (all 46 features)
X_train_all = train_data[FEATURES_46].copy()
X_test_all = test_data[FEATURES_46].copy()

m = LGBMRegressor(**PARAMS)
m.fit(X_train_all, y_train)
r2_base = r2_score(y_test, m.predict(X_test_all))
mae_base = mean_absolute_error(y_test, m.predict(X_test_all))
print(f"\n  Baseline (46 features): R2={r2_base:.4f}, MAE={mae_base:.4f}")

# Progressive removal
print("\n  Suppression progressive des features les moins importants:")
print(f"  {'N_supprimees':>14s} | {'Features_restantes':>18s} | {'R2':>8s} | {'MAE':>8s} | {'Delta_R2':>9s}")
print("  " + "-" * 70)

results_exp = {"baseline": {"n_features": 46, "r2": r2_base, "mae": mae_base}, "removals": []}

lowest_importance = imp_sorted["Variable"].tolist()

for n_remove in [5, 10, 15, 20, 25, 30]:
    removed = lowest_importance[:n_remove]
    remaining = [f for f in FEATURES_46 if f not in removed]

    X_tr = train_data[remaining].copy()
    X_te = test_data[remaining].copy()

    m_test = LGBMRegressor(**PARAMS)
    m_test.fit(X_tr, y_train)
    r2 = r2_score(y_test, m_test.predict(X_te))
    mae = mean_absolute_error(y_test, m_test.predict(X_te))
    delta = r2 - r2_base

    status = "IMPROVE" if delta > 0 else "worse"
    print(f"  {n_remove:>13d} | {len(remaining):>17d} | {r2:.4f} | {mae:.4f} | {delta:+.4f}  {status}")

    results_exp["removals"].append({
        "n_removed": n_remove,
        "n_remaining": len(remaining),
        "r2": r2,
        "mae": mae,
        "delta_r2": delta,
        "removed_features": removed,
    })

# Also test removing only features with importance == 0
zero_imp_features = imp_sorted[imp_sorted["Importance"] == 0]["Variable"].tolist()
if len(zero_imp_features) > 0:
    remaining_zero = [f for f in FEATURES_46 if f not in zero_imp_features]
    X_tr = train_data[remaining_zero].copy()
    X_te = test_data[remaining_zero].copy()
    m_zero = LGBMRegressor(**PARAMS)
    m_zero.fit(X_tr, y_train)
    r2_zero = r2_score(y_test, m_zero.predict(X_te))
    mae_zero = mean_absolute_error(y_test, m_zero.predict(X_te))
    delta_zero = r2_zero - r2_base
    print(f"\n  Features avec importance == 0: {len(zero_imp_features)} -> {zero_imp_features}")
    print(f"  Apres suppression de ces {len(zero_imp_features)} features: R2={r2_zero:.4f}, MAE={mae_zero:.4f}, Delta={delta_zero:+.4f}")
    results_exp["zero_importance"] = {
        "n_removed": len(zero_imp_features),
        "features": zero_imp_features,
        "r2": r2_zero,
        "mae": mae_zero,
        "delta_r2": delta_zero,
    }
else:
    print("\n  Aucune feature avec importance == 0.")
    results_exp["zero_importance"] = None

print("\n" + "=" * 70)
best_delta = 0.0
best_result = None
for r in results_exp["removals"]:
    if r["delta_r2"] > best_delta:
        best_delta = r["delta_r2"]
        best_result = r
if best_result is None:
    print("  CONCLUSION : Aucun niveau de suppression n'ameliore le R2.")
    print("               Le modele actuel est deja optimal avec 46 features.")
    print("               Feature selection ne sera PAS appliquee au modele deploye.")
else:
    print(f"  CONCLUSION : La suppression de {best_result['n_removed']} features")
    print(f"               ameliore le R2 de +{best_result['delta_r2']:.4f}.")
    print(f"               Features a supprimer : {best_result['removed_features']}")
print("=" * 70)

RESULTS_PATH.write_text(json.dumps(results_exp, indent=2))
print(f"\n  Resultats sauvegardes : {RESULTS_PATH}")
