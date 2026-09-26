"""MIA V5 - Evaluation decisionnelle structuree.
Aucune execution, action, memorisation ou apprentissage automatique.
"""

SECURITE_FALSE = {
    "execution_reelle": False,
    "execution_automatique": False,
    "action_automatique": False,
    "modification_memoire_automatique": False,
    "apprentissage_automatique": False,
    "memorisation_automatique": False,
}

def mia_evaluation_decisionnelle_v5(
    question=None,
    options=None,
    scenarios=None,
    criteres=None,
    risques=None,
    contraintes=None,
    confiance=0.0,
):
    if not isinstance(question, str) or not question.strip():
        return {
            "question": question,
            "evaluation_valide": False,
            "recommandation": None,
            "validation_humaine_requise": True,
            "securite": SECURITE_FALSE.copy(),
            "statut": "evaluation_decisionnelle_v5_echec",
        }

    options = options if isinstance(options, list) else []
    scenarios = scenarios if isinstance(scenarios, list) else []
    criteres = criteres if isinstance(criteres, list) else []
    risques = risques if isinstance(risques, list) else []
    contraintes = contraintes if isinstance(contraintes, list) else []

    elements = options if options else scenarios

    if not elements:
        return {
            "question": question,
            "evaluation_valide": False,
            "recommandation": None,
            "validation_humaine_requise": True,
            "criteres": criteres,
            "risques": risques,
            "contraintes": contraintes,
            "securite": SECURITE_FALSE.copy(),
            "statut": "evaluation_decisionnelle_v5_informations_insuffisantes",
        }

    evaluations = []
    for element in elements:
        texte = str(element).lower()
        score = 0
        points_forts = []
        points_faibles = []

        for critere in criteres:
            c = str(critere).lower()
            if c and c in texte:
                score += 2
                points_forts.append(str(critere))

        for risque in risques:
            r = str(risque).lower()
            if r and r in texte:
                score -= 2
                points_faibles.append(str(risque))

        for contrainte in contraintes:
            c = str(contrainte).lower()
            if c and c in texte:
                score -= 1
                points_faibles.append(str(contrainte))

        evaluations.append({
            "element": element,
            "score": score,
            "points_forts": points_forts,
            "points_faibles": points_faibles,
        })

    score_max = max(x["score"] for x in evaluations)
    gagnants = [x for x in evaluations if x["score"] == score_max]

    if score_max <= 0 or len(gagnants) != 1:
        recommandation = None
        statut = "evaluation_decisionnelle_v5_validation_humaine_necessaire"
    else:
        recommandation = gagnants[0]["element"]
        statut = "evaluation_decisionnelle_v5_prete_validation_humaine"

    return {
        "question": question,
        "evaluation_valide": True,
        "elements_evalues": elements,
        "evaluations": evaluations,
        "criteres": criteres,
        "risques": risques,
        "contraintes": contraintes,
        "confiance": float(confiance) if isinstance(confiance, (int, float)) else 0.0,
        "recommandation": recommandation,
        "recommandation_score": score_max,
        "validation_humaine_requise": True,
        "decision_humaine": True,
        "securite": SECURITE_FALSE.copy(),
        "statut": statut,
    }
