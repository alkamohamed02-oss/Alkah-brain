
from datetime import datetime
from mia_v12_continuite import mia_v12_determiner_prochaine_etape

V12133_VERSION = "V12.13.3"


def mia133_normaliser(texte):
    return " ".join(
        str(texte or "").strip().lower().split()
    )


def mia133_historique_present(etat):
    if not isinstance(etat, dict):
        return False

    return bool(
        etat.get("numero_tour", 0)
        or etat.get("derniere_question")
        or etat.get("derniere_reponse")
    )


def mia133_analyser_etat(
    projet=None,
    objectif=None,
    sujet=None,
    derniere_question=None,
    derniere_reponse=None,
    numero_tour=0
):
    contexte = {
        "projet_actif": projet,
        "objectif_actif": objectif,
        "sujet_actif": sujet,
        "derniere_question": derniere_question,
        "derniere_reponse": derniere_reponse,
        "numero_tour": numero_tour
    }

    if not projet:
        return {
            "etat_analyse": False,
            "statut": "contexte_insuffisant",
            "contexte": contexte,
            "raison": "Projet actif absent.",
            "confiance": 0
        }

    if not objectif:
        return {
            "etat_analyse": True,
            "statut": "objectif_manquant",
            "contexte": contexte,
            "raison": "Le projet est identifié mais son objectif actif manque.",
            "confiance": 70
        }

    if numero_tour <= 0:
        return {
            "etat_analyse": True,
            "statut": "historique_absent",
            "contexte": contexte,
            "raison": "Aucun historique conversationnel exploitable.",
            "confiance": 65
        }

    return {
        "etat_analyse": True,
        "statut": "contexte_exploitable",
        "contexte": contexte,
        "raison": (
            "Projet, objectif et historique conversationnel "
            "disponibles pour déterminer la prochaine action."
        ),
        "confiance": 90
    }


def mia133_determiner_action(
    analyse,
    derniere_question=None,
    derniere_reponse=None
):
    if not isinstance(analyse, dict):
        return {
            "action_identifiee": False,
            "action": None,
            "raison": "Analyse absente.",
            "confiance": 0
        }

    contexte = analyse.get("contexte", {})

    projet = contexte.get("projet_actif")
    objectif = contexte.get("objectif_actif")

    if not projet:
        return {
            "action_identifiee": False,
            "action": None,
            "raison": "Projet actif absent.",
            "confiance": 0
        }

    continuite_v12 = analyse.get("continuite_v12", {})
    if isinstance(continuite_v12, dict):
        prochaine_etape = continuite_v12.get("prochaine_etape", {})
        if isinstance(prochaine_etape, dict):
            action_v12 = prochaine_etape.get("prochaine_etape")
            if action_v12:
                return {
                    "action_identifiee": True,
                    "action": action_v12,
                    "type": "prochaine_action_logique",
                    "autorisation_execution": False,
                    "raison": prochaine_etape.get(
                        "raison",
                        "Étape déterminée par la continuité V12.11."
                    ),
                    "confiance": 95
                }

    if not objectif:
        return {
            "action_identifiee": True,
            "action": (
                "Identifier ou confirmer l'objectif actif "
                "du projet avant de poursuivre."
            ),
            "type": "clarification",
            "autorisation_execution": False,
            "raison": "Objectif manquant.",
            "confiance": 80
        }

    objectif_normalise = mia133_normaliser(objectif)

    if (
        "continuité conversationnelle" in objectif_normalise
        or "continuite conversationnelle" in objectif_normalise
    ):
        return {
            "action_identifiee": True,
            "action": (
                "Examiner l'état actuel de la continuité, "
                "identifier le point non terminé et proposer "
                "la prochaine évolution logique de MIA."
            ),
            "type": "prochaine_action_logique",
            "autorisation_execution": False,
            "raison": (
                "La continuité conversationnelle est active "
                "et l'historique permet une décision suivante."
            ),
            "confiance": 95
        }

    if "alkah-brain" in mia133_normaliser(projet):
        prochaine = mia_v12_determiner_prochaine_etape(
            projet_identifie=projet,
            contexte_projet=contexte,
            manques=[],
            etat_projet={}
        )
        return {
            "action_identifiee": True,
            "action": prochaine.get(
                "prochaine_etape",
                "Analyser la prochaine étape du projet."
            ),
            "type": "prochaine_action_logique",
            "autorisation_execution": False,
            "raison": prochaine.get(
                "raison",
                "Prochaine étape déterminée par la continuité V12."
            ),
            "confiance": 90
        }

    return {
        "action_identifiee": True,
        "action": (
            "Analyser le contexte disponible et proposer "
            "la prochaine action logique."
        ),
        "type": "analyse",
        "autorisation_execution": False,
        "raison": "Contexte exploitable.",
        "confiance": 75
    }


