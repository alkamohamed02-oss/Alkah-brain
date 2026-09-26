"""
ALKAH-BRAIN — V12.94.0
Raccordement sécurisé V12.92 ↔ V12.93

V12.93 : progression / trajectoires
V12.92 : routage général existant
Fallback : V76/MIA25/B33

Aucune exécution d'outil.
Aucune modification documentaire.
Aucune écriture persistante.
Validation humaine requise.
"""

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[3]


def _charger(chemin, nom):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger {chemin}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def charger_v12_93():
    p = ROOT / "developpement" / "V12.93.0" / "socle" / \
        "mia_v12_93_pont_progression.py"
    return _charger(p, "mia_v12_93_pont_progression")


def classifier_progression(demande):
    texte = str(demande).lower()

    mots = (
        "progression",
        "trajectoire",
        "historique",
        "scenario",
        "scénario",
        "synthèse",
        "synthese",
        "objectif",
        "évolution",
        "evolution",
        "cohérence",
        "coherence",
    )

    return any(mot in texte for mot in mots)


def router(demande):
    if classifier_progression(demande):
        v93 = charger_v12_93()
        resultat = v93.verifier_chaine()

        return {
            "version": "V12.94.0",
            "route": "V12.93.0",
            "moteur": "progression_V12.23_V12.27",
            "fallback": "V76/MIA25/B33",
            "validation_humaine_requise": True,
            "resultat": resultat,
        }

    return {
        "version": "V12.94.0",
        "route": "V12.92.0",
        "moteur": "V12.92",
        "fallback": "V76/MIA25/B33",
        "validation_humaine_requise": True,
        "resultat": None,
    }


def statut():
    return {
        "version": "V12.94.0",
        "routage_progression": True,
        "v12_93_active": True,
        "fallback_v76": True,
        "execution_outils": False,
        "modification_documents": False,
        "ecriture_persistante": False,
        "validation_humaine_requise": True,
    }
