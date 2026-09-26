# -*- coding: utf-8 -*-

VERSION = "V12.50.0"
MISSION = "MOTEUR_DE_TACHES"

AUTORISATION_EXECUTION = False
EXECUTION = False
LECTURE_SEULE = True
APPRENTISSAGE_PERSISTANT = False
DECISION_AUTOMATIQUE = False
ECRITURE_PERSISTANTE = False
VALIDATION_HUMAINE_REQUISE = True

ETATS_TACHE = (
    "a_analyser",
    "structuree",
    "a_valider",
    "validee",
    "en_cours",
    "bloquee",
    "terminee",
    "abandonnee",
)

PRIORITES = (
    "critique",
    "haute",
    "normale",
    "basse",
)


def mia50_normaliser_demande(demande):
    texte = str(demande or "").strip()

    return {
        "demande_originale": texte,
        "demande_normalisee": " ".join(texte.split()),
        "longueur": len(texte),
        "valide": bool(texte),
    }


def mia50_creer_structure(demande):
    return {
        "demande_originale": str(demande or "").strip(),
        "objectif": None,
        "sous_objectifs": [],
        "etapes": [],
        "priorite": "normale",
        "contraintes": [],
        "ressources": [],
        "etat": "a_analyser",
        "resultat_attendu": None,
        "validation": {
            "statut": "a_valider",
            "validation_humaine_requise": True,
            "commentaire": "",
        },
        "historique": [],
    }


def mia50_definir_objectif(tache, objectif):
    resultat = dict(tache)
    valeur = str(objectif or "").strip()

    resultat["objectif"] = valeur or None

    if resultat["objectif"]:
        resultat["etat"] = "structuree"

    return resultat


def mia50_ajouter_sous_objectif(tache, sous_objectif):
    resultat = dict(tache)
    resultat["sous_objectifs"] = list(tache.get("sous_objectifs", []))

    valeur = str(sous_objectif or "").strip()

    if valeur:
        resultat["sous_objectifs"].append(valeur)

    return resultat


def mia50_ajouter_etape(tache, etape):
    resultat = dict(tache)
    resultat["etapes"] = list(tache.get("etapes", []))

    valeur = str(etape or "").strip()

    if valeur:
        resultat["etapes"].append(valeur)

    return resultat


def mia50_definir_priorite(tache, priorite):
    resultat = dict(tache)
    valeur = str(priorite or "").strip().lower()

    resultat["priorite"] = valeur if valeur in PRIORITES else "normale"

    return resultat


def mia50_ajouter_contrainte(tache, contrainte):
    resultat = dict(tache)
    resultat["contraintes"] = list(tache.get("contraintes", []))

    valeur = str(contrainte or "").strip()

    if valeur:
        resultat["contraintes"].append(valeur)

    return resultat


def mia50_ajouter_ressource(tache, ressource):
    resultat = dict(tache)
    resultat["ressources"] = list(tache.get("ressources", []))

    valeur = str(ressource or "").strip()

    if valeur:
        resultat["ressources"].append(valeur)

    return resultat


def mia50_definir_resultat_attendu(tache, resultat_attendu):
    resultat = dict(tache)
    valeur = str(resultat_attendu or "").strip()

    resultat["resultat_attendu"] = valeur or None

    return resultat


def mia50_ajouter_historique(tache, evenement):
    resultat = dict(tache)
    resultat["historique"] = list(tache.get("historique", []))

    valeur = str(evenement or "").strip()

    if valeur:
        resultat["historique"].append(valeur)

    return resultat


def mia50_evaluer_completude(tache):
    manques = []

    if not tache.get("objectif"):
        manques.append("objectif")

    if not tache.get("etapes"):
        manques.append("etapes")

    if not tache.get("resultat_attendu"):
        manques.append("resultat_attendu")

    return {
        "complete": not manques,
        "manques": manques,
        "objectif_present": bool(tache.get("objectif")),
        "etapes_presentes": bool(tache.get("etapes")),
        "resultat_attendu_present": bool(tache.get("resultat_attendu")),
    }


def mia50_preparer_validation(tache):
    resultat = dict(tache)

    resultat["validation"] = {
        "statut": "a_valider",
        "validation_humaine_requise": True,
        "commentaire": "Structure proposée par MIA, validation humaine requise.",
    }

    resultat["etat"] = "a_valider"

    return resultat


def _mia50_lignes(demande):
    texte = str(demande or "").strip()

    return [
        ligne.strip()
        for ligne in texte.splitlines()
        if ligne.strip()
    ]


def _mia50_est_contrainte(texte):
    t = texte.lower()

    marqueurs = (
        "contrainte",
        "contraintes",
        "ne pas ",
        "ne modifie ",
        "ne modifiez ",
        "n'interdit",
        "interdit",
        "sans ",
        "respecte ",
        "respecter ",
        "obligation",
        "obligatoire",
    )

    return t.startswith(marqueurs)


def _mia50_est_resultat(texte):
    t = texte.lower()

    marqueurs = (
        "résultat attendu",
        "resultat attendu",
        "objectif final",
        "doit permettre",
        "doit produire",
        "livrable",
        "à obtenir",
        "a obtenir",
        "identifie ce qui doit être fait",
        "identifiez ce qui doit être fait",
        "prépare une prochaine étape",
        "prepare une prochaine étape",
    )

    return t.startswith(marqueurs)


def _mia50_est_ressource(texte):
    t = texte.lower()

    marqueurs = (
        "ressource",
        "ressources",
        "utiliser ",
        "utilise ",
        "avec ",
        "disposer de ",
        "à partir de ",
        "a partir de ",
    )

    return t.startswith(marqueurs)


