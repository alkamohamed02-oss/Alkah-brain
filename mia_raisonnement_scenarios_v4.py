def mia_raisonnement_scenarios_v4(
    question=None,
    faits=None,
    scenarios=None,
):
    """
    Raisonnement par scénarios V4 de MIA.

    Capacités :
    - analyser une situation ;
    - structurer plusieurs scénarios ;
    - identifier les conséquences possibles ;
    - identifier les risques ;
    - comparer les scénarios ;
    - signaler les informations manquantes ;
    - produire une conclusion prudente ;
    - produire un niveau de confiance.

    Sécurité :
    - aucune navigation Internet ;
    - aucun outil externe ;
    - aucune exécution réelle ;
    - aucune action automatique ;
    - aucune modification mémoire ;
    - aucun apprentissage automatique ;
    - aucune mémorisation automatique.
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
            "scenarios_valides": False,
            "faits": [],
            "scenarios_analyses": [],
            "consequences_possibles": [],
            "risques": [],
            "informations_manquantes": [],
            "comparaison_possible": False,
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v4_bloque_question_invalide",
        }

    if faits is None:
        faits = []

    if scenarios is None:
        scenarios = []

    if not isinstance(faits, list):
        return {
            "raisonnement_valide": False,
            "scenarios_valides": False,
            "faits": [],
            "scenarios_analyses": [],
            "consequences_possibles": [],
            "risques": [],
            "informations_manquantes": [],
            "comparaison_possible": False,
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v4_bloque_faits_invalides",
        }

    if not isinstance(scenarios, list):
        return {
            "raisonnement_valide": False,
            "scenarios_valides": False,
            "faits": [],
            "scenarios_analyses": [],
            "consequences_possibles": [],
            "risques": [],
            "informations_manquantes": [],
            "comparaison_possible": False,
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v4_bloque_scenarios_invalides",
        }

    faits_valides = [
        f.strip()
        for f in faits
        if isinstance(f, str) and f.strip()
    ]

    scenarios_valides = [
        s.strip()
        for s in scenarios
        if isinstance(s, str) and s.strip()
    ]

    informations_manquantes = []

    if not faits_valides:
        informations_manquantes.append(
            "Aucun fait exploitable n'a été fourni."
        )

    if len(faits_valides) < 2:
        informations_manquantes.append(
            "Davantage de faits seraient nécessaires "
            "pour renforcer l'analyse des scénarios."
        )

    if len(scenarios_valides) < 2:
        informations_manquantes.append(
            "Au moins deux scénarios sont nécessaires "
            "pour effectuer une comparaison."
        )

    scenarios_analyses = []

    for numero, scenario in enumerate(scenarios_valides, start=1):
        mots = [
            mot.strip(".,:;!?()[]{}'").lower()
            for mot in scenario.lower().replace(":", " ").split()
            if len(mot.strip(".,:;!?()[]{}'")) >= 4
        ]

        expressions = []
        for i in range(len(mots) - 1):
            expressions.append(mots[i] + " " + mots[i + 1])

        faits_pertinents = [
            fait for fait in faits_valides
            if any(expression in fait.lower() for expression in expressions)
        ]

        consequences = []
        risques_scenario = []

        for fait in faits_pertinents:
            texte_fait = fait.lower()

            if any(mot in texte_fait for mot in [
                "réduit",
                "reduit",
                "réduire",
                "reduire",
                "augmente",
                "augmenter",
                "utilise moins",
                "utiliser moins",
                "provoque",
                "provoquent",
                "entraîne",
                "entraine",
                "conséquence",
                "consequence",
                "résultat",
                "resultat",
                "donc",
            ]):
                consequences.append(fait)

            if any(mot in texte_fait for mot in [
                "risque",
                "danger",
                "incertitude",
                "perte",
            ]):
                risques_scenario.append(fait)

        if not consequences:
            consequences = [
                "Aucune conséquence spécifique ne peut être établie avec certitude à partir des faits fournis."
            ]

        if not risques_scenario:
            risques_scenario = [
                "Aucun risque spécifique ne peut être établi avec certitude à partir des faits fournis."
            ]

        scenarios_analyses.append({
            "numero": numero,
            "scenario": scenario,
            "faits_pertinents": faits_pertinents,
            "consequences": consequences,
            "risques": risques_scenario,
            "statut": "analyse_provisoire",
        })

    consequences_possibles = []

    for fait in faits_valides:
        texte = fait.lower()

        if any(mot in texte for mot in [
            "conséquence",
            "consequence",
            "résultat",
            "resultat",
            "donc",
            "entraîne",
            "entraine",
            "réduit",
            "reduit",
            "réduire",
            "reduire",
            "utilise moins",
            "utiliser moins",
        ]):
            consequences_possibles.append(fait)

    risques = []

    for fait in faits_valides:
        texte = fait.lower()

        if any(mot in texte for mot in [
            "risque",
            "danger",
            "incertitude",
            "problème",
            "probleme",
            "perte",
        ]):
            risques.append(fait)

    comparaison_possible = len(scenarios_valides) >= 2
    scenarios_valides_bool = comparaison_possible

    if not faits_valides:
        confiance = 0.10
        conclusion = (
            "Conclusion impossible à établir de manière fiable : "
            "aucun fait exploitable n'est disponible."
        )

    elif not comparaison_possible:
        confiance = 0.35
        conclusion = (
            "Conclusion très provisoire : plusieurs scénarios "
            "sont nécessaires pour permettre une comparaison fiable."
        )

    elif len(faits_valides) < 2:
        confiance = 0.45
        conclusion = (
            "Conclusion provisoire : plusieurs scénarios sont présents, "
            "mais les informations disponibles restent limitées."
        )

    else:
        confiance = 0.75
        conclusion = (
            "Conclusion par scénarios : les possibilités peuvent être "
            "comparées à partir des éléments fournis, mais les "
            "conséquences et risques doivent être vérifiés avant "
            "toute décision."
        )

    return {
        "raisonnement_valide": True,
        "scenarios_valides": scenarios_valides_bool,
        "question": question.strip(),
        "faits": faits_valides,
        "scenarios_analyses": scenarios_analyses,
        "consequences_possibles": consequences_possibles,
        "risques": risques,
        "informations_manquantes": informations_manquantes,
        "comparaison_possible": comparaison_possible,
        "conclusion": conclusion,
        "confiance": confiance,
        **securite,
        "statut": "raisonnement_scenarios_v4_valide_mode_securise",
    }


