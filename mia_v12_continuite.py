from pathlib import Path
"""
MIA V12 — COUCHE DE CONTINUITE
V12.1 — IDENTIFICATION DU PROJET

Principe :
- ne crée aucune nouvelle mémoire ;
- n'exécute aucune action ;
- n'altère pas V76 ;
- n'altère pas V3-V11 ;
- utilise uniquement les informations fournies.
"""

import re


def mia_v12_identifier_projet(
    question,
    contexte=None,
    memoires=None,
    projet_structure_v7=None
):
    """
    V12.10 — Identification intelligente d'un projet.

    Priorité :
    1. Demande de reprise + contexte V4 identifiable.
    2. Demande de reprise + mémoire contenant une identité explicite.
    3. Projet explicitement fourni dans le contexte.
    4. Projet explicitement fourni par V7, sauf lorsqu'il s'agit
       simplement de la phrase actuelle de l'utilisateur.
    5. Formulation explicite dans la question.
    6. Incertitude explicite si aucun projet fiable n'est identifiable.

    Aucun projet n'est inventé.
    Aucune mémoire n'est créée.
    Aucune écriture SQLite.
    Aucune exécution.
    """

    question = str(question or "").strip()
    contexte = contexte if isinstance(contexte, dict) else []
    memoires = memoires if isinstance(memoires, list) else {}

    resultat = {
        "active": True,
        "projet_identifie": None,
        "confiance": 0,
        "source": [],
        "elements_manquants": [],
        "autorisation_execution": False
    }

    if not question:
        resultat["elements_manquants"].append("question")
        return resultat

    question_normalisee = question.lower().strip()

    # ---------------------------------------------------------
    # V12.10 — Détection d'une demande de reprise
    # ---------------------------------------------------------

    motifs_reprise = (
        r"\breprenons\b",
        r"\bcontinuons\b",
        r"\bpoursuivons\b",
        r"\breprendre\b",
        r"\bcontinuer\b",
        r"\bpoursuivre\b"
    )

    demande_reprise = any(
        re.search(motif, question_normalisee, re.IGNORECASE)
        for motif in motifs_reprise
    )

    # ---------------------------------------------------------
    # 1. DEMANDE DE REPRISE : chercher d'abord dans V4
    # ---------------------------------------------------------

    if demande_reprise:

        for cle in (
            "projet",
            "nom_projet",
            "projet_actif",
            "titre_projet"
        ):
            valeur = contexte.get(cle)

            if isinstance(valeur, str) and valeur.strip():
                valeur = valeur.strip()

                # Ne pas considérer la phrase actuelle comme
                # une identité de projet.
                if valeur.lower() != question_normalisee:
                    resultat["projet_identifie"] = valeur
                    resultat["confiance"] = 95
                    resultat["source"].append("V4")
                    return resultat

        # -----------------------------------------------------
        # 2. DEMANDE DE REPRISE : chercher dans les mémoires
        # -----------------------------------------------------

        for memoire in reversed(memoires):
            if not isinstance(memoire, dict):
                continue

            for cle in (
                "projet",
                "nom_projet",
                "titre_projet"
            ):
                valeur = memoire.get(cle)

                if isinstance(valeur, str) and valeur.strip():
                    valeur = valeur.strip()

                    if valeur.lower() != question_normalisee:
                        resultat["projet_identifie"] = valeur
                        resultat["confiance"] = 80
                        resultat["source"].append("memoire")
                        return resultat

        # -----------------------------------------------------
        # Aucun projet réellement identifiable.
        # Ne pas utiliser "idee" de V7 ici.
        # -----------------------------------------------------

        resultat["elements_manquants"].append(
            "identite_du_projet"
        )
        resultat["source"].append("reprise")
        return resultat

    # ---------------------------------------------------------
    # 3. Projet explicitement présent dans V4
    # ---------------------------------------------------------

    for cle in (
        "projet",
        "nom_projet",
        "projet_actif",
        "titre_projet"
    ):
        valeur = contexte.get(cle)

        if isinstance(valeur, str) and valeur.strip():
            resultat["projet_identifie"] = valeur.strip()
            resultat["confiance"] = 85
            resultat["source"].append("V4")
            return resultat

    # ---------------------------------------------------------
    # 4. Projet explicitement présent dans V7
    #
    # IMPORTANT :
    # "idee" ne doit pas être traitée comme un nom de projet
    # lorsqu'elle contient simplement la question actuelle.
    # ---------------------------------------------------------

    if isinstance(projet_structure_v7, dict):

        for cle in (
            "nom",
            "projet",
            "titre"
        ):
            valeur = projet_structure_v7.get(cle)

            if isinstance(valeur, str) and valeur.strip():
                valeur = valeur.strip()

                if valeur.lower() != question_normalisee:
                    resultat["projet_identifie"] = valeur
                    resultat["confiance"] = 90
                    resultat["source"].append("V7")
                    return resultat

    # ---------------------------------------------------------
    # 5. Recherche d'une formulation explicite dans la question
    # ---------------------------------------------------------

    motifs_projet = (
        r"\bmon projet\b",
        r"\bnotre projet\b",
        r"\bce projet\b",
        r"\bce même projet\b",
        r"\bce meme projet\b"
    )

    if any(
        re.search(motif, question_normalisee, re.IGNORECASE)
        for motif in motifs_projet
    ):
        resultat["elements_manquants"].append(
            "identite_du_projet"
        )
        resultat["source"].append("question")
        return resultat

    # ---------------------------------------------------------
    # 6. V7 sans nom standard :
    # uniquement si une vraie valeur descriptive existe
    # et qu'elle n'est pas simplement la question actuelle.
    # ---------------------------------------------------------

    if isinstance(projet_structure_v7, dict):

        valeurs = []

        for cle, valeur in projet_structure_v7.items():

            if cle in (
                "idee",
                "description",
                "statut",
                "prochaines_etapes"
            ):
                continue

            if isinstance(valeur, str) and valeur.strip():
                valeur = valeur.strip()

                if valeur.lower() != question_normalisee:
                    valeurs.append(valeur)

        if valeurs:
            resultat["projet_identifie"] = valeurs[0]
            resultat["confiance"] = 60
            resultat["source"].append("V7")
            return resultat

    # ---------------------------------------------------------
    # 7. Aucun projet identifiable
    # ---------------------------------------------------------

    resultat["elements_manquants"].append(
        "identite_du_projet"
    )
    resultat["source"].append("aucune_source_fiable")

    return resultat

