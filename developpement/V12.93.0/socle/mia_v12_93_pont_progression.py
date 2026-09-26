"""
ALKAH-BRAIN — V12.93.0
Pont de progression V12.23 → V12.27

Principe :
- modules historiques inchangés
- chargement dynamique
- aucune exécution d'outil
- aucune modification documentaire
- aucune écriture persistante par le pont
- validation humaine requise
"""

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[3]

CHAIN = {
    "V12.23.0": [
        "mia_v12_etat_objectif.py",
        "mia_v12_actualisation_progression.py",
        "mia_v12_coherence_progression.py",
        "mia_v12_integration_progression.py",
        "mia_v12_historique_progression.py",
        "mia_v12_analyse_trajectoire.py",
        "mia_v12_projection_scenarios.py",
    ],
    "V12.24.0": [
        "mia_v12_comparaison_trajectoires.py",
    ],
    "V12.25.0": [
        "mia_v12_relations_trajectoires.py",
    ],
    "V12.26.0": [
        "mia_v12_synthese_multi_trajectoires.py",
    ],
    "V12.27.0": [
        "mia_v12_coherence_syntheses.py",
        "mia_v12_qualification_scenarios.py",
    ],
}


def charger_module(version, fichier):
    chemin = ROOT / "developpement" / version / "socle" / fichier

    if not chemin.exists():
        raise FileNotFoundError(str(chemin))

    nom = "alkah_" + version.replace(".", "_") + "_" + fichier[:-3]

    dossier = str(chemin.parent)
    import sys

    # V12.93 : rendre le dossier du module courant
    # prioritaire pour ses imports locaux.
    if dossier in sys.path:
        sys.path.remove(dossier)

    sys.path.insert(0, dossier)

    # Nettoyage du module local homonyme avant chargement.
    module_local = fichier[:-3]
    ancien_module = sys.modules.get(module_local)

    if ancien_module is not None:
        del sys.modules[module_local]

    spec = importlib.util.spec_from_file_location(nom, chemin)

    if spec is None or spec.loader is None:
        raise ImportError(f"Chargement impossible : {chemin}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def charger_chaine():
    modules = {}

    for version, fichiers in CHAIN.items():
        modules[version] = {}

        for fichier in fichiers:
            modules[version][fichier] = charger_module(version, fichier)

    return modules


def verifier_chaine():
    modules = charger_chaine()

    return {
        "version": "V12.93.0",
        "chaine": list(CHAIN.keys()),
        "modules_charges": sum(len(x) for x in modules.values()),
        "execution_outils": False,
        "modification_documents": False,
        "ecriture_persistante": False,
        "validation_humaine_requise": True,
    }


def statut():
    return {
        "version": "V12.93.0",
        "pont": "V12.23-V12.27",
        "chargement_dynamique": True,
        "execution_outils": False,
        "modification_documents": False,
        "ecriture_persistante": False,
        "validation_humaine_requise": True,
    }
