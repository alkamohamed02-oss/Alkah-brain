"""
ALKAH-BRAIN V12.23.0

PROJECTION DES TRAJECTOIRES
ET ANALYSE DE SCENARIOS

Version descriptive et conditionnelle.

Garanties :
- lecture seule ;
- aucune exécution autonome ;
- aucune décision autonome ;
- aucun apprentissage persistant ;
- aucune modification des versions antérieures ;
- aucune prédiction certaine ;
- aucune causalité inventée.
"""

VERSION = "V12.23.0"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False


SCENARIOS_STANDARD = (
    "progression",
    "stagnation",
    "regression",
    "mixte",
)


def mia23_normaliser_analyse(analyse):
    """
    Normalise une analyse de trajectoire.

    La source n'est jamais modifiée.
    """
    if analyse is None:
        return {}

    if isinstance(analyse, dict):
        return dict(analyse)

    return {
        "valeur": analyse
    }


def mia23_extraire_indicateurs(analyse):
    """
    Extrait les indicateurs disponibles sans les modifier.
    """
    data = mia23_normaliser_analyse(analyse)

    indicateurs = data.get("indicateurs", {})

    if not isinstance(indicateurs, dict):
        indicateurs = {}

    return dict(indicateurs)


def mia23_identifier_tendance(analyse):
    """
    Identifie la tendance descriptive issue de l'analyse.
    """
    data = mia23_normaliser_analyse(analyse)

    tendance = data.get("tendance")

    if tendance is None:
        tendance = data.get("direction")

    if tendance is None:
        tendance = "indeterminee"

    return {
        "tendance": tendance,
        "descriptive": True,
        "certitude": False,
    }


def mia23_identifier_conditions(analyse):
    """
    Identifie les conditions disponibles pour une projection.
    """
    data = mia23_normaliser_analyse(analyse)

    conditions = data.get("conditions", [])

    if conditions is None:
        conditions = []

    if not isinstance(conditions, (list, tuple)):
        conditions = [conditions]

    return list(conditions)


def mia23_identifier_hypotheses(analyse):
    """
    Identifie les hypothèses nécessaires.

    Aucune hypothèse n'est présentée comme un fait.
    """
    data = mia23_normaliser_analyse(analyse)

    hypotheses = data.get("hypotheses", [])

    if hypotheses is None:
        hypotheses = []

    if not isinstance(hypotheses, (list, tuple)):
        hypotheses = [hypotheses]

    return list(hypotheses)


def mia23_detecter_stabilite(analyse):
    """
    Recherche des éléments décrits comme stables.
    """
    data = mia23_normaliser_analyse(analyse)

    stables = data.get("stables", [])

    if stables is None:
        stables = []

    if not isinstance(stables, (list, tuple)):
        stables = [stables]

    return list(stables)


def mia23_construire_projection(analyse):
    """
    Construit une projection descriptive conditionnelle.

    Il ne s'agit pas d'une prédiction certaine.
    """
    tendance = mia23_identifier_tendance(analyse)
    indicateurs = mia23_extraire_indicateurs(analyse)
    conditions = mia23_identifier_conditions(analyse)
    hypotheses = mia23_identifier_hypotheses(analyse)
    stables = mia23_detecter_stabilite(analyse)

    return {
        "tendance_source": tendance,
        "indicateurs": indicateurs,
        "conditions": conditions,
        "hypotheses": hypotheses,
        "elements_stables": stables,
        "projection_certaine": False,
        "type": "descriptive_conditionnelle",
    }


def mia23_generer_scenarios(analyse):
    """
    Génère les quatre scénarios standards.

    Aucun scénario n'est automatiquement choisi.
    """
    projection = mia23_construire_projection(analyse)

    scenarios = []

    for nom in SCENARIOS_STANDARD:
        scenarios.append({
            "nom": nom,
            "type": "conditionnel",
            "tendance_source": projection["tendance_source"],
            "conditions": list(projection["conditions"]),
            "hypotheses": list(projection["hypotheses"]),
            "indicateurs": dict(projection["indicateurs"]),
            "projection_certaine": False,
        })

    return {
        "scenarios": scenarios,
        "scenario_selectionne": None,
        "decision_automatique": False,
    }


def mia23_evaluer_plausibilite_descriptive(scenario):
    """
    Produit une qualification descriptive minimale.

    Elle ne constitue pas une probabilité mathématique.
    """
    if not isinstance(scenario, dict):
        return {
            "niveau": "indetermine",
            "nature": "descriptive",
        }

    nom = scenario.get("nom", "indetermine")

    return {
        "scenario": nom,
        "niveau": "a_qualifier",
        "nature": "descriptive",
        "probabilite_mathématique": False,
    }


def mia23_qualifier_incertitude(scenarios):
    """
    Rend l'incertitude explicite pour chaque scénario.
    """
    if not isinstance(scenarios, dict):
        scenarios = {}

    resultat = dict(scenarios)

    liste = resultat.get("scenarios", [])

    nouvelles = []

    for scenario in liste:
        item = dict(scenario)

        item["incertitude"] = {
            "niveau": "explicite",
            "hypotheses_requises": True,
            "projection_certaine": False,
            "probabilite_mathématique": False,
        }

        nouvelles.append(item)

    resultat["scenarios"] = nouvelles

    return resultat


def mia23_identifier_limites(analyse):
    """
    Identifie les limites explicites de la projection.
    """
    data = mia23_normaliser_analyse(analyse)

    limites = data.get("limites", [])

    if limites is None:
        limites = []

    if not isinstance(limites, (list, tuple)):
        limites = [limites]

    limites = list(limites)

    limites_standard = [
        "donnees_historiques_limitees",
        "evolution_future_non_certaine",
        "absence_de_causalite_demontree",
    ]

    for limite in limites_standard:
        if limite not in limites:
            limites.append(limite)

    return limites


def mia23_synthetiser_projection(analyse):
    """
    Produit la synthèse complète de projection.
    """
    projection = mia23_construire_projection(analyse)
    scenarios = mia23_generer_scenarios(analyse)
    scenarios = mia23_qualifier_incertitude(scenarios)

    return {
        "version": VERSION,
        "projection": projection,
        "scenarios": scenarios["scenarios"],
        "scenario_selectionne": None,
        "limites": mia23_identifier_limites(analyse),
        "execution": False,
        "lecture_seule": True,
        "apprentissage_persistant": False,
        "projection_certaine": False,
        "decision_automatique": False,
    }


def mia23_expliquer_projection(analyse):
    """
    Produit une explication descriptive de la projection.
    """
    resultat = mia23_synthetiser_projection(analyse)

    return {
        "version": VERSION,
        "explication": {
            "nature": "projection_conditionnelle",
            "base": "trajectoire_observee",
            "hypotheses": resultat["projection"]["hypotheses"],
            "conditions": resultat["projection"]["conditions"],
            "limites": resultat["limites"],
            "certitude": False,
        },
        "execution": False,
    }


def mia23_verifier_projection(resultat):
    """
    Vérifie les garanties fondamentales de V12.23.0.
    """
    if not isinstance(resultat, dict):
        return {
            "integrite": False,
            "raison": "resultat_invalide",
        }

    return {
        "version": VERSION,
        "integrite": True,
        "execution": False,
        "lecture_seule": True,
        "apprentissage_persistant": False,
        "projection_certaine": False,
        "decision_automatique": False,
        "scenario_selectionne": None,
    }


def mia23_statut():
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
