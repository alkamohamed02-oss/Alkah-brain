"""
MIA V12.21 — Mémoire active
Première brique : détection explicite d'une demande de mémorisation.

Ce module ne modifie aucune base de données.
"""

import re


MOTIFS_MEMOIRE = (
    r"^\s*retiens(?:-moi)?\s+(?:cette\s+information|ceci|cela)\s*:\s*(.+)$",
    r"^\s*mémorise(?:-moi)?\s+(?:cette\s+information|ceci|cela)\s*:\s*(.+)$",
    r"^\s*souviens-toi\s+(?:de|que)\s+(.+)$",
)


def mia_v12_detecter_demande_memoire(question):
    """Détecte uniquement une demande explicite de mémorisation."""

    if not isinstance(question, str):
        return {
            "memoire_demandee": False,
            "contenu": None,
            "raison": "question_invalide",
        }

    texte = question.strip()

    for motif in MOTIFS_MEMOIRE:
        resultat = re.match(motif, texte, re.IGNORECASE)
        if resultat:
            contenu = resultat.group(1).strip()

            if contenu:
                return {
                    "memoire_demandee": True,
                    "contenu": contenu,
                    "raison": "demande_explicite",
                }

    return {
        "memoire_demandee": False,
        "contenu": None,
        "raison": "aucune_demande_explicite",
    }


def mia_v12_preparer_memoire(question):
    """Prépare une mémoire candidate sans l'enregistrer."""

    detection = mia_v12_detecter_demande_memoire(question)

    if not detection["memoire_demandee"]:
        return {
            "valide": False,
            "memoire": None,
            "detection": detection,
        }

    return {
        "valide": True,
        "memoire": {
            "type": "information_utilisateur",
            "question": question.strip(),
            "decision": "memoriser",
            "qualite": 100,
            "lecon": detection["contenu"],
            "utilisable": True,
        },
        "detection": detection,
    }
