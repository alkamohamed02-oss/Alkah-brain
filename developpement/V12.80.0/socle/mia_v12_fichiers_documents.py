"""
ALKAH-BRAIN
V12.80.0 — FICHIERS ET DOCUMENTS

Mission :
Rechercher, lire, analyser, comparer et classer des fichiers
et documents de manière contrôlée.

Principe :
LECTURE / ANALYSE != MODIFICATION

Aucune exécution de contenu de fichier.
Aucune écriture persistante.
Aucune suppression.
Validation humaine requise.
"""

VERSION = "V12.80.0"
MISSION = "FICHIERS_ET_DOCUMENTS"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False
DECISION_AUTOMATIQUE = False
ECRITURE_PERSISTANTE = False
VALIDATION_HUMAINE_REQUISE = True

TYPES_DOCUMENT = (
    "texte",
    "pdf",
    "document",
    "tableur",
    "presentation",
    "image",
    "archive",
    "inconnu",
)

ETATS_DOCUMENT = (
    "identifie",
    "lisible",
    "analyse",
    "compare",
    "classe",
    "a_valider",
)


def mia80_normaliser_document(document):
    """Normalise une description de document sans accéder au fichier."""
    if isinstance(document, str):
        return {
            "nom": document.strip(),
            "type": "inconnu",
            "description": "",
            "etat": "identifie",
        }

    if isinstance(document, dict):
        resultat = dict(document)
        resultat.setdefault("nom", "")
        resultat.setdefault("type", "inconnu")
        resultat.setdefault("description", "")
        resultat.setdefault("etat", "identifie")
        return resultat

    return {
        "nom": "",
        "type": "inconnu",
        "description": "",
        "etat": "identifie",
    }


def mia80_identifier_type(document):
    """Identifie le type à partir du nom ou de l'extension."""
    doc = mia80_normaliser_document(document)
    nom = str(doc.get("nom", "")).lower()

    extensions = {
        ".txt": "texte",
        ".md": "texte",
        ".py": "texte",
        ".csv": "tableur",
        ".xlsx": "tableur",
        ".xls": "tableur",
        ".pdf": "pdf",
        ".doc": "document",
        ".docx": "document",
        ".odt": "document",
        ".ppt": "presentation",
        ".pptx": "presentation",
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".webp": "image",
        ".zip": "archive",
        ".tar": "archive",
        ".gz": "archive",
    }

    for extension, type_document in extensions.items():
        if nom.endswith(extension):
            return type_document

    return doc.get("type", "inconnu")


def mia80_rechercher_documents(documents, terme=""):
    """Recherche des documents dans une collection déjà fournie."""
    terme = str(terme or "").strip().lower()
    resultat = []

    for element in documents or []:
        doc = mia80_normaliser_document(element)

        texte = " ".join(
            str(doc.get(cle, ""))
            for cle in ("nom", "description", "type")
        ).lower()

        if not terme or terme in texte:
            resultat.append(doc)

    return resultat


def mia80_lire_document(document, contenu=None):
    """
    Prépare une représentation de lecture.
    Le module ne lit pas lui-même le système de fichiers.
    Le contenu doit être fourni explicitement.
    """
    doc = mia80_normaliser_document(document)

    if contenu is None:
        return {
            "document": doc,
            "lecture": "contenu_non_fourni",
            "validation_humaine": True,
        }

    return {
        "document": doc,
        "contenu": str(contenu),
        "etat": "lisible",
        "validation_humaine": True,
    }


def mia80_extraire_elements(document, contenu=None):
    """Extrait des éléments textuels simples à partir d'un contenu fourni."""
    lecture = mia80_lire_document(document, contenu)

    if "contenu" not in lecture:
        return {
            "elements": [],
            "etat": "contenu_non_fourni",
            "validation_humaine": True,
        }

    texte = lecture["contenu"]
    lignes = [ligne.strip() for ligne in texte.splitlines() if ligne.strip()]

    return {
        "elements": lignes,
        "nombre_elements": len(lignes),
        "etat": "analyse",
        "validation_humaine": True,
    }


def mia80_analyser_document(document, contenu=None):
    """Produit une analyse descriptive sans modifier le document."""
    doc = mia80_normaliser_document(document)
    extraction = mia80_extraire_elements(doc, contenu)

    elements = extraction.get("elements", [])

    return {
        "document": doc,
        "type": mia80_identifier_type(doc),
        "nombre_elements": len(elements),
        "contenu_present": bool(elements),
        "analyse": "descriptive",
        "modification": False,
        "etat": "analyse",
        "validation_humaine": True,
    }


