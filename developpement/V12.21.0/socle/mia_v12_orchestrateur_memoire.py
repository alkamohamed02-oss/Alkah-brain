"""
MIA V12.21 — Orchestrateur mémoire.

Rôle :
1. détecter une demande explicite de mémorisation ;
2. préparer la mémoire candidate ;
3. laisser la couche d'intégration décider de l'enregistrement.

Ce module ne modifie aucune base de données.
"""

from mia_v12_memoire_active import mia_v12_preparer_memoire


def mia_v12_traiter_demande_memoire(question):
    """Traite une éventuelle demande explicite de mémorisation."""

    preparation = mia_v12_preparer_memoire(question)

    if not preparation["valide"]:
        return {
            "memoire_demandee": False,
            "a_enregistrer": False,
            "memoire": None,
            "detection": preparation["detection"],
        }

    return {
        "memoire_demandee": True,
        "a_enregistrer": True,
        "memoire": preparation["memoire"],
        "detection": preparation["detection"],
    }
