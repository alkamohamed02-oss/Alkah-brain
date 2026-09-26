"""
ALKAH-BRAIN V12.26.0

Synthèse multi-trajectoires et agrégation descriptive.

Module strictement descriptif et lecture seule.
"""

VERSION = "V12.26.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False


def mia26_normaliser_trajectoire(trajectoire):
    if trajectoire is None:
        return {}

    if not isinstance(trajectoire, dict):
        return {"valeur": trajectoire}

    return dict(trajectoire)


def mia26_extraire_indicateurs(trajectoire):
    t = mia26_normaliser_trajectoire(trajectoire)

    indicateurs = t.get("indicateurs", {})

    if not isinstance(indicateurs, dict):
        return {}

    return dict(indicateurs)


def mia26_extraire_trajectoires(trajectoires):
    if not isinstance(trajectoires, list):
        return []

    return [
        mia26_normaliser_trajectoire(t)
        for t in trajectoires
    ]


def mia26_indicateurs_communs(trajectoires):
    trajectoires = mia26_extraire_trajectoires(
        trajectoires
    )

    if not trajectoires:
        return []

    ensembles = [
        set(mia26_extraire_indicateurs(t).keys())
        for t in trajectoires
    ]

    communs = ensembles[0]

    for ensemble in ensembles[1:]:
        communs &= ensemble

    return sorted(communs)


def mia26_agréger_indicateur(trajectoires, cle):
    valeurs = []

    for trajectoire in mia26_extraire_trajectoires(
        trajectoires
    ):
        indicateurs = mia26_extraire_indicateurs(
            trajectoire
        )

        if cle in indicateurs:
            valeur = indicateurs[cle]

            if (
                isinstance(valeur, (int, float))
                and not isinstance(valeur, bool)
            ):
                valeurs.append(valeur)

    if not valeurs:
        return {
            "nombre": 0,
            "valeurs": [],
            "moyenne": None,
        }

    return {
        "nombre": len(valeurs),
        "valeurs": list(valeurs),
        "moyenne": sum(valeurs) / len(valeurs),
    }


def mia26_detecter_stabilites(trajectoires):
    trajectoires = mia26_extraire_trajectoires(
        trajectoires
    )

    resultats = {}

    for cle in mia26_indicateurs_communs(
        trajectoires
    ):
        valeurs = [
            mia26_extraire_indicateurs(t)[cle]
            for t in trajectoires
        ]

        if all(valeur == valeurs[0] for valeur in valeurs):
            resultats[cle] = valeurs[0]

    return resultats


def mia26_detecter_divergences(trajectoires):
    trajectoires = mia26_extraire_trajectoires(
        trajectoires
    )

    resultats = {}

    for cle in mia26_indicateurs_communs(
        trajectoires
    ):
        valeurs = [
            mia26_extraire_indicateurs(t)[cle]
            for t in trajectoires
        ]

        if not all(valeur == valeurs[0] for valeur in valeurs):
            resultats[cle] = {
                "valeurs": valeurs,
                "nature": "divergence_descriptive",
            }

    return resultats


def mia26_identifier_tendances(trajectoires):
    trajectoires = mia26_extraire_trajectoires(
        trajectoires
    )

    resultats = {}

    for cle in mia26_indicateurs_communs(
        trajectoires
    ):
        valeurs = [
            mia26_extraire_indicateurs(t)[cle]
            for t in trajectoires
        ]

        numeriques = all(
            isinstance(v, (int, float))
            and not isinstance(v, bool)
            for v in valeurs
        )

        if numeriques and len(valeurs) >= 2:
            if valeurs[-1] > valeurs[0]:
                resultats[cle] = "hausse_globale"

            elif valeurs[-1] < valeurs[0]:
                resultats[cle] = "baisse_globale"

            else:
                resultats[cle] = "stable_globalement"

    return resultats


def mia26_qualifier_synthese(synthese):
    if not isinstance(synthese, dict):
        return "synthese_invalide"

    if not synthese.get("trajectoires"):
        return "aucune_trajectoire"

    if not synthese.get("indicateurs_communs"):
        return "donnees_insuffisantes"

    return "synthese_multi_trajectoires_descriptive"


def mia26_synthetiser_trajectoires(trajectoires):
    trajectoires = mia26_extraire_trajectoires(
        trajectoires
    )

    communs = mia26_indicateurs_communs(
        trajectoires
    )

    agregations = {
        cle: mia26_agréger_indicateur(
            trajectoires,
            cle
        )
        for cle in communs
    }

    stabilites = mia26_detecter_stabilites(
        trajectoires
    )

    divergences = mia26_detecter_divergences(
        trajectoires
    )

    tendances = mia26_identifier_tendances(
        trajectoires
    )

    resultat = {
        "version": VERSION,
        "trajectoires": len(trajectoires),
        "indicateurs_communs": communs,
        "agregations": agregations,
        "stabilites": stabilites,
        "divergences": divergences,
        "tendances": tendances,
        "incertitude": True,
        "correlation_demontree": False,
        "causalite_demontree": False,
        "decision_automatique": False,
        "execution": False,
    }

    resultat["qualification"] = (
        mia26_qualifier_synthese(resultat)
    )

    return resultat


def mia26_expliquer_synthese(resultat):
    if not isinstance(resultat, dict):
        return {
            "nature": "resultat_invalide"
        }

    return {
        "nature": "synthese_multi_trajectoires_descriptive",
        "qualification": resultat.get(
            "qualification",
            "indeterminee"
        ),
        "limites": [
            "dependance_aux_donnees_fournies",
            "absence_de_correlation_statistique_demontree",
            "absence_de_causalite_demontree",
            "evolution_future_non_certaine",
            "heterogeneite_possible_des_trajectoires",
        ],
    }


def mia26_verifier_synthese(resultat):
    return {
        "integrite": isinstance(resultat, dict),
        "autorisation_execution": False,
        "execution": False,
        "lecture_seule": True,
        "apprentissage_persistant": False,
        "decision_automatique": False,
        "correlation_demontree": False,
        "causalite_demontree": False,
    }


def mia26_statut():
    return {
        "version": VERSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
    }