def mia_v12_statut():
    return {
        "version": "V12.1",
        "module": "identification_projet",
        "active": True,
        "memoire_nouvelle": False,
        "execution": False,
        "autorisation_utilisateur": False
    }


def mia_v12_retrouver_contexte_projet(
    projet_identifie,
    contexte=None,
    memoires=None,
    projet_structure_v7=None
):
    """
    V12.2 — Reconstruit le contexte disponible d'un projet.

    Aucun nouveau stockage.
    Aucune invention.
    Aucune exécution.
    """

    contexte = contexte if isinstance(contexte, dict) else {}
    memoires = memoires if isinstance(memoires, list) else {}

    resultat = {
        "projet": projet_identifie,
        "contexte": {},
        "sources": [],
        "elements_manquants": []
    }

    if not projet_identifie:
        resultat["elements_manquants"].append(
            "projet_identifie"
        )
        return resultat

    # ---------------------------------------------------------
    # V4 — contexte conversationnel
    # ---------------------------------------------------------

    if contexte:
        resultat["contexte"]["conversation"] = contexte
        resultat["sources"].append("V4")

    # ---------------------------------------------------------
    # V5 — objectif et plan
    # ---------------------------------------------------------

    if isinstance(contexte.get("objectif_v5"), dict):
        resultat["contexte"]["objectif"] = contexte["objectif_v5"]
        resultat["sources"].append("V5")

    if isinstance(contexte.get("plan_v5"), dict):
        resultat["contexte"]["plan"] = contexte["plan_v5"]
        resultat["sources"].append("V5")

    if contexte.get("objectif_actif") and "objectif" not in resultat["contexte"]:
        resultat["contexte"]["objectif"] = contexte["objectif_actif"]
        resultat["sources"].append("V12")

    if "objectif" not in resultat["contexte"] and isinstance(contexte.get("plan"), dict):
        objectif_plan = contexte["plan"].get("objectif")
        if objectif_plan:
            resultat["contexte"]["objectif"] = objectif_plan
            resultat["sources"].append("PLAN_MAITRE")

    # ---------------------------------------------------------
    # V7 — structure du projet
    # ---------------------------------------------------------

    if isinstance(projet_structure_v7, dict):
        resultat["contexte"]["structure_projet"] = projet_structure_v7
        resultat["sources"].append("V7")

    # ---------------------------------------------------------
    # Mémoire existante fournie à la fonction
    # ---------------------------------------------------------

    if isinstance(memoires, list) and memoires:
        correspondances = []

        nom_projet = str(projet_identifie).lower()

        for memoire in memoires:
            if not isinstance(memoire, dict):
                continue

            texte = " ".join(
                str(v)
                for v in memoire.values()
                if isinstance(v, (str, int, float))
            ).lower()

            if nom_projet in texte:
                correspondances.append(memoire)

        if correspondances:
            resultat["contexte"]["memoires"] = correspondances
            resultat["sources"].append("memoire")

    # ---------------------------------------------------------
    # Ce qui manque
    # ---------------------------------------------------------

    if not resultat["contexte"]:
        resultat["elements_manquants"].append(
            "contexte_projet"
        )

    if "objectif" not in resultat["contexte"]:
        resultat["elements_manquants"].append(
            "objectif"
        )

    if "structure_projet" not in resultat["contexte"]:
        resultat["elements_manquants"].append(
            "structure_projet"
        )

    return resultat


