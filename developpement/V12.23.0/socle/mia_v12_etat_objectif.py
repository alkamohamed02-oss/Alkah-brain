"""
ALKAH-BRAIN / MIA
V12.20.0 — Module 1
Etat d'objectif, progression et cohérence

STATUT : DEVELOPPEMENT
EXECUTION REELLE : INTERDITE
LECTURE SEULE : ACTIVE
"""

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True

VERSION = "V12.20.0"

ETATS_AUTORISES = (
    "A_FAIRE",
    "EN_COURS",
    "REALISEE",
    "BLOQUEE",
)

STATUTS_COHERENCE = (
    "COHERENT",
    "INCOHERENT",
    "A_REEVALUER",
    "NON_DETERMINE",
)


def mia20_creer_etat_objectif(objectif, plan, cycle):
    """Crée un état initial structuré sans exécution réelle."""

    if not isinstance(objectif, dict):
        raise TypeError("objectif doit être un dictionnaire")

    if not isinstance(plan, dict):
        raise TypeError("plan doit être un dictionnaire")

    if "id" not in objectif:
        raise ValueError("objectif.id obligatoire")

    if "etapes" not in plan:
        raise ValueError("plan.etapes obligatoire")

    if not isinstance(plan["etapes"], list):
        raise TypeError("plan.etapes doit être une liste")

    etapes = []

    for index, etape in enumerate(plan["etapes"], start=1):
        if not isinstance(etape, dict):
            raise TypeError("chaque étape doit être un dictionnaire")

        etape_id = etape.get("id", f"etape_{index}")

        etapes.append({
            "id": etape_id,
            "ordre": etape.get("ordre", index),
            "description": etape.get("description", ""),
            "etat": etape.get("etat", "A_FAIRE"),
            "cycle_creation": cycle,
            "dernier_cycle": cycle,
        })

    etat = {
        "objectif": objectif,
        "plan": {
            "id": plan.get("id"),
            "description": plan.get("description", ""),
        },
        "etapes": etapes,
        "etape_actuelle": None,
        "etapes_realisees": [],
        "etapes_en_cours": [],
        "etapes_a_faire": [],
        "etapes_bloquees": [],
        "progression": None,
        "dernier_etat": "INITIAL",
        "decision_associee": None,
        "prochaine_etape": None,
        "coherence": "NON_DETERMINE",
        "anomalies": [],
        "cycle": cycle,
        "securite": {
            "autorisation_execution": False,
            "execution": False,
            "lecture_seule": True,
        },
    }

    _reconstruire_etat(etat)

    return etat


def mia20_evaluer_progression(etat_objectif):
    """Calcule la progression exclusivement à partir des étapes REALISEE."""

    etapes = etat_objectif.get("etapes", [])

    total = len(etapes)

    realisees = sum(
        1 for e in etapes
        if e.get("etat") == "REALISEE"
    )

    en_cours = sum(
        1 for e in etapes
        if e.get("etat") == "EN_COURS"
    )

    a_faire = sum(
        1 for e in etapes
        if e.get("etat") == "A_FAIRE"
    )

    bloquees = sum(
        1 for e in etapes
        if e.get("etat") == "BLOQUEE"
    )

    if total == 0:
        progression = None
        statut = "NON_DETERMINE"
    else:
        progression = (realisees / total) * 100
        progression = round(progression, 2)

        if progression == 100:
            statut = "TERMINE"
        elif bloquees > 0 and realisees + bloquees == total:
            statut = "BLOQUE"
        else:
            statut = "EN_PROGRESSION"

    return {
        "nombre_total_etapes": total,
        "nombre_etapes_realisees": realisees,
        "nombre_etapes_en_cours": en_cours,
        "nombre_etapes_a_faire": a_faire,
        "nombre_etapes_bloquees": bloquees,
        "progression": progression,
        "statut_progression": statut,
    }


