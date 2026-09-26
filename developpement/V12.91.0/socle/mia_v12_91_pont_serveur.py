"""
ALKAH-BRAIN — V12.91.0
Pont sécurisé entre mia_serveur.py et l'adaptateur V12.91.

Le pont :
- ne remplace pas V76 ;
- ne modifie aucun moteur source ;
- ne lance aucun outil externe ;
- ne modifie aucun document ;
- prépare uniquement le routage futur.
"""

from pathlib import Path
import importlib.util


VERSION = "V12.91.0-PONT"


ROOT = Path(__file__).resolve().parents[2]

ADAPTATEUR = (
    ROOT
    / "V12.91.0"
    / "socle"
    / "mia_v12_adaptateur_raccordement.py"
)


def charger_adaptateur():
    if not ADAPTATEUR.exists():
        raise FileNotFoundError(
            f"Adaptateur V12.91 introuvable : {ADAPTATEUR}"
        )

    spec = importlib.util.spec_from_file_location(
        "mia_v12_91_adaptateur_serveur",
        ADAPTATEUR,
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Impossible de charger l'adaptateur V12.91"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def statut_pont():
    adaptateur = charger_adaptateur()

    statut = adaptateur.statut()

    return {
        "pont": VERSION,
        "adaptateur": statut,
        "moteur_principal": "V76/MIA25/B33",
        "routage_actif": False,
        "execution_outils": False,
        "modification_documents": False,
        "validation_humaine_requise": True,
    }
