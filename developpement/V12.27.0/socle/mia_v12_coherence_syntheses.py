"""
ALKAH-BRAIN V12.27.0

Cohérence descriptive entre synthèses multi-trajectoires.

Module strictement descriptif et lecture seule.
"""

VERSION = "V12.27.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False


def mia27_normaliser_synthese(synthese):
    if synthese is None:
        return {}

    if not isinstance(synthese, dict):
        return {"valeur": synthese}

    return dict(synthese)


def mia27_extraire_agregations(synthese):
    s = mia27_normaliser_synthese(synthese)

    agregations = s.get("agregations", {})

    if not isinstance(agregations, dict):
        return {}

    return dict(agregations)


def mia27_extraire_syntheses(syntheses):
    if not isinstance(syntheses, list):
        return []

    return [
        mia27_normaliser_synthese(s)
        for s in syntheses
    ]


def mia27_indicateurs_communs(syntheses):
    syntheses = mia27_extraire_syntheses(syntheses)

    if not syntheses:
        return []

    ensembles = [
        set(mia27_extraire_agregations(s).keys())
        for s in syntheses
    ]

    communs = ensembles[0]

    for ensemble in ensembles[1:]:
        communs &= ensemble

    return sorted(communs)


def mia27_extraire_moyenne(synthese, cle):
    agregations = mia27_extraire_agregations(synthese)

    element = agregations.get(cle, {})

    if not isinstance(element, dict):
        return None

    valeur = element.get("moyenne")

    if (
        isinstance(valeur, (int, float))
        and not isinstance(valeur, bool)
    ):
        return valeur

    return None


def mia27_detecter_accords(syntheses):
    syntheses = mia27_extraire_syntheses(syntheses)

    resultats = {}

    for cle in mia27_indicateurs_communs(syntheses):
        valeurs = [
            mia27_extraire_moyenne(s, cle)
            for s in syntheses
        ]

        valeurs_valides = [
            v for v in valeurs
            if v is not None
        ]

        if valeurs_valides and all(
            v == valeurs_valides[0]
            for v in valeurs_valides
        ):
            resultats[cle] = {
                "valeur": valeurs_valides[0],
                "nature": "accord_descriptif",
            }

    return resultats


def mia27_detecter_desaccords(syntheses):
    syntheses = mia27_extraire_syntheses(syntheses)

    resultats = {}

    for cle in mia27_indicateurs_communs(syntheses):
        valeurs = [
            mia27_extraire_moyenne(s, cle)
            for s in syntheses
        ]

        valeurs_valides = [
            v for v in valeurs
            if v is not None
        ]

        if len(valeurs_valides) >= 2:
            if not all(
                v == valeurs_valides[0]
                for v in valeurs_valides
            ):
                resultats[cle] = {
                    "valeurs": valeurs_valides,
                    "nature": "desaccord_descriptif",
                }

    return resultats


def mia27_evaluer_coherence_indicateur(
    syntheses,
    cle
):
    syntheses = mia27_extraire_syntheses(syntheses)

    valeurs = [
        mia27_extraire_moyenne(s, cle)
        for s in syntheses
    ]

    valeurs = [
        v for v in valeurs
        if v is not None
    ]

    if not valeurs:
        return {
            "nombre": 0,
            "coherence": None,
        }

    if len(valeurs) == 1:
        return {
            "nombre": 1,
            "coherence": 1.0,
        }

    minimum = min(valeurs)
    maximum = max(valeurs)

    if maximum == minimum:
        score = 1.0
    else:
        moyenne = sum(valeurs) / len(valeurs)

        if moyenne == 0:
            score = 0.0
        else:
            ecart = maximum - minimum
            score = max(
                0.0,
                1.0 - (abs(ecart) / abs(moyenne))
            )

    return {
        "nombre": len(valeurs),
        "coherence": score,
    }


def mia27_evaluer_coherence(syntheses):
    syntheses = mia27_extraire_syntheses(syntheses)

    resultats = {}

    for cle in mia27_indicateurs_communs(
        syntheses
    ):
        resultats[cle] = (
            mia27_evaluer_coherence_indicateur(
                syntheses,
                cle
            )
        )

    return resultats


def mia27_qualifier_coherence(resultat):
    if not isinstance(resultat, dict):
        return "resultat_invalide"

    if not resultat.get("syntheses"):
        return "aucune_synthese"

    if not resultat.get("indicateurs_communs"):
        return "donnees_insuffisantes"

    coherences = resultat.get("coherences", {})

    if not coherences:
        return "coherence_indeterminee"

    valeurs = [
        element.get("coherence")
        for element in coherences.values()
        if isinstance(element, dict)
        and isinstance(
            element.get("coherence"),
            (int, float)
        )
    ]

    if not valeurs:
        return "coherence_indeterminee"

    moyenne = sum(valeurs) / len(valeurs)

    if moyenne >= 0.8:
        return "coherence_descriptive_forte"

    if moyenne >= 0.5:
        return "coherence_descriptive_moderee"

    return "coherence_descriptive_faible"


def mia27_synthetiser_coherence(syntheses):
    syntheses = mia27_extraire_syntheses(
        syntheses
    )

    communs = mia27_indicateurs_communs(
        syntheses
    )

    accords = mia27_detecter_accords(
        syntheses
    )

    desaccords = mia27_detecter_desaccords(
        syntheses
    )

    coherences = mia27_evaluer_coherence(
        syntheses
    )

    resultat = {
        "version": VERSION,
        "syntheses": len(syntheses),
        "indicateurs_communs": communs,
        "accords": accords,
        "desaccords": desaccords,
        "coherences": coherences,
        "incertitude": True,
        "correlation_demontree": False,
        "causalite_demontree": False,
        "decision_automatique": False,
        "execution": False,
    }

    resultat["qualification"] = (
        mia27_qualifier_coherence(resultat)
    )

    return resultat


def mia27_expliquer_coherence(resultat):
    if not isinstance(resultat, dict):
        return {
            "nature": "resultat_invalide"
        }

    return {
        "nature": "coherence_descriptive",
        "qualification": resultat.get(
            "qualification",
            "indeterminee"
        ),
        "limites": [
            "dependance_aux_donnees_fournies",
            "absence_de_preuve_statistique_complete",
            "absence_de_correlation_demontree",
            "absence_de_causalite_demontree",
            "comparaison_descriptive",
        ],
    }


def mia27_verifier_coherence(resultat):
    return {
        "integrite": isinstance(resultat, dict),
        "autorisation_execution": False,
        "execution": False,
        "lecture_seule": True,
        "apprentissage_persistant": False,
        "decision_automatique": False,
        "correlation_demontree": False,
        "causalite_demontee": False,
    }


def mia27_statut():
    return {
        "version": VERSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
    }