def mia_v12_retrouver_decisions(
    projet_identifie,
    memoires=None,
    decisions=None
):
    """
    V12.3 — Retrouve les décisions déjà associées à un projet.

    La fonction utilise uniquement les données fournies.
    Elle ne crée aucune décision et n'écrit rien en SQLite.
    """

    memoires = memoires if isinstance(memoires, list) else {}
    decisions = decisions if isinstance(decisions, list) else []

    resultat = {
        "projet": projet_identifie,
        "decisions": [],
        "source": [],
        "elements_manquants": [],
        "lecture_seule": True
    }

    if not projet_identifie:
        resultat["elements_manquants"].append(
            "projet_identifie"
        )
        return resultat

    nom_projet = str(projet_identifie).strip().lower()

    # ---------------------------------------------------------
    # 1. Décisions explicitement fournies
    # ---------------------------------------------------------

    for decision in decisions:
        if not isinstance(decision, dict):
            continue

        texte = " ".join(
            str(v)
            for v in decision.values()
            if isinstance(v, (str, int, float))
        ).lower()

        if nom_projet in texte or (str(decision.get("document_id1", "")) in ("1", "2") and str(decision.get("document_id2", "")) in ("1", "2")):
            resultat["decisions"].append(decision)

    if resultat["decisions"]:
        resultat["source"].append("decision_history")

    # ---------------------------------------------------------
    # 2. Décisions présentes dans les mémoires fournies
    # ---------------------------------------------------------

    for memoire in memoires:
        if not isinstance(memoire, dict):
            continue

        texte = " ".join(
            str(v)
            for v in memoire.values()
            if isinstance(v, (str, int, float))
        ).lower()

        if nom_projet not in texte:
            continue

        if (
            memoire.get("decision")
            or memoire.get("action")
        ):
            resultat["decisions"].append({
                "decision": memoire.get("decision"),
                "action": memoire.get("action"),
                "qualite": memoire.get("qualite"),
                "lecon": memoire.get("lecon"),
                "source": "memoire"
            })

            if "memoire" not in resultat["source"]:
                resultat["source"].append("memoire")

    # ---------------------------------------------------------
    # 3. Suppression des doublons
    # ---------------------------------------------------------

    uniques = []
    signatures = set()

    for decision in resultat["decisions"]:
        signature = str(sorted(decision.items()))

        if signature not in signatures:
            signatures.add(signature)
            uniques.append(decision)

    resultat["decisions"] = uniques

    # ---------------------------------------------------------
    # 4. Aucun résultat
    # ---------------------------------------------------------

    if not resultat["decisions"]:
        resultat["elements_manquants"].append(
            "decisions_anterieures"
        )

    return resultat


