"""
ALKAH-BRAIN / MIA
V12.20.0 — Module 4
Intégration et orchestration de la progression inter-cycle.

Chaîne :
état objectif
    -> actualisation
    -> cohérence
    -> intégration
    -> orchestration

Aucune exécution externe.
"""

from copy import deepcopy

from mia_v12_actualisation_progression import (
    mia20_actualiser_progression,
)
from mia_v12_coherence_progression import (
    mia20_verifier_coherence_progression,
)

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
VERSION = "V12.20.0"


def mia20_integrer_progression_inter_cycle(
    contexte,
    decision,
    etat_precedent,
    nouvelles_informations,
    cycle,
):
    """
    Intègre le contexte, la décision et l'état objectif.

    La décision est conservée comme décision.
    Elle ne transforme jamais une étape en REALISEE.
    """

    if not isinstance(contexte, dict):
        raise ValueError("contexte doit être un dictionnaire")

    if decision is not None and not isinstance(decision, dict):
        raise ValueError("decision doit être un dictionnaire")

    informations = (
        deepcopy(nouvelles_informations)
        if nouvelles_informations is not None
        else {}
    )

    if not isinstance(informations, dict):
        raise ValueError(
            "nouvelles_informations doit être un dictionnaire"
        )

    # La décision est une information associée.
    if decision is not None:
        informations["decision"] = deepcopy(decision)

    etat = mia20_actualiser_progression(
        etat_precedent,
        informations,
        cycle,
    )

    coherence = mia20_verifier_coherence_progression(
        etat,
        decision,
    )

    resultat = {
        "contexte": deepcopy(contexte),
        "decision": deepcopy(decision),
        "etat_objectif": etat,
        "progression": etat.get("progression"),
        "coherence": coherence.get("statut"),
        "anomalies": list(coherence.get("anomalies", [])),
        "cycle": cycle,
        "securite": {
            "autorisation_execution": False,
            "execution": False,
            "lecture_seule": True,
        },
    }

    return resultat


def mia20_orchestrer_progression_inter_cycle(
    contexte,
    decision,
    etat_precedent,
    nouvelles_informations,
    cycle,
):
    """
    Orchestration finale du cycle de progression.
    """

    integration = mia20_integrer_progression_inter_cycle(
        contexte,
        decision,
        etat_precedent,
        nouvelles_informations,
        cycle,
    )

    etat = integration["etat_objectif"]

    # La prochaine étape vient de l'état, jamais d'une
    # réalisation implicite.
    prochaine = etat.get("prochaine_etape")

    return {
        "statut": "ORCHESTRATION_ACTIVE",
        "cycle": cycle,
        "contexte": integration["contexte"],
        "decision": integration["decision"],
        "etat_objectif": etat,
        "progression": integration["progression"],
        "coherence": integration["coherence"],
        "anomalies": integration["anomalies"],
        "prochaine_etape": prochaine,
        "securite": {
            "autorisation_execution": False,
            "execution": False,
            "lecture_seule": True,
        },
    }


def mia20_statut():
    return {
        "version": VERSION,
        "module": "integration_orchestration_progression",
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "statut": "OPERATIONNEL_DEVELOPPEMENT",
    }
