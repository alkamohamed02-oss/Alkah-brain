# -*- coding: utf-8 -*-

"""
MIA V12.12 — CONTINUITE CONVERSATIONNELLE REELLE

Couche indépendante de la continuité de projet V12.11.

Responsabilités :
- session persistante
- historique des tours
- sujet actif
- projet actif
- objectif actif
- dernière intention
- dernière question
- dernière réponse
- résolution de référents conversationnels
- persistance SQLite

Ne remplace pas :
- mémoire documentaire
- mémoire d'apprentissage
- mémoire décisionnelle MIA25
- continuité de projet V12.11
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path


DB_PATH = "database/alkah_brain.db"


def _connexion():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def mia12_initialiser_sqlite():
    conn = _connexion()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_state (
            session_id TEXT PRIMARY KEY,
            numero_tour INTEGER NOT NULL DEFAULT 0,
            sujet_actif TEXT,
            projet_actif TEXT,
            objectif_actif TEXT,
            derniere_intention TEXT,
            derniere_question TEXT,
            derniere_reponse TEXT,
            referents TEXT,
            updated_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation_turns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            numero_tour INTEGER NOT NULL,
            question TEXT NOT NULL,
            question_resolue TEXT,
            intention TEXT,
            sujet_actif TEXT,
            projet_actif TEXT,
            objectif_actif TEXT,
            reponse TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def mia12_charger_etat(session_id="session_principale"):
    mia12_initialiser_sqlite()

    conn = _connexion()

    row = conn.execute(
        """
        SELECT *
        FROM conversation_state
        WHERE session_id = ?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    if not row:
        return {
            "session_id": session_id,
            "numero_tour": 0,
            "sujet_actif": None,
            "projet_actif": None,
            "objectif_actif": None,
            "derniere_intention": None,
            "derniere_question": None,
            "derniere_reponse": None,
            "referents": {}
        }

    try:
        referents = json.loads(row["referents"] or "{}")
    except Exception:
        referents = {}

    return {
        "session_id": row["session_id"],
        "numero_tour": row["numero_tour"],
        "sujet_actif": row["sujet_actif"],
        "projet_actif": row["projet_actif"],
        "objectif_actif": row["objectif_actif"],
        "derniere_intention": row["derniere_intention"],
        "derniere_question": row["derniere_question"],
        "derniere_reponse": row["derniere_reponse"],
        "referents": referents
    }


