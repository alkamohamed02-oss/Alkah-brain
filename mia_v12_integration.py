import re
from mia_v12_cycle_decision import mia15_cycle_decisionnel
"""
ALKAH-BRAIN / MIA
V12.12 — Couche d'intégration dialogue.

Cette couche utilise les fonctions V12.12 existantes
sans modifier le coeur B34/V12.11.
"""

from mia_v12_dialogue import (
    mia12_preparer_tour,
    mia12_enregistrer_tour,
    mia12_charger_etat,
)

from mia_v12_decision import (
    mia13_analyser_continuite,
)

from mia_v12_decision_reelle import mia133_continuite_decisionnelle
from mia_v12_continuite import mia_v12_continuite

import sys
from pathlib import Path as _Path

_V1221_SOCLE = _Path(__file__).resolve().parent / "developpement" / "V12.21.0" / "socle"
if str(_V1221_SOCLE) not in sys.path:
    sys.path.insert(0, str(_V1221_SOCLE))

from mia_v12_orchestrateur_memoire import mia_v12_traiter_demande_memoire
from mia_v12_rapprochement_memoire import mia_v12_rapprocher_memoires
from mia_v12_decision_persistante import mia14_continuite_decisionnelle_persistante


def mia12_interroger_moteur(
    question,
    moteur_reponse,
    session_id="session_principale",
    moteur_memoire=None,
    memoire_ecriture=False,
    intention_conversationnelle=None,
):
    preparation = mia12_preparer_tour(
        question,
        session_id=session_id
    )

    question_resolue = preparation["question_resolue"]
    contexte = preparation["contexte"]

    # V12.21 — détection/orchestration mémoire.
    # L'écriture reste interdite par défaut.
    orchestration_memoire = mia_v12_traiter_demande_memoire(
        question
    )

    ecriture_effectuee = False
    resultat_ecriture = {
        "sauvegardee": False,
        "raison": "ecriture_non_autorisee"
    }

    # V12.21 — écriture explicitement autorisée uniquement par l'appelant.
    if (
        memoire_ecriture is True
        and moteur_memoire is not None
        and isinstance(orchestration_memoire, dict)
        and orchestration_memoire.get("a_enregistrer") is True
    ):
        memoire_candidate = orchestration_memoire.get("memoire")

        if isinstance(memoire_candidate, dict):
            sauvegarder = getattr(
                moteur_memoire,
                "mia_sauvegarder_memoire_apprentissage",
                None
            )

            if callable(sauvegarder):
                resultat_ecriture = sauvegarder(
                    memoire_candidate
                )
                ecriture_effectuee = bool(
                    isinstance(resultat_ecriture, dict)
                    and resultat_ecriture.get("sauvegardee") is True
                )
            else:
                resultat_ecriture = {
                    "sauvegardee": False,
                    "raison": "fonction_sauvegarde_indisponible"
                }

    # V12.21 — rapprochement intelligent des mémoires.
    # Lecture seule : aucune écriture mémoire ici.
    rapprochement_memoire = {
        "active": False,
        "resultats": [],
        "selection": None
    }

    if moteur_memoire is not None:
        chargeur_memoires = getattr(
            moteur_memoire,
            "mia_charger_memoires_apprentissage_sqlite",
            None
        )

        if callable(chargeur_memoires):
            memoires_existantes = chargeur_memoires()

            if isinstance(memoires_existantes, list):
                analyses_memoire = mia_v12_rapprocher_memoires(
                    question,
                    memoires_existantes
                )

                rapprochement_memoire = {
                    "active": True,
                    "resultats": analyses_memoire,
                    "selection": (
                        analyses_memoire.get("meilleure")
                        if isinstance(analyses_memoire, dict)
                        else None
                    )
                }

    etat_precedent = preparation.get(
        "etat_precedent",
        {}
    )

    # V12.11 — continuité réelle du projet, lecture seule.
    # Charge le plan maître avant l'orchestration V12.
    try:
        import json
        fichier_plan = _Path(__file__).resolve().parent / "developpement" / "PLAN_MAITRE_ALKAH_BRAIN.json"
        with fichier_plan.open("r", encoding="utf-8") as f:
            plan_v12 = json.load(f)
        if isinstance(plan_v12, dict) and plan_v12.get("etapes"):
            contexte["plan"] = plan_v12
            contexte["structure_projet"] = {
                "source": "plan_maitre_alkah_brain",
                "projet": plan_v12.get("projet"),
                "etapes": len(plan_v12.get("etapes", []))
            }
    except Exception:
        pass

    decisions_v12 = []
    if moteur_memoire is not None:
        chargeur_decisions = getattr(moteur_memoire, "consulter_decisions", None)
        if callable(chargeur_decisions):
            try:
                lignes_decisions = chargeur_decisions()
                for ligne in lignes_decisions or []:
                    if isinstance(ligne, (list, tuple)) and len(ligne) >= 10:
                        decisions_v12.append({
                            "id": ligne[0],
                            "document_id1": ligne[1],
                            "document_id2": ligne[2],
                            "score_global": ligne[3],
                            "confiance": ligne[4],
                            "signaux": ligne[5],
                            "raisons": ligne[6],
                            "decision": ligne[7],
                            "action": ligne[8],
                            "created_at": ligne[9]
                        })
            except Exception:
                decisions_v12 = []

    continuite_v12 = mia_v12_continuite(
        question=question,
        projet_identifie=contexte.get("projet_actif"),
        contexte_projet={**contexte, "confirmation_v12_11_precedente": preparation.get("confirmation", {})},
        decisions=decisions_v12
    )

    decision_v12_13 = mia13_analyser_continuite(
        question,
        etat=etat_precedent,
        contexte=contexte
    )

    decision_v12_13_3 = mia133_continuite_decisionnelle(
        question,
        etat=etat_precedent,
        contexte=contexte,
        continuite_v12=continuite_v12
    )

    # V12.12 — réponse directe depuis la mémoire conversationnelle.
    # Les informations déjà mémorisées ne doivent pas être envoyées
    # au moteur documentaire comme une connaissance externe.
    referents = contexte.get("referents", {}) if isinstance(contexte, dict) else {}

    nom_utilisateur = referents.get("nom_utilisateur") if isinstance(referents, dict) else None

    # V12.21 — pont sécurisé vers V76.
    # Une correspondance exacte et parfaite est transmise comme
    # contexte complémentaire, sans modifier V76 ni la mémoire originale.
    question_moteur = question_resolue

    if isinstance(rapprochement_memoire, dict):
        analyses = rapprochement_memoire.get("resultats", {})
        meilleure = (
            analyses.get("meilleure")
            if isinstance(analyses, dict)
            else None
        )

        if isinstance(meilleure, dict):
            score = meilleure.get("score", 0)
            decision_memoire = meilleure.get("decision", "")

            if (
                score >= 60
                and decision_memoire in ("correspondance_identifiant_exact", "correspondance_lexicale_forte")
            ):
                question_memorisee = meilleure.get(
                    "memoire_question",
                    ""
                )
                lecon_memorisee = meilleure.get(
                    "memoire_lecon",
                    ""
                )

                contexte_memoire_v1221 = (
                    "\n\n"
                    "Contexte mémoire complémentaire validé par V12.21 :\n"
                    "Question mémorisée : "
                    + str(question_memorisee)
                    + "\nLeçon mémorisée : "
                    + str(lecon_memorisee)
                    + "\nCorrespondance validée : " + str(score) + "/100\n"
                    "Décision : " + str(decision_memoire) + "\n"
                    "Source : mémoire expérientielle ALKAH-BRAIN\n"
                    "Utiliser uniquement comme contexte complémentaire."
                )

                question_moteur = (
                    question_resolue
                    + contexte_memoire_v1221
                )

    objectif_actif = (
        contexte.get("objectif_actif")
        if isinstance(contexte, dict)
        else None
    )

    if not objectif_actif and isinstance(contexte, dict):
        plan = contexte.get("plan", {})
        if isinstance(plan, dict):
            objectif_actif = plan.get("objectif")

    demande_rappel_objectif = bool(
        re.search(
            r"\bobjectif\b.*\b("
            r"viens de vous donner|"
            r"viens de donner|"
            r"que je viens de vous donner|"
            r"que je vous ai donné|"
            r"que je vous ai donne"
            r")\b",
            question.strip().lower()
        )
        or re.search(
            r"\bquel est (?:mon|notre)\s+objectif\b|\bquel est l[’']objectif\b",
            question.strip().lower()
        )
    )

    demande_etat_projet = bool(
        re.search(r"où en est|ou en est|avancement|progression|état du projet|etat du projet|quel est le projet actuel|quel est notre projet actuel|quel est mon projet actuel|quel est mon projet|quel est notre projet", question.strip().lower())
    )

    demande_nom_projet = bool(re.search(r"quel est (?:le|notre|mon) nom (?:du|de) projet|nom (?:du|de) projet", question.strip().lower()))

    demande_connaissance_projet = bool(
        re.search(
            r"\b(que sais-tu|que savez-vous|parle-moi|parlez-moi|peux-tu me parler|présente|presente|décris|decris).*(projet\s+ALKAH[- ]BRAIN|ALKAH[- ]BRAIN|mon projet|notre projet)\b",
            question.strip().lower()
        )
        or re.search(
            r"\b(ALKAH[- ]BRAIN).*(c'est quoi|qu'est-ce que|quel est|présente|presente|décris|decris|connais|sais)",
            question.strip().lower()
        )
    )

    if demande_rappel_objectif and objectif_actif:
        resultat = {
            "reponse": (
                "L’objectif que vous venez de me donner est : "
                + str(objectif_actif).rstrip(".")
                + "."
            ),
            "intention": "memoire_conversationnelle",
            "source": "memoire_conversationnelle_v12_12"
        }

    elif nom_utilisateur and question.strip().lower().rstrip(" .!?;:") in (
        "comment je m'appelle",
        "comment je m’appelle",
        "quel est mon nom",
        "quelle est mon nom",
    ):
        resultat = {
            "reponse": f"Vous vous appelez {nom_utilisateur}.",
            "intention": "memoire_conversationnelle",
            "source": "memoire_conversationnelle_v12_12"
        }
    elif demande_nom_projet:
        plan_projet = contexte.get("plan", {}) if isinstance(contexte, dict) else {}
        nom_projet = plan_projet.get("projet") or "ALKAH-BRAIN"
        resultat = {
            "reponse": "Le nom du projet est : " + str(nom_projet) + ".",
            "intention": "nom_projet",
            "source": "plan_maitre_alkah_brain"
        }

    elif demande_connaissance_projet:
        plan_projet = contexte.get("plan", {}) if isinstance(contexte, dict) else {}
        objectif_plan = plan_projet.get("objectif") or objectif_actif
        total_etapes = len(plan_projet.get("etapes", []))
        resultat = {
            "reponse": "ALKAH-BRAIN est votre projet de cerveau numérique local. " + (("Son objectif est : " + str(objectif_plan).rstrip(".") + ". ") if objectif_plan else "") + (("Le plan maître comprend " + str(total_etapes) + " étapes.") if total_etapes else ""),
            "intention": "connaissance_projet",
            "source": "plan_maitre_alkah_brain"
        }
    elif demande_etat_projet and objectif_actif:
        plan_projet = {}
        fichier_plan = _Path(__file__).resolve().parent / "developpement" / "PLAN_MAITRE_ALKAH_BRAIN.json"
        try:
            import json
            with fichier_plan.open("r", encoding="utf-8") as f:
                plan_projet = json.load(f)
        except Exception:
            plan_projet = {}

        etapes = plan_projet.get("etapes", [])
        total = len(etapes)
        realisees = sum(1 for e in etapes if e.get("etat") == "REALISEE")
        en_cours = sum(1 for e in etapes if e.get("etat") == "EN_COURS")
        a_faire = sum(1 for e in etapes if e.get("etat") == "A_FAIRE")
        bloquees = sum(1 for e in etapes if e.get("etat") == "BLOQUEE")
        progression = round((realisees / total) * 100, 2) if total else None
        etape_en_cours = next((e for e in etapes if e.get("etat") == "EN_COURS"), None)
        prochaines = [e for e in etapes if e.get("etat") == "A_FAIRE"]

        resume = (
            "L’objectif actuel est : " + str(plan_projet.get("objectif", objectif_actif)).rstrip(".") +
            ". Progression du plan : " + (str(progression) + " %" if progression is not None else "non calculable") +
            " (" + str(realisees) + "/" + str(total) + " étapes REALISEE)."
        )
        if etape_en_cours:
            resume += " Étape en cours : " + str(etape_en_cours.get("id")) + " — " + str(etape_en_cours.get("description"))
        if prochaines:
            resume += " Prochaine étape à faire : " + str(prochaines[0].get("id")) + " — " + str(prochaines[0].get("description"))

        resultat = {
            "reponse": resume,
            "intention": "progression_projet",
            "source": "plan_maitre_alkah_brain"
        }

    elif intention_conversationnelle == "prochaine_etape":
        prochaine_v12 = continuite_v12.get("prochaine_etape", {}) if isinstance(continuite_v12, dict) else {}
        texte_v12 = prochaine_v12.get("prochaine_etape") if isinstance(prochaine_v12, dict) else None

        if texte_v12:
            resultat = {
                "reponse": str(texte_v12),
                "intention": "prochaine_etape",
                "source": "continuite_v12"
            }
        else:
            plan_projet = {}
            fichier_plan = _Path(__file__).resolve().parent / "developpement" / "PLAN_MAITRE_ALKAH_BRAIN.json"
            try:
                import json
                with fichier_plan.open("r", encoding="utf-8") as f:
                    plan_projet = json.load(f)
            except Exception:
                plan_projet = {}

            etapes = plan_projet.get("etapes", [])
            en_cours = [e for e in etapes if e.get("etat") == "EN_COURS"]
            a_faire = [e for e in etapes if e.get("etat") == "A_FAIRE"]

            if en_cours:
                e = en_cours[0]
                reponse = "Étape en cours : " + str(e.get("description", e.get("id", ""))) + "."
            elif a_faire:
                e = a_faire[0]
                reponse = "Prochaine étape : " + str(e.get("description", e.get("id", ""))) + "."
            elif etapes and all(e.get("etat") == "REALISEE" for e in etapes):
                reponse = "Le plan maître du projet ALKAH-BRAIN est entièrement réalisé : 10 étapes sur 10."
            else:
                reponse = "Le plan maître ne définit pas encore de prochaine étape."

            resultat = {
                "reponse": reponse,
                "intention": "prochaine_etape",
                "source": "plan_maitre_alkah_brain"
            }

    else:
        selection_memoire = (
            rapprochement_memoire.get("selection")
            if isinstance(rapprochement_memoire, dict)
            else None
        )

        if (
            isinstance(selection_memoire, dict)
            and selection_memoire.get("score", 0) >= 60
            and selection_memoire.get("decision", "") in ("correspondance_identifiant_exact", "correspondance_lexicale_forte")
            and selection_memoire.get("memoire_lecon")
        ):
            resultat = {
                "reponse": str(selection_memoire.get("memoire_lecon")),
                "intention": "rappel_memoire_experientielle",
                "source": "memoire_experientielle_alkah_brain",
                "memoire_id": selection_memoire.get("memoire_id"),
                "correspondance": selection_memoire.get("decision"),
                "score_memoire": selection_memoire.get("score")
            }
        else:
            resultat = moteur_reponse(question_moteur)

    if isinstance(resultat, dict):
        reponse = resultat.get("reponse", "")
        if not isinstance(reponse, str):
            reponse = str(reponse)

        intention = resultat.get("intention")

    else:
        reponse = str(resultat)
        intention = None

    resultat_enregistrement = mia12_enregistrer_tour(
        session_id=session_id,
        question=question,
        question_resolue=question_resolue,
        intention=intention,
        contexte=contexte,
        reponse=reponse
    )

    if isinstance(resultat_enregistrement, dict):
        numero_tour = resultat_enregistrement.get(
            "numero_tour",
            0
        )
    else:
        numero_tour = resultat_enregistrement

    decision_v12_14 = mia14_continuite_decisionnelle_persistante(
        question,
        etat_decision={
            "derniere_decision": decision_v12_13_3,
            "projet_actif": contexte.get("projet_actif") if isinstance(contexte, dict) else None,
            "objectif_actif": contexte.get("objectif_actif") if isinstance(contexte, dict) else None,
            "sujet_actif": contexte.get("sujet_actif") if isinstance(contexte, dict) else None
        }
    )

    decision_v12_15 = mia15_cycle_decisionnel(
        question,
        etat={
            "derniere_decision": decision_v12_13_3,
            "objectif_actif": contexte.get("objectif_actif") if isinstance(contexte, dict) else None
        }
    )

    return {
        "session_id": session_id,
        "numero_tour": numero_tour,
        "question": question,
        "question_resolue": question_resolue,
        "contexte": contexte,
        "confirmation": preparation.get(
            "confirmation",
            {
                "confirmation": False,
                "type": None,
                "confiance": 0,
                "raison": "aucune_confirmation_detectee"
            }
        ),
        "memoire_v12_21": {
            "orchestration": orchestration_memoire,
            "rapprochement": rapprochement_memoire,
            "ecriture_autorisee": bool(memoire_ecriture is True),
            "ecriture_effectuee": ecriture_effectuee,
            "resultat_ecriture": resultat_ecriture
        },
        "reponse": reponse,
        "decision_v12_13": decision_v12_13,
        "decision_v12_13_3": decision_v12_13_3,
        "decision_v12_14": decision_v12_14,
        "decision_v12_15": decision_v12_15,
        "resultat_moteur": resultat
    }


def mia12_etat(session_id="session_principale"):
    return mia12_charger_etat(session_id)
