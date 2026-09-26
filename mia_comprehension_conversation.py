"""
MIA — Couche de compréhension conversationnelle
Prototype V1

Cette couche est indépendante du moteur ALKAH-BRAIN V76.
Elle ne modifie aucune mémoire et n'exécute aucune action.
"""

def mia_comprendre_demande(question):
    q = question.lower().strip()

    # V6 : comparaison / décision — priorité avant les autres intentions
    if any(x in q for x in [
        "compare", "comparer", "comparaison",
        "compare deux", "compare les",
        "quelle solution", "quelle option",
        "aide-moi à choisir", "aide moi à choisir",
        "lequel choisir", "laquelle choisir"
    ]):
        return "comparaison"

    if any(x in q for x in [
        "prochaine étape", "prochaine etape",
        "quelle est la suite", "quelle est la prochaine",
        "que fait-on ensuite", "que faisons-nous ensuite",
        "et maintenant"
    ]):
        return "prochaine_etape"

    if any(x in q for x in [
        "prochaine étape", "prochaine etape",
        "quelle est la suite", "quelle est la prochaine",
        "que fait-on ensuite", "que faisons-nous ensuite",
        "et maintenant"
    ]):
        return "prochaine_etape"

    if any(x in q for x in [
        "prochaine étape", "prochaine etape",
        "quelle est la suite", "quelle est la prochaine",
        "que fait-on ensuite", "que faisons-nous ensuite",
        "et maintenant"
    ]):
        return "prochaine_etape"

    # V5/V3 : création de projet
    mots_projet = [
        "je veux créer", "je veux creer",
        "je voudrais créer", "je voudrais creer",
        "je souhaite créer", "je souhaite creer",
        "je veux développer", "je veux developper",
        "je voudrais développer", "je voudrais developper",
        "je souhaite développer", "je souhaite developper",
        "j'ai un projet", "j’ai un projet",
        "mon projet", "créer une application", "creer une application",
        "développer une application", "developper une application",
        "construire une application"
    ]

    if any(x in q for x in mots_projet):
        return "idee"

    # Reconnaissance explicite des demandes de création/construction de projet
    mots_projet = [
        "je veux créer", "je veux creer",
        "je voudrais créer", "je voudrais creer",
        "je souhaite créer", "je souhaite creer",
        "je veux développer", "je veux developper",
        "je voudrais développer", "je voudrais developper",
        "je souhaite développer", "je souhaite developper",
        "j'ai un projet", "j’ai un projet",
        "mon projet", "créer une application", "creer une application",
        "développer une application", "developper une application",
        "construire une application"
    ]

    if any(x in q for x in mots_projet):
        return "idee"

    if "améliore" in q or "ameliore" in q or \
       "améliorer" in q or "ameliorer" in q:
        return "amelioration"

    if "idée" in q or "idee" in q:
        return "idee"

    if "guide-moi" in q or "guide moi" in q:
        return "guide"

    if "compare" in q or "comparaison" in q or "comparer" in q:
        return "comparaison"

    if "construire" in q or \
       "réaliser mon projet" in q or \
       "realiser mon projet" in q:
        return "construction"

    if any(x in q for x in [
        "prochaine étape", "prochaine etape",
        "quelle est la suite", "quelle est la prochaine",
        "que fait-on ensuite", "que faisons-nous ensuite",
        "et maintenant"
    ]):
        return "prochaine_etape"

    if "apprends-moi" in q or \
       "apprends moi" in q or \
       "apprendre" in q:
        return "apprentissage"

    return "inconnue"


def mia_formuler_reaction(intention):
    reactions = {
        "idee": {
            "message": "Très bien. Décrivez-moi votre idée avec vos propres mots. Nous allons l'examiner ensemble.",
            "action": "recueillir_idee",
            "prochaine_etape": "demander_description"
        },
        "guide": {
            "message": "Bien sûr. Dites-moi ce que vous cherchez à réaliser et je vous guiderai étape par étape.",
            "action": "preparer_guidage",
            "prochaine_etape": "demander_objectif"
        },
        "comparaison": {
            "message": "Bien sûr. Donnez-moi les solutions que vous souhaitez comparer et nous les examinerons ensemble.",
            "action": "preparer_comparaison",
            "prochaine_etape": "demander_solutions"
        },
        "construction": {
            "message": "Avec plaisir. Dites-moi ce que vous souhaitez construire et nous allons le structurer progressivement.",
            "action": "preparer_construction",
            "prochaine_etape": "demander_projet"
        },
        "apprentissage": {
            "message": "Bien sûr. Quel sujet souhaitez-vous apprendre ? Je peux vous l'expliquer simplement.",
            "action": "preparer_apprentissage",
            "prochaine_etape": "demander_sujet"
        },
        "amelioration": {
            "message": "Avec plaisir. Présentez-moi votre idée et nous chercherons ensemble comment la rendre meilleure.",
            "action": "preparer_amelioration",
            "prochaine_etape": "demander_idee"
        },
        "prochaine_etape": {
            "message": "Très bien. Nous allons regarder ensemble la prochaine étape du projet.",
            "action": "proposer_prochaine_etape",
            "prochaine_etape": "analyser_suite"
        },
        "inconnue": {
            "message": "Je vous écoute. Dites-moi simplement ce que vous souhaitez faire, avec vos propres mots.",
            "action": "ecouter",
            "prochaine_etape": "attendre_demande"
        }
    }

    return reactions.get(
        intention,
        reactions["inconnue"]
    )
