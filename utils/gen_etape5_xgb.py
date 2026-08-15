"""Ajoute l'étape 5.2 (optimisation XGBoost) au notebook 07."""
import json
import nbformat as nbf

path = "notebooks/07_entrainement_optimisation_ML.ipynb"
with open(path, encoding="utf-8") as f:
    nb = nbf.reads(f.read(), as_version=4)


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(src):
    return nbf.v4.new_code_cell(src.strip())


cells = []

cells.append(md(
    "### 5.2 — Optimiser XGBoost\n"
    "\n"
    "Même démarche que pour LightGBM : XGBoost baseline → RandomizedSearchCV "
    "→ TimeSeriesSplit → meilleurs hyperparamètres → évaluation sur TEST → "
    "comparaison avec LightGBM.\n"
    "\n"
    "**Modèle à battre (LightGBM optimisé) :**\n"
    "\n"
    "| Métrique | Valeur |\n"
    "|---|---|\n"
    "| MAE | 5.7264 |\n"
    "| RMSE | 7.5150 |\n"
    "| MAPE | 63.00% |\n"
    "| R² TEST | 0.8339 |"
))

# Cellule 1 — Import
cells.append(code(
    "from sklearn.model_selection import RandomizedSearchCV\n"
    "from xgboost import XGBRegressor\n"
    "\n"
    "print(\"XGBoost importé.\")"
))

# Cellule 2 — Validation temporelle
cells.append(code(
    "# Validation temporelle (déjà définie, on la réutilise)\n"
    "print(tscv)"
))

# Cellule 3 — Modèle de base
cells.append(code(
    "xgb = XGBRegressor(\n"
    "    random_state=42,\n"
    "    n_jobs=-1\n"
    ")\n"
    "\n"
    "print(xgb)"
))

# Cellule 4 — Hyperparamètres
cells.append(code(
    "param_grid_xgb = {\n"
    "    \"n_estimators\": [100, 200, 300, 500],\n"
    "    \"learning_rate\": [0.01, 0.03, 0.05, 0.1],\n"
    "    \"max_depth\": [3, 4, 6, 8],\n"
    "    \"min_child_weight\": [1, 3, 5],\n"
    "    \"subsample\": [0.7, 0.8, 0.9, 1.0],\n"
    "    \"colsample_bytree\": [0.7, 0.8, 0.9, 1.0]\n"
    "}\n"
    "\n"
    "print(\"Espace de recherche défini.\")"
))

# Cellule 5 — Recherche
cells.append(code(
    "random_search_xgb = RandomizedSearchCV(\n"
    "    estimator=xgb,\n"
    "    param_distributions=param_grid_xgb,\n"
    "    n_iter=20,\n"
    "    scoring=\"r2\",\n"
    "    cv=tscv,\n"
    "    verbose=1,\n"
    "    random_state=42,\n"
    "    n_jobs=-1\n"
    ")"
))

# Cellule 6 — Entraînement
cells.append(code(
    "import time as _t2\n"
    "debut = _t2.time()\n"
    "\n"
    "random_search_xgb.fit(X_train, y_train)\n"
    "\n"
    "print(f\"Recherche terminée en {(_t2.time() - debut) / 60:.2f} minutes\")"
))

# Cellule 7 — Résultat de recherche
cells.append(code(
    "print(\"Meilleurs paramètres :\")\n"
    "print(random_search_xgb.best_params_)\n"
    "\n"
    "print(\"\\nMeilleur score CV :\")\n"
    "print(random_search_xgb.best_score_)"
))

# Cellule 8 — Meilleur modèle
cells.append(code(
    "best_xgb = random_search_xgb.best_estimator_\n"
    "\n"
    "print(\"Meilleur XGBoost récupéré.\")"
))

# Cellule 9 — Prédictions
cells.append(code(
    "y_pred_xgb = best_xgb.predict(X_test)"
))

# Cellule 10 — Évaluation
cells.append(code(
    "mae_xgb = mean_absolute_error(y_test, y_pred_xgb)\n"
    "\n"
    "rmse_xgb = np.sqrt(\n"
    "    mean_squared_error(y_test, y_pred_xgb)\n"
    ")\n"
    "\n"
    "r2_xgb = r2_score(\n"
    "    y_test,\n"
    "    y_pred_xgb\n"
    ")\n"
    "\n"
    "mask = y_test != 0\n"
    "\n"
    "mape_xgb = np.mean(\n"
    "    np.abs(\n"
    "        (y_test[mask] - y_pred_xgb[mask])\n"
    "        / y_test[mask]\n"
    "    )\n"
    ") * 100"
))

# Cellule 11 — Résultat final
cells.append(code(
    "print(\"========== XGBOOST OPTIMISÉ ==========\")\n"
    "print(f\"MAE  : {mae_xgb:.4f}\")\n"
    "print(f\"RMSE : {rmse_xgb:.4f}\")\n"
    "print(f\"MAPE : {mape_xgb:.2f}%\")\n"
    "print(f\"R²   : {r2_xgb:.4f}\")"
))

cells.append(code(
    "ligne_base_xgb = results_df[results_df[\"Modele\"] == \"XGBoost\"].iloc[0]"
))

cells.append(code(
    "comparaison_xgb = pd.DataFrame({\n"
    "    \"Phase\": [\"LightGBM optimisé\", \"XGBoost baseline\", \"XGBoost optimisé\"],\n"
    "    \"MAE\": [mae_lgbm, ligne_base_xgb[\"MAE\"], mae_xgb],\n"
    "    \"RMSE\": [rmse_lgbm, ligne_base_xgb[\"RMSE\"], rmse_xgb],\n"
    "    \"MAPE\": [mape_lgbm, ligne_base_xgb[\"MAPE\"], mape_xgb],\n"
    "    \"R2\": [r2_lgbm, ligne_base_xgb[\"R2\"], r2_xgb],\n"
    "})\n"
    "\n"
    "comparaison_xgb"
))

nb.cells = list(nb.cells) + cells

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cellules ajoutées :", len(cells))
print("Total cellules :", len(nb.cells))