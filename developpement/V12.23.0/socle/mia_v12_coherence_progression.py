"""
ALKAH-BRAIN / MIA
V12.20.0 — Module 3
Vérification de cohérence de la progression inter-cycle.

Règles :
- REALISEE seule compte dans la progression ;
- EN_COURS n'est jamais REALISEE ;
- BLOQUEE n'est jamais REALISEE ;
- décision != réalisation ;
- absence d'information != réalisation ;
- aucune mutation de l'état fourni ;
- lecture seule.
"""

from copy import deepcopy

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
VERSION = "V12.20.0"

STATUTS = (
    "COHERENT",
    "INCOHERENT",
    "A_REEVALUER",
    "NON_DETERMINE",
)


def _copie(etat):
    if not isinstance(etat, dict):
        raise ValueError("etat_objectif doit être un dictionnaire")
    return deepcopy(etat)


def _ids(etat):
    return {
        e.get("id")
        for e in etat.get("etapes", [])
        if isinstance(e, dict) and e.get("id") is not None
    }


def mia20_verifier_coherence_progression(
    etat_objectif,
    decision_precedente=None,
):
    """
    Vérifie la cohérence de l'état courant et, si présente,
    de la décision précédente.

    Retour interne détaillé :
        statut
        coherent
        anomalies
    """

    etat = _copie(etat_objectif)
    anomalies = []

    etapes = etat.get("etapes", [])

    if not isinstance(etapes, list):
        return {
            "statut": "INCOHERENT",
            "coherent": False,
            "anomalies": ["ETAPES_INVALIDES"],
        }

    ids = _ids(etat)

    # Vérification des états.
    for etape in etapes:
        if etape.get("etat") not in (
            "A_FAIRE",
            "EN_COURS",
            "REALISEE",
            "BLOQUEE",
        ):
            anomalies.append(
                f"ETAT_INVALIDE:{etape.get('id')}"
            )

    realisees = {
        e.get("id")
        for e in etapes
        if e.get("etat") == "REALISEE"
    }

    en_cours = {
        e.get("id")
        for e in etapes
        if e.get("etat") == "EN_COURS"
    }

    # Une étape ne peut appartenir à deux catégories.
    if realisees & en_cours:
        anomalies.append("ETAT_MULTIPLE")

    # Progression attendue.
    total = len(etapes)

    if total == 0:
        progression_calculee = None
    else:
        progression_calculee = round(
            len(realisees) / total * 100,
            10,
        )

    progression = etat.get("progression")

    if progression is not None:
        try:
            progression_float = float(progression)
        except (TypeError, ValueError):
            anomalies.append("PROGRESSION_NON_NUMERIQUE")
        else:
            if abs(progression_float - progression_calculee) > 1e-9:
                anomalies.append("PROGRESSION_INCOHERENTE")

    # Étape actuelle.
    actuelle = etat.get("etape_actuelle")

    if actuelle is not None and actuelle not in ids:
        anomalies.append("ETAPE_ACTUELLE_INEXISTANTE")

    if actuelle is not None:
        etat_actuelle = next(
            (
                e for e in etapes
                if e.get("id") == actuelle
            ),
            None,
        )

        # Une étape peut devenir REALISEE entre deux cycles.
        # Le fait qu'elle ait été l'étape actuelle au cycle précédent
        # ne constitue pas une incohérence.
        #
        # La réalisation explicite est validée par l'état de l'étape.
        # La réévaluation de l'étape actuelle relève de l'orchestration.

    # Décision : elle ne réalise jamais l'étape.
    if decision_precedente is not None:
        if not isinstance(decision_precedente, dict):
            anomalies.append("DECISION_INVALIDE")
        else:
            prochaine = decision_precedente.get(
                "prochaine_etape"
            )

            if prochaine is not None:
                if prochaine not in ids:
                    anomalies.append(
                        f"PROCHAINE_ETAPE_INEXISTANTE:{prochaine}"
                    )
                elif prochaine in realisees:
                    anomalies.append(
                        "DECISION_POINTE_ETAPE_DEJA_REALISEE"
                    )

    if total == 0:
        statut = "NON_DETERMINE"
        coherent = not anomalies
    elif anomalies:
        # Une décision vers une étape déjà réalisée nécessite
        # une réévaluation plutôt qu'une corruption de l'état.
        if "DECISION_POINTE_ETAPE_DEJA_REALISEE" in anomalies:
            statut = "A_REEVALUER"
        else:
            statut = "INCOHERENT"
        coherent = False
    else:
        statut = "COHERENT"
        coherent = True

    return {
        "statut": statut,
        "coherent": coherent,
        "anomalies": anomalies,
    }


def mia20_statut():
    return {
        "version": VERSION,
        "module": "coherence_progression",
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "statut": "OPERATIONNEL_DEVELOPPEMENT",
    }
