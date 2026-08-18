"""Tests pour les fonctions de prediction et priorisation."""

import pytest
import pandas as pd
import numpy as np

from utils.prediction import (
    ORDRE_PRIORITE,
    COULEURS_PRIORITE,
    COULEURS_BADGE,
    SEUILS,
    normaliser_priorite,
    definir_priorite,
    generer_recommandation,
    enrichir_priorite_action,
    cohercer_slider,
    estimer_risque_debordement,
)


class TestNormaliserPriorite:
    def test_urgente(self):
        assert normaliser_priorite("Urgente") == "Urgente"
        assert normaliser_priorite("urgente") == "Urgente"
        assert normaliser_priorite("URGENTE") == "Urgente"

    def test_elevee(self):
        assert normaliser_priorite("Elevée") == "Elevée"
        assert normaliser_priorite("élevée") == "Elevée"
        assert normaliser_priorite("elevee") == "Elevée"
        assert normaliser_priorite("ELEVEE") == "Elevée"

    def test_moyenne(self):
        assert normaliser_priorite("Moyenne") == "Moyenne"
        assert normaliser_priorite("moyenne") == "Moyenne"

    def test_faible(self):
        assert normaliser_priorite("Faible") == "Faible"
        assert normaliser_priorite("faible") == "Faible"

    def test_valeur_inconnue(self):
        assert normaliser_priorite("Inconnue") == "Faible"
        assert normaliser_priorite("") == "Faible"
        assert normaliser_priorite(123) == "Faible"
        assert normaliser_priorite(None) == "Faible"


class TestDefinirPriorite:
    def test_urgente(self):
        assert definir_priorite(95) == "Urgente"
        assert definir_priorite(100) == "Urgente"

    def test_elevee(self):
        assert definir_priorite(70) == "Elevée"
        assert definir_priorite(89) == "Elevée"

    def test_moyenne(self):
        assert definir_priorite(40) == "Moyenne"
        assert definir_priorite(69) == "Moyenne"

    def test_faible(self):
        assert definir_priorite(0) == "Faible"
        assert definir_priorite(39) == "Faible"

    def test_seuils(self):
        assert definir_priorite(SEUILS["faible"]) == "Moyenne"
        assert definir_priorite(SEUILS["moyenne"]) == "Elevée"
        assert definir_priorite(SEUILS["elevee"]) == "Urgente"


class TestGenererRecommandation:
    def test_collecte_immediate(self):
        assert generer_recommandation(95) == "Collecte immédiate"
        assert generer_recommandation(100) == "Collecte immédiate"

    def test_collecte_aujourdhui(self):
        assert generer_recommandation(70) == "Planifier une collecte aujourd'hui"
        assert generer_recommandation(89) == "Planifier une collecte aujourd'hui"

    def test_collecte_48h(self):
        assert generer_recommandation(40) == "Programmer une collecte sous 48 heures"
        assert generer_recommandation(69) == "Programmer une collecte sous 48 heures"

    def test_surveillance(self):
        assert generer_recommandation(0) == "Surveillance simple"
        assert generer_recommandation(39) == "Surveillance simple"


class TestEnrichirPrioriteAction:
    def test_ajoute_priorite_action(self):
        df = pd.DataFrame({
            "id_point": [1, 2, 3],
            "fillRate_predit": [95, 50, 20],
        })
        result = enrichir_priorite_action(df)
        assert "priorite_prediction" in result.columns
        assert "action_recommandee" in result.columns
        assert result.iloc[0]["priorite_prediction"] == "Urgente"
        assert result.iloc[1]["priorite_prediction"] == "Moyenne"
        assert result.iloc[2]["priorite_prediction"] == "Faible"

    def test_ne_remplace_pas_si_colonnes_existent(self):
        df = pd.DataFrame({
            "id_point": [1, 2],
            "fillRate_predit": [95, 50],
            "priorite_prediction": ["Faible", "Faible"],
            "action_recommandee": ["Test", "Test"],
        })
        result = enrichir_priorite_action(df)
        assert result.iloc[0]["priorite_prediction"] == "Faible"
        assert result.iloc[0]["action_recommandee"] == "Test"


class TestCohercerSlider:
    def test_entiers(self):
        val, mini, maxi, pas = cohercer_slider(np.int64(5), 0, 10, 1)
        assert isinstance(val, int)
        assert isinstance(mini, int)
        assert isinstance(maxi, int)
        assert isinstance(pas, int)

    def test_floats(self):
        val, mini, maxi, pas = cohercer_slider(5.5, 0.0, 10.0, 0.1)
        assert isinstance(val, float)
        assert isinstance(mini, float)
        assert isinstance(maxi, float)
        assert isinstance(pas, float)


class TestConstantes:
    def test_ordre_priorite(self):
        assert len(ORDRE_PRIORITE) == 4
        assert ORDRE_PRIORITE == ["Urgente", "Elevée", "Moyenne", "Faible"]

    def test_couleurs_priorite(self):
        for priorite in ORDRE_PRIORITE:
            assert priorite in COULEURS_PRIORITE
            assert COULEURS_PRIORITE[priorite].startswith("#")

    def test_couleurs_badge(self):
        for priorite in ORDRE_PRIORITE:
            assert priorite in COULEURS_BADGE
            assert "fond" in COULEURS_BADGE[priorite]
            assert "texte" in COULEURS_BADGE[priorite]

    def test_seuils_coherents(self):
        assert SEUILS["faible"] < SEUILS["moyenne"] < SEUILS["elevee"]


class TestEstimerRisqueDebordement:
    def test_critique(self):
        assert estimer_risque_debordement(95.0) == "critique"
        assert estimer_risque_debordement(90.0) == "critique"

    def test_eleve(self):
        assert estimer_risque_debordement(89.0) == "eleve"
        assert estimer_risque_debordement(70.0) == "eleve"

    def test_modere(self):
        assert estimer_risque_debordement(69.0) == "modere"
        assert estimer_risque_debordement(40.0) == "modere"

    def test_faible(self):
        assert estimer_risque_debordement(39.0) == "faible"
        assert estimer_risque_debordement(0.0) == "faible"
