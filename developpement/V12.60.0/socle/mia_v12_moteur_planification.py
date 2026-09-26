"""
ALKAH-BRAIN — V12.60.0
MOTEUR DE PLANIFICATION

Mission :
Transformer une tâche structurée en plan proposé.

Principe :
PLANIFIER != EXECUTER

Toute proposition reste soumise à validation humaine.
"""

VERSION = "V12.60.0"
MISSION = "MOTEUR_DE_PLANIFICATION"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False
DECISION_AUTOMATIQUE = False
ECRITURE_PERSISTANTE = False
VALIDATION_HUMAINE_REQUISE = True

ETATS_PLAN = (
    "a_analyser",
    "analyse",
    "structure",
    "propose",
    "a_valider",
    "valide",
)


def mia60_normaliser_tache(tache):
    if tache is None:
        return ""

    if isinstance(tache, str):
        return tache.strip()

    if isinstance(tache, dict):
        return tache.copy()

    return str(tache).strip()


def mia60_creer_plan(tache):
    return {
        "version": VERSION,
        "mission": MISSION,
        "objectif": "",
        "analyse": [],
        "sous_objectifs": [],
        "etapes": [],
        "dependances": [],
        "contraintes": [],
        "risques": [],
        "alternatives": [],
        "criteres_reussite": [],
        "plan_propose": [],
        "validation": {
            "statut": "a_valider",
            "validation_humaine_requise": True,
        },
        "etat": "a_analyser",
        "execution": False,
    }


def mia60_definir_objectif(plan, objectif):
    plan["objectif"] = str(objectif).strip()
    return plan


def mia60_ajouter_analyse(plan, analyse):
    texte = str(analyse).strip()
    if texte:
        plan["analyse"].append(texte)
    return plan


def mia60_ajouter_sous_objectif(plan, sous_objectif):
    texte = str(sous_objectif).strip()
    if texte:
        plan["sous_objectifs"].append(texte)
    return plan


def mia60_ajouter_etape(plan, etape):
    texte = str(etape).strip()
    if texte:
        plan["etapes"].append(texte)
    return plan


def mia60_ajouter_dependance(plan, dependance):
    texte = str(dependance).strip()
    if texte:
        plan["dependances"].append(texte)
    return plan


def mia60_ajouter_contrainte(plan, contrainte):
    texte = str(contrainte).strip()
    if texte:
        plan["contraintes"].append(texte)
    return plan


def mia60_ajouter_risque(plan, risque):
    texte = str(risque).strip()
    if texte:
        plan["risques"].append(texte)
    return plan


def mia60_ajouter_alternative(plan, alternative):
    texte = str(alternative).strip()
    if texte:
        plan["alternatives"].append(texte)
    return plan


def mia60_ajouter_critere_reussite(plan, critere):
    texte = str(critere).strip()
    if texte:
        plan["criteres_reussite"].append(texte)
    return plan


def mia60_ajouter_plan_propose(plan, etape):
    texte = str(etape).strip()
    if texte:
        plan["plan_propose"].append(texte)
    return plan


def mia60_evaluer_completude(plan):
    champs = (
        "objectif",
        "analyse",
        "sous_objectifs",
        "etapes",
        "criteres_reussite",
        "plan_propose",
    )

    presents = sum(bool(plan.get(champ)) for champ in champs)
    total = len(champs)

    return {
        "complete": presents == total,
        "pourcentage": int((presents / total) * 100),
        "champs_presents": presents,
        "champs_total": total,
    }


def mia60_preparer_validation(plan):
    plan["etat"] = "a_valider"

    plan["validation"] = {
        "statut": "a_valider",
        "validation_humaine_requise": True,
        "commentaire": (
            "Plan proposé par MIA. "
            "Aucune exécution automatique. "
            "Validation humaine obligatoire."
        ),
    }

    return plan


def mia60_proposer_plan(tache):
    entree = mia60_normaliser_tache(tache)
    plan = mia60_creer_plan(entree)

    if isinstance(entree, dict):
        mia60_definir_objectif(
            plan,
            entree.get("objectif", "")
        )

        for item in entree.get("sous_objectifs", []):
            mia60_ajouter_sous_objectif(plan, item)

        for item in entree.get("etapes", []):
            mia60_ajouter_etape(plan, item)

        for item in entree.get("contraintes", []):
            mia60_ajouter_contrainte(plan, item)

        plan["etat"] = "propose"

    else:
        mia60_definir_objectif(plan, entree)
        plan["etat"] = "structure"

    return mia60_preparer_validation(plan)


def mia60_statut():
    return {
        "version": VERSION,
        "mission": MISSION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
        "decision_automatique": DECISION_AUTOMATIQUE,
        "ecriture_persistante": ECRITURE_PERSISTANTE,
        "validation_humaine_requise": VALIDATION_HUMAINE_REQUISE,
        "etats_plan": ETATS_PLAN,
    }