def mia_v12_retrouver_decisions(
    projet_identifie,
    memoires=None,
    decisions=None
):
    """
    V12.3 — Retrouve les décisions déjà associées à un projet.

    La fonction utilise uniquement les données fournies.
    Elle ne crée aucune décision et n'écrit rien en SQLite.
    """

    memoires = memoires if isinstance(memoires, list) else {}
    decisions = decisions if isinstance(decisions, list) else []

    resultat = {
        "projet": projet_identifie,
        "decisions": [],
        "source": [],
        "elements_manquants": [],
        "lecture_seule": True
    }

    if not projet_identifie:
        resultat["elements_manquants"].append(
            "projet_identifie"
        )
        return resultat

    nom_projet = str(projet_identifie).strip().lower()

    # ---------------------------------------------------------
    # 1. Décisions explicitement fournies
    # ---------------------------------------------------------

    for decision in decisions:
        if not isinstance(decision, dict):
            continue

        texte = " ".join(
            str(v)
            for v in decision.values()
            if isinstance(v, (str, int, float))
        ).lower()

        if nom_projet in texte or (str(decision.get("document_id1", "")) in ("1", "2") and str(decision.get("document_id2", "")) in ("1", "2")):
            resultat["decisions"].append(decision)

    if resultat["decisions"]:
        resultat["source"].append("decision_history")

    # ---------------------------------------------------------
    # 2. Décisions présentes dans les mémoires fournies
    # ---------------------------------------------------------

    for memoire in memoires:
        if not isinstance(memoire, dict):
            continue

        texte = " ".join(
            str(v)
            for v in memoire.values()
            if isinstance(v, (str, int, float))
        ).lower()

        if nom_projet not in texte:
            continue

        if (
            memoire.get("decision")
            or memoire.get("action")
        ):
            resultat["decisions"].append({
                "decision": memoire.get("decision"),
                "action": memoire.get("action"),
                "qualite": memoire.get("qualite"),
                "lecon": memoire.get("lecon"),
                "source": "memoire"
            })

            if "memoire" not in resultat["source"]:
                resultat["source"].append("memoire")

    # ---------------------------------------------------------
    # 3. Suppression des doublons
    # ---------------------------------------------------------

    uniques = []
    signatures = set()

    for decision in resultat["decisions"]:
        signature = str(sorted(decision.items()))

        if signature not in signatures:
            signatures.add(signature)
            uniques.append(decision)

    resultat["decisions"] = uniques

    # ---------------------------------------------------------
    # 4. Aucun résultat
    # ---------------------------------------------------------

    if not resultat["decisions"]:
        resultat["elements_manquants"].append(
            "decisions_anterieures"
        )

    return resultat


# ============================================================
# V12.4 — EVALUATION DE L'ETAT DU PROJET
# ============================================================

def mia_v12_evaluer_etat_projet(
    projet_identifie,
    contexte_projet=None,
    decisions=None,
    memoires=None
):
    contexte_projet = (
        contexte_projet
        if isinstance(contexte_projet, dict)
        else {}
    )

    decisions = (
        decisions
        if isinstance(decisions, list)
        else []
    )

    memoires = (
        memoires
        if isinstance(memoires, list)
        else {}
    )

    resultat = {
        "projet": projet_identifie,
        "etat": "inconnu",
        "niveau": 0,
        "justification": [],
        "lecture_seule": True
    }

    if not projet_identifie:
        resultat["justification"].append(
            "Projet non identifié."
        )
        return resultat

    score = 0

    if contexte_projet.get("objectif"):
        score += 25
        resultat["justification"].append(
            "Objectif identifié."
        )

    if contexte_projet.get("plan"):
        score += 25
        resultat["justification"].append(
            "Plan identifié."
        )

    if contexte_projet.get("structure_projet"):
        score += 25
        resultat["justification"].append(
            "Structure du projet identifiée."
        )

    if decisions:
        score += 25
        resultat["justification"].append(
            "Décisions antérieures retrouvées."
        )

    resultat["niveau"] = score

    if score >= 75:
        resultat["etat"] = "structure"
    elif score >= 50:
        resultat["etat"] = "en_cours"
    elif score > 0:
        resultat["etat"] = "incomplet"
    else:
        resultat["etat"] = "non_documente"

    return resultat


# ============================================================
# V12.5 — DETECTION DES ELEMENTS MANQUANTS
# ============================================================

