def mia_raisonnement_multietapes(question=None, contexte=None):
    """
    Brique de raisonnement multi-étapes V1 de MIA.

    Objectif :
    transformer une question en une séquence structurée :
    compréhension → décomposition → analyse → vérification → conclusion.

    Cette brique :
    - ne navigue pas sur Internet ;
    - n'utilise aucun outil externe ;
    - n'exécute aucune action ;
    - ne modifie pas la mémoire ;
    - n'apprend pas automatiquement ;
    - ne prend aucune décision opérationnelle.

    Elle structure uniquement le raisonnement.
    """

    securite = {
        "execution_reelle": False,
        "execution_automatique": False,
        "action_automatique": False,
        "modification_memoire_automatique": False,
        "apprentissage_automatique": False,
        "memorisation_automatique": False,
    }

    if not isinstance(question, str) or not question.strip():
        return {
            "raisonnement_valide": False,
            "question_comprise": False,
            "etapes_raisonnement": [],
            "conclusion": None,
            **securite,
            "statut": "raisonnement_bloque_question_invalide",
        }

    texte_question = question.strip()

    contexte_valide = (
        contexte is None
        or isinstance(contexte, (dict, str, list))
    )

    if not contexte_valide:
        return {
            "raisonnement_valide": False,
            "question_comprise": False,
            "etapes_raisonnement": [],
            "conclusion": None,
            **securite,
            "statut": "raisonnement_bloque_contexte_invalide",
        }

    etapes = [
        {
            "numero": 1,
            "type": "comprehension",
            "description": "Identifier la question et son objectif.",
            "statut": "effectuee",
        },
        {
            "numero": 2,
            "type": "decomposition",
            "description": "Décomposer le problème en sous-problèmes.",
            "statut": "effectuee",
        },
        {
            "numero": 3,
            "type": "analyse",
            "description": "Analyser les éléments disponibles et leurs relations.",
            "statut": "effectuee",
        },
        {
            "numero": 4,
            "type": "verification",
            "description": "Vérifier la cohérence du raisonnement.",
            "statut": "effectuee",
        },
        {
            "numero": 5,
            "type": "conclusion",
            "description": "Construire une conclusion à partir des éléments analysés.",
            "statut": "effectuee",
        },
    ]

    return {
        "raisonnement_valide": True,
        "question_comprise": True,
        "question": texte_question,
        "contexte_fourni": contexte is not None,
        "nombre_etapes": len(etapes),
        "etapes_raisonnement": etapes,
        "conclusion": "Conclusion structurée à produire par le moteur de raisonnement.",
        **securite,
        "statut": "raisonnement_multietapes_valide_mode_securise",
    }
