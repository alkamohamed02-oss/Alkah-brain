def mia_raisonnement_causal_comparatif_v3(
    question=None,
    faits=None,
    options=None,
):
    """
    Raisonnement causal et comparatif V3 de MIA.

    Capacités :
    - identifier les faits disponibles ;
    - identifier les causes possibles ;
    - identifier les conséquences possibles ;
    - comparer des options ;
    - signaler les informations insuffisantes ;
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
            "causalite_valide": False,
            "comparaison_valide": False,
            "faits": [],
            "causes_possibles": [],
            "consequences_possibles": [],
            "options_comparees": [],
            "informations_manquantes": [],
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v3_bloque_question_invalide",
        }

    if faits is None:
        faits = []

    if options is None:
        options = []

    if not isinstance(faits, list):
        return {
            "raisonnement_valide": False,
            "causalite_valide": False,
            "comparaison_valide": False,
            "faits": [],
            "causes_possibles": [],
            "consequences_possibles": [],
            "options_comparees": [],
            "informations_manquantes": [],
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v3_bloque_faits_invalides",
        }

    if not isinstance(options, list):
        return {
            "raisonnement_valide": False,
            "causalite_valide": False,
            "comparaison_valide": False,
            "faits": [],
            "causes_possibles": [],
            "consequences_possibles": [],
            "options_comparees": [],
            "informations_manquantes": [],
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v3_bloque_options_invalides",
        }

    faits_valides = [
        f.strip()
        for f in faits
        if isinstance(f, str) and f.strip()
    ]

    options_valides = [
        o.strip()
        for o in options
        if isinstance(o, str) and o.strip()
    ]

    causes_possibles = []
    consequences_possibles = []

    # Detection semantique causale renforcee V3.1
    marqueurs_cause = [
        "cause", "causes", "provoque", "provoquent",
        "provoquer", "entraîne", "entraine",
        "entraînent", "entrainent", "raison",
        "parce que", "en raison de", "du fait de"
    ]

    marqueurs_effet = [
        "réduire", "reduit", "réduit",
        "diminuer", "diminue",
        "augmenter", "augmente",
        "fragiliser", "fragilise",
        "affecter", "affecte",
        "impacter", "impacte"
    ]

    marqueurs_consequence = [
        "conséquence", "consequence",
        "résultat", "resultat",
        "donc", "ainsi",
        "par conséquent", "par consequent",
        "entraînera", "entrainera"
    ]

    marqueurs_risque = [
        "risque", "danger", "incertitude",
        "problème", "probleme", "perte"
    ]

    for fait in faits_valides:
        texte_fait = fait.lower().strip()

        # 1. Cause explicite
        # Les relations "A provoque B" / "A entraîne B"
        # sont extraites séparément par le bloc 3bis.
        marqueurs_relation = [
            "provoque",
            "provoquent",
            "entraîne",
            "entraine",
            "entraînent",
            "entrainent",
        ]

        if (
            any(mot in texte_fait for mot in marqueurs_cause)
            and not any(mot in texte_fait for mot in marqueurs_relation)
        ):
            causes_possibles.append(fait)

        # 2. Relation causale implicite :
        # une formulation comme "peut réduire" décrit
        # un effet potentiel, pas une cause.
        if (
            any(mot in texte_fait for mot in marqueurs_effet)
            and (
                "peut" in texte_fait
                or "peuvent" in texte_fait
            )
        ):
            if fait not in consequences_possibles:
                consequences_possibles.append(fait)

        # 3. Consequence explicite
        if any(mot in texte_fait for mot in marqueurs_consequence):
            if fait not in consequences_possibles:
                consequences_possibles.append(fait)

        # 3bis. Extraction sémantique d'une relation causale explicite.
        # Exemple : "A provoque B" -> cause = A, consequence = B.
        for marqueur in [
            "provoque",
            "provoquent",
            "entraîne",
            "entraine",
            "entraînent",
            "entrainent",
        ]:
            index = texte_fait.find(marqueur)
            if index != -1:
                cause = fait[:index].strip()
                consequence = fait[index + len(marqueur):].strip()

                if cause and cause not in causes_possibles:
                    causes_possibles.append(cause)

                if consequence and consequence not in consequences_possibles:
                    consequences_possibles.append(consequence)

                break

        # 4. Consequence implicite
        if any(
            expression in texte_fait
            for expression in [
                "peut réduire",
                "peut diminuer",
                "peut fragiliser",
                "peut affecter",
                "peut impacter",
                "peuvent réduire",
                "peuvent diminuer",
                "peuvent fragiliser",
            ]
        ):
            if fait not in consequences_possibles:
                consequences_possibles.append(fait)

        # 5. Un risque constitue une consequence potentielle
        if any(mot in texte_fait for mot in marqueurs_risque):
            if fait not in consequences_possibles:
                consequences_possibles.append(fait)

    informations_manquantes = []

    if len(faits_valides) == 0:
        informations_manquantes.append(
            "Aucun fait exploitable n'a été fourni."
        )

    if len(faits_valides) < 2:
        informations_manquantes.append(
            "Davantage de faits seraient nécessaires "
            "pour renforcer le raisonnement causal."
        )

    if options_valides and len(options_valides) < 2:
        informations_manquantes.append(
            "Au moins deux options sont nécessaires "
            "pour effectuer une comparaison."
        )

    options_comparees = []

    if len(options_valides) >= 2:
        for numero, option in enumerate(options_valides, start=1):
            options_comparees.append({
                "numero": numero,
                "option": option,
                "statut": "comparee_sur_base_des_elements_fournis",
            })

    # Une causalité n'est valide que si au moins une cause
    # et une conséquence sont effectivement identifiées.
    causalite_valide = (
        len(causes_possibles) > 0
        and len(consequences_possibles) > 0
    )
    comparaison_valide = len(options_valides) >= 2

    if not faits_valides:
        confiance = 0.10
        conclusion = (
            "Conclusion impossible à établir de manière fiable : "
            "aucun fait exploitable n'est disponible."
        )

    elif len(faits_valides) < 2:
        confiance = 0.35
        conclusion = (
            "Conclusion très provisoire : les éléments disponibles "
            "sont insuffisants pour établir une relation causale fiable."
        )

    elif comparaison_valide:
        confiance = 0.75
        conclusion = (
            "Conclusion comparative provisoire : les options peuvent "
            "être comparées à partir des éléments fournis, mais "
            "aucune décision opérationnelle n'est prise automatiquement."
        )

    elif causalite_valide:
        confiance = 0.65
        conclusion = (
            "Conclusion causale provisoire : les éléments fournis "
            "permettent d'examiner des relations possibles entre "
            "causes et conséquences, sous réserve de leur exactitude."
        )
    else:
        confiance = 0.35
        conclusion = (
            "Aucune relation causale suffisamment établie n'a été "
            "identifiée à partir des éléments fournis."
        )

    return {
        "raisonnement_valide": True,
        "causalite_valide": causalite_valide,
        "comparaison_valide": comparaison_valide,
        "question": question.strip(),
        "faits": faits_valides,
        "causes_possibles": causes_possibles,
        "consequences_possibles": consequences_possibles,
        "options_comparees": options_comparees,
        "informations_manquantes": informations_manquantes,
        "conclusion": conclusion,
        "confiance": confiance,
        **securite,
        "statut": "raisonnement_causal_comparatif_v3_valide_mode_securise",
    }
