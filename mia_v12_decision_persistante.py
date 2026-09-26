from datetime import datetime

V1214_VERSION = "V12.14.1"


def mia14_creer_etat_decision(
    decision=None,
    projet_actif=None,
    objectif_actif=None,
    sujet_actif=None
):
    decision = decision if isinstance(decision, dict) else {}

    return {
        "version": V1214_VERSION,
        "projet_actif": projet_actif,
        "objectif_actif": objectif_actif,
        "sujet_actif": sujet_actif,
        "derniere_decision": decision,
        "statut_decision": (
            "decision_en_attente"
            if decision
            else "aucune_decision"
        ),
        "autorisation_execution": False,
        "lecture_seule": True,
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def mia14_analyser_suivi(
    question,
    etat_decision=None
):
    etat_decision = (
        etat_decision
        if isinstance(etat_decision, dict)
        else {}
    )

    import re
    texte = str(question or "").strip().lower()
    texte = re.sub(r"[^\w\sàâäçéèêëîïôöùûüÿœæ-]", " ", texte, flags=re.UNICODE)
    texte = re.sub(r"\s+", " ", texte).strip()

    confirmation = texte in (
        "oui",
        "d'accord",
        "daccord",
        "je confirme",
        "je valide",
        "confirme",
        "confirmer"
    )

    refus = texte in (
        "non",
        "annule",
        "annuler",
        "je refuse",
        "arrête",
        "arrete"
    )

    continuation = texte in (
        "la suite",
        "fais la suite",
        "continue",
        "continuons",
        "poursuis",
        "reprends",
        "on continue"
    )

    if confirmation:
        statut = "confirmation"
    elif refus:
        statut = "refus"
    elif continuation:
        statut = "continuation"
    elif etat_decision.get("derniere_decision"):
        statut = "decision_en_attente"
    else:
        statut = "aucune_decision"

    return {
        "version": V1214_VERSION,
        "statut": statut,
        "confirmation": confirmation,
        "refus": refus,
        "continuation": continuation,
        "decision_presente": bool(
            etat_decision.get("derniere_decision")
        ),
        "autorisation_execution": False,
        "lecture_seule": True,
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def mia14_continuite_decisionnelle_persistante(
    question,
    etat_decision=None
):
    analyse = mia14_analyser_suivi(
        question,
        etat_decision
    )

    return {
        "version": V1214_VERSION,
        "question": question,
        "etat_precedent": (
            etat_decision
            if isinstance(etat_decision, dict)
            else {}
        ),
        "suivi": analyse,
        "autorisation_execution": False,
        "lecture_seule": True,
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def mia14_statut():
    return {
        "version": V1214_VERSION,
        "module": "decision_persistante",
        "active": True,
        "persistance_decision": True,
        "suivi_confirmation": True,
        "suivi_refus": True,
        "suivi_continuation": True,
        "execution": False,
        "autorisation_utilisateur": False,
        "lecture_seule": True
    }