def mia12_extraire_contexte(question, etat=None):
    """
    Extrait le contexte actif V12.12.

    Une confirmation ou une demande de continuation courte
    ne remplace jamais le sujet actif précédent.
    """

    etat = etat or {}

    texte = str(question or "").strip()
    bas = texte.lower()

    projet = etat.get("projet_actif")
    objectif = etat.get("objectif_actif")
    sujet = etat.get("sujet_actif")

    # Projet explicite.
    if "alkah-brain v12.12" in bas:
        projet = "ALKAH-BRAIN V12.12"
    elif "alkah-brain" in bas:
        projet = "ALKAH-BRAIN"

    # Objectif explicite.
    match_objectif = re.search(
        r"\b(?:notre|mon|l')?\s*objectif(?:\s+actif)?\s+(?:est|sera|consiste\s+à)\s+(?:de\s+)?(.+?)(?:[.!?;:]|$)",
        texte,
        re.IGNORECASE
    )

    if match_objectif:
        objectif_extrait = match_objectif.group(1).strip()
        if objectif_extrait:
            objectif = objectif_extrait

    # Formulation naturelle d'objectif liée au projet.
    if not match_objectif and re.search(
        r"\b(développer|developper|construire|créer|creer|concevoir|faire)\b.*\balkah-brain\b",
        bas,
        re.IGNORECASE
    ):
        objectif = texte.rstrip(" .!?;:")

    mots_objectif = (
        "continuité conversationnelle",
        "continuite conversationnelle",
        "continuité multi-tour",
        "continuite multi-tour",
        "confirmation",
        "reprise de projet",
        "mémoire conversationnelle",
        "memoire conversationnelle",
    )

    for mot in mots_objectif:
        if mot in bas:
            objectif = mot
            break

    # Confirmation : ne doit jamais devenir le sujet.
    confirmations = {
        "je confirme",
        "je valide",
        "confirme",
        "confirmer",
        "validation confirmée",
        "validation confirmee",
        "oui",
        "d'accord",
        "daccord",
    }

    normalise = bas.rstrip(" .!?;:")

    est_confirmation = (
        normalise in confirmations
        or normalise.startswith("je confirme ")
        or normalise.startswith("je valide ")
    )

    # Continuation/référent : ne doit pas devenir le sujet.
    expressions_continuation = (
        "fais la suite",
        "faire la suite",
        "la suite",
        "continue",
        "continuons",
        "poursuis",
        "reprends",
        "reprendre",
        "ce projet",
        "ce travail",
        "cela",
        "ça",
        "ce point",
        "cet objectif",
    )

    est_continuation = any(
        expression in normalise
        for expression in expressions_continuation
    )

    # Seul un nouveau contenu substantiel remplace le sujet.
    if texte and not est_confirmation and not est_continuation:
        sujet = texte[:300]

    # Premier tour : le premier contenu devient le sujet.
    if not sujet and texte and not est_confirmation and not est_continuation:
        sujet = texte[:300]

    return {
        "sujet_actif": sujet,
        "projet_actif": projet,
        "objectif_actif": objectif,
    }



def mia12_resoudre_referents(question, etat):
    texte = question.strip()
    bas = texte.lower()

    projet = etat.get("projet_actif")
    objectif = etat.get("objectif_actif")
    sujet = etat.get("sujet_actif")

    referents_precedents = etat.get("referents", {})
    if not isinstance(referents_precedents, dict):
        referents_precedents = {}

    referents = dict(referents_precedents)
    resolue = texte

    # Mémoire personnelle simple : nom de l'utilisateur.
    match_nom = re.search(
        r"\bje\s+m['’]appelle\s+([A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ'’-]*)",
        texte,
        re.IGNORECASE
    )

    if match_nom:
        nom = match_nom.group(1).strip(" .!?;:")
        if nom:
            referents["nom_utilisateur"] = nom

    # Question sur le nom mémorisé.
    demande_nom = re.search(
        r"\b(comment|quel|quelle)\b.*\b(appelle|nom)\b",
        bas
    )

    if demande_nom and referents.get("nom_utilisateur"):
        nom = referents["nom_utilisateur"]
        resolue = (
            texte
            + " — nom_utilisateur : "
            + nom
        )

    # Rappel explicite de l'objectif actif
    demande_rappel_objectif = bool(
        re.search(
            r"\bobjectif\b.*\b("
            r"viens de vous donner|"
            r"viens de donner|"
            r"que je viens de vous donner|"
            r"que je vous ai donné|"
            r"que je vous ai donne"
            r")\b",
            bas
        )
        or re.search(
            r"\bquel est l['’]objectif\b",
            bas
        )
    )

    if demande_rappel_objectif and objectif:
        referents["rappel->objectif_actif"] = True
        resolue = (
            "Rappel de l’objectif actif : "
            + str(objectif)
        )

    # Expressions de reprise
    expressions_suite = (
        "la suite",
        "prochaine étape",
        "prochaine etape",
        "continue",
        "continuer",
        "fais la suite",
        "faire la suite",
        "on continue",
        "poursuis",
        "poursuivre",
        "reprends",
        "reprendre"
    )

    demande_suite = (
        bas in expressions_suite
        or re.search(
            r"\b(fais|faire|continue|continuer|poursuis|poursuivre|reprends|reprendre|prochaine étape|prochaine etape)\b",
            bas
        )
    )

    if demande_suite:
        contexte = []

        if projet:
            contexte.append(f"projet actif : {projet}")
            referents["suite->projet_actif"] = True

        if objectif:
            contexte.append(f"objectif actif : {objectif}")
            referents["suite->objectif_actif"] = True

        if sujet:
            contexte.append(f"sujet actif : {sujet}")
            referents["suite->sujet_actif"] = True

        if contexte:
            resolue = texte + " — " + " ; ".join(contexte)

    # Questions de positionnement
    elif re.search(
        r"\b(où en sommes[- ]nous|ou en sommes[- ]nous|"
        r"où en est[- ]on|ou en est[- ]on|"
        r"état actuel|etat actuel)\b",
        bas
    ):
        contexte = []

        if projet:
            contexte.append(f"projet actif : {projet}")
            referents["positionnement->projet_actif"] = True

        if objectif:
            contexte.append(f"objectif actif : {objectif}")
            referents["positionnement->objectif_actif"] = True

        if sujet:
            contexte.append(f"sujet actif : {sujet}")
            referents["positionnement->sujet_actif"] = True

        if contexte:
            resolue = texte + " — " + " ; ".join(contexte)

    # Référents directs
    elif re.search(
        r"\b(ce projet|ce travail|cela|ça|ca|ce point|cet objectif)\b",
        bas
    ):
        contexte = []

        if projet:
            contexte.append(f"projet : {projet}")
            referents["référent->projet_actif"] = True

        if objectif:
            contexte.append(f"objectif : {objectif}")
            referents["référent->objectif_actif"] = True

        if sujet:
            contexte.append(f"sujet : {sujet}")
            referents["référent->sujet_actif"] = True

        if contexte:
            resolue = (
                texte
                + " — contexte précédent : "
                + " ; ".join(contexte)
            )

    return resolue, referents


