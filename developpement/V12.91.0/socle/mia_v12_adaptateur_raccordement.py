"""
ALKAH-BRAIN — V12.91.0
Adaptateur de raccordement des briques sémantiques.

Chaîne :
V12.50 → V12.60 → V12.70 → V12.80 → V12.90

IMPORTANT :
- ne modifie aucun moteur source ;
- ne modifie aucun document ;
- ne modifie aucune donnée persistante ;
- ne déclenche aucun outil externe ;
- toute proposition reste soumise à validation humaine.
"""

VERSION = "V12.91.0"

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]


def _charger_module(chemin, nom):
    """Charge un module Python depuis son chemin sans modifier son fichier."""
    chemin = Path(chemin)

    if not chemin.exists():
        raise FileNotFoundError(str(chemin))

    spec = importlib.util.spec_from_file_location(nom, chemin)

    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger {nom}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def charger_v12_50():
    return _charger_module(
        ROOT / "V12.50.0/socle/mia_v12_moteur_taches.py",
        "mia_v12_50_source",
    )


def charger_v12_60():
    return _charger_module(
        ROOT / "V12.60.0/socle/mia_v12_moteur_planification.py",
        "mia_v12_60_source",
    )


def charger_v12_70():
    return _charger_module(
        ROOT / "V12.70.0/socle/mia_v12_registre_outils.py",
        "mia_v12_70_source",
    )


def charger_v12_80():
    return _charger_module(
        ROOT / "V12.80.0/socle/mia_v12_fichiers_documents.py",
        "mia_v12_80_source",
    )


def charger_v12_90():
    return _charger_module(
        ROOT / "V12.90.0/socle/mia_v12_orchestration_documentaire.py",
        "mia_v12_90_source",
    )


def structurer_et_planifier(demande):
    """
    Premier raccordement réel :
    demande → V12.50 → V12.60

    Aucun outil ni document n'est exécuté.
    """
    v50 = charger_v12_50()
    v60 = charger_v12_60()

    structure = v50.mia50_structurer_demande(demande)
    plan = v60.mia60_proposer_plan(structure)

    return {
        "version_adaptateur": VERSION,
        "etape": "semantique_planification",
        "structure_v12_50": structure,
        "plan_v12_60": plan,
        "validation_humaine_requise": True,
    }


def preparer_orchestration_documentaire(demande, registre=None):
    """
    Raccordement V12.80 → V12.90.

    Aucun document n'est modifié.
    Aucun outil n'est exécuté.
    """
    v80 = charger_v12_80()
    v90 = charger_v12_90()

    document = demande.get("document", "") if isinstance(demande, dict) else ""

    action = demande.get("action", "") if isinstance(demande, dict) else ""

    document_normalise = v80.mia80_normaliser_document(document)

    orchestration = v90.mia90_orchestrer(
        {
            "document": document_normalise,
            "action": action,
        },
        registre=registre or {},
    )

    return {
        "version_adaptateur": VERSION,
        "etape": "orchestration_documentaire",
        "document": document_normalise,
        "orchestration_v12_90": orchestration,
        "validation_humaine_requise": True,
    }


def verifier_chaine():
    """
    Vérifie que les cinq briques peuvent être chargées.
    Aucun traitement utilisateur n'est effectué.
    """
    modules = {
        "V12.50": charger_v12_50,
        "V12.60": charger_v12_60,
        "V12.70": charger_v12_70,
        "V12.80": charger_v12_80,
        "V12.90": charger_v12_90,
    }

    resultat = {}

    for nom, chargeur in modules.items():
        try:
            chargeur()
            resultat[nom] = "chargeable"
        except Exception as exc:
            resultat[nom] = f"erreur: {type(exc).__name__}: {exc}"

    return {
        "version": VERSION,
        "modules": resultat,
        "validation_humaine_requise": True,
    }


def statut():
    return {
        "version": VERSION,
        "fonction": "adaptateur_raccordement",
        "chaine": [
            "V12.50",
            "V12.60",
            "V12.70",
            "V12.80",
            "V12.90",
        ],
        "execution_outils": False,
        "modification_documents": False,
        "ecriture_persistante": False,
        "validation_humaine_requise": True,
    }
