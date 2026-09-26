"""
ALKAH-BRAIN V12.22.0
Analyse de trajectoire et apprentissage descriptif.

Lecture seule.
Aucune exécution.
Aucune décision autonome.
Aucune modification de l'historique source.
"""

from copy import deepcopy
from statistics import mean

VERSION = "V12.22.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True


def _copie(valeur):
    return deepcopy(valeur)


def _variation(trace):
    if not isinstance(trace, dict):
        return 0.0

    valeur = trace.get("variation")

    if isinstance(valeur, (int, float)):
        return float(valeur)

    comparaison = trace.get("comparaison")

    if isinstance(comparaison, dict):
        valeur = comparaison.get("variation")
        if isinstance(valeur, (int, float)):
            return float(valeur)

    return 0.0


def _type(trace):
    if not isinstance(trace, dict):
        return "inconnu"

    valeur = trace.get("type_evolution")

    if valeur:
        return str(valeur).lower()

    valeur = trace.get("qualification")

    if valeur:
        return str(valeur).lower()

    return "inconnu"


def mia22_normaliser_historique(historique):
    """Retourne une copie normalisée de l'historique."""

    if not isinstance(historique, list):
        return []

    resultat = []

    for trace in historique:

        if isinstance(trace, dict):

            copie = _copie(trace)

            copie["variation"] = _variation(copie)

            copie["type_evolution"] = _type(copie)

            resultat.append(copie)

    return resultat


def mia22_calculer_indicateurs_trajectoire(historique):
    """Calcule les indicateurs descriptifs."""

    traces = mia22_normaliser_historique(historique)

    variations = [
        trace["variation"]
        for trace in traces
    ]

    positives = [
        valeur
        for valeur in variations
        if valeur > 0
    ]

    nulles = [
        valeur
        for valeur in variations
        if valeur == 0
    ]

    negatives = [
        valeur
        for valeur in variations
        if valeur < 0
    ]

    return {
        "nombre_traces": len(traces),
        "nombre_progressions": len(positives),
        "nombre_stagnations": len(nulles),
        "nombre_regressions": len(negatives),
        "variation_moyenne": (
            round(mean(variations), 2)
            if variations
            else 0.0
        ),
        "variation_totale": round(
            sum(variations),
            2
        ),
        "variations": _copie(variations),
    }


def mia22_analyser_tendance(historique):
    """Analyse la direction dominante."""

    indicateurs = (
        mia22_calculer_indicateurs_trajectoire(
            historique
        )
    )

    progressions = indicateurs[
        "nombre_progressions"
    ]

    stagnations = indicateurs[
        "nombre_stagnations"
    ]

    regressions = indicateurs[
        "nombre_regressions"
    ]

    if (
        progressions == 0
        and stagnations == 0
        and regressions == 0
    ):
        direction = "inconnue"

    elif (
        progressions > regressions
        and progressions >= stagnations
    ):
        direction = "hausse"

    elif (
        regressions > progressions
        and regressions >= stagnations
    ):
        direction = "baisse"

    elif (
        stagnations >= progressions
        and stagnations >= regressions
    ):
        direction = "stable"

    else:
        direction = "mixte"

    return {
        "direction_dominante": direction,
        "progressions": progressions,
        "stagnations": stagnations,
        "regressions": regressions,
        "variation_moyenne": indicateurs[
            "variation_moyenne"
        ],
    }


def mia22_detecter_stagnations(historique):
    """Détecte les stagnations."""

    traces = mia22_normaliser_historique(
        historique
    )

    return [
        _copie(trace)
        for trace in traces
        if (
            trace["variation"] == 0
            or trace["type_evolution"]
            in ("stagnation", "stable")
        )
    ]


def mia22_detecter_regressions(historique):
    """Détecte les régressions."""

    traces = mia22_normaliser_historique(
        historique
    )

    return [
        _copie(trace)
        for trace in traces
        if (
            trace["variation"] < 0
            or trace["type_evolution"]
            in ("regression", "régression")
        )
    ]


def mia22_detecter_recurrences(historique):
    """Compte les types d'évolution récurrents."""

    traces = mia22_normaliser_historique(
        historique
    )

    compte = {}

    for trace in traces:

        type_evolution = trace[
            "type_evolution"
        ]

        compte[type_evolution] = (
            compte.get(type_evolution, 0) + 1
        )

    recurrences = {
        cle: valeur
        for cle, valeur in compte.items()
        if valeur >= 2
    }

    return {
        "types": compte,
        "recurrences": recurrences,
    }


def mia22_detecter_patterns(historique):
    """Détecte des motifs descriptifs simples."""

    traces = mia22_normaliser_historique(
        historique
    )

    variations = [
        trace["variation"]
        for trace in traces
    ]

    progression_continue = (
        len(variations) >= 2
        and all(
            valeur > 0
            for valeur in variations
        )
    )

    regression_continue = (
        len(variations) >= 2
        and all(
            valeur < 0
            for valeur in variations
        )
    )

    stagnation_repetee = (
        len(variations) >= 2
        and sum(
            valeur == 0
            for valeur in variations
        ) >= 2
    )

    alternance = False

    if len(variations) >= 3:

        signes = [
            1 if valeur > 0
            else -1 if valeur < 0
            else 0
            for valeur in variations
        ]

        signes_utiles = [
            signe
            for signe in signes
            if signe != 0
        ]

        if len(signes_utiles) >= 3:

            alternance = all(
                signes_utiles[index]
                != signes_utiles[index - 1]
                for index in range(
                    1,
                    len(signes_utiles)
                )
            )

    return {
        "alternance": alternance,
        "progression_continue": progression_continue,
        "regression_continue": regression_continue,
        "stagnation_repetee": stagnation_repetee,
    }


