"""
PASSERELLE MIA → ALKAH-BRAIN

Couche indépendante entre l'interface MIA
et le moteur ALKAH-BRAIN V76/MIA25/B33.

Cette passerelle ne modifie pas V62.
"""

import importlib.util
from pathlib import Path


BASE = Path(__file__).resolve().parent

FICHIER_MOTEUR = BASE / "alkah_brain_v76_MIA25_B33_CORRIGEE_VALIDE.py"


def charger_alkah_brain():
    """Charge le moteur V76/MIA25/B33 validé."""
    if not FICHIER_MOTEUR.is_file():
        raise FileNotFoundError(
            f"Moteur introuvable : {FICHIER_MOTEUR}"
        )

    spec = importlib.util.spec_from_file_location(
        "alkah_brain_v62",
        FICHIER_MOTEUR
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            "Impossible de charger ALKAH-BRAIN V76/MIA25/B33."
        )

    moteur = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moteur)

    return moteur


def statut_mia():
    """Vérifie la connexion logique avec V62."""
    moteur = charger_alkah_brain()

    return {
        "statut": "ok",
        "moteur": "ALKAH-BRAIN",
        "version": "V76/MIA25/B33",
        "mia62_disponible": hasattr(
            moteur,
            "mia62_identifier_version_recente_fiable"
        ),
    }


if __name__ == "__main__":

    resultat = statut_mia()

    print("=== PASSERELLE MIA ===")
    print("Statut :", resultat["statut"])
    print("Moteur :", resultat["moteur"])
    print("Version :", resultat["version"])
    print(
        "MIA62 disponible :",
        resultat["mia62_disponible"]
    )
    print("=== PASSERELLE VALIDEE ===")
