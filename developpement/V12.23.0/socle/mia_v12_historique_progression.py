"""
ALKAH-BRAIN / MIA
V12.21.0 — Historique et traçabilité de la progression.

V12.20 = état actuel de progression.
V12.21 = évolution et trajectoire entre états.

Le module est descriptif et lecture seule.
Il ne prend aucune décision d'exécution et ne modifie
aucun état de V12.20.0.
"""

from copy import deepcopy
from datetime import datetime, timezone


VERSION = "V12.21.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True


def _copie(donnees):
    return deepcopy(donnees)


def _progression(valeur):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return 0.0


def _horodatage():
    return datetime.now(timezone.utc).isoformat()


def mia21_comparer_etats(etat_precedent, etat_actuel):
    """Compare deux états sans les modifier."""

    precedent = (
        etat_precedent
        if isinstance(etat_precedent, dict)
        else {}
    )

    actuel = (
        etat_actuel
        if isinstance(etat_actuel, dict)
        else {}
    )

    champs = (
        "objectif",
        "plan",
        "etapes",
        "etapes_realisees",
        "etapes_en_cours",
        "etapes_a_faire",
        "etapes_bloquees",
        "progression",
        "decision_associee",
        "cycle",
        "etape_actuelle",
    )

    changements = {}

    for champ in champs:
        ancien = precedent.get(champ)
        nouveau = actuel.get(champ)

        if ancien != nouveau:
            changements[champ] = {
                "precedent": _copie(ancien),
                "actuel": _copie(nouveau),
            }

    p0 = _progression(precedent.get("progression", 0))
    p1 = _progression(actuel.get("progression", 0))

    return {
        "etat_precedent_present": bool(precedent),
        "etat_actuel_present": bool(actuel),
        "progression_precedente": p0,
        "progression_actuelle": p1,
        "variation_progression": round(p1 - p0, 6),
        "changements": changements,
        "nombre_changements": len(changements),
    }


def mia21_calculer_variation(progression_precedente, progression_actuelle):
    """Calcule la variation de progression."""

    p0 = _progression(progression_precedente)
    p1 = _progression(progression_actuelle)

    variation = round(p1 - p0, 6)

    if variation > 0:
        direction = "hausse"
    elif variation < 0:
        direction = "baisse"
    else:
        direction = "stable"

    return {
        "progression_precedente": p0,
        "progression_actuelle": p1,
        "variation": variation,
        "direction": direction,
    }


def mia21_qualifier_evolution(comparaison):
    """Qualifie l'évolution observée."""

    if not isinstance(comparaison, dict):
        return {
            "qualification": "indeterminee",
            "variation": 0.0,
            "nombre_changements": 0,
        }

    variation = _progression(
        comparaison.get("variation_progression", 0)
    )

    changements = comparaison.get("changements", {})
    nombre = len(changements)

    if variation > 0:
        qualification = "progression"
    elif variation < 0:
        qualification = "regression"
    elif nombre == 0:
        qualification = "stagnation"
    else:
        qualification = "changement_sans_variation"

    return {
        "qualification": qualification,
        "variation": round(variation, 6),
        "nombre_changements": nombre,
    }


def mia21_detecter_changements(etat_precedent, etat_actuel):
    """Détecte les changements observables."""

    comparaison = mia21_comparer_etats(
        etat_precedent,
        etat_actuel,
    )

    changements = comparaison.get("changements", {})

    return {
        "changements": changements,
        "nombre_changements": len(changements),
        "etapes_changees": "etapes" in changements,
        "progression_changee": "progression" in changements,
        "decision_changee": "decision_associee" in changements,
        "cycle_change": "cycle" in changements,
        "etape_actuelle_changee": "etape_actuelle" in changements,
    }


def mia21_creer_copie_trace(donnees):
    """Crée une copie indépendante des données."""

    return _copie(donnees)


def mia21_creer_trace_historique(
    etat_precedent,
    etat_actuel,
    comparaison=None,
):
    """Crée une trace historique complète."""

    if comparaison is None:
        comparaison = mia21_comparer_etats(
            etat_precedent,
            etat_actuel,
        )

    qualification = mia21_qualifier_evolution(
        comparaison
    )

    changements = mia21_detecter_changements(
        etat_precedent,
        etat_actuel,
    )

    correspondance = mia21_evaluer_correspondance_temporelle(
        etat_precedent,
        etat_actuel,
    )

    trace = {
        "version": VERSION,
        "horodatage": _horodatage(),
        "etat_precedent": _copie(etat_precedent),
        "etat_actuel": _copie(etat_actuel),
        "comparaison": _copie(comparaison),
        "qualification": _copie(qualification),
        "changements": _copie(changements),
        "correspondance_temporelle": _copie(
            correspondance
        ),
    }

    return mia21_creer_copie_trace(trace)