def mia22_qualifier_trajectoire(indicateurs):
    """Qualifie la trajectoire."""

    if not isinstance(indicateurs, dict):
        return {
            "qualification":
                "historique_insuffisant",
            "certitude": "faible",
        }

    nombre = indicateurs.get(
        "nombre_traces",
        0
    )

    if nombre == 0:

        qualification = (
            "historique_insuffisant"
        )

    else:

        progressions = indicateurs.get(
            "nombre_progressions",
            0
        )

        stagnations = indicateurs.get(
            "nombre_stagnations",
            0
        )

        regressions = indicateurs.get(
            "nombre_regressions",
            0
        )

        if (
            progressions > 0
            and regressions > 0
        ):
            qualification = (
                "trajectoire_mixte"
            )

        elif progressions > 0:

            qualification = "progression"

        elif regressions > 0:

            qualification = "regression"

        elif stagnations > 0:

            qualification = "stagnation"

        else:

            qualification = (
                "trajectoire_mixte"
            )

    return {
        "qualification": qualification,
        "nombre_traces": nombre,
        "certitude": "descriptive",
    }


def mia22_synthetiser_trajectoire(
    qualification,
    indicateurs
):
    """Construit une synthèse descriptive."""

    if not isinstance(
        qualification,
        dict
    ):
        qualification = (
            mia22_qualifier_trajectoire(
                indicateurs
            )
        )

    if isinstance(indicateurs, dict):

        nombre = indicateurs.get(
            "nombre_traces",
            0
        )

        moyenne = indicateurs.get(
            "variation_moyenne",
            0.0
        )

    else:

        nombre = 0
        moyenne = 0.0

    return {
        "qualification": qualification.get(
            "qualification",
            "historique_insuffisant",
        ),
        "nombre_traces": nombre,
        "variation_moyenne": moyenne,
        "lecture": "descriptive",
        "causalite_etablie": False,
    }


def mia22_expliquer_trajectoire(
    analyse
):
    """Produit une explication descriptive."""

    if not isinstance(
        analyse,
        dict
    ):
        return {
            "explication":
                "Analyse indisponible.",
            "causalite_etablie": False,
            "niveau_certitude":
                "descriptif",
        }

    qualification = analyse.get(
        "qualification",
        "historique_insuffisant"
    )

    moyenne = analyse.get(
        "variation_moyenne",
        0.0
    )

    nombre = analyse.get(
        "nombre_traces",
        0
    )

    if qualification == "progression":

        texte = (
            "La trajectoire présente "
            f"une progression sur {nombre} "
            "trace(s), avec une variation "
            f"moyenne de {moyenne} point(s)."
        )

    elif qualification == "regression":

        texte = (
            "La trajectoire présente "
            f"une régression sur {nombre} "
            "trace(s), avec une variation "
            f"moyenne de {moyenne} point(s)."
        )

    elif qualification == "stagnation":

        texte = (
            "La trajectoire présente "
            f"une stagnation sur {nombre} "
            "trace(s)."
        )

    elif qualification == "trajectoire_mixte":

        texte = (
            "La trajectoire est mixte sur "
            f"{nombre} trace(s), avec "
            "plusieurs directions observées."
        )

    else:

        texte = (
            "L'historique disponible "
            "est insuffisant."
        )

    return {
        "explication": texte,
        "type_trajectoire": qualification,
        "variation_moyenne": moyenne,
        "nombre_traces": nombre,
        "causalite_etablie": False,
        "niveau_certitude": "descriptif",
    }


def mia22_verifier_analyse(analyse):
    """Vérifie la structure minimale."""

    erreurs = []

    if not isinstance(
        analyse,
        dict
    ):
        erreurs.append(
            "analyse_non_dict"
        )

    else:

        if "qualification" not in analyse:
            erreurs.append(
                "qualification_absente"
            )

        if "nombre_traces" not in analyse:
            erreurs.append(
                "nombre_traces_absent"
            )

        if (
            "causalite_etablie"
            in analyse
            and analyse[
                "causalite_etablie"
            ] is not False
        ):
            erreurs.append(
                "causalite_non_autorisee"
            )

    return {
        "valide": len(erreurs) == 0,
        "erreurs": erreurs,
        "version": VERSION,
    }


def mia22_statut():
    """Retourne le statut sécurisé."""

    return {
        "module":
            "mia_v12_analyse_trajectoire",
        "version": VERSION,
        "statut": "operationnel",
        "responsabilite":
            "analyse_trajectoire",
        "autorisation_execution":
            AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "v12_20_modifiee": False,
        "v12_21_modifiee": False,
        "apprentissage_persistant": False,
    }
