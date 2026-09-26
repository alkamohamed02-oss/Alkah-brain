import re

V1215_VERSION = "V12.15.0"


def mia15_normaliser(texte):
    texte = str(texte or "").strip().lower()
    texte = re.sub(
        r"[^\w\sàâäçéèêëîïôöùûüÿœæ-]",
        " ",
        texte,
        flags=re.UNICODE
    )
    return re.sub(r"\s+", " ", texte).strip()


def mia15_analyser_cycle(question, etat=None):
    texte = mia15_normaliser(question)
    etat = etat if isinstance(etat, dict) else {}

    confirmations = (
        "je confirme",
        "je valide",
        "confirme",
        "confirmer",
        "validation confirmée",
        "validation confirmee",
        "oui je confirme",
        "oui je valide",
    )

    refus = (
        "je refuse",
        "refus",
        "non",
        "annule",
        "annuler",
        "stop",
    )

    continuations = (
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

    modifications = (
        "modifie l objectif",
        "modifier l objectif",
        "change l objectif",
        "changer l objectif",
        "nouvel objectif",
        "je change l objectif",
    )

    decision = etat.get("derniere_decision")
    objectif = etat.get("objectif_actif")

    confirmation = any(texte == x or texte.startswith(x + " ") for x in confirmations)
    refus_detecte = any(texte == x or texte.startswith(x + " ") for x in refus)
    continuation = any(texte == x or texte.startswith(x + " ") for x in continuations)
    modification = any(x in texte for x in modifications)

    if modification:
        statut = "modification_objectif"
    elif confirmation:
        statut = "confirmation"
    elif refus_detecte:
        statut = "refus"
    elif continuation and decision:
        statut = "continuation"
    elif decision:
        statut = "decision_en_attente"
    else:
        statut = "nouvelle_decision"

    return {
        "version": V1215_VERSION,
        "statut": statut,
        "confirmation": confirmation,
        "refus": refus_detecte,
        "continuation": continuation,
        "modification_objectif": modification,
        "decision_presente": bool(decision),
        "objectif_present": bool(objectif),
        "autorisation_execution": False,
        "lecture_seule": True,
    }


def mia15_cycle_decisionnel(question, etat=None):
    etat = etat if isinstance(etat, dict) else {}
    suivi = mia15_analyser_cycle(question, etat)

    return {
        "version": V1215_VERSION,
        "question": question,
        "etat_precedent": etat,
        "suivi": suivi,
        "autorisation_execution": False,
        "lecture_seule": True,
    }


def mia15_statut():
    return {
        "version": V1215_VERSION,
        "module": "cycle_decisionnel",
        "active": True,
        "nouvelle_decision": True,
        "decision_en_attente": True,
        "confirmation": True,
        "refus": True,
        "modification_objectif": True,
        "continuation": True,
        "execution": False,
        "autorisation_utilisateur": True,
        "lecture_seule": True,
    }
