"""
ALKAH-BRAIN V12.25.0

Relations entre trajectoires et corrélations descriptives.

Module strictement descriptif et lecture seule.
"""

VERSION = "V12.25.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False


def mia25_normaliser_trajectoire(trajectoire):
    if trajectoire is None:
        return {}

    if not isinstance(trajectoire, dict):
        return {"valeur": trajectoire}

    return dict(trajectoire)


def mia25_extraire_indicateurs(trajectoire):
    t = mia25_normaliser_trajectoire(trajectoire)

    indicateurs = t.get("indicateurs", {})

    if not isinstance(indicateurs, dict):
        indicateurs = {}

    return dict(indicateurs)


def mia25_alignement_indicateurs(trajectoire_a, trajectoire_b):
    a = mia25_extraire_indicateurs(trajectoire_a)
    b = mia25_extraire_indicateurs(trajectoire_b)

    cles_a = set(a.keys())
    cles_b = set(b.keys())

    return {
        "communs": sorted(cles_a & cles_b),
        "uniquement_a": sorted(cles_a - cles_b),
        "uniquement_b": sorted(cles_b - cles_a),
    }


def mia25_comparer_indicateur(valeur_a, valeur_b):
    if valeur_a == valeur_b:
        return "stable"

    if (
        isinstance(valeur_a, (int, float))
        and isinstance(valeur_b, (int, float))
        and not isinstance(valeur_a, bool)
        and not isinstance(valeur_b, bool)
    ):
        if valeur_b > valeur_a:
            return "hausse"

        if valeur_b < valeur_a:
            return "baisse"

    return "different"


def mia25_detecter_coevolutions(trajectoire_a, trajectoire_b):
    a = mia25_extraire_indicateurs(trajectoire_a)
    b = mia25_extraire_indicateurs(trajectoire_b)

    communs = sorted(set(a.keys()) & set(b.keys()))
    relations = {}

    for cle in communs:
        comparaison = mia25_comparer_indicateur(a[cle], b[cle])

        if comparaison in ("hausse", "baisse"):
            relations[cle] = {
                "valeur_a": a[cle],
                "valeur_b": b[cle],
                "direction": comparaison,
                "nature": "coevolution_descriptive",
            }

    return relations


def mia25_detecter_relations(trajectoire_a, trajectoire_b):
    a = mia25_extraire_indicateurs(trajectoire_a)
    b = mia25_extraire_indicateurs(trajectoire_b)

    communs = sorted(set(a.keys()) & set(b.keys()))
    relations = {}

    for cle in communs:
        comparaison = mia25_comparer_indicateur(a[cle], b[cle])

        relations[cle] = {
            "valeur_a": a[cle],
            "valeur_b": b[cle],
            "relation": comparaison,
        }

    return relations


def mia25_detecter_stabilites(trajectoire_a, trajectoire_b):
    relations = mia25_detecter_relations(
        trajectoire_a,
        trajectoire_b
    )

    return sorted(
        cle
        for cle, valeur in relations.items()
        if valeur["relation"] == "stable"
    )


def mia25_detecter_relations_recurrentes(historique_relations):
    if not isinstance(historique_relations, list):
        return []

    compte = {}

    for relation in historique_relations:
        cle = str(relation)
        compte[cle] = compte.get(cle, 0) + 1

    return sorted(
        cle
        for cle, nombre in compte.items()
        if nombre > 1
    )


def mia25_qualifier_relations(relations):
    if not relations:
        return "aucune_relation_descriptive"

    return "relations_descriptives_detectees"


def mia25_evaluer_coherence(relations):
    if not isinstance(relations, dict):
        return False

    for valeur in relations.values():
        if not isinstance(valeur, dict):
            return False

    return True


def mia25_synthetiser_relations(trajectoire_a, trajectoire_b):
    alignement = mia25_alignement_indicateurs(
        trajectoire_a,
        trajectoire_b
    )

    relations = mia25_detecter_relations(
        trajectoire_a,
        trajectoire_b
    )

    coevolutions = mia25_detecter_coevolutions(
        trajectoire_a,
        trajectoire_b
    )

    stabilites = mia25_detecter_stabilites(
        trajectoire_a,
        trajectoire_b
    )

    return {
        "version": VERSION,
        "alignement": alignement,
        "relations": relations,
        "coevolutions": coevolutions,
        "stabilites": stabilites,
        "qualification": mia25_qualifier_relations(relations),
        "incertitude": True,
        "correlation_demontree": False,
        "causalite_demontree": False,
        "decision_automatique": False,
        "execution": False,
    }


def mia25_expliquer_relations(resultat):
    if not isinstance(resultat, dict):
        return {
            "nature": "resultat_invalide"
        }

    return {
        "nature": "analyse_relationnelle_descriptive",
        "qualification": resultat.get(
            "qualification",
            "indeterminee"
        ),
        "limites": [
            "relations_dependantes_des_donnees_fournies",
            "absence_de_correlation_statistique_demontree",
            "absence_de_causalite_demontree",
            "evolution_future_non_certaine",
        ],
    }


def mia25_verifier_relations(resultat):
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


def mia25_statut():
    return {
        "version": VERSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
    }
