"""
ALKAH-BRAIN / MIA
V12.20.0 — Module 2
Actualisation explicite de l'état d'objectif inter-cycle.

PRINCIPE :
- aucune réalisation implicite ;
- une décision ne réalise jamais une étape ;
- EN_COURS ne compte jamais comme REALISEE ;
- BLOQUEE reste BLOQUEE tant qu'aucune information explicite ne la modifie ;
- l'état précédent n'est jamais muté ;
- progression publique = float compatible avec le contrat du Module 1 ;
- cohérence publique = statut texte compatible avec le contrat du Module 1 ;
- sécurité : lecture seule.
"""

from copy import deepcopy

from mia_v12_etat_objectif import (
    mia20_evaluer_progression,
    mia20_verifier_coherence_progression,
)


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


def _valider_cycle(cycle):
    if not isinstance(cycle, int) or isinstance(cycle, bool):
        raise ValueError("cycle doit être un entier")
    if cycle < 1:
        raise ValueError("cycle doit être >= 1")


def _valider_informations(nouvelles_informations):
    if nouvelles_informations is None:
        return {}

    if not isinstance(nouvelles_informations, dict):
        raise ValueError("nouvelles_informations doit être un dictionnaire")

    return nouvelles_informations


def _indexer_etapes(etat):
    return {
        etape.get("id"): etape
        for etape in etat.get("etapes", [])
        if isinstance(etape, dict) and etape.get("id") is not None
    }


def _extraire_mises_a_jour(nouvelles_informations):
    """
    Extrait uniquement les changements d'état explicitement fournis.

    Formats acceptés :
        {"etapes": [{"id": "E1", "etat": "REALISEE"}]}

    La présence d'une décision seule ne produit aucune réalisation.
    """
    mises_a_jour = nouvelles_informations.get("etapes", [])

    if mises_a_jour is None:
        return []

    if not isinstance(mises_a_jour, list):
        raise ValueError("nouvelles_informations['etapes'] doit être une liste")

    resultat = []

    for item in mises_a_jour:
        if not isinstance(item, dict):
            raise ValueError("chaque mise à jour d'étape doit être un dictionnaire")

        identifiant = item.get("id")
        nouvel_etat = item.get("etat")

        if not identifiant:
            raise ValueError("identifiant d'étape absent")

        if nouvel_etat not in ETATS_AUTORISES:
            raise ValueError(f"état invalide pour {identifiant}: {nouvel_etat}")

        resultat.append(
            {
                "id": identifiant,
                "etat": nouvel_etat,
            }
        )

    return resultat


def _reconstruire_listes(etat):
    """
    Reconstruit les listes dérivées sans modifier les règles du Module 1.
    """
    etapes = etat.get("etapes", [])

    etat["etapes_realisees"] = [
        e["id"] for e in etapes if e.get("etat") == "REALISEE"
    ]

    etat["etapes_en_cours"] = [
        e["id"] for e in etapes if e.get("etat") == "EN_COURS"
    ]

    etat["etapes_a_faire"] = [
        e["id"] for e in etapes if e.get("etat") == "A_FAIRE"
    ]

    etat["etapes_bloquees"] = [
        e["id"] for e in etapes if e.get("etat") == "BLOQUEE"
    ]

    if len(etat["etapes_en_cours"]) == 1:
        etat["etape_actuelle"] = etat["etapes_en_cours"][0]
    elif not etat["etapes_en_cours"]:
        # On conserve l'étape actuelle précédente si elle existe.
        actuelle = etat.get("etape_actuelle")
        ids = {e.get("id") for e in etapes}

        if actuelle not in ids:
            etat["etape_actuelle"] = None
    else:
        # Plusieurs étapes en cours : état non déterministe.
        etat["etape_actuelle"] = None

    if etat["etapes_en_cours"]:
        etat["dernier_etat"] = "EN_COURS"
    elif etat["etapes_realisees"]:
        etat["dernier_etat"] = "REALISEE"
    elif etat["etapes_bloquees"]:
        etat["dernier_etat"] = "BLOQUEE"
    else:
        etat["dernier_etat"] = "A_FAIRE"


def _recalculer_progression_publique(etat):
    """
    Le contrat public de V12.20.0 exige :
        progression = float

    Le calcul est :
        REALISEE / total * 100

    EN_COURS et BLOQUEE ne sont jamais comptées comme réalisées.
    """
    resultat = mia20_evaluer_progression(etat)

    if not isinstance(resultat, dict):
        raise ValueError("contrat invalide de mia20_evaluer_progression")

    valeur = resultat.get("progression")

    if valeur is None:
        etat["progression"] = None
    else:
        etat["progression"] = float(valeur)