def _mia50_est_priorite(texte):
    t = texte.lower()

    if "priorité critique" in t or "priorite critique" in t:
        return "critique"

    if "priorité haute" in t or "priorite haute" in t:
        return "haute"

    if "priorité basse" in t or "priorite basse" in t:
        return "basse"

    if "priorité normale" in t or "priorite normale" in t:
        return "normale"

    return None


def _mia50_nettoyer_objectif(texte):
    resultat = str(texte or "").strip()

    prefixes = (
        "fais ",
        "faire ",
        "prépare ",
        "prepare ",
        "construis ",
        "construire ",
        "crée ",
        "créer ",
        "creer ",
        "analyse ",
        "analyser ",
        "développe ",
        "developpe ",
    )

    bas = resultat.lower()

    for prefixe in prefixes:
        if bas.startswith(prefixe):
            resultat = resultat[len(prefixe):].strip()
            break

    return resultat


def _mia50_extraire_validation(texte):
    t = str(texte or "").strip()
    bas = t.lower()

    validation = False

    marqueurs = (
        "validation humaine",
        "valider par l'humain",
        "valider par humain",
        "validation par l'humain",
        "validation par humain",
    )

    for marqueur in marqueurs:
        if marqueur in bas:
            validation = True
            break

    if not validation:
        return t, False

    resultat = t

    for marqueur in marqueurs:
        position = resultat.lower().find(marqueur)

        if position >= 0:
            prefixe = resultat[:position].rstrip()

            # Cas "avec validation humaine" :
            # conserver le résultat situé avant "avec".
            if prefixe.lower().endswith("avec"):
                prefixe = prefixe[:-4].rstrip()

            resultat = prefixe.rstrip(" ,;:")
            break

    resultat = resultat.rstrip(" ,;:")

    return resultat, True


def mia50_structurer_demande(demande):
    """
    Transforme une demande en tâche structurée.

    La décomposition utilise le texte original afin de conserver
    les séparations entre objectif, étapes, contraintes et résultats.
    Aucune exécution ni écriture persistante.
    """

    normalisee = mia50_normaliser_demande(demande)

    texte_original = normalisee.get("demande_originale", "")
    texte_normalise = normalisee.get("demande_normalisee", "")

    lignes = [
        ligne.strip()
        for ligne in texte_original.splitlines()
        if ligne.strip()
    ]

    # ==========================================================
    # DEMANDE SIMPLE
    # ==========================================================
    if len(lignes) <= 1:
        structure = mia50_creer_structure(texte_original)

        objectif = _mia50_nettoyer_objectif(texte_normalise)

        structure = mia50_definir_objectif(
            structure,
            objectif
        )

        structure["validation"] = {
            "statut": "a_valider",
            "validation_humaine_requise": True,
            "commentaire": (
                "Structure proposée par MIA, validation humaine requise."
            ),
        }

        structure["completude"] = mia50_evaluer_completude(structure)

        return structure

    # ==========================================================
    # DEMANDE COMPLEXE
    # ==========================================================
    structure = mia50_creer_structure(texte_original)

    objectif = None

    for ligne in lignes:
        bas = ligne.lower()

        if _mia50_est_contrainte(ligne):
            structure = mia50_ajouter_contrainte(
                structure,
                ligne
            )

        elif _mia50_est_resultat(ligne):
            ligne_resultat = ligne

            # Séparer le résultat de la mention de validation humaine.
            for separateur in (
                " avec validation humaine",
                " avec validation",
            ):
                if separateur in ligne_resultat.lower():
                    index = ligne_resultat.lower().find(separateur)
                    ligne_resultat = ligne_resultat[:index].rstrip(
                        " .,:;-"
                    )
                    break

            if ligne_resultat:
                precedent = structure.get("resultat_attendu")

                if precedent is None:
                    structure = mia50_definir_resultat_attendu(
                        structure,
                        ligne_resultat
                    )
                elif isinstance(precedent, list):
                    precedent.append(ligne_resultat)
                    structure["resultat_attendu"] = precedent
                else:
                    structure["resultat_attendu"] = [
                        precedent,
                        ligne_resultat,
                    ]

            if "validation humaine" in bas:
                structure["validation"] = {
                    "statut": "a_valider",
                    "validation_humaine_requise": True,
                    "commentaire": (
                        "Structure proposée par MIA, validation humaine requise."
                    ),
                }

        elif "validation humaine" in bas:
            structure["validation"] = _mia50_extraire_validation(
                ligne
            )

        elif _mia50_est_ressource(ligne):
            structure = mia50_ajouter_ressource(
                structure,
                ligne
            )

        elif _mia50_est_priorite(ligne):
            structure = mia50_definir_priorite(
                structure,
                ligne
            )

        elif objectif is None:
            objectif = _mia50_nettoyer_objectif(ligne)

        else:
            structure = mia50_ajouter_etape(
                structure,
                ligne
            )

    if objectif:
        structure = mia50_definir_objectif(
            structure,
            objectif
        )

    if structure["validation"]["statut"] != "a_valider":
        structure["validation"]["statut"] = "a_valider"

    structure["validation"]["validation_humaine_requise"] = True
    structure["validation"]["commentaire"] = (
        "Structure proposée par MIA, validation humaine requise."
    )

    structure["completude"] = mia50_evaluer_completude(structure)

    return structure


def mia50_statut():
    return {
        "version": VERSION,
        "mission": MISSION,
        "autorisation_execution": AUTORISATION_EXECUTION,
        "execution": EXECUTION,
        "lecture_seule": LECTURE_SEULE,
        "apprentissage_persistant": APPRENTISSAGE_PERSISTANT,
        "decision_automatique": DECISION_AUTOMATIQUE,
        "ecriture_persistante": ECRITURE_PERSISTANTE,
        "validation_humaine_requise": VALIDATION_HUMAINE_REQUISE,
    }
