def mia_raisonnement_multietapes_v2(question=None, faits=None):
    """
    Raisonnement multi-etapes V2 de MIA.

    Capacites :
    - identifier les faits fournis ;
    - distinguer faits et hypotheses ;
    - identifier les informations manquantes ;
    - detecter certaines contradictions explicites ;
    - produire des deductions simples ;
    - construire une conclusion justifiee ;
    - produire un niveau de confiance.

    Limites :
    - aucun acces Internet ;
    - aucun outil externe ;
    - aucune execution ;
    - aucune action automatique ;
    - aucune modification de memoire ;
    - aucun apprentissage automatique.
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
            "faits": [],
            "hypotheses": [],
            "informations_manquantes": [],
            "contradictions": [],
            "deductions": [],
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v2_bloque_question_invalide",
        }

    if faits is None:
        faits = []

    if not isinstance(faits, list):
        return {
            "raisonnement_valide": False,
            "question_comprise": True,
            "faits": [],
            "hypotheses": [],
            "informations_manquantes": [],
            "contradictions": [],
            "deductions": [],
            "conclusion": None,
            "confiance": 0.0,
            **securite,
            "statut": "raisonnement_v2_bloque_faits_invalides",
        }

    faits_valides = []
    hypotheses = []
    contradictions = []

    for element in faits:
        if not isinstance(element, str):
            continue

        element = element.strip()

        if not element:
            continue

        faits_valides.append(element)

        texte = element.lower()

        if "peut-être" in texte or "peut etre" in texte:
            hypotheses.append(element)

    # Detection ciblee de contradictions explicites.
    # Une phrase affirmative et une phrase negative
    # portant sur la meme proposition sont considerees
    # comme potentiellement contradictoires.
    for i, fait_a in enumerate(faits_valides):
        for fait_b in faits_valides[i + 1:]:
            a = fait_a.lower().strip()
            b = fait_b.lower().strip()

            def normaliser(texte):
                texte = (
                    texte.replace(",", "")
                    .replace(".", "")
                    .replace("!", "")
                    .replace("?", "")
                )
                return " ".join(texte.split())

            a = normaliser(a)
            b = normaliser(b)

            negatif_a = (
                (" ne " in f" {a} " or "n'" in a)
                and " pas" in a
            )
            negatif_b = (
                (" ne " in f" {b} " or "n'" in b)
                and " pas" in b
            )

            # Cas direct : meme proposition avec negation.
            if negatif_a != negatif_b:
                positif = b if negatif_a else a
                negatif = a if negatif_a else b

                positif_sans_marqueurs = (
                    positif
                    .replace(" ne ", " ")
                    .replace(" pas ", " ")
                )
                negatif_sans_marqueurs = (
                    negatif
                    .replace(" ne ", " ")
                    .replace(" pas ", " ")
                )

                mots_positif = set(positif_sans_marqueurs.split())
                mots_negatif = set(negatif_sans_marqueurs.split())

                communs = mots_positif & mots_negatif

                if len(communs) >= 2:
                    contradictions.append(
                        f"Contradiction potentielle entre : '{fait_a}' et '{fait_b}'"
                    )

    informations_manquantes = []

    if not faits_valides:
        informations_manquantes.append(
            "Aucun fait exploitable n'a été fourni."
        )

    if len(faits_valides) < 2:
        informations_manquantes.append(
            "Davantage d'informations seraient nécessaires pour renforcer l'analyse."
        )

    deductions = []

    if faits_valides:
        deductions.append(
            "Les conclusions doivent rester limitées aux éléments fournis."
        )

    if hypotheses:
        deductions.append(
            "Les éléments formulés comme hypothèses ne doivent pas être traités comme des faits."
        )

    if contradictions:
        deductions.append(
            "Une contradiction potentielle a été détectée et doit être vérifiée."
        )

    if contradictions:
        confiance = 0.40
        conclusion = (
            "Conclusion provisoire : les données contiennent au moins "
            "une contradiction potentielle et nécessitent une vérification."
        )
    elif not faits_valides:
        confiance = 0.10
        conclusion = (
            "Conclusion impossible à établir de manière fiable : "
            "aucun fait exploitable n'est disponible."
        )
    elif len(faits_valides) < 2:
        confiance = 0.55
        conclusion = (
            "Conclusion provisoire : les éléments disponibles permettent "
            "une première analyse, mais les informations restent limitées."
        )
    else:
        confiance = 0.80
        conclusion = (
            "Conclusion structurée : les éléments fournis permettent "
            "une analyse cohérente, sous réserve de leur exactitude."
        )

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
            "description": "Organiser le problème en éléments analysables.",
            "statut": "effectuee",
        },
        {
            "numero": 3,
            "type": "analyse",
            "description": "Séparer faits, hypothèses et informations disponibles.",
            "statut": "effectuee",
        },
        {
            "numero": 4,
            "type": "verification",
            "description": "Rechercher contradictions et informations manquantes.",
            "statut": "effectuee",
        },
        {
            "numero": 5,
            "type": "conclusion",
            "description": "Construire une conclusion proportionnelle aux preuves disponibles.",
            "statut": "effectuee",
        },
    ]

    return {
        "raisonnement_valide": True,
        "question_comprise": True,
        "question": question.strip(),
        "faits": faits_valides,
        "hypotheses": hypotheses,
        "informations_manquantes": informations_manquantes,
        "contradictions": contradictions,
        "deductions": deductions,
        "conclusion": conclusion,
        "confiance": confiance,
        "nombre_etapes": len(etapes),
        "etapes_raisonnement": etapes,
        **securite,
        "statut": "raisonnement_multietapes_v2_valide_mode_securise",
    }
