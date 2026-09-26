"""
ALKAH-BRAIN
V12.90.0 — ORCHESTRATION DOCUMENTAIRE

Mission :
Relier le registre des outils et le socle fichiers/documents
afin de préparer un traitement documentaire cohérent.

Principe :
ORCHESTRER != EXECUTER
PROPOSER != MODIFIER

Cette version ne modifie aucun document,
n'exécute aucun outil et n'écrit aucune donnée persistante.
"""

VERSION = "V12.90.0"
MISSION = "ORCHESTRATION_DOCUMENTAIRE"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False
DECISION_AUTOMATIQUE = False
ECRITURE_PERSISTANTE = False
VALIDATION_HUMAINE_REQUISE = True


def mia90_normaliser_demande(demande):
    """Normalise une demande documentaire."""
    if isinstance(demande, str):
        return {
            "demande": demande.strip(),
            "document": "",
            "action": "",
        }

    if isinstance(demande, dict):
        resultat = dict(demande)
        resultat.setdefault("demande", "")
        resultat.setdefault("document", "")
        resultat.setdefault("action", "")
        return resultat

    return {
        "demande": "",
        "document": "",
        "action": "",
    }


def mia90_identifier_action(demande):
    """Identifie l'action documentaire demandée."""
    texte = str(
        mia90_normaliser_demande(demande).get("demande", "")
    ).lower()

    actions = (
        ("comparer", "comparer"),
        ("classer", "classer"),
        ("analyser", "analyser"),
        ("lire", "lire"),
        ("rechercher", "rechercher"),
        ("chercher", "rechercher"),
        ("synthétiser", "synthétiser"),
        ("synthese", "synthétiser"),
        ("synthèse", "synthétiser"),
    )

    for mot, action in actions:
        if mot in texte:
            return action

    return "a_preciser"


def mia90_preparer_besoin(demande):
    """Prépare le besoin documentaire sans exécution."""
    normalisee = mia90_normaliser_demande(demande)

    action = normalisee.get("action") or mia90_identifier_action(
        normalisee
    )

    return {
        "demande": normalisee,
        "action": action,
        "besoin_prepare": True,
        "execution": False,
        "validation_humaine": True,
    }


def mia90_selectionner_outil(registre, besoin):
    """
    Sélectionne un outil compatible à partir d'un registre fourni.
    Aucun outil n'est exécuté.
    """
    if not isinstance(registre, dict):
        return {
            "outil": None,
            "compatible": False,
            "raison": "registre_invalide",
            "execution": False,
        }

    outils = registre.get("outils", [])
    action = str(
        besoin.get("action", "")
    ).lower()

    candidats = []

    for outil in outils:
        if not isinstance(outil, dict):
            continue

        capacites = outil.get("capacites", [])

        if isinstance(capacites, str):
            capacites = [capacites]

        texte = " ".join(
            str(capacite).lower()
            for capacite in capacites
        )

        if action and action in texte:
            candidats.append(outil)

    if not candidats:
        return {
            "outil": None,
            "compatible": False,
            "raison": "aucun_outil_compatible",
            "execution": False,
            "validation_humaine": True,
        }

    return {
        "outil": candidats[0],
        "compatible": True,
        "raison": "capacite_compatible",
        "execution": False,
        "validation_humaine": True,
    }


def mia90_preparer_traitement(document, action):
    """Prépare le traitement documentaire proposé."""
    return {
        "document": document,
        "action": str(action or ""),
        "etapes": [
            "identifier",
            "verifier_lisibilite",
            "traiter",
            "analyser",
            "preparer_resultat",
        ],
        "execution": False,
        "modification": False,
        "ecriture": False,
        "validation_humaine": True,
    }


def mia90_evaluer_risque(outil):
    """Évalue le niveau de risque déclaré d'un outil."""
    if not isinstance(outil, dict):
        return {
            "niveau_risque": "inconnu",
            "validation_humaine": True,
        }

    return {
        "niveau_risque": outil.get(
            "niveau_risque",
            "inconnu"
        ),
        "validation_humaine": True,
        "execution": False,
    }