def mia20_verifier_coherence_progression(
    etat_objectif,
    decision_precedente=None
):
    """Vérifie la cohérence interne de l'état et sa relation
    avec une éventuelle décision précédente.
    """

    anomalies = []
    etapes = etat_objectif.get("etapes", [])

    ids = [e.get("id") for e in etapes]

    if len(ids) != len(set(ids)):
        anomalies.append("IDENTIFIANTS_ETAPES_DUPLIQUES")

    for etape in etapes:
        if etape.get("etat") not in ETATS_AUTORISES:
            anomalies.append(
                f"ETAT_INVALIDE:{etape.get('id')}"
            )

    realisees = {
        e.get("id") for e in etapes
        if e.get("etat") == "REALISEE"
    }

    en_cours = {
        e.get("id") for e in etapes
        if e.get("etat") == "EN_COURS"
    }

    a_faire = {
        e.get("id") for e in etapes
        if e.get("etat") == "A_FAIRE"
    }

    bloquees = {
        e.get("id") for e in etapes
        if e.get("etat") == "BLOQUEE"
    }

    if realisees & a_faire:
        anomalies.append("ETAPE_REALISEE_ET_A_FAIRE")

    if realisees & en_cours:
        anomalies.append("ETAPE_REALISEE_ET_EN_COURS")

    if realisees & bloquees:
        anomalies.append("ETAPE_REALISEE_ET_BLOQUEE")

    etape_actuelle = etat_objectif.get("etape_actuelle")

    if etape_actuelle is not None and etape_actuelle not in ids:
        anomalies.append("ETAPE_ACTUELLE_INEXISTANTE")

    evaluation = mia20_evaluer_progression(etat_objectif)

    progression_declared = etat_objectif.get("progression")

    if progression_declared is not None:
        progression_calculee = evaluation["progression"]

        if progression_declared != progression_calculee:
            anomalies.append("PROGRESSION_INCOHERENTE")

    if decision_precedente is not None:
        objectif_etat = etat_objectif.get("objectif", {})
        objectif_decision = decision_precedente.get("objectif", {})

        if (
            objectif_decision
            and objectif_etat.get("id") != objectif_decision.get("id")
        ):
            anomalies.append("OBJECTIF_DECISION_INCOMPATIBLE")

        prochaine = decision_precedente.get("prochaine_etape")

        if prochaine is not None and prochaine not in ids:
            anomalies.append("PROCHAINE_ETAPE_INEXISTANTE")

        if prochaine in realisees:
            anomalies.append("DECISION_ETAT_A_REEVALUER")

    if anomalies:
        if "DECISION_ETAT_A_REEVALUER" in anomalies:
            statut = "A_REEVALUER"
        else:
            statut = "INCOHERENT"
        coherent = False
    elif not etapes:
        statut = "NON_DETERMINE"
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
    """Retourne le statut sécurisé du module."""

    return {
        "version": VERSION,
        "statut": "DEVELOPPEMENT",
        "autorisation_execution": False,
        "execution": False,
        "lecture_seule": True,
    }


def _reconstruire_etat(etat):
    """Reconstruit les listes dérivées et la progression."""

    etapes = etat["etapes"]

    etat["etapes_realisees"] = [
        e["id"] for e in etapes
        if e["etat"] == "REALISEE"
    ]

    etat["etapes_en_cours"] = [
        e["id"] for e in etapes
        if e["etat"] == "EN_COURS"
    ]

    etat["etapes_a_faire"] = [
        e["id"] for e in etapes
        if e["etat"] == "A_FAIRE"
    ]

    etat["etapes_bloquees"] = [
        e["id"] for e in etapes
        if e["etat"] == "BLOQUEE"
    ]

    evaluation = mia20_evaluer_progression(etat)

    etat["progression"] = evaluation["progression"]

    if etat["etapes_en_cours"]:
        etat["etape_actuelle"] = etat["etapes_en_cours"][0]
    elif etat["etapes_a_faire"]:
        etat["etape_actuelle"] = etat["etapes_a_faire"][0]
    else:
        etat["etape_actuelle"] = None

    controle = mia20_verifier_coherence_progression(etat)

    etat["coherence"] = controle["statut"]
    etat["anomalies"] = controle["anomalies"]

    if evaluation["statut_progression"] == "TERMINE":
        etat["dernier_etat"] = "TERMINE"
    elif evaluation["statut_progression"] == "BLOQUE":
        etat["dernier_etat"] = "BLOQUE"
    elif etat["etapes_en_cours"]:
        etat["dernier_etat"] = "EN_COURS"
    else:
        etat["dernier_etat"] = "A_FAIRE"
