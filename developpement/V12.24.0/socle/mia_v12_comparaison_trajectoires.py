"""
ALKAH-BRAIN V12.24.0

Comparaison des trajectoires et analyse des écarts.

Module strictement descriptif et lecture seule.
"""

VERSION = "V12.24.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False


def mia24_normaliser_trajectoire(trajectoire):
    """
    Normalise une trajectoire sans modifier la source.
    """
    if trajectoire is None:
        return {}

    if not isinstance(trajectoire, dict):
        return {"valeur": trajectoire}

    return dict(trajectoire)


def mia24_extraire_indicateurs(trajectoire):
    """
    Extrait les indicateurs disponibles.
    """
    t = mia24_normaliser_trajectoire(trajectoire)

    indicateurs = t.get("indicateurs", {})

    if not isinstance(indicateurs, dict):
        indicateurs = {}

    return dict(indicateurs)


def mia24_alignement(trajectoire_a, trajectoire_b):
    """
    Identifie les éléments comparables entre deux trajectoires.
    """
    a = mia24_normaliser_trajectoire(trajectoire_a)
    b = mia24_normaliser_trajectoire(trajectoire_b)

    cles_a = set(a.keys())
    cles_b = set(b.keys())

    return {
        "communs": sorted(cles_a & cles_b),
        "uniquement_a": sorted(cles_a - cles_b),
        "uniquement_b": sorted(cles_b - cles_a),
    }


def mia24_comparer_valeurs(valeur_a, valeur_b):
    """
    Compare deux valeurs de manière descriptive.
    """
    if valeur_a == valeur_b:
        return "identique"

    if isinstance(valeur_a, (int, float)) and isinstance(valeur_b, (int, float)):
        if valeur_b > valeur_a:
            return "augmentation"
        if valeur_b < valeur_a:
            return "diminution"

    return "different"


def mia24_detecter_ecarts(trajectoire_a, trajectoire_b):
    """
    Détecte les écarts descriptifs.
    """
    a = mia24_normaliser_trajectoire(trajectoire_a)
    b = mia24_normaliser_trajectoire(trajectoire_b)

    communs = set(a.keys()) & set(b.keys())

    ecarts = {}

    for cle in sorted(communs):
        comparaison = mia24_comparer_valeurs(a[cle], b[cle])

        if comparaison != "identique":
            ecarts[cle] = {
                "valeur_a": a[cle],
                "valeur_b": b[cle],
                "nature": comparaison,
            }

    return ecarts


def mia24_detecter_convergences(trajectoire_a, trajectoire_b):
    """
    Détecte les éléments identiques ou convergents.
    """
    a = mia24_normaliser_trajectoire(trajectoire_a)
    b = mia24_normaliser_trajectoire(trajectoire_b)

    communs = set(a.keys()) & set(b.keys())

    convergences = []

    for cle in sorted(communs):
        if a[cle] == b[cle]:
            convergences.append(cle)

    return convergences


def mia24_detecter_divergences(trajectoire_a, trajectoire_b):
    """
    Détecte les éléments divergents.
    """
    ecarts = mia24_detecter_ecarts(
        trajectoire_a,
        trajectoire_b
    )

    return sorted(ecarts.keys())


def mia24_detecter_stabilites(trajectoire_a, trajectoire_b):
    """
    Détecte les éléments stables.
    """
    return mia24_detecter_convergences(
        trajectoire_a,
        trajectoire_b
    )


def mia24_qualifier_ecarts(ecarts):
    """
    Qualifie les écarts sans établir de causalité.
    """
    if not ecarts:
        return "aucun_ecart_detecte"

    return "ecarts_descriptifs_detectes"


def mia24_detecter_recurrences(historique_ecarts):
    """
    Détecte les écarts récurrents dans un historique.
    """
    if not isinstance(historique_ecarts, list):
        return []

    compte = {}

    for element in historique_ecarts:
        cle = str(element)
        compte[cle] = compte.get(cle, 0) + 1

    return sorted(
        [cle for cle, nombre in compte.items() if nombre > 1]
    )


def mia24_synthetiser_comparaison(trajectoire_a, trajectoire_b):
    """
    Produit une synthèse descriptive complète.
    """
    a = mia24_normaliser_trajectoire(trajectoire_a)
    b = mia24_normaliser_trajectoire(trajectoire_b)

    ecarts = mia24_detecter_ecarts(a, b)
    convergences = mia24_detecter_convergences(a, b)
    divergences = mia24_detecter_divergences(a, b)

    return {
        "version": VERSION,
        "comparaison": {
            "ecarts": ecarts,
            "convergences": convergences,
            "divergences": divergences,
        },
        "qualification": mia24_qualifier_ecarts(ecarts),
        "incertitude": True,
        "causalite_demontree": False,
        "decision_automatique": False,
        "execution": False,
    }


def mia24_expliquer_comparaison(resultat):
    """
    Produit une explication descriptive.
    """
    if not isinstance(resultat, dict):
        return {
            "nature": "resultat_invalide"
        }

    return {
        "nature": "comparaison_descriptive",
        "qualification": resultat.get(
            "qualification",
            "indeterminee"
        ),
        "limites": [
            "comparaison_dependante_des_donnees_fournies",
            "absence_de_causalite_demontree",
            "evolution_future_non_certaine",
        ],
    }


def mia24_verifier_comparaison(resultat):
    """
    Vérifie l'intégrité logique et les limites de sécurité.
    """
    return {
        "integrite": isinstance(resultat, dict),
        "autorisation_execution": False,
        "execution": False,
        "lecture_seule": True,
        "apprentissage_persistant": False,
        "decision_automatique": False,
        "causalite_demontree": False,
    }


def mia24_statut():
    """
    Retourne le statut de sécurité du module.
    """
    return {
        "version": VERSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
    }
