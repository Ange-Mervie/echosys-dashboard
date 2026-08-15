"""Ajoute l'étape 5 (optimisation LightGBM) au notebook 07."""
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
    "## Étape 5 — Optimisation des hyperparamètres\n"
    "\n"
    "### 5.0 — Choix du modèle à optimiser\n"
    "\n"
    "On n'optimise pas les 6 modèles au hasard. On repart du classement de "
    "l'étape 4 et on sélectionne les 2-3 meilleurs selon R², MAE et RMSE.\n"
    "\n"
    "**Classement réel obtenu (étape 4) :**\n"
    "\n"
    "| Rang | Modèle | R² | MAE | RMSE |\n"
    "|---|---|---|---|---|\n"
    "| 1 | **LightGBM** | **0.8331** | 5.77 | 7.53 |\n"
    "| 2 | XGBoost | 0.8323 | 5.76 | 7.55 |\n"
    "| 3 | Random Forest | 0.8287 | 5.78 | 7.63 |\n"
    "| 4 | CatBoost | 0.8282 | 5.91 | 7.64 |\n"
    "| 5 | Gradient Boosting | 0.8231 | 6.03 | 7.76 |\n"
    "| 6 | Linear Regression | 0.7246 | 8.00 | 9.68 |\n"
    "\n"
    "**Décision :** on commence par **LightGBM**, le meilleur R² de la "
    "baseline, avec le meilleur compromis performance/vitesse."
))

cells.append(md(
    "### 5.1 — Validation temporelle (TimeSeriesSplit)\n"
    "\n"
    "On respecte l'ordre du temps : on ne mélange jamais aléatoirement, "
    "car l'objectif est de prédire le remplissage futur."
))

cells.append(code(
    "from sklearn.model_selection import TimeSeriesSplit\n"
    "\n"
    "tscv = TimeSeriesSplit(n_splits=5)\n"
    "\n"
    "print(tscv)"
))

cells.append(md(
    "### 5.2 — Optimiser LightGBM\n"
    "\n"
    "#### Espace de recherche (paramètres importants de LightGBM)"
))

cells.append(code(
    "from sklearn.model_selection import RandomizedSearchCV\n"
    "from lightgbm import LGBMRegressor\n"
    "\n"
    "lgbm = LGBMRegressor(\n"
    "    random_state=42,\n"
    "    n_jobs=-1,\n"
    "    verbosity=-1\n"
    ")\n"
    "\n"
    "param_grid_lgbm = {\n"
    "    \"n_estimators\": [100, 200, 300, 500],\n"
    "    \"learning_rate\": [0.01, 0.03, 0.05, 0.1],\n"
    "    \"num_leaves\": [31, 63, 127],\n"
    "    \"max_depth\": [-1, 5, 10, 15],\n"
    "    \"min_child_samples\": [10, 20, 40],\n"
    "    \"subsample\": [0.7, 0.8, 0.9, 1.0],\n"
    "    \"colsample_bytree\": [0.7, 0.8, 0.9, 1.0]\n"
    "}"
))

cells.append(md("#### Lancer la recherche (RandomizedSearchCV + validation temporelle)"))

cells.append(code(
    "random_search_lgbm = RandomizedSearchCV(\n"
    "    estimator=lgbm,\n"
    "    param_distributions=param_grid_lgbm,\n"
    "    n_iter=20,\n"
    "    scoring=\"r2\",\n"
    "    cv=tscv,\n"
    "    verbose=1,\n"
    "    random_state=42,\n"
    "    n_jobs=-1\n"
    ")"
))

cells.append(code(
    "import time as _t\n"
    "debut = _t.time()\n"
    "\n"
    "random_search_lgbm.fit(X_train, y_train)\n"
    "\n"
    "print(f\"Recherche terminée en {(_t.time() - debut) / 60:.2f} minutes\")"
))

cells.append(md("#### Voir les meilleurs paramètres"))

cells.append(code(
    "print(\"Meilleurs paramètres :\")\n"
    "print(random_search_lgbm.best_params_)\n"
    "\n"
    "print(\"\\nMeilleur score CV :\")\n"
    "print(random_search_lgbm.best_score_)"
))

cells.append(md(
    "### 5.3 — Évaluer sur notre vrai TEST\n"
    "\n"
    "⚠️ Le `best_score_` de la validation n'est pas notre résultat final. "
    "On récupère le meilleur modèle et on l'évalue sur le jeu TEST jamais vu."
))

cells.append(code(
    "best_lgbm = random_search_lgbm.best_estimator_\n"
    "\n"
    "y_pred_lgbm = best_lgbm.predict(X_test)"
))

cells.append(code(
    "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n"
    "\n"
    "mae_lgbm = mean_absolute_error(y_test, y_pred_lgbm)\n"
    "\n"
    "rmse_lgbm = np.sqrt(\n"
    "    mean_squared_error(y_test, y_pred_lgbm)\n"
    ")\n"
    "\n"
    "r2_lgbm = r2_score(\n"
    "    y_test,\n"
    "    y_pred_lgbm\n"
    ")\n"
    "\n"
    "mask = y_test != 0\n"
    "\n"
    "mape_lgbm = np.mean(\n"
    "    np.abs(\n"
    "        (y_test[mask] - y_pred_lgbm[mask])\n"
    "        / y_test[mask]\n"
    "    )\n"
    ") * 100\n"
    "\n"
    "print(\"========== LIGHTGBM OPTIMISÉ ==========\")\n"
    "print(f\"MAE  : {mae_lgbm:.4f}\")\n"
    "print(f\"RMSE : {rmse_lgbm:.4f}\")\n"
    "print(f\"MAPE : {mape_lgbm:.2f}%\")\n"
    "print(f\"R²   : {r2_lgbm:.4f}\")"
))

cells.append(md(
    "#### Comparaison baseline vs optimisé\n"
    "\n"
    "L'objectif est d'obtenir une **vraie amélioration généralisable**, pas "
    "de forcer un score artificiel."
))

cells.append(code(
    "ligne_base = results_df[results_df[\"Modele\"] == \"LightGBM\"].iloc[0]\n"
    "\n"
    "comparaison_lgbm = pd.DataFrame({\n"
    "    \"Phase\": [\"Baseline\", \"Optimisé\"],\n"
    "    \"MAE\": [ligne_base[\"MAE\"], mae_lgbm],\n"
    "    \"RMSE\": [ligne_base[\"RMSE\"], rmse_lgbm],\n"
    "    \"MAPE\": [ligne_base[\"MAPE\"], mape_lgbm],\n"
    "    \"R2\": [ligne_base[\"R2\"], r2_lgbm],\n"
    "})\n"
    "\n"
    "comparaison_lgbm"
))

nb.cells = list(nb.cells) + cells

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Cellules ajoutées :", len(cells))
print("Total cellules :", len(nb.cells))