def mia12_enregistrer_tour(
    session_id,
    question,
    question_resolue,
    intention,
    contexte,
    reponse
):
    mia12_initialiser_sqlite()

    etat = mia12_charger_etat(session_id)
    tour = int(etat.get("numero_tour", 0)) + 1

    maintenant = datetime.now().isoformat(timespec="seconds")

    referents = contexte.get("referents", [])

    conn = _connexion()

    conn.execute(
        """
        INSERT INTO conversation_turns (
            session_id,
            numero_tour,
            question,
            question_resolue,
            intention,
            sujet_actif,
            projet_actif,
            objectif_actif,
            reponse,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            tour,
            question,
            question_resolue,
            intention,
            contexte.get("sujet_actif"),
            contexte.get("projet_actif"),
            contexte.get("objectif_actif"),
            reponse,
            maintenant
        )
    )

    conn.execute(
        """
        INSERT INTO conversation_state (
            session_id,
            numero_tour,
            sujet_actif,
            projet_actif,
            objectif_actif,
            derniere_intention,
            derniere_question,
            derniere_reponse,
            referents,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            numero_tour = excluded.numero_tour,
            sujet_actif = excluded.sujet_actif,
            projet_actif = excluded.projet_actif,
            objectif_actif = excluded.objectif_actif,
            derniere_intention = excluded.derniere_intention,
            derniere_question = excluded.derniere_question,
            derniere_reponse = excluded.derniere_reponse,
            referents = excluded.referents,
            updated_at = excluded.updated_at
        """,
        (
            session_id,
            tour,
            contexte.get("sujet_actif"),
            contexte.get("projet_actif"),
            contexte.get("objectif_actif"),
            intention,
            question,
            reponse,
            json.dumps(referents, ensure_ascii=False),
            maintenant
        )
    )

    conn.commit()
    conn.close()

    return {
        "session_id": session_id,
        "numero_tour": tour,
        "enregistre": True
    }


def mia12_detecter_confirmation(question, etat=None):
    """
    Détecte les confirmations explicites et contextuelles.

    V12.12 :
    - "Je confirme." => confirmation explicite
    - "Je valide." => confirmation explicite
    - "Confirme" => confirmation explicite
    - "Oui"/"D'accord"/"Continue"/"Fais-le" =>
      confirmation contextuelle uniquement si le tour précédent
      demandait une confirmation.
    """

    texte = str(question or "").strip().lower()

    if not texte:
        return {
            "confirmation": False,
            "type": None,
            "confiance": 0,
            "raison": "question_vide"
        }

    # Normalisation simple de la ponctuation finale.
    normalise = texte.rstrip(" .!?;:")

    confirmations_explicites = {
        "je confirme",
        "je valide",
        "confirme",
        "confirmer",
        "validation confirmée",
        "validation confirmee",
    }

    if normalise in confirmations_explicites:
        return {
            "confirmation": True,
            "type": "explicite",
            "confiance": 100,
            "raison": "confirmation_explicite"
        }

    confirmations_contextuelles = {
        "oui",
        "d'accord",
        "daccord",
        "continue",
        "fais-le",
        "fais le",
    }

    if normalise in confirmations_contextuelles:
        derniere_reponse = ""

        if isinstance(etat, dict):
            derniere_reponse = str(
                etat.get("derniere_reponse") or ""
            ).lower()

        demande_confirmation = any(
            expression in derniere_reponse
            for expression in (
                "confirmer",
                "confirmation",
                "valider",
                "validation",
                "voulez-vous",
                "souhaitez-vous",
            )
        )

        if demande_confirmation:
            return {
                "confirmation": True,
                "type": "contextuelle",
                "confiance": 95,
                "raison": "confirmation_contextuelle"
            }

    return {
        "confirmation": False,
        "type": None,
        "confiance": 0,
        "raison": "aucune_confirmation_detectee"
    }


def mia12_preparer_tour(
    question,
    session_id="session_principale"
):
    etat = mia12_charger_etat(session_id)

    contexte = mia12_extraire_contexte(
        question,
        etat
    )

    question_resolue, referents = mia12_resoudre_referents(
        question,
        {
            **etat,
            **contexte
        }
    )

    contexte["referents"] = referents

    # V12.12.5 :
    # raccordement explicite de la détection de confirmation
    # à l'orchestrateur principal.
    confirmation = mia12_detecter_confirmation(
        question,
        etat
    )

    return {
        "session_id": session_id,
        "etat_precedent": etat,
        "question_originale": question,
        "question_resolue": question_resolue,
        "contexte": contexte,
        "confirmation": confirmation,
        "continuité_active": bool(
            etat.get("numero_tour", 0) > 0
        ),
        "referents_resolus": referents
    }


def mia12_resume_session(session_id="session_principale"):
    etat = mia12_charger_etat(session_id)

    return {
        "session_id": session_id,
        "numero_tour": etat["numero_tour"],
        "projet_actif": etat["projet_actif"],
        "objectif_actif": etat["objectif_actif"],
        "sujet_actif": etat["sujet_actif"],
        "derniere_intention": etat["derniere_intention"],
        "derniere_question": etat["derniere_question"],
        "continuité_active": etat["numero_tour"] > 0
    }


def mia12_derniers_tours(
    session_id="session_principale",
    limite=10
):
    mia12_initialiser_sqlite()

    conn = _connexion()

    rows = conn.execute(
        """
        SELECT
            numero_tour,
            question,
            question_resolue,
            intention,
            sujet_actif,
            projet_actif,
            objectif_actif,
            reponse,
            created_at
        FROM conversation_turns
        WHERE session_id = ?
        ORDER BY numero_tour DESC
        LIMIT ?
        """,
        (session_id, int(limite))
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def mia12_statut(session_id="session_principale"):
    return {
        "module": "MIA V12.12",
        "nom": "CONTINUITE CONVERSATIONNELLE REELLE",
        "statut": "operationnel",
        "session": mia12_resume_session(session_id)
    }


# Initialisation non destructive
mia12_initialiser_sqlite()
