"""
ALKAH-BRAIN
V12.70.0 — REGISTRE DES OUTILS

Mission :
Permettre à MIA de connaître les outils disponibles,
leurs capacités, paramètres, permissions, risques et limites.

Principe :
CONNAITRE ≠ EXECUTER

Cette version est descriptive et consultative.
Aucune exécution automatique.
"""

VERSION = "V12.70.0"
MISSION = "REGISTRE_DES_OUTILS"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False
DECISION_AUTOMATIQUE = False
ECRITURE_PERSISTANTE = False
VALIDATION_HUMAINE_REQUISE = True


NIVEAUX_RISQUE = (
    "faible",
    "moyen",
    "eleve",
    "tres_eleve",
)


def mia70_normaliser_outil(outil):
    if isinstance(outil, str):
        return {
            "nom": outil.strip(),
            "description": "",
            "capacites": [],
            "parametres": [],
            "permissions": [],
            "niveau_risque": "moyen",
            "limites": [],
            "conditions_utilisation": [],
            "alternatives": [],
            "validation_humaine": True,
        }

    if not isinstance(outil, dict):
        return {}

    resultat = dict(outil)

    resultat.setdefault("nom", "")
    resultat.setdefault("description", "")
    resultat.setdefault("capacites", [])
    resultat.setdefault("parametres", [])
    resultat.setdefault("permissions", [])
    resultat.setdefault("niveau_risque", "moyen")
    resultat.setdefault("limites", [])
    resultat.setdefault("conditions_utilisation", [])
    resultat.setdefault("alternatives", [])
    resultat.setdefault("validation_humaine", True)

    return resultat


def mia70_creer_registre():
    return {
        "version": VERSION,
        "mission": MISSION,
        "outils": [],
        "lecture_seule": True,
        "execution": False,
        "validation_humaine_requise": True,
    }


def mia70_ajouter_outil(registre, outil):
    resultat = dict(registre)
    outils = list(registre.get("outils", []))

    normalise = mia70_normaliser_outil(outil)

    if normalise:
        outils.append(normalise)

    resultat["outils"] = outils

    return resultat


def mia70_rechercher_outil(registre, terme):
    terme = str(terme).lower().strip()

    resultats = []

    for outil in registre.get("outils", []):

        texte = " ".join([
            str(outil.get("nom", "")),
            str(outil.get("description", "")),
            " ".join(map(str, outil.get("capacites", []))),
        ]).lower()

        if terme in texte:
            resultats.append(outil)

    return resultats


def mia70_obtenir_outil(registre, nom):
    nom = str(nom).lower().strip()

    for outil in registre.get("outils", []):

        if str(outil.get("nom", "")).lower().strip() == nom:
            return outil

    return None


def mia70_lister_outils(registre):
    return list(registre.get("outils", []))


def mia70_verifier_risque(outil):
    niveau = str(
        outil.get("niveau_risque", "moyen")
    ).lower().strip()

    if niveau not in NIVEAUX_RISQUE:
        return {
            "valide": False,
            "niveau": niveau,
            "raison": "Niveau de risque inconnu.",
        }

    return {
        "valide": True,
        "niveau": niveau,
        "raison": "Niveau de risque reconnu.",
    }


def mia70_verifier_permissions(outil):
    permissions = outil.get("permissions", [])

    if not isinstance(permissions, list):
        permissions = [permissions]

    return {
        "permissions": permissions,
        "lecture_seule": "ecriture" not in [
            str(p).lower() for p in permissions
        ],
    }


def mia70_analyser_compatibilite(outil, besoin):
    texte = str(besoin).lower()

    capacites = [
        str(c).lower()
        for c in outil.get("capacites", [])
    ]

    correspondances = []

    for capacite in capacites:
        if capacite and capacite in texte:
            correspondances.append(capacite)

    return {
        "outil": outil.get("nom", ""),
        "besoin": besoin,
        "correspondances": correspondances,
        "compatible": bool(correspondances),
    }


def mia70_evaluer_outil(outil, besoin):
    risque = mia70_verifier_risque(outil)
    permissions = mia70_verifier_permissions(outil)
    compatibilite = mia70_analyser_compatibilite(
        outil,
        besoin
    )

    return {
        "outil": outil.get("nom", ""),
        "compatible": compatibilite["compatible"],
        "correspondances": compatibilite["correspondances"],
        "risque": risque,
        "permissions": permissions,
        "limites": outil.get("limites", []),
        "validation_humaine": outil.get(
            "validation_humaine",
            True
        ),
    }


def mia70_proposer_outil(registre, besoin):
    candidats = []

    for outil in registre.get("outils", []):

        evaluation = mia70_evaluer_outil(
            outil,
            besoin
        )

        if evaluation["compatible"]:
            candidats.append(evaluation)

    return {
        "besoin": besoin,
        "candidats": candidats,
        "outil_propose": (
            candidats[0]["outil"]
            if candidats
            else None
        ),
        "validation_humaine_requise": True,
        "execution": False,
    }


def mia70_expliquer_choix(evaluation):
    if not evaluation:
        return "Aucun outil compatible identifié."

    nom = evaluation.get("outil", "")

    raisons = []

    if evaluation.get("correspondances"):
        raisons.append(
            "capacités compatibles avec le besoin"
        )

    niveau = evaluation.get(
        "risque",
        {}
    ).get("niveau")

    if niveau:
        raisons.append(
            "niveau de risque identifié : " + niveau
        )

    return (
        "Outil proposé : "
        + str(nom)
        + ". Raisons : "
        + ", ".join(raisons)
        + "."
    )


def mia70_statut():
    return {
        "version": VERSION,
        "mission": MISSION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant":
            APPRENTISSAGE_PERSISTANT,
        "decision_automatique":
            DECISION_AUTOMATIQUE,
        "ecriture_persistante":
            ECRITURE_PERSISTANTE,
        "validation_humaine_requise":
            VALIDATION_HUMAINE_REQUISE,
        "niveaux_risque": NIVEAUX_RISQUE,
    }