def mia90_verifier_permissions(outil):
    """Vérifie les permissions déclarées sans les modifier."""
    if not isinstance(outil, dict):
        return {
            "lecture": False,
            "ecriture": False,
            "execution": False,
        }

    permissions = outil.get("permissions", [])

    if isinstance(permissions, str):
        permissions = [permissions]

    permissions = [
        str(permission).lower()
        for permission in permissions
    ]

    return {
        "lecture": "lecture" in permissions,
        "ecriture": "ecriture" in permissions,
        "execution": "execution" in permissions,
        "modification": "modification" in permissions,
    }


def mia90_controler_compatibilite(outil, action):
    """Contrôle la compatibilité outil/action."""
    if not isinstance(outil, dict):
        return {
            "compatible": False,
            "raison": "outil_invalide",
        }

    capacites = outil.get("capacites", [])

    if isinstance(capacites, str):
        capacites = [capacites]

    action = str(action or "").lower()

    compatible = any(
        action in str(capacite).lower()
        for capacite in capacites
    )

    return {
        "compatible": compatible,
        "action": action,
        "capacites": capacites,
        "execution": False,
    }


def mia90_construire_sequence(document, action, outil):
    """Construit une séquence proposée, sans l'exécuter."""
    return {
        "document": document,
        "action": action,
        "outil_propose": outil,
        "sequence": [
            "besoin",
            "outil",
            "permission",
            "risque",
            "traitement",
            "resultat",
            "validation",
        ],
        "execution": False,
        "modification": False,
        "validation_humaine": True,
    }


def mia90_preparer_validation(sequence):
    """Prépare la validation humaine finale."""
    return {
        "sequence": sequence,
        "etat": "a_valider",
        "execution": False,
        "modification": False,
        "ecriture": False,
        "validation_humaine_requise": True,
    }


def mia90_orchestrer(demande, registre=None):
    """
    Fonction principale d'orchestration documentaire.

    Elle prépare une chaîne de traitement mais n'exécute
    aucune opération.
    """
    besoin = mia90_preparer_besoin(demande)

    resultat_outil = mia90_selectionner_outil(
        registre or {},
        besoin,
    )

    outil = resultat_outil.get("outil")

    risque = mia90_evaluer_risque(outil)
    permissions = mia90_verifier_permissions(outil)

    compatibilite = mia90_controler_compatibilite(
        outil,
        besoin.get("action"),
    )

    traitement = mia90_preparer_traitement(
        mia90_normaliser_demande(demande).get("document"),
        besoin.get("action"),
    )

    sequence = mia90_construire_sequence(
        traitement,
        besoin.get("action"),
        outil,
    )

    validation = mia90_preparer_validation(sequence)

    return {
        "besoin": besoin,
        "outil": resultat_outil,
        "risque": risque,
        "permissions": permissions,
        "compatibilite": compatibilite,
        "traitement": traitement,
        "validation": validation,
        "execution": False,
        "modification": False,
        "ecriture_persistante": False,
    }


def mia90_expliquer_orchestration(resultat):
    """Explique la chaîne proposée."""
    return {
        "raison": (
            "Le traitement est préparé à partir du besoin, "
            "de l'outil proposé, des permissions et du risque."
        ),
        "resultat": resultat,
        "execution": False,
        "validation_humaine": True,
    }


def mia90_statut():
    """Retourne le statut de sécurité de V12.90.0."""
    return {
        "version": VERSION,
        "mission": MISSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
        "decision_automatique": DECISION_AUTOMATIQUE,
        "ecriture_persistante": ECRITURE_PERSISTANTE,
        "validation_humaine_requise": VALIDATION_HUMAINE_REQUISE,
        "principe": "ORCHESTRER != EXECUTER",
    }
