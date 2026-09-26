from mia_raisonnement_multietapes import mia_raisonnement_multietapes
from mia_raisonnement_multietapes_v2 import mia_raisonnement_multietapes_v2
from mia_raisonnement_causal_comparatif_v3 import mia_raisonnement_causal_comparatif_v3
from mia_raisonnement_scenarios_v4 import mia_raisonnement_scenarios_v4
from mia_evaluation_decisionnelle_v5 import mia_evaluation_decisionnelle_v5


def _securite_resultat(resultat):
    """
    Vérifie que la brique de raisonnement reste en mode sécurisé.
    Aucun effet réel ou automatique n'est autorisé.
    """
    return all([
        resultat.get("execution_reelle") is False,
        resultat.get("execution_automatique") is False,
        resultat.get("action_automatique") is False,
        resultat.get("modification_memoire_automatique") is False,
        resultat.get("apprentissage_automatique") is False,
        resultat.get("memorisation_automatique") is False,
    ])


def mia_orchestrer_raisonnement_v1(
    question=None,
    contexte=None,
    faits=None,
    options=None,
    scenarios=None
):
    """
    Orchestrateur sécurisé du raisonnement MIA V1.

    Ordre :
    V1 → V2 → V3.2 → V4

    Cette fonction :
    - n'exécute aucune action réelle ;
    - ne modifie aucune mémoire ;
    - ne déclenche aucun apprentissage ;
    - ne prend aucune décision opérationnelle automatique.
    """

    if contexte is None:
        contexte = {}

    if faits is None:
        faits = []

    if options is None:
        options = []

    if scenarios is None:
        scenarios = []

    # ---------------------------------------------------------
    # V1 — Raisonnement multi-étapes
    # ---------------------------------------------------------
    v1 = mia_raisonnement_multietapes(
        question=question,
        contexte=contexte
    )

    # ---------------------------------------------------------
    # V2 — Raisonnement multi-étapes renforcé
    # ---------------------------------------------------------
    v2 = mia_raisonnement_multietapes_v2(
        question=question,
        faits=faits
    )

    # ---------------------------------------------------------
    # V3.2 — Causalité + comparaison
    # ---------------------------------------------------------
    v3 = mia_raisonnement_causal_comparatif_v3(
        question=question,
        faits=faits,
        options=options
    )

    # ---------------------------------------------------------
    # V4 — Analyse par scénarios
    # ---------------------------------------------------------
    v4 = mia_raisonnement_scenarios_v4(
        question=question,
        faits=faits,
        scenarios=scenarios
    )

    # ---------------------------------------------------------
    # Contrôle global de sécurité
    # ---------------------------------------------------------
    securite = all([
        _securite_resultat(v1),
        _securite_resultat(v2),
        _securite_resultat(v3),
        _securite_resultat(v4),
    ])

    # ---------------------------------------------------------
    # Validation globale
    # ---------------------------------------------------------
    raisonnement_valide = all([
        v1.get("raisonnement_valide") is True,
        v2.get("raisonnement_valide") is True,
        v3.get("raisonnement_valide") is True,
        v4.get("raisonnement_valide") is True,
        securite,
    ])

    # ---------------------------------------------------------
    # Confiance globale
    # ---------------------------------------------------------
    confiances = []

    for resultat in [v2, v3, v4]:
        valeur = resultat.get("confiance")
        if isinstance(valeur, (int, float)):
            confiances.append(float(valeur))

    if confiances:
        confiance_globale = sum(confiances) / len(confiances)
    else:
        confiance_globale = 0.0

    # ---------------------------------------------------------
    # V5 — Evaluation decisionnelle
    # ---------------------------------------------------------
    v5 = mia_evaluation_decisionnelle_v5(
        question=question,
        options=options,
        scenarios=scenarios,
        criteres=[],
        risques=v4.get("risques", []),
        contraintes=[],
        confiance=confiance_globale,
    )

    # ---------------------------------------------------------
    # Résultat unifié
    # ---------------------------------------------------------
    return {
        "orchestration_valide": raisonnement_valide,
        "raisonnement_valide": raisonnement_valide,

        "question": question,
        "contexte": contexte,
        "faits": faits,
        "options": options,
        "scenarios": scenarios,

        "v1_multietapes": v1,
        "v2_multietapes_renforce": v2,
        "v3_causal_comparatif": v3,
        "v4_scenarios": v4,
        "v5_evaluation_decisionnelle": v5,

        "causalite": {
            "valide": v3.get("causalite_valide"),
            "causes_possibles": v3.get("causes_possibles", []),
            "consequences_possibles": v3.get(
                "consequences_possibles", []
            ),
        },

        "comparaison": {
            "valide": v3.get("comparaison_valide"),
            "options": v3.get("options_comparees", []),
        },

        "scenarios_analyse": v4.get(
            "scenarios_analyses", []
        ),

        "risques": v4.get(
            "risques",
            []
        ),

        "informations_manquantes": list(dict.fromkeys(
            v2.get("informations_manquantes", [])
            + v3.get("informations_manquantes", [])
            + v4.get("informations_manquantes", [])
        )),

        "confiance": confiance_globale,

        "conclusions": {
            "v1": v1.get("conclusion"),
            "v2": v2.get("conclusion"),
            "v3": v3.get("conclusion"),
            "v4": v4.get("conclusion"),
        },

        "securite": {
            "valide": securite,
            "execution_reelle": False,
            "execution_automatique": False,
            "action_automatique": False,
            "modification_memoire_automatique": False,
            "apprentissage_automatique": False,
            "memorisation_automatique": False,
        },

        "statut": (
            "orchestration_raisonnement_v1_valide_mode_securise"
            if raisonnement_valide
            else "orchestration_raisonnement_v1_echec"
        ),
    }
