"""Tests pour les composants UI."""

import pytest

from utils.prediction import COULEURS_PRIORITE, COULEURS_BADGE
from utils.ui import badge_priorite, style_table


class TestBadgePriorite:
    def test_badge_urgente(self):
        result = badge_priorite("Urgente")
        assert "badge-prio-urgente" in result
        assert "Urgente" in result

    def test_badge_elevee(self):
        result = badge_priorite("Elevée")
        assert "badge-prio-elevee" in result
        assert "Elevée" in result

    def test_badge_moyenne(self):
        result = badge_priorite("Moyenne")
        assert "badge-prio-moyenne" in result
        assert "Moyenne" in result

    def test_badge_faible(self):
        result = badge_priorite("Faible")
        assert "badge-prio-faible" in result
        assert "Faible" in result

    def test_badge_inconnu(self):
        result = badge_priorite("Inconnue")
        assert "badge" in result
        assert "Inconnue" in result
        assert "badge-prio-" not in result

    def test_badge_avec_espaces(self):
        result = badge_priorite("  Urgente  ")
        assert "badge-prio-urgente" in result

    def test_badge_html_secure(self):
        result = badge_priorite("Urgente")
        assert "<span" in result
        assert "class=" in result


class TestStyleTable:
    def test_style_urgente(self):
        result = style_table("Urgente")
        assert "background-color:" in result
        assert "font-weight: 700" in result

    def test_style_elevee(self):
        result = style_table("Elevée")
        assert "background-color:" in result

    def test_style_inconnue(self):
        result = style_table("Inconnue")
        assert "font-weight: 700" in result

    def test_couleurs_coherentes(self):
        for priorite in COULEURS_PRIORITE:
            result = style_table(priorite)
            assert "color:" in result


class TestCouleursCUD:
    def test_vert_echosys(self):
        assert COULEURS_PRIORITE["Moyenne"] == "#F9A825"
        assert COULEURS_PRIORITE["Faible"] == "#2E7D32"

    def test_rouge_echosys(self):
        assert COULEURS_PRIORITE["Urgente"] == "#C62828"

    def test_orange_echosys(self):
        assert COULEURS_PRIORITE["Elevée"] == "#E65100"

    def test_badges_fond(self):
        assert COULEURS_BADGE["Urgente"]["fond"] == "#FDECEC"
        assert COULEURS_BADGE["Elevée"]["fond"] == "#FFF0E0"
        assert COULEURS_BADGE["Moyenne"]["fond"] == "#FFF8E1"
        assert COULEURS_BADGE["Faible"]["fond"] == "#E8F5E9"