def mia80_comparer_documents(document_a, document_b):
    """Compare les métadonnées de deux documents fournis."""
    a = mia80_normaliser_document(document_a)
    b = mia80_normaliser_document(document_b)

    champs = ("nom", "type", "description", "etat")
    differences = {}
    similitudes = {}

    for champ in champs:
        valeur_a = a.get(champ)
        valeur_b = b.get(champ)

        if valeur_a == valeur_b:
            similitudes[champ] = valeur_a
        else:
            differences[champ] = {
                "document_a": valeur_a,
                "document_b": valeur_b,
            }

    return {
        "document_a": a,
        "document_b": b,
        "similitudes": similitudes,
        "differences": differences,
        "etat": "compare",
        "modification": False,
        "validation_humaine": True,
    }


def mia80_classer_document(document, categorie=None):
    """Propose une catégorie sans déplacer ni modifier le fichier."""
    doc = mia80_normaliser_document(document)

    if categorie:
        proposition = str(categorie).strip()
    else:
        proposition = mia80_identifier_type(doc)

    return {
        "document": doc,
        "categorie_proposee": proposition,
        "action": "proposition",
        "deplacement": False,
        "modification": False,
        "etat": "classe",
        "validation_humaine": True,
    }


def mia80_detecter_contenu_sensible(contenu=""):
    """Signale certains termes sensibles sans interprétation automatique."""
    texte = str(contenu).lower()

    termes = (
        "mot de passe",
        "password",
        "secret",
        "clé privée",
        "private key",
        "numero de carte",
        "numéro de carte",
        "iban",
        "document d'identité",
    )

    detectes = [terme for terme in termes if terme in texte]

    return {
        "sensible_potentiel": bool(detectes),
        "indicateurs": detectes,
        "decision_automatique": False,
        "validation_humaine": True,
    }


def mia80_evaluer_lisibilite(document, contenu=None):
    """Évalue uniquement si un contenu fourni est exploitable."""
    doc = mia80_normaliser_document(document)

    if contenu is None:
        return {
            "lisible": False,
            "raison": "contenu_non_fourni",
            "document": doc,
        }

    texte = str(contenu)

    return {
        "lisible": bool(texte.strip()),
        "taille_caracteres": len(texte),
        "document": doc,
        "etat": "lisible" if texte.strip() else "identifie",
    }


def mia80_preparer_synthese(document, contenu=None):
    """Prépare une synthèse descriptive sans modifier la source."""
    analyse = mia80_analyser_document(document, contenu)
    sensibilite = mia80_detecter_contenu_sensible(contenu or "")

    return {
        "document": analyse["document"],
        "type": analyse["type"],
        "nombre_elements": analyse["nombre_elements"],
        "contenu_present": analyse["contenu_present"],
        "sensibilite_potentielle": sensibilite["sensible_potentiel"],
        "synthese": "synthese_descriptive_a_valider",
        "modification_source": False,
        "validation_humaine": True,
    }


def mia80_proposer_action(document, action):
    """
    Propose une action documentaire mais ne l'exécute jamais.
    """
    actions_autorisees_en_proposition = (
        "lire",
        "analyser",
        "comparer",
        "classer",
        "synthétiser",
        "synthétiser",
        "préparer",
    )

    action_normalisee = str(action or "").strip().lower()

    return {
        "document": mia80_normaliser_document(document),
        "action_proposee": action_normalisee,
        "action_dans_ce_socle": (
            action_normalisee in actions_autorisees_en_proposition
        ),
        "execution": False,
        "ecriture": False,
        "validation_humaine": True,
    }


def mia80_expliquer_traitement(document, action):
    """Explique pourquoi un traitement documentaire est proposé."""
    doc = mia80_normaliser_document(document)
    type_document = mia80_identifier_type(doc)

    return {
        "document": doc,
        "type": type_document,
        "action": str(action or ""),
        "raison": (
            "traitement documentaire descriptif proposé "
            "sans modification de la source"
        ),
        "risque": "controle",
        "execution": False,
        "validation_humaine": True,
    }


def mia80_statut():
    """Retourne le statut de sécurité et de mission."""
    return {
        "version": VERSION,
        "mission": MISSION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
        "decision_automatique": DECISION_AUTOMATIQUE,
        "ecriture_persistante": ECRITURE_PERSISTANTE,
        "validation_humaine_requise": VALIDATION_HUMAINE_REQUISE,
        "principe": "LECTURE_ANALYSE != MODIFICATION",
    }