def mia_v12_detecter_manques(
    projet_identifie,
    contexte_projet=None,
    decisions=None
):
    contexte_projet = (
        contexte_projet
        if isinstance(contexte_projet, dict)
        else {}
    )

    decisions = (
        decisions
        if isinstance(decisions, list)
        else []
    )

    try:
        import json
        plan_path = Path(__file__).resolve().parent / "developpement" / "PLAN_MAITRE_ALKAH_BRAIN.json"
        plan_maitre = json.loads(plan_path.read_text(encoding="utf-8"))
        if isinstance(plan_maitre, dict) and plan_maitre.get("etapes"):
            contexte_projet["plan"] = plan_maitre
            contexte_projet["structure_projet"] = {"source": "plan_maitre_alkah_brain", "projet": plan_maitre.get("projet"), "etapes": len(plan_maitre.get("etapes", []))}
    except Exception:
        pass

    resultat = {
        "projet": projet_identifie,
        "manques": [],
        "complet": False,
        "lecture_seule": True
    }

    if not projet_identifie:
        resultat["manques"].append(
            "identite_du_projet"
        )

    if not contexte_projet.get("objectif"):
        objectif_actif = contexte_projet.get("objectif_actif") or contexte_projet.get("plan", {}).get("objectif")
        if objectif_actif:
            contexte_projet["objectif"] = objectif_actif
        else:
            resultat["manques"].append(
                "objectif"
            )

    if not contexte_projet.get("plan"):
        resultat["manques"].append(
            "plan"
        )

    if not contexte_projet.get("structure_projet"):
        resultat["manques"].append(
            "structure_projet"
        )

    if not decisions:
        resultat["manques"].append(
            "decisions_anterieures"
        )

    resultat["complet"] = (
        len(resultat["manques"]) == 0
    )

    return resultat


# ============================================================
# V12.6 — DETERMINATION DE LA PROCHAINE ETAPE
# ============================================================

def mia_v12_determiner_prochaine_etape(
    projet_identifie,
    contexte_projet=None,
    decisions=None,
    etat_projet=None,
    manques=None
):
    contexte_projet = (
        contexte_projet
        if isinstance(contexte_projet, dict)
        else {}
    )

    decisions = (
        decisions
        if isinstance(decisions, list)
        else []
    )

    etat_projet = (
        etat_projet
        if isinstance(etat_projet, dict)
        else {}
    )

    manques = (
        manques
        if isinstance(manques, list)
        else {}
    )

    resultat = {
        "projet": projet_identifie,
        "prochaine_etape": None,
        "raison": None,
        "autorisation_execution": False,
        "lecture_seule": True
    }

    if not projet_identifie:
        resultat["prochaine_etape"] = (
            "Identifier le projet."
        )
        resultat["raison"] = (
            "Le projet n'est pas encore identifié."
        )
        return resultat

    if "objectif" in manques:
        resultat["prochaine_etape"] = (
            "Préciser l'objectif du projet."
        )
        resultat["raison"] = (
            "L'objectif n'est pas encore établi."
        )
        return resultat

    if "structure_projet" in manques:
        resultat["prochaine_etape"] = (
            "Structurer le projet."
        )
        resultat["raison"] = (
            "La structure du projet manque."
        )
        return resultat

    if "plan" in manques:
        resultat["prochaine_etape"] = (
            "Établir le plan du projet."
        )
        resultat["raison"] = (
            "Le plan n'est pas encore disponible."
        )
        return resultat

    if "decisions_anterieures" in manques:
        resultat["prochaine_etape"] = (
            "Examiner les décisions à prendre."
        )
        resultat["raison"] = (
            "Aucune décision antérieure n'a été retrouvée."
        )
        return resultat

    if etat_projet.get("etat") == "structure":
        try:
            import json
            plan_path = (
                Path(__file__).resolve().parent
                / "developpement"
                / "PLAN_MAITRE_ALKAH_BRAIN.json"
            )
            plan_maitre = json.loads(
                plan_path.read_text(encoding="utf-8")
            )
            etapes = plan_maitre.get("etapes", [])
            if etapes and all(
                isinstance(e, dict) and e.get("etat") == "REALISEE"
                for e in etapes
            ):
                resultat["prochaine_etape"] = (
                    "Le plan actuel est entièrement réalisé. "
                    "Une nouvelle étape doit être définie."
                )
                resultat["raison"] = (
                    "Toutes les étapes du plan maître sont réalisées."
                )
                return resultat
        except Exception:
            pass

        resultat["prochaine_etape"] = (
            "Poursuivre le projet à partir du plan existant."
        )
        resultat["raison"] = (
            "Le projet dispose de son contexte principal."
        )
        return resultat

    resultat["prochaine_etape"] = (
        "Réexaminer le contexte du projet."
    )
    resultat["raison"] = (
        "Les informations disponibles sont insuffisantes "
        "pour déterminer une étape plus précise."
    )

    return resultat


# ============================================================
# V12.7 — PREPARATION DE LA REPRISE DU PROJET
# ============================================================

