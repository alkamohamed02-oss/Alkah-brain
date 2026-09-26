"""
ALKAH-BRAIN — V12.21.0
Rapprochement intelligent de mémoire.

Rôle :
- comparer une question avec des mémoires déjà existantes ;
- privilégier les identifiants exacts ;
- calculer une correspondance lexicale contrôlée ;
- retourner une décision explicable ;
- NE PAS écrire en base ;
- NE PAS modifier V76.

Ce module est volontairement isolé.
"""

import re


MOTS_VIDES = {
    "le", "la", "les", "un", "une", "des",
    "de", "du", "et", "est", "dans", "avec",
    "pour", "mon", "ma", "mes", "son", "sa",
    "ce", "cette", "ces", "qui", "que", "en",
    "sur", "par", "aux", "au", "tu", "sais", "comment"
}


def mia_v12_normaliser_texte(texte):
    """Normalise un texte pour comparaison."""
    if not isinstance(texte, str):
        return ""

    texte = texte.lower()
    texte = texte.replace("-", " ")
    texte = texte.replace("_", " ")

    texte = re.sub(r"[^\w\s]", " ", texte, flags=re.UNICODE)
    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


def mia_v12_mots_significatifs(texte):
    """Extrait les mots suffisamment significatifs."""
    normalise = mia_v12_normaliser_texte(texte)

    mots = set()

    for mot in normalise.split():
        if (len(mot) >= 3 or (len(mot) >= 2 and any(c.isalpha() for c in mot) and any(c.isdigit() for c in mot))) and mot not in MOTS_VIDES:
            mots.add(mot)

    return mots


def mia_v12_extraire_identifiants(texte):
    """
    Extrait les identifiants structurés du type :
    V1221-TEST-REEL
    ALPHA-47
    TEST_123
    """
    if not isinstance(texte, str):
        return set()

    motif = r"\b[A-Z]{1,10}[-_]?\d+(?:[-_][A-Z0-9]+)*\b"

    return {
        identifiant.upper()
        for identifiant in re.findall(motif, texte.upper())
    }


def mia_v12_evaluer_rapprochement(question, memoire):
    """
    Évalue une mémoire par rapport à une question.

    Retourne uniquement une analyse.
    Aucune modification externe.
    """

    if not isinstance(question, str):
        question = ""

    if not isinstance(memoire, dict):
        memoire = {}

    question_memoire = str(memoire.get("question", "") or "")
    lecon = str(memoire.get("lecon", "") or "")

    texte_memoire = (
        question_memoire + " " + lecon
    ).strip()

    identifiants_question = mia_v12_extraire_identifiants(question)
    identifiants_memoire = mia_v12_extraire_identifiants(
        texte_memoire
    )

    identifiants_communs = (
        identifiants_question &
        identifiants_memoire
    )

    mots_question = mia_v12_mots_significatifs(question)
    mots_memoire = mia_v12_mots_significatifs(question_memoire)

    mots_communs = mots_question & mots_memoire

    correspondance_mots = len(mots_communs)
    identifiant_exact = any("-" in x or "_" in x for x in identifiants_communs)

    if identifiant_exact:
        niveau = "fort"
        score = 100
        decision = "correspondance_identifiant_exact"

    elif mots_question == mots_memoire and mots_question:
        niveau = "fort"
        score = 80
        decision = "correspondance_lexicale_forte"

    elif correspondance_mots >= 5:
        niveau = "fort"
        score = 80
        decision = "correspondance_lexicale_forte"

    elif correspondance_mots >= 3:
        niveau = "moyen"
        score = 60
        decision = "correspondance_lexicale_moyenne"

    elif correspondance_mots >= 1:
        niveau = "faible"
        score = 30
        decision = "correspondance_lexicale_faible"

    else:
        niveau = "aucune"
        score = 0
        decision = "aucune_correspondance"

    return {
        "score": score,
        "niveau": niveau,
        "decision": decision,
        "identifiant_exact": identifiant_exact,
        "identifiants_communs": sorted(identifiants_communs),
        "correspondance_mots": correspondance_mots,
        "mots_communs": sorted(mots_communs),
        "question": question,
        "memoire_id": memoire.get("id"),
        "memoire_question": question_memoire,
        "memoire_lecon": lecon,
    }


def mia_v12_rapprocher_memoires(question, memoires):
    """
    Analyse plusieurs mémoires et retourne la meilleure correspondance.

    Aucun seuil V76 n'est modifié.
    Aucune mémoire n'est écrite.
    """

    if not isinstance(memoires, list):
        memoires = []

    analyses = []

    for memoire in memoires:
        analyse = mia_v12_evaluer_rapprochement(
            question,
            memoire
        )

        analyses.append(analyse)

    analyses.sort(
        key=lambda element: (
            element.get("identifiant_exact", False),
            element.get("score", 0),
            element.get("correspondance_mots", 0)
        ),
        reverse=True
    )

    meilleure = analyses[0] if analyses else None

    if meilleure is None:
        return {
            "trouve": False,
            "statut": "aucune_memoire",
            "meilleure": None,
            "candidats": []
        }

    if meilleure["score"] == 0:
        return {
            "trouve": False,
            "statut": "aucune_correspondance",
            "meilleure": meilleure,
            "candidats": analyses
        }

    return {
        "trouve": True,
        "statut": "correspondance_trouvee",
        "meilleure": meilleure,
        "candidats": analyses
    }
