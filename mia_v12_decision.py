# -*- coding: utf-8 -*-
"""
ALKAH-BRAIN / MIA
V12.13 — Continuité décisionnelle
Version initiale : V12.13.0

Objectif :
Transformer la continuité conversationnelle de V12.12
en identification de l'étape logique suivante.

IMPORTANT :
- Ne modifie pas B34 / V76.
- Ne modifie pas V12.11.
- Module autonome pour validation progressive.
"""

from datetime import datetime


V1213_VERSION = "V12.13.0"


def mia13_normaliser_texte(texte):
    """Normalise un texte pour les comparaisons simples."""
    return " ".join(
        str(texte or "").strip().lower().split()
    )


def mia13_est_continuation(question):
    """Détecte une demande de poursuite du travail."""
    texte = mia13_normaliser_texte(question)

    expressions = (
        "fais la suite",
        "faire la suite",
        "la suite",
        "continue",
        "continuons",
        "poursuis",
        "reprends",
        "reprendre",
        "continue le travail",
        "poursuis le travail",
        "on continue",
        "suite",
    )

    return any(
        expression in texte
        for expression in expressions
    )


def mia13_construire_etape_suivante(
    projet=None,
    objectif=None,
    sujet=None,
    derniere_question=None,
    derniere_reponse=None,
):
    """
    Identifie une étape logique suivante à partir du contexte actif.

    Cette V12.13.0 reste volontairement déterministe :
    elle ne prétend pas encore planifier arbitrairement un projet.
    """

    projet = str(projet or "").strip()
    objectif = str(objectif or "").strip()
    sujet = str(sujet or "").strip()
    derniere_question = str(
        derniere_question or ""
    ).strip()
    derniere_reponse = str(
        derniere_reponse or ""
    ).strip()

    contexte_present = bool(
        projet or objectif or sujet
    )

    if not contexte_present:
        return {
            "etape_identifiee": False,
            "type": "aucun_contexte",
            "etape_suivante": None,
            "raison": "aucun_contexte_projet_actif",
            "confiance": 0,
        }

    # Cas prioritaire : continuité du projet ALKAH-BRAIN / MIA.
    objectif_normalise = mia13_normaliser_texte(
        objectif
    )
    projet_normalise = mia13_normaliser_texte(
        projet
    )

    if (
        "continuité conversationnelle" in objectif_normalise
        or "continuite conversationnelle" in objectif_normalise
        or "continuité multi-tour" in objectif_normalise
        or "continuite multi-tour" in objectif_normalise
    ):
        return {
            "etape_identifiee": True,
            "type": "evolution_logique",
            "etape_suivante": (
                "Passer de la continuité conversationnelle "
                "à la continuité décisionnelle : "
                "identifier et proposer automatiquement "
                "la prochaine étape logique du projet."
            ),
            "raison": (
                "V12.12.5 assure la continuité du contexte ; "
                "l'étape suivante est l'exploitation "
                "décisionnelle de ce contexte."
            ),
            "confiance": 95,
        }

    if (
        "alkah-brain" in projet_normalise
        or "mia" in projet_normalise
    ):
        return {
            "etape_identifiee": True,
            "type": "evolution_logique",
            "etape_suivante": (
                "Analyser l'état actif du projet, "
                "identifier le prochain objectif non terminé "
                "et proposer une action concrète."
            ),
            "raison": (
                "Projet MIA/ALKAH-BRAIN identifié."
            ),
            "confiance": 85,
        }

    # Cas générique : contexte présent mais aucune règle
    # spécialisée ne permet encore de déterminer une étape.
    return {
        "etape_identifiee": True,
        "type": "analyse_requise",
        "etape_suivante": (
            "Analyser le sujet et l'objectif actifs "
            "avant de proposer la prochaine action."
        ),
        "raison": (
            "Contexte présent mais aucune règle "
            "décisionnelle spécialisée."
        ),
        "confiance": 60,
    }


def mia13_analyser_continuite(
    question,
    etat=None,
    contexte=None,
):
    """
    Point d'entrée principal V12.13.

    Ne déclenche une décision de continuité que si
    la question correspond à une demande de poursuite.
    """

    etat = etat if isinstance(etat, dict) else {}
    contexte = (
        contexte
        if isinstance(contexte, dict)
        else {}
    )

    continuation = mia13_est_continuation(
        question
    )

    projet = (
        contexte.get("projet_actif")
        or etat.get("projet_actif")
    )

    objectif = (
        contexte.get("objectif_actif")
        or etat.get("objectif_actif")
    )

    sujet = (
        contexte.get("sujet_actif")
        or etat.get("sujet_actif")
    )

    if not continuation:
        return {
            "version": V1213_VERSION,
            "continuation_detectee": False,
            "decisionnelle_active": False,
            "decision": None,
        }

    decision = mia13_construire_etape_suivante(
        projet=projet,
        objectif=objectif,
        sujet=sujet,
        derniere_question=etat.get(
            "derniere_question"
        ),
        derniere_reponse=etat.get(
            "derniere_reponse"
        ),
    )

    return {
        "version": V1213_VERSION,
        "continuation_detectee": True,
        "decisionnelle_active": True,
        "projet_actif": projet,
        "objectif_actif": objectif,
        "sujet_actif": sujet,
        "decision": decision,
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        ),
    }


def mia13_statut():
    """Retourne le statut du module V12.13."""
    return {
        "version": V1213_VERSION,
        "module": "continuité décisionnelle",
        "statut": "prototype",
        "autonome": True,
        "modifie_b34": False,
        "modifie_v12_11": False,
    }


if __name__ == "__main__":
    print("=== MIA V12.13 ===")
    print(mia13_statut())