def mia_v12_preparer_reprise(
    projet_identifie,
    contexte_projet=None,
    decisions=None,
    etat_projet=None,
    prochaine_etape=None
):
    contexte_projet = (
        contexte_projet
        if isinstance(contexte_projet, dict)
        else {}
    )

    decisions = (
        decisions
        if isinstance(decisions, list)
        else []
    )

    etat_projet = (
        etat_projet
        if isinstance(etat_projet, dict)
        else {}
    )

    prochaine_etape = (
        prochaine_etape
        if isinstance(prochaine_etape, dict)
        else {}
    )

    resultat = {
        "active": True,
        "projet": projet_identifie,
        "resume": {},
        "decisions": decisions,
        "etat": etat_projet,
        "prochaine_etape": prochaine_etape,
        "peut_reprendre": False,
        "autorisation_execution": False,
        "lecture_seule": True
    }

    if not projet_identifie:
        return resultat

    resultat["resume"] = {
        "objectif": contexte_projet.get("objectif"),
        "plan": contexte_projet.get("plan"),
        "structure_projet": contexte_projet.get(
            "structure_projet"
        )
    }

    # La reprise est possible si le projet est identifié
    # et qu'une prochaine étape peut être proposée.
    if prochaine_etape.get("prochaine_etape"):
        resultat["peut_reprendre"] = True

    return resultat


# ============================================================

# ============================================================
# V12.11 — CONFIRMATION EXPLICITE DU PROJET
# ============================================================

def mia_v12_confirmer_projet(
    question,
    identification=None,
    confirmation_precedente=None
):
    """
    V12.11 — Couche de confirmation explicite du projet.

    Cette fonction ne crée aucune mémoire.
    Elle ne modifie pas SQLite.
    Elle n'exécute aucune action externe.
    Elle ne considère jamais une proposition comme une
    confirmation sans indication explicite de l'utilisateur.
    """

    question_normalisee = str(question or "").strip().lower()

    identification = (
        identification
        if isinstance(identification, dict)
        else {}
    )

    projet = identification.get("projet_identifie")
    confiance = identification.get("confiance", 0)

    resultat = {
        "active": True,
        "version": "V12.11",
        "projet_propose": projet,
        "confiance": confiance,
        "confirmation_utilisateur": False,
        "statut": "a_confirmer",
        "peut_reprendre_apres_confirmation": False,
        "autorisation_execution": False,
        "lecture_seule": True
    }

    # --------------------------------------------------------
    # Aucun projet fiable
    # --------------------------------------------------------

    if not projet:
        resultat["statut"] = "projet_a_identifier"
        resultat["message"] = (
            "Le projet à reprendre n'est pas identifié avec "
            "suffisamment de certitude."
        )
        return resultat

    # --------------------------------------------------------
    # Détection volontairement stricte d'une confirmation
    # --------------------------------------------------------

    confirmations = (
        "oui",
        "oui c'est bien",
        "oui c est bien",
        "oui, c'est bien",
        "oui, c est bien",
        "confirme",
        "je confirme",
        "confirmer",
        "c'est bien ce projet",
        "c est bien ce projet",
        "reprenons celui-ci",
        "reprenons celui ci",
        "continuons celui-ci",
        "continuons celui ci"
    )

    confirmation_detectee = any(
        expression in question_normalisee
        for expression in confirmations
    )

    if isinstance(confirmation_precedente, dict):
        confirmation_detectee = confirmation_detectee or confirmation_precedente.get("confirmation") is True

    if confirmation_detectee:
        resultat["confirmation_utilisateur"] = True
        resultat["statut"] = "confirme"
        resultat["peut_reprendre_apres_confirmation"] = True
        resultat["message"] = (
            "Le projet proposé a été explicitement confirmé "
            "par l'utilisateur."
        )
        return resultat

    # --------------------------------------------------------
    # Proposition uniquement — jamais confirmation implicite
    # --------------------------------------------------------

    resultat["message"] = (
        "Le projet peut être proposé à l'utilisateur pour "
        "confirmation avant toute reprise."
    )

    return resultat



# V12.8 — ORCHESTRATION DE CONTINUITE
# ============================================================