def mia21_ajouter_trace_historique(historique, trace):
    """Ajoute une trace sans modifier la source."""

    if historique is None:
        historique = []

    if not isinstance(historique, list):
        return historique

    resultat = _copie(historique)
    resultat.append(
        mia21_creer_copie_trace(trace)
    )

    return resultat


def mia21_lire_historique(historique):
    """Retourne une copie indépendante de l'historique."""

    if not isinstance(historique, list):
        return []

    return _copie(historique)


def mia21_expliquer_evolution(trace):
    """Explique l'évolution sans établir de causalité non prouvée."""

    if not isinstance(trace, dict):
        return {
            "explication": "Trace absente ou invalide.",
            "niveau_certitude": "indetermine",
            "causalite_etablie": False,
        }

    qualification = trace.get(
        "qualification",
        {},
    )

    type_evolution = qualification.get(
        "qualification",
        "indeterminee",
    )

    variation = _progression(
        qualification.get("variation", 0)
    )

    changements = trace.get(
        "changements",
        {},
    )

    nombre = changements.get(
        "nombre_changements",
        0,
    )

    if type_evolution == "progression":
        texte = (
            "La progression a augmenté de "
            f"{variation} point(s)."
        )

    elif type_evolution == "regression":
        texte = (
            "La progression a diminué de "
            f"{abs(variation)} point(s)."
        )

    elif type_evolution == "stagnation":
        texte = (
            "Aucune évolution observable "
            "de l'état."
        )

    else:
        texte = (
            "Des changements ont été observés "
            "sans variation de progression."
        )

    return {
        "explication": texte,
        "type_evolution": type_evolution,
        "variation": variation,
        "nombre_changements": nombre,
        "causalite_etablie": False,
        "niveau_certitude": "descriptif",
    }


def mia21_evaluer_correspondance_temporelle(
    etat_precedent,
    etat_actuel,
):
    """
    Évalue une correspondance temporelle observable.

    Cette fonction ne déduit aucune causalité.
    """

    precedent = (
        etat_precedent
        if isinstance(etat_precedent, dict)
        else {}
    )

    actuel = (
        etat_actuel
        if isinstance(etat_actuel, dict)
        else {}
    )

    cycle_precedent = precedent.get("cycle")
    cycle_actuel = actuel.get("cycle")

    correspondance = False
    motif = "cycles_non_identifiables"

    if (
        cycle_precedent is not None
        and cycle_actuel is not None
    ):
        try:
            correspondance = (
                int(cycle_actuel)
                > int(cycle_precedent)
            )

            if correspondance:
                motif = "cycle_actuel_posterieur"
            else:
                motif = "cycle_actuel_non_posterieur"

        except (TypeError, ValueError):
            motif = "cycles_non_numeriques"

    return {
        "correspondance_temporelle": correspondance,
        "cycle_precedent": cycle_precedent,
        "cycle_actuel": cycle_actuel,
        "motif": motif,
        "causalite_etablie": False,
    }


def mia21_verifier_trace(trace):
    """Vérifie l'intégrité minimale d'une trace."""

    if not isinstance(trace, dict):
        return {
            "valide": False,
            "erreurs": ["trace_non_dict"],
        }

    obligatoires = (
        "version",
        "horodatage",
        "etat_precedent",
        "etat_actuel",
        "comparaison",
        "qualification",
        "changements",
        "correspondance_temporelle",
    )

    erreurs = []

    for champ in obligatoires:
        if champ not in trace:
            erreurs.append(champ)

    if trace.get("version") != VERSION:
        erreurs.append("version_incorrecte")

    return {
        "valide": len(erreurs) == 0,
        "erreurs": erreurs,
        "version": trace.get("version"),
    }


def mia21_statut():
    """Retourne le statut officiel du module."""

    return {
        "module": "mia_v12_historique_progression",
        "version": VERSION,
        "statut": "operationnel",
        "responsabilite": (
            "historique_et_tracabilite"
        ),
        "autorisation_execution": (
            AUTORISATION_EXECUTION
        ),
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "v12_20_modifiee": False,
    }