def mia133_continuite_decisionnelle(
    question,
    etat=None,
    contexte=None,
    continuite_v12=None
):
    etat = etat if isinstance(etat, dict) else {}
    contexte = contexte if isinstance(contexte, dict) else {}

    projet = (
        contexte.get("projet_actif")
        or etat.get("projet_actif")
    )

    objectif = (
        contexte.get("objectif_actif")
        or etat.get("objectif_actif")
    )
    if not objectif and isinstance(continuite_v12, dict):
        c = continuite_v12.get("contexte", {})
        if isinstance(c, dict):
            objectif = c.get("objectif") or c.get("plan", {}).get("objectif")

    sujet = (
        contexte.get("sujet_actif")
        or etat.get("sujet_actif")
    )

    numero_tour = (
        etat.get("numero_tour", 0)
        or 0
    )

    if not projet and isinstance(continuite_v12, dict):
        projet = continuite_v12.get("projet") or continuite_v12.get("projet_identifie")
    analyse = mia133_analyser_etat(
        projet=projet,
        objectif=objectif,
        sujet=sujet,
        derniere_question=etat.get("derniere_question"),
        derniere_reponse=etat.get("derniere_reponse"),
        numero_tour=numero_tour
    )

    # Pont lecture seule vers la continuité réelle V12.11.
    # Les données existantes sont transmises au moteur de décision
    # sans aucune écriture ni modification de la mémoire.
    if isinstance(continuite_v12, dict):
        contexte_continuite = continuite_v12.get("contexte", {})
        if isinstance(contexte_continuite, dict):
            for cle, valeur in contexte_continuite.items():
                if cle == "contexte":
                    continue
                if valeur not in (None, "", [], {}):
                    contexte[cle] = valeur

        etat_continuite = continuite_v12.get("etat", {})
        manques_continuite = continuite_v12.get("manques", {})
        decisions_continuite = continuite_v12.get("decisions", {})
        prochaine_etape_continuite = continuite_v12.get("prochaine_etape", {})

        if not isinstance(etat_continuite, dict):
            etat_continuite = {}
        if not isinstance(manques_continuite, (dict, list)):
            manques_continuite = {}
        if not isinstance(decisions_continuite, (dict, list)):
            decisions_continuite = {}
        if not isinstance(prochaine_etape_continuite, dict):
            prochaine_etape_continuite = {}

        analyse["continuite_v12"] = {
            "etat": etat_continuite,
            "manques": manques_continuite,
            "decisions": decisions_continuite,
            "prochaine_etape": prochaine_etape_continuite
        }

    if projet:
        contexte["projet_actif"] = projet
    if objectif:
        contexte["objectif_actif"] = objectif

        # Synchronisation lecture seule du contexte V12.11.
        contexte_analyse = analyse.get("contexte", {})
        if not isinstance(contexte_analyse, dict):
            contexte_analyse = {}
        for cle, valeur in contexte.items():
            if valeur not in (None, "", [], {}):
                contexte_analyse[cle] = valeur
        analyse["contexte"] = contexte_analyse

    if not objectif and isinstance(contexte.get("plan"), dict):
        objectif = contexte["plan"].get("objectif")
    if objectif:
        contexte["objectif_actif"] = objectif
        analyse["contexte"]["objectif_actif"] = objectif
        analyse["statut"] = "contexte_complet"

    action = mia133_determiner_action(
        analyse,
        derniere_question=etat.get("derniere_question"),
        derniere_reponse=etat.get("derniere_reponse")
    )

    return {
        "version": V12133_VERSION,
        "question": question,
        "projet_actif": projet,
        "objectif_actif": objectif,
        "sujet_actif": sujet,
        "etat": analyse,
        "prochaine_action": action,
        "autorisation_execution": False,
        "lecture_seule": True,
        "horodatage": datetime.now().isoformat(
            timespec="seconds"
        )
    }


def mia133_statut():
    return {
        "version": V12133_VERSION,
        "module": "continuite_decisionnelle_reelle",
        "active": True,
        "analyse_etat": True,
        "determination_action": True,
        "execution": False,
        "autorisation_utilisateur": False,
        "lecture_seule": True
    }