def _recalculer_coherence_publique(etat, decision_precedente=None):
    """
    Le contrat public de V12.20.0 exige :
        coherence = statut texte

    Le détail reste dans anomalies.
    """
    resultat = mia20_verifier_coherence_progression(
        etat,
        decision_precedente,
    )

    if isinstance(resultat, dict):
        statut = resultat.get("statut", "NON_DETERMINE")
        anomalies = resultat.get("anomalies", [])

        etat["coherence"] = statut

        if anomalies:
            existantes = etat.setdefault("anomalies", [])

            for anomalie in anomalies:
                if anomalie not in existantes:
                    existantes.append(anomalie)
    else:
        etat["coherence"] = str(resultat)


def mia20_actualiser_progression(
    etat_precedent,
    nouvelles_informations,
    cycle,
):
    """
    Actualise l'état objectif au cycle suivant.

    Règle fondamentale :
    seule une information explicite d'état peut modifier une étape.

    Une décision :
        {"decision": {"prochaine_etape": "E4"}}

    ne modifie PAS l'état de E4.
    """

    _valider_cycle(cycle)
    nouvelles_informations = _valider_informations(nouvelles_informations)

    if not isinstance(etat_precedent, dict):
        raise ValueError("etat_precedent doit être un dictionnaire")

    ancien_cycle = etat_precedent.get("cycle")

    if not isinstance(ancien_cycle, int):
        raise ValueError("cycle précédent invalide")

    if cycle <= ancien_cycle:
        raise ValueError("le nouveau cycle doit être strictement supérieur")

    nouvel_etat = deepcopy(etat_precedent)

    nouvel_etat["cycle"] = cycle
    nouvel_etat.setdefault("anomalies", [])
    nouvel_etat["anomalies"] = list(nouvel_etat["anomalies"])

    index = _indexer_etapes(nouvel_etat)
    mises_a_jour = _extraire_mises_a_jour(nouvelles_informations)

    # ============================================================
    # APPLICATION DES CHANGEMENTS EXPLICITES UNIQUEMENT
    # ============================================================
    for mise in mises_a_jour:
        identifiant = mise["id"]
        nouvel_etat_etape = mise["etat"]

        if identifiant not in index:
            anomalie = f"ETAPE_INCONNUE:{identifiant}"

            if anomalie not in nouvel_etat["anomalies"]:
                nouvel_etat["anomalies"].append(anomalie)

            continue

        etape = index[identifiant]

        # Une réalisation doit être explicitement déclarée.
        etape["etat"] = nouvel_etat_etape
        etape["dernier_cycle"] = cycle

    # ============================================================
    # LA DECISION NE REALISE JAMAIS L'ETAPE
    # ============================================================
    decision = nouvelles_informations.get("decision")

    if decision is not None:
        if not isinstance(decision, dict):
            raise ValueError("decision doit être un dictionnaire")

        nouvel_etat["decision_associee"] = deepcopy(decision)

        prochaine = decision.get("prochaine_etape")

        if prochaine is not None:
            nouvel_etat["prochaine_etape"] = prochaine

            if prochaine not in index:
                anomalie = f"PROCHAINE_ETAPE_INCONNUE:{prochaine}"

                if anomalie not in nouvel_etat["anomalies"]:
                    nouvel_etat["anomalies"].append(anomalie)
    else:
        # Continuité : conserver la décision précédente.
        nouvel_etat["decision_associee"] = deepcopy(
            etat_precedent.get("decision_associee")
        )
        nouvel_etat["prochaine_etape"] = etat_precedent.get(
            "prochaine_etape"
        )

    # ============================================================
    # RECONSTRUCTION DERIVEE
    # ============================================================
    _reconstruire_listes(nouvel_etat)

    # La progression publique reste un FLOAT.
    _recalculer_progression_publique(nouvel_etat)

    # La cohérence publique reste un STATUT texte.
    decision_associee = nouvel_etat.get("decision_associee")
    _recalculer_coherence_publique(
        nouvel_etat,
        decision_associee,
    )

    # ============================================================
    # SECURITE INVARIANTE
    # ============================================================
    nouvel_etat["securite"] = {
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
    }

    return nouvel_etat


def mia20_statut():
    return {
        "version": VERSION,
        "module": "actualisation_progression",
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "statut": "OPERATIONNEL_DEVELOPPEMENT",
    }