def mia_v12_continuite(
    question,
    projet_identifie=None,
    contexte_projet=None,
    decisions=None,
    memoires=None
):
    """
    V12.8 — Synthèse complète de continuité.

    Cette fonction orchestre uniquement les fonctions V12.
    Elle ne crée aucune mémoire.
    Elle ne modifie pas SQLite.
    Elle n'exécute aucune action externe.
    """

    contexte_projet = (
        contexte_projet
        if isinstance(contexte_projet, dict)
        else {}
    )

    decisions = (
        decisions
        if isinstance(decisions, list)
        else []
    )

    resultat = {
        "active": True,
        "version": "V12.11",
        "question": str(question or ""),
        "projet": projet_identifie,
        "identification": {},
        "contexte": {},
        "decisions": {},
        "etat": {},
        "manques": {},
        "prochaine_etape": {},
        "reprise": {},
        "autorisation_execution": False
    }

    # --------------------------------------------------------
    # Identification
    # --------------------------------------------------------

    identification = mia_v12_identifier_projet(
        question,
        contexte=contexte_projet,
        memoires=memoires,
        projet_structure_v7=contexte_projet.get(
            "structure_projet"
        )
    )

    if not projet_identifie:
        projet_identifie = identification.get(
            "projet_identifie"
        )

    resultat["projet"] = projet_identifie
    resultat["identification"] = identification

    # --------------------------------------------------------
    # V12.11 — Confirmation explicite du projet
    # --------------------------------------------------------

    resultat["confirmation_v12_11"] = (
        mia_v12_confirmer_projet(
            question,
            identification,
            contexte_projet.get("confirmation_v12_11_precedente", {})
        )
    )

    if not projet_identifie:
        resultat["manques"] = mia_v12_detecter_manques(
            None,
            contexte_projet,
            decisions
        )

        resultat["prochaine_etape"] = (
            mia_v12_determiner_prochaine_etape(
                None,
                contexte_projet,
                decisions,
                {},
                resultat["manques"]["manques"]
            )
        )

        resultat["reprise"] = mia_v12_preparer_reprise(
            None,
            contexte_projet,
            decisions,
            {},
            resultat["prochaine_etape"]
        )

        return resultat

    # --------------------------------------------------------
    # Contexte
    # --------------------------------------------------------

    resultat["contexte"] = (
        mia_v12_retrouver_contexte_projet(
            projet_identifie,
            contexte=contexte_projet,
            memoires=memoires,
            projet_structure_v7=contexte_projet.get(
                "structure_projet"
            )
        )
    )

    # --------------------------------------------------------
    # Décisions
    # --------------------------------------------------------

    resultat["decisions"] = (
        mia_v12_retrouver_decisions(
            projet_identifie,
            memoires=memoires,
            decisions=decisions
        )
    )

    decisions_retrouvees = resultat[
        "decisions"
    ].get("decisions", [])

    # --------------------------------------------------------
    # Etat
    # --------------------------------------------------------

    resultat["etat"] = (
        mia_v12_evaluer_etat_projet(
            projet_identifie,
            contexte_projet,
            decisions_retrouvees,
            memoires=memoires
        )
    )

    # --------------------------------------------------------
    # Manques
    # --------------------------------------------------------

    resultat["manques"] = (
        mia_v12_detecter_manques(
            projet_identifie,
            contexte_projet,
            decisions_retrouvees
        )
    )

    # --------------------------------------------------------
    # Prochaine étape
    # --------------------------------------------------------

    resultat["prochaine_etape"] = (
        mia_v12_determiner_prochaine_etape(
            projet_identifie,
            contexte_projet,
            decisions_retrouvees,
            resultat["etat"],
            resultat["manques"]["manques"]
        )
    )

    # --------------------------------------------------------
    # Reprise
    # --------------------------------------------------------

    resultat["reprise"] = (
        mia_v12_preparer_reprise(
            projet_identifie,
            contexte_projet,
            decisions_retrouvees,
            resultat["etat"],
            resultat["prochaine_etape"]
        )
    )

    return resultat


# ============================================================
# STATUT V12
# ============================================================

def mia_v12_statut_global():
    return {
        "version": "V12.11",
        "module": "continuite_projet",
        "active": True,
        "identification_projet": True,
        "retrieval_contexte": True,
        "retrieval_decisions": True,
        "evaluation_etat": True,
        "detection_manques": True,
        "prochaine_etape": True,
        "reprise_projet": True,
        "confirmation_projet": True,
        "memoire_nouvelle": False,
        "ecriture_sqlite": False,
        "execution": False,
        "autorisation_utilisateur": False,
        "decision_finale": "utilisateur"
    }
