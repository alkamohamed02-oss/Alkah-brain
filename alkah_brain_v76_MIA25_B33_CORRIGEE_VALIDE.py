import sqlite3
import datetime
import os
import re

from mia_orchestrateur_raisonnement_v1 import mia_orchestrer_raisonnement_v1
DB = "database/alkah_brain.db"


def ajouter():
    type_souvenir = input("Type du souvenir : ")
    titre = input("Titre du souvenir : ")
    contenu = input("Contenu du souvenir : ")
    importance = input("Importance (1-5) : ")
    try:
        importance = int(importance)
        if importance < 1 or importance > 5:
            importance = 3
    except ValueError:
        importance = 3

    now = datetime.datetime.now().isoformat()

    c = sqlite3.connect(DB)
    c.execute(
        "INSERT INTO documents "
        "(title, content, source, created_at, updated_at, type, importance) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (titre, contenu, "ALKAH-BRAIN", now, now, type_souvenir, importance)
    )
    c.commit()
    c.close()

    print("Souvenir enregistre.")



def calculer_pertinence(mot, titre, contenu, importance):
    mot = mot.lower().strip()
    titre = titre.lower()
    contenu = contenu.lower()

    score = 0

    # Le titre est le signal principal : le document traite directement du sujet.
    if mot and mot in titre:
        score += 70
    # Une simple mention dans le contenu est un signal secondaire.
    elif mot and mot in contenu:
        score += 20

    # L'importance complète le signal de pertinence.
    score += importance * 4

    if score > 100:
        score = 100

    return score
def rechercher():
    mot = input("Que veux-tu rechercher ? ")

    c = sqlite3.connect(DB)

    resultats = c.execute(
        "SELECT id, title, content, importance FROM documents "
        "WHERE title LIKE ? OR content LIKE ?",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    resultats = sorted(
        resultats,
        key=lambda x: calculer_pertinence(mot, x[1], x[2], x[3]),
        reverse=True
    )

    if resultats:
        for sid, titre, contenu, importance in resultats:
            pertinence = calculer_pertinence(
                mot, titre, contenu, importance
            )

            print()
            print("Titre :", titre)
            print("Importance :", importance)
            print("Pertinence :", pertinence)
            print("Contenu :", contenu)

            contextes = c.execute(
                "SELECT contexte_type, contenu "
                "FROM contexts WHERE document_id=?",
                (sid,)
            ).fetchall()

            if contextes:
                print("Contextes :")
                for contexte_type, contexte in contextes:
                    print("  -", contexte_type, ":", contexte)

    else:
        print("Aucun souvenir trouve.")

    c.close()



def synthese_contexte():
    mot = input("Sujet de la synthese : ")

    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title, content, importance "
        "FROM documents "
        "WHERE title LIKE ? OR content LIKE ?",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    souvenirs = sorted(
        souvenirs,
        key=lambda x: calculer_pertinence(mot, x[1], x[2], x[3]),
        reverse=True
    )

    if not souvenirs:
        print("Aucune information trouvee.")
        c.close()
        return

    print("\n=== SYNTHESE ALKAH-BRAIN ===")
    print("Sujet :", mot)

    print("\nSouvenirs principaux :")

    for sid, titre, contenu, importance in souvenirs[:5]:
        pertinence = calculer_pertinence(
            mot, titre, contenu, importance
        )

        print("\n- Titre :", titre)
        print("  Importance :", importance)
        print("  Pertinence :", pertinence)
        print("  Contenu :", contenu)

    print("\nContextes :")

    for sid, titre, contenu, importance in souvenirs[:5]:
        contextes = c.execute(
            "SELECT contexte_type, contenu "
            "FROM contexts WHERE document_id=?",
            (sid,)
        ).fetchall()

        for contexte_type, contexte in contextes:
            print("  -", contexte_type, ":", contexte)

    print("\nRelations :")

    for sid, titre, contenu, importance in souvenirs[:5]:
        relations = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.target_id=d.id "
            "WHERE r.source_id=?",
            (sid,)
        ).fetchall()

        for relation, cible in relations:
            print("  -", titre, "->", relation, "->", cible)

    print("\n=== SYNTHESE FACTUELLE ===")

    meilleur = souvenirs[0]
    meilleur_score = calculer_pertinence(
        mot,
        meilleur[1],
        meilleur[2],
        meilleur[3]
    )

    print("Nombre de souvenirs :", len(souvenirs))
    print("Souvenir le plus pertinent :", meilleur[1])
    print("Importance :", meilleur[3])
    print("Pertinence :", meilleur_score)

    types_contextes = set()

    for sid, titre, contenu, importance in souvenirs[:5]:
        contextes = c.execute(
            "SELECT contexte_type FROM contexts WHERE document_id=?",
            (sid,)
        ).fetchall()

        for (contexte_type,) in contextes:
            types_contextes.add(contexte_type)

    if types_contextes:
        print("Types de contexte :", ", ".join(sorted(types_contextes)))
    else:
        print("Types de contexte : aucun")

    print("La synthèse est construite uniquement à partir des données mémorisées.")

    c.close()



def explorer_relations_intelligentes():
    mot = input("Sujet a explorer : ")

    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title, content, importance "
        "FROM documents "
        "WHERE title LIKE ? OR content LIKE ?",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    souvenirs = sorted(
        souvenirs,
        key=lambda x: calculer_pertinence(mot, x[1], x[2], x[3]),
        reverse=True
    )

    if not souvenirs:
        print("Aucun souvenir trouve.")
        c.close()
        return

    print("\n=== RAISONNEMENT RELATIONNEL ===")

    trouvee = False

    for sid, titre, contenu, importance in souvenirs[:5]:

        relations_sortantes = c.execute(
            "SELECT r.relation, d.title, d.content "
            "FROM relations r "
            "JOIN documents d ON r.target_id=d.id "
            "WHERE r.source_id=?",
            (sid,)
        ).fetchall()

        for relation, cible, contenu_cible in relations_sortantes:
            trouvee = True

            print("\nRelation sortante")
            print("Souvenir :", titre)
            print("Relation :", relation)
            print("Souvenir lie :", cible)
            print("Contenu lie :", contenu_cible)

        relations_entrantes = c.execute(
            "SELECT r.relation, d.title, d.content "
            "FROM relations r "
            "JOIN documents d ON r.source_id=d.id "
            "WHERE r.target_id=?",
            (sid,)
        ).fetchall()

        for relation, source, contenu_source in relations_entrantes:
            trouvee = True

            print("\nRelation entrante")
            print("Souvenir :", titre)
            print("Relation :", relation)
            print("Souvenir lie :", source)
            print("Contenu lie :", contenu_source)

    if not trouvee:
        print("Aucune relation trouvee.")

    c.close()





def mots_significatifs(texte):
    mots_vides = {
        "le", "la", "les", "un", "une", "des",
        "de", "du", "et", "est", "dans", "avec",
        "pour", "mon", "ma", "mes", "son", "sa",
        "ce", "cette", "ces", "qui", "que", "en",
        "sur", "par", "une", "aux", "au"
    }

    mots = texte.lower().replace("-", " ").split()

    resultat = set()

    for mot in mots:
        mot = mot.strip(".,;:!?()[]{}\"'")

        if len(mot) >= 3 and mot not in mots_vides:
            resultat.add(mot)

    return resultat



def obtenir_frequences_mots():
    c = sqlite3.connect(DB)

    documents = c.execute(
        "SELECT title, content FROM documents"
    ).fetchall()

    frequences = {}

    for titre, contenu in documents:
        mots = mots_significatifs(titre + " " + contenu)

        for mot in mots:
            frequences[mot] = frequences.get(mot, 0) + 1

    c.close()

    return frequences



def obtenir_contextes_document(document_id):
    c = sqlite3.connect(DB)

    contextes = c.execute(
        "SELECT contexte_type, contenu "
        "FROM contexts "
        "WHERE document_id=?",
        (document_id,)
    ).fetchall()

    c.close()

    return contextes




def ajouter_contexte():
    c = sqlite3.connect(DB)

    documents = c.execute(
        "SELECT id, title FROM documents ORDER BY id"
    ).fetchall()

    if not documents:
        print("Aucun souvenir disponible.")
        c.close()
        return

    print("\n=== AJOUT D'UN CONTEXTE ===")
    print("Souvenirs disponibles :")

    for document_id, titre in documents:
        print(document_id, "-", titre)

    try:
        document_id = int(input("\nID du souvenir : "))
    except ValueError:
        print("ID invalide.")
        c.close()
        return

    document = c.execute(
        "SELECT title FROM documents WHERE id=?",
        (document_id,)
    ).fetchone()

    if not document:
        print("Souvenir introuvable.")
        c.close()
        return

    print("\nTypes disponibles :")
    print("1 - statique")
    print("2 - dynamique")
    print("3 - holistique")

    choix = input("Type de contexte : ").strip()

    types = {
        "1": "statique",
        "2": "dynamique",
        "3": "holistique"
    }

    contexte_type = types.get(choix)

    if not contexte_type:
        print("Type de contexte invalide.")
        c.close()
        return

    contenu = input("Contenu du contexte : ").strip()

    if not contenu:
        print("Le contenu ne peut pas être vide.")
        c.close()
        return

    maintenant = datetime.datetime.now().isoformat()

    c.execute(
        "INSERT INTO contexts "
        "(document_id, contexte_type, contenu, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            document_id,
            contexte_type,
            contenu,
            maintenant,
            maintenant
        )
    )

    c.commit()
    c.close()

    print("\nContexte ajoute avec succes.")
    print("Souvenir :", document[0])
    print("Type :", contexte_type)


def analyser_etat_contextes():
    c = sqlite3.connect(DB)

    documents = c.execute(
        "SELECT id, title FROM documents ORDER BY id"
    ).fetchall()

    avec_contexte = []
    sans_contexte = []

    for document_id, titre in documents:
        nombre = c.execute(
            "SELECT COUNT(*) FROM contexts WHERE document_id=?",
            (document_id,)
        ).fetchone()[0]

        if nombre > 0:
            avec_contexte.append((document_id, titre, nombre))
        else:
            sans_contexte.append((document_id, titre))

    print("\n=== ETAT DES CONTEXTES ===")

    print("\nSouvenirs avec contexte :", len(avec_contexte))

    for document_id, titre, nombre in avec_contexte:
        print(
            "-",
            titre,
            "->",
            nombre,
            "contexte(s)"
        )

    print("\nSouvenirs sans contexte :", len(sans_contexte))

    for document_id, titre in sans_contexte:
        print("-", titre)

    c.close()


def calculer_similarite_contextuelle(document_id1, document_id2):
    contextes1 = obtenir_contextes_document(document_id1)
    contextes2 = obtenir_contextes_document(document_id2)

    if not contextes1 or not contextes2:
        return 0

    textes1 = [
        contexte_type + " " + contenu
        for contexte_type, contenu in contextes1
    ]

    textes2 = [
        contexte_type + " " + contenu
        for contexte_type, contenu in contextes2
    ]

    meilleur_score = 0

    for texte1 in textes1:
        for texte2 in textes2:
            score = calculer_similarite(texte1, texte2)

            if score > meilleur_score:
                meilleur_score = score

    return meilleur_score


def calculer_similarite(texte1, texte2):
    mots1 = mots_significatifs(texte1)
    mots2 = mots_significatifs(texte2)

    if not mots1 or not mots2:
        return 0

    frequences = obtenir_frequences_mots()

    communs = mots1.intersection(mots2)

    if not communs:
        return 0

    poids_communs = 0
    poids_total = 0

    for mot in mots1.union(mots2):
        frequence = frequences.get(mot, 1)

        poids = 1 / frequence

        poids_total += poids

        if mot in communs:
            poids_communs += poids

    score = int((poids_communs / poids_total) * 100)

    return score


def calculer_similarite_document(titre1, contenu1, titre2, contenu2):
    score_titre = calculer_similarite(titre1, titre2)
    score_contenu = calculer_similarite(contenu1, contenu2)

    score_final = int(
        (score_titre * 0.4) +
        (score_contenu * 0.6)
    )

    return score_final



def analyser_similarite(texte1, texte2):
    mots1 = mots_significatifs(texte1)
    mots2 = mots_significatifs(texte2)

    communs = sorted(mots1.intersection(mots2))

    score = calculer_similarite(texte1, texte2)

    return score, communs







def analyser_decision_complete(
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    signaux = analyser_signaux_presents(
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    decision = construire_decision(
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    decision["signaux"] = signaux

    return decision



def enregistrer_decision(
    document_id1,
    document_id2,
    resultat
):
    c = sqlite3.connect(DB)

    maintenant = datetime.datetime.now().isoformat()

    signaux = ", ".join(
        resultat.get("signaux", [])
    )

    raisons = " | ".join(
        resultat.get("raisons", [])
    )

    c.execute(
        "INSERT INTO decision_history "
        "(document_id1, document_id2, score_global, "
        "confiance, signaux, raisons, decision, "
        "action, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            document_id1,
            document_id2,
            resultat["score_global"],
            resultat["confiance"],
            signaux,
            raisons,
            resultat["decision"],
            resultat["action"],
            maintenant
        )
    )

    c.commit()
    c.close()

    print("Decision enregistree dans la memoire du raisonnement.")



def consulter_decisions(
    document_id1=None,
    document_id2=None
):
    c = sqlite3.connect(DB)

    if document_id1 is not None and document_id2 is not None:
        resultats = c.execute(
            "SELECT id, document_id1, document_id2, "
            "score_global, confiance, signaux, raisons, "
            "decision, action, created_at "
            "FROM decision_history "
            "WHERE document_id1=? AND document_id2=? "
            "ORDER BY id DESC",
            (document_id1, document_id2)
        ).fetchall()
    else:
        resultats = c.execute(
            "SELECT id, document_id1, document_id2, "
            "score_global, confiance, signaux, raisons, "
            "decision, action, created_at "
            "FROM decision_history "
            "ORDER BY id DESC"
        ).fetchall()

    c.close()

    return resultats



def decision_precedente(
    document_id1,
    document_id2
):
    resultats = consulter_decisions(
        document_id1,
        document_id2
    )

    if not resultats:
        return None

    return resultats[0]



def recuperer_experience(
    document_id1,
    document_id2
):
    precedente = decision_precedente(
        document_id1,
        document_id2
    )

    if precedente is None:
        return {
            "existe": False,
            "experience": None
        }

    return {
        "existe": True,
        "experience": {
            "score_global": precedente[3],
            "confiance": precedente[4],
            "signaux": precedente[5],
            "raisons": precedente[6],
            "decision": precedente[7],
            "action": precedente[8],
            "date": precedente[9]
        }
    }



def preparer_analyse_avec_experience(
    document_id1,
    document_id2,
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    analyse = analyser_decision_complete(
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    experience = recuperer_experience(
        document_id1,
        document_id2
    )

    return {
        "analyse_actuelle": analyse,
        "experience_precedente": experience
    }



def comparer_experience_analyse(
    resultat
):
    analyse = resultat["analyse_actuelle"]
    experience = resultat["experience_precedente"]

    if not experience["existe"]:
        return {
            "statut": "nouvelle",
            "ecart_score": None
        }

    ancienne = experience["experience"]

    ecart = (
        analyse["score_global"]
        - ancienne["score_global"]
    )

    if ecart == 0:
        statut = "coherente"
    else:
        statut = "evolution_detectee"

    return {
        "statut": statut,
        "ecart_score": ecart
    }



def evaluer_experience_pour_raisonnement(
    resultat
):
    comparaison = comparer_experience_analyse(
        resultat
    )

    if comparaison["statut"] == "nouvelle":
        pertinence = "aucune_experience"
    elif comparaison["statut"] == "coherente":
        pertinence = "experience_coherente"
    else:
        pertinence = "experience_a_examiner"

    return {
        "statut": comparaison["statut"],
        "ecart_score": comparaison["ecart_score"],
        "pertinence": pertinence
    }



def analyser_avec_experience(
    document_id1,
    document_id2,
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    resultat = preparer_analyse_avec_experience(
        document_id1,
        document_id2,
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    evaluation = evaluer_experience_pour_raisonnement(
        resultat
    )

    resultat["evaluation_experience"] = evaluation

    signal_experience = obtenir_signal_experience(
        resultat
    )

    resultat["signal_experience"] = signal_experience

    utilisation_experience = decider_utilisation_experience(
        resultat
    )

    resultat["utilisation_experience"] = utilisation_experience

    impact_experience = determiner_impact_experience(
        resultat
    )

    resultat["impact_experience"] = impact_experience

    return resultat



def obtenir_signal_experience(
    resultat
):
    evaluation = resultat.get(
        "evaluation_experience"
    )

    if evaluation is None:
        return {
            "signal": "aucun",
            "important": False
        }

    pertinence = evaluation["pertinence"]

    if pertinence == "experience_coherente":
        return {
            "signal": "experience_coherente",
            "important": True
        }

    if pertinence == "experience_a_examiner":
        return {
            "signal": "experience_a_examiner",
            "important": True
        }

    return {
        "signal": "nouvelle",
        "important": False
    }



def decider_utilisation_experience(
    resultat
):
    signal = resultat.get(
        "signal_experience"
    )

    if signal is None:
        return {
            "utiliser_experience": False,
            "raison": "aucun_signal"
        }

    if signal["important"] is True:
        return {
            "utiliser_experience": True,
            "raison": signal["signal"]
        }

    return {
        "utiliser_experience": False,
        "raison": signal["signal"]
    }



def determiner_impact_experience(
    resultat
):
    utilisation = resultat.get(
        "utilisation_experience"
    )

    if utilisation is None:
        return {
            "impact": "aucun",
            "niveau": 0
        }

    if utilisation["utiliser_experience"] is False:
        return {
            "impact": "non_utilisee",
            "niveau": 0
        }

    raison = utilisation["raison"]

    if raison == "experience_coherente":
        return {
            "impact": "coherent",
            "niveau": 1
        }

    if raison == "experience_a_examiner":
        return {
            "impact": "a_examiner",
            "niveau": 1
        }

    return {
        "impact": "inconnu",
        "niveau": 0
    }



def evaluer_experience_decision(
    decision_id,
    statut,
    qualite
):
    statuts_valides = {
        "confirmee",
        "infirmee",
        "non_evaluee"
    }

    if statut not in statuts_valides:
        raise ValueError(
            "Statut d'experience invalide."
        )

    if not isinstance(qualite, int):
        raise ValueError(
            "La qualite doit etre un entier."
        )

    if qualite < 0 or qualite > 100:
        raise ValueError(
            "La qualite doit etre comprise entre 0 et 100."
        )

    maintenant = datetime.datetime.now().isoformat()

    c = sqlite3.connect(DB)

    c.execute(
        "UPDATE decision_history "
        "SET experience_statut=?, "
        "experience_qualite=?, "
        "experience_evaluee_at=? "
        "WHERE id=?",
        (
            statut,
            qualite,
            maintenant,
            decision_id
        )
    )

    c.commit()
    c.close()

    return {
        "decision_id": decision_id,
        "statut": statut,
        "qualite": qualite,
        "evaluee_at": maintenant
    }



def recuperer_experience_evaluee(
    decision_id
):
    c = sqlite3.connect(DB)

    resultat = c.execute(
        "SELECT id, document_id1, document_id2, "
        "score_global, confiance, decision, action, "
        "experience_statut, experience_qualite, "
        "experience_evaluee_at "
        "FROM decision_history "
        "WHERE id=?",
        (decision_id,)
    ).fetchone()

    c.close()

    if resultat is None:
        return {
            "existe": False,
            "experience": None
        }

    return {
        "existe": True,
        "experience": {
            "decision_id": resultat[0],
            "document_id1": resultat[1],
            "document_id2": resultat[2],
            "score_global": resultat[3],
            "confiance": resultat[4],
            "decision": resultat[5],
            "action": resultat[6],
            "statut": resultat[7],
            "qualite": resultat[8],
            "evaluee_at": resultat[9]
        }
    }



def calculer_poids_experience(
    experience
):
    if not experience["existe"]:
        return {
            "poids": 0,
            "niveau": 0,
            "raison": "aucune_experience"
        }

    e = experience["experience"]

    statut = e["statut"]
    qualite = e["qualite"]

    if statut == "non_evaluee":
        return {
            "poids": 0,
            "niveau": 0,
            "raison": "experience_non_evaluee"
        }

    if statut == "infirmee":
        if qualite >= 80:
            niveau = 3
        elif qualite >= 50:
            niveau = 2
        else:
            niveau = 1

        return {
            "poids": -niveau,
            "niveau": niveau,
            "raison": "experience_infirmee"
        }

    if statut == "confirmee":
        if qualite >= 80:
            niveau = 3
        elif qualite >= 50:
            niveau = 2
        else:
            niveau = 1

        return {
            "poids": niveau,
            "niveau": niveau,
            "raison": "experience_confirmee"
        }

    return {
        "poids": 0,
        "niveau": 0,
        "raison": "statut_inconnu"
    }



def mia_interroger(question):
    """
    Recherche les connaissances pertinentes dans la mémoire ALKAH-BRAIN.

    La recherche utilise les mots significatifs de la question
    au lieu de rechercher la phrase complète.
    """
    import sqlite3
    import re

    if not isinstance(question, str):
        raise ValueError("La question doit etre un texte.")

    question = question.strip()

    if not question:
        return {
            "question": "",
            "reponse": "La question est vide.",
            "souvenirs": []
        }

    mots_vides = {
        "qui", "que", "quoi", "quel", "quelle", "quels", "quelles",
        "est", "es", "sont", "une", "un", "des", "les", "le", "la",
        "de", "du", "dans", "pour", "avec", "sur", "et", "ou",
        "comment", "faire", "peut", "peux", "vous", "moi", "elle",
        "il", "je", "tu", "ce", "cette", "ces", "mon", "ma", "mes",
        "ton", "ta", "tes"
    }

    mots = re.findall(r"[A-Za-zÀ-ÿ0-9-]+", question.lower())
    mots = [mot for mot in mots if len(mot) >= 3 and mot not in mots_vides]

    if not mots:
        mots = re.findall(r"[A-Za-zÀ-ÿ0-9-]+", question.lower())

    c = sqlite3.connect(DB)

    conditions = []
    parametres = []

    for mot in mots:
        conditions.append("(title LIKE ? OR content LIKE ?)")
        parametres.extend(["%" + mot + "%", "%" + mot + "%"])

    requete = f"""
        SELECT id, title, content, type, statut, importance
        FROM documents
        WHERE statut = 'actif'
        AND ({" OR ".join(conditions)})
    """

    lignes = c.execute(requete, parametres).fetchall()

    souvenirs = []

    for sid, titre, contenu, type_souvenir, statut, importance in lignes:
        score_mots = 0

        titre_bas = titre.lower()
        contenu_bas = contenu.lower()

        mots_generaux = {
            "comme", "local", "simple", "nouveau", "nouvelle",
            "faire", "aider", "besoin", "projet"
        }

        for mot in mots:
            if mot in mots_generaux:
                continue

            if mot in titre_bas:
                score_mots += 70
            elif mot in contenu_bas:
                score_mots += 10

        score_mots += importance * 2
        score_mots = min(score_mots, 100)


        souvenirs.append({
            "id": sid,
            "titre": titre,
            "contenu": contenu,
            "type": type_souvenir,
            "statut": statut,
            "importance": importance,
            "pertinence": score_mots
        })

    c.close()

    souvenirs.sort(
        key=lambda x: x.get("pertinence", 0),
        reverse=True
    )

    if not souvenirs:
        reponse = (
            "Je n'ai pas trouve de connaissance pertinente "
            "dans la memoire ALKAH-BRAIN."
        )
    else:
        reponse = (
            f"J'ai trouve {len(souvenirs)} souvenir(s) "
            "pertinent(s) dans la memoire ALKAH-BRAIN."
        )

    return {
        "question": question,
        "reponse": reponse,
        "souvenirs": souvenirs
    }


def mia_repondre(question):
    """
    Point d'entrée principal de réponse de MIA V35.

    Utilise le pipeline complet V35 :
    intention → recherche → évaluation → décision → réponse.
    """
    return mia_generer_reponse(question)


def mia_verifier_connaissance(
    resultat,
    seuil_pertinence=40
):
    if not resultat or not resultat.get("souvenirs"):
        return {
            "connait": False,
            "niveau": 0,
            "raison": "aucune_connaissance_trouvee"
        }

    souvenirs_valides = [
        s for s in resultat["souvenirs"]
        if (s.get("pertinence") or 0) >= seuil_pertinence
    ]

    if not souvenirs_valides:
        return {
            "connait": False,
            "niveau": 0,
            "raison": "pertinence_insuffisante"
        }

    meilleure_pertinence = max(
        s.get("pertinence") or 0
        for s in souvenirs_valides
    )

    if meilleure_pertinence >= 90:
        niveau = 3
    elif meilleure_pertinence >= 70:
        niveau = 2
    else:
        niveau = 1

    return {
        "connait": True,
        "niveau": niveau,
        "raison": "connaissance_memorisee",
        "pertinence": meilleure_pertinence,
        "nombre_sources": len(souvenirs_valides)
    }



def mia_dialogue_controle(question):
    resultat = mia_interroger(question)

    controle = mia_verifier_connaissance(resultat)

    if not controle["connait"]:
        return {
            "question": question,
            "connait": False,
            "niveau": controle["niveau"],
            "reponse": (
                "Je ne dispose pas encore de suffisamment "
                "de connaissances memorisees dans ALKAH-BRAIN "
                "pour repondre avec fiabilite a cette question."
            ),
            "sources": []
        }

    reponse = mia_repondre(question)

    return {
        "question": question,
        "connait": True,
        "niveau": controle["niveau"],
        "pertinence": controle["pertinence"],
        "reponse": reponse["reponse"],
        "sources": reponse["sources"]
    }



def mia_classer_intention(question):
    if not isinstance(question, str):
        raise ValueError("La question doit etre un texte.")

    q = question.strip().lower()

    if not q:
        return {
            "intention": "inconnue",
            "confiance": 0
        }

    mots_synthese = [
        "resume", "résume", "synthese", "synthèse",
        "résumer", "resumer", "en bref"
    ]

    mots_explication = [
        "explique", "expliquer", "comment",
        "pourquoi", "décris", "decris"
    ]

    mots_salutation = [
        "bonjour", "bonsoir", "salut", "coucou",
        "hello", "bonne journée", "bonne journee"
    ]

    mots_identite_mia = [
        "qui es-tu", "qui êtes-vous", "qui etes-vous",
        "présente-toi", "presente-toi",
        "que peux-tu faire", "que pouvez-vous faire",
        "à quoi sers-tu", "a quoi sers-tu",
        "quel est ton rôle", "quel est ton role"
    ]

    mots_analyse = [
        "analyse", "analyser", "évalue", "evalue",
        "évaluer", "decision", "décision"
    ]

    if any(mot in q for mot in mots_salutation):
        intention = "salutation"
        confiance = 100

    elif any(mot in q for mot in mots_identite_mia):
        intention = "identite_mia"
        confiance = 100

    elif any(mot in q for mot in mots_synthese):
        intention = "synthese"
        confiance = 90

    elif any(mot in q for mot in mots_explication):
        intention = "explication"
        confiance = 90

    elif any(mot in q for mot in mots_analyse):
        intention = "analyse"
        confiance = 90

    else:
        intention = "recherche"
        confiance = 70

    return {
        "intention": intention,
        "confiance": confiance
    }



def mia_choisir_action(intention):
    actions = {
        "recherche": "rechercher_memoire",
        "explication": "rechercher_pour_expliquer",
        "synthese": "rechercher_pour_synthetiser",
        "analyse": "rechercher_pour_analyser",
        "identite_mia": "repondre_identite_mia",
        "salutation": "repondre_salutation"
    }

    return {
        "intention": intention,
        "action": actions.get(
            intention,
            "demander_clarification"
        )
    }



def mia25_detecter_demande_decision(question):
    q = question.strip().lower()

    mots_decision = [
        "choisir", "choix", "option", "options", "hésite", "hesite",
        "recommande", "recommandation",
        "décision", "decision",
        "décider", "decider",
        "comparer", "comparaison",
        "stratégie", "strategie",
        "quelle option", "quel choix",
        "quelle décision", "quel plan",
        "devrais-je"
    ]

    return any(mot in q for mot in mots_decision)


def mia25_extraire_options(question):
    q = " ".join(question.strip().split())
    q_min = q.lower()

    prefixes = [
        "je dois choisir entre ",
        "j'hésite entre ",
        "je compare ",
        "dois-je ",
        "faut-il ",
        "je dois "
    ]

    debut = q

    for prefixe in prefixes:
        if q_min.startswith(prefixe):
            debut = q[len(prefixe):]
            break

    separateurs_criteres = [
        ". je privilégie ",
        ". je privilegie ",
        ", je privilégie ",
        ", je privilegie "
    ]

    partie_decision = debut

    for separateur in separateurs_criteres:
        position = partie_decision.lower().find(separateur)

        if position != -1:
            partie_decision = partie_decision[:position]
            break

    for marqueur in [". laquelle", ". laquelle est", "? laquelle"]:
        position = partie_decision.lower().find(marqueur)
        if position != -1:
            partie_decision = partie_decision[:position]
            break

    parties = partie_decision.split(" ou ", 1)

    if len(parties) != 2 and q_min.startswith("je dois choisir entre "):
        parties = partie_decision.split(" et ", 1)

    if len(parties) == 2:
        options = [
            parties[0].strip(" ?.!"),
            parties[1].strip(" ?.!"),
        ]
        if all(options):
            return options

    if q_min.startswith("je compare "):
        parties = partie_decision.split(" et ", 1)

        if len(parties) == 2:
            options = [
                parties[0].strip(" ?.!"),
                parties[1].strip(" ?.!"),
            ]
            if all(options):
                return options

    return []


def mia25_extraire_criteres(question):
    q = question.strip().lower()

    correspondances = {
        "cohérence": "coherence",
        "coherence": "coherence",
        "faisabilité": "faisabilite",
        "faisabilite": "faisabilite",
        "ressources": "ressources",
        "contraintes": "contraintes",
        "risques": "risques",
        "incertitudes": "incertitudes"
    }

    criteres = []

    for mot, critere in correspondances.items():
        if mot in q and critere not in criteres:
            criteres.append(critere)

    return criteres


def mia25_extraire_valeurs_criteres(question):
    q = question.strip().lower()

    correspondances = {
        "coherence": ["cohérence", "coherence"],
        "faisabilite": ["faisabilité", "faisabilite"],
        "ressources": ["ressources"],
        "contraintes": ["contraintes"],
        "risques": ["risques"],
        "incertitudes": ["incertitudes"]
    }

    criteres = {}

    for critere, variantes in correspondances.items():
        for variante in variantes:
            motif = rf"\b{re.escape(variante)}\s*[:=]?\s*([0-5])\b"
            match = re.search(motif, q, re.IGNORECASE)

            if match:
                criteres[critere] = int(match.group(1))
                break

    return criteres



def mia25_extraire_options_detaillees(question):
    """
    Extrait les options et leurs critères propres depuis une question structurée.
    Ne complète pas les critères absents et n'invente aucune valeur.
    """
    correspondances = {
        "coherence": ["cohérence", "coherence"],
        "faisabilite": ["faisabilité", "faisabilite"],
        "ressources": ["ressources"],
        "contraintes": ["contraintes"],
        "risques": ["risques"],
        "incertitudes": ["incertitudes"]
    }

    blocs = re.split(
        r'\bOption\s+\d+\s*:',
        question,
        flags=re.IGNORECASE
    )

    options = []

    for i, bloc in enumerate(blocs[1:], start=1):
        texte = bloc.strip()
        criteres = {}

        for critere, variantes in correspondances.items():
            for variante in variantes:
                motif = rf"\b{re.escape(variante)}\s*[:=]?\s*([0-5])\b"
                match = re.search(motif, texte, re.IGNORECASE)

                if match:
                    criteres[critere] = int(match.group(1))
                    break

        positions = []

        for variante in sum(correspondances.values(), []):
            match = re.search(
                rf"\b{re.escape(variante)}\s*[:=]?\s*[0-5]\b",
                texte,
                re.IGNORECASE
            )
            if match:
                positions.append(match.start())

        fin_description = min(positions) if positions else len(texte)
        description = texte[:fin_description].strip(" .,\n")

        options.append({
            "nom": f"Option_{i}",
            "description": description,
            "criteres": criteres
        })

    return options

def mia25_controle_criteres(question):
    criteres_detectes = mia25_extraire_criteres(question)
    criteres_evalues = mia25_extraire_valeurs_criteres(question)

    criteres_manquants = [
        critere
        for critere in criteres_detectes
        if critere not in criteres_evalues
    ]

    return {
        "criteres_detectes": criteres_detectes,
        "criteres_evalues": criteres_evalues,
        "criteres_manquants": criteres_manquants,
        "pret_pour_mia25": (
            len(criteres_detectes) > 0
            and len(criteres_manquants) == 0
        )
    }


def mia_executer_action(question):
    intention_resultat = mia_classer_intention(question)
    intention = intention_resultat["intention"]

    action_resultat = mia_choisir_action(intention)
    action = action_resultat["action"]

    decision_detectee = mia25_detecter_demande_decision(question)
    options = mia25_extraire_options(question)

    mia25_resultat = None

    options_detaillees = mia25_extraire_options_detaillees(question)

    if decision_detectee and (len(options) >= 2 or len(options_detaillees) >= 2):

        if len(options_detaillees) >= 2:
            options_mia25 = options_detaillees[:2]

            criteres_complets = all(
                len(option.get("criteres", {})) == 6
                for option in options_mia25
            )

            if criteres_complets:
                mia25_resultat = mia25_recommander_option(options_mia25)

            else:
                criteres_par_option = []

                for option in options_mia25:
                    criteres_par_option.append({
                        "nom": option.get("nom"),
                        "criteres_evalues": option.get("criteres", {}),
                        "criteres_manquants": [
                            critere
                            for critere in [
                                "coherence",
                                "faisabilite",
                                "ressources",
                                "contraintes",
                                "risques",
                                "incertitudes"
                            ]
                            if critere not in option.get("criteres", {})
                        ]
                    })

                mia25_resultat = {
                    "statut": "criteres_manquants_par_option",
                    "criteres_par_option": criteres_par_option,
                    "demande": (
                        "Pour poursuivre la comparaison, veuillez évaluer "
                        "pour chaque option les critères manquants de 0 à 5."
                    ),
                    "validation_humaine_requise": True,
                    "execution_autorisee": False
                }

        else:
            controle_criteres = mia25_controle_criteres(question)

            if controle_criteres["pret_pour_mia25"]:
                options_mia25 = [
                    {
                        "nom": f"Option_{i}",
                        "description": option,
                        "criteres": dict(controle_criteres["criteres_evalues"])
                    }
                    for i, option in enumerate(options[:2], 1)
                ]

                mia25_resultat = mia25_recommander_option(options_mia25)

            else:
                mia25_resultat = {
                    "statut": "criteres_manquants",
                    "criteres_detectes": controle_criteres["criteres_detectes"],
                    "criteres_detectes": controle_criteres["criteres_detectes"],
                    "criteres_evalues": controle_criteres["criteres_evalues"],
                    "criteres_manquants": controle_criteres["criteres_manquants"],
                    "demande": (
                        "Pour poursuivre la comparaison, veuillez évaluer "
                        "les critères suivants de 0 à 5 : "
                        + ", ".join(controle_criteres["criteres_manquants"])
                        + "."
                    ),
                    "validation_humaine_requise": True,
                    "execution_autorisee": False
                }

    if action == "repondre_salutation":
        resultat = {
            "souvenirs": [],
            "reponse": (
                "Bonjour ! Je suis MIA, l'interface intelligente "
                "d'ALKAH-BRAIN. Comment puis-je vous aider ?"
            )
        }

        return {
            "question": question,
            "requete_memoire": "",
            "intention": intention,
            "action": action,
            "resultat": resultat,
            "mia25": mia25_resultat
        }

    if action == "repondre_identite_mia":
        q = question.strip().lower()

        if any(mot in q for mot in [
            "que peux-tu faire", "que pouvez-vous faire",
            "à quoi sers-tu", "a quoi sers-tu",
            "quel est ton rôle", "quel est ton role"
        ]):
            resultat = (
                "Je suis MIA, l'interface intelligente d'ALKAH-BRAIN. "
                "Je peux aider l'utilisateur à rechercher, comprendre, "
                "analyser et synthétiser des informations, avec une réponse "
                "adaptée au niveau de confiance du système."
            )
        else:
            resultat = (
                "Je suis MIA, l'interface intelligente d'ALKAH-BRAIN. "
                "Je suis conçue pour faciliter l'utilisation du système "
                "et accompagner l'utilisateur simplement."
            )

        return {
            "question": question,
            "requete_memoire": "",
            "intention": intention,
            "action": action,
            "resultat": resultat,
            "mia25": mia25_resultat
        }

    requete_memoire = mia_normaliser_requete(
        question,
        intention
    )

    if action in (
        "rechercher_memoire",
        "rechercher_pour_expliquer",
        "rechercher_pour_synthetiser",
        "rechercher_pour_analyser"
    ):
        resultat = mia_interroger(requete_memoire)

        return {
            "question": question,
            "requete_memoire": requete_memoire,
            "intention": intention,
            "action": action,
            "resultat": resultat,
            "mia25": mia25_resultat
        }

    return {
        "question": question,
        "requete_memoire": requete_memoire,
        "intention": intention,
        "action": action,
        "resultat": None,
        "mia25": mia25_resultat
    }



def mia_normaliser_requete(question, intention):
    q = question.strip()

    prefixes = [
        "qu'est-ce que ",
        "qu est ce que ",
        "c'est quoi ",
        "explique-moi ",
        "explique moi ",
        "explique ",
        "décris ",
        "decris ",
        "résume ",
        "resume ",
        "analyse "
    ]

    q_min = q.lower()

    for prefixe in prefixes:
        if q_min.startswith(prefixe):
            q = q[len(prefixe):].strip()
            break

    q = q.rstrip(" ?!.")

    return q






def mia_synthetiser_reponse(question, sources):
    """
    Brique de synthèse locale V63.

    Transforme les sources principales en réponse concise,
    puis utilise éventuellement la mémoire expérientielle
    comme contexte complémentaire.

    La mémoire expérientielle ne devient jamais une connaissance
    principale et ne remplace jamais les sources actuelles.
    Aucun contenu mémorisé n'est modifié.
    Aucune action n'est exécutée.
    """

    if not isinstance(question, str) or not question.strip():
        return ""

    if not isinstance(sources, list) or not sources:
        return ""

    question_basse = question.strip().lower()

    # ----------------------------------------------------
    # Séparation des sources
    # ----------------------------------------------------
    sources_principales = [
        source for source in sources
        if source.get("type") != "memoire_experientielle"
    ]

    memoires_experientielles = [
        source for source in sources
        if source.get("type") == "memoire_experientielle"
    ]

    sources_triees = sorted(
        sources_principales,
        key=lambda s: (
            s.get("pertinence", 0) or 0,
            1 if s.get("type") == "connaissance" else 0
        ),
        reverse=True
    )

    # ----------------------------------------------------
    # Réponse spécialisée ALKAH-BRAIN
    # ----------------------------------------------------
    if "alkah-brain" in question_basse and (
        "qu'est-ce" in question_basse
        or "qu'est ce" in question_basse
        or "c'est quoi" in question_basse
    ):
        return (
            "ALKAH-BRAIN est un projet de cerveau numérique local "
            "et l'architecture qui se trouve derrière MIA. "
            "Il constitue la fondation du système et réunit notamment "
            "la mémoire, le raisonnement, l'analyse du contexte "
            "et l'apprentissage basé sur l'expérience."
        )

    # ----------------------------------------------------
    # Réponse spécialisée MIA
    # ----------------------------------------------------
    if "mia" in question_basse and "qui es-tu" in question_basse:
        return (
            "Je suis MIA, une interface intelligente conçue pour "
            "faciliter la technologie. Je peux accompagner l'utilisateur "
            "simplement, sans lui demander de connaître les aspects "
            "techniques de l'intelligence artificielle."
        )

    if "mia" in question_basse and "que peut faire" in question_basse:
        return (
            "MIA peut aider à comprendre une information, trouver une "
            "réponse, organiser des connaissances, analyser un problème, "
            "comparer des possibilités, prendre une décision, créer un "
            "plan d'action, automatiser certaines tâches et accompagner "
            "l'utilisateur étape par étape."
        )

    # ----------------------------------------------------
    # Synthèse des connaissances principales
    # ----------------------------------------------------
    morceaux = []

    for source in sources_triees[:3]:
        contenu = (source.get("contenu") or "").strip()

        if not contenu:
            continue

        phrases = [
            p.strip()
            for p in contenu.replace("\n", " ").split(".")
            if p.strip()
        ]

        for phrase in phrases:
            phrase_normalisee = " ".join(
                phrase.lower().split()
            )

            deja_present = any(
                phrase_normalisee == " ".join(
                    existante.lower().split()
                )
                for existante in morceaux
            )

            if not deja_present:
                morceaux.append(phrase)

    # ----------------------------------------------------
    # Ajout contrôlé de l'expérience passée
    # ----------------------------------------------------
    experiences = []

    for memoire in memoires_experientielles[:1]:
        contenu = (memoire.get("contenu") or "").strip()

        if contenu:
            contenu = contenu.strip()

            # Nettoyage des répétitions introduites par le contexte mémoire.
            contenu = contenu.replace(
                "Expérience précédente : ",
                "Question précédente : ",
                1
            )

            contenu = contenu.replace(
                "..",
                "."
            )

            experiences.append(
                "Expérience antérieure pertinente : " + contenu
            )

    if not morceaux and not experiences:
        return ""

    reponse = ". ".join(morceaux[:3]).strip()

    if reponse and not reponse.endswith("."):
        reponse += "."

    if experiences:
        if reponse:
            reponse += "\n" + experiences[0]
        else:
            reponse = experiences[0]

    return reponse


def mia_generer_reponse(question):
    execution = mia_executer_action(question)

    if execution.get("intention") == "salutation":
        return {
            "question": question,
            "intention": "salutation",
            "confiance": {
                "niveau": 3,
                "score": 100,
                "statut": "tres_fiable",
                "autoriser_reponse": True
            },
            "coherence": {
                "score": 100,
                "statut": "coherente"
            },
            "fiabilite_globale": {
                "score": 100,
                "statut": "tres_fiable"
            },
            "decision": {
                "decision": "repondre",
                "niveau": 3,
                "raison": "salutation",
                "autoriser": True
            },
            "justification": "Salutation reconnue directement.",
            "trace": None,
            "experience": None,
            "reponse": (
                "Bonjour ! Je suis MIA, l'interface intelligente "
                "d'ALKAH-BRAIN. Comment puis-je vous aider ?"
            ),
            "sources": [],
            "mia25": execution.get("mia25"),
            "memoire_apprentissage": {
                "nombre_memoires": 0,
                "nombre_resultats": 0,
                "selection": None,
                "contexte": None
            }
        }

    if execution.get("intention") == "identite_mia":
        q = question.strip().lower()

        if any(mot in q for mot in [
            "que peux-tu faire", "que pouvez-vous faire",
            "à quoi sers-tu", "a quoi sers-tu",
            "quel est ton rôle", "quel est ton role",
            "que peut faire"
        ]):
            reponse_identite = (
                "Je suis MIA, l'interface intelligente d'ALKAH-BRAIN. "
                "Je peux aider l'utilisateur à rechercher, comprendre, "
                "analyser et synthétiser des informations, avec une réponse "
                "adaptée au niveau de confiance du système."
            )
        else:
            reponse_identite = (
                "Je suis MIA, l'interface intelligente d'ALKAH-BRAIN. "
                "Je suis conçue pour faciliter l'utilisation du système "
                "et accompagner l'utilisateur simplement."
            )

        return {
            "question": question,
            "intention": "identite_mia",
            "confiance": {
                "niveau": 3,
                "score": 100,
                "statut": "tres_fiable",
                "autoriser_reponse": True
            },
            "coherence": {
                "score": 100,
                "statut": "coherente"
            },
            "fiabilite_globale": {
                "score": 100,
                "statut": "tres_fiable"
            },
            "decision": {
                "decision": "repondre",
                "niveau": 3,
                "raison": "identite_mia",
                "autoriser": True
            },
            "justification": "Identité ou capacités de MIA reconnues directement.",
            "trace": None,
            "experience": None,
            "reponse": reponse_identite,
            "sources": [],
            "mia25": execution.get("mia25"),
            "memoire_apprentissage": {
                "nombre_memoires": 0,
                "nombre_resultats": 0,
                "selection": None,
                "contexte": None
            }
        }

    resultat = execution["resultat"]
    intention = execution["intention"]
    mia25_resultat = execution.get("mia25")

    # MÉMOIRE D'APPRENTISSAGE V63 — recherche globale sécurisée
    # La mémoire reste indépendante des sources principales.
    memoires_apprentissage = mia_charger_memoires_apprentissage_sqlite()

    resultats_memoire = mia_rechercher_memoire_apprentissage(
        question,
        memoires_apprentissage
    )

    selection_memoire = mia_selectionner_meilleure_memoire_securisee(
        resultats_memoire
    )

    contexte_memoire = mia_preparer_contexte_memoire_selectionnee(
        selection_memoire
    )

    if not resultat:
        confiance = mia_evaluer_confiance(None)
        coherence = mia_evaluer_coherence([])

        fiabilite_globale = mia_evaluer_fiabilite_globale(
            confiance,
            coherence,
            []
        )

        decision = mia_decider_reponse(fiabilite_globale)

        justification = mia_justifier_decision(
            decision,
            fiabilite_globale
        )

        trace = mia_creer_trace_decision(
            question,
            [],
            confiance,
            coherence,
            fiabilite_globale,
            decision,
            justification
        )

        experience = mia_creer_experience_decision(
            question,
            decision,
            fiabilite_globale,
            justification,
            []
        )

        return {
            "question": question,
            "intention": intention,
            "confiance": confiance,
            "coherence": coherence,
            "fiabilite_globale": fiabilite_globale,
            "decision": decision,
            "justification": justification,
            "trace": trace,
            "experience": experience,
            "reponse": mia_formuler_niveau_confiance(confiance),
            "sources": [],
            "mia25": mia25_resultat,
            "memoire_apprentissage": {
                "nombre_memoires": len(memoires_apprentissage),
                "nombre_resultats": len(resultats_memoire),
                "selection": selection_memoire,
                "contexte": contexte_memoire
            }
        }

    sources = mia_selectionner_sources(resultat)
    resultat_selection = {
        "souvenirs": sources
    }

    confiance = mia_evaluer_confiance(resultat_selection)
    coherence = mia_evaluer_coherence(sources)

    fiabilite_globale = mia_evaluer_fiabilite_globale(
        confiance,
        coherence,
        sources
    )

    decision = mia_decider_reponse(fiabilite_globale)

    justification = mia_justifier_decision(
        decision,
        fiabilite_globale
    )

    trace = mia_creer_trace_decision(
        question,
        sources,
        confiance,
        coherence,
        fiabilite_globale,
        decision,
        justification
    )

    experience = mia_creer_experience_decision(
        question,
        decision,
        fiabilite_globale,
        justification,
        sources
    )

    niveau_confiance = mia_formuler_niveau_decision(decision)

    if not confiance["autoriser_reponse"]:
        return {
            "question": question,
            "intention": intention,
            "confiance": confiance,
            "coherence": coherence,
            "fiabilite_globale": fiabilite_globale,
            "decision": decision,
            "justification": justification,
            "trace": trace,
            "experience": experience,
            "reponse": niveau_confiance,
            "sources": [],
            "mia25": mia25_resultat,
            "memoire_apprentissage": {
                "nombre_memoires": len(memoires_apprentissage),
                "nombre_resultats": len(resultats_memoire),
                "selection": selection_memoire,
                "contexte": contexte_memoire
            }
        }

    # MÉMOIRE D'APPRENTISSAGE V63 — injection sécurisée dans le contexte
    # Une mémoire bloquée par conflit ne peut jamais être injectée.
    sources_synthese = list(sources)

    if contexte_memoire:
        sources_synthese.append({
            "titre": "Mémoire expérientielle sécurisée",
            "contenu": (
                "Expérience précédente : "
                + str(contexte_memoire.get("question_precedente", ""))
                + ". Décision précédente : "
                + str(contexte_memoire.get("decision", ""))
                + ". Leçon : "
                + str(contexte_memoire.get("lecon", ""))
                + ". Qualité de l'expérience : "
                + str(contexte_memoire.get("qualite", 0))
            ),
            "pertinence": contexte_memoire.get("score_selection", 0),
            "type": "memoire_experientielle"
        })

    reponse_synthetisee = mia_synthetiser_reponse(
        question,
        sources_synthese
    )

    if reponse_synthetisee:
        reponse = reponse_synthetisee
    else:
        combinaison = mia_combiner_sources(sources)
        contenu = combinaison["contenu"]

        if intention == "synthese":
            reponse = (
                "Voici la synthèse des connaissances mémorisées :\n"
                + contenu
            )

        elif intention == "explication":
            reponse = (
                "D'après les connaissances mémorisées dans ALKAH-BRAIN :\n"
                + contenu
            )

        elif intention == "analyse":
            reponse = (
                "Analyse basée uniquement sur les connaissances mémorisées :\n"
                + contenu
            )

        else:
            reponse = (
                "J'ai trouvé les connaissances suivantes dans ALKAH-BRAIN :\n"
                + contenu
            )

    if mia25_resultat:
        if mia25_resultat.get("option_recommandee"):
            reponse += (
                "\n\nMIA25 — Analyse décisionnelle :\n"
                "Option recommandée : "
                + str(mia25_resultat.get("option_recommandee"))
                + "\nScore indicatif : "
                + str(mia25_resultat.get("score"))
                + "/30"
                + "\nNiveau de confiance : "
                + str(mia25_resultat.get("niveau_confiance"))
                + "\nValidation humaine requise : Oui"
                + "\nAucune exécution automatique n'est autorisée."
            )
        elif mia25_resultat.get("statut"):
            reponse += (
                "\n\nMIA25 — Analyse décisionnelle :\n"
                + str(mia25_resultat.get("statut"))
            )

    reponse = reponse

    return {
        "question": question,
        "intention": intention,
        "confiance": confiance,
        "coherence": coherence,
        "fiabilite_globale": fiabilite_globale,
        "decision": decision,
        "justification": justification,
        "trace": trace,
        "experience": experience,
        "reponse": reponse,
        "sources": sources,
        "mia25": mia25_resultat,

        # MÉMOIRE D'APPRENTISSAGE V63 — informations de contexte
        "memoire_apprentissage": {
            "nombre_memoires": len(memoires_apprentissage),
            "nombre_resultats": len(resultats_memoire),
            "selection": selection_memoire,
            "contexte": contexte_memoire
        }
    }


def mia_evaluer_confiance(resultat):
    if not resultat or not resultat.get("souvenirs"):
        return {
            "niveau": 0,
            "score": 0,
            "statut": "insuffisant",
            "autoriser_reponse": False
        }

    pertinences = [
        s.get("pertinence", 0) or 0
        for s in resultat["souvenirs"]
    ]

    meilleur_score = max(pertinences)

    if meilleur_score >= 90:
        niveau = 3
        statut = "fort"
        autoriser = True
    elif meilleur_score >= 70:
        niveau = 2
        statut = "correct"
        autoriser = True
    elif meilleur_score >= 40:
        niveau = 1
        statut = "faible"
        autoriser = True
    else:
        niveau = 0
        statut = "insuffisant"
        autoriser = False

    return {
        "niveau": niveau,
        "score": meilleur_score,
        "statut": statut,
        "autoriser_reponse": autoriser
    }



def mia_formuler_niveau_decision(decision):
    """
    Formule le niveau de réponse à partir de la décision finale de MIA V35.

    La formulation affichée doit correspondre à la décision issue
    de la fiabilité globale, et non uniquement au meilleur score
    d'une source.
    """
    if not decision:
        return "Je ne dispose pas encore de suffisamment de connaissances."

    niveau = decision.get("niveau", 0) or 0

    if niveau >= 3:
        return "Je peux vous répondre avec confiance."

    if niveau == 2:
        return (
            "Je dispose d'une connaissance correcte sur ce sujet, "
            "mais elle peut être incomplète. Je réponds donc avec réserve."
        )

    if niveau == 1:
        return (
            "Je dispose d'une connaissance partielle sur ce sujet. "
            "Je vais donc répondre avec prudence."
        )

    return (
        "Je ne dispose pas de connaissances suffisantes "
        "pour répondre de manière fiable."
    )


def mia_formuler_niveau_confiance(confiance):
    if not confiance:
        return "Je ne dispose pas encore de suffisamment de connaissances."

    niveau = confiance.get("niveau", 0)

    if niveau >= 3:
        return (
            "Je peux vous répondre avec confiance."
        )

    if niveau == 2:
        return (
            "Je dispose d'une connaissance correcte sur ce sujet, "
            "mais elle peut être incomplète."
        )

    if niveau == 1:
        return (
            "Je dispose d'une connaissance partielle sur ce sujet. "
            "Je vais donc répondre avec prudence."
        )

    return (
        "Je ne dispose pas de connaissances suffisantes "
        "pour répondre de manière fiable."
    )



def mia_selectionner_sources(resultat, seuil=40):
    """
    Sélectionne les sources utilisables par MIA V35.

    Règles :
    - uniquement les souvenirs actifs ;
    - respect du seuil de pertinence ;
    - priorité aux connaissances ;
    - les projets restent utilisables ;
    - les autres types restent possibles mais secondaires ;
    - aucun contenu mémorisé n'est modifié.
    """
    if not resultat or not resultat.get("souvenirs"):
        return []

    priorite_type = {
        "connaissance": 1,
        "projet": 2
    }

    sources = []

    for souvenir in resultat["souvenirs"]:
        pertinence = souvenir.get("pertinence", 0) or 0
        statut = souvenir.get("statut", "actif")

        if statut != "actif":
            continue

        if pertinence < seuil:
            continue

        type_souvenir = souvenir.get("type", "autre")

        sources.append(souvenir)

    sources.sort(
        key=lambda s: (
            priorite_type.get(s.get("type", "autre"), 3),
            -(s.get("pertinence", 0) or 0)
        )
    )

    return sources


def mia_combiner_sources(sources):
    if not sources:
        return {
            "nombre_sources": 0,
            "contenu": ""
        }

    lignes = []

    for source in sources:
        titre = source.get("titre", "Source sans titre")
        contenu = source.get("contenu", "")

        lignes.append(
            f"{titre} : {contenu}"
        )

    return {
        "nombre_sources": len(sources),
        "contenu": "\n".join(lignes)
    }



def mia_evaluer_coherence(sources):
    if not sources:
        return {
            "niveau": 0,
            "score": 0,
            "statut": "aucune_source",
            "coherent": False
        }

    if len(sources) == 1:
        return {
            "niveau": 3,
            "score": 100,
            "statut": "source_unique",
            "coherent": True
        }

    pertinences = [
        s.get("pertinence", 0) or 0
        for s in sources
    ]

    moyenne = sum(pertinences) / len(pertinences)

    score = min(100, int(moyenne))

    if score >= 80:
        niveau = 3
        statut = "forte_coherence"
        coherent = True
    elif score >= 60:
        niveau = 2
        statut = "coherence_correcte"
        coherent = True
    else:
        niveau = 1
        statut = "coherence_faible"
        coherent = False

    return {
        "niveau": niveau,
        "score": score,
        "statut": statut,
        "coherent": coherent,
        "nombre_sources": len(sources)
    }

def mia_evaluer_valeur_type_source(source):
    """
    Détermine le rôle d'une source dans l'évaluation V35.

    Cette fonction ne modifie aucun score et ne modifie
    aucun souvenir mémorisé.
    """
    if not source:
        return {
            "type": "autre",
            "role": "secondaire"
        }

    type_souvenir = source.get("type", "autre") or "autre"

    if type_souvenir == "connaissance":
        role = "principal"
    elif type_souvenir == "projet":
        role = "secondaire"
    elif type_souvenir == "test":
        role = "validation"
    else:
        role = "secondaire"

    return {
        "type": type_souvenir,
        "role": role
    }


def mia_evaluer_fiabilite_globale(confiance, coherence, sources):
    if not sources:
        return {
            "niveau": 0,
            "score": 0,
            "statut": "insuffisant",
            "autoriser_reponse": False,
            "pertinence_moyenne": 0
        }

    score_confiance = confiance.get("score", 0) or 0
    score_coherence = coherence.get("score", 0) or 0

    pertinences = [
        s.get("pertinence", 0) or 0
        for s in sources
    ]

    pertinence_moyenne = (
        sum(pertinences) / len(pertinences)
        if pertinences
        else 0
    )

    score_global = int(
        (
            score_confiance
            + score_coherence
            + pertinence_moyenne
        ) / 3
    )

    if score_global >= 90:
        niveau = 3
        statut = "fiabilite_forte"
        autoriser = True

    elif score_global >= 70:
        niveau = 2
        statut = "fiabilite_correcte"
        autoriser = True

    elif score_global >= 50:
        niveau = 1
        statut = "fiabilite_faible"
        autoriser = True

    else:
        niveau = 0
        statut = "fiabilite_insuffisante"
        autoriser = False

    return {
        "niveau": niveau,
        "score": score_global,
        "statut": statut,
        "autoriser_reponse": autoriser,
        "pertinence_moyenne": pertinence_moyenne
    }



def mia_decider_reponse(fiabilite_globale):
    if not fiabilite_globale:
        return {
            "decision": "refuser",
            "niveau": 0,
            "raison": "fiabilite_absente",
            "autoriser": False
        }

    niveau = fiabilite_globale.get("niveau", 0) or 0
    score = fiabilite_globale.get("score", 0) or 0

    if niveau >= 3 and score >= 90:
        return {
            "decision": "repondre",
            "niveau": 3,
            "raison": "fiabilite_forte",
            "autoriser": True
        }

    if niveau == 2 and score >= 70:
        return {
            "decision": "repondre_avec_reserve",
            "niveau": 2,
            "raison": "fiabilite_correcte",
            "autoriser": True
        }

    if niveau == 1 and score >= 50:
        return {
            "decision": "repondre_prudemment",
            "niveau": 1,
            "raison": "fiabilite_faible",
            "autoriser": True
        }

    return {
        "decision": "refuser",
        "niveau": 0,
        "raison": "fiabilite_insuffisante",
        "autoriser": False
    }



def mia_justifier_decision(decision, fiabilite_globale):
    if not decision:
        return "Aucune décision fiable n'a pu être établie."

    nom_decision = decision.get("decision", "refuser")
    raison = decision.get("raison", "raison_inconnue")
    score = fiabilite_globale.get("score", 0) if fiabilite_globale else 0

    if nom_decision == "repondre":
        return (
            "MIA répond car les connaissances disponibles présentent "
            "un niveau de fiabilité fort."
        )

    if nom_decision == "repondre_avec_reserve":
        return (
            "MIA répond avec réserve car les connaissances disponibles "
            "sont suffisamment fiables, mais ne sont pas totalement solides."
        )

    if nom_decision == "repondre_prudemment":
        return (
            "MIA répond prudemment car les connaissances disponibles "
            "sont limitées et leur fiabilité est faible."
        )

    return (
        "MIA refuse de répondre car les connaissances disponibles "
        "ne sont pas suffisantes pour produire une réponse fiable."
    )



def mia_creer_trace_decision(
    question,
    sources,
    confiance,
    coherence,
    fiabilite_globale,
    decision,
    justification
):
    return {
        "question": question,
        "nombre_sources": len(sources) if sources else 0,
        "confiance": confiance,
        "coherence": coherence,
        "fiabilite_globale": fiabilite_globale,
        "decision": decision,
        "justification": justification
    }





def mia_interpreter_experience_decision(resultat_recherche):
    """
    Extrait les informations utiles d'une expérience retrouvée.
    Ne modifie pas la décision actuelle de MIA.
    """

    if not resultat_recherche:
        return {
            "experience_trouvee": False,
            "message": "Aucune expérience pertinente trouvée."
        }

    experience = resultat_recherche.get("experience", {})

    decision = experience.get("decision", {})
    fiabilite = experience.get("fiabilite_globale", {})

    return {
        "experience_trouvee": True,
        "question": experience.get("question"),
        "decision": decision.get("decision"),
        "niveau_decision": decision.get("niveau"),
        "score_fiabilite": fiabilite.get("score"),
        "qualite": experience.get("qualite"),
        "statut_qualite": experience.get("statut_qualite"),
        "resultat_verifie": experience.get("resultat_verifie", False),
        "resultat_correct": experience.get("resultat_correct")
    }


def mia_rechercher_experience_decision(question, experiences):
    """
    Recherche les expériences décisionnelles liées à une question.
    La recherche reste simple et déterministe pour cette version.
    """

    if not question or not experiences:
        return []

    question_normalisee = question.lower().strip()
    resultats = []

    for experience in experiences:
        ancienne_question = experience.get("question", "").lower().strip()

        if not ancienne_question:
            continue

        mots = [
            mot for mot in question_normalisee.split()
            if len(mot) > 2
        ]

        correspondance = sum(
            1 for mot in mots
            if mot in ancienne_question
        )

        if correspondance > 0:
            resultats.append({
                "experience": experience,
                "correspondance": correspondance
            })

    resultats.sort(
        key=lambda element: element["correspondance"],
        reverse=True
    )

    return resultats


def mia_creer_experience_decision(
    question,
    decision,
    fiabilite_globale,
    justification,
    sources=None
):
    experience = {
        "question": question,
        "decision": decision,
        "fiabilite_globale": fiabilite_globale,
        "justification": justification,
        "nombre_sources": len(sources) if sources else 0,
        "qualite": None,
        "resultat_verifie": False
    }

    evaluation = mia_evaluer_experience_decision(experience)

    experience["qualite"] = evaluation["qualite"]
    experience["statut_qualite"] = evaluation["statut"]
    experience["resultat_verifie"] = evaluation["resultat_verifie"]

    return experience













def mia_preparer_contexte_memoire_selectionnee(selection):
    """
    Prépare la mémoire sélectionnée comme contexte complémentaire.

    Accepte :
    - une sélection directe ;
    - l'enveloppe retournée par la sélection sécurisée.

    Une sélection bloquée par conflit ne peut jamais entrer
    dans le contexte.
    """
    if not selection:
        return None

    # Si la sélection vient du verrou sécurisé,
    # récupérer la sélection interne.
    if selection.get("statut") == "selection_bloquee":
        return None

    selection_interne = selection.get("selection")

    if isinstance(selection_interne, dict):
        selection = selection_interne

    memoire = selection.get("memoire", {})

    if not memoire.get("utilisable", False):
        return None

    return {
        "type": "memoire_experientielle_selectionnee",
        "question_precedente": memoire.get("question"),
        "decision": memoire.get("decision"),
        "lecon": memoire.get("lecon"),
        "qualite": memoire.get("qualite", 0),
        "correspondance": selection.get("correspondance", 0),
        "score_selection": selection.get("score_selection", 0),
        "role": "contexte_complementaire",
        "source_selection": "memoire_apprentissage"
    }


def mia_expliquer_selection_memoire(selection):
    """
    Explique pourquoi une mémoire a été sélectionnée.
    """

    if not selection:
        return {
            "selection": False,
            "raison": "aucune_memoire_selectionnee"
        }

    memoire = selection.get("memoire", {})

    return {
        "selection": True,
        "question": memoire.get("question"),
        "qualite": memoire.get("qualite", 0),
        "correspondance": selection.get("correspondance", 0),
        "score_selection": selection.get("score_selection", 0),
        "raison": "meilleure_combinaison_qualite_correspondance"
    }














def mia_decider_contribution_memoire(
    verification_contribution,
    verification_coherence
):
    """
    Détermine si une mémoire peut être retenue
    comme contribution cohérente au contexte.
    La décision reste déterministe et transparente.
    """

    if not verification_contribution:
        return {
            "contribution": False,
            "decision": "rejeter",
            "raison": "verification_contribution_absente"
        }

    if not verification_coherence:
        return {
            "contribution": False,
            "decision": "rejeter",
            "raison": "verification_coherence_absente"
        }

    contribution = verification_contribution.get(
        "contribution",
        False
    )

    coherence = verification_coherence.get(
        "coherent",
        False
    )

    if not contribution:
        return {
            "contribution": False,
            "decision": "rejeter",
            "raison": "memoire_sans_contribution"
        }

    if not coherence:
        return {
            "contribution": False,
            "decision": "rejeter",
            "raison": "memoire_incoherente"
        }

    return {
        "contribution": True,
        "decision": "accepter",
        "raison": "memoire_coherente_et_contributive"
    }

def mia_verifier_coherence_memoire_resume(
    contexte_final,
    resume_memoire
):
    """
    Vérifie que le résumé de mémoire correspond à la mémoire
    effectivement présente dans le contexte final.

    Cette fonction ne modifie ni le contexte ni la mémoire.
    """

    if not contexte_final:
        return {
            "coherent": False,
            "raison": "contexte_absent"
        }

    if not resume_memoire:
        return {
            "coherent": False,
            "raison": "resume_absent"
        }

    memoire = contexte_final.get(
        "memoire_experientielle"
    )

    if not memoire:
        return {
            "coherent": False,
            "raison": "memoire_non_integree"
        }

    question_resume = resume_memoire.get(
        "question_precedente"
    )
    question_memoire = memoire.get(
        "question_precedente"
    )

    if question_resume != question_memoire:
        return {
            "coherent": False,
            "raison": "questions_memoire_differentes"
        }

    lecon_resume = resume_memoire.get("lecon")
    lecon_memoire = memoire.get("lecon")

    if lecon_resume != lecon_memoire:
        return {
            "coherent": False,
            "raison": "lecons_memoire_differentes"
        }

    return {
        "coherent": True,
        "raison": "resume_correspond_a_la_memoire_integree"
    }

def mia_verifier_contribution_memoire(
    contexte_final,
    resume_memoire
):
    """
    Vérifie si une mémoire résumée a réellement contribué
    au contexte final.
    La vérification reste descriptive et déterministe.
    """

    if not contexte_final:
        return {
            "contribution": False,
            "raison": "contexte_absent"
        }

    if not resume_memoire:
        return {
            "contribution": False,
            "raison": "resume_absent"
        }

    memoire = contexte_final.get(
        "memoire_experientielle"
    )

    if not memoire:
        return {
            "contribution": False,
            "raison": "memoire_non_integree"
        }

    if resume_memoire.get("utilisation") == "ne_pas_utiliser":
        return {
            "contribution": False,
            "raison": "memoire_rejetee"
        }

    return {
        "contribution": True,
        "raison": "memoire_integree_au_contexte",
        "utilisation": resume_memoire.get(
            "utilisation"
        ),
        "niveau": resume_memoire.get(
            "fiabilite_ajustee",
            0
        )
    }

def mia_resumer_memoire_utilisee(
    memoire,
    fiabilite_memoire,
    decision_utilisation
):
    """
    Produit un résumé simple de la mémoire utilisée.
    Le résumé ne modifie jamais la mémoire originale.
    """

    if not memoire:
        return {
            "resume": False,
            "raison": "memoire_absente"
        }

    if not fiabilite_memoire or not decision_utilisation:
        return {
            "resume": False,
            "raison": "evaluation_absente"
        }

    return {
        "resume": True,
        "question_precedente": memoire.get("question"),
        "lecon": memoire.get("lecon"),
        "qualite_originale": memoire.get("qualite", 0),
        "fiabilite_ajustee": fiabilite_memoire.get("fiabilite", 0),
        "utilisation": decision_utilisation.get(
            "utilisation",
            "ne_pas_utiliser"
        ),
        "raison": decision_utilisation.get(
            "raison",
            "raison_inconnue"
        ),
        "source": "memoire_apprentissage"
    }

def mia_tracer_utilisation_memoire(
    memoire,
    fiabilite_memoire,
    decision_utilisation
):
    """
    Crée une trace explicite de l'utilisation d'une mémoire.
    La mémoire originale n'est jamais modifiée.
    """

    if not memoire:
        return {
            "trace": False,
            "raison": "memoire_absente"
        }

    if not fiabilite_memoire or not decision_utilisation:
        return {
            "trace": False,
            "raison": "evaluation_absente"
        }

    utilisation = decision_utilisation.get("utilisation", "ne_pas_utiliser")

    return {
        "trace": True,
        "question": memoire.get("question"),
        "type_memoire": memoire.get("type"),
        "qualite_originale": memoire.get("qualite", 0),
        "fiabilite_ajustee": fiabilite_memoire.get("fiabilite", 0),
        "niveau": fiabilite_memoire.get("niveau", 0),
        "utilisation": utilisation,
        "raison_utilisation": decision_utilisation.get("raison"),
        "source": "memoire_apprentissage"
    }


def mia_integrer_contexte_memoire(contexte_actuel, contexte_memoire):
    """
    Intègre une mémoire validée au contexte actuel.
    La mémoire reste toujours un contexte complémentaire.
    """

    if contexte_actuel is None:
        contexte_actuel = {}

    contexte_final = dict(contexte_actuel)

    if not contexte_memoire:
        contexte_final["memoire_experientielle"] = None
        return contexte_final

    utilisation = contexte_memoire.get("utilisation")

    if utilisation == "ne_pas_utiliser":
        contexte_final["memoire_experientielle"] = None
        return contexte_final

    contexte_final["memoire_experientielle"] = contexte_memoire
    contexte_final["memoire_role"] = "contexte_complementaire"

    return contexte_final


def mia_preparer_contexte_memoire_ajustee(
    memoire,
    fiabilite_memoire,
    decision_utilisation
):
    """
    Prépare le contexte mémoire après ajustement de fiabilité.
    Une mémoire rejetée ne peut pas entrer dans le contexte final.
    """

    if not memoire:
        return None

    if not fiabilite_memoire or not decision_utilisation:
        return None

    utilisation = decision_utilisation.get("utilisation")

    if utilisation == "ne_pas_utiliser":
        return None

    return {
        "type": "memoire_experientielle_ajustee",
        "question_precedente": memoire.get("question"),
        "lecon": memoire.get("lecon"),
        "qualite_originale": memoire.get("qualite", 0),
        "fiabilite_ajustee": fiabilite_memoire.get("fiabilite", 0),
        "niveau": fiabilite_memoire.get("niveau", 0),
        "utilisation": utilisation,
        "role": "contexte_complementaire",
        "source": "memoire_apprentissage"
    }


def mia_decider_utilisation_memoire(fiabilite_memoire):
    """
    Détermine comment une mémoire ajustée peut être utilisée.
    La mémoire ne devient jamais une vérité principale.
    """

    if not fiabilite_memoire:
        return {
            "utilisation": "ne_pas_utiliser",
            "niveau": 0,
            "raison": "evaluation_absente"
        }

    niveau = fiabilite_memoire.get("niveau", 0)

    if niveau >= 3:
        return {
            "utilisation": "utiliser",
            "niveau": 3,
            "raison": "fiabilite_forte"
        }

    if niveau >= 1:
        return {
            "utilisation": "utiliser_prudemment",
            "niveau": niveau,
            "raison": "fiabilite_limitee"
        }

    return {
        "utilisation": "ne_pas_utiliser",
        "niveau": 0,
        "raison": "fiabilite_insuffisante"
    }


def mia_ajuster_fiabilite_memoire(memoire, evaluation_conflit):
    """
    Ajuste prudemment le niveau d'utilisation d'une mémoire
    selon la présence éventuelle d'un conflit.
    La mémoire originale n'est jamais modifiée.
    """

    if not memoire:
        return {
            "fiabilite": 0,
            "niveau": 0,
            "raison": "memoire_absente"
        }

    qualite = memoire.get("qualite", 0)

    if not evaluation_conflit:
        return {
            "fiabilite": qualite,
            "niveau": qualite,
            "raison": "evaluation_absente"
        }

    if evaluation_conflit.get("niveau", 0) >= 2:
        return {
            "fiabilite": max(0, qualite - 1),
            "niveau": max(0, qualite - 1),
            "raison": "fiabilite_reduite_par_conflit"
        }

    return {
        "fiabilite": qualite,
        "niveau": qualite,
        "raison": "fiabilite_conservee"
    }


def mia_evaluer_conflit_memoires(conflit):
    """
    Évalue la situation créée par un éventuel conflit entre mémoires.
    Un conflit ne doit jamais être ignoré silencieusement.
    """

    if not conflit:
        return {
            "niveau": 0,
            "action": "prudence",
            "raison": "conflit_absent"
        }

    if not conflit.get("conflit", False):
        return {
            "niveau": 0,
            "action": "continuer",
            "raison": "memoires_coherentes"
        }

    nombre_decisions = conflit.get("nombre_decisions", 0)

    if nombre_decisions >= 2:
        return {
            "niveau": 2,
            "action": "repondre_prudemment",
            "raison": "conflit_memoires_detecte"
        }

    return {
        "niveau": 1,
        "action": "prudence",
        "raison": "conflit_indetermine"
    }


def mia_charger_memoires_apprentissage_sqlite():
    """
    Charge les mémoires d'apprentissage persistées dans SQLite.

    Retourne une liste de dictionnaires compatibles avec
    mia_rechercher_memoire_apprentissage().

    La base SQLite reste la source persistante.
    Aucune mémoire n'est modifiée pendant le chargement.
    """
    import sqlite3

    memoires = []

    try:
        c = sqlite3.connect(DB)

        lignes_db = c.execute("""
            SELECT
                id,
                type,
                question,
                decision,
                qualite,
                lecon,
                utilisable,
                created_at
            FROM mia_learning_memory
            ORDER BY id DESC
        """).fetchall()

        c.close()

        for ligne in lignes_db:
            memoires.append({
                "id": ligne[0],
                "type": ligne[1],
                "question": ligne[2],
                "decision": ligne[3],
                "qualite": ligne[4],
                "lecon": ligne[5],
                "utilisable": bool(ligne[6]),
                "created_at": ligne[7],
            })

    except Exception:
        return []

    return memoires
def mia_detecter_conflit_memoires(comparaison):
    """
    Détecte un éventuel conflit entre les mémoires candidates.
    Un conflit existe lorsque plusieurs mémoires utilisables
    présentent des décisions différentes.
    """

    if not comparaison:
        return {
            "conflit": False,
            "raison": "aucune_memoire"
        }

    decisions = set()

    for element in comparaison:
        decision = element.get("decision")
        if decision:
            decisions.add(decision)

    if len(decisions) <= 1:
        return {
            "conflit": False,
            "raison": "decisions_coherentes"
        }

    return {
        "conflit": True,
        "raison": "decisions_differentes",
        "nombre_decisions": len(decisions),
        "decisions": list(decisions)
    }


def mia_comparer_memoires(resultats):
    """
    Compare les mémoires candidates avant leur sélection.
    La comparaison reste déterministe et transparente.
    La décision est conservée pour permettre la détection des conflits.
    """
    if not resultats:
        return []

    comparaison = []

    for resultat in resultats:
        memoire = resultat.get("memoire", {})

        if not memoire.get("utilisable", False):
            continue

        qualite = memoire.get("qualite", 0)
        correspondance = resultat.get("correspondance", 0)
        score = qualite * 10 + correspondance

        comparaison.append({
            "question": memoire.get("question"),
            "decision": memoire.get("decision"),
            "qualite": qualite,
            "correspondance": correspondance,
            "score": score,
            "type": memoire.get("type")
        })

    comparaison.sort(
        key=lambda element: element["score"],
        reverse=True
    )

    return comparaison
def mia_selectionner_meilleure_memoire(resultats):
    """
    Sélectionne la mémoire d'apprentissage la plus pertinente.

    La sélection repose sur la qualité de la mémoire
    et sa correspondance avec la question.

    Une mémoire trop éloignée de la question est refusée
    avant toute injection dans le contexte.
    """

    MIN_CORRESPONDANCE_MEMOIRE = 5

    if not resultats:
        return None

    candidats = []

    for resultat in resultats:
        memoire = resultat.get("memoire", {})

        if not memoire.get("utilisable", False):
            continue

        qualite = memoire.get("qualite", 0)
        correspondance = resultat.get("correspondance", 0)

        # Filtrage de pertinence avant sélection.
        if correspondance < MIN_CORRESPONDANCE_MEMOIRE:
            continue

        score_selection = (qualite * 10) + correspondance

        candidats.append({
            "memoire": memoire,
            "correspondance": correspondance,
            "score_selection": score_selection
        })

    if not candidats:
        return None

    candidats.sort(
        key=lambda element: element["score_selection"],
        reverse=True
    )

    return candidats[0]


def mia_filtrer_memoires_conflit(comparaison):
    """
    Filtre les mémoires réellement pertinentes avant la détection
    d'un conflit.

    Seules les mémoires ayant la meilleure correspondance sont
    utilisées pour déterminer une contradiction décisionnelle.
    Les mémoires moins pertinentes restent disponibles comme
    contexte potentiel mais ne déclenchent pas le conflit.
    """
    if not comparaison:
        return []

    correspondances = [
        element.get("correspondance", 0)
        for element in comparaison
        if isinstance(element, dict)
    ]

    if not correspondances:
        return []

    meilleure_correspondance = max(correspondances)

    return [
        element
        for element in comparaison
        if isinstance(element, dict)
        and element.get("correspondance", 0) == meilleure_correspondance
    ]


def mia_selectionner_meilleure_memoire_securisee(resultats):
    """
    Sélectionne une mémoire uniquement si aucune contradiction
    entre mémoires utilisables n'est détectée.

    En cas de conflit, aucune mémoire n'est sélectionnée
    automatiquement. MIA doit répondre prudemment.
    """
    if not resultats:
        return {
            "selection": None,
            "statut": "aucune_memoire",
            "raison": "aucun_resultat",
            "action": "prudence"
        }

    comparaison = mia_comparer_memoires(resultats)

    # Seules les mémoires les plus pertinentes participent
    # à la détection d'un conflit décisionnel.
    comparaison_conflit = mia_filtrer_memoires_conflit(comparaison)

    conflit = mia_detecter_conflit_memoires(comparaison_conflit)
    evaluation = mia_evaluer_conflit_memoires(conflit)

    if conflit.get("conflit", False):
        return {
            "selection": None,
            "statut": "selection_bloquee",
            "raison": "conflit_memoires_detecte",
            "niveau_conflit": evaluation.get("niveau", 0),
            "action": "repondre_prudemment",
            "nombre_decisions": conflit.get("nombre_decisions", 0),
            "decisions": conflit.get("decisions", []),
            "donnees_modifiees": False
        }

    selection = mia_selectionner_meilleure_memoire(resultats)

    return {
        "selection": selection,
        "statut": "selection_validee" if selection else "aucune_selection",
        "raison": "aucun_conflit",
        "action": "utiliser_memoire" if selection else "prudence",
        "donnees_modifiees": False
    }


def mia_preparer_contexte_memoire(
    memoire_interpretee,
    evaluation_memoire
):
    """
    Prépare une mémoire validée comme contexte complémentaire.
    La mémoire ne devient jamais une source principale de vérité.
    """

    if not memoire_interpretee or not evaluation_memoire:
        return None

    if not evaluation_memoire.get("utilisable", False):
        return None

    return {
        "type": "memoire_experientielle",
        "niveau": evaluation_memoire.get("niveau", 0),
        "question_precedente": memoire_interpretee.get("question"),
        "lecon": memoire_interpretee.get("lecon"),
        "qualite": memoire_interpretee.get("qualite", 0),
        "correspondance": memoire_interpretee.get("correspondance", 0),
        "role": "contexte_complementaire"
    }


def mia_evaluer_memoire_apprentissage(memoire_interpretee):
    """
    Évalue si une mémoire d'apprentissage peut être utilisée
    comme contexte complémentaire.

    La mémoire ne remplace jamais les connaissances actuelles.
    """

    if not memoire_interpretee:
        return {
            "utilisable": False,
            "niveau": 0,
            "raison": "memoire_absente"
        }

    if not memoire_interpretee.get("memoire_trouvee", False):
        return {
            "utilisable": False,
            "niveau": 0,
            "raison": "memoire_non_trouvee"
        }

    if not memoire_interpretee.get("utilisable", False):
        return {
            "utilisable": False,
            "niveau": 0,
            "raison": "memoire_non_utilisable"
        }

    qualite = memoire_interpretee.get("qualite", 0)
    correspondance = memoire_interpretee.get("correspondance", 0)

    if qualite >= 3 and correspondance >= 2:
        return {
            "utilisable": True,
            "niveau": 3,
            "raison": "memoire_forte"
        }

    if qualite >= 1 and correspondance >= 1:
        return {
            "utilisable": True,
            "niveau": 1,
            "raison": "memoire_prudente"
        }

    return {
        "utilisable": False,
        "niveau": 0,
        "raison": "qualite_insuffisante"
    }


def mia_interpreter_memoire_apprentissage(resultat_recherche):
    """
    Extrait les informations utiles de la meilleure mémoire retrouvée.
    Accepte une liste de résultats de recherche ou un résultat individuel.
    Ne modifie pas la décision actuelle de MIA.
    """
    if not resultat_recherche:
        return {
            "memoire_trouvee": False,
            "message": "Aucune mémoire d'apprentissage pertinente trouvée."
        }

    if isinstance(resultat_recherche, list):
        resultat_recherche = resultat_recherche[0] if resultat_recherche else {}

    if not isinstance(resultat_recherche, dict):
        return {
            "memoire_trouvee": False,
            "message": "Résultat de recherche invalide."
        }

    memoire = resultat_recherche.get("memoire", {})

    if not isinstance(memoire, dict):
        return {
            "memoire_trouvee": False,
            "message": "Mémoire retrouvée invalide."
        }

    if not memoire.get("utilisable", False):
        return {
            "memoire_trouvee": False,
            "message": "La mémoire retrouvée n'est pas utilisable."
        }

    return {
        "memoire_trouvee": True,
        "type": memoire.get("type"),
        "question": memoire.get("question"),
        "decision": memoire.get("decision"),
        "qualite": memoire.get("qualite"),
        "lecon": memoire.get("lecon"),
        "utilisable": memoire.get("utilisable", False),
        "correspondance": resultat_recherche.get("correspondance", 0)
    }
def mia_rechercher_memoire_apprentissage(question, memoires):
    """
    Recherche les mémoires d'apprentissage pertinentes
    pour une nouvelle question.
    """

    if not question or not memoires:
        return []

    question_normalisee = question.lower().strip()
    resultats = []

    for memoire in memoires:
        ancienne_question = memoire.get("question", "").lower().strip()

        if not ancienne_question:
            continue

        mots = mots_significatifs(question_normalisee)
        mots_ancienne_question = mots_significatifs(ancienne_question)

        correspondance = len(mots.intersection(mots_ancienne_question))

        if correspondance > 0:
            resultats.append({
                "memoire": memoire,
                "correspondance": correspondance
            })

    resultats.sort(
        key=lambda element: element["correspondance"],
        reverse=True
    )

    return resultats


def mia_creer_memoire_apprentissage(apprentissage):
    """
    Crée une mémoire d'apprentissage à partir d'une leçon validée.
    La mémoire reste indépendante de la décision actuelle de MIA.
    """

    if not apprentissage:
        return None

    if not apprentissage.get("apprentissage", False):
        return None

    return {
        "type": apprentissage.get("type"),
        "question": apprentissage.get("question"),
        "decision": apprentissage.get("decision"),
        "qualite": apprentissage.get("qualite", 0),
        "lecon": apprentissage.get("lecon"),
        "utilisable": True
    }



def mia_sauvegarder_memoire_apprentissage(memoire):
    """
    Sauvegarde une mémoire d'apprentissage validée dans SQLite.
    La mémoire Python originale n'est jamais modifiée.
    """

    if not memoire:
        return {
            "sauvegardee": False,
            "raison": "memoire_absente"
        }

    if not isinstance(memoire, dict):
        return {
            "sauvegardee": False,
            "raison": "memoire_invalide"
        }

    if not memoire.get("question"):
        return {
            "sauvegardee": False,
            "raison": "question_absente"
        }

    if not memoire.get("type"):
        return {
            "sauvegardee": False,
            "raison": "type_absent"
        }

    maintenant = datetime.datetime.now().isoformat()

    c = sqlite3.connect(DB)

    c.execute(
        """
        INSERT INTO mia_learning_memory
        (type, question, decision, qualite, lecon, utilisable, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            memoire.get("type"),
            memoire.get("question"),
            memoire.get("decision"),
            memoire.get("qualite", 0),
            memoire.get("lecon"),
            1 if memoire.get("utilisable", True) else 0,
            maintenant
        )
    )

    identifiant = c.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    c.commit()
    c.close()

    return {
        "sauvegardee": True,
        "id": identifiant,
        "source": "mia_learning_memory"
    }


def mia_extraire_apprentissage_experience(experience):
    """
    Extrait une leçon uniquement à partir d'une expérience vérifiée.
    Aucun apprentissage n'est produit si le résultat n'a pas été vérifié.
    """

    if not experience:
        return {
            "apprentissage": False,
            "raison": "experience_absente"
        }

    if not experience.get("resultat_verifie", False):
        return {
            "apprentissage": False,
            "raison": "experience_non_verifiee"
        }

    resultat_correct = experience.get("resultat_correct")

    if resultat_correct is True:
        return {
            "apprentissage": True,
            "type": "confirmation",
            "question": experience.get("question"),
            "decision": experience.get("decision", {}).get("decision"),
            "qualite": experience.get("qualite", 0),
            "lecon": "La décision prise a été confirmée."
        }

    if resultat_correct is False:
        return {
            "apprentissage": True,
            "type": "correction",
            "question": experience.get("question"),
            "decision": experience.get("decision", {}).get("decision"),
            "qualite": experience.get("qualite", 0),
            "lecon": "La décision prise n'a pas été confirmée."
        }

    return {
        "apprentissage": False,
        "raison": "resultat_invalide"
    }


def mia_reviser_qualite_experience(experience):
    """
    Révise la qualité d'une expérience après vérification.
    """

    if not experience:
        return {
            "qualite": 0,
            "statut": "experience_absente"
        }

    if not experience.get("resultat_verifie", False):
        return {
            "qualite": experience.get("qualite", 0),
            "statut": "non_verifiee"
        }

    resultat_correct = experience.get("resultat_correct")

    if resultat_correct is True:
        qualite = experience.get("qualite", 0)

        if qualite >= 3:
            statut = "confirmee_forte"
        elif qualite >= 1:
            statut = "confirmee"
        else:
            statut = "confirmee_faible"

    else:
        qualite = max(0, experience.get("qualite", 0) - 1)

        if qualite == 0:
            statut = "erreur_critique"
        else:
            statut = "qualite_diminuee"

    experience["qualite"] = qualite
    experience["statut_qualite"] = statut

    return {
        "qualite": qualite,
        "statut": statut
    }


def mia_verifier_experience_decision(experience, resultat_correct):
    """
    Vérifie après coup si une décision expérimentale était correcte.
    resultat_correct doit être True ou False.
    """

    if not experience:
        return {
            "verifie": False,
            "statut": "experience_absente"
        }

    if not isinstance(resultat_correct, bool):
        return {
            "verifie": False,
            "statut": "verification_invalide"
        }

    experience["resultat_verifie"] = True
    experience["resultat_correct"] = resultat_correct

    if resultat_correct:
        experience["verification"] = "confirmee"
    else:
        experience["verification"] = "non_confirmee"

    return {
        "verifie": True,
        "statut": experience["verification"],
        "resultat_correct": resultat_correct
    }


def mia_evaluer_experience_decision(experience):
    """
    Évalue automatiquement la qualité d'une expérience décisionnelle.
    Cette fonction ne modifie pas la décision originale.
    """

    if not experience:
        return {
            "qualite": 0,
            "statut": "experience_absente",
            "resultat_verifie": False
        }

    decision = experience.get("decision", {})
    fiabilite = experience.get("fiabilite_globale", {})

    score = fiabilite.get("score", 0)
    autoriser = decision.get("autoriser", False)

    if score >= 80 and autoriser:
        return {
            "qualite": 3,
            "statut": "experience_forte",
            "resultat_verifie": False
        }

    if score > 0 and autoriser:
        return {
            "qualite": 1,
            "statut": "experience_prudente",
            "resultat_verifie": False
        }

    return {
        "qualite": 0,
        "statut": "experience_refus",
        "resultat_verifie": False
    }


def interpreter_confiance(score):
    if score < 20:
        return "faible"
    elif score < 40:
        return "moderee"
    elif score < 60:
        return "moyenne"
    elif score < 80:
        return "forte"
    else:
        return "tres_forte"



def expliquer_similarite(
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    raisons = []

    if score_titre >= 30:
        raisons.append("le titre presente une similarite")

    if score_contenu >= 30:
        raisons.append("le contenu presente une similarite")

    if score_contexte is not None and score_contexte >= 20:
        raisons.append("le contexte presente une similarite")

    if relation:
        raisons.append("une relation existe entre les souvenirs")

    if not raisons:
        raisons.append("aucun signal fort detecte")

    return raisons





def analyser_signaux_presents(
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    signaux = []

    if score_titre >= 30:
        signaux.append("titre")

    if score_contenu >= 30:
        signaux.append("contenu")

    if score_contexte is not None and score_contexte >= 20:
        signaux.append("contexte")

    if relation:
        signaux.append("relation")

    return signaux


def construire_decision(
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    rapport = construire_rapport_decision(
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    score = rapport["score_global"]

    if score >= 60:
        decision = "probablement lies"
    elif score >= 30:
        decision = "possiblement lies"
    else:
        decision = "lien faible"

    return {
        "decision": decision,
        "score_global": score,
        "confiance": rapport["confiance"],
        "raisons": rapport["raisons"],
        "action": "aucune"
    }


def construire_rapport_decision(
    score_titre,
    score_contenu,
    score_contexte=None,
    relation=False
):
    score_global = calculer_score_global(
        score_titre,
        score_contenu,
        score_contexte
    )

    confiance = interpreter_confiance(
        score_global
    )

    raisons = expliquer_similarite(
        score_titre,
        score_contenu,
        score_contexte,
        relation
    )

    return {
        "score_global": score_global,
        "confiance": confiance,
        "raisons": raisons
    }


def calculer_score_global(
    score_titre,
    score_contenu,
    score_contexte=None
):
    signaux = []

    if score_titre is not None:
        signaux.append(("titre", score_titre, 0.30))

    if score_contenu is not None:
        signaux.append(("contenu", score_contenu, 0.40))

    if score_contexte is not None:
        signaux.append(("contexte", score_contexte, 0.30))

    if not signaux:
        return 0

    poids_total = sum(poids for _, _, poids in signaux)

    score = sum(
        valeur * poids
        for _, valeur, poids in signaux
    ) / poids_total

    return int(score)


def analyser_signaux_similarite(
    id1, titre1, contenu1, id2, titre2, contenu2
):
    score_titre = calculer_similarite(
        titre1,
        titre2
    )

    score_contenu = calculer_similarite(
        contenu1,
        contenu2
    )

    score_document = calculer_similarite_document(
        titre1,
        contenu1,
        titre2,
        contenu2
    )

    score_contexte = calculer_similarite_contextuelle(
        id1,
        id2
    )

    print("\n=== ANALYSE MULTI-SIGNAUX ===")
    print("Souvenir 1 :", titre1)
    print("Souvenir 2 :", titre2)
    print("Similarite titre :", score_titre, "%")
    print("Similarite contenu :", score_contenu, "%")
    print("Similarite documentaire :", score_document, "%")
    print("Similarite contextuelle :", score_contexte, "%")


def detecter_similaires():
    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title, content FROM documents ORDER BY id"
    ).fetchall()

    print("\n=== DETECTION DES SOUVENIRS SIMILAIRES ===")

    trouve = False

    for i in range(len(souvenirs)):
        for j in range(i + 1, len(souvenirs)):
            id1, titre1, contenu1 = souvenirs[i]
            id2, titre2, contenu2 = souvenirs[j]

            score = calculer_similarite_document(
                titre1,
                contenu1,
                titre2,
                contenu2
            )

            if score >= 30:
                trouve = True

                mots1 = mots_significatifs(
                    titre1 + " " + contenu1
                )
                mots2 = mots_significatifs(
                    titre2 + " " + contenu2
                )

                mots_communs = sorted(
                    mots1.intersection(mots2)
                )

                print("\nSouvenir 1 :", titre1)
                print("Souvenir 2 :", titre2)
                print("Similarite :", score, "%")
                print("Mots communs :", ", ".join(mots_communs))

    if not trouve:
        print("Aucun souvenir suffisamment similaire trouve.")

    c.close()


def detecter_doublons():
    c = sqlite3.connect(DB)

    doublons = c.execute(
        "SELECT title, content, COUNT(*) "
        "FROM documents "
        "GROUP BY title, content "
        "HAVING COUNT(*) > 1 "
        "ORDER BY COUNT(*) DESC"
    ).fetchall()

    print("\n=== DETECTION DES DOUBLONS ===")

    if not doublons:
        print("Aucun doublon exact trouve.")
    else:
        for titre, contenu, nombre in doublons:
            print("\nTitre :", titre)
            print("Occurrences :", nombre)
            print("Contenu :", contenu)

    c.close()


def voir_relations():
    c = sqlite3.connect(DB)

    resultats = c.execute(
        "SELECT d1.title, r.relation, d2.title "
        "FROM relations r "
        "JOIN documents d1 ON r.source_id=d1.id "
        "JOIN documents d2 ON r.target_id=d2.id"
    ).fetchall()

    c.close()

    if resultats:
        for source, relation, cible in resultats:
            print(source, "->", relation, "->", cible)
    else:
        print("Aucune relation.")


def rechercher_par_type():
    type_recherche = input("Type du souvenir : ")

    c = sqlite3.connect(DB)

    resultats = c.execute(
        "SELECT id, title, content, importance FROM documents "
        "WHERE type LIKE ? "
        "ORDER BY importance DESC",
        ("%" + type_recherche + "%",)
    ).fetchall()

    if resultats:
        for sid, titre, contenu, importance in resultats:
            print("\nTitre :", titre)
            print("Importance :", importance)
            print("Contenu :", contenu)
    else:
        print("Aucun souvenir de ce type trouve.")

    c.close()


def rechercher_contextuel():
    mot = input("Recherche contextuelle : ")

    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title, content, importance FROM documents "
        "WHERE title LIKE ? OR content LIKE ? "
        "ORDER BY importance DESC",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    for sid, titre, contenu, importance in souvenirs:
        print("\nTitre :", titre)
        print("Importance :", importance)
        print("Contenu :", contenu)

        relations = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.target_id=d.id "
            "WHERE r.source_id=?",
            (sid,)
        ).fetchall()

        for relation, cible in relations:
            print("Relation :", relation, "->", cible)

    if not souvenirs:
        print("Aucun souvenir trouve.")

    c.close()


def relations_bidirectionnelles():
    mot = input("Souvenir a explorer : ")

    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title FROM documents WHERE title LIKE ?",
        ("%" + mot + "%",)
    ).fetchall()

    for sid, titre in souvenirs:
        print("\nSouvenir :", titre)

        sortantes = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.target_id=d.id "
            "WHERE r.source_id=?",
            (sid,)
        ).fetchall()

        entrantes = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.source_id=d.id "
            "WHERE r.target_id=?",
            (sid,)
        ).fetchall()

        for relation, cible in sortantes:
            print("->", relation, "->", cible)

        for relation, source in entrantes:
            print("<-", relation, "<-", source)

    if not souvenirs:
        print("Aucun souvenir trouve.")

    c.close()


def voir_contexte_complet():
    mot = input("Sujet a explorer : ")

    c = sqlite3.connect(DB)

    souvenirs = c.execute(
        "SELECT id, title, content, type, importance FROM documents "
        "WHERE title LIKE ? OR content LIKE ? "
        "ORDER BY importance DESC",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    if not souvenirs:
        print("Aucun contexte trouve.")

    for sid, titre, contenu, type_souvenir, importance in souvenirs:
        print("\n=== CONTEXTE ===")
        print("Titre :", titre)
        print("Type :", type_souvenir)
        print("Importance :", importance)
        print("Contenu :", contenu)

        contextes = c.execute(
            "SELECT contexte_type, contenu "
            "FROM contexts WHERE document_id=?",
            (sid,)
        ).fetchall()

        print("Contextes :")

        for contexte_type, contexte in contextes:
            print("  -", contexte_type, ":", contexte)

        sortantes = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.target_id=d.id "
            "WHERE r.source_id=?",
            (sid,)
        ).fetchall()

        entrantes = c.execute(
            "SELECT r.relation, d.title "
            "FROM relations r "
            "JOIN documents d ON r.source_id=d.id "
            "WHERE r.target_id=?",
            (sid,)
        ).fetchall()

        print("Relations sortantes :")

        for relation, cible in sortantes:
            print("  ->", relation, "->", cible)

        print("Relations entrantes :")

        for relation, source in entrantes:
            print("  <-", relation, "<-", source)

    c.close()


def explorer_graphe():
    mot = input("Sujet a explorer dans le graphe : ")
    profondeur_max = 3

    c = sqlite3.connect(DB)
    visites = set()

    def explorer(sid, niveau):
        if niveau > profondeur_max or sid in visites:
            return

        visites.add(sid)

        resultat = c.execute(
            "SELECT title, content, type "
            "FROM documents WHERE id=?",
            (sid,)
        ).fetchone()

        if not resultat:
            return

        titre, contenu, type_souvenir = resultat

        print("\n" + "  " * niveau + "=== NIVEAU", niveau, "===")
        print("  " * niveau + "Titre :", titre)
        print("  " * niveau + "Type :", type_souvenir)
        print("  " * niveau + "Contenu :", contenu)

        relations = c.execute(
            "SELECT relation, target_id "
            "FROM relations WHERE source_id=?",
            (sid,)
        ).fetchall()

        for relation, cible_id in relations:
            cible = c.execute(
                "SELECT title FROM documents WHERE id=?",
                (cible_id,)
            ).fetchone()

            if cible:
                print(
                    "  " * niveau,
                    "->",
                    relation,
                    "->",
                    cible[0]
                )
                explorer(cible_id, niveau + 1)

    souvenirs = c.execute(
        "SELECT id FROM documents "
        "WHERE title LIKE ? OR content LIKE ?",
        ("%" + mot + "%", "%" + mot + "%")
    ).fetchall()

    if not souvenirs:
        print("Aucun sujet trouve.")
    else:
        for (sid,) in souvenirs:
            explorer(sid, 0)

    c.close()


def menu():
    while True:
        print("\n=== ALKAH-BRAIN ===")
        print("1. Ajouter un souvenir")
        print("2. Rechercher dans la memoire")
        print("3. Quitter")
        print("4. Rechercher par type")
        print("5. Voir les relations")
        print("6. Recherche contextuelle")
        print("7. Explorer les relations")
        print("8. Voir le contexte complet")
        print("9. Explorer le graphe")
        print("10. Synthèse du contexte")

        choix = input("Choix : ")

        if choix == "1":
            ajouter()
        elif choix == "2":
            rechercher()
        elif choix == "3":
            print("ALKAH-BRAIN termine.")
            break
        elif choix == "4":
            rechercher_par_type()
        elif choix == "5":
            voir_relations()
        elif choix == "6":
            rechercher_contextuel()
        elif choix == "7":
            relations_bidirectionnelles()
        elif choix == "8":
            voir_contexte_complet()
        elif choix == "9":
            explorer_graphe()
        elif choix == "10":
            synthese_contexte()
        else:
            print("Option non disponible pour le moment.")


if __name__ == "__main__":
    menu()







# ============================================================
# MIA V24 — PREMIERE BRIQUE : CONFIGURATION
# ============================================================

def mia_creer_configuration(
    nom,
    type_configuration,
    valeur,
    description="",
    source="ALKAH",
    version="V24",
    statut="PROPOSEE",
    confiance=0.0
):
    """Crée une configuration MIA structurée sans l'activer."""

    maintenant = datetime.datetime.now().isoformat()

    return {
        "id": f"MIA-CONFIG-{maintenant}",
        "nom": nom,
        "type": type_configuration,
        "valeur": valeur,
        "description": description,
        "source": source,
        "version": version,
        "statut": statut,
        "confiance": confiance,
        "date_creation": maintenant,
        "date_modification": maintenant
    }



# ============================================================
# MIA V24 — BRIQUE 02 : VERIFICATION DE CONFIGURATION
# ============================================================

def mia_verifier_configuration(configuration):
    """Vérifie la structure et les valeurs d'une configuration MIA."""

    erreurs = []
    avertissements = []

    if not isinstance(configuration, dict):
        return {
            "valide": False,
            "erreurs": ["La configuration doit être un dictionnaire."],
            "avertissements": []
        }

    champs_obligatoires = [
        "id",
        "nom",
        "type",
        "valeur",
        "version",
        "statut",
        "confiance"
    ]

    for champ in champs_obligatoires:
        if champ not in configuration:
            erreurs.append(f"Champ obligatoire absent : {champ}")

    types_autorises = [
        "IDENTITE",
        "CAPACITE",
        "REGLE",
        "MEMOIRE",
        "CONTEXTE",
        "DECISION",
        "CONFIANCE",
        "SECURITE",
        "EVOLUTION"
    ]

    if "type" in configuration:
        if configuration["type"] not in types_autorises:
            erreurs.append(
                f"Type de configuration non autorisé : "
                f"{configuration['type']}"
            )

    statuts_autorises = [
        "PROPOSEE",
        "ANALYSEE",
        "VALIDEE",
        "ACTIVE",
        "REMPLACEE",
        "REJETEE"
    ]

    if "statut" in configuration:
        if configuration["statut"] not in statuts_autorises:
            erreurs.append(
                f"Statut non autorisé : {configuration['statut']}"
            )

    if "confiance" in configuration:
        confiance = configuration["confiance"]

        if not isinstance(confiance, (int, float)):
            erreurs.append("La confiance doit être numérique.")
        elif confiance < 0 or confiance > 1:
            erreurs.append("La confiance doit être comprise entre 0 et 1.")

    if "nom" in configuration:
        if not isinstance(configuration["nom"], str) or not configuration["nom"].strip():
            erreurs.append("Le nom de configuration est obligatoire.")

    if "version" in configuration:
        if not configuration["version"]:
            erreurs.append("La version est obligatoire.")

    if (
        "statut" in configuration
        and configuration["statut"] == "ACTIVE"
        and "confiance" in configuration
        and isinstance(configuration["confiance"], (int, float))
        and configuration["confiance"] < 0.70
    ):
        avertissements.append(
            "Configuration ACTIVE avec un niveau de confiance inférieur à 0.70."
        )

    return {
        "valide": len(erreurs) == 0,
        "erreurs": erreurs,
        "avertissements": avertissements
    }



# ============================================================
# MIA V24 — BRIQUE 03 : DETECTION DES CONFLITS
# ============================================================

def mia_detecter_conflit_configuration(configuration_a, configuration_b):
    """Détecte une contradiction entre deux configurations MIA."""

    if not isinstance(configuration_a, dict):
        return {
            "conflit": False,
            "raison": "La première configuration est invalide.",
            "details": []
        }

    if not isinstance(configuration_b, dict):
        return {
            "conflit": False,
            "raison": "La deuxième configuration est invalide.",
            "details": []
        }

    details = []

    meme_nom = (
        configuration_a.get("nom")
        == configuration_b.get("nom")
    )

    meme_type = (
        configuration_a.get("type")
        == configuration_b.get("type")
    )

    valeurs_differentes = (
        configuration_a.get("valeur")
        != configuration_b.get("valeur")
    )

    if meme_nom and meme_type and valeurs_differentes:
        details.append(
            "Les deux configurations concernent le même élément "
            "mais possèdent des valeurs différentes."
        )

        return {
            "conflit": True,
            "raison": "Valeurs contradictoires.",
            "details": details
        }

    return {
        "conflit": False,
        "raison": "Aucun conflit détecté.",
        "details": []
    }



# ============================================================
# MIA V24 — BRIQUE 04 : EVALUATION DE CONFIGURATION
# ============================================================

def mia_evaluer_configuration(configuration):
    """Évalue une configuration sans l'activer."""

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        return {
            "evaluation": "REJETEE",
            "valide": False,
            "confiance": configuration.get("confiance", 0.0)
                if isinstance(configuration, dict) else 0.0,
            "erreurs": verification["erreurs"],
            "avertissements": verification["avertissements"],
            "recommandation": "CORRIGER"
        }

    confiance = configuration.get("confiance", 0.0)

    avertissements = list(verification["avertissements"])

    if confiance >= 0.90:
        evaluation = "TRES_FIABLE"
        recommandation = "POURSUIVRE"

    elif confiance >= 0.70:
        evaluation = "FIABLE"
        recommandation = "POURSUIVRE_AVEC_SURVEILLANCE"

    elif confiance >= 0.50:
        evaluation = "INCERTAINE"
        recommandation = "REVOIR"

    else:
        evaluation = "FAIBLE"
        recommandation = "REJETER_OU_REVOIR"

    return {
        "evaluation": evaluation,
        "valide": True,
        "confiance": confiance,
        "erreurs": [],
        "avertissements": avertissements,
        "recommandation": recommandation
    }



# ============================================================
# MIA V24 — BRIQUE 05 : CYCLE DE VIE DE CONFIGURATION
# ============================================================

def mia_changer_statut_configuration(configuration, nouveau_statut):
    """Contrôle le changement de statut d'une configuration MIA."""

    statuts_autorises = [
        "PROPOSEE",
        "ANALYSEE",
        "VALIDEE",
        "ACTIVE",
        "REMPLACEE",
        "REJETEE"
    ]

    transitions = {
        "PROPOSEE": ["ANALYSEE", "REJETEE"],
        "ANALYSEE": ["VALIDEE", "REJETEE"],
        "VALIDEE": ["ACTIVE", "REJETEE"],
        "ACTIVE": ["REMPLACEE"],
        "REMPLACEE": [],
        "REJETEE": []
    }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "statut": None,
            "erreur": "La configuration doit être un dictionnaire."
        }

    if nouveau_statut not in statuts_autorises:
        return {
            "succes": False,
            "statut": configuration.get("statut"),
            "erreur": f"Statut non autorisé : {nouveau_statut}"
        }

    ancien_statut = configuration.get("statut")

    if ancien_statut not in transitions:
        return {
            "succes": False,
            "statut": ancien_statut,
            "erreur": f"Statut actuel inconnu : {ancien_statut}"
        }

    if nouveau_statut not in transitions[ancien_statut]:
        return {
            "succes": False,
            "statut": ancien_statut,
            "erreur": (
                f"Transition interdite : "
                f"{ancien_statut} -> {nouveau_statut}"
            )
        }

    configuration["statut"] = nouveau_statut

    return {
        "succes": True,
        "ancien_statut": ancien_statut,
        "nouveau_statut": nouveau_statut,
        "erreur": None
    }



# ============================================================
# MIA V24 — BRIQUE 06 : HISTORIQUE DES CONFIGURATIONS
# ============================================================

def mia_enregistrer_historique_configuration(
    configuration,
    action,
    details="",
    source="MIA"
):
    """Enregistre une trace structurée d'une action sur une configuration."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    maintenant = datetime.datetime.now().isoformat()

    historique = {
        "id": f"MIA-HIST-{maintenant}",
        "date": maintenant,
        "configuration_id": configuration.get("id"),
        "nom_configuration": configuration.get("nom"),
        "action": action,
        "ancien_statut": configuration.get("statut"),
        "details": details,
        "source": source,
        "version": configuration.get("version", "V24")
    }

    return {
        "succes": True,
        "historique": historique,
        "erreur": None
    }



# ============================================================
# MIA V24 — BRIQUE 07 : COMPARAISON DES CONFIGURATIONS
# ============================================================

def mia_comparer_configurations(configuration_a, configuration_b):
    """Compare deux configurations MIA sans les modifier."""

    if not isinstance(configuration_a, dict):
        return {
            "succes": False,
            "erreur": "La première configuration doit être un dictionnaire."
        }

    if not isinstance(configuration_b, dict):
        return {
            "succes": False,
            "erreur": "La deuxième configuration doit être un dictionnaire."
        }

    champs_comparaison = [
        "nom",
        "type",
        "valeur",
        "description",
        "source",
        "version",
        "statut",
        "confiance"
    ]

    differences = []

    for champ in champs_comparaison:
        valeur_a = configuration_a.get(champ)
        valeur_b = configuration_b.get(champ)

        if valeur_a != valeur_b:
            differences.append({
                "champ": champ,
                "configuration_a": valeur_a,
                "configuration_b": valeur_b
            })

    meme_configuration = len(differences) == 0

    conflit = (
        configuration_a.get("nom") == configuration_b.get("nom")
        and configuration_a.get("type") == configuration_b.get("type")
        and configuration_a.get("valeur") != configuration_b.get("valeur")
    )

    if conflit:
        resultat = "CONFLIT"
    elif meme_configuration:
        resultat = "IDENTIQUES"
    else:
        resultat = "DIFFERENTES"

    return {
        "succes": True,
        "resultat": resultat,
        "identiques": meme_configuration,
        "conflit": conflit,
        "nombre_differences": len(differences),
        "differences": differences,
        "erreur": None
    }



# ============================================================
# MIA V24 — BRIQUE 08 : SELECTION DE CONFIGURATION
# ============================================================

def mia_selectionner_configuration(configurations):
    """Sélectionne la meilleure configuration sans l'activer."""

    if not isinstance(configurations, list):
        return {
            "succes": False,
            "selection": None,
            "raison": "Les configurations doivent être fournies sous forme de liste.",
            "candidates": []
        }

    candidates = []
    rejetees = []

    for configuration in configurations:

        verification = mia_verifier_configuration(configuration)

        if not verification["valide"]:
            rejetees.append({
                "configuration": configuration,
                "raison": verification["erreurs"]
            })
            continue

        if configuration.get("statut") == "REJETEE":
            rejetees.append({
                "configuration": configuration,
                "raison": ["Configuration déjà rejetée."]
            })
            continue

        candidates.append(configuration)

    if not candidates:
        return {
            "succes": False,
            "selection": None,
            "raison": "Aucune configuration valide disponible.",
            "candidates": [],
            "rejetees": rejetees
        }

    meilleure_confiance = max(
        configuration.get("confiance", 0.0)
        for configuration in candidates
    )

    meilleures = [
        configuration
        for configuration in candidates
        if configuration.get("confiance", 0.0) == meilleure_confiance
    ]

    if len(meilleures) > 1:
        return {
            "succes": False,
            "selection": None,
            "raison": "Plusieurs configurations ont le même niveau de confiance.",
            "candidates": meilleures,
            "rejetees": rejetees
        }

    selection = meilleures[0]

    return {
        "succes": True,
        "selection": selection,
        "raison": "Configuration sélectionnée selon le niveau de confiance.",
        "candidates": candidates,
        "rejetees": rejetees
    }



# ============================================================
# MIA V24 — BRIQUE 09 : DECISION SECURISEE
# ============================================================

def mia_proposer_decision_configuration(configuration):
    """Produit une décision contrôlée sans activer la configuration."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "decision": "REFUSER",
            "activation": False,
            "raison": "La configuration doit être un dictionnaire.",
            "erreurs": ["Configuration invalide."]
        }

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        return {
            "succes": False,
            "decision": "REFUSER",
            "activation": False,
            "raison": "La configuration est invalide.",
            "erreurs": verification["erreurs"],
            "avertissements": verification["avertissements"]
        }

    evaluation = mia_evaluer_configuration(configuration)

    confiance = configuration.get("confiance", 0.0)

    if confiance < 0.50:
        return {
            "succes": True,
            "decision": "REVOIR",
            "activation": False,
            "raison": "Niveau de confiance insuffisant.",
            "confiance": confiance,
            "evaluation": evaluation["evaluation"],
            "erreurs": [],
            "avertissements": evaluation["avertissements"]
        }

    if confiance < 0.90:
        return {
            "succes": True,
            "decision": "PROPOSER_AVEC_SURVEILLANCE",
            "activation": False,
            "raison": "Configuration suffisamment fiable mais nécessitant une surveillance.",
            "confiance": confiance,
            "evaluation": evaluation["evaluation"],
            "erreurs": [],
            "avertissements": evaluation["avertissements"]
        }

    return {
        "succes": True,
        "decision": "PROPOSER",
        "activation": False,
        "raison": "Configuration très fiable. Activation non automatique.",
        "confiance": confiance,
        "evaluation": evaluation["evaluation"],
        "erreurs": [],
        "avertissements": evaluation["avertissements"]
    }



# ============================================================
# MIA V24 — BRIQUE 10 : APPROBATION EXPLICITE
# ============================================================

def mia_approuver_configuration(configuration, approbateur):
    """Approuve explicitement une configuration sans l'activer automatiquement."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    if not isinstance(approbateur, str) or not approbateur.strip():
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "erreur": "Un approbateur explicite est obligatoire."
        }

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "erreur": "La configuration est invalide.",
            "details": verification["erreurs"]
        }

    statut = configuration.get("statut")

    if statut == "REJETEE":
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "erreur": "Une configuration rejetée ne peut pas être approuvée."
        }

    if statut == "ACTIVE":
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "erreur": "La configuration est déjà active."
        }

    maintenant = datetime.datetime.now().isoformat()

    configuration["approbation"] = {
        "approuvee": True,
        "approbateur": approbateur,
        "date": maintenant
    }

    return {
        "succes": True,
        "approuvee": True,
        "activation": False,
        "approbateur": approbateur,
        "date_approbation": maintenant,
        "raison": "Configuration approuvée explicitement. Activation toujours séparée."
    }



# ============================================================
# MIA V24 — BRIQUE 11 : ACTIVATION CONTROLEE
# ============================================================

def mia_activer_configuration(configuration):
    """Active une configuration uniquement après approbation explicite."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "activation": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        return {
            "succes": False,
            "activation": False,
            "erreur": "La configuration est invalide.",
            "details": verification["erreurs"]
        }

    if configuration.get("statut") == "REJETEE":
        return {
            "succes": False,
            "activation": False,
            "erreur": "Une configuration rejetée ne peut pas être activée."
        }

    if configuration.get("statut") == "ACTIVE":
        return {
            "succes": False,
            "activation": False,
            "erreur": "La configuration est déjà active."
        }

    approbation = configuration.get("approbation")

    if not isinstance(approbation, dict):
        return {
            "succes": False,
            "activation": False,
            "erreur": "Aucune approbation explicite trouvée."
        }

    if approbation.get("approuvee") is not True:
        return {
            "succes": False,
            "activation": False,
            "erreur": "L'approbation explicite est obligatoire."
        }

    approbateur = approbation.get("approbateur")

    if not isinstance(approbateur, str) or not approbateur.strip():
        return {
            "succes": False,
            "activation": False,
            "erreur": "L'identité de l'approbateur est obligatoire."
        }

    confiance = configuration.get("confiance", 0.0)

    if confiance < 0.90:
        return {
            "succes": False,
            "activation": False,
            "erreur": (
                "Niveau de confiance insuffisant pour une activation."
            ),
            "confiance": confiance
        }

    ancien_statut = configuration.get("statut")

    if ancien_statut != "VALIDEE":
        return {
            "succes": False,
            "activation": False,
            "erreur": (
                "La configuration doit être au statut VALIDEE "
                "avant activation."
            ),
            "statut": ancien_statut
        }

    resultat_transition = mia_changer_statut_configuration(
        configuration,
        "ACTIVE"
    )

    if not resultat_transition["succes"]:
        return {
            "succes": False,
            "activation": False,
            "erreur": resultat_transition["erreur"]
        }

    maintenant = datetime.datetime.now().isoformat()

    configuration["activation"] = {
        "activee": True,
        "date": maintenant,
        "approbateur": approbateur
    }

    return {
        "succes": True,
        "activation": True,
        "ancien_statut": ancien_statut,
        "nouveau_statut": "ACTIVE",
        "date_activation": maintenant,
        "approbateur": approbateur,
        "raison": "Configuration activée après approbation explicite."
    }



# ============================================================
# MIA V24 — BRIQUE 12 : ORCHESTRATION DU CYCLE COMPLET
# ============================================================

def mia_orchestrer_configuration(configuration):
    """Orchestre le cycle de contrôle d'une configuration MIA.
    
    La fonction analyse, évalue et propose une décision.
    Elle ne déclenche jamais l'activation automatiquement.
    """

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "etape": "ENTREE",
            "decision": "REFUSER",
            "activation": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # ETAPE 1 : VERIFICATION
    # --------------------------------------------------------

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        return {
            "succes": False,
            "etape": "VERIFICATION",
            "decision": "REFUSER",
            "activation": False,
            "verification": verification,
            "erreur": "La configuration est invalide."
        }

    # --------------------------------------------------------
    # ETAPE 2 : EVALUATION
    # --------------------------------------------------------

    evaluation = mia_evaluer_configuration(configuration)

    # --------------------------------------------------------
    # ETAPE 3 : DECISION SECURISEE
    # --------------------------------------------------------

    decision = mia_proposer_decision_configuration(configuration)

    return {
        "succes": decision["succes"],
        "etape": "DECISION",
        "configuration_id": configuration.get("id"),
        "nom": configuration.get("nom"),
        "verification": verification,
        "evaluation": evaluation,
        "decision": decision["decision"],
        "activation": False,
        "raison": decision["raison"],
        "confiance": configuration.get("confiance", 0.0),
        "erreurs": decision.get("erreurs", []),
        "avertissements": decision.get("avertissements", []),
        "prochaine_etape": (
            "APPROBATION_EXPLICITE"
            if decision["decision"] in [
                "PROPOSER",
                "PROPOSER_AVEC_SURVEILLANCE"
            ]
            else "REVISION"
        )
    }



# ============================================================
# MIA V24 — BRIQUE 13 : JOURNAL COMPLET DU CYCLE
# ============================================================

def mia_creer_journal_cycle():
    """Crée un journal vide pour suivre le cycle de vie MIA."""

    return {
        "version": "V24",
        "evenements": [],
        "nombre_evenements": 0
    }


def mia_ajouter_evenement_cycle(
    journal,
    configuration,
    action,
    source="MIA",
    details=""
):
    """Ajoute un événement structuré au journal du cycle."""

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    if not isinstance(action, str) or not action.strip():
        return {
            "succes": False,
            "erreur": "L'action est obligatoire."
        }

    maintenant = datetime.datetime.now().isoformat()

    evenement = {
        "id": f"MIA-EVENT-{maintenant}",
        "date": maintenant,
        "configuration_id": configuration.get("id"),
        "nom_configuration": configuration.get("nom"),
        "action": action,
        "statut": configuration.get("statut"),
        "source": source,
        "details": details,
        "version": configuration.get("version", "V24")
    }

    journal.setdefault("evenements", [])
    journal["evenements"].append(evenement)
    journal["nombre_evenements"] = len(journal["evenements"])

    return {
        "succes": True,
        "evenement": evenement,
        "nombre_evenements": journal["nombre_evenements"],
        "erreur": None
    }


def mia_lire_journal_cycle(journal):
    """Retourne une copie contrôlée du journal du cycle."""

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "evenements": [],
            "nombre_evenements": 0,
            "erreur": "Le journal doit être un dictionnaire."
        }

    evenements = list(journal.get("evenements", []))

    return {
        "succes": True,
        "evenements": evenements,
        "nombre_evenements": len(evenements),
        "erreur": None
    }



# ============================================================
# MIA V24 — BRIQUE 14 : JOURNALISATION AUTOMATIQUE DU CYCLE
# ============================================================

def mia_journaliser_cycle_configuration(
    journal,
    configuration,
    action,
    resultat=None,
    source="MIA"
):
    """Journalise automatiquement une étape du cycle de configuration."""

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    if not isinstance(action, str) or not action.strip():
        return {
            "succes": False,
            "erreur": "L'action est obligatoire."
        }

    details = ""

    if isinstance(resultat, dict):

        if "decision" in resultat:
            details += f"Décision : {resultat['decision']}. "

        if "activation" in resultat:
            details += f"Activation : {resultat['activation']}. "

        if "raison" in resultat:
            details += f"Raison : {resultat['raison']}"

    elif resultat is not None:
        details = str(resultat)

    return mia_ajouter_evenement_cycle(
        journal=journal,
        configuration=configuration,
        action=action,
        source=source,
        details=details
    )


def mia_executer_cycle_journalise(configuration):
    """Exécute le cycle d'analyse et journalise chaque étape.

    Cette fonction n'active jamais automatiquement une configuration.
    """

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "activation": False,
            "erreur": "La configuration doit être un dictionnaire.",
            "journal": None
        }

    journal = mia_creer_journal_cycle()

    # --------------------------------------------------------
    # ETAPE 1 : CREATION / ENTREE
    # --------------------------------------------------------

    mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="CREATION",
        resultat="Configuration reçue.",
        source="ALKAH"
    )

    # --------------------------------------------------------
    # ETAPE 2 : VERIFICATION
    # --------------------------------------------------------

    verification = mia_verifier_configuration(configuration)

    mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="VERIFICATION",
        resultat=verification,
        source="MIA"
    )

    if not verification["valide"]:
        return {
            "succes": False,
            "activation": False,
            "decision": "REFUSER",
            "verification": verification,
            "journal": journal,
            "erreur": "La configuration est invalide."
        }

    # --------------------------------------------------------
    # ETAPE 3 : EVALUATION
    # --------------------------------------------------------

    evaluation = mia_evaluer_configuration(configuration)

    mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="EVALUATION",
        resultat=evaluation,
        source="MIA"
    )

    # --------------------------------------------------------
    # ETAPE 4 : DECISION
    # --------------------------------------------------------

    decision = mia_proposer_decision_configuration(configuration)

    mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="DECISION",
        resultat=decision,
        source="MIA"
    )

    return {
        "succes": decision["succes"],
        "activation": False,
        "decision": decision["decision"],
        "verification": verification,
        "evaluation": evaluation,
        "journal": journal,
        "prochaine_etape": (
            "APPROBATION_EXPLICITE"
            if decision["decision"] in [
                "PROPOSER",
                "PROPOSER_AVEC_SURVEILLANCE"
            ]
            else "REVISION"
        ),
        "erreur": None
    }



# ============================================================
# MIA V24 — BRIQUE 15 : APPROBATION ET ACTIVATION JOURNALISEES
# ============================================================

def mia_approbation_journalisee(
    journal,
    configuration,
    approbateur
):
    """Approuve une configuration et enregistre l'approbation."""

    resultat = mia_approuver_configuration(
        configuration,
        approbateur
    )

    if not resultat["succes"]:
        return {
            "succes": False,
            "approuvee": False,
            "activation": False,
            "journal": journal,
            "resultat": resultat
        }

    evenement = mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="APPROBATION",
        resultat=resultat,
        source=approbateur
    )

    return {
        "succes": True,
        "approuvee": True,
        "activation": False,
        "resultat": resultat,
        "journalisation": evenement,
        "journal": journal
    }




# ============================================================
# MIA V24 — BRIQUE 16 : REFUS ET JOURNALISATION SECURISEE
# ============================================================

def mia_journaliser_refus_configuration(
    journal,
    configuration,
    action,
    raison,
    source="MIA"
):
    """Journalise une action refusée ou bloquée."""

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "erreur": "La configuration doit être un dictionnaire."
        }

    if not isinstance(action, str) or not action.strip():
        return {
            "succes": False,
            "erreur": "L'action est obligatoire."
        }

    if not isinstance(raison, str) or not raison.strip():
        return {
            "succes": False,
            "erreur": "La raison du refus est obligatoire."
        }

    maintenant = datetime.datetime.now().isoformat()

    evenement = {
        "id": f"MIA-REFUS-{maintenant}",
        "date": maintenant,
        "configuration_id": configuration.get("id"),
        "nom_configuration": configuration.get("nom"),
        "action": action,
        "statut": configuration.get("statut"),
        "source": source,
        "resultat": "REFUSEE",
        "raison": raison,
        "version": configuration.get("version", "V24")
    }

    journal.setdefault("evenements", [])
    journal["evenements"].append(evenement)
    journal["nombre_evenements"] = len(journal["evenements"])

    return {
        "succes": True,
        "evenement": evenement,
        "nombre_evenements": journal["nombre_evenements"],
        "erreur": None
    }


def mia_refuser_et_journaliser(
    journal,
    configuration,
    action,
    raison,
    source="MIA"
):
    """Refuse une action sensible et en conserve la trace."""

    resultat = mia_journaliser_refus_configuration(
        journal=journal,
        configuration=configuration,
        action=action,
        raison=raison,
        source=source
    )

    return {
        "succes": False,
        "autorisee": False,
        "activation": False,
        "action": action,
        "raison": raison,
        "journalisation": resultat,
        "journal": journal
    }


# ============================================================
# MIA V24 — BRIQUE 17 : CONTROLE GLOBAL AVANT ACTIVATION
# ============================================================

def mia_controle_global_avant_activation(configuration):
    """Effectue le contrôle final avant une activation."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreurs": ["La configuration doit être un dictionnaire."]
        }

    erreurs = []
    avertissements = []

    # --------------------------------------------------------
    # 1. VERIFICATION DE LA CONFIGURATION
    # --------------------------------------------------------

    verification = mia_verifier_configuration(configuration)

    if not verification["valide"]:
        erreurs.extend(verification["erreurs"])

    # --------------------------------------------------------
    # 2. CONTROLE DU STATUT
    # --------------------------------------------------------

    statut = configuration.get("statut")

    if statut != "VALIDEE":
        erreurs.append(
            "La configuration doit être au statut VALIDEE."
        )

    # --------------------------------------------------------
    # 3. CONTROLE DE L'APPROBATION
    # --------------------------------------------------------

    approbation = configuration.get("approbation")

    if not isinstance(approbation, dict):
        erreurs.append(
            "Aucune approbation explicite trouvée."
        )
    else:
        if approbation.get("approuvee") is not True:
            erreurs.append(
                "L'approbation explicite est obligatoire."
            )

        approbateur = approbation.get("approbateur")

        if not isinstance(approbateur, str) or not approbateur.strip():
            erreurs.append(
                "L'identité de l'approbateur est obligatoire."
            )

    # --------------------------------------------------------
    # 4. CONTROLE DE CONFIANCE
    # --------------------------------------------------------

    confiance = configuration.get("confiance", 0.0)

    if not isinstance(confiance, (int, float)):
        erreurs.append(
            "Le niveau de confiance doit être numérique."
        )
    elif confiance < 0.90:
        erreurs.append(
            "Niveau de confiance insuffisant pour activation."
        )

    # --------------------------------------------------------
    # 5. CONTROLE D'UNE CONFIGURATION DEJA ACTIVE
    # --------------------------------------------------------

    if statut == "ACTIVE":
        erreurs.append(
            "La configuration est déjà active."
        )

    # --------------------------------------------------------
    # 6. DECISION FINALE
    # --------------------------------------------------------

    if erreurs:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "configuration_id": configuration.get("id"),
            "nom": configuration.get("nom"),
            "statut": statut,
            "confiance": confiance,
            "erreurs": erreurs,
            "avertissements": avertissements,
            "raison": "Les conditions de sécurité ne sont pas réunies."
        }

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "AUTORISER_ACTIVATION",
        "configuration_id": configuration.get("id"),
        "nom": configuration.get("nom"),
        "statut": statut,
        "confiance": confiance,
        "approbateur": approbation.get("approbateur"),
        "erreurs": [],
        "avertissements": avertissements,
        "raison": (
            "Toutes les conditions de sécurité sont réunies. "
            "L'activation peut être demandée explicitement."
        )
    }


# ============================================================
# MIA V24 — BRIQUE 18 : CONTROLE D'INTEGRITE AVANT ACTIVATION
# ============================================================

def mia_calculer_integrite_configuration(configuration):
    """Calcule une empreinte stable de la configuration.

    L'empreinte de référence elle-même n'entre jamais
    dans le calcul.
    """

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "empreinte": None,
            "erreur": "La configuration doit être un dictionnaire."
        }

    import hashlib
    import json

    donnees = dict(configuration)

    # L'empreinte de référence ne doit jamais
    # entrer dans son propre calcul.
    donnees.pop("integrite_reference", None)

    contenu = json.dumps(
        donnees,
        sort_keys=True,
        ensure_ascii=False,
        default=str
    )

    empreinte = hashlib.sha256(
        contenu.encode("utf-8")
    ).hexdigest()

    return {
        "succes": True,
        "empreinte": empreinte,
        "erreur": None
    }


def mia_enregistrer_integrite_configuration(configuration):
    """Enregistre l'empreinte de référence de la configuration."""

    resultat = mia_calculer_integrite_configuration(configuration)

    if not resultat["succes"]:
        return resultat

    configuration["integrite_reference"] = resultat["empreinte"]

    return {
        "succes": True,
        "empreinte": resultat["empreinte"],
        "erreur": None
    }


def mia_verifier_integrite_configuration(configuration):
    """Vérifie que la configuration n'a pas changé depuis son enregistrement."""

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "integre": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    reference = configuration.get("integrite_reference")

    if not isinstance(reference, str) or not reference:
        return {
            "succes": False,
            "integre": False,
            "decision": "REFUSER",
            "erreur": "Aucune empreinte d'intégrité de référence."
        }

    # On exclut l'empreinte elle-même du calcul.
    copie = dict(configuration)
    copie.pop("integrite_reference", None)

    resultat = mia_calculer_integrite_configuration(copie)

    if not resultat["succes"]:
        return {
            "succes": False,
            "integre": False,
            "decision": "REFUSER",
            "erreur": resultat["erreur"]
        }

    integre = resultat["empreinte"] == reference

    return {
        "succes": True,
        "integre": integre,
        "decision": "AUTORISER" if integre else "REFUSER",
        "empreinte_reference": reference,
        "empreinte_actuelle": resultat["empreinte"],
        "erreur": None if integre else
            "La configuration a été modifiée après l'enregistrement de son intégrité."
    }


# ============================================================
# MIA V24 — BRIQUE 19 : INTEGRATION DU CONTROLE D'INTEGRITE
# DANS LE CONTROLE GLOBAL
# ============================================================

def mia_controle_global_securise_avant_activation(configuration):
    """Effectue le contrôle global complet avant activation.

    Vérifie :
    - la configuration
    - le statut
    - l'approbation
    - la confiance
    - l'intégrité

    Cette fonction n'active jamais automatiquement.
    """

    resultat_global = mia_controle_global_avant_activation(
        configuration
    )

    if not resultat_global["succes"]:
        return resultat_global

    integrite = mia_verifier_integrite_configuration(
        configuration
    )

    if not integrite["succes"] or not integrite["integre"]:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "configuration_id": configuration.get("id"),
            "nom": configuration.get("nom"),
            "statut": configuration.get("statut"),
            "confiance": configuration.get("confiance"),
            "erreurs": [
                integrite.get(
                    "erreur",
                    "Contrôle d'intégrité échoué."
                )
            ],
            "avertissements": [],
            "raison": (
                "L'intégrité de la configuration "
                "n'est pas garantie."
            )
        }

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "AUTORISER_ACTIVATION",
        "configuration_id": configuration.get("id"),
        "nom": configuration.get("nom"),
        "statut": configuration.get("statut"),
        "confiance": configuration.get("confiance"),
        "approbateur": configuration.get(
            "approbation", {}
        ).get("approbateur"),
        "integrite": True,
        "erreurs": [],
        "avertissements": [],
        "raison": (
            "Tous les contrôles de sécurité et "
            "d'intégrité sont satisfaits. "
            "L'activation peut être demandée explicitement."
        )
    }


# ============================================================
# MIA V24 — BRIQUE 20 : JOURNALISATION DU CONTROLE SECURISE
# ============================================================

def mia_controle_securise_journalise(
    journal,
    configuration
):
    """Effectue le contrôle global sécurisé et journalise le résultat.

    Cette fonction n'active jamais automatiquement une configuration.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    controle = mia_controle_global_securise_avant_activation(
        configuration
    )

    if controle["succes"]:
        action = "CONTROLE_SECURITE"
        source = "MIA"
        resultat_journal = mia_journaliser_cycle_configuration(
            journal=journal,
            configuration=configuration,
            action=action,
            resultat=controle,
            source=source
        )

        return {
            "succes": True,
            "autorisation": True,
            "activation": False,
            "decision": controle["decision"],
            "controle": controle,
            "journalisation": resultat_journal,
            "journal": journal,
            "erreur": None
        }

    raison = controle.get(
        "raison",
        "Contrôle de sécurité refusé."
    )

    erreurs = controle.get("erreurs", [])

    if erreurs:
        raison = " ".join(
            str(erreur) for erreur in erreurs
        )

    resultat_journal = mia_journaliser_refus_configuration(
        journal=journal,
        configuration=configuration,
        action="CONTROLE_SECURITE",
        raison=raison,
        source="MIA"
    )

    return {
        "succes": False,
        "autorisation": False,
        "activation": False,
        "decision": "REFUSER",
        "controle": controle,
        "journalisation": resultat_journal,
        "journal": journal,
        "erreur": raison
    }


# ============================================================
# MIA V24 — BRIQUE 21 : DECISION FINALE D'ACTIVATION SECURISEE
# ============================================================



# ============================================================
# MIA V24 — BRIQUE 22 : VERROUILLAGE POST-ACTIVATION
# ============================================================





# ============================================================
# MIA V24 — BRIQUE 22 : VERROUILLAGE POST-ACTIVATION
# ============================================================





# ============================================================
# MIA V24 — CORRECTION BRIQUE 22
# VERROUILLAGE POST-ACTIVATION — INTEGRITE REFERENCE
# ============================================================





# ============================================================
# MIA V24 — CORRECTION FINALE BRIQUE 22
# VERROUILLAGE POST-ACTIVATION — ETAT ACTIVE FINAL
# ============================================================

def mia_activation_journalisee(journal, configuration):
    """
    Active une configuration approuvée.

    Après l'activation réelle, l'état ACTIVE final est enregistré
    comme référence d'intégrité.

    Ainsi, le verrouillage post-activation porte sur l'état réel
    de la configuration après activation.
    """

    resultat = mia_activer_configuration(configuration)

    if not resultat["succes"]:
        return {
            "succes": False,
            "activation": False,
            "journal": journal,
            "resultat": resultat
        }

    # --------------------------------------------------------
    # ENREGISTREMENT DE L'INTEGRITE APRES ACTIVATION
    # --------------------------------------------------------

    integrite = mia_enregistrer_integrite_configuration(
        configuration
    )

    if not integrite["succes"]:
        return {
            "succes": False,
            "activation": True,
            "journal": journal,
            "resultat": resultat,
            "integrite": integrite,
            "erreur": "Impossible d'enregistrer l'intégrité après activation."
        }

    evenement = mia_journaliser_cycle_configuration(
        journal,
        configuration,
        action="ACTIVATION",
        resultat=resultat,
        source="MIA"
    )

    return {
        "succes": True,
        "activation": True,
        "resultat": resultat,
        "integrite": integrite,
        "journalisation": evenement,
        "journal": journal
    }


def mia_verifier_verrouillage_post_activation(configuration):
    """
    Vérifie qu'une configuration ACTIVE reste strictement intacte.

    Une configuration ACTIVE doit posséder une empreinte de référence.
    Le contrôle utilise le mécanisme officiel d'intégrité de MIA.

    Cette fonction ne modifie jamais la configuration.
    """

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "verrouillee": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    statut = configuration.get("statut")

    # Une configuration non ACTIVE n'est pas encore verrouillée.
    if statut != "ACTIVE":
        return {
            "succes": True,
            "verrouillee": False,
            "decision": "AUTORISER",
            "erreur": None,
            "raison": "La configuration n'est pas encore ACTIVE."
        }

    # Une configuration ACTIVE doit posséder une référence.
    reference = configuration.get("integrite_reference")

    if not isinstance(reference, str) or not reference:
        return {
            "succes": False,
            "verrouillee": True,
            "decision": "REFUSER",
            "erreur": (
                "Configuration ACTIVE sans empreinte "
                "d'intégrité de référence."
            )
        }

    try:
        verification = mia_verifier_integrite_configuration(
            configuration
        )
    except Exception as erreur:
        return {
            "succes": False,
            "verrouillee": True,
            "decision": "REFUSER",
            "erreur": f"Impossible de vérifier l'intégrité : {erreur}"
        }

    if not verification.get("succes"):
        return {
            "succes": False,
            "verrouillee": True,
            "decision": "REFUSER",
            "erreur": verification.get(
                "erreur",
                "Échec du contrôle d'intégrité."
            )
        }

    if verification.get("integre") is not True:
        return {
            "succes": False,
            "verrouillee": True,
            "decision": "REFUSER",
            "erreur": (
                "La configuration ACTIVE a été modifiée "
                "après son activation."
            ),
            "empreinte_reference": verification.get(
                "empreinte_reference"
            ),
            "empreinte_actuelle": verification.get(
                "empreinte_actuelle"
            )
        }

    return {
        "succes": True,
        "verrouillee": True,
        "decision": "VERROUILLEE",
        "erreur": None,
        "raison": (
            "La configuration ACTIVE est intacte "
            "et correctement verrouillée."
        ),
        "empreinte_reference": verification.get(
            "empreinte_reference"
        ),
        "empreinte_actuelle": verification.get(
            "empreinte_actuelle"
        )
    }


def mia_controle_post_activation(configuration):
    """
    Effectue le contrôle de sécurité post-activation.

    Ne modifie aucune configuration.
    N'effectue aucune activation.
    """

    verrouillage = mia_verifier_verrouillage_post_activation(
        configuration
    )

    if not verrouillage["succes"]:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "verrouillage": verrouillage,
            "erreur": verrouillage["erreur"]
        }

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": verrouillage["decision"],
        "verrouillage": verrouillage,
        "erreur": None
    }


# ============================================================
# MIA V24 — CORRECTION BRIQUE 21
# PREPARATION DE L'INTEGRITE AVANT LE CONTROLE FINAL
# ============================================================

def mia_decision_finale_activation(journal, configuration):
    """
    Décision finale sécurisée d'activation.

    Cycle :
    VALIDEE
       ↓
    préparation de l'intégrité
       ↓
    contrôle global
       ↓
    autorisation explicite
       ↓
    activation
       ↓
    nouvelle empreinte de l'état ACTIVE
       ↓
    verrouillage post-activation
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. ETAT
    # --------------------------------------------------------

    if configuration.get("statut") == "ACTIVE":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration est déjà active."
        }

    if configuration.get("statut") != "VALIDEE":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "La configuration doit être au statut VALIDEE "
                "avant activation."
            )
        }

    # --------------------------------------------------------
    # 2. PREPARATION DE L'INTEGRITE
    # --------------------------------------------------------

    reference = configuration.get("integrite_reference")

    if not isinstance(reference, str) or not reference:
        integrite = mia_enregistrer_integrite_configuration(
            configuration
        )

        if not integrite["succes"]:
            return {
                "succes": False,
                "autorisation": False,
                "activation": False,
                "decision": "REFUSER",
                "erreur": (
                    "Impossible d'établir l'intégrité "
                    "avant activation."
                ),
                "integrite": integrite
            }

    # --------------------------------------------------------
    # 3. CONTROLE SECURISE FINAL
    # --------------------------------------------------------

    controle = mia_controle_securise_journalise(
        journal,
        configuration
    )

    if not controle.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "controle": controle,
            "journal": journal,
            "erreur": controle.get(
                "erreur",
                "Contrôle sécurisé refusé."
            )
        }

    if controle.get("autorisation") is not True:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "controle": controle,
            "journal": journal,
            "erreur": (
                "L'autorisation d'activation "
                "n'est pas accordée."
            )
        }

    # --------------------------------------------------------
    # 4. ACTIVATION REELLE
    # --------------------------------------------------------

    activation = mia_activation_journalisee(
        journal,
        configuration
    )

    if not activation.get("succes"):
        return {
            "succes": False,
            "autorisation": True,
            "activation": False,
            "decision": "REFUSER",
            "controle": controle,
            "activation_resultat": activation,
            "journal": journal,
            "erreur": activation.get(
                "erreur",
                "Activation refusée."
            )
        }

    # --------------------------------------------------------
    # 5. DECISION FINALE
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": True,
        "decision": "ACTIVATION_AUTORISEE_ET_EFFECTUEE",
        "controle": controle,
        "activation_resultat": activation,
        "journal": journal,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 23 : TRAÇABILITE DU VERROUILLAGE
# ============================================================

def mia_tracer_verrouillage_post_activation(journal, configuration):
    """
    Brique 23 — Trace dans le journal le résultat du verrouillage
    post-activation.

    Cette fonction :
    - vérifie le verrouillage de la configuration ;
    - journalise le résultat ;
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - refuse toute configuration ACTIVE compromise.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. CONTROLE DU VERROUILLAGE
    # --------------------------------------------------------

    verrouillage = mia_verifier_verrouillage_post_activation(
        configuration
    )

    if not verrouillage.get("succes"):
        evenement = mia_ajouter_evenement_cycle(
            journal,
            configuration,
            "VERROUILLAGE_REFUSE",
            verrouillage.get(
                "erreur",
                "Verrouillage post-activation refusé."
            )
        )

        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "verrouillage": verrouillage,
            "journalisation": evenement,
            "journal": journal,
            "erreur": verrouillage.get(
                "erreur",
                "Verrouillage post-activation refusé."
            )
        }

    # --------------------------------------------------------
    # 2. JOURNALISATION DU VERROUILLAGE
    # --------------------------------------------------------

    decision = verrouillage.get("decision")

    evenement = mia_ajouter_evenement_cycle(
        journal,
        configuration,
        "VERROUILLAGE_POST_ACTIVATION",
        (
            f"Contrôle du verrouillage : {decision}. "
            f"Activation automatique : False."
        )
    )

    if not evenement.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "verrouillage": verrouillage,
            "journalisation": evenement,
            "journal": journal,
            "erreur": evenement.get(
                "erreur",
                "Impossible de journaliser le verrouillage."
            )
        }

    # --------------------------------------------------------
    # 3. RESULTAT FINAL
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": decision,
        "verrouillage": verrouillage,
        "journalisation": evenement,
        "journal": journal,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 24 : AUDIT COMPLET POST-ACTIVATION
# ============================================================

def mia_auditer_cycle_post_activation(journal, configuration):
    """
    Brique 24 — Audit complet et non destructif du cycle
    post-activation.

    Vérifie successivement :
    - la validité du journal ;
    - la validité de la configuration ;
    - le statut ACTIVE ;
    - l'intégrité ;
    - le verrouillage ;
    - la traçabilité.

    Cette fonction :
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - ne change aucun statut ;
    - refuse toute configuration compromise.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. VERIFICATION DU STATUT
    # --------------------------------------------------------

    if configuration.get("statut") != "ACTIVE":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "L'audit post-activation exige une configuration ACTIVE."
            )
        }

    # --------------------------------------------------------
    # 2. VERIFICATION DE L'INTEGRITE
    # --------------------------------------------------------

    integrite = mia_verifier_integrite_configuration(
        configuration
    )

    if not integrite.get("succes") or not integrite.get("integre"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "integrite": integrite,
            "erreur": integrite.get(
                "erreur",
                "L'intégrité de la configuration est compromise."
            )
        }

    # --------------------------------------------------------
    # 3. VERIFICATION DU VERROUILLAGE
    # --------------------------------------------------------

    verrouillage = mia_verifier_verrouillage_post_activation(
        configuration
    )

    if not verrouillage.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "integrite": integrite,
            "verrouillage": verrouillage,
            "erreur": verrouillage.get(
                "erreur",
                "Le verrouillage post-activation est compromis."
            )
        }

    # --------------------------------------------------------
    # 4. VERIFICATION DE LA TRAÇABILITE
    # --------------------------------------------------------

    trace = mia_tracer_verrouillage_post_activation(
        journal,
        configuration
    )

    if not trace.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "integrite": integrite,
            "verrouillage": verrouillage,
            "tracabilite": trace,
            "erreur": trace.get(
                "erreur",
                "La traçabilité du verrouillage a échoué."
            )
        }

    # --------------------------------------------------------
    # 5. AUDIT GLOBAL VALIDE
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "AUDIT_POST_ACTIVATION_VALIDE",
        "statut": configuration.get("statut"),
        "integrite": integrite,
        "verrouillage": verrouillage,
        "tracabilite": trace,
        "journal": journal,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 25 : COHERENCE GLOBALE DU JOURNAL
# ============================================================

def mia_verifier_coherence_journal_post_activation(journal, configuration):
    """
    Brique 25 — Vérifie la cohérence globale du journal
    après activation.

    Fonction strictement non destructive :
    - ne modifie pas le journal ;
    - ne modifie pas la configuration ;
    - ne déclenche aucune activation ;
    - ne change aucun statut.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    if journal.get("version") != "V24":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal n'est pas un journal MIA V24."
        }

    evenements = journal.get("evenements")

    if not isinstance(evenements, list):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La liste des événements est invalide."
        }

    nombre_evenements = journal.get("nombre_evenements")

    if not isinstance(nombre_evenements, int):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le nombre d'événements est invalide."
        }

    if nombre_evenements != len(evenements):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "Le nombre d'événements ne correspond pas "
                "au contenu réel du journal."
            ),
            "nombre_declare": nombre_evenements,
            "nombre_reel": len(evenements)
        }

    if configuration.get("statut") != "ACTIVE":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "La configuration doit être ACTIVE "
                "pour effectuer cet audit."
            )
        }

    configuration_id = (
        configuration.get("id")
        or configuration.get("configuration_id")
    )

    if not configuration_id:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Impossible d'identifier la configuration."
        }

    actions = []

    for index, evenement in enumerate(evenements, 1):

        if not isinstance(evenement, dict):
            return {
                "succes": False,
                "autorisation": False,
                "activation": False,
                "decision": "REFUSER",
                "erreur": (
                    f"L'événement {index} n'est pas un dictionnaire."
                )
            }

        champs_obligatoires = {
            "id",
            "date",
            "configuration_id",
            "nom_configuration",
            "action",
            "statut",
            "source",
            "details",
            "version"
        }

        champs_manquants = sorted(
            champ
            for champ in champs_obligatoires
            if champ not in evenement
        )

        if champs_manquants:
            return {
                "succes": False,
                "autorisation": False,
                "activation": False,
                "decision": "REFUSER",
                "erreur": (
                    f"L'événement {index} contient des champs manquants."
                ),
                "champs_manquants": champs_manquants
            }

        if evenement.get("version") != "V24":
            return {
                "succes": False,
                "autorisation": False,
                "activation": False,
                "decision": "REFUSER",
                "erreur": (
                    f"L'événement {index} n'est pas en version V24."
                )
            }

        if evenement.get("configuration_id") != configuration_id:
            return {
                "succes": False,
                "autorisation": False,
                "activation": False,
                "decision": "REFUSER",
                "erreur": (
                    f"L'événement {index} ne correspond pas "
                    "à la configuration contrôlée."
                )
            }

        actions.append(evenement.get("action"))

    activations = [
        evenement
        for evenement in evenements
        if evenement.get("action") == "ACTIVATION"
    ]

    if not activations:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "Aucun événement ACTIVATION n'est présent "
                "dans le journal."
            )
        }

    activation_active = [
        evenement
        for evenement in activations
        if evenement.get("statut") == "ACTIVE"
    ]

    if not activation_active:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": (
                "L'événement ACTIVATION ne confirme pas "
                "le statut ACTIVE."
            )
        }

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "COHERENCE_JOURNAL_VALIDEE",
        "version": journal.get("version"),
        "configuration_id": configuration_id,
        "statut_configuration": configuration.get("statut"),
        "nombre_evenements": len(evenements),
        "actions": actions,
        "activation_tracee": True,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 26 : ANALYSE DES ANOMALIES DU CYCLE
# ============================================================

def mia_analyser_anomalies_cycle(journal, configuration):
    """
    Brique 26 — Analyse non destructive des anomalies du cycle MIA.

    Vérifie :
    - la structure du journal ;
    - la cohérence du nombre d'événements ;
    - l'identité de la configuration ;
    - la présence des événements essentiels ;
    - la cohérence des statuts ;
    - l'ordre logique du cycle.

    Cette fonction :
    - ne modifie jamais le journal ;
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - ne change aucun statut ;
    - signale les anomalies au lieu de les corriger automatiquement.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "anomalies": [
                "Le journal doit être un dictionnaire."
            ],
            "erreur": "Journal invalide."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "anomalies": [
                "La configuration doit être un dictionnaire."
            ],
            "erreur": "Configuration invalide."
        }

    anomalies = []

    evenements = journal.get("evenements")

    if not isinstance(evenements, list):
        anomalies.append(
            "La liste des événements est absente ou invalide."
        )
        evenements = []

    nombre_annonce = journal.get("nombre_evenements")

    if nombre_annonce != len(evenements):
        anomalies.append(
            "Le nombre d'événements ne correspond pas "
            "au contenu réel du journal."
        )

    configuration_id = (
        configuration.get("id")
        or configuration.get("configuration_id")
    )

    if not configuration_id:
        anomalies.append(
            "Identifiant de configuration absent."
        )

    actions = []

    for index, evenement in enumerate(evenements, 1):

        if not isinstance(evenement, dict):
            anomalies.append(
                f"L'événement {index} n'est pas un dictionnaire."
            )
            continue

        evenement_id = (
            evenement.get("configuration_id")
        )

        if configuration_id and evenement_id != configuration_id:
            anomalies.append(
                f"L'événement {index} ne correspond pas "
                "à la configuration contrôlée."
            )

        action = evenement.get("action")

        if action:
            actions.append(action)
        else:
            anomalies.append(
                f"L'événement {index} ne possède aucune action."
            )

    # --------------------------------------------------------
    # VERIFICATION DU CYCLE LOGIQUE
    # --------------------------------------------------------

    if "CONTROLE_SECURITE" not in actions:
        anomalies.append(
            "Aucun événement CONTROLE_SECURITE n'est présent."
        )

    if "ACTIVATION" not in actions:
        anomalies.append(
            "Aucun événement ACTIVATION n'est présent."
        )

    if "ACTIVATION" in actions:
        index_controle = (
            actions.index("CONTROLE_SECURITE")
            if "CONTROLE_SECURITE" in actions
            else None
        )

        index_activation = actions.index("ACTIVATION")

        if (
            index_controle is not None
            and index_controle > index_activation
        ):
            anomalies.append(
                "L'ordre du cycle est incohérent : "
                "l'activation précède le contrôle de sécurité."
            )

    # --------------------------------------------------------
    # VERIFICATION DU STATUT FINAL
    # --------------------------------------------------------

    statut = configuration.get("statut")

    if "ACTIVATION" in actions and statut != "ACTIVE":
        anomalies.append(
            "Une activation est journalisée alors que "
            "la configuration n'est pas ACTIVE."
        )

    if (
        "ACTIVATION" not in actions
        and statut == "ACTIVE"
    ):
        anomalies.append(
            "La configuration est ACTIVE sans événement "
            "d'activation dans le journal."
        )

    # --------------------------------------------------------
    # RESULTAT FINAL
    # --------------------------------------------------------

    if anomalies:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "ANOMALIES_DETECTEES",
            "anomalies": anomalies,
            "nombre_anomalies": len(anomalies),
            "nombre_evenements": len(evenements),
            "actions": actions,
            "erreur": "Des anomalies ont été détectées dans le cycle."
        }

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "CYCLE_COHERENT",
        "anomalies": [],
        "nombre_anomalies": 0,
        "nombre_evenements": len(evenements),
        "actions": actions,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 27 : SYNTHESE SECURISEE DU CYCLE
# ============================================================

def mia_synthetiser_cycle_securise(journal, configuration):
    """
    Brique 27 — Produit une synthèse sécurisée et non destructive
    du cycle MIA post-activation.

    Vérifie successivement :
    - la cohérence du journal ;
    - l'intégrité de la configuration ;
    - le verrouillage post-activation ;
    - la traçabilité ;
    - les anomalies du cycle.

    Cette fonction :
    - ne modifie jamais le journal ;
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - ne change aucun statut ;
    - refuse toute synthèse si un contrôle essentiel échoue.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. COHERENCE DU JOURNAL
    # --------------------------------------------------------

    coherence = mia_verifier_coherence_journal_post_activation(
        journal,
        configuration
    )

    if not coherence.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "coherence": coherence,
            "erreur": coherence.get(
                "erreur",
                "La cohérence du journal est refusée."
            )
        }

    # --------------------------------------------------------
    # 2. INTEGRITE
    # --------------------------------------------------------

    integrite = mia_verifier_integrite_configuration(
        configuration
    )

    if (
        not integrite.get("succes")
        or integrite.get("integre") is not True
    ):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "coherence": coherence,
            "integrite": integrite,
            "erreur": integrite.get(
                "erreur",
                "L'intégrité de la configuration est refusée."
            )
        }

    # --------------------------------------------------------
    # 3. VERROUILLAGE
    # --------------------------------------------------------

    verrouillage = mia_verifier_verrouillage_post_activation(
        configuration
    )

    if not verrouillage.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "coherence": coherence,
            "integrite": integrite,
            "verrouillage": verrouillage,
            "erreur": verrouillage.get(
                "erreur",
                "Le verrouillage post-activation est refusé."
            )
        }

    # --------------------------------------------------------
    # 4. TRACABILITE NON DESTRUCTIVE
    # --------------------------------------------------------
    # La Brique 27 ne doit jamais modifier le journal.
    # Le contrôle de traçabilité repose donc sur le résultat
    # du verrouillage déjà vérifié.
    #
    # IMPORTANT :
    # mia_tracer_verrouillage_post_activation() est volontairement
    # NOT appelé ici car cette fonction ajoute un événement au journal.

    tracabilite = {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": verrouillage.get(
            "decision",
            "VERROUILLEE"
        ),
        "verrouillage": verrouillage,
        "journalisation": False,
        "modification_journal": False,
        "erreur": None
    }

    # --------------------------------------------------------
    # 5. ANALYSE DES ANOMALIES
    # --------------------------------------------------------

    anomalies = mia_analyser_anomalies_cycle(
        journal,
        configuration
    )

    if not anomalies.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "decision": "REFUSER",
            "coherence": coherence,
            "integrite": integrite,
            "verrouillage": verrouillage,
            "tracabilite": tracabilite,
            "anomalies": anomalies,
            "erreur": anomalies.get(
                "erreur",
                "Des anomalies ont été détectées."
            )
        }

    # --------------------------------------------------------
    # 6. SYNTHESE FINALE
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "decision": "CYCLE_SECURise_VALIDE",
        "statut": configuration.get("statut"),
        "coherence": coherence,
        "integrite": integrite,
        "verrouillage": verrouillage,
        "tracabilite": tracabilite,
        "anomalies": anomalies,
        "resume": {
            "journal_coherent": True,
            "integrite_valide": True,
            "verrouillage_valide": True,
            "tracabilite_valide": True,
            "aucune_anomalie": True
        },
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 28 : CONTROLE FINAL AVANT CLOTURE DU CYCLE
# ============================================================

def mia_controle_final_avant_cloture(journal, configuration):
    """
    Brique 28 — Contrôle final, sécurisé et non destructif
    avant la clôture du cycle MIA.

    Vérifie successivement :
    - la synthèse sécurisée du cycle ;
    - la cohérence du journal ;
    - l'intégrité de la configuration ;
    - le verrouillage post-activation ;
    - la traçabilité ;
    - l'absence d'anomalies ;
    - le statut ACTIVE.

    Cette fonction :
    - ne modifie jamais le journal ;
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - ne change aucun statut ;
    - refuse la clôture si un contrôle essentiel échoue.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. VERIFICATION DU STATUT
    # --------------------------------------------------------

    if configuration.get("statut") != "ACTIVE":
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "erreur": (
                "La clôture du cycle exige une configuration ACTIVE."
            )
        }

    # --------------------------------------------------------
    # 2. SYNTHESE SECURISEE
    # --------------------------------------------------------

    synthese = mia_synthetiser_cycle_securise(
        journal,
        configuration
    )

    if not synthese.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "synthese": synthese,
            "erreur": synthese.get(
                "erreur",
                "La synthèse sécurisée du cycle est refusée."
            )
        }

    # --------------------------------------------------------
    # 3. VERIFICATION EXPLICITE DE L'INTEGRITE
    # --------------------------------------------------------

    integrite = mia_verifier_integrite_configuration(
        configuration
    )

    if (
        not integrite.get("succes")
        or integrite.get("integre") is not True
    ):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "synthese": synthese,
            "integrite": integrite,
            "erreur": integrite.get(
                "erreur",
                "L'intégrité de la configuration est refusée."
            )
        }

    # --------------------------------------------------------
    # 4. VERIFICATION DU VERROUILLAGE
    # --------------------------------------------------------

    verrouillage = mia_verifier_verrouillage_post_activation(
        configuration
    )

    if not verrouillage.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "synthese": synthese,
            "integrite": integrite,
            "verrouillage": verrouillage,
            "erreur": verrouillage.get(
                "erreur",
                "Le verrouillage post-activation est refusé."
            )
        }

    # --------------------------------------------------------
    # 5. RECUPERATION DE LA TRACABILITE DE LA SYNTHESE
    # --------------------------------------------------------
    # La Brique 27 a déjà effectué le contrôle et la
    # traçabilité. La Brique 28 réutilise son résultat
    # afin d'éviter toute double journalisation.
    
    tracabilite = synthese.get("tracabilite")

    if (
        not isinstance(tracabilite, dict)
        or not tracabilite.get("succes")
    ):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "synthese": synthese,
            "integrite": integrite,
            "verrouillage": verrouillage,
            "tracabilite": tracabilite,
            "erreur": (
                "La traçabilité issue de la synthèse sécurisée est invalide."
            )
        }

    # --------------------------------------------------------
    # 6. VERIFICATION DES ANOMALIES
    # --------------------------------------------------------

    anomalies = mia_analyser_anomalies_cycle(
        journal,
        configuration
    )

    if not anomalies.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "synthese": synthese,
            "integrite": integrite,
            "verrouillage": verrouillage,
            "tracabilite": tracabilite,
            "anomalies": anomalies,
            "erreur": anomalies.get(
                "erreur",
                "Des anomalies empêchent la clôture du cycle."
            )
        }

    # --------------------------------------------------------
    # 7. CONTROLE FINAL
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "cloture": True,
        "decision": "CLOTURE_CYCLE_AUTORISEE",
        "statut": configuration.get("statut"),
        "synthese": synthese,
        "integrite": integrite,
        "verrouillage": verrouillage,
        "tracabilite": tracabilite,
        "anomalies": anomalies,
        "resume": {
            "synthese_valide": True,
            "journal_coherent": True,
            "integrite_valide": True,
            "verrouillage_valide": True,
            "tracabilite_valide": True,
            "aucune_anomalie": True,
            "configuration_active": True,
            "activation_declenchee": False
        },
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 29 : ENREGISTREMENT SECURISE DE LA CLOTURE
# ============================================================

def mia_enregistrer_cloture_cycle(journal, configuration):
    """
    Brique 29 — Enregistre de manière sécurisée la clôture
    d'un cycle MIA après validation complète.

    Vérifie :
    - le contrôle final avant clôture ;
    - la cohérence du journal ;
    - l'intégrité ;
    - le verrouillage ;
    - la traçabilité ;
    - l'absence d'anomalies ;
    - l'autorisation effective de clôture.

    Cette fonction :
    - ne modifie jamais la configuration ;
    - n'effectue aucune activation ;
    - ne change aucun statut ;
    - ajoute uniquement un événement de clôture
      au journal lorsque tous les contrôles sont valides.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    # --------------------------------------------------------
    # 1. CONTROLE FINAL AVANT CLOTURE
    # --------------------------------------------------------

    controle = mia_controle_final_avant_cloture(
        journal,
        configuration
    )

    if not controle.get("succes"):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "controle": controle,
            "erreur": controle.get(
                "erreur",
                "Le contrôle final avant clôture a échoué."
            )
        }

    # --------------------------------------------------------
    # 2. IDENTIFICATION DE LA CONFIGURATION
    # --------------------------------------------------------

    configuration_id = (
        configuration.get("id")
        or configuration.get("configuration_id")
    )

    if not configuration_id:
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "controle": controle,
            "erreur": "Identifiant de configuration absent."
        }

    # --------------------------------------------------------
    # 3. PREPARATION DE L'EVENEMENT DE CLOTURE
    # --------------------------------------------------------

    from datetime import datetime

    date_cloture = datetime.now().isoformat()

    evenement = {
        "id": f"MIA-EVENT-CLOTURE-{date_cloture}",
        "date": date_cloture,
        "configuration_id": configuration_id,
        "nom_configuration": configuration.get("nom"),
        "action": "CLOTURE",
        "statut": configuration.get("statut"),
        "source": "MIA",
        "details": (
            "Clôture du cycle autorisée après validation "
            "complète des contrôles de sécurité."
        ),
        "version": configuration.get("version", "V24")
    }

    # --------------------------------------------------------
    # 4. ENREGISTREMENT SECURISE
    # --------------------------------------------------------

    evenements = journal.get("evenements")

    if not isinstance(evenements, list):
        return {
            "succes": False,
            "autorisation": False,
            "activation": False,
            "cloture": False,
            "decision": "REFUSER",
            "controle": controle,
            "erreur": "La liste des événements du journal est invalide."
        }

    evenements.append(evenement)
    journal["nombre_evenements"] = len(evenements)

    # --------------------------------------------------------
    # 5. CONFIRMATION
    # --------------------------------------------------------

    return {
        "succes": True,
        "autorisation": True,
        "activation": False,
        "cloture": True,
        "decision": "CLOTURE_ENREGISTREE",
        "statut": configuration.get("statut"),
        "controle": controle,
        "evenement": evenement,
        "nombre_evenements": journal.get("nombre_evenements"),
        "journal": journal,
        "erreur": None
    }


# ============================================================
# MIA V24 — BRIQUE 30 : CONFIRMATION SECURISEE DE FIN DE CYCLE
# ============================================================

def mia_confirmer_fin_cycle(journal, configuration):
    """
    Brique 30 — Confirme qu'un cycle MIA a été correctement clôturé.

    Vérifie :
    - la validité du journal ;
    - la validité de la configuration ;
    - la présence d'une activation ;
    - la présence d'une clôture ;
    - la cohérence de l'événement de clôture ;
    - l'intégrité de la configuration ;
    - l'absence d'anomalies.

    Cette fonction :
    - ne modifie jamais le journal ;
    - ne modifie jamais la configuration ;
    - ne déclenche aucune activation ;
    - ne crée aucun nouvel événement ;
    - ne change aucun statut.

    La Brique 30 est donc strictement confirmative et non destructive.
    """

    if not isinstance(journal, dict):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "Le journal doit être un dictionnaire."
        }

    if not isinstance(configuration, dict):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "La configuration doit être un dictionnaire."
        }

    evenements = journal.get("evenements")

    if not isinstance(evenements, list):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "La liste des événements du journal est invalide."
        }

    if journal.get("nombre_evenements") != len(evenements):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": (
                "Le nombre d'événements ne correspond pas "
                "au contenu réel du journal."
            )
        }

    # --------------------------------------------------------
    # 1. IDENTIFICATION DE LA CONFIGURATION
    # --------------------------------------------------------

    configuration_id = (
        configuration.get("id")
        or configuration.get("configuration_id")
    )

    if not configuration_id:
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "Impossible d'identifier la configuration."
        }

    # --------------------------------------------------------
    # 2. RECHERCHE DES EVENEMENTS ESSENTIELS
    # --------------------------------------------------------

    activations = [
        evenement
        for evenement in evenements
        if isinstance(evenement, dict)
        and evenement.get("action") == "ACTIVATION"
    ]

    clotures = [
        evenement
        for evenement in evenements
        if isinstance(evenement, dict)
        and evenement.get("action") == "CLOTURE"
    ]

    if not activations:
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "Aucun événement ACTIVATION n'est présent dans le journal."
        }

    if not clotures:
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": "Aucun événement CLOTURE n'est présent dans le journal."
        }

    # --------------------------------------------------------
    # 3. VERIFICATION DE L'EVENEMENT DE CLOTURE
    # --------------------------------------------------------

    cloture = clotures[-1]

    if cloture.get("configuration_id") != configuration_id:
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": (
                "L'événement de clôture ne correspond pas "
                "à la configuration contrôlée."
            )
        }

    if cloture.get("source") != "MIA":
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "erreur": (
                "L'événement de clôture ne possède pas "
                "une source MIA valide."
            )
        }

    # --------------------------------------------------------
    # 4. VERIFICATION DE L'INTEGRITE
    # --------------------------------------------------------

    integrite = mia_verifier_integrite_configuration(
        configuration
    )

    if (
        not integrite.get("succes")
        or integrite.get("integre") is not True
    ):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "integrite": integrite,
            "erreur": integrite.get(
                "erreur",
                "L'intégrité de la configuration est refusée."
            )
        }

    # --------------------------------------------------------
    # 5. ANALYSE DES ANOMALIES
    # --------------------------------------------------------

    anomalies = mia_analyser_anomalies_cycle(
        journal,
        configuration
    )

    if not anomalies.get("succes"):
        return {
            "succes": False,
            "confirme": False,
            "decision": "REFUSER",
            "integrite": integrite,
            "anomalies": anomalies,
            "erreur": anomalies.get(
                "erreur",
                "Des anomalies empêchent la confirmation du cycle."
            )
        }

    # --------------------------------------------------------
    # 6. CONFIRMATION FINALE
    # --------------------------------------------------------

    return {
        "succes": True,
        "confirme": True,
        "decision": "CYCLE_CLOTURE_CONFIRME",
        "activation": False,
        "cloture": True,
        "configuration_id": configuration_id,
        "evenement_cloture": cloture,
        "integrite": integrite,
        "anomalies": anomalies,
        "modification_journal": False,
        "modification_configuration": False,
        "erreur": None
    }


# ============================================================
# BRIQUE 31 — VALIDATION FINALE MIA V24
# ============================================================

def mia_validation_finale_v24():
    """
    Brique 31 :
    Validation finale de l'intégrité fonctionnelle de MIA V24.
    Ne modifie aucune donnée existante.
    """
    resultats = {}

    try:
        resultats["module_charge"] = True
        resultats["interroger_disponible"] = callable(mia_interroger)
        resultats["generer_reponse_disponible"] = callable(mia_generer_reponse)
        resultats["verifier_configuration_disponible"] = callable(mia_verifier_configuration)
        resultats["verifier_integrite_disponible"] = callable(mia_verifier_integrite_configuration)
        resultats["journalisation_disponible"] = callable(mia_creer_journal_cycle)
        resultats["controle_global_disponible"] = callable(mia_controle_global_avant_activation)

        resultats["validation"] = all(resultats.values())

    except Exception as e:
        resultats["validation"] = False
        resultats["erreur"] = f"{type(e).__name__}: {e}"

    return resultats

# ============================================================
# FIN BRIQUE 31
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 01
# GESTION DES OBJECTIFS
# ============================================================

def mia25_creer_objectif(
    objectif,
    description="",
    priorite="normale",
    resultat_attendu=""
):
    """
    Crée un objectif structuré pour MIA V25.

    Cette fonction ne modifie aucune donnée de V24.
    """

    if not objectif or not str(objectif).strip():
        return None

    priorites_valides = {
        "basse",
        "normale",
        "haute",
        "critique"
    }

    if priorite not in priorites_valides:
        priorite = "normale"

    return {
        "objectif": str(objectif).strip(),
        "description": str(description).strip(),
        "priorite": priorite,
        "etat": "nouveau",
        "resultat_attendu": str(resultat_attendu).strip(),
        "etapes": [],
        "progression": 0,
        "actif": True
    }


def mia25_modifier_etat_objectif(objectif, nouvel_etat):
    """
    Modifie l'état d'un objectif existant.
    """

    if not isinstance(objectif, dict):
        return None

    etats_valides = {
        "nouveau",
        "planifie",
        "en_cours",
        "termine",
        "suspendu",
        "abandonne"
    }

    if nouvel_etat not in etats_valides:
        return objectif

    objectif["etat"] = nouvel_etat

    if nouvel_etat == "termine":
        objectif["progression"] = 100
        objectif["actif"] = False

    elif nouvel_etat == "abandonne":
        objectif["actif"] = False

    else:
        objectif["actif"] = True

    return objectif


def mia25_ajouter_etape_objectif(objectif, etape):
    """
    Ajoute une étape à un objectif.
    """

    if not isinstance(objectif, dict):
        return None

    if not etape or not str(etape).strip():
        return objectif

    objectif.setdefault("etapes", [])

    objectif["etapes"].append({
        "etape": str(etape).strip(),
        "etat": "a_faire"
    })

    return objectif


def mia25_calculer_progression_objectif(objectif):
    """
    Calcule la progression d'un objectif à partir de ses étapes.
    """

    if not isinstance(objectif, dict):
        return 0

    etapes = objectif.get("etapes", [])

    if not etapes:
        return objectif.get("progression", 0)

    terminees = sum(
        1 for etape in etapes
        if etape.get("etat") == "terminee"
    )

    progression = int((terminees / len(etapes)) * 100)

    objectif["progression"] = progression

    if progression == 100:
        objectif["etat"] = "termine"
        objectif["actif"] = False

    return progression


def mia25_consulter_objectif(objectif):
    """
    Retourne une copie simple de l'état actuel d'un objectif.
    """

    if not isinstance(objectif, dict):
        return None

    return {
        "objectif": objectif.get("objectif"),
        "description": objectif.get("description"),
        "priorite": objectif.get("priorite"),
        "etat": objectif.get("etat"),
        "resultat_attendu": objectif.get("resultat_attendu"),
        "nombre_etapes": len(objectif.get("etapes", [])),
        "progression": objectif.get("progression", 0),
        "actif": objectif.get("actif", False)
    }

# ============================================================
# FIN MIA V25 — BRIQUE 01
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 02
# PLANIFICATION DES OBJECTIFS
# ============================================================

def mia25_creer_plan(objectif):
    """
    Crée un plan de réalisation à partir d'un objectif structuré.
    Ne lance aucune action.
    """

    if not isinstance(objectif, dict):
        return None

    if not objectif.get("objectif"):
        return None

    etapes = objectif.get("etapes", [])

    plan = []

    for numero, etape in enumerate(etapes, start=1):
        if isinstance(etape, dict):
            plan.append({
                "numero": numero,
                "etape": etape.get("etape", ""),
                "etat": etape.get("etat", "a_faire"),
                "depend_de": numero - 1 if numero > 1 else None
            })

    return {
        "objectif": objectif.get("objectif"),
        "priorite": objectif.get("priorite", "normale"),
        "etat": "planifie",
        "nombre_etapes": len(plan),
        "etapes": plan,
        "etape_suivante": 1 if plan else None,
        "execution_autorisee": False
    }


def mia25_identifier_etape_suivante(plan):
    """
    Identifie la prochaine étape à réaliser.
    Ne l'exécute pas.
    """

    if not isinstance(plan, dict):
        return None

    etapes = plan.get("etapes", [])

    for etape in etapes:
        if etape.get("etat") != "terminee":
            return etape

    return None


def mia25_mettre_a_jour_plan(plan, numero, nouvel_etat):
    """
    Met à jour l'état d'une étape du plan.
    """

    if not isinstance(plan, dict):
        return None

    etats_valides = {
        "a_faire",
        "en_cours",
        "terminee",
        "bloquee"
    }

    if nouvel_etat not in etats_valides:
        return plan

    for etape in plan.get("etapes", []):
        if etape.get("numero") == numero:
            etape["etat"] = nouvel_etat
            break

    suivante = mia25_identifier_etape_suivante(plan)

    if suivante:
        plan["etape_suivante"] = suivante.get("numero")
        plan["etat"] = "en_cours"
    else:
        plan["etape_suivante"] = None
        plan["etat"] = "termine"

    return plan


def mia25_verifier_plan(plan):
    """
    Vérifie la cohérence minimale d'un plan.
    """

    if not isinstance(plan, dict):
        return False

    if not plan.get("objectif"):
        return False

    if not isinstance(plan.get("etapes"), list):
        return False

    if plan.get("execution_autorisee") is not False:
        return False

    numeros = [
        e.get("numero")
        for e in plan["etapes"]
        if isinstance(e, dict)
    ]

    return numeros == list(range(1, len(plan["etapes"]) + 1))


# ============================================================
# FIN MIA V25 — BRIQUE 02
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 03
# SUIVI D'EXECUTION DU PLAN
# ============================================================

def mia25_suivre_execution_plan(plan):
    """
    Analyse l'état actuel d'un plan.
    Ne lance aucune action automatiquement.
    """

    if not isinstance(plan, dict):
        return None

    etapes = plan.get("etapes", [])

    total = len(etapes)

    terminees = sum(
        1 for etape in etapes
        if etape.get("etat") == "terminee"
    )

    en_cours = sum(
        1 for etape in etapes
        if etape.get("etat") == "en_cours"
    )

    a_faire = sum(
        1 for etape in etapes
        if etape.get("etat") == "a_faire"
    )

    bloquees = sum(
        1 for etape in etapes
        if etape.get("etat") == "bloquee"
    )

    if total:
        progression = int((terminees / total) * 100)
    else:
        progression = 0

    if bloquees > 0:
        statut = "bloque"
    elif terminees == total and total > 0:
        statut = "termine"
    elif en_cours > 0:
        statut = "en_cours"
    else:
        statut = "en_attente"

    return {
        "total_etapes": total,
        "terminees": terminees,
        "en_cours": en_cours,
        "a_faire": a_faire,
        "bloquees": bloquees,
        "progression": progression,
        "statut": statut,
        "execution_autorisee": False
    }


def mia25_detecter_etape_bloquee(plan):
    """
    Recherche une étape bloquée.
    Ne modifie pas le plan.
    """

    if not isinstance(plan, dict):
        return None

    for etape in plan.get("etapes", []):
        if etape.get("etat") == "bloquee":
            return {
                "bloquee": True,
                "numero": etape.get("numero"),
                "etape": etape.get("etape"),
                "action": "intervention_humaine_requise"
            }

    return {
        "bloquee": False,
        "action": "aucune"
    }


def mia25_resumer_execution_plan(plan):
    """
    Produit un résumé lisible du suivi du plan.
    """

    suivi = mia25_suivre_execution_plan(plan)

    if suivi is None:
        return None

    blocage = mia25_detecter_etape_bloquee(plan)

    return {
        "objectif": plan.get("objectif"),
        "statut": suivi.get("statut"),
        "progression": suivi.get("progression"),
        "etapes_terminees": suivi.get("terminees"),
        "etapes_en_cours": suivi.get("en_cours"),
        "etapes_a_faire": suivi.get("a_faire"),
        "etapes_bloquees": suivi.get("bloquees"),
        "intervention_humaine": (
            blocage.get("bloquee", False)
            if blocage else False
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 03
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 04
# DEPENDANCES ET CONDITIONS
# ============================================================

def mia25_verifier_dependances_etape(plan, numero_etape):
    """
    Vérifie si les dépendances d'une étape sont satisfaites.
    Aucune exécution automatique.
    """

    if not isinstance(plan, dict):
        return None

    etapes = plan.get("etapes", [])

    etape_cible = None

    for etape in etapes:
        if etape.get("numero") == numero_etape:
            etape_cible = etape
            break

    if etape_cible is None:
        return None

    depend_de = etape_cible.get("depend_de")

    if depend_de is None:
        return {
            "numero": numero_etape,
            "depend_de": None,
            "dependance_satisfaite": True,
            "disponible": True
        }

    etape_dependance = None

    for etape in etapes:
        if etape.get("numero") == depend_de:
            etape_dependance = etape
            break

    if etape_dependance is None:
        return {
            "numero": numero_etape,
            "depend_de": depend_de,
            "dependance_satisfaite": False,
            "disponible": False,
            "raison": "dependance_introuvable"
        }

    satisfaite = etape_dependance.get("etat") == "terminee"

    return {
        "numero": numero_etape,
        "depend_de": depend_de,
        "dependance_satisfaite": satisfaite,
        "disponible": satisfaite,
        "raison": (
            "dependance_satisfaite"
            if satisfaite
            else "dependance_non_terminee"
        )
    }


def mia25_lister_etapes_disponibles(plan):
    """
    Retourne les étapes dont les dépendances sont satisfaites.
    Ne modifie pas le plan.
    """

    if not isinstance(plan, dict):
        return None

    disponibles = []

    for etape in plan.get("etapes", []):
        numero = etape.get("numero")

        if etape.get("etat") != "a_faire":
            continue

        verification = mia25_verifier_dependances_etape(
            plan,
            numero
        )

        if verification and verification.get("disponible"):
            disponibles.append(etape)

    return disponibles


def mia25_detecter_dependances_bloquantes(plan):
    """
    Identifie les étapes qui ne peuvent pas encore commencer
    à cause d'une dépendance non terminée.
    """

    if not isinstance(plan, dict):
        return None

    bloquees = []

    for etape in plan.get("etapes", []):
        if etape.get("etat") != "a_faire":
            continue

        verification = mia25_verifier_dependances_etape(
            plan,
            etape.get("numero")
        )

        if verification and not verification.get("disponible"):
            bloquees.append({
                "numero": etape.get("numero"),
                "etape": etape.get("etape"),
                "depend_de": etape.get("depend_de"),
                "raison": verification.get("raison")
            })

    return bloquees


def mia25_resumer_dependances_plan(plan):
    """
    Produit une vue synthétique des dépendances du plan.
    """

    if not isinstance(plan, dict):
        return None

    disponibles = mia25_lister_etapes_disponibles(plan)
    bloquantes = mia25_detecter_dependances_bloquantes(plan)

    return {
        "objectif": plan.get("objectif"),
        "etapes_disponibles": [
            etape.get("numero")
            for etape in disponibles
        ],
        "etapes_bloquees_par_dependance": [
            item.get("numero")
            for item in bloquantes
        ],
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 04
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 05
# PRIORISATION INTELLIGENTE DES ÉTAPES
# ============================================================

def mia25_calculer_score_priorite(etape, plan):
    """
    Calcule un score de priorité pour une étape disponible.
    Aucune exécution automatique.
    """

    if not isinstance(etape, dict) or not isinstance(plan, dict):
        return None

    scores_priorite = {
        "basse": 1,
        "normale": 2,
        "haute": 3,
        "critique": 4
    }

    priorite = plan.get("priorite", "normale")
    score = scores_priorite.get(priorite, 2)

    # Une étape sans dépendance est légèrement favorisée.
    if etape.get("depend_de") is None:
        score += 1

    return score


def mia25_prioriser_etapes_disponibles(plan):
    """
    Classe les étapes disponibles par priorité.
    Ne modifie pas le plan.
    """

    if not isinstance(plan, dict):
        return None

    disponibles = mia25_lister_etapes_disponibles(plan)

    if disponibles is None:
        return None

    resultats = []

    for etape in disponibles:
        score = mia25_calculer_score_priorite(etape, plan)

        resultats.append({
            "numero": etape.get("numero"),
            "etape": etape.get("etape"),
            "priorite": plan.get("priorite", "normale"),
            "score": score
        })

    resultats.sort(
        key=lambda item: item.get("score", 0),
        reverse=True
    )

    return resultats


def mia25_selectionner_etape_prioritaire(plan):
    """
    Sélectionne l'étape disponible ayant le meilleur score.
    Ne lance aucune action.
    """

    priorisees = mia25_prioriser_etapes_disponibles(plan)

    if not priorisees:
        return None

    meilleure = priorisees[0]

    return {
        "numero": meilleure.get("numero"),
        "etape": meilleure.get("etape"),
        "priorite": meilleure.get("priorite"),
        "score": meilleure.get("score"),
        "decision": "etape_prioritaire_identifiee",
        "execution_autorisee": False
    }


def mia25_justifier_priorite_etape(plan, numero_etape):
    """
    Explique pourquoi une étape est prioritaire.
    """

    if not isinstance(plan, dict):
        return None

    priorisees = mia25_prioriser_etapes_disponibles(plan)

    if priorisees is None:
        return None

    for item in priorisees:
        if item.get("numero") == numero_etape:
            return {
                "numero": numero_etape,
                "etape": item.get("etape"),
                "priorite": item.get("priorite"),
                "score": item.get("score"),
                "raison": (
                    "étape disponible avec le meilleur niveau "
                    "de priorité actuellement identifié"
                ),
                "execution_autorisee": False
            }

    return {
        "numero": numero_etape,
        "disponible": False,
        "raison": "etape_non_disponible",
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 05
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 06
# RESSOURCES ET CONTRAINTES
# ============================================================

def mia25_creer_ressource(
    nom,
    type_ressource="generale",
    disponible=True,
    quantite=None,
    description=""
):
    """
    Crée une ressource structurée.
    Ne réserve et ne consomme aucune ressource.
    """

    if not nom or not str(nom).strip():
        return None

    types_valides = {
        "humaine",
        "materielle",
        "financiere",
        "temps",
        "information",
        "technique",
        "generale"
    }

    if type_ressource not in types_valides:
        type_ressource = "generale"

    return {
        "nom": str(nom).strip(),
        "type": type_ressource,
        "disponible": bool(disponible),
        "quantite": quantite,
        "description": str(description).strip()
    }


def mia25_creer_contrainte(
    nom,
    type_contrainte="generale",
    active=True,
    description=""
):
    """
    Crée une contrainte structurée.
    Une contrainte décrit une limite connue.
    """

    if not nom or not str(nom).strip():
        return None

    types_valides = {
        "temps",
        "budget",
        "technique",
        "humaine",
        "information",
        "securite",
        "generale"
    }

    if type_contrainte not in types_valides:
        type_contrainte = "generale"

    return {
        "nom": str(nom).strip(),
        "type": type_contrainte,
        "active": bool(active),
        "description": str(description).strip()
    }


def mia25_verifier_ressource(ressource):
    """
    Vérifie simplement si une ressource est disponible.
    Ne modifie pas la ressource.
    """

    if not isinstance(ressource, dict):
        return None

    return {
        "nom": ressource.get("nom"),
        "disponible": ressource.get("disponible", False),
        "utilisable": ressource.get("disponible", False) is True
    }


def mia25_verifier_contrainte(contrainte):
    """
    Vérifie si une contrainte est actuellement active.
    """

    if not isinstance(contrainte, dict):
        return None

    return {
        "nom": contrainte.get("nom"),
        "active": contrainte.get("active", False),
        "bloquante": contrainte.get("active", False) is True
    }


def mia25_evaluer_ressources_et_contraintes(
    ressources=None,
    contraintes=None
):
    """
    Évalue les ressources disponibles et les contraintes actives.
    Ne réserve aucune ressource.
    Ne modifie aucune donnée.
    """

    ressources = ressources or []
    contraintes = contraintes or []

    ressources_valides = [
        r for r in ressources
        if isinstance(r, dict)
    ]

    contraintes_valides = [
        c for c in contraintes
        if isinstance(c, dict)
    ]

    ressources_disponibles = sum(
        1
        for r in ressources_valides
        if r.get("disponible", False) is True
    )

    ressources_indisponibles = sum(
        1
        for r in ressources_valides
        if r.get("disponible", False) is not True
    )

    contraintes_actives = sum(
        1
        for c in contraintes_valides
        if c.get("active", False) is True
    )

    return {
        "nombre_ressources": len(ressources_valides),
        "ressources_disponibles": ressources_disponibles,
        "ressources_indisponibles": ressources_indisponibles,
        "nombre_contraintes": len(contraintes_valides),
        "contraintes_actives": contraintes_actives,
        "ressources_suffisantes": (
            ressources_indisponibles == 0
        ),
        "contraintes_bloquantes": (
            contraintes_actives > 0
        ),
        "execution_autorisee": False
    }


def mia25_resumer_ressources_contraintes(
    ressources=None,
    contraintes=None
):
    """
    Produit un résumé décisionnel des ressources et contraintes.
    """

    evaluation = mia25_evaluer_ressources_et_contraintes(
        ressources,
        contraintes
    )

    if evaluation is None:
        return None

    if evaluation["contraintes_bloquantes"]:
        statut = "contraintes_actives"

    elif not evaluation["ressources_suffisantes"]:
        statut = "ressources_insuffisantes"

    else:
        statut = "conditions_disponibles"

    return {
        "statut": statut,
        "ressources_disponibles": evaluation[
            "ressources_disponibles"
        ],
        "ressources_indisponibles": evaluation[
            "ressources_indisponibles"
        ],
        "contraintes_actives": evaluation[
            "contraintes_actives"
        ],
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 06
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 07
# ÉVALUATION DES RISQUES ET INCERTITUDES
# ============================================================

def mia25_creer_risque(
    nom,
    niveau="moyen",
    probabilite="moyenne",
    impact="moyen",
    description=""
):
    """
    Crée une fiche de risque structurée.
    Aucune action automatique.
    """

    if not nom or not str(nom).strip():
        return None

    niveaux = {"faible", "moyen", "eleve", "critique"}
    probabilites = {"faible", "moyenne", "forte"}

    if niveau not in niveaux:
        niveau = "moyen"

    if probabilite not in probabilites:
        probabilite = "moyenne"

    if impact not in niveaux:
        impact = "moyen"

    return {
        "nom": str(nom).strip(),
        "niveau": niveau,
        "probabilite": probabilite,
        "impact": impact,
        "description": str(description).strip(),
        "traite": False,
        "validation_humaine_requise": niveau in {"eleve", "critique"}
    }


def mia25_creer_incertitude(
    nom,
    niveau="moyen",
    description=""
):
    """
    Crée une incertitude identifiée.
    Une incertitude n'est pas considérée comme un fait certain.
    """

    if not nom or not str(nom).strip():
        return None

    niveaux = {"faible", "moyen", "eleve"}

    if niveau not in niveaux:
        niveau = "moyen"

    return {
        "nom": str(nom).strip(),
        "niveau": niveau,
        "description": str(description).strip(),
        "resolue": False,
        "validation_humaine_requise": niveau == "eleve"
    }


def mia25_evaluer_risque(risque):
    """
    Évalue un risque existant sans le modifier.
    """

    if not isinstance(risque, dict):
        return None

    return {
        "nom": risque.get("nom"),
        "niveau": risque.get("niveau"),
        "probabilite": risque.get("probabilite"),
        "impact": risque.get("impact"),
        "traite": risque.get("traite", False),
        "validation_humaine_requise": (
            risque.get("validation_humaine_requise", False)
        )
    }


def mia25_evaluer_incertitude(incertitude):
    """
    Évalue une incertitude existante sans la modifier.
    """

    if not isinstance(incertitude, dict):
        return None

    return {
        "nom": incertitude.get("nom"),
        "niveau": incertitude.get("niveau"),
        "resolue": incertitude.get("resolue", False),
        "validation_humaine_requise": (
            incertitude.get("validation_humaine_requise", False)
        )
    }


def mia25_analyser_risques_et_incertitudes(
    risques=None,
    incertitudes=None
):
    """
    Produit une analyse globale des risques et incertitudes.

    Ne modifie aucune donnée.
    Ne déclenche aucune action.
    """

    risques = risques or []
    incertitudes = incertitudes or []

    risques_valides = [
        r for r in risques
        if isinstance(r, dict)
    ]

    incertitudes_valides = [
        i for i in incertitudes
        if isinstance(i, dict)
    ]

    risques_eleves = sum(
        1
        for r in risques_valides
        if r.get("niveau") in {"eleve", "critique"}
    )

    risques_traites = sum(
        1
        for r in risques_valides
        if r.get("traite") is True
    )

    incertitudes_elevees = sum(
        1
        for i in incertitudes_valides
        if i.get("niveau") == "eleve"
    )

    incertitudes_resolues = sum(
        1
        for i in incertitudes_valides
        if i.get("resolue") is True
    )

    validation_requise = (
        risques_eleves > 0
        or incertitudes_elevees > 0
    )

    return {
        "nombre_risques": len(risques_valides),
        "risques_eleves": risques_eleves,
        "risques_traites": risques_traites,
        "nombre_incertitudes": len(incertitudes_valides),
        "incertitudes_elevees": incertitudes_elevees,
        "incertitudes_resolues": incertitudes_resolues,
        "validation_humaine_requise": validation_requise,
        "execution_autorisee": False
    }


def mia25_resumer_risques_et_incertitudes(
    risques=None,
    incertitudes=None
):
    """
    Produit un résumé décisionnel des risques et incertitudes.
    """

    analyse = mia25_analyser_risques_et_incertitudes(
        risques,
        incertitudes
    )

    if analyse is None:
        return None

    if analyse["validation_humaine_requise"]:
        statut = "validation_humaine_requise"
    elif analyse["nombre_risques"] > 0:
        statut = "risques_identifies"
    elif analyse["nombre_incertitudes"] > 0:
        statut = "incertitudes_identifiees"
    else:
        statut = "aucun_risque_ou_incertitude"

    return {
        "statut": statut,
        "risques_eleves": analyse["risques_eleves"],
        "incertitudes_elevees": analyse["incertitudes_elevees"],
        "validation_humaine_requise": (
            analyse["validation_humaine_requise"]
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 07
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 08
# DECISION CONTROLEE ET VALIDATION HUMAINE
# ============================================================

def mia25_creer_proposition_decision(
    plan,
    decision,
    justification="",
    niveau_confiance="moyen"
):
    """
    Crée une proposition de décision.
    MIA ne prend pas la décision à la place de l'humain.
    Aucune exécution automatique.
    """

    if not isinstance(plan, dict):
        return None

    if not decision or not str(decision).strip():
        return None

    niveaux_valides = {
        "faible",
        "moyen",
        "eleve"
    }

    if niveau_confiance not in niveaux_valides:
        niveau_confiance = "moyen"

    return {
        "objectif": plan.get("objectif"),
        "decision_proposee": str(decision).strip(),
        "justification": str(justification).strip(),
        "niveau_confiance": niveau_confiance,
        "statut": "en_attente_validation_humaine",
        "validation_humaine": False,
        "execution_autorisee": False
    }


def mia25_evaluer_decision_proposee(proposition):
    """
    Évalue une proposition de décision.
    Ne valide pas la décision et ne l'exécute pas.
    """

    if not isinstance(proposition, dict):
        return None

    return {
        "decision_proposee": proposition.get(
            "decision_proposee"
        ),
        "niveau_confiance": proposition.get(
            "niveau_confiance"
        ),
        "statut": proposition.get(
            "statut",
            "en_attente_validation_humaine"
        ),
        "validation_humaine": proposition.get(
            "validation_humaine",
            False
        ),
        "execution_autorisee": False
    }


def mia25_demander_validation_humaine(proposition):
    """
    Prépare une demande de validation humaine.
    La fonction ne valide rien automatiquement.
    """

    if not isinstance(proposition, dict):
        return None

    return {
        "objectif": proposition.get("objectif"),
        "decision_proposee": proposition.get(
            "decision_proposee"
        ),
        "justification": proposition.get(
            "justification"
        ),
        "niveau_confiance": proposition.get(
            "niveau_confiance"
        ),
        "validation_requise": True,
        "validation_humaine": False,
        "execution_autorisee": False,
        "message": (
            "Validation humaine requise avant toute exécution."
        )
    }


def mia25_enregistrer_validation_humaine(
    proposition,
    validation
):
    """
    Enregistre explicitement une validation humaine.
    Cette fonction ne lance aucune action.
    """

    if not isinstance(proposition, dict):
        return None

    if validation is True:
        proposition["validation_humaine"] = True
        proposition["statut"] = "validee_par_humain"
    else:
        proposition["validation_humaine"] = False
        proposition["statut"] = "refusee_par_humain"

    # La validation humaine ne donne pas automatiquement
    # le droit d'exécuter une action.
    proposition["execution_autorisee"] = False

    return proposition


def mia25_resumer_decision_controlee(proposition):
    """
    Produit un résumé de la décision proposée.
    """

    if not isinstance(proposition, dict):
        return None

    return {
        "objectif": proposition.get("objectif"),
        "decision": proposition.get(
            "decision_proposee"
        ),
        "niveau_confiance": proposition.get(
            "niveau_confiance"
        ),
        "statut": proposition.get("statut"),
        "validation_humaine": proposition.get(
            "validation_humaine",
            False
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 08
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 09
# COMPARAISON DES OPTIONS ET AIDE A LA DECISION
# ============================================================

def mia25_creer_option(
    nom,
    description="",
    coherence=0,
    faisabilite=0,
    ressources=0,
    contraintes=0,
    risques=0,
    incertitudes=0
):
    """
    Crée une option structurée pour l'aide à la décision.
    Ne prend aucune décision et n'exécute aucune action.
    """

    if not nom or not str(nom).strip():
        return None

    criteres = {
        "coherence": coherence,
        "faisabilite": faisabilite,
        "ressources": ressources,
        "contraintes": contraintes,
        "risques": risques,
        "incertitudes": incertitudes
    }

    criteres_normalises = {}

    for nom_critere, valeur in criteres.items():
        try:
            valeur = int(valeur)
        except (TypeError, ValueError):
            valeur = 0

        valeur = max(0, min(5, valeur))
        criteres_normalises[nom_critere] = valeur

    return {
        "nom": str(nom).strip(),
        "description": str(description).strip(),
        "criteres": criteres_normalises,
        "execution_autorisee": False
    }


def mia25_evaluer_option(option):
    """
    Évalue une option selon ses six critères.
    Produit un score indicatif de 0 à 30.
    Ne modifie pas l'option.
    """

    if not isinstance(option, dict):
        return None

    criteres = option.get("criteres", {})

    noms_criteres = [
        "coherence",
        "faisabilite",
        "ressources",
        "contraintes",
        "risques",
        "incertitudes"
    ]

    valeurs = [
        criteres.get(critere, 0)
        for critere in noms_criteres
    ]

    score = sum(valeurs)

    if score >= 25:
        confiance = "eleve"
    elif score >= 18:
        confiance = "moyen"
    else:
        confiance = "faible"

    return {
        "nom": option.get("nom"),
        "description": option.get("description"),
        "criteres": dict(criteres),
        "score": score,
        "score_maximum": 30,
        "niveau_confiance": confiance,
        "execution_autorisee": False
    }


def mia25_comparer_options(options):
    """
    Compare plusieurs options.
    Ne sélectionne pas automatiquement une action.
    """

    if not isinstance(options, list):
        return None

    evaluations = []

    for option in options:
        evaluation = mia25_evaluer_option(option)

        if evaluation is not None:
            evaluations.append(evaluation)

    return {
        "nombre_options": len(evaluations),
        "options": evaluations,
        "execution_autorisee": False
    }


def mia25_classer_options(options):
    """
    Classe les options selon leur score indicatif.
    Le classement ne constitue pas une autorisation d'exécution.
    """

    comparaison = mia25_comparer_options(options)

    if comparaison is None:
        return None

    classement = list(comparaison.get("options", []))

    classement.sort(
        key=lambda option: option.get("score", 0),
        reverse=True
    )

    for index, option in enumerate(classement, start=1):
        option["rang"] = index

    return {
        "nombre_options": len(classement),
        "classement": classement,
        "execution_autorisee": False
    }


def mia25_recommander_option(options):
    """
    Identifie l'option présentant le meilleur score indicatif.
    Ne prend pas la décision à la place de l'humain.
    """

    classement = mia25_classer_options(options)

    if classement is None:
        return None

    options_classees = classement.get("classement", [])

    if not options_classees:
        return {
            "option_recommandee": None,
            "statut": "aucune_option",
            "validation_humaine_requise": True,
            "execution_autorisee": False
        }

    meilleure = options_classees[0]

    if meilleure.get("score", 0) < 18:
        return {
            "option_recommandee": None,
            "statut": "aucune_option_suffisamment_fiable",
            "meilleure_option_identifiee": meilleure.get("nom"),
            "meilleur_score": meilleure.get("score"),
            "validation_humaine_requise": True,
            "execution_autorisee": False
        }

    return {
        "option_recommandee": meilleure.get("nom"),
        "score": meilleure.get("score"),
        "niveau_confiance": meilleure.get("niveau_confiance"),
        "raison": (
            "option présentant actuellement le meilleur score "
            "indicatif parmi les options analysées"
        ),
        "validation_humaine_requise": True,
        "execution_autorisee": False
    }


def mia25_resumer_comparaison_options(options):
    """
    Produit un résumé lisible de la comparaison et de la recommandation.
    """

    recommandation = mia25_recommander_option(options)

    if recommandation is None:
        return None

    comparaison = mia25_comparer_options(options)

    return {
        "nombre_options": comparaison.get("nombre_options", 0),
        "option_recommandee": recommandation.get(
            "option_recommandee"
        ),
        "score": recommandation.get("score"),
        "niveau_confiance": recommandation.get(
            "niveau_confiance"
        ),
        "statut": recommandation.get("statut"),
        "validation_humaine_requise": recommandation.get(
            "validation_humaine_requise", True
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 09
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 09
# COMPARAISON DES OPTIONS ET AIDE A LA DECISION
# ============================================================













# ============================================================
# FIN MIA V25 — BRIQUE 09
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 10
# CONTROLE DE COHERENCE GLOBALE
# ============================================================

def mia25_analyser_coherence_globale(
    objectif=None,
    plan=None,
    ressources=None,
    contraintes=None,
    risques=None,
    incertitudes=None,
    proposition_decision=None,
    options=None
):
    """
    Analyse la cohérence globale des éléments de décision de MIA V25.

    Cette fonction :
    - ne modifie aucune donnée ;
    - ne prend aucune décision ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    ressources = ressources or []
    contraintes = contraintes or []
    risques = risques or []
    incertitudes = incertitudes or []
    options = options or []

    controles = {}

    controles["objectif_present"] = isinstance(objectif, dict)
    controles["plan_present"] = isinstance(plan, dict)

    controles["ressources_valides"] = all(
        isinstance(r, dict) for r in ressources
    )

    controles["contraintes_valides"] = all(
        isinstance(c, dict) for c in contraintes
    )

    controles["risques_valides"] = all(
        isinstance(r, dict) for r in risques
    )

    controles["incertitudes_valides"] = all(
        isinstance(i, dict) for i in incertitudes
    )

    controles["decision_valide"] = (
        proposition_decision is None
        or isinstance(proposition_decision, dict)
    )

    controles["options_valides"] = all(
        isinstance(o, dict) for o in options
    )

    coherence_structurelle = all(controles.values())

    contraintes_bloquantes = any(
        c.get("active") is True
        for c in contraintes
        if isinstance(c, dict)
    )

    validation_risque = any(
        r.get("validation_humaine_requise") is True
        for r in risques
        if isinstance(r, dict)
    )

    validation_incertitude = any(
        i.get("validation_humaine_requise") is True
        for i in incertitudes
        if isinstance(i, dict)
    )

    validation_decision = (
        isinstance(proposition_decision, dict)
        and proposition_decision.get(
            "validation_humaine", False
        ) is True
    )

    validation_humaine_requise = (
        validation_risque
        or validation_incertitude
        or (
            isinstance(proposition_decision, dict)
            and proposition_decision.get(
                "validation_humaine", False
            ) is False
        )
    )

    return {
        "coherence_structurelle": coherence_structurelle,
        "controles": controles,
        "contraintes_bloquantes": contraintes_bloquantes,
        "validation_risque_requise": validation_risque,
        "validation_incertitude_requise": validation_incertitude,
        "validation_decision_requise": validation_humaine_requise,
        "validation_humaine_requise": validation_humaine_requise,
        "execution_autorisee": False
    }


def mia25_evaluer_coherence_globale(analyse):
    """
    Évalue une analyse de cohérence globale existante.
    """

    if not isinstance(analyse, dict):
        return None

    coherence = analyse.get(
        "coherence_structurelle", False
    )

    contraintes = analyse.get(
        "contraintes_bloquantes", False
    )

    validation = analyse.get(
        "validation_humaine_requise", True
    )

    if not coherence:
        statut = "incoherence_detectee"
    elif contraintes:
        statut = "contraintes_bloquantes"
    elif validation:
        statut = "validation_humaine_requise"
    else:
        statut = "coherent"

    return {
        "statut": statut,
        "coherence_structurelle": coherence,
        "contraintes_bloquantes": contraintes,
        "validation_humaine_requise": validation,
        "execution_autorisee": False
    }


def mia25_resumer_coherence_globale(analyse):
    """
    Produit un résumé décisionnel de la cohérence globale.
    """

    evaluation = mia25_evaluer_coherence_globale(analyse)

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "coherence_structurelle": evaluation.get(
            "coherence_structurelle"
        ),
        "contraintes_bloquantes": evaluation.get(
            "contraintes_bloquantes"
        ),
        "validation_humaine_requise": evaluation.get(
            "validation_humaine_requise"
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 10
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 11
# TRAÇABILITÉ ET JOURNAL DES DÉCISIONS
# ============================================================

def mia25_creer_entree_journal(
    type_evenement,
    description="",
    source="MIA",
    niveau="information",
    validation_humaine=False
):
    """
    Crée une entrée structurée dans le journal de MIA V25.

    Cette fonction :
    - ne déclenche aucune action ;
    - ne modifie aucune décision ;
    - ne donne aucune autorisation d'exécution.
    """

    types_valides = {
        "proposition",
        "evaluation",
        "validation",
        "refus",
        "information",
        "alerte"
    }

    niveaux_valides = {
        "information",
        "attention",
        "important",
        "critique"
    }

    if not type_evenement or not str(type_evenement).strip():
        return None

    if type_evenement not in types_valides:
        type_evenement = "information"

    if niveau not in niveaux_valides:
        niveau = "information"

    return {
        "type_evenement": str(type_evenement).strip(),
        "description": str(description).strip(),
        "source": str(source).strip(),
        "niveau": niveau,
        "validation_humaine": bool(validation_humaine),
        "execution_autorisee": False
    }


def mia25_ajouter_entree_journal(journal, entree):
    """
    Ajoute une entrée au journal.

    Aucun événement n'est exécuté automatiquement.
    """

    if not isinstance(journal, list):
        return None

    if not isinstance(entree, dict):
        return journal

    nouvelle_entree = dict(entree)
    nouvelle_entree["numero"] = len(journal) + 1
    nouvelle_entree["execution_autorisee"] = False

    journal.append(nouvelle_entree)

    return journal


def mia25_consulter_journal(journal):
    """
    Retourne une copie du journal pour consultation.
    """

    if not isinstance(journal, list):
        return None

    return [dict(entree) for entree in journal]


def mia25_filtrer_journal(journal, type_evenement=None):
    """
    Filtre le journal selon le type d'événement.
    """

    if not isinstance(journal, list):
        return None

    if type_evenement is None:
        return [dict(entree) for entree in journal]

    return [
        dict(entree)
        for entree in journal
        if isinstance(entree, dict)
        and entree.get("type_evenement") == type_evenement
    ]


def mia25_analyser_journal(journal):
    """
    Analyse globalement le journal.

    Identifie notamment :
    - le nombre total d'événements ;
    - les propositions ;
    - les validations ;
    - les refus ;
    - les alertes ;
    - les événements critiques.
    """

    if not isinstance(journal, list):
        return None

    analyse = {
        "nombre_entrees": len(journal),
        "propositions": 0,
        "evaluations": 0,
        "validations": 0,
        "refus": 0,
        "informations": 0,
        "alertes": 0,
        "evenements_critiques": 0
    }

    for entree in journal:

        if not isinstance(entree, dict):
            continue

        type_evenement = entree.get("type_evenement")
        niveau = entree.get("niveau")

        if type_evenement == "proposition":
            analyse["propositions"] += 1

        elif type_evenement == "evaluation":
            analyse["evaluations"] += 1

        elif type_evenement == "validation":
            analyse["validations"] += 1

        elif type_evenement == "refus":
            analyse["refus"] += 1

        elif type_evenement == "information":
            analyse["informations"] += 1

        elif type_evenement == "alerte":
            analyse["alertes"] += 1

        if niveau == "critique":
            analyse["evenements_critiques"] += 1

    analyse["execution_autorisee"] = False

    return analyse


def mia25_resumer_journal(journal):
    """
    Produit un résumé du journal de traçabilité.
    """

    analyse = mia25_analyser_journal(journal)

    if analyse is None:
        return None

    return {
        "nombre_entrees": analyse.get("nombre_entrees", 0),
        "propositions": analyse.get("propositions", 0),
        "validations": analyse.get("validations", 0),
        "refus": analyse.get("refus", 0),
        "alertes": analyse.get("alertes", 0),
        "evenements_critiques": analyse.get(
            "evenements_critiques",
            0
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 11
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 12
# MEMOIRE DECISIONNELLE ET CONTINUITE
# ============================================================

def mia25_creer_memoire_decisionnelle():
    """
    Crée une mémoire structurée des décisions de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune décision ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """
    return {
        "entrees": [],
        "nombre_entrees": 0,
        "execution_autorisee": False
    }


def mia25_enregistrer_decision_memoire(
    memoire,
    objectif,
    decision,
    statut="en_attente_validation_humaine",
    validation_humaine=False,
    source="MIA",
    resultat=None
):
    """
    Enregistre une décision ou proposition dans la mémoire décisionnelle.

    L'enregistrement est uniquement informatif et traçable.
    """

    if not isinstance(memoire, dict):
        return None

    if not isinstance(memoire.get("entrees"), list):
        memoire["entrees"] = []

    if not decision or not str(decision).strip():
        return memoire

    entree = {
        "numero": len(memoire["entrees"]) + 1,
        "objectif": str(objectif).strip() if objectif is not None else None,
        "decision": str(decision).strip(),
        "statut": str(statut).strip(),
        "validation_humaine": bool(validation_humaine),
        "source": str(source).strip(),
        "resultat": resultat,
        "execution_autorisee": False
    }

    memoire["entrees"].append(entree)
    memoire["nombre_entrees"] = len(memoire["entrees"])
    memoire["execution_autorisee"] = False

    return entree


def mia25_consulter_memoire_decisionnelle(memoire):
    """
    Retourne une copie de la mémoire décisionnelle.
    """

    if not isinstance(memoire, dict):
        return None

    entrees = memoire.get("entrees", [])

    if not isinstance(entrees, list):
        return []

    return [dict(entree) for entree in entrees if isinstance(entree, dict)]


def mia25_rechercher_decision_memoire(
    memoire,
    objectif=None,
    statut=None
):
    """
    Recherche des décisions enregistrées selon des critères simples.
    """

    if not isinstance(memoire, dict):
        return None

    entrees = memoire.get("entrees", [])

    if not isinstance(entrees, list):
        return []

    resultats = []

    for entree in entrees:
        if not isinstance(entree, dict):
            continue

        if objectif is not None:
            if entree.get("objectif") != objectif:
                continue

        if statut is not None:
            if entree.get("statut") != statut:
                continue

        resultats.append(dict(entree))

    return resultats


def mia25_analyser_continuite_decisionnelle(memoire):
    """
    Analyse la continuité des décisions enregistrées.

    Identifie notamment :
    - le nombre de décisions ;
    - les décisions validées ;
    - les décisions en attente ;
    - les décisions refusées ;
    - les décisions sans validation humaine.
    """

    if not isinstance(memoire, dict):
        return None

    entrees = memoire.get("entrees", [])

    if not isinstance(entrees, list):
        return None

    analyse = {
        "nombre_entrees": 0,
        "decisions_validees": 0,
        "decisions_en_attente": 0,
        "decisions_refusees": 0,
        "sans_validation_humaine": 0,
        "execution_autorisee": False
    }

    for entree in entrees:

        if not isinstance(entree, dict):
            continue

        analyse["nombre_entrees"] += 1

        statut = entree.get("statut")
        validation = entree.get(
            "validation_humaine",
            False
        )

        if statut == "validee_par_humain":
            analyse["decisions_validees"] += 1

        elif statut == "en_attente_validation_humaine":
            analyse["decisions_en_attente"] += 1

        elif statut == "refusee_par_humain":
            analyse["decisions_refusees"] += 1

        if validation is not True:
            analyse["sans_validation_humaine"] += 1

    return analyse


def mia25_resumer_memoire_decisionnelle(memoire):
    """
    Produit un résumé de la mémoire décisionnelle.
    """

    analyse = mia25_analyser_continuite_decisionnelle(
        memoire
    )

    if analyse is None:
        return None

    return {
        "nombre_entrees": analyse.get(
            "nombre_entrees",
            0
        ),
        "decisions_validees": analyse.get(
            "decisions_validees",
            0
        ),
        "decisions_en_attente": analyse.get(
            "decisions_en_attente",
            0
        ),
        "decisions_refusees": analyse.get(
            "decisions_refusees",
            0
        ),
        "sans_validation_humaine": analyse.get(
            "sans_validation_humaine",
            0
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 12
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 12
# MEMOIRE DECISIONNELLE ET CONTINUITE
# ============================================================













# ============================================================
# FIN MIA V25 — BRIQUE 12
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 13
# CONSOLIDATION DU CYCLE DECISIONNEL
# ============================================================

def mia25_consolider_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    journal=None,
    memoire=None
):
    """
    Consolide les éléments du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune décision ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    options = options if isinstance(options, list) else []
    journal = journal if isinstance(journal, list) else []

    if not isinstance(memoire, dict):
        memoire = {}

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get("coherence_structurelle") is True
    )

    validation_requise = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get("validation_humaine_requise") is True
    )

    nombre_options = len([
        option for option in options
        if isinstance(option, dict)
    ])

    nombre_journal = len([
        entree for entree in journal
        if isinstance(entree, dict)
    ])

    entrees_memoire = memoire.get("entrees", [])

    if not isinstance(entrees_memoire, list):
        entrees_memoire = []

    nombre_memoire = len([
        entree for entree in entrees_memoire
        if isinstance(entree, dict)
    ])

    if not coherence_valide:
        statut = "coherence_insuffisante"

    elif validation_requise:
        statut = "validation_humaine_requise"

    else:
        statut = "cycle_coherent"

    return {
        "objectif_present": isinstance(objectif, dict),
        "nombre_options": nombre_options,
        "coherence_valide": coherence_valide,
        "nombre_entrees_journal": nombre_journal,
        "nombre_entrees_memoire": nombre_memoire,
        "statut": statut,
        "validation_humaine_requise": validation_requise,
        "execution_autorisee": False
    }


def mia25_evaluer_cycle_decisionnel(consolidation):
    """
    Évalue le résultat d'une consolidation du cycle décisionnel.

    Aucun élément n'est modifié et aucune action n'est exécutée.
    """

    if not isinstance(consolidation, dict):
        return None

    coherence = consolidation.get(
        "coherence_valide",
        False
    )

    validation = consolidation.get(
        "validation_humaine_requise",
        True
    )

    options = consolidation.get(
        "nombre_options",
        0
    )

    if not coherence:
        statut = "cycle_incoherent"

    elif options == 0:
        statut = "aucune_option"

    elif validation:
        statut = "validation_humaine_requise"

    else:
        statut = "cycle_valide"

    return {
        "statut": statut,
        "coherence_valide": coherence,
        "nombre_options": options,
        "validation_humaine_requise": validation,
        "execution_autorisee": False
    }


def mia25_resumer_cycle_decisionnel(consolidation):
    """
    Produit un résumé lisible du cycle décisionnel consolidé.
    """

    evaluation = mia25_evaluer_cycle_decisionnel(
        consolidation
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "coherence_valide": evaluation.get(
            "coherence_valide"
        ),
        "nombre_options": evaluation.get(
            "nombre_options",
            0
        ),
        "validation_humaine_requise": evaluation.get(
            "validation_humaine_requise",
            True
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 13
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 14
# CONTROLE DES DEPENDANCES DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_dependances_cycle(
    objectif=None,
    options=None,
    analyse_coherence=None,
    journal=None,
    memoire=None
):
    """
    Analyse les dépendances entre les différents éléments
    du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    options = options if isinstance(options, list) else []
    journal = journal if isinstance(journal, list) else []

    dependances = {
        "objectif_vers_options":
            isinstance(objectif, dict) and len(options) > 0,

        "objectif_vers_coherence":
            isinstance(objectif, dict)
            and isinstance(analyse_coherence, dict),

        "coherence_vers_journal":
            isinstance(analyse_coherence, dict)
            and isinstance(journal, list),

        "journal_vers_memoire":
            isinstance(journal, list)
            and isinstance(memoire, dict)
    }

    dependances_valides = all(dependances.values())

    memoire_valide = isinstance(memoire, dict)

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    validation_requise = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "validation_humaine_requise"
        ) is True
    )

    if not dependances_valides:
        statut = "dependances_incompletes"
    elif not coherence_valide:
        statut = "coherence_insuffisante"
    elif validation_requise:
        statut = "validation_humaine_requise"
    else:
        statut = "dependances_coherentes"

    return {
        "dependances": dependances,
        "dependances_valides": dependances_valides,
        "memoire_valide": memoire_valide,
        "coherence_valide": coherence_valide,
        "validation_humaine_requise": validation_requise,
        "statut": statut,
        "execution_autorisee": False
    }


def mia25_evaluer_dependances_cycle(analyse):
    """
    Évalue une analyse des dépendances du cycle décisionnel.

    Aucun élément n'est modifié et aucune action n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    dependances_valides = analyse.get(
        "dependances_valides",
        False
    )

    coherence = analyse.get(
        "coherence_valide",
        False
    )

    validation = analyse.get(
        "validation_humaine_requise",
        True
    )

    if not dependances_valides:
        statut = "dependances_incompletes"
    elif not coherence:
        statut = "coherence_insuffisante"
    elif validation:
        statut = "validation_humaine_requise"
    else:
        statut = "dependances_valides"

    return {
        "statut": statut,
        "dependances_valides": dependances_valides,
        "coherence_valide": coherence,
        "validation_humaine_requise": validation,
        "execution_autorisee": False
    }


def mia25_resumer_dependances_cycle(analyse):
    """
    Produit un résumé du contrôle des dépendances.
    """

    evaluation = mia25_evaluer_dependances_cycle(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "dependances_valides": evaluation.get(
            "dependances_valides"
        ),
        "coherence_valide": evaluation.get(
            "coherence_valide"
        ),
        "validation_humaine_requise": evaluation.get(
            "validation_humaine_requise",
            True
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 14
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 15
# CONTROLE DE COHERENCE DES DECISIONS
# ============================================================

def mia25_analyser_coherence_decisions(
    objectif=None,
    memoire=None,
    analyse_coherence=None,
    analyse_dependances=None
):
    """
    Analyse la cohérence des décisions enregistrées
    avec le cycle décisionnel global de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune décision ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)
    memoire_valide = isinstance(memoire, dict)

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    entrees = []

    if memoire_valide:
        entrees = memoire.get("entrees", [])
        if not isinstance(entrees, list):
            entrees = []

    nombre_decisions = len([
        entree
        for entree in entrees
        if isinstance(entree, dict)
    ])

    decisions_incompatibles = 0
    decisions_en_attente = 0
    decisions_validees = 0
    decisions_refusees = 0

    for entree in entrees:

        if not isinstance(entree, dict):
            continue

        statut = entree.get("statut")

        if statut == "en_attente_validation_humaine":
            decisions_en_attente += 1

        elif statut == "validee_par_humain":
            decisions_validees += 1

        elif statut == "refusee_par_humain":
            decisions_refusees += 1

        if entree.get("execution_autorisee") is not False:
            decisions_incompatibles += 1

    securite_decisions = (
        decisions_incompatibles == 0
    )

    coherence_decisions = (
        objectif_valide
        and memoire_valide
        and coherence_valide
        and dependances_valides
        and securite_decisions
    )

    validation_requise = (
        decisions_en_attente > 0
        or decisions_refusees > 0
        or (
            isinstance(analyse_coherence, dict)
            and analyse_coherence.get(
                "validation_humaine_requise"
            ) is True
        )
    )

    if not coherence_decisions:
        statut = "incoherence_decisions_detectee"
    elif validation_requise:
        statut = "validation_humaine_requise"
    else:
        statut = "decisions_coherentes"

    return {
        "objectif_valide": objectif_valide,
        "memoire_valide": memoire_valide,
        "coherence_globale_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "nombre_decisions": nombre_decisions,
        "decisions_validees": decisions_validees,
        "decisions_en_attente": decisions_en_attente,
        "decisions_refusees": decisions_refusees,
        "decisions_incompatibles": decisions_incompatibles,
        "securite_decisions": securite_decisions,
        "coherence_decisions": coherence_decisions,
        "validation_humaine_requise": validation_requise,
        "statut": statut,
        "execution_autorisee": False
    }


def mia25_evaluer_coherence_decisions(analyse):
    """
    Évalue une analyse de cohérence des décisions.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    coherence = analyse.get(
        "coherence_decisions",
        False
    )

    validation = analyse.get(
        "validation_humaine_requise",
        True
    )

    incompatibles = analyse.get(
        "decisions_incompatibles",
        0
    )

    if incompatibles > 0:
        statut = "decisions_incompatibles"

    elif not coherence:
        statut = "incoherence_decisions"

    elif validation:
        statut = "validation_humaine_requise"

    else:
        statut = "decisions_coherentes"

    return {
        "statut": statut,
        "coherence_decisions": coherence,
        "decisions_incompatibles": incompatibles,
        "validation_humaine_requise": validation,
        "execution_autorisee": False
    }


def mia25_resumer_coherence_decisions(analyse):
    """
    Produit un résumé du contrôle de cohérence
    des décisions.
    """

    evaluation = mia25_evaluer_coherence_decisions(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "coherence_decisions": evaluation.get(
            "coherence_decisions"
        ),
        "decisions_incompatibles": evaluation.get(
            "decisions_incompatibles",
            0
        ),
        "validation_humaine_requise": evaluation.get(
            "validation_humaine_requise",
            True
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 15
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 16
# CONTROLE DE STABILITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_stabilite_cycle_decisionnel(
    objectif=None,
    memoire=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None
):
    """
    Analyse la stabilité du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune décision ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)
    memoire_valide = isinstance(memoire, dict)

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    securite_decisions = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "securite_decisions"
        ) is True
    )

    entrees = []

    if memoire_valide:
        entrees = memoire.get("entrees", [])

    if not isinstance(entrees, list):
        entrees = []

    nombre_decisions = len([
        entree
        for entree in entrees
        if isinstance(entree, dict)
    ])

    decisions_incompatibles = 0
    decisions_en_attente = 0

    for entree in entrees:
        if not isinstance(entree, dict):
            continue

        if entree.get("execution_autorisee") is not False:
            decisions_incompatibles += 1

        if entree.get(
            "statut"
        ) == "en_attente_validation_humaine":
            decisions_en_attente += 1

    stabilite_structurelle = (
        objectif_valide
        and memoire_valide
        and coherence_valide
        and dependances_valides
        and decisions_coherentes
        and securite_decisions
        and decisions_incompatibles == 0
    )

    validation_requise = (
        decisions_en_attente > 0
        or (
            isinstance(analyse_coherence, dict)
            and analyse_coherence.get(
                "validation_humaine_requise"
            ) is True
        )
    )

    if not stabilite_structurelle:
        statut = "stabilite_insuffisante"

    elif validation_requise:
        statut = "validation_humaine_requise"

    else:
        statut = "cycle_stable"

    return {
        "objectif_valide": objectif_valide,
        "memoire_valide": memoire_valide,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "securite_decisions": securite_decisions,
        "nombre_decisions": nombre_decisions,
        "decisions_en_attente": decisions_en_attente,
        "decisions_incompatibles": decisions_incompatibles,
        "stabilite_structurelle": stabilite_structurelle,
        "validation_humaine_requise": validation_requise,
        "statut": statut,
        "execution_autorisee": False
    }


def mia25_evaluer_stabilite_cycle_decisionnel(analyse):
    """
    Évalue la stabilité du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    stabilite = analyse.get(
        "stabilite_structurelle",
        False
    )

    validation = analyse.get(
        "validation_humaine_requise",
        True
    )

    incompatibles = analyse.get(
        "decisions_incompatibles",
        0
    )

    if incompatibles > 0:
        statut = "decisions_incompatibles"

    elif not stabilite:
        statut = "stabilite_insuffisante"

    elif validation:
        statut = "validation_humaine_requise"

    else:
        statut = "cycle_stable"

    return {
        "statut": statut,
        "stabilite_structurelle": stabilite,
        "decisions_incompatibles": incompatibles,
        "validation_humaine_requise": validation,
        "execution_autorisee": False
    }


def mia25_resumer_stabilite_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de stabilité.
    """

    evaluation = mia25_evaluer_stabilite_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "stabilite_structurelle": evaluation.get(
            "stabilite_structurelle"
        ),
        "decisions_incompatibles": evaluation.get(
            "decisions_incompatibles",
            0
        ),
        "validation_humaine_requise": evaluation.get(
            "validation_humaine_requise",
            True
        ),
        "execution_autorisee": False
    }


# ============================================================
# FIN MIA V25 — BRIQUE 16
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 17
# CONTROLE DE COMPLETUDE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_completude_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    journal=None,
    memoire=None
):
    """
    Analyse la complétude du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    elements = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "journal": journal_valide,
        "memoire": memoire_valide
    }

    completude_valide = all(elements.values())

    execution_interdite = True

    if not completude_valide:
        statut = "cycle_incomplet"
    else:
        statut = "cycle_complet"

    return {
        "elements": elements,
        "completude_valide": completude_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_completude_cycle_decisionnel(analyse):
    """
    Évalue la complétude du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    completude = analyse.get(
        "completude_valide",
        False
    )

    if completude:
        statut = "cycle_complet"
    else:
        statut = "cycle_incomplet"

    return {
        "statut": statut,
        "completude_valide": completude,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_completude_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de complétude.
    """

    evaluation = mia25_evaluer_completude_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "completude_valide": evaluation.get(
            "completude_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 17
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 18
# CONTROLE DE CONTINUITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_continuite_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    journal=None,
    memoire=None
):
    """
    Analyse la continuité du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "journal": journal_valide,
        "memoire": memoire_valide
    }

    continuite_valide = all(etapes.values())

    execution_interdite = True

    if not objectif_valide:
        statut = "rupture_objectif"

    elif not options_valides:
        statut = "rupture_options"

    elif not coherence_valide:
        statut = "rupture_coherence"

    elif not dependances_valides:
        statut = "rupture_dependances"

    elif not decisions_coherentes:
        statut = "rupture_decisions"

    elif not stabilite_valide:
        statut = "rupture_stabilite"

    elif not completude_valide:
        statut = "rupture_completude"

    elif not journal_valide:
        statut = "rupture_journal"

    elif not memoire_valide:
        statut = "rupture_memoire"

    else:
        statut = "cycle_continu"

    return {
        "etapes": etapes,
        "continuite_valide": continuite_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_continuite_cycle_decisionnel(analyse):
    """
    Évalue la continuité du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    continuite = analyse.get(
        "continuite_valide",
        False
    )

    if continuite:
        statut = "cycle_continu"
    else:
        statut = "rupture_cycle"

    return {
        "statut": statut,
        "continuite_valide": continuite,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_continuite_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de continuité.
    """

    evaluation = mia25_evaluer_continuite_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "continuite_valide": evaluation.get(
            "continuite_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 18
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 19
# CONTROLE DE TRACABILITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_tracabilite_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    analyse_continuite=None,
    journal=None,
    memoire=None
):
    """
    Analyse la traçabilité du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    continuite_valide = (
        isinstance(analyse_continuite, dict)
        and analyse_continuite.get(
            "continuite_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_tracable = False
    memoire_tracable = False

    if journal_valide:
        journal_tracable = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])
        if isinstance(entrees_memoire, list):
            memoire_tracable = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "continuite": continuite_valide,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_tracable": journal_tracable,
        "memoire_tracable": memoire_tracable
    }

    tracabilite_valide = all(etapes.values())

    execution_interdite = True

    if not tracabilite_valide:
        statut = "tracabilite_incomplete"
    else:
        statut = "cycle_tracable"

    return {
        "etapes": etapes,
        "tracabilite_valide": tracabilite_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "continuite_valide": continuite_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_tracable": journal_tracable,
        "memoire_tracable": memoire_tracable,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_tracabilite_cycle_decisionnel(analyse):
    """
    Évalue la traçabilité du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    tracabilite = analyse.get(
        "tracabilite_valide",
        False
    )

    if tracabilite:
        statut = "cycle_tracable"
    else:
        statut = "tracabilite_incomplete"

    return {
        "statut": statut,
        "tracabilite_valide": tracabilite,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_tracabilite_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de traçabilité.
    """

    evaluation = mia25_evaluer_tracabilite_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "tracabilite_valide": evaluation.get(
            "tracabilite_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 19
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 20
# CONTROLE D'INTEGRITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_integrite_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    analyse_continuite=None,
    analyse_tracabilite=None,
    journal=None,
    memoire=None
):
    """
    Analyse l'intégrité du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    continuite_valide = (
        isinstance(analyse_continuite, dict)
        and analyse_continuite.get(
            "continuite_valide"
        ) is True
    )

    tracabilite_valide = (
        isinstance(analyse_tracabilite, dict)
        and analyse_tracabilite.get(
            "tracabilite_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_integre = False
    memoire_integre = False

    if journal_valide:
        journal_integre = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])

        if isinstance(entrees_memoire, list):
            memoire_integre = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "continuite": continuite_valide,
        "tracabilite": tracabilite_valide,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_integre": journal_integre,
        "memoire_integre": memoire_integre
    }

    integrite_valide = all(etapes.values())

    execution_interdite = True

    if not integrite_valide:
        statut = "integrite_incomplete"
    else:
        statut = "cycle_integre"

    return {
        "etapes": etapes,
        "integrite_valide": integrite_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "continuite_valide": continuite_valide,
        "tracabilite_valide": tracabilite_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_integre": journal_integre,
        "memoire_integre": memoire_integre,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_integrite_cycle_decisionnel(analyse):
    """
    Évalue l'intégrité du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    integrite = analyse.get(
        "integrite_valide",
        False
    )

    if integrite:
        statut = "cycle_integre"
    else:
        statut = "integrite_incomplete"

    return {
        "statut": statut,
        "integrite_valide": integrite,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_integrite_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle d'intégrité.
    """

    evaluation = mia25_evaluer_integrite_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "integrite_valide": evaluation.get(
            "integrite_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 20
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 21
# CONTROLE DE COHERENCE FINALE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_coherence_finale_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    analyse_continuite=None,
    analyse_tracabilite=None,
    analyse_integrite=None,
    journal=None,
    memoire=None
):
    """
    Analyse la cohérence finale du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    continuite_valide = (
        isinstance(analyse_continuite, dict)
        and analyse_continuite.get(
            "continuite_valide"
        ) is True
    )

    tracabilite_valide = (
        isinstance(analyse_tracabilite, dict)
        and analyse_tracabilite.get(
            "tracabilite_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "continuite": continuite_valide,
        "tracabilite": tracabilite_valide,
        "integrite": integrite_valide,
        "journal": journal_valide,
        "memoire": memoire_valide
    }

    coherence_finale_valide = all(etapes.values())

    execution_interdite = True

    if not coherence_finale_valide:
        statut = "coherence_finale_incomplete"
    else:
        statut = "cycle_coherent_finalement"

    return {
        "etapes": etapes,
        "coherence_finale_valide": coherence_finale_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "continuite_valide": continuite_valide,
        "tracabilite_valide": tracabilite_valide,
        "integrite_valide": integrite_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_coherence_finale_cycle_decisionnel(analyse):
    """
    Évalue la cohérence finale du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    coherence_finale = analyse.get(
        "coherence_finale_valide",
        False
    )

    if coherence_finale:
        statut = "cycle_coherent_finalement"
    else:
        statut = "coherence_finale_incomplete"

    return {
        "statut": statut,
        "coherence_finale_valide": coherence_finale,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_coherence_finale_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de cohérence finale.
    """

    evaluation = mia25_evaluer_coherence_finale_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "coherence_finale_valide": evaluation.get(
            "coherence_finale_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 21
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 22
# CONTROLE DE CONFORMITE FINALE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_conformite_finale_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    analyse_continuite=None,
    analyse_tracabilite=None,
    analyse_integrite=None,
    analyse_coherence_finale=None,
    journal=None,
    memoire=None
):
    """
    Analyse la conformité finale du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    continuite_valide = (
        isinstance(analyse_continuite, dict)
        and analyse_continuite.get(
            "continuite_valide"
        ) is True
    )

    tracabilite_valide = (
        isinstance(analyse_tracabilite, dict)
        and analyse_tracabilite.get(
            "tracabilite_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    coherence_finale_valide = (
        isinstance(analyse_coherence_finale, dict)
        and analyse_coherence_finale.get(
            "coherence_finale_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    execution_interdite = True

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "continuite": continuite_valide,
        "tracabilite": tracabilite_valide,
        "integrite": integrite_valide,
        "coherence_finale": coherence_finale_valide,
        "journal": journal_valide,
        "memoire": memoire_valide
    }

    conformite_finale_valide = all(etapes.values())

    if not conformite_finale_valide:
        statut = "conformite_finale_incomplete"
    else:
        statut = "cycle_conforme_finalement"

    return {
        "etapes": etapes,
        "conformite_finale_valide": conformite_finale_valide,
        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "continuite_valide": continuite_valide,
        "tracabilite_valide": tracabilite_valide,
        "integrite_valide": integrite_valide,
        "coherence_finale_valide": coherence_finale_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_conformite_finale_cycle_decisionnel(analyse):
    """
    Évalue la conformité finale du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    conformite_finale = analyse.get(
        "conformite_finale_valide",
        False
    )

    if conformite_finale:
        statut = "cycle_conforme_finalement"
    else:
        statut = "conformite_finale_incomplete"

    return {
        "statut": statut,
        "conformite_finale_valide": conformite_finale,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_conformite_finale_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de conformité finale.
    """

    evaluation = mia25_evaluer_conformite_finale_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "conformite_finale_valide": evaluation.get(
            "conformite_finale_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 22
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 22
# CONTROLE DE VALIDATION GLOBALE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_validation_globale_cycle_decisionnel(
    objectif=None,
    options=None,
    analyse_coherence=None,
    analyse_dependances=None,
    analyse_decisions=None,
    analyse_stabilite=None,
    analyse_completude=None,
    analyse_continuite=None,
    analyse_tracabilite=None,
    analyse_integrite=None,
    analyse_coherence_finale=None,
    journal=None,
    memoire=None
):
    """
    Analyse la validation globale du cycle décisionnel de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    options_valides = (
        isinstance(options, list)
        and len([
            option for option in options
            if isinstance(option, dict)
        ]) > 0
    )

    coherence_valide = (
        isinstance(analyse_coherence, dict)
        and analyse_coherence.get(
            "coherence_structurelle"
        ) is True
    )

    dependances_valides = (
        isinstance(analyse_dependances, dict)
        and analyse_dependances.get(
            "dependances_valides"
        ) is True
    )

    decisions_coherentes = (
        isinstance(analyse_decisions, dict)
        and analyse_decisions.get(
            "coherence_decisions"
        ) is True
    )

    stabilite_valide = (
        isinstance(analyse_stabilite, dict)
        and analyse_stabilite.get(
            "stabilite_structurelle"
        ) is True
    )

    completude_valide = (
        isinstance(analyse_completude, dict)
        and analyse_completude.get(
            "completude_valide"
        ) is True
    )

    continuite_valide = (
        isinstance(analyse_continuite, dict)
        and analyse_continuite.get(
            "continuite_valide"
        ) is True
    )

    tracabilite_valide = (
        isinstance(analyse_tracabilite, dict)
        and analyse_tracabilite.get(
            "tracabilite_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    coherence_finale_valide = (
        isinstance(analyse_coherence_finale, dict)
        and analyse_coherence_finale.get(
            "coherence_finale_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_valide_structure = False
    memoire_valide_structure = False

    if journal_valide:
        journal_valide_structure = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])

        if isinstance(entrees_memoire, list):
            memoire_valide_structure = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "options": options_valides,
        "coherence": coherence_valide,
        "dependances": dependances_valides,
        "decisions": decisions_coherentes,
        "stabilite": stabilite_valide,
        "completude": completude_valide,
        "continuite": continuite_valide,
        "tracabilite": tracabilite_valide,
        "integrite": integrite_valide,
        "coherence_finale": coherence_finale_valide,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_structure": journal_valide_structure,
        "memoire_structure": memoire_valide_structure
    }

    validation_globale_valide = all(
        etapes.values()
    )

    execution_interdite = True

    if not validation_globale_valide:
        statut = "validation_globale_incomplete"
    else:
        statut = "cycle_globalement_valide"

    return {
        "etapes": etapes,
        "validation_globale_valide": validation_globale_valide,

        "objectif_valide": objectif_valide,
        "options_valides": options_valides,
        "coherence_valide": coherence_valide,
        "dependances_valides": dependances_valides,
        "decisions_coherentes": decisions_coherentes,
        "stabilite_valide": stabilite_valide,
        "completude_valide": completude_valide,
        "continuite_valide": continuite_valide,
        "tracabilite_valide": tracabilite_valide,
        "integrite_valide": integrite_valide,
        "coherence_finale_valide": coherence_finale_valide,

        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_structure": journal_valide_structure,
        "memoire_structure": memoire_valide_structure,

        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_validation_globale_cycle_decisionnel(
    analyse
):
    """
    Évalue la validation globale du cycle décisionnel.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    validation_globale = analyse.get(
        "validation_globale_valide",
        False
    )

    if validation_globale:
        statut = "cycle_globalement_valide"
    else:
        statut = "validation_globale_incomplete"

    return {
        "statut": statut,
        "validation_globale_valide": validation_globale,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_validation_globale_cycle_decisionnel(
    analyse
):
    """
    Produit un résumé de la validation globale du cycle.
    """

    evaluation = (
        mia25_evaluer_validation_globale_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "validation_globale_valide": evaluation.get(
            "validation_globale_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 22
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 23
# CONTROLE DE PREPARATION A L'ACTION
# ============================================================

def mia25_analyser_preparation_action_cycle_decisionnel(
    objectif=None,
    analyse_validation_globale=None,
    analyse_coherence_finale=None,
    analyse_integrite=None,
    journal=None,
    memoire=None
):
    """
    Analyse si le cycle décisionnel est suffisamment préparé
    pour envisager une action.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.

    La validation humaine reste obligatoire avant toute exécution.
    """

    objectif_valide = isinstance(objectif, dict)

    validation_globale_valide = (
        isinstance(analyse_validation_globale, dict)
        and analyse_validation_globale.get(
            "validation_globale_valide"
        ) is True
    )

    coherence_finale_valide = (
        isinstance(analyse_coherence_finale, dict)
        and analyse_coherence_finale.get(
            "coherence_finale_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_structure = False
    memoire_structure = False

    if journal_valide:
        journal_structure = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])

        if isinstance(entrees_memoire, list):
            memoire_structure = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "validation_globale": validation_globale_valide,
        "coherence_finale": coherence_finale_valide,
        "integrite": integrite_valide,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure
    }

    preparation_valide = all(etapes.values())

    # La préparation ne signifie jamais que l'action est autorisée.
    execution_autorisee = False
    execution_interdite = True

    if preparation_valide:
        statut = "action_preparee_sous_controle"
    else:
        statut = "preparation_action_incomplete"

    return {
        "etapes": etapes,
        "preparation_valide": preparation_valide,
        "objectif_valide": objectif_valide,
        "validation_globale_valide": validation_globale_valide,
        "coherence_finale_valide": coherence_finale_valide,
        "integrite_valide": integrite_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure,
        "statut": statut,
        "execution_autorisee": execution_autorisee,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_preparation_action_cycle_decisionnel(analyse):
    """
    Évalue la préparation du cycle à une éventuelle action.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    preparation = analyse.get(
        "preparation_valide",
        False
    )

    if preparation:
        statut = "action_preparee_sous_controle"
    else:
        statut = "preparation_action_incomplete"

    return {
        "statut": statut,
        "preparation_valide": preparation,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_preparation_action_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de préparation à l'action.
    """

    evaluation = mia25_evaluer_preparation_action_cycle_decisionnel(
        analyse
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "preparation_valide": evaluation.get(
            "preparation_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 23
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 24
# VALIDATION HUMAINE EXPLICITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_validation_humaine_cycle_decisionnel(
    analyse_preparation=None,
    validation_humaine=None,
    journal=None,
    memoire=None
):
    """
    Contrôle la présence d'une validation humaine explicite.

    Cette fonction :
    - ne prend aucune décision à la place de l'humain ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action automatique ;
    - ne transforme pas une préparation en exécution automatique.

    Une validation humaine explicite peut être constatée,
    mais l'exécution reste interdite par défaut.
    """

    preparation_valide = (
        isinstance(analyse_preparation, dict)
        and analyse_preparation.get(
            "preparation_valide"
        ) is True
    )

    validation_structure_valide = isinstance(
        validation_humaine, dict
    )

    validation_explicite = False

    if validation_structure_valide:
        validation_explicite = (
            validation_humaine.get(
                "validation_explicite"
            ) is True
            and validation_humaine.get(
                "valideur"
            ) is not None
            and validation_humaine.get(
                "decision"
            ) is not None
        )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    etapes = {
        "preparation": preparation_valide,
        "validation_humaine_structure": validation_structure_valide,
        "validation_explicite": validation_explicite,
        "journal": journal_valide,
        "memoire": memoire_valide
    }

    validation_humaine_valide = all(etapes.values())

    # Sécurité : aucune autorisation automatique.
    execution_autorisee = False
    execution_interdite = True

    if validation_humaine_valide:
        statut = "validation_humaine_constatee_sous_controle"
    else:
        statut = "validation_humaine_incomplete"

    return {
        "etapes": etapes,
        "validation_humaine_valide": validation_humaine_valide,
        "preparation_valide": preparation_valide,
        "validation_structure_valide": validation_structure_valide,
        "validation_explicite": validation_explicite,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "statut": statut,
        "execution_autorisee": execution_autorisee,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_validation_humaine_cycle_decisionnel(analyse):
    """
    Évalue le contrôle de validation humaine.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    validation = analyse.get(
        "validation_humaine_valide",
        False
    )

    if validation:
        statut = "validation_humaine_constatee_sous_controle"
    else:
        statut = "validation_humaine_incomplete"

    return {
        "statut": statut,
        "validation_humaine_valide": validation,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_validation_humaine_cycle_decisionnel(analyse):
    """
    Produit un résumé du contrôle de validation humaine.
    """

    evaluation = (
        mia25_evaluer_validation_humaine_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "validation_humaine_valide": evaluation.get(
            "validation_humaine_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 24
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 24
# VALIDATION HUMAINE EXPLICITE DU CYCLE DECISIONNEL
# ============================================================







# ============================================================
# FIN MIA V25 — BRIQUE 24
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 24
# CONTROLE DES CONDITIONS PREALABLES A L'AUTORISATION
# ============================================================

def mia25_analyser_conditions_autorisation_cycle_decisionnel(
    objectif=None,
    analyse_validation_globale=None,
    analyse_coherence_finale=None,
    analyse_integrite=None,
    analyse_preparation_action=None,
    journal=None,
    memoire=None
):
    """
    Contrôle les conditions préalables à une éventuelle
    autorisation d'action de MIA V25.

    Cette fonction :
    - ne prend aucune décision ;
    - ne modifie aucune donnée ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution.

    Elle vérifie uniquement si les conditions structurelles
    préalables sont réunies.
    """

    objectif_valide = isinstance(objectif, dict)

    validation_globale_valide = (
        isinstance(analyse_validation_globale, dict)
        and analyse_validation_globale.get(
            "validation_globale_valide"
        ) is True
    )

    coherence_finale_valide = (
        isinstance(analyse_coherence_finale, dict)
        and analyse_coherence_finale.get(
            "coherence_finale_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    preparation_valide = (
        isinstance(analyse_preparation_action, dict)
        and analyse_preparation_action.get(
            "preparation_valide"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_structure = False
    memoire_structure = False

    if journal_valide:
        journal_structure = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])

        if isinstance(entrees_memoire, list):
            memoire_structure = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "validation_globale": validation_globale_valide,
        "coherence_finale": coherence_finale_valide,
        "integrite": integrite_valide,
        "preparation_action": preparation_valide,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure
    }

    conditions_valides = all(etapes.values())

    # La Brique 24 constate uniquement les conditions.
    # Elle ne transforme jamais ce contrôle en autorisation.
    execution_autorisee = False
    execution_interdite = True

    if conditions_valides:
        statut = "conditions_autorisation_satisfaites"
    else:
        statut = "conditions_autorisation_incompletes"

    return {
        "etapes": etapes,
        "conditions_valides": conditions_valides,
        "objectif_valide": objectif_valide,
        "validation_globale_valide": validation_globale_valide,
        "coherence_finale_valide": coherence_finale_valide,
        "integrite_valide": integrite_valide,
        "preparation_valide": preparation_valide,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure,
        "statut": statut,
        "execution_autorisee": execution_autorisee,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_conditions_autorisation_cycle_decisionnel(
    analyse
):
    """
    Évalue les conditions préalables à une éventuelle
    autorisation.

    Aucun élément n'est modifié et aucune action
    n'est exécutée.
    """

    if not isinstance(analyse, dict):
        return None

    conditions_valides = analyse.get(
        "conditions_valides",
        False
    )

    if conditions_valides:
        statut = "conditions_autorisation_satisfaites"
    else:
        statut = "conditions_autorisation_incompletes"

    return {
        "statut": statut,
        "conditions_valides": conditions_valides,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_conditions_autorisation_cycle_decisionnel(
    analyse
):
    """
    Produit un résumé du contrôle des conditions
    préalables à l'autorisation.
    """

    evaluation = (
        mia25_evaluer_conditions_autorisation_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "conditions_valides": evaluation.get(
            "conditions_valides"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 24
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 25
# DEMANDE D'AUTORISATION HUMAINE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_demande_autorisation_humaine_cycle_decisionnel(
    objectif=None,
    analyse_validation_globale=None,
    analyse_coherence_finale=None,
    analyse_integrite=None,
    analyse_preparation_action=None,
    analyse_conditions_autorisation=None,
    journal=None,
    memoire=None,
    validation_humaine=False
):
    """
    Prépare une demande d'autorisation humaine.

    Principe fondamental :
    - MIA ne s'autorise jamais elle-même ;
    - MIA ne déclenche aucune action ;
    - MIA ne modifie aucune donnée ;
    - l'autorisation finale appartient à l'humain.

    validation_humaine=True signifie uniquement qu'une validation
    humaine explicite a été fournie au système appelant cette fonction.
    """

    objectif_valide = isinstance(objectif, dict)

    validation_globale_valide = (
        isinstance(analyse_validation_globale, dict)
        and analyse_validation_globale.get(
            "validation_globale_valide"
        ) is True
    )

    coherence_finale_valide = (
        isinstance(analyse_coherence_finale, dict)
        and analyse_coherence_finale.get(
            "coherence_finale_valide"
        ) is True
    )

    integrite_valide = (
        isinstance(analyse_integrite, dict)
        and analyse_integrite.get(
            "integrite_valide"
        ) is True
    )

    preparation_valide = (
        isinstance(analyse_preparation_action, dict)
        and analyse_preparation_action.get(
            "preparation_valide"
        ) is True
    )

    conditions_valides = (
        isinstance(analyse_conditions_autorisation, dict)
        and analyse_conditions_autorisation.get(
            "conditions_valides"
        ) is True
    )

    journal_valide = isinstance(journal, list)
    memoire_valide = isinstance(memoire, dict)

    journal_structure = False
    memoire_structure = False

    if journal_valide:
        journal_structure = all(
            isinstance(entree, dict)
            for entree in journal
        )

    if memoire_valide:
        entrees_memoire = memoire.get("entrees", [])

        if isinstance(entrees_memoire, list):
            memoire_structure = all(
                isinstance(entree, dict)
                for entree in entrees_memoire
            )

    etapes = {
        "objectif": objectif_valide,
        "validation_globale": validation_globale_valide,
        "coherence_finale": coherence_finale_valide,
        "integrite": integrite_valide,
        "preparation_action": preparation_valide,
        "conditions_autorisation": conditions_valides,
        "journal": journal_valide,
        "memoire": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure
    }

    conditions_demande_valides = all(etapes.values())

    # --------------------------------------------------------
    # IMPORTANT :
    # Une demande valide n'est PAS une autorisation.
    # --------------------------------------------------------

    demande_autorisation_prete = conditions_demande_valides

    if demande_autorisation_prete:
        statut = "demande_autorisation_humaine_prete"
    else:
        statut = "demande_autorisation_humaine_incomplete"

    # Même si validation_humaine est True, cette fonction
    # ne transforme jamais cela en autorisation d'exécution.
    execution_autorisee = False
    execution_interdite = True

    if validation_humaine is True:
        statut_humain = "validation_humaine_recue"
    else:
        statut_humain = "validation_humaine_en_attente"

    return {
        "etapes": etapes,
        "demande_autorisation_prete": demande_autorisation_prete,
        "objectif_valide": objectif_valide,
        "validation_globale_valide": validation_globale_valide,
        "coherence_finale_valide": coherence_finale_valide,
        "integrite_valide": integrite_valide,
        "preparation_valide": preparation_valide,
        "conditions_autorisation_valides": conditions_valides,
        "journal_valide": journal_valide,
        "memoire_valide": memoire_valide,
        "journal_structure": journal_structure,
        "memoire_structure": memoire_structure,
        "validation_humaine": validation_humaine,
        "statut": statut,
        "statut_humain": statut_humain,
        "execution_autorisee": execution_autorisee,
        "execution_interdite": execution_interdite
    }


def mia25_evaluer_demande_autorisation_humaine_cycle_decisionnel(
    analyse
):
    """
    Évalue l'état de la demande d'autorisation humaine.

    Cette fonction ne déclenche aucune action.
    """

    if not isinstance(analyse, dict):
        return None

    demande_prete = analyse.get(
        "demande_autorisation_prete",
        False
    )

    validation_humaine = analyse.get(
        "validation_humaine",
        False
    )

    if demande_prete:
        statut = "demande_autorisation_humaine_prete"
    else:
        statut = "demande_autorisation_humaine_incomplete"

    if validation_humaine:
        statut_humain = "validation_humaine_recue"
    else:
        statut_humain = "validation_humaine_en_attente"

    return {
        "statut": statut,
        "statut_humain": statut_humain,
        "demande_autorisation_prete": demande_prete,
        "validation_humaine": validation_humaine,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_demande_autorisation_humaine_cycle_decisionnel(
    analyse
):
    """
    Produit un résumé de la demande d'autorisation humaine.
    """

    evaluation = (
        mia25_evaluer_demande_autorisation_humaine_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "statut_humain": evaluation.get("statut_humain"),
        "demande_autorisation_prete": evaluation.get(
            "demande_autorisation_prete"
        ),
        "validation_humaine": evaluation.get(
            "validation_humaine"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 25
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 26
# TRAITEMENT DE LA REPONSE HUMAINE
# ============================================================

def mia25_analyser_reponse_humaine_cycle_decisionnel(
    analyse_demande_autorisation=None,
    reponse_humaine=None
):
    """
    Traite la réponse humaine sans déclencher d'action.
    
    Réponses possibles :
    - autorisee
    - refusee
    - revision_demandee
    """

    demande_valide = (
        isinstance(analyse_demande_autorisation, dict)
        and analyse_demande_autorisation.get(
            "demande_autorisation_prete"
        ) is True
        and analyse_demande_autorisation.get(
            "execution_autorisee"
        ) is False
        and analyse_demande_autorisation.get(
            "execution_interdite"
        ) is True
    )

    reponse_valide = reponse_humaine in {
        "autorisee",
        "refusee",
        "revision_demandee"
    }

    if not demande_valide:
        statut = "demande_autorisation_invalide"
    elif not reponse_valide:
        statut = "reponse_humaine_invalide"
    elif reponse_humaine == "autorisee":
        statut = "autorisation_humaine_recue"
    elif reponse_humaine == "refusee":
        statut = "autorisation_humaine_refusee"
    else:
        statut = "revision_humaine_demandee"

    traitement_valide = (
        demande_valide and reponse_valide
    )

    return {
        "demande_valide": demande_valide,
        "reponse_humaine": reponse_humaine,
        "reponse_valide": reponse_valide,
        "traitement_valide": traitement_valide,
        "statut": statut,

        "autorisation_humaine_recue": (
            traitement_valide
            and reponse_humaine == "autorisee"
        ),

        "autorisation_humaine_refusee": (
            traitement_valide
            and reponse_humaine == "refusee"
        ),

        "revision_humaine_demandee": (
            traitement_valide
            and reponse_humaine == "revision_demandee"
        ),

        # Sécurité : B26 ne déclenche jamais l'action.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_reponse_humaine_cycle_decisionnel(
    analyse
):
    """Évalue la réponse humaine sans exécuter d'action."""

    if not isinstance(analyse, dict):
        return None

    return {
        "statut": analyse.get(
            "statut",
            "reponse_humaine_invalide"
        ),
        "traitement_valide": analyse.get(
            "traitement_valide",
            False
        ),
        "reponse_humaine": analyse.get(
            "reponse_humaine"
        ),
        "autorisation_humaine_recue": analyse.get(
            "autorisation_humaine_recue",
            False
        ),
        "autorisation_humaine_refusee": analyse.get(
            "autorisation_humaine_refusee",
            False
        ),
        "revision_humaine_demandee": analyse.get(
            "revision_humaine_demandee",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_reponse_humaine_cycle_decisionnel(
    analyse
):
    """Produit le résumé de la réponse humaine."""

    evaluation = (
        mia25_evaluer_reponse_humaine_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get("statut"),
        "traitement_valide": evaluation.get(
            "traitement_valide"
        ),
        "reponse_humaine": evaluation.get(
            "reponse_humaine"
        ),
        "autorisation_humaine_recue": evaluation.get(
            "autorisation_humaine_recue"
        ),
        "autorisation_humaine_refusee": evaluation.get(
            "autorisation_humaine_refusee"
        ),
        "revision_humaine_demandee": evaluation.get(
            "revision_humaine_demandee"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 26
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 27
# ETAT DU CYCLE APRES REPONSE HUMAINE
# ============================================================

def mia25_analyser_etat_cycle_apres_reponse_humaine(
    analyse_reponse_humaine=None
):
    """
    Détermine l'état logique du cycle après la réponse humaine.

    Cette brique :
    - n'exécute aucune action ;
    - ne modifie aucune donnée ;
    - ne crée aucune autorisation automatique ;
    - respecte intégralement la réponse humaine.

    Réponses reconnues :
        autorisee
        refusee
        revision_demandee
    """

    analyse_valide = (
        isinstance(analyse_reponse_humaine, dict)
        and analyse_reponse_humaine.get(
            "traitement_valide"
        ) is True
        and analyse_reponse_humaine.get(
            "execution_autorisee"
        ) is False
        and analyse_reponse_humaine.get(
            "execution_interdite"
        ) is True
    )

    reponse = None

    if isinstance(analyse_reponse_humaine, dict):
        reponse = analyse_reponse_humaine.get(
            "reponse_humaine"
        )

    if not analyse_valide:
        etat_cycle = "reponse_humaine_invalide"

    elif reponse == "autorisee":
        etat_cycle = "autorisation_humaine_recue"

    elif reponse == "refusee":
        etat_cycle = "cycle_refuse_par_humain"

    elif reponse == "revision_demandee":
        etat_cycle = "cycle_en_revision_humaine"

    else:
        etat_cycle = "reponse_humaine_inconnue"

    return {
        "analyse_valide": analyse_valide,
        "reponse_humaine": reponse,
        "etat_cycle": etat_cycle,

        "autorisation_humaine_recue": (
            analyse_valide
            and reponse == "autorisee"
        ),

        "cycle_refuse_par_humain": (
            analyse_valide
            and reponse == "refusee"
        ),

        "cycle_en_revision_humaine": (
            analyse_valide
            and reponse == "revision_demandee"
        ),

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_etat_cycle_apres_reponse_humaine(
    analyse
):
    """
    Évalue l'état du cycle sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    return {
        "etat_cycle": analyse.get(
            "etat_cycle",
            "reponse_humaine_invalide"
        ),

        "analyse_valide": analyse.get(
            "analyse_valide",
            False
        ),

        "reponse_humaine": analyse.get(
            "reponse_humaine"
        ),

        "autorisation_humaine_recue": analyse.get(
            "autorisation_humaine_recue",
            False
        ),

        "cycle_refuse_par_humain": analyse.get(
            "cycle_refuse_par_humain",
            False
        ),

        "cycle_en_revision_humaine": analyse.get(
            "cycle_en_revision_humaine",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_etat_cycle_apres_reponse_humaine(
    analyse
):
    """
    Produit un résumé de l'état du cycle.
    """

    evaluation = (
        mia25_evaluer_etat_cycle_apres_reponse_humaine(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "etat_cycle": evaluation.get(
            "etat_cycle"
        ),

        "reponse_humaine": evaluation.get(
            "reponse_humaine"
        ),

        "autorisation_humaine_recue": evaluation.get(
            "autorisation_humaine_recue"
        ),

        "cycle_refuse_par_humain": evaluation.get(
            "cycle_refuse_par_humain"
        ),

        "cycle_en_revision_humaine": evaluation.get(
            "cycle_en_revision_humaine"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 27
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 28
# ORIENTATION DU CYCLE APRES DECISION HUMAINE
# ============================================================

def mia25_analyser_orientation_cycle_apres_decision_humaine(
    analyse_etat_cycle=None
):
    """
    Détermine l'orientation logique du cycle après la décision
    humaine.

    B28 ne déclenche aucune action et ne donne aucune
    autorisation d'exécution.

    Orientations :
        continuer_sous_controle
        cycle_arrete
        revision_necessaire
    """

    analyse_valide = (
        isinstance(analyse_etat_cycle, dict)
        and analyse_etat_cycle.get(
            "analyse_valide"
        ) is True
        and analyse_etat_cycle.get(
            "execution_autorisee"
        ) is False
        and analyse_etat_cycle.get(
            "execution_interdite"
        ) is True
    )

    etat_cycle = None

    if isinstance(analyse_etat_cycle, dict):
        etat_cycle = analyse_etat_cycle.get(
            "etat_cycle"
        )

    if not analyse_valide:
        orientation = "orientation_invalide"

    elif etat_cycle == "autorisation_humaine_recue":
        orientation = "continuer_sous_controle"

    elif etat_cycle == "cycle_refuse_par_humain":
        orientation = "cycle_arrete"

    elif etat_cycle == "cycle_en_revision_humaine":
        orientation = "revision_necessaire"

    else:
        orientation = "orientation_inconnue"

    return {
        "analyse_valide": analyse_valide,
        "etat_cycle": etat_cycle,
        "orientation": orientation,

        "continuer_sous_controle": (
            analyse_valide
            and orientation == "continuer_sous_controle"
        ),

        "cycle_arrete": (
            analyse_valide
            and orientation == "cycle_arrete"
        ),

        "revision_necessaire": (
            analyse_valide
            and orientation == "revision_necessaire"
        ),

        # ----------------------------------------------------
        # VERROU DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_orientation_cycle_apres_decision_humaine(
    analyse
):
    """
    Évalue l'orientation du cycle sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    return {
        "analyse_valide": analyse.get(
            "analyse_valide",
            False
        ),

        "etat_cycle": analyse.get(
            "etat_cycle"
        ),

        "orientation": analyse.get(
            "orientation",
            "orientation_invalide"
        ),

        "continuer_sous_controle": analyse.get(
            "continuer_sous_controle",
            False
        ),

        "cycle_arrete": analyse.get(
            "cycle_arrete",
            False
        ),

        "revision_necessaire": analyse.get(
            "revision_necessaire",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_orientation_cycle_apres_decision_humaine(
    analyse
):
    """
    Produit un résumé de l'orientation du cycle.
    """

    evaluation = (
        mia25_evaluer_orientation_cycle_apres_decision_humaine(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "orientation": evaluation.get(
            "orientation"
        ),

        "etat_cycle": evaluation.get(
            "etat_cycle"
        ),

        "continuer_sous_controle": evaluation.get(
            "continuer_sous_controle"
        ),

        "cycle_arrete": evaluation.get(
            "cycle_arrete"
        ),

        "revision_necessaire": evaluation.get(
            "revision_necessaire"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 28
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 29
# CONTROLE FINAL AVANT TRANSITION DU CYCLE
# ============================================================

def mia25_analyser_controle_final_transition_cycle(
    analyse_orientation=None
):
    """
    Effectue le contrôle final de la transition logique du cycle.

    B29 ne lance aucune action.
    B29 ne transforme jamais une orientation en autorisation
    d'exécution.

    Elle vérifie uniquement que l'état précédent est cohérent
    et que la transition logique peut être préparée.
    """

    analyse_valide = (
        isinstance(analyse_orientation, dict)
        and analyse_orientation.get(
            "analyse_valide"
        ) is True
        and analyse_orientation.get(
            "execution_autorisee"
        ) is False
        and analyse_orientation.get(
            "execution_interdite"
        ) is True
    )

    orientation = None

    if isinstance(analyse_orientation, dict):
        orientation = analyse_orientation.get(
            "orientation"
        )

    orientations_valides = {
        "continuer_sous_controle",
        "cycle_arrete",
        "revision_necessaire"
    }

    orientation_valide = (
        orientation in orientations_valides
    )

    controle_valide = (
        analyse_valide
        and orientation_valide
    )

    if controle_valide:
        statut = "transition_cycle_controlee"
    else:
        statut = "transition_cycle_invalide"

    return {
        "analyse_valide": analyse_valide,
        "orientation": orientation,
        "orientation_valide": orientation_valide,
        "controle_valide": controle_valide,
        "statut": statut,

        "transition_controlee": controle_valide,

        # VERROU DE SECURITE
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_controle_final_transition_cycle(
    analyse
):
    """
    Évalue le contrôle final sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    return {
        "analyse_valide": analyse.get(
            "analyse_valide",
            False
        ),

        "orientation": analyse.get(
            "orientation"
        ),

        "orientation_valide": analyse.get(
            "orientation_valide",
            False
        ),

        "controle_valide": analyse.get(
            "controle_valide",
            False
        ),

        "statut": analyse.get(
            "statut",
            "transition_cycle_invalide"
        ),

        "transition_controlee": analyse.get(
            "transition_controlee",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_controle_final_transition_cycle(
    analyse
):
    """
    Produit le résumé du contrôle final.
    """

    evaluation = (
        mia25_evaluer_controle_final_transition_cycle(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get(
            "statut"
        ),

        "orientation": evaluation.get(
            "orientation"
        ),

        "controle_valide": evaluation.get(
            "controle_valide"
        ),

        "transition_controlee": evaluation.get(
            "transition_controlee"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 29
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 30
# CLOTURE SECURISEE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_cloture_cycle_decisionnel(
    analyse_etat_cycle=None,
    analyse_controle_final=None
):
    """
    B30 clôture le cycle décisionnel sur le plan logique.

    PRINCIPES :
    - aucune exécution ;
    - aucune modification de donnée ;
    - aucune nouvelle autorisation ;
    - aucune auto-validation ;
    - la décision humaine reste souveraine.
    """
    ETATS_VALIDES = {
        "autorisation_humaine_recue",
        "cycle_refuse_par_humain",
        "cycle_en_revision_humaine"
    }

    ORIENTATIONS_VALIDES = {
        "continuer_sous_controle",
        "cycle_arrete",
        "revision_necessaire"
    }

    etat_valide = (
        isinstance(analyse_etat_cycle, dict)
        and analyse_etat_cycle.get(
            "analyse_valide"
        ) is True
        and analyse_etat_cycle.get(
            "etat_cycle"
        ) in ETATS_VALIDES
        and analyse_etat_cycle.get(
            "execution_autorisee"
        ) is False
        and analyse_etat_cycle.get(
            "execution_interdite"
        ) is True
    )

    controle_valide = (
        isinstance(analyse_controle_final, dict)
        and analyse_controle_final.get(
            "analyse_valide"
        ) is True
        and analyse_controle_final.get(
            "controle_valide"
        ) is True
        and analyse_controle_final.get(
            "orientation_valide"
        ) is True
        and analyse_controle_final.get(
            "transition_controlee"
        ) is True
        and analyse_controle_final.get(
            "orientation"
        ) in ORIENTATIONS_VALIDES
        and analyse_controle_final.get(
            "execution_autorisee"
        ) is False
        and analyse_controle_final.get(
            "execution_interdite"
        ) is True
    )

    etat_cycle = (
        analyse_etat_cycle.get("etat_cycle")
        if isinstance(analyse_etat_cycle, dict)
        else None
    )

    securite_etat = (
        isinstance(analyse_etat_cycle, dict)
        and analyse_etat_cycle.get(
            "execution_autorisee"
        ) is False
        and analyse_etat_cycle.get(
            "execution_interdite"
        ) is True
    )

    securite_controle = (
        isinstance(analyse_controle_final, dict)
        and analyse_controle_final.get(
            "execution_autorisee"
        ) is False
        and analyse_controle_final.get(
            "execution_interdite"
        ) is True
    )

    cloture_valide = (
        etat_valide
        and controle_valide
    )

    if cloture_valide:
        statut = "cycle_decisionnel_cloture"
    else:
        statut = "cycle_decisionnel_non_cloturable"

    return {
        "etat_cycle": etat_cycle,
        "etat_valide": etat_valide,
        "controle_valide": controle_valide,
        "securite_etat": securite_etat,
        "securite_controle": securite_controle,
        "cloture_valide": cloture_valide,
        "statut": statut,

        # Sécurité absolue :
        "execution_autorisee": False,
        "execution_interdite": True
    }

def mia25_evaluer_cloture_cycle_decisionnel(
    analyse
):
    """
    Évalue la clôture sans déclencher aucune action.
    """

    if not isinstance(analyse, dict):
        return None

    return {
        "statut": analyse.get(
            "statut",
            "cycle_decisionnel_non_cloturable"
        ),
        "cloture_valide": analyse.get(
            "cloture_valide",
            False
        ),
        "securite_etat": analyse.get(
            "securite_etat",
            False
        ),
        "securite_controle": analyse.get(
            "securite_controle",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_cloture_cycle_decisionnel(
    analyse
):
    """
    Produit le résumé final de B30.
    """

    evaluation = (
        mia25_evaluer_cloture_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "statut": evaluation.get(
            "statut"
        ),
        "cloture_valide": evaluation.get(
            "cloture_valide"
        ),
        "securite_etat": evaluation.get(
            "securite_etat"
        ),
        "securite_controle": evaluation.get(
            "securite_controle"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 30
# ============================================================


# ============================================================
# MIA V25 — BRIQUE 31
# COHERENCE POST-CLOTURE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_coherence_post_cloture_cycle_decisionnel(
    analyse_cloture_cycle=None
):
    """
    Vérifie la cohérence de l'état du cycle après sa clôture.

    B31 ne déclenche aucune action.
    B31 ne crée aucune autorisation d'exécution.
    """

    valide = (
        isinstance(analyse_cloture_cycle, dict)
        and analyse_cloture_cycle.get("cloture_valide") is True
        and analyse_cloture_cycle.get("execution_autorisee") is False
        and analyse_cloture_cycle.get("execution_interdite") is True
    )

    if valide:
        statut = "coherence_post_cloture_validee"
    else:
        statut = "coherence_post_cloture_invalide"

    return {
        "analyse_valide": valide,
        "cloture_valide": (
            analyse_cloture_cycle.get("cloture_valide")
            if isinstance(analyse_cloture_cycle, dict)
            else False
        ),
        "statut": statut,

        # Sécurité fondamentale B31.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_coherence_post_cloture_cycle_decisionnel(
    analyse=None
):
    """
    Évalue la cohérence post-clôture sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    return {
        "analyse_valide": analyse.get(
            "analyse_valide",
            False
        ),
        "cloture_valide": analyse.get(
            "cloture_valide",
            False
        ),
        "statut": analyse.get(
            "statut",
            "coherence_post_cloture_invalide"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_coherence_post_cloture_cycle_decisionnel(
    analyse=None
):
    """
    Produit le résumé de la cohérence post-clôture.
    """

    evaluation = (
        mia25_evaluer_coherence_post_cloture_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get(
            "analyse_valide"
        ),
        "cloture_valide": evaluation.get(
            "cloture_valide"
        ),
        "statut": evaluation.get(
            "statut"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 31
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 32
# TRAÇABILITE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_trace_cycle_decisionnel(
    analyse_coherence_post_cloture=None
):
    """
    Produit une trace structurée du cycle décisionnel.

    B32 est une brique passive :
    elle observe le résultat du cycle sans déclencher
    ni autoriser aucune exécution automatique.
    """

    donnees_valides = (
        isinstance(analyse_coherence_post_cloture, dict)
        and analyse_coherence_post_cloture.get(
            "analyse_valide"
        ) is True
        and analyse_coherence_post_cloture.get(
            "execution_autorisee"
        ) is False
        and analyse_coherence_post_cloture.get(
            "execution_interdite"
        ) is True
    )

    if donnees_valides:
        statut = "trace_cycle_decisionnel_validee"
    else:
        statut = "trace_cycle_decisionnel_invalide"

    return {
        "analyse_valide": donnees_valides,
        "statut": statut,

        "source_coherence_validee": donnees_valides,

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_trace_cycle_decisionnel(
    analyse
):
    """
    Évalue la trace du cycle sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    analyse_valide = (
        analyse.get("analyse_valide") is True
    )

    return {
        "analyse_valide": analyse_valide,
        "statut": analyse.get(
            "statut",
            "trace_cycle_decisionnel_invalide"
        ),
        "source_coherence_validee": analyse.get(
            "source_coherence_validee",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_trace_cycle_decisionnel(
    analyse
):
    """
    Produit le résumé final de la trace décisionnelle.
    """

    evaluation = (
        mia25_evaluer_trace_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get(
            "analyse_valide"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "source_coherence_validee": evaluation.get(
            "source_coherence_validee"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 32
# ============================================================

# ============================================================
# MIA V25 — BRIQUE 33
# VALIDATION INTEGRALE FINALE DU CYCLE DECISIONNEL
# ============================================================

def mia25_analyser_validation_integrale_cycle_decisionnel(
    trace_cycle_decisionnel=None
):
    """
    Validation intégrale finale du cycle décisionnel.

    B33 est une brique terminale et passive.
    Elle vérifie la validité de la chaîne précédente
    sans déclencher ni autoriser aucune exécution.
    """

    donnees_valides = (
        isinstance(trace_cycle_decisionnel, dict)
        and trace_cycle_decisionnel.get(
            "analyse_valide"
        ) is True
        and trace_cycle_decisionnel.get(
            "execution_autorisee"
        ) is False
        and trace_cycle_decisionnel.get(
            "execution_interdite"
        ) is True
    )

    if donnees_valides:
        statut = "validation_integrale_cycle_decisionnel_validee"
    else:
        statut = "validation_integrale_cycle_decisionnel_invalide"

    return {
        "analyse_valide": donnees_valides,
        "validation_integrale": donnees_valides,
        "statut": statut,

        "trace_cycle_validee": donnees_valides,

        # Sécurité terminale :
        # B33 ne déclenche aucune action.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_evaluer_validation_integrale_cycle_decisionnel(
    analyse
):
    """
    Évalue la validation intégrale sans exécuter d'action.
    """

    if not isinstance(analyse, dict):
        return None

    analyse_valide = (
        analyse.get("analyse_valide") is True
        and analyse.get("validation_integrale") is True
    )

    return {
        "analyse_valide": analyse_valide,
        "validation_integrale": analyse_valide,
        "statut": analyse.get(
            "statut",
            "validation_integrale_cycle_decisionnel_invalide"
        ),
        "trace_cycle_validee": analyse.get(
            "trace_cycle_validee",
            False
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia25_resumer_validation_integrale_cycle_decisionnel(
    analyse
):
    """
    Produit le résumé final de la validation intégrale.
    """

    evaluation = (
        mia25_evaluer_validation_integrale_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get(
            "analyse_valide"
        ),
        "validation_integrale": evaluation.get(
            "validation_integrale"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "trace_cycle_validee": evaluation.get(
            "trace_cycle_validee"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V25 — BRIQUE 33
# FIN DE LA CHAINE DECISIONNELLE
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 1
# ANALYSE DU CONTEXTE
# ============================================================

def mia26_analyser_contexte(contexte=None):
    """
    B1 — Analyse structurée du contexte.

    Cette brique observe uniquement les informations fournies.
    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = isinstance(contexte, dict)

    if contexte_valide:
        statut = "contexte_valide"
    else:
        statut = "contexte_invalide"

    return {
        "analyse_valide": contexte_valide,
        "contexte_valide": contexte_valide,
        "statut": statut,
        "contexte": contexte if contexte_valide else None,

        # Sécurité : aucune exécution automatique.
        # Transmission intacte des états de contrôle vers B02.
        "approbation_controlee": contexte.get(
            "approbation_controlee"
        ),
        "approbation_humaine": contexte.get(
            "approbation_humaine"
        ),
        "activation_valide": contexte.get(
            "activation_valide"
        ),
        "refus_securise_valide": contexte.get(
            "refus_securise_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_contexte(analyse):
    """
    B1 — Évaluation du résultat de l'analyse du contexte.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(analyse, dict):
        return None

    contexte_valide = (
        analyse.get("analyse_valide") is True
        and analyse.get("contexte_valide") is True
    )

    return {
        "analyse_valide": contexte_valide,
        "contexte_valide": contexte_valide,
        "statut": analyse.get(
            "statut",
            "contexte_invalide"
        ),
        "contexte": analyse.get("contexte"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_contexte(analyse):
    """
    B1 — Résumé final de l'analyse du contexte.
    """

    evaluation = mia26_evaluer_contexte(analyse)

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get(
            "analyse_valide"
        ),
        "contexte_valide": evaluation.get(
            "contexte_valide"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "contexte": evaluation.get(
            "contexte"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 1
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 2
# COMPRÉHENSION DU CONTEXTE
# ============================================================

def mia26_analyser_comprehension_contexte(analyse_contexte=None):
    """
    B2 — Comprend et structure le contexte fourni par B1.

    Cette brique interprète uniquement les informations déjà
    analysées. Elle ne prend aucune décision et ne déclenche
    aucune action.
    """

    contexte_valide = (
        isinstance(analyse_contexte, dict)
        and analyse_contexte.get("analyse_valide") is True
        and analyse_contexte.get("contexte_valide") is True
    )

    if contexte_valide:
        statut = "comprehension_contexte_validee"
    else:
        statut = "comprehension_contexte_invalide"

    return {
        "analyse_valide": contexte_valide,
        "comprehension_valide": contexte_valide,
        "statut": statut,
        "contexte": (
            analyse_contexte.get("contexte")
            if contexte_valide else None
        ),

        # Transmission intacte des états de contrôle vers B03.
        "approbation_controlee": analyse_contexte.get(
            "approbation_controlee"
        ),
        "approbation_humaine": analyse_contexte.get(
            "approbation_humaine"
        ),
        "activation_valide": analyse_contexte.get(
            "activation_valide"
        ),
        "refus_securise_valide": analyse_contexte.get(
            "refus_securise_valide"
        ),

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_comprehension_contexte(analyse):
    """
    B2 — Évalue la compréhension du contexte.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(analyse, dict):
        return None

    comprehension_valide = (
        analyse.get("analyse_valide") is True
        and analyse.get("comprehension_valide") is True
    )

    return {
        "analyse_valide": comprehension_valide,
        "comprehension_valide": comprehension_valide,
        "statut": analyse.get(
            "statut",
            "comprehension_contexte_invalide"
        ),
        "contexte": analyse.get("contexte"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_comprehension_contexte(analyse):
    """
    B2 — Produit le résumé final de la compréhension du contexte.
    """

    evaluation = mia26_evaluer_comprehension_contexte(analyse)

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get(
            "analyse_valide"
        ),
        "comprehension_valide": evaluation.get(
            "comprehension_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 2
# ============================================================
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 3
# IDENTIFICATION DES ELEMENTS DU CONTEXTE
# ============================================================

def mia26_identifier_elements_contexte(comprehension_contexte=None):
    """
    B3 — Identifie les éléments présents dans le contexte compris par B2.

    Cette brique observe et structure uniquement les informations
    déjà comprises. Elle ne prend aucune décision et ne déclenche
    aucune action.
    """

    contexte_valide = (
        isinstance(comprehension_contexte, dict)
        and comprehension_contexte.get("analyse_valide") is True
        and comprehension_contexte.get("comprehension_valide") is True
    )

    if contexte_valide:
        contexte = comprehension_contexte.get("contexte")
        elements = list(contexte.keys()) if isinstance(contexte, dict) else []
        statut = "elements_contexte_identifies"
    else:
        contexte = None
        elements = []
        statut = "elements_contexte_invalides"

    return {
        "analyse_valide": contexte_valide,
        "comprehension_valide": contexte_valide,
        "identification_valide": contexte_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,

        # Transmission intacte des états de contrôle vers B04.
        "approbation_controlee": comprehension_contexte.get(
            "approbation_controlee"
        ),
        "approbation_humaine": comprehension_contexte.get(
            "approbation_humaine"
        ),
        "activation_valide": comprehension_contexte.get(
            "activation_valide"
        ),
        "refus_securise_valide": comprehension_contexte.get(
            "refus_securise_valide"
        ),

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_elements_contexte(identification):
    """
    B3 — Évalue l'identification des éléments du contexte.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(identification, dict):
        return None

    identification_valide = (
        identification.get("analyse_valide") is True
        and identification.get("comprehension_valide") is True
        and identification.get("identification_valide") is True
    )

    return {
        "analyse_valide": identification_valide,
        "comprehension_valide": identification_valide,
        "identification_valide": identification_valide,
        "statut": identification.get(
            "statut",
            "elements_contexte_invalides"
        ),
        "contexte": identification.get("contexte"),
        "elements": identification.get("elements", []),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_elements_contexte(identification):
    """
    B3 — Produit le résumé final des éléments identifiés.
    """

    evaluation = mia26_evaluer_elements_contexte(identification)

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "comprehension_valide": evaluation.get(
            "comprehension_valide"
        ),
        "identification_valide": evaluation.get(
            "identification_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 3
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 4
# CLASSIFICATION DU CONTEXTE
# ============================================================

def mia26_classifier_contexte(elements_contexte=None):
    """
    B4 — Classifie le contexte à partir des éléments identifiés par B3.

    Cette brique organise les éléments déjà identifiés.
    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = (
        isinstance(elements_contexte, dict)
        and elements_contexte.get("analyse_valide") is True
        and elements_contexte.get("identification_valide") is True
    )

    if contexte_valide:
        contexte = elements_contexte.get("contexte")
        elements = elements_contexte.get("elements", [])

        if isinstance(elements, list):
            nombre_elements = len(elements)
        else:
            nombre_elements = 0

        if nombre_elements == 0:
            classification = "contexte_sans_elements"
        elif nombre_elements <= 3:
            classification = "contexte_simple"
        else:
            classification = "contexte_structure"

        statut = "classification_contexte_validee"
    else:
        contexte = None
        elements = []
        nombre_elements = 0
        classification = "contexte_non_classifiable"
        statut = "classification_contexte_invalide"

    return {
        "analyse_valide": contexte_valide,
        "identification_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "nombre_elements": nombre_elements,
        "classification": classification,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_classification_contexte(classification):
    """
    B4 — Évalue la classification du contexte.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(classification, dict):
        return None

    classification_valide = (
        classification.get("analyse_valide") is True
        and classification.get("identification_valide") is True
        and classification.get("classification_valide") is True
    )

    return {
        "analyse_valide": classification_valide,
        "identification_valide": classification_valide,
        "classification_valide": classification_valide,
        "statut": classification.get(
            "statut",
            "classification_contexte_invalide"
        ),
        "contexte": classification.get("contexte"),
        "elements": classification.get("elements", []),
        "nombre_elements": classification.get("nombre_elements", 0),
        "classification": classification.get(
            "classification",
            "contexte_non_classifiable"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_classification_contexte(classification):
    """
    B4 — Produit le résumé final de la classification du contexte.
    """

    evaluation = mia26_evaluer_classification_contexte(classification)

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "identification_valide": evaluation.get(
            "identification_valide"
        ),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "nombre_elements": evaluation.get("nombre_elements", 0),
        "classification": evaluation.get("classification"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 4
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 5
# DETERMINATION DU BESOIN CONTEXTUEL
# ============================================================

def mia26_determiner_besoin_contextuel(classification_contexte=None):
    """
    B5 — Détermine le besoin contextuel à partir du contexte classifié.

    Cette brique identifie le besoin exprimé ou implicite dans
    les informations déjà structurées par B1 à B4.

    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = (
        isinstance(classification_contexte, dict)
        and classification_contexte.get("analyse_valide") is True
        and classification_contexte.get("identification_valide") is True
        and classification_contexte.get("classification_valide") is True
    )

    if contexte_valide:
        contexte = classification_contexte.get("contexte")
        elements = classification_contexte.get("elements", [])
        classification = classification_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )

        besoin = None

        if isinstance(contexte, dict):
            objectif = contexte.get("objectif")

            if isinstance(objectif, str) and objectif.strip():
                besoin = objectif.strip()

        if besoin:
            besoin_identifie = True
            statut = "besoin_contextuel_identifie"
        else:
            besoin_identifie = False
            statut = "besoin_contextuel_non_determine"
    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_identifie = False
        statut = "besoin_contextuel_invalide"

    return {
        "analyse_valide": contexte_valide,
        "identification_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": besoin_identifie,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_besoin_contextuel(besoin_contextuel):
    """
    B5 — Évalue la détermination du besoin contextuel.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(besoin_contextuel, dict):
        return None

    besoin_valide = (
        besoin_contextuel.get("analyse_valide") is True
        and besoin_contextuel.get("identification_valide") is True
        and besoin_contextuel.get("classification_valide") is True
        and besoin_contextuel.get("besoin_valide") is True
    )

    return {
        "analyse_valide": besoin_valide,
        "identification_valide": besoin_valide,
        "classification_valide": besoin_valide,
        "besoin_valide": besoin_valide,
        "statut": besoin_contextuel.get(
            "statut",
            "besoin_contextuel_invalide"
        ),
        "contexte": besoin_contextuel.get("contexte"),
        "elements": besoin_contextuel.get("elements", []),
        "classification": besoin_contextuel.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": besoin_contextuel.get("besoin"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_besoin_contextuel(besoin_contextuel):
    """
    B5 — Produit le résumé final du besoin contextuel.
    """

    evaluation = mia26_evaluer_besoin_contextuel(
        besoin_contextuel
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "identification_valide": evaluation.get(
            "identification_valide"
        ),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "besoin_valide": evaluation.get("besoin_valide"),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 5
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 6
# PRECISION DU BESOIN CONTEXTUEL
# ============================================================

def mia26_preciser_besoin_contextuel(besoin_contextuel=None):
    """
    B6 — Précise le besoin contextuel identifié par B5.

    Cette brique affine uniquement le besoin déjà identifié.
    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = (
        isinstance(besoin_contextuel, dict)
        and besoin_contextuel.get("analyse_valide") is True
        and besoin_contextuel.get("classification_valide") is True
        and besoin_contextuel.get("besoin_valide") is True
    )

    if contexte_valide:
        contexte = besoin_contextuel.get("contexte")
        elements = besoin_contextuel.get("elements", [])
        classification = besoin_contextuel.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = besoin_contextuel.get("besoin")

        if isinstance(besoin, str) and besoin.strip():
            besoin_precis = besoin.strip()
            precision_valide = True
            statut = "besoin_contextuel_precise"
        else:
            besoin_precis = None
            precision_valide = False
            statut = "besoin_contextuel_non_precisable"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        precision_valide = False
        statut = "precision_besoin_contextuel_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": precision_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_precision_besoin_contextuel(precision_besoin):
    """
    B6 — Évalue la précision du besoin contextuel.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(precision_besoin, dict):
        return None

    precision_valide = (
        precision_besoin.get("analyse_valide") is True
        and precision_besoin.get("classification_valide") is True
        and precision_besoin.get("besoin_valide") is True
        and precision_besoin.get("precision_valide") is True
    )

    return {
        "analyse_valide": precision_valide,
        "classification_valide": precision_valide,
        "besoin_valide": precision_valide,
        "precision_valide": precision_valide,
        "statut": precision_besoin.get(
            "statut",
            "precision_besoin_contextuel_invalide"
        ),
        "contexte": precision_besoin.get("contexte"),
        "elements": precision_besoin.get("elements", []),
        "classification": precision_besoin.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": precision_besoin.get("besoin"),
        "besoin_precis": precision_besoin.get("besoin_precis"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_precision_besoin_contextuel(precision_besoin):
    """
    B6 — Produit le résumé final du besoin précisé.
    """

    evaluation = mia26_evaluer_precision_besoin_contextuel(
        precision_besoin
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 6
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 7
# DETERMINATION DES CONTRAINTES DU CONTEXTE
# ============================================================

def mia26_determiner_contraintes_contexte(precision_besoin=None):
    """
    B7 — Détermine les contraintes liées au contexte et au besoin précisé.

    Cette brique identifie uniquement les contraintes explicitement
    présentes dans les informations déjà structurées par B1 à B6.
    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = (
        isinstance(precision_besoin, dict)
        and precision_besoin.get("analyse_valide") is True
        and precision_besoin.get("classification_valide") is True
        and precision_besoin.get("besoin_valide") is True
        and precision_besoin.get("precision_valide") is True
    )

    if contexte_valide:
        contexte = precision_besoin.get("contexte")
        elements = precision_besoin.get("elements", [])
        classification = precision_besoin.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = precision_besoin.get("besoin")
        besoin_precis = precision_besoin.get("besoin_precis")

        contraintes = []

        if isinstance(contexte, dict):
            for cle, valeur in contexte.items():
                if "contrainte" in str(cle).lower():
                    contraintes.append({
                        "type": str(cle),
                        "valeur": valeur
                    })

        contraintes_identifiees = len(contraintes) > 0

        if contraintes_identifiees:
            statut = "contraintes_contexte_identifiees"
        else:
            statut = "aucune_contrainte_contexte_identifiee"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        contraintes_identifiees = False
        statut = "contraintes_contexte_invalides"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "contraintes_identifiees": contraintes_identifiees,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_contraintes_contexte(contraintes_contexte):
    """
    B7 — Évalue les contraintes identifiées dans le contexte.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(contraintes_contexte, dict):
        return None

    contraintes_valide = (
        contraintes_contexte.get("analyse_valide") is True
        and contraintes_contexte.get("classification_valide") is True
        and contraintes_contexte.get("besoin_valide") is True
        and contraintes_contexte.get("precision_valide") is True
        and contraintes_contexte.get("contraintes_valide") is True
    )

    return {
        "analyse_valide": contraintes_valide,
        "classification_valide": contraintes_valide,
        "besoin_valide": contraintes_valide,
        "precision_valide": contraintes_valide,
        "contraintes_valide": contraintes_valide,
        "contraintes_identifiees": contraintes_contexte.get(
            "contraintes_identifiees",
            False
        ),
        "statut": contraintes_contexte.get(
            "statut",
            "contraintes_contexte_invalides"
        ),
        "contexte": contraintes_contexte.get("contexte"),
        "elements": contraintes_contexte.get("elements", []),
        "classification": contraintes_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": contraintes_contexte.get("besoin"),
        "besoin_precis": contraintes_contexte.get("besoin_precis"),
        "contraintes": contraintes_contexte.get("contraintes", []),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_contraintes_contexte(contraintes_contexte):
    """
    B7 — Produit le résumé final des contraintes du contexte.
    """

    evaluation = mia26_evaluer_contraintes_contexte(
        contraintes_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "contraintes_identifiees": evaluation.get(
            "contraintes_identifiees"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 7
# ============================================================


# ============================================================
# MIA V26 — BRIQUE 8
# DETERMINATION DU NIVEAU DE PRIORITE
# ============================================================

def mia26_determiner_priorite_contexte(contraintes_contexte=None):
    """
    B8 — Détermine le niveau de priorité du contexte.

    Cette brique évalue uniquement les informations déjà structurées
    par B1 à B7.
    Elle ne prend aucune décision et ne déclenche aucune action.
    """

    contexte_valide = (
        isinstance(contraintes_contexte, dict)
        and contraintes_contexte.get("analyse_valide") is True
        and contraintes_contexte.get("classification_valide") is True
        and contraintes_contexte.get("besoin_valide") is True
        and contraintes_contexte.get("precision_valide") is True
        and contraintes_contexte.get("contraintes_valide") is True
    )

    if contexte_valide:
        contexte = contraintes_contexte.get("contexte")
        elements = contraintes_contexte.get("elements", [])
        classification = contraintes_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = contraintes_contexte.get("besoin")
        besoin_precis = contraintes_contexte.get("besoin_precis")
        contraintes = contraintes_contexte.get("contraintes", [])

        # ----------------------------------------------------
        # Détermination prudente de la priorité.
        # La priorité est basée uniquement sur les données
        # explicitement disponibles.
        # ----------------------------------------------------

        priorite = "normale"

        if isinstance(contexte, dict):
            valeur_priorite = contexte.get("priorite")

            if isinstance(valeur_priorite, str):
                valeur = valeur_priorite.strip().lower()

                if valeur in {"critique", "urgente", "haute"}:
                    priorite = valeur
                elif valeur in {"moyenne", "normale", "basse"}:
                    priorite = valeur

        priorite_valide = True
        statut = "priorite_contexte_determinee"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        priorite = "priorite_non_determinable"
        priorite_valide = False
        statut = "priorite_contexte_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "priorite_valide": priorite_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_priorite_contexte(priorite_contexte):
    """
    B8 — Évalue la détermination du niveau de priorité.

    Cette fonction évalue uniquement.
    Elle n'exécute aucune action.
    """

    if not isinstance(priorite_contexte, dict):
        return None

    priorite_valide = (
        priorite_contexte.get("analyse_valide") is True
        and priorite_contexte.get("classification_valide") is True
        and priorite_contexte.get("besoin_valide") is True
        and priorite_contexte.get("precision_valide") is True
        and priorite_contexte.get("contraintes_valide") is True
        and priorite_contexte.get("priorite_valide") is True
    )

    return {
        "analyse_valide": priorite_valide,
        "classification_valide": priorite_valide,
        "besoin_valide": priorite_valide,
        "precision_valide": priorite_valide,
        "contraintes_valide": priorite_valide,
        "priorite_valide": priorite_valide,
        "statut": priorite_contexte.get(
            "statut",
            "priorite_contexte_invalide"
        ),
        "contexte": priorite_contexte.get("contexte"),
        "elements": priorite_contexte.get("elements", []),
        "classification": priorite_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": priorite_contexte.get("besoin"),
        "besoin_precis": priorite_contexte.get("besoin_precis"),
        "contraintes": priorite_contexte.get("contraintes", []),
        "priorite": priorite_contexte.get(
            "priorite",
            "priorite_non_determinable"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_priorite_contexte(priorite_contexte):
    """
    B8 — Produit le résumé final du niveau de priorité.
    """

    evaluation = mia26_evaluer_priorite_contexte(
        priorite_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "priorite_valide": evaluation.get("priorite_valide"),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),
        "priorite": evaluation.get("priorite"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 8
# ============================================================


# ============================================================
# MIA V26 — BRIQUE 9
# DETERMINATION DU TYPE DE REPONSE NECESSAIRE
# ============================================================

def mia26_determiner_type_reponse(priorite_contexte=None):
    """
    B9 — Détermine le type de réponse nécessaire.

    Cette brique analyse uniquement les informations déjà
    structurées par B1 à B8.
    Elle identifie le type de réponse approprié sans
    générer la réponse et sans déclencher aucune action.
    """

    contexte_valide = (
        isinstance(priorite_contexte, dict)
        and priorite_contexte.get("analyse_valide") is True
        and priorite_contexte.get("classification_valide") is True
        and priorite_contexte.get("besoin_valide") is True
        and priorite_contexte.get("precision_valide") is True
        and priorite_contexte.get("contraintes_valide") is True
        and priorite_contexte.get("priorite_valide") is True
    )

    if contexte_valide:
        contexte = priorite_contexte.get("contexte")
        elements = priorite_contexte.get("elements", [])
        classification = priorite_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = priorite_contexte.get("besoin")
        besoin_precis = priorite_contexte.get("besoin_precis")
        contraintes = priorite_contexte.get("contraintes", [])
        priorite = priorite_contexte.get(
            "priorite",
            "priorite_non_determinable"
        )

        type_reponse = "information"

        if isinstance(contexte, dict):
            valeur_type = contexte.get("type_reponse")

            if isinstance(valeur_type, str):
                valeur = valeur_type.strip().lower()

                types_valides = {
                    "information",
                    "explication",
                    "conseil",
                    "analyse",
                    "orientation",
                    "clarification"
                }

                if valeur in types_valides:
                    type_reponse = valeur

        type_reponse_valide = True
        statut = "type_reponse_determine"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        priorite = "priorite_non_determinable"
        type_reponse = "type_reponse_non_determinable"
        type_reponse_valide = False
        statut = "type_reponse_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "priorite_valide": contexte_valide,
        "type_reponse_valide": type_reponse_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,
        "type_reponse": type_reponse,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_type_reponse(type_reponse_contexte):
    """
    B9 — Évalue le type de réponse déterminé.

    Cette fonction évalue uniquement.
    Elle ne génère aucune réponse et n'exécute aucune action.
    """

    if not isinstance(type_reponse_contexte, dict):
        return None

    type_reponse_valide = (
        type_reponse_contexte.get("analyse_valide") is True
        and type_reponse_contexte.get("classification_valide") is True
        and type_reponse_contexte.get("besoin_valide") is True
        and type_reponse_contexte.get("precision_valide") is True
        and type_reponse_contexte.get("contraintes_valide") is True
        and type_reponse_contexte.get("priorite_valide") is True
        and type_reponse_contexte.get("type_reponse_valide") is True
    )

    return {
        "analyse_valide": type_reponse_valide,
        "classification_valide": type_reponse_valide,
        "besoin_valide": type_reponse_valide,
        "precision_valide": type_reponse_valide,
        "contraintes_valide": type_reponse_valide,
        "priorite_valide": type_reponse_valide,
        "type_reponse_valide": type_reponse_valide,
        "statut": type_reponse_contexte.get(
            "statut",
            "type_reponse_invalide"
        ),
        "contexte": type_reponse_contexte.get("contexte"),
        "elements": type_reponse_contexte.get("elements", []),
        "classification": type_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": type_reponse_contexte.get("besoin"),
        "besoin_precis": type_reponse_contexte.get("besoin_precis"),
        "contraintes": type_reponse_contexte.get("contraintes", []),
        "priorite": type_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        ),
        "type_reponse": type_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_type_reponse(type_reponse_contexte):
    """
    B9 — Produit le résumé final du type de réponse nécessaire.
    """

    evaluation = mia26_evaluer_type_reponse(
        type_reponse_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get(
            "classification_valide"
        ),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "priorite_valide": evaluation.get("priorite_valide"),
        "type_reponse_valide": evaluation.get(
            "type_reponse_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),
        "priorite": evaluation.get("priorite"),
        "type_reponse": evaluation.get("type_reponse"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 9
# ============================================================


# ============================================================
# MIA V26 — BRIQUE 10
# DETERMINATION DE LA STRUCTURE DE REPONSE
# ============================================================

def mia26_determiner_structure_reponse(type_reponse_contexte=None):
    """
    B10 — Détermine la structure nécessaire de la réponse.

    Cette brique analyse uniquement les informations déjà
    structurées par B1 à B9.
    Elle détermine une structure de réponse adaptée sans
    générer la réponse et sans déclencher aucune action.
    """

    contexte_valide = (
        isinstance(type_reponse_contexte, dict)
        and type_reponse_contexte.get("analyse_valide") is True
        and type_reponse_contexte.get("classification_valide") is True
        and type_reponse_contexte.get("besoin_valide") is True
        and type_reponse_contexte.get("precision_valide") is True
        and type_reponse_contexte.get("contraintes_valide") is True
        and type_reponse_contexte.get("priorite_valide") is True
        and type_reponse_contexte.get("type_reponse_valide") is True
    )

    if contexte_valide:
        contexte = type_reponse_contexte.get("contexte")
        elements = type_reponse_contexte.get("elements", [])
        classification = type_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = type_reponse_contexte.get("besoin")
        besoin_precis = type_reponse_contexte.get("besoin_precis")
        contraintes = type_reponse_contexte.get("contraintes", [])
        priorite = type_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        )
        type_reponse = type_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        )

        structure_reponse = "reponse_directe"

        if type_reponse == "explication":
            structure_reponse = "introduction_explication_conclusion"
        elif type_reponse == "conseil":
            structure_reponse = "situation_recommandations_conclusion"
        elif type_reponse == "analyse":
            structure_reponse = "contexte_analyse_conclusion"
        elif type_reponse == "orientation":
            structure_reponse = "situation_options_orientation"
        elif type_reponse == "clarification":
            structure_reponse = "clarification_question_reponse"
        elif type_reponse == "information":
            structure_reponse = "information_directe"

        structure_reponse_valide = True
        statut = "structure_reponse_determinee"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        priorite = "priorite_non_determinable"
        type_reponse = "type_reponse_non_determinable"
        structure_reponse = "structure_reponse_non_determinable"
        structure_reponse_valide = False
        statut = "structure_reponse_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "priorite_valide": contexte_valide,
        "type_reponse_valide": contexte_valide,
        "structure_reponse_valide": structure_reponse_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,
        "type_reponse": type_reponse,
        "structure_reponse": structure_reponse,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_structure_reponse(structure_reponse_contexte):
    """
    B10 — Évalue la structure de réponse déterminée.

    Cette fonction évalue uniquement.
    Elle ne génère aucune réponse et n'exécute aucune action.
    """

    if not isinstance(structure_reponse_contexte, dict):
        return None

    structure_reponse_valide = (
        structure_reponse_contexte.get("analyse_valide") is True
        and structure_reponse_contexte.get("classification_valide") is True
        and structure_reponse_contexte.get("besoin_valide") is True
        and structure_reponse_contexte.get("precision_valide") is True
        and structure_reponse_contexte.get("contraintes_valide") is True
        and structure_reponse_contexte.get("priorite_valide") is True
        and structure_reponse_contexte.get("type_reponse_valide") is True
        and structure_reponse_contexte.get("structure_reponse_valide") is True
    )

    return {
        "analyse_valide": structure_reponse_valide,
        "classification_valide": structure_reponse_valide,
        "besoin_valide": structure_reponse_valide,
        "precision_valide": structure_reponse_valide,
        "contraintes_valide": structure_reponse_valide,
        "priorite_valide": structure_reponse_valide,
        "type_reponse_valide": structure_reponse_valide,
        "structure_reponse_valide": structure_reponse_valide,
        "statut": structure_reponse_contexte.get(
            "statut",
            "structure_reponse_invalide"
        ),
        "contexte": structure_reponse_contexte.get("contexte"),
        "elements": structure_reponse_contexte.get("elements", []),
        "classification": structure_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": structure_reponse_contexte.get("besoin"),
        "besoin_precis": structure_reponse_contexte.get("besoin_precis"),
        "contraintes": structure_reponse_contexte.get("contraintes", []),
        "priorite": structure_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        ),
        "type_reponse": structure_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        ),
        "structure_reponse": structure_reponse_contexte.get(
            "structure_reponse",
            "structure_reponse_non_determinable"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_structure_reponse(structure_reponse_contexte):
    """
    B10 — Produit le résumé final de la structure de réponse.
    """

    evaluation = mia26_evaluer_structure_reponse(
        structure_reponse_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get("classification_valide"),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "priorite_valide": evaluation.get("priorite_valide"),
        "type_reponse_valide": evaluation.get("type_reponse_valide"),
        "structure_reponse_valide": evaluation.get(
            "structure_reponse_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),
        "priorite": evaluation.get("priorite"),
        "type_reponse": evaluation.get("type_reponse"),
        "structure_reponse": evaluation.get("structure_reponse"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 10
# ============================================================


# ============================================================

# ============================================================


# ============================================================
# MIA V26 — BRIQUE 11
# DETERMINATION DU CONTENU DE REPONSE
# ============================================================

def mia26_determiner_contenu_reponse(structure_reponse_contexte=None):
    """
    B11 — Détermine les éléments de contenu nécessaires à la réponse.

    Cette brique utilise uniquement les informations structurées
    par B1 à B10.
    Elle détermine le contenu nécessaire sans générer la réponse
    et sans déclencher aucune action.
    """

    contexte_valide = (
        isinstance(structure_reponse_contexte, dict)
        and structure_reponse_contexte.get("analyse_valide") is True
        and structure_reponse_contexte.get("classification_valide") is True
        and structure_reponse_contexte.get("besoin_valide") is True
        and structure_reponse_contexte.get("precision_valide") is True
        and structure_reponse_contexte.get("contraintes_valide") is True
        and structure_reponse_contexte.get("priorite_valide") is True
        and structure_reponse_contexte.get("type_reponse_valide") is True
        and structure_reponse_contexte.get("structure_reponse_valide") is True
    )

    if contexte_valide:
        contexte = structure_reponse_contexte.get("contexte")
        elements = structure_reponse_contexte.get("elements", [])
        classification = structure_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = structure_reponse_contexte.get("besoin")
        besoin_precis = structure_reponse_contexte.get("besoin_precis")
        contraintes = structure_reponse_contexte.get("contraintes", [])
        priorite = structure_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        )
        type_reponse = structure_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        )
        structure_reponse = structure_reponse_contexte.get(
            "structure_reponse",
            "structure_reponse_non_determinable"
        )

        contenu_reponse = []

        if isinstance(besoin_precis, str) and besoin_precis.strip():
            contenu_reponse.append("reponse_au_besoin")

        if type_reponse == "explication":
            contenu_reponse.append("explication_claire")
        elif type_reponse == "conseil":
            contenu_reponse.append("recommandations")
        elif type_reponse == "analyse":
            contenu_reponse.append("elements_analyse")
        elif type_reponse == "orientation":
            contenu_reponse.append("options_orientation")
        elif type_reponse == "clarification":
            contenu_reponse.append("question_clarification")
        elif type_reponse == "information":
            contenu_reponse.append("informations_essentielles")

        if structure_reponse == "introduction_explication_conclusion":
            contenu_reponse.extend([
                "introduction",
                "explication",
                "conclusion"
            ])
        elif structure_reponse == "situation_recommandations_conclusion":
            contenu_reponse.extend([
                "situation",
                "recommandations",
                "conclusion"
            ])
        elif structure_reponse == "contexte_analyse_conclusion":
            contenu_reponse.extend([
                "contexte",
                "analyse",
                "conclusion"
            ])
        elif structure_reponse == "situation_options_orientation":
            contenu_reponse.extend([
                "situation",
                "options",
                "orientation"
            ])
        elif structure_reponse == "clarification_question_reponse":
            contenu_reponse.extend([
                "clarification",
                "question",
                "reponse"
            ])
        elif structure_reponse == "information_directe":
            contenu_reponse.append("information_directe")
        elif structure_reponse == "reponse_directe":
            contenu_reponse.append("reponse_directe")

        # Suppression prudente des doublons en conservant l'ordre.
        contenu_reponse = list(dict.fromkeys(contenu_reponse))

        contenu_reponse_valide = len(contenu_reponse) > 0

        statut = (
            "contenu_reponse_determine"
            if contenu_reponse_valide
            else "contenu_reponse_non_determine"
        )

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        priorite = "priorite_non_determinable"
        type_reponse = "type_reponse_non_determinable"
        structure_reponse = "structure_reponse_non_determinable"
        contenu_reponse = []
        contenu_reponse_valide = False
        statut = "contenu_reponse_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "priorite_valide": contexte_valide,
        "type_reponse_valide": contexte_valide,
        "structure_reponse_valide": contexte_valide,
        "contenu_reponse_valide": contenu_reponse_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,
        "type_reponse": type_reponse,
        "structure_reponse": structure_reponse,
        "contenu_reponse": contenu_reponse,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_contenu_reponse(contenu_reponse_contexte):
    """
    B11 — Évalue le contenu de réponse déterminé.

    Cette fonction évalue uniquement.
    Elle ne génère aucune réponse et n'exécute aucune action.
    """

    if not isinstance(contenu_reponse_contexte, dict):
        return None

    contenu_reponse_valide = (
        contenu_reponse_contexte.get("analyse_valide") is True
        and contenu_reponse_contexte.get("classification_valide") is True
        and contenu_reponse_contexte.get("besoin_valide") is True
        and contenu_reponse_contexte.get("precision_valide") is True
        and contenu_reponse_contexte.get("contraintes_valide") is True
        and contenu_reponse_contexte.get("priorite_valide") is True
        and contenu_reponse_contexte.get("type_reponse_valide") is True
        and contenu_reponse_contexte.get("structure_reponse_valide") is True
        and contenu_reponse_contexte.get("contenu_reponse_valide") is True
        and isinstance(
            contenu_reponse_contexte.get("contenu_reponse"),
            list
        )
        and len(contenu_reponse_contexte.get("contenu_reponse", [])) > 0
    )

    return {
        "analyse_valide": contenu_reponse_valide,
        "classification_valide": contenu_reponse_valide,
        "besoin_valide": contenu_reponse_valide,
        "precision_valide": contenu_reponse_valide,
        "contraintes_valide": contenu_reponse_valide,
        "priorite_valide": contenu_reponse_valide,
        "type_reponse_valide": contenu_reponse_valide,
        "structure_reponse_valide": contenu_reponse_valide,
        "contenu_reponse_valide": contenu_reponse_valide,
        "statut": contenu_reponse_contexte.get(
            "statut",
            "contenu_reponse_invalide"
        ),
        "contexte": contenu_reponse_contexte.get("contexte"),
        "elements": contenu_reponse_contexte.get("elements", []),
        "classification": contenu_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": contenu_reponse_contexte.get("besoin"),
        "besoin_precis": contenu_reponse_contexte.get("besoin_precis"),
        "contraintes": contenu_reponse_contexte.get("contraintes", []),
        "priorite": contenu_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        ),
        "type_reponse": contenu_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        ),
        "structure_reponse": contenu_reponse_contexte.get(
            "structure_reponse",
            "structure_reponse_non_determinable"
        ),
        "contenu_reponse": contenu_reponse_contexte.get(
            "contenu_reponse",
            []
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_contenu_reponse(contenu_reponse_contexte):
    """
    B11 — Produit le résumé final du contenu de réponse.
    """

    evaluation = mia26_evaluer_contenu_reponse(
        contenu_reponse_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get("classification_valide"),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "priorite_valide": evaluation.get("priorite_valide"),
        "type_reponse_valide": evaluation.get("type_reponse_valide"),
        "structure_reponse_valide": evaluation.get(
            "structure_reponse_valide"
        ),
        "contenu_reponse_valide": evaluation.get(
            "contenu_reponse_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),
        "priorite": evaluation.get("priorite"),
        "type_reponse": evaluation.get("type_reponse"),
        "structure_reponse": evaluation.get("structure_reponse"),
        "contenu_reponse": evaluation.get("contenu_reponse", []),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 11
# ============================================================


# ============================================================
# MIA V26 — BRIQUE 12
# DETERMINATION DE LA FORME DE REPONSE
# ============================================================

def mia26_determiner_forme_reponse(contenu_reponse_contexte=None):
    """
    B12 — Détermine la forme de présentation nécessaire de la réponse.

    Cette brique utilise uniquement les informations structurées
    par B1 à B11.
    Elle détermine la forme de présentation sans générer la réponse
    et sans déclencher aucune action.
    """

    contexte_valide = (
        isinstance(contenu_reponse_contexte, dict)
        and contenu_reponse_contexte.get("analyse_valide") is True
        and contenu_reponse_contexte.get("classification_valide") is True
        and contenu_reponse_contexte.get("besoin_valide") is True
        and contenu_reponse_contexte.get("precision_valide") is True
        and contenu_reponse_contexte.get("contraintes_valide") is True
        and contenu_reponse_contexte.get("priorite_valide") is True
        and contenu_reponse_contexte.get("type_reponse_valide") is True
        and contenu_reponse_contexte.get("structure_reponse_valide") is True
        and contenu_reponse_contexte.get("contenu_reponse_valide") is True
        and isinstance(
            contenu_reponse_contexte.get("contenu_reponse"),
            list
        )
        and len(contenu_reponse_contexte.get("contenu_reponse", [])) > 0
    )

    if contexte_valide:
        contexte = contenu_reponse_contexte.get("contexte")
        elements = contenu_reponse_contexte.get("elements", [])
        classification = contenu_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        )
        besoin = contenu_reponse_contexte.get("besoin")
        besoin_precis = contenu_reponse_contexte.get("besoin_precis")
        contraintes = contenu_reponse_contexte.get("contraintes", [])
        priorite = contenu_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        )
        type_reponse = contenu_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        )
        structure_reponse = contenu_reponse_contexte.get(
            "structure_reponse",
            "structure_reponse_non_determinable"
        )
        contenu_reponse = contenu_reponse_contexte.get(
            "contenu_reponse",
            []
        )

        forme_reponse = "texte_structure"

        if type_reponse == "explication":
            forme_reponse = "texte_clair_structure"
        elif type_reponse == "conseil":
            forme_reponse = "liste_recommandations"
        elif type_reponse == "analyse":
            forme_reponse = "analyse_structuree"
        elif type_reponse == "orientation":
            forme_reponse = "options_structurees"
        elif type_reponse == "clarification":
            forme_reponse = "question_courte"
        elif type_reponse == "information":
            forme_reponse = "information_directe"

        forme_reponse_valide = True
        statut = "forme_reponse_determinee"

    else:
        contexte = None
        elements = []
        classification = "contexte_non_classifiable"
        besoin = None
        besoin_precis = None
        contraintes = []
        priorite = "priorite_non_determinable"
        type_reponse = "type_reponse_non_determinable"
        structure_reponse = "structure_reponse_non_determinable"
        contenu_reponse = []
        forme_reponse = "forme_reponse_non_determinable"
        forme_reponse_valide = False
        statut = "forme_reponse_invalide"

    return {
        "analyse_valide": contexte_valide,
        "classification_valide": contexte_valide,
        "besoin_valide": contexte_valide,
        "precision_valide": contexte_valide,
        "contraintes_valide": contexte_valide,
        "priorite_valide": contexte_valide,
        "type_reponse_valide": contexte_valide,
        "structure_reponse_valide": contexte_valide,
        "contenu_reponse_valide": contexte_valide,
        "forme_reponse_valide": forme_reponse_valide,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,
        "type_reponse": type_reponse,
        "structure_reponse": structure_reponse,
        "contenu_reponse": contenu_reponse,
        "forme_reponse": forme_reponse,

        # Sécurité : aucune exécution automatique.
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_forme_reponse(forme_reponse_contexte):
    """
    B12 — Évalue la forme de réponse déterminée.

    Cette fonction évalue uniquement.
    Elle ne génère aucune réponse et n'exécute aucune action.
    """

    if not isinstance(forme_reponse_contexte, dict):
        return None

    forme_reponse_valide = (
        forme_reponse_contexte.get("analyse_valide") is True
        and forme_reponse_contexte.get("classification_valide") is True
        and forme_reponse_contexte.get("besoin_valide") is True
        and forme_reponse_contexte.get("precision_valide") is True
        and forme_reponse_contexte.get("contraintes_valide") is True
        and forme_reponse_contexte.get("priorite_valide") is True
        and forme_reponse_contexte.get("type_reponse_valide") is True
        and forme_reponse_contexte.get("structure_reponse_valide") is True
        and forme_reponse_contexte.get("contenu_reponse_valide") is True
        and forme_reponse_contexte.get("forme_reponse_valide") is True
        and isinstance(
            forme_reponse_contexte.get("forme_reponse"),
            str
        )
        and bool(
            forme_reponse_contexte.get("forme_reponse", "").strip()
        )
    )

    return {
        "analyse_valide": forme_reponse_valide,
        "classification_valide": forme_reponse_valide,
        "besoin_valide": forme_reponse_valide,
        "precision_valide": forme_reponse_valide,
        "contraintes_valide": forme_reponse_valide,
        "priorite_valide": forme_reponse_valide,
        "type_reponse_valide": forme_reponse_valide,
        "structure_reponse_valide": forme_reponse_valide,
        "contenu_reponse_valide": forme_reponse_valide,
        "forme_reponse_valide": forme_reponse_valide,
        "statut": forme_reponse_contexte.get(
            "statut",
            "forme_reponse_invalide"
        ),
        "contexte": forme_reponse_contexte.get("contexte"),
        "elements": forme_reponse_contexte.get("elements", []),
        "classification": forme_reponse_contexte.get(
            "classification",
            "contexte_non_classifiable"
        ),
        "besoin": forme_reponse_contexte.get("besoin"),
        "besoin_precis": forme_reponse_contexte.get("besoin_precis"),
        "contraintes": forme_reponse_contexte.get("contraintes", []),
        "priorite": forme_reponse_contexte.get(
            "priorite",
            "priorite_non_determinable"
        ),
        "type_reponse": forme_reponse_contexte.get(
            "type_reponse",
            "type_reponse_non_determinable"
        ),
        "structure_reponse": forme_reponse_contexte.get(
            "structure_reponse",
            "structure_reponse_non_determinable"
        ),
        "contenu_reponse": forme_reponse_contexte.get(
            "contenu_reponse",
            []
        ),
        "forme_reponse": forme_reponse_contexte.get(
            "forme_reponse",
            "forme_reponse_non_determinable"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_forme_reponse(forme_reponse_contexte):
    """
    B12 — Produit le résumé final de la forme de réponse.
    """

    evaluation = mia26_evaluer_forme_reponse(
        forme_reponse_contexte
    )

    if evaluation is None:
        return None

    return {
        "analyse_valide": evaluation.get("analyse_valide"),
        "classification_valide": evaluation.get("classification_valide"),
        "besoin_valide": evaluation.get("besoin_valide"),
        "precision_valide": evaluation.get("precision_valide"),
        "contraintes_valide": evaluation.get("contraintes_valide"),
        "priorite_valide": evaluation.get("priorite_valide"),
        "type_reponse_valide": evaluation.get("type_reponse_valide"),
        "structure_reponse_valide": evaluation.get(
            "structure_reponse_valide"
        ),
        "contenu_reponse_valide": evaluation.get(
            "contenu_reponse_valide"
        ),
        "forme_reponse_valide": evaluation.get(
            "forme_reponse_valide"
        ),
        "statut": evaluation.get("statut"),
        "contexte": evaluation.get("contexte"),
        "elements": evaluation.get("elements", []),
        "classification": evaluation.get("classification"),
        "besoin": evaluation.get("besoin"),
        "besoin_precis": evaluation.get("besoin_precis"),
        "contraintes": evaluation.get("contraintes", []),
        "priorite": evaluation.get("priorite"),
        "type_reponse": evaluation.get("type_reponse"),
        "structure_reponse": evaluation.get("structure_reponse"),
        "contenu_reponse": evaluation.get("contenu_reponse", []),
        "forme_reponse": evaluation.get(
            "forme_reponse",
            "forme_reponse_non_determinable"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 12

# ============================================================
# MIA V26 — BRIQUE 13
# CONTROLE FINAL DE COHERENCE DE LA REPONSE
# ============================================================

def mia26_controler_coherence_finale(forme_reponse_contexte=None):
    """
    B13 — Contrôle final de cohérence de la chaîne de réponse.

    Cette brique :
    - vérifie la validité des informations B1 à B12 ;
    - vérifie la présence des éléments nécessaires ;
    - contrôle la cohérence entre type, structure, contenu et forme ;
    - ne génère aucune réponse ;
    - ne prend aucune décision ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(forme_reponse_contexte, dict):
        return {
            "coherence_finale_valide": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    validations_requises = [
        "analyse_valide",
        "classification_valide",
        "besoin_valide",
        "precision_valide",
        "contraintes_valide",
        "priorite_valide",
        "type_reponse_valide",
        "structure_reponse_valide",
        "contenu_reponse_valide",
        "forme_reponse_valide"
    ]

    validations_ok = all(
        forme_reponse_contexte.get(cle) is True
        for cle in validations_requises
    )

    type_reponse = forme_reponse_contexte.get("type_reponse")
    structure_reponse = forme_reponse_contexte.get("structure_reponse")
    contenu_reponse = forme_reponse_contexte.get("contenu_reponse")
    forme_reponse = forme_reponse_contexte.get("forme_reponse")

    type_valide = (
        isinstance(type_reponse, str)
        and bool(type_reponse.strip())
        and type_reponse != "type_reponse_non_determinable"
    )

    structure_valide = (
        isinstance(structure_reponse, str)
        and bool(structure_reponse.strip())
        and structure_reponse != "structure_reponse_non_determinable"
    )

    contenu_valide = (
        isinstance(contenu_reponse, list)
        and len(contenu_reponse) > 0
    )

    forme_valide = (
        isinstance(forme_reponse, str)
        and bool(forme_reponse.strip())
        and forme_reponse != "forme_reponse_non_determinable"
    )

    coherence_finale_valide = (
        validations_ok
        and type_valide
        and structure_valide
        and contenu_valide
        and forme_valide
    )

    if coherence_finale_valide:
        statut = "coherence_finale_validee"
    else:
        statut = "coherence_finale_invalide"

    return {
        "coherence_finale_valide": coherence_finale_valide,
        "validations_b1_b12": validations_ok,
        "type_reponse_valide": type_valide,
        "structure_reponse_valide": structure_valide,
        "contenu_reponse_valide": contenu_valide,
        "forme_reponse_valide": forme_valide,
        "statut": statut,
        "type_reponse": type_reponse,
        "structure_reponse": structure_reponse,
        "contenu_reponse": contenu_reponse,
        "forme_reponse": forme_reponse,

        # Transmission des états de contrôle vers B14/B15.
        # B13 ne modifie pas ces états.
        "approbation_controlee": forme_reponse_contexte.get(
            "approbation_controlee"
        ),
        "approbation_humaine": forme_reponse_contexte.get(
            "approbation_humaine"
        ),
        "activation_valide": forme_reponse_contexte.get(
            "activation_valide"
        ),
        "refus_securise_valide": forme_reponse_contexte.get(
            "refus_securise_valide"
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_coherence_finale(coherence_contexte):
    """
    B13 — Évalue uniquement le contrôle final.
    """

    if not isinstance(coherence_contexte, dict):
        return None

    coherence_valide = (
        coherence_contexte.get("coherence_finale_valide") is True
        and coherence_contexte.get("validations_b1_b12") is True
        and coherence_contexte.get("type_reponse_valide") is True
        and coherence_contexte.get("structure_reponse_valide") is True
        and coherence_contexte.get("contenu_reponse_valide") is True
        and coherence_contexte.get("forme_reponse_valide") is True
    )

    return {
        "coherence_finale_valide": coherence_valide,
        "statut": (
            "coherence_finale_validee"
            if coherence_valide
            else "coherence_finale_invalide"
        ),
        "type_reponse": coherence_contexte.get("type_reponse"),
        "structure_reponse": coherence_contexte.get("structure_reponse"),
        "forme_reponse": coherence_contexte.get("forme_reponse"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_coherence_finale(coherence_contexte):
    """
    B13 — Produit le résumé final du contrôle de cohérence.
    """

    evaluation = mia26_evaluer_coherence_finale(
        coherence_contexte
    )

    if evaluation is None:
        return None

    return {
        "coherence_finale_valide": evaluation.get(
            "coherence_finale_valide"
        ),
        "statut": evaluation.get("statut"),
        "type_reponse": evaluation.get("type_reponse"),
        "structure_reponse": evaluation.get(
            "structure_reponse"
        ),
        "forme_reponse": evaluation.get(
            "forme_reponse"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 13
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 14
# JOURNALISATION DU CYCLE B1 → B13
# ============================================================

def mia26_journaliser_cycle_final(forme_reponse_contexte=None):
    """
    B14 — Journalise l'état final du cycle de réponse B1 → B13.

    Cette fonction :
    - vérifie la présence du contrôle B13 ;
    - conserve les informations essentielles du cycle ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(forme_reponse_contexte, dict):
        return {
            "journalisation_valide": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    coherence_finale = (
        forme_reponse_contexte.get(
            "coherence_finale_valide"
        ) is True
    )

    validations_b1_b12 = (
        forme_reponse_contexte.get(
            "validations_b1_b12"
        ) is True
    )

    type_reponse = forme_reponse_contexte.get(
        "type_reponse"
    )

    structure_reponse = forme_reponse_contexte.get(
        "structure_reponse"
    )

    forme_reponse = forme_reponse_contexte.get(
        "forme_reponse"
    )

    journalisation_valide = (
        coherence_finale
        and validations_b1_b12
        and isinstance(type_reponse, str)
        and bool(type_reponse.strip())
        and isinstance(structure_reponse, str)
        and bool(structure_reponse.strip())
        and isinstance(forme_reponse, str)
        and bool(forme_reponse.strip())
    )

    if journalisation_valide:
        statut = "cycle_final_journalise"
    else:
        statut = "journalisation_invalide"

    return {
        "journalisation_valide": journalisation_valide,
        "coherence_finale_valide": coherence_finale,
        "validations_b1_b12": validations_b1_b12,
        "type_reponse": type_reponse,
        "structure_reponse": structure_reponse,
        "forme_reponse": forme_reponse,

        # Transmission intacte des états de contrôle vers B15.
        "approbation_controlee": forme_reponse_contexte.get(
            "approbation_controlee"
        ),
        "approbation_humaine": forme_reponse_contexte.get(
            "approbation_humaine"
        ),
        "activation_valide": forme_reponse_contexte.get(
            "activation_valide"
        ),
        "refus_securise_valide": forme_reponse_contexte.get(
            "refus_securise_valide"
        ),

        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_journal_cycle_final(journal_contexte):
    """
    B14 — Évalue uniquement la journalisation du cycle final.
    """

    if not isinstance(journal_contexte, dict):
        return None

    journalisation_valide = (
        journal_contexte.get(
            "journalisation_valide"
        ) is True
        and journal_contexte.get(
            "coherence_finale_valide"
        ) is True
        and journal_contexte.get(
            "validations_b1_b12"
        ) is True
    )

    return {
        "journalisation_valide": journalisation_valide,
        "statut": (
            "cycle_final_journalise"
            if journalisation_valide
            else "journalisation_invalide"
        ),
        "type_reponse": journal_contexte.get(
            "type_reponse"
        ),
        "structure_reponse": journal_contexte.get(
            "structure_reponse"
        ),
        "forme_reponse": journal_contexte.get(
            "forme_reponse"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_journal_cycle_final(journal_contexte):
    """
    B14 — Produit le résumé du journal du cycle final.
    """

    evaluation = mia26_evaluer_journal_cycle_final(
        journal_contexte
    )

    if evaluation is None:
        return None

    return {
        "journalisation_valide": evaluation.get(
            "journalisation_valide"
        ),
        "statut": evaluation.get("statut"),
        "type_reponse": evaluation.get(
            "type_reponse"
        ),
        "structure_reponse": evaluation.get(
            "structure_reponse"
        ),
        "forme_reponse": evaluation.get(
            "forme_reponse"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 14
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 15
# APPROBATION HUMAINE ET ETAT D'ACTIVATION
# ============================================================

def mia26_controler_approbation_humaine(journal_contexte=None):
    """
    B15 — Contrôle l'état d'approbation humaine du cycle final.

    Cette fonction :
    - vérifie la validité de B14 ;
    - vérifie la cohérence finale ;
    - ne prend aucune décision à la place de l'humain ;
    - ne modifie aucune donnée source ;
    - ne déclenche aucune action ;
    - ne donne aucune autorisation d'exécution automatique.
    """

    if not isinstance(journal_contexte, dict):
        return {
            "approbation_controlee": False,
            "approbation_humaine_requise": True,
            "activation_valide": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    journalisation_valide = (
        journal_contexte.get(
            "journalisation_valide"
        ) is True
    )

    coherence_finale_valide = (
        journal_contexte.get(
            "coherence_finale_valide"
        ) is True
    )

    validations_b1_b12 = (
        journal_contexte.get(
            "validations_b1_b12"
        ) is True
    )

    approbation_humaine = journal_contexte.get(
        "approbation_humaine"
    )

    approbation_valide = (
        approbation_humaine is True
    )

    approbation_controlee = (
        journalisation_valide
        and coherence_finale_valide
        and validations_b1_b12
    )

    activation_valide = (
        approbation_controlee
        and approbation_valide
    )

    if not approbation_controlee:
        statut = "approbation_non_possible"

    elif not approbation_valide:
        statut = "validation_humaine_requise"

    else:
        statut = "activation_humaine_validee"

    return {
        "approbation_controlee": approbation_controlee,
        "approbation_humaine_requise": not approbation_valide,
        "approbation_humaine": approbation_humaine,
        "journalisation_valide": journalisation_valide,
        "coherence_finale_valide": coherence_finale_valide,
        "validations_b1_b12": validations_b1_b12,
        "activation_valide": activation_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_approbation_humaine(approbation_contexte):
    """
    B15 — Évalue uniquement le contrôle d'approbation humaine.
    """

    if not isinstance(approbation_contexte, dict):
        return None

    approbation_valide = (
        approbation_contexte.get(
            "approbation_controlee"
        ) is True
        and approbation_contexte.get(
            "approbation_humaine"
        ) is True
        and approbation_contexte.get(
            "activation_valide"
        ) is True
    )

    return {
        "approbation_valide": approbation_valide,
        "activation_valide": approbation_valide,
        "statut": (
            "activation_humaine_validee"
            if approbation_valide
            else "validation_humaine_requise"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_approbation_humaine(approbation_contexte):
    """
    B15 — Produit le résumé du contrôle d'approbation humaine.
    """

    evaluation = mia26_evaluer_approbation_humaine(
        approbation_contexte
    )

    if evaluation is None:
        return None

    return {
        "approbation_valide": evaluation.get(
            "approbation_valide"
        ),
        "activation_valide": evaluation.get(
            "activation_valide"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 15
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 16
# REFUS ET JOURNALISATION SECURISEE
# ============================================================

def mia26_controler_refus_securise(approbation_contexte=None):
    """
    B16 — Contrôle l'état de refus ou d'absence d'approbation.

    Cette fonction :
    - vérifie l'état de B15 ;
    - distingue l'absence d'approbation d'une approbation valide ;
    - journalise le refus de manière sécurisée ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(approbation_contexte, dict):
        return {
            "refus_securise_valide": False,
            "refus_journalise": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    approbation_controlee = (
        approbation_contexte.get(
            "approbation_controlee"
        ) is True
    )

    approbation_humaine = approbation_contexte.get(
        "approbation_humaine"
    )

    activation_valide = (
        approbation_contexte.get(
            "activation_valide"
        ) is True
    )

    refus = (
        approbation_controlee
        and approbation_humaine is not True
        and activation_valide is not True
    )

    refus_journalise = refus

    refus_securise_valide = (
        refus
        and refus_journalise
    )

    if refus_securise_valide:
        statut = "refus_securise_journalise"
    else:
        statut = "refus_securise_non_valide"

    return {
        "refus_securise_valide": refus_securise_valide,
        "refus_journalise": refus_journalise,
        "approbation_controlee": approbation_controlee,
        "approbation_humaine": approbation_humaine,
        "activation_valide": activation_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_refus_securise(refus_contexte):
    """
    B16 — Évalue uniquement le refus sécurisé.
    """

    if not isinstance(refus_contexte, dict):
        return None

    refus_valide = (
        refus_contexte.get(
            "refus_securise_valide"
        ) is True
        and refus_contexte.get(
            "refus_journalise"
        ) is True
        and refus_contexte.get(
            "execution_autorisee"
        ) is False
        and refus_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "refus_securise_valide": refus_valide,
        "refus_journalise": (
            refus_contexte.get(
                "refus_journalise"
            ) is True
        ),
        "statut": (
            "refus_securise_journalise"
            if refus_valide
            else "refus_securise_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_refus_securise(refus_contexte):
    """
    B16 — Produit le résumé du refus sécurisé.
    """

    evaluation = mia26_evaluer_refus_securise(
        refus_contexte
    )

    if evaluation is None:
        return None

    return {
        "refus_securise_valide": evaluation.get(
            "refus_securise_valide"
        ),
        "refus_journalise": evaluation.get(
            "refus_journalise"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 16
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 17
# CONTROLE GLOBAL AVANT ACTIVATION
# ============================================================

def mia26_controler_global_avant_activation(refus_contexte=None):
    """
    B17 — Effectue un contrôle global de l'état du cycle
    avant toute activation humaine éventuelle.

    Cette fonction :
    - vérifie la cohérence de B15 et B16 ;
    - vérifie l'état d'approbation humaine ;
    - vérifie l'état du refus sécurisé ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(refus_contexte, dict):
        return {
            "controle_global_valide": False,
            "activation_humaine_possible": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    approbation_controlee = (
        refus_contexte.get(
            "approbation_controlee"
        ) is True
    )

    approbation_humaine = (
        refus_contexte.get(
            "approbation_humaine"
        )
    )

    activation_valide = (
        refus_contexte.get(
            "activation_valide"
        ) is True
    )

    refus_securise_valide = (
        refus_contexte.get(
            "refus_securise_valide"
        ) is True
    )

    controle_global_valide = (
        approbation_controlee
        and approbation_humaine is True
        and activation_valide
        and not refus_securise_valide
    )

    activation_humaine_possible = controle_global_valide

    if controle_global_valide:
        statut = "controle_global_valide"
    else:
        statut = "controle_global_non_valide"

    return {
        "controle_global_valide": controle_global_valide,
        "activation_humaine_possible": activation_humaine_possible,
        "approbation_controlee": approbation_controlee,
        "approbation_humaine": approbation_humaine,
        "activation_valide": activation_valide,
        "refus_securise_valide": refus_securise_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_global_avant_activation(
    controle_contexte
):
    """
    B17 — Évalue uniquement le contrôle global avant activation.
    """

    if not isinstance(controle_contexte, dict):
        return None

    controle_valide = (
        controle_contexte.get(
            "controle_global_valide"
        ) is True
        and controle_contexte.get(
            "activation_humaine_possible"
        ) is True
        and controle_contexte.get(
            "execution_autorisee"
        ) is False
        and controle_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "controle_global_valide": controle_valide,
        "activation_humaine_possible": (
            controle_contexte.get(
                "activation_humaine_possible"
            ) is True
        ),
        "statut": (
            "controle_global_valide"
            if controle_valide
            else "controle_global_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_global_avant_activation(
    controle_contexte
):
    """
    B17 — Produit le résumé du contrôle global.
    """

    evaluation = mia26_evaluer_global_avant_activation(
        controle_contexte
    )

    if evaluation is None:
        return None

    return {
        "controle_global_valide": evaluation.get(
            "controle_global_valide"
        ),
        "activation_humaine_possible": evaluation.get(
            "activation_humaine_possible"
        ),
        "statut": evaluation.get(
            "statut"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 17
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 17
# CONTROLE GLOBAL AVANT ACTIVATION
# ============================================================

# ============================================================

# ============================================================
# MIA V26 — BRIQUE 18
# CONTROLE D'INTEGRITE AVANT ACTIVATION
# ============================================================

def mia26_controler_integrite_avant_activation(
    controle_contexte=None
):
    """
    B18 — Contrôle l'intégrité de l'état avant activation.

    Cette fonction :
    - vérifie que le contrôle global B17 est valide ;
    - vérifie qu'une activation humaine est possible ;
    - vérifie l'absence de refus sécurisé ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(controle_contexte, dict):
        return {
            "integrite_avant_activation_valide": False,
            "activation_humaine_possible": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    controle_global_valide = (
        controle_contexte.get(
            "controle_global_valide"
        ) is True
    )

    activation_humaine_possible = (
        controle_contexte.get(
            "activation_humaine_possible"
        ) is True
    )

    refus_securise_valide = (
        controle_contexte.get(
            "refus_securise_valide"
        ) is True
    )

    integrite_avant_activation_valide = (
        controle_global_valide
        and activation_humaine_possible
        and not refus_securise_valide
    )

    if integrite_avant_activation_valide:
        statut = "integrite_avant_activation_validee"
    else:
        statut = "integrite_avant_activation_non_validee"

    return {
        "integrite_avant_activation_valide":
            integrite_avant_activation_valide,
        "controle_global_valide":
            controle_global_valide,
        "activation_humaine_possible":
            activation_humaine_possible,
        "refus_securise_valide":
            refus_securise_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_integrite_avant_activation(
    integrite_contexte
):
    """
    B18 — Évalue uniquement l'intégrité avant activation.
    """

    if not isinstance(integrite_contexte, dict):
        return None

    integrite_valide = (
        integrite_contexte.get(
            "integrite_avant_activation_valide"
        ) is True
        and integrite_contexte.get(
            "execution_autorisee"
        ) is False
        and integrite_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "integrite_avant_activation_valide":
            integrite_valide,
        "statut": (
            "integrite_avant_activation_validee"
            if integrite_valide
            else "integrite_avant_activation_non_validee"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_integrite_avant_activation(
    integrite_contexte
):
    """
    B18 — Produit le résumé du contrôle d'intégrité.
    """

    evaluation = mia26_evaluer_integrite_avant_activation(
        integrite_contexte
    )

    if evaluation is None:
        return None

    return {
        "integrite_avant_activation_valide":
            evaluation.get(
                "integrite_avant_activation_valide"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 18
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 19
# INTEGRATION DU CONTROLE D'INTEGRITE
# ============================================================

def mia26_integrer_controle_integrite(
    integrite_contexte=None
):
    """
    B19 — Intègre le résultat du contrôle d'intégrité
    dans l'état global du cycle.

    Cette fonction :
    - vérifie l'intégrité B18 ;
    - conserve l'état de validation ;
    - bloque toute intégration si l'intégrité est invalide ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(integrite_contexte, dict):
        return {
            "integration_integrite_valide": False,
            "integrite_avant_activation_valide": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    integrite_valide = (
        integrite_contexte.get(
            "integrite_avant_activation_valide"
        ) is True
    )

    execution_interdite = (
        integrite_contexte.get(
            "execution_autorisee"
        ) is False
        and integrite_contexte.get(
            "execution_interdite"
        ) is True
    )

    integration_integrite_valide = (
        integrite_valide
        and execution_interdite
    )

    if integration_integrite_valide:
        statut = "integration_integrite_validee"
    else:
        statut = "integration_integrite_non_validee"

    return {
        "integration_integrite_valide":
            integration_integrite_valide,
        "integrite_avant_activation_valide":
            integrite_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_integration_integrite(
    integration_contexte
):
    """
    B19 — Évalue uniquement l'intégration du contrôle
    d'intégrité.
    """

    if not isinstance(integration_contexte, dict):
        return None

    integration_valide = (
        integration_contexte.get(
            "integration_integrite_valide"
        ) is True
        and integration_contexte.get(
            "execution_autorisee"
        ) is False
        and integration_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "integration_integrite_valide":
            integration_valide,
        "statut": (
            "integration_integrite_validee"
            if integration_valide
            else "integration_integrite_non_validee"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_integration_integrite(
    integration_contexte
):
    """
    B19 — Produit le résumé de l'intégration
    du contrôle d'intégrité.
    """

    evaluation = mia26_evaluer_integration_integrite(
        integration_contexte
    )

    if evaluation is None:
        return None

    return {
        "integration_integrite_valide":
            evaluation.get(
                "integration_integrite_valide"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 19
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 20
# JOURNALISATION DU CONTROLE SECURISE
# ============================================================

def mia26_journaliser_controle_securise(
    integration_contexte=None
):
    """
    B20 — Journalise l'état du contrôle sécurisé.

    Cette fonction :
    - vérifie que l'intégration B19 est valide ;
    - conserve une trace structurée de l'état ;
    - journalise uniquement les informations de contrôle ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - ne déclenche aucune action ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(integration_contexte, dict):
        return {
            "journal_controle_securise_valide": False,
            "integration_integrite_valide": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    integration_valide = (
        integration_contexte.get(
            "integration_integrite_valide"
        ) is True
    )

    execution_securisee = (
        integration_contexte.get(
            "execution_autorisee"
        ) is False
        and integration_contexte.get(
            "execution_interdite"
        ) is True
    )

    journal_controle_securise_valide = (
        integration_valide
        and execution_securisee
    )

    if journal_controle_securise_valide:
        statut = "journal_controle_securise_valide"
    else:
        statut = "journal_controle_securise_non_valide"

    return {
        "journal_controle_securise_valide":
            journal_controle_securise_valide,
        "integration_integrite_valide":
            integration_valide,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_journal_controle_securise(
    journal_contexte
):
    """
    B20 — Évalue uniquement la journalisation
    du contrôle sécurisé.
    """

    if not isinstance(journal_contexte, dict):
        return None

    journal_valide = (
        journal_contexte.get(
            "journal_controle_securise_valide"
        ) is True
        and journal_contexte.get(
            "execution_autorisee"
        ) is False
        and journal_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "journal_controle_securise_valide":
            journal_valide,
        "statut": (
            "journal_controle_securise_valide"
            if journal_valide
            else "journal_controle_securise_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_journal_controle_securise(
    journal_contexte
):
    """
    B20 — Produit le résumé de la journalisation
    du contrôle sécurisé.
    """

    evaluation = mia26_evaluer_journal_controle_securise(
        journal_contexte
    )

    if evaluation is None:
        return None

    return {
        "journal_controle_securise_valide":
            evaluation.get(
                "journal_controle_securise_valide"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 20
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 21
# DECISION FINALE D'ACTIVATION SECURISEE
# ============================================================

def mia26_decider_activation_securisee(
    journal_contexte=None
):
    """
    B21 — Détermine si les conditions préalables permettent
    une activation humaine sécurisée.

    Cette fonction :
    - vérifie la validité de la journalisation B20 ;
    - vérifie que l'intégrité précédente est valide ;
    - vérifie l'absence de refus sécurisé ;
    - vérifie la présence d'une approbation humaine ;
    - ne déclenche aucune activation ;
    - ne prend aucune décision opérationnelle à la place de l'humain ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(journal_contexte, dict):
        return {
            "decision_activation_securisee_valide": False,
            "activation_humaine_possible": False,
            "approbation_humaine": False,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    journal_valide = (
        journal_contexte.get(
            "journal_controle_securise_valide"
        ) is True
    )

    integrite_valide = (
        journal_contexte.get(
            "integration_integrite_valide"
        ) is True
    )

    approbation_humaine = (
        journal_contexte.get(
            "approbation_humaine"
        ) is True
    )

    refus_securise_valide = (
        journal_contexte.get(
            "refus_securise_valide"
        ) is True
    )

    conditions_valides = (
        journal_valide
        and integrite_valide
        and approbation_humaine
        and not refus_securise_valide
    )

    if conditions_valides:
        decision_activation_securisee_valide = True
        activation_humaine_possible = True
        statut = "activation_humaine_admissible"
    else:
        decision_activation_securisee_valide = False
        activation_humaine_possible = False
        statut = "activation_humaine_non_admissible"

    return {
        "decision_activation_securisee_valide":
            decision_activation_securisee_valide,
        "journal_controle_securise_valide":
            journal_valide,
        "integration_integrite_valide":
            integrite_valide,
        "approbation_humaine":
            approbation_humaine,
        "refus_securise_valide":
            refus_securise_valide,
        "activation_humaine_possible":
            activation_humaine_possible,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_decision_activation_securisee(
    decision_contexte
):
    """
    B21 — Évalue uniquement la décision d'activation
    sécurisée.
    """

    if not isinstance(decision_contexte, dict):
        return None

    decision_valide = (
        decision_contexte.get(
            "decision_activation_securisee_valide"
        ) is True
        and decision_contexte.get(
            "activation_humaine_possible"
        ) is True
        and decision_contexte.get(
            "execution_autorisee"
        ) is False
        and decision_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "decision_activation_securisee_valide":
            decision_valide,
        "activation_humaine_possible":
            decision_contexte.get(
                "activation_humaine_possible"
            ) is True,
        "statut": (
            "activation_humaine_admissible"
            if decision_valide
            else "activation_humaine_non_admissible"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_decision_activation_securisee(
    decision_contexte
):
    """
    B21 — Produit le résumé de la décision finale
    d'activation sécurisée.
    """

    evaluation = mia26_evaluer_decision_activation_securisee(
        decision_contexte
    )

    if evaluation is None:
        return None

    return {
        "decision_activation_securisee_valide":
            evaluation.get(
                "decision_activation_securisee_valide"
            ),
        "activation_humaine_possible":
            evaluation.get(
                "activation_humaine_possible"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 21
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 22
# VERROUILLAGE POST-ACTIVATION
# ============================================================

def mia26_verrouiller_post_activation(
    decision_contexte=None
):
    """
    B22 — Établit le verrouillage logique post-activation.

    Cette fonction :
    - vérifie la validité de la décision B21 ;
    - conserve l'état de décision ;
    - établit un verrou logique de sécurité ;
    - ne déclenche aucune activation réelle ;
    - ne modifie aucune donnée source ;
    - ne prend aucune décision à la place de l'humain ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(decision_contexte, dict):
        return {
            "verrouillage_post_activation_valide": False,
            "decision_activation_securisee_valide": False,
            "verrou_post_activation": True,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    decision_valide = (
        decision_contexte.get(
            "decision_activation_securisee_valide"
        ) is True
    )

    activation_humaine_possible = (
        decision_contexte.get(
            "activation_humaine_possible"
        ) is True
    )

    verrouillage_securise = (
        decision_contexte.get(
            "execution_autorisee"
        ) is False
        and decision_contexte.get(
            "execution_interdite"
        ) is True
    )

    verrouillage_post_activation_valide = (
        decision_valide
        and activation_humaine_possible
        and verrouillage_securise
    )

    if verrouillage_post_activation_valide:
        statut = "verrouillage_post_activation_valide"
    else:
        statut = "verrouillage_post_activation_non_valide"

    return {
        "verrouillage_post_activation_valide":
            verrouillage_post_activation_valide,
        "decision_activation_securisee_valide":
            decision_valide,
        "activation_humaine_possible":
            activation_humaine_possible,
        "verrou_post_activation": True,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_verrouillage_post_activation(
    verrouillage_contexte
):
    """
    B22 — Évalue uniquement le verrouillage
    post-activation.
    """

    if not isinstance(verrouillage_contexte, dict):
        return None

    verrouillage_valide = (
        verrouillage_contexte.get(
            "verrouillage_post_activation_valide"
        ) is True
        and verrouillage_contexte.get(
            "verrou_post_activation"
        ) is True
        and verrouillage_contexte.get(
            "execution_autorisee"
        ) is False
        and verrouillage_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "verrouillage_post_activation_valide":
            verrouillage_valide,
        "verrou_post_activation":
            verrouillage_contexte.get(
                "verrou_post_activation"
            ) is True,
        "statut": (
            "verrouillage_post_activation_valide"
            if verrouillage_valide
            else "verrouillage_post_activation_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_verrouillage_post_activation(
    verrouillage_contexte
):
    """
    B22 — Produit le résumé du verrouillage
    post-activation.
    """

    evaluation = mia26_evaluer_verrouillage_post_activation(
        verrouillage_contexte
    )

    if evaluation is None:
        return None

    return {
        "verrouillage_post_activation_valide":
            evaluation.get(
                "verrouillage_post_activation_valide"
            ),
        "verrou_post_activation":
            evaluation.get(
                "verrou_post_activation"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 22
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 23
# TRACABILITE DU VERROUILLAGE
# ============================================================

def mia26_tracer_verrouillage(
    verrouillage_contexte=None
):
    """
    B23 — Assure la traçabilité du verrouillage post-activation.

    Cette fonction :
    - vérifie la validité du verrouillage B22 ;
    - conserve une trace structurée de son état ;
    - vérifie que le verrou post-activation est actif ;
    - ne modifie aucune donnée source ;
    - ne modifie aucune décision précédente ;
    - ne déclenche aucune activation ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(verrouillage_contexte, dict):
        return {
            "tracabilite_verrouillage_valide": False,
            "verrouillage_post_activation_valide": False,
            "verrou_post_activation": True,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    verrouillage_valide = (
        verrouillage_contexte.get(
            "verrouillage_post_activation_valide"
        ) is True
    )

    verrou_actif = (
        verrouillage_contexte.get(
            "verrou_post_activation"
        ) is True
    )

    tracabilite_verrouillage_valide = (
        verrouillage_valide
        and verrou_actif
    )

    if tracabilite_verrouillage_valide:
        statut = "tracabilite_verrouillage_valide"
    else:
        statut = "tracabilite_verrouillage_non_valide"

    return {
        "tracabilite_verrouillage_valide":
            tracabilite_verrouillage_valide,
        "verrouillage_post_activation_valide":
            verrouillage_valide,
        "verrou_post_activation":
            verrou_actif,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_tracabilite_verrouillage(
    tracabilite_contexte
):
    """
    B23 — Évalue uniquement la traçabilité
    du verrouillage.
    """

    if not isinstance(tracabilite_contexte, dict):
        return None

    tracabilite_valide = (
        tracabilite_contexte.get(
            "tracabilite_verrouillage_valide"
        ) is True
        and tracabilite_contexte.get(
            "verrou_post_activation"
        ) is True
        and tracabilite_contexte.get(
            "execution_autorisee"
        ) is False
        and tracabilite_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "tracabilite_verrouillage_valide":
            tracabilite_valide,
        "verrou_post_activation":
            tracabilite_contexte.get(
                "verrou_post_activation"
            ) is True,
        "statut": (
            "tracabilite_verrouillage_valide"
            if tracabilite_valide
            else "tracabilite_verrouillage_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_tracabilite_verrouillage(
    tracabilite_contexte
):
    """
    B23 — Produit le résumé de la traçabilité
    du verrouillage.
    """

    evaluation = mia26_evaluer_tracabilite_verrouillage(
        tracabilite_contexte
    )

    if evaluation is None:
        return None

    return {
        "tracabilite_verrouillage_valide":
            evaluation.get(
                "tracabilite_verrouillage_valide"
            ),
        "verrou_post_activation":
            evaluation.get(
                "verrou_post_activation"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 23
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 24
# AUDIT COMPLET POST-ACTIVATION
# ============================================================

def mia26_auditer_post_activation(
    tracabilite_contexte=None
):
    """
    B24 — Réalise un audit complet de l'état
    post-activation.

    Cette fonction :
    - vérifie la validité de la traçabilité B23 ;
    - vérifie que le verrou post-activation est actif ;
    - vérifie que l'exécution automatique reste interdite ;
    - conserve l'état des contrôles précédents ;
    - ne modifie aucune donnée source ;
    - ne modifie aucune décision précédente ;
    - ne déclenche aucune activation ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(tracabilite_contexte, dict):
        return {
            "audit_post_activation_valide": False,
            "tracabilite_verrouillage_valide": False,
            "verrou_post_activation": True,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    tracabilite_valide = (
        tracabilite_contexte.get(
            "tracabilite_verrouillage_valide"
        ) is True
    )

    verrou_actif = (
        tracabilite_contexte.get(
            "verrou_post_activation"
        ) is True
    )

    securite_execution = (
        tracabilite_contexte.get(
            "execution_autorisee"
        ) is False
        and tracabilite_contexte.get(
            "execution_interdite"
        ) is True
    )

    audit_post_activation_valide = (
        tracabilite_valide
        and verrou_actif
        and securite_execution
    )

    if audit_post_activation_valide:
        statut = "audit_post_activation_valide"
    else:
        statut = "audit_post_activation_non_valide"

    return {
        "audit_post_activation_valide":
            audit_post_activation_valide,
        "tracabilite_verrouillage_valide":
            tracabilite_valide,
        "verrou_post_activation":
            verrou_actif,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_audit_post_activation(
    audit_contexte
):
    """
    B24 — Évalue uniquement l'audit
    post-activation.
    """

    if not isinstance(audit_contexte, dict):
        return None

    audit_valide = (
        audit_contexte.get(
            "audit_post_activation_valide"
        ) is True
        and audit_contexte.get(
            "verrou_post_activation"
        ) is True
        and audit_contexte.get(
            "execution_autorisee"
        ) is False
        and audit_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "audit_post_activation_valide":
            audit_valide,
        "verrou_post_activation":
            audit_contexte.get(
                "verrou_post_activation"
            ) is True,
        "statut": (
            "audit_post_activation_valide"
            if audit_valide
            else "audit_post_activation_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_audit_post_activation(
    audit_contexte
):
    """
    B24 — Produit le résumé de l'audit
    post-activation.
    """

    evaluation = mia26_evaluer_audit_post_activation(
        audit_contexte
    )

    if evaluation is None:
        return None

    return {
        "audit_post_activation_valide":
            evaluation.get(
                "audit_post_activation_valide"
            ),
        "verrou_post_activation":
            evaluation.get(
                "verrou_post_activation"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 24
# ============================================================



# ============================================================
# MIA V26 — BRIQUE 25
# COHERENCE GLOBALE DU JOURNAL
# ============================================================

def mia26_controler_coherence_globale_journal(
    audit_contexte=None
):
    """
    B25 — Contrôle la cohérence globale du journal
    à partir de l'état d'audit post-activation B24.

    Cette fonction :
    - vérifie la validité de l'audit B24 ;
    - vérifie la traçabilité du verrouillage B23 ;
    - vérifie que le verrou post-activation reste actif ;
    - vérifie que l'exécution automatique reste interdite ;
    - ne modifie aucune donnée source ;
    - ne modifie aucune décision précédente ;
    - ne déclenche aucune activation ;
    - n'autorise aucune exécution automatique.
    """

    if not isinstance(audit_contexte, dict):
        return {
            "coherence_globale_journal_valide": False,
            "audit_post_activation_valide": False,
            "tracabilite_verrouillage_valide": False,
            "verrou_post_activation": True,
            "statut": "contexte_invalide",
            "execution_autorisee": False,
            "execution_interdite": True
        }

    audit_valide = (
        audit_contexte.get(
            "audit_post_activation_valide"
        ) is True
    )

    tracabilite_valide = (
        audit_contexte.get(
            "tracabilite_verrouillage_valide"
        ) is True
    )

    verrou_actif = (
        audit_contexte.get(
            "verrou_post_activation"
        ) is True
    )

    securite_execution = (
        audit_contexte.get(
            "execution_autorisee"
        ) is False
        and audit_contexte.get(
            "execution_interdite"
        ) is True
    )

    coherence_globale_journal_valide = (
        audit_valide
        and tracabilite_valide
        and verrou_actif
        and securite_execution
    )

    if coherence_globale_journal_valide:
        statut = "coherence_globale_journal_valide"
    else:
        statut = "coherence_globale_journal_non_valide"

    return {
        "coherence_globale_journal_valide":
            coherence_globale_journal_valide,
        "audit_post_activation_valide":
            audit_valide,
        "tracabilite_verrouillage_valide":
            tracabilite_valide,
        "verrou_post_activation":
            verrou_actif,
        "statut": statut,
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_coherence_globale_journal(
    coherence_contexte
):
    """
    B25 — Évalue uniquement la cohérence globale
    du journal.
    """

    if not isinstance(coherence_contexte, dict):
        return None

    coherence_valide = (
        coherence_contexte.get(
            "coherence_globale_journal_valide"
        ) is True
        and coherence_contexte.get(
            "audit_post_activation_valide"
        ) is True
        and coherence_contexte.get(
            "tracabilite_verrouillage_valide"
        ) is True
        and coherence_contexte.get(
            "verrou_post_activation"
        ) is True
        and coherence_contexte.get(
            "execution_autorisee"
        ) is False
        and coherence_contexte.get(
            "execution_interdite"
        ) is True
    )

    return {
        "coherence_globale_journal_valide":
            coherence_valide,
        "verrou_post_activation":
            coherence_contexte.get(
                "verrou_post_activation"
            ) is True,
        "statut": (
            "coherence_globale_journal_valide"
            if coherence_valide
            else "coherence_globale_journal_non_valide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_coherence_globale_journal(
    coherence_contexte
):
    """
    B25 — Produit le résumé de la cohérence globale
    du journal.
    """

    evaluation = mia26_evaluer_coherence_globale_journal(
        coherence_contexte
    )

    if evaluation is None:
        return None

    return {
        "coherence_globale_journal_valide":
            evaluation.get(
                "coherence_globale_journal_valide"
            ),
        "verrou_post_activation":
            evaluation.get(
                "verrou_post_activation"
            ),
        "statut": evaluation.get("statut"),
        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 25
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 26
# TRAITEMENT DE LA REPONSE HUMAINE
# ============================================================

def mia26_analyser_reponse_humaine_cycle_decisionnel(
    coherence_contexte=None,
    reponse_humaine=None
):
    """
    B26 — Traite explicitement la réponse humaine
    après validation de la cohérence globale B25.

    Réponses reconnues :
    - autorisee
    - refusee
    - revision_demandee

    Cette fonction :
    - exige une cohérence B25 valide ;
    - respecte strictement la réponse humaine ;
    - ne déclenche aucune action ;
    - ne crée aucune autorisation automatique ;
    - interdit toute exécution automatique.
    """

    coherence_valide = (
        isinstance(coherence_contexte, dict)
        and coherence_contexte.get(
            "coherence_globale_journal_valide"
        ) is True
        and coherence_contexte.get(
            "audit_post_activation_valide"
        ) is True
        and coherence_contexte.get(
            "tracabilite_verrouillage_valide"
        ) is True
        and coherence_contexte.get(
            "verrou_post_activation"
        ) is True
        and coherence_contexte.get(
            "execution_autorisee"
        ) is False
        and coherence_contexte.get(
            "execution_interdite"
        ) is True
    )

    reponse_valide = reponse_humaine in {
        "autorisee",
        "refusee",
        "revision_demandee"
    }

    if not coherence_valide:
        statut = "coherence_globale_invalide"

    elif not reponse_valide:
        statut = "reponse_humaine_invalide"

    elif reponse_humaine == "autorisee":
        statut = "autorisation_humaine_recue"

    elif reponse_humaine == "refusee":
        statut = "autorisation_humaine_refusee"

    else:
        statut = "revision_humaine_demandee"

    traitement_valide = (
        coherence_valide
        and reponse_valide
    )

    return {
        "coherence_globale_valide": coherence_valide,
        "reponse_humaine": reponse_humaine,
        "reponse_valide": reponse_valide,
        "traitement_valide": traitement_valide,
        "statut": statut,

        "autorisation_humaine_recue": (
            traitement_valide
            and reponse_humaine == "autorisee"
        ),

        "autorisation_humaine_refusee": (
            traitement_valide
            and reponse_humaine == "refusee"
        ),

        "revision_humaine_demandee": (
            traitement_valide
            and reponse_humaine == "revision_demandee"
        ),

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_reponse_humaine_cycle_decisionnel(
    analyse
):
    """
    B26 — Évalue la réponse humaine sans
    exécuter aucune action.
    """

    if not isinstance(analyse, dict):
        return None

    traitement_valide = (
        analyse.get(
            "traitement_valide"
        ) is True
    )

    return {
        "coherence_globale_valide":
            analyse.get(
                "coherence_globale_valide",
                False
            ),

        "reponse_humaine":
            analyse.get(
                "reponse_humaine"
            ),

        "reponse_valide":
            analyse.get(
                "reponse_valide",
                False
            ),

        "traitement_valide":
            traitement_valide,

        "autorisation_humaine_recue":
            analyse.get(
                "autorisation_humaine_recue",
                False
            ),

        "autorisation_humaine_refusee":
            analyse.get(
                "autorisation_humaine_refusee",
                False
            ),

        "revision_humaine_demandee":
            analyse.get(
                "revision_humaine_demandee",
                False
            ),

        "statut": (
            analyse.get(
                "statut",
                "reponse_humaine_invalide"
            )
        ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_reponse_humaine_cycle_decisionnel(
    analyse
):
    """
    B26 — Produit le résumé de la réponse humaine.
    """

    evaluation = (
        mia26_evaluer_reponse_humaine_cycle_decisionnel(
            analyse
        )
    )

    if evaluation is None:
        return None

    return {
        "coherence_globale_valide":
            evaluation.get(
                "coherence_globale_valide"
            ),

        "reponse_humaine":
            evaluation.get(
                "reponse_humaine"
            ),

        "reponse_valide":
            evaluation.get(
                "reponse_valide"
            ),

        "traitement_valide":
            evaluation.get(
                "traitement_valide"
            ),

        "autorisation_humaine_recue":
            evaluation.get(
                "autorisation_humaine_recue"
            ),

        "autorisation_humaine_refusee":
            evaluation.get(
                "autorisation_humaine_refusee"
            ),

        "revision_humaine_demandee":
            evaluation.get(
                "revision_humaine_demandee"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 26
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 27
# SYNTHESE SECURISEE DU CYCLE
# ============================================================

def mia26_analyser_synthese_securisee_cycle(
    reponse_humaine_contexte=None
):
    """
    B27 — Produit une synthèse sécurisée du cycle
    après traitement de la réponse humaine B26.

    Cette fonction :
    - exige un traitement B26 valide ;
    - respecte strictement la réponse humaine ;
    - synthétise l'état du cycle ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation automatique ;
    - ne déclenche aucune action ;
    - interdit toute exécution automatique.
    """

    contexte_valide = (
        isinstance(reponse_humaine_contexte, dict)
        and reponse_humaine_contexte.get(
            "coherence_globale_valide"
        ) is True
        and reponse_humaine_contexte.get(
            "reponse_valide"
        ) is True
        and reponse_humaine_contexte.get(
            "traitement_valide"
        ) is True
        and reponse_humaine_contexte.get(
            "execution_autorisee"
        ) is False
        and reponse_humaine_contexte.get(
            "execution_interdite"
        ) is True
    )

    reponse = None

    if isinstance(reponse_humaine_contexte, dict):
        reponse = reponse_humaine_contexte.get(
            "reponse_humaine"
        )

    if not contexte_valide:
        statut = "contexte_b26_invalide"
        synthese = "cycle_invalide"

    elif reponse == "autorisee":
        statut = "synthese_autorisation_humaine"
        synthese = "autorisation_humaine_recue"

    elif reponse == "refusee":
        statut = "synthese_refus_humain"
        synthese = "cycle_refuse_par_humain"

    elif reponse == "revision_demandee":
        statut = "synthese_revision_humaine"
        synthese = "cycle_en_revision_humaine"

    else:
        statut = "synthese_reponse_inconnue"
        synthese = "reponse_humaine_inconnue"

    synthese_valide = (
        contexte_valide
        and reponse in {
            "autorisee",
            "refusee",
            "revision_demandee"
        }
    )

    return {
        "contexte_b26_valide": contexte_valide,
        "reponse_humaine": reponse,
        "synthese": synthese,
        "synthese_valide": synthese_valide,
        "statut": statut,

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_synthese_securisee_cycle(
    synthese_contexte
):
    """
    B27 — Évalue la synthèse sécurisée
    sans exécuter aucune action.
    """

    if not isinstance(synthese_contexte, dict):
        return None

    return {
        "contexte_b26_valide":
            synthese_contexte.get(
                "contexte_b26_valide",
                False
            ),

        "reponse_humaine":
            synthese_contexte.get(
                "reponse_humaine"
            ),

        "synthese":
            synthese_contexte.get(
                "synthese"
            ),

        "synthese_valide":
            synthese_contexte.get(
                "synthese_valide",
                False
            ),

        "statut":
            synthese_contexte.get(
                "statut",
                "contexte_b26_invalide"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_synthese_securisee_cycle(
    synthese_contexte
):
    """
    B27 — Produit le résumé final de la synthèse
    sécurisée du cycle.
    """

    evaluation = (
        mia26_evaluer_synthese_securisee_cycle(
            synthese_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "synthese_valide":
            evaluation.get(
                "synthese_valide"
            ),

        "reponse_humaine":
            evaluation.get(
                "reponse_humaine"
            ),

        "synthese":
            evaluation.get(
                "synthese"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 27
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 28
# CONTROLE FINAL AVANT CLOTURE DU CYCLE
# ============================================================

def mia26_analyser_controle_final_avant_cloture_cycle(
    synthese_securisee_contexte=None
):
    """
    B28 — Contrôle final avant clôture du cycle.

    Cette fonction :
    - exige une synthèse B27 valide ;
    - vérifie que le contexte B26 est valide ;
    - respecte la réponse humaine ;
    - vérifie que la synthèse correspond à la réponse humaine ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation automatique ;
    - ne déclenche aucune action ;
    - interdit toute exécution automatique.
    """

    contexte_valide = (
        isinstance(synthese_securisee_contexte, dict)
        and synthese_securisee_contexte.get(
            "contexte_b26_valide"
        ) is True
        and synthese_securisee_contexte.get(
            "synthese_valide"
        ) is True
        and synthese_securisee_contexte.get(
            "execution_autorisee"
        ) is False
        and synthese_securisee_contexte.get(
            "execution_interdite"
        ) is True
    )

    reponse = None
    synthese = None

    if isinstance(synthese_securisee_contexte, dict):
        reponse = synthese_securisee_contexte.get(
            "reponse_humaine"
        )
        synthese = synthese_securisee_contexte.get(
            "synthese"
        )

    correspondance_valide = (
        (reponse == "autorisee"
         and synthese == "autorisation_humaine_recue")
        or
        (reponse == "refusee"
         and synthese == "cycle_refuse_par_humain")
        or
        (reponse == "revision_demandee"
         and synthese == "cycle_en_revision_humaine")
    )

    controle_valide = (
        contexte_valide
        and correspondance_valide
    )

    if not contexte_valide:
        statut = "contexte_b27_invalide"
        cloture = "cloture_interdite"

    elif not correspondance_valide:
        statut = "correspondance_reponse_synthese_invalide"
        cloture = "cloture_interdite"

    elif reponse == "autorisee":
        statut = "controle_final_cloture_admissible"
        cloture = "cloture_securisee_admissible"

    elif reponse == "refusee":
        statut = "controle_final_refus_humain"
        cloture = "cloture_securisee_admissible"

    else:
        statut = "controle_final_revision_humaine"
        cloture = "cloture_securisee_admissible"

    return {
        "contexte_b27_valide": contexte_valide,
        "reponse_humaine": reponse,
        "synthese": synthese,
        "correspondance_valide": correspondance_valide,
        "controle_valide": controle_valide,
        "cloture": cloture,
        "statut": statut,

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_controle_final_avant_cloture_cycle(
    controle_contexte
):
    """
    B28 — Évalue le contrôle final sans exécuter
    aucune action.
    """

    if not isinstance(controle_contexte, dict):
        return None

    return {
        "contexte_b27_valide":
            controle_contexte.get(
                "contexte_b27_valide",
                False
            ),

        "reponse_humaine":
            controle_contexte.get(
                "reponse_humaine"
            ),

        "synthese":
            controle_contexte.get(
                "synthese"
            ),

        "correspondance_valide":
            controle_contexte.get(
                "correspondance_valide",
                False
            ),

        "controle_valide":
            controle_contexte.get(
                "controle_valide",
                False
            ),

        "cloture":
            controle_contexte.get(
                "cloture",
                "cloture_interdite"
            ),

        "statut":
            controle_contexte.get(
                "statut",
                "contexte_b27_invalide"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_controle_final_avant_cloture_cycle(
    controle_contexte
):
    """
    B28 — Produit le résumé du contrôle final
    avant clôture du cycle.
    """

    evaluation = (
        mia26_evaluer_controle_final_avant_cloture_cycle(
            controle_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "controle_valide":
            evaluation.get(
                "controle_valide"
            ),

        "reponse_humaine":
            evaluation.get(
                "reponse_humaine"
            ),

        "synthese":
            evaluation.get(
                "synthese"
            ),

        "correspondance_valide":
            evaluation.get(
                "correspondance_valide"
            ),

        "cloture":
            evaluation.get(
                "cloture"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 28
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 29
# ENREGISTREMENT SECURISE DE LA CLOTURE
# ============================================================

def mia26_analyser_enregistrement_securise_cloture_cycle(
    controle_final_contexte=None
):
    """
    B29 — Enregistre de manière sécurisée l'état de clôture
    après validation du contrôle final B28.

    Cette fonction :
    - exige un contrôle B28 valide ;
    - exige une clôture sécurisée admissible ;
    - respecte strictement la réponse humaine ;
    - enregistre uniquement l'état du cycle ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation automatique ;
    - ne déclenche aucune action ;
    - interdit toute exécution automatique.
    """

    contexte_valide = (
        isinstance(controle_final_contexte, dict)
        and controle_final_contexte.get(
            "contexte_b27_valide"
        ) is True
        and controle_final_contexte.get(
            "correspondance_valide"
        ) is True
        and controle_final_contexte.get(
            "controle_valide"
        ) is True
        and controle_final_contexte.get(
            "cloture"
        ) == "cloture_securisee_admissible"
        and controle_final_contexte.get(
            "execution_autorisee"
        ) is False
        and controle_final_contexte.get(
            "execution_interdite"
        ) is True
    )

    reponse = None
    synthese = None

    if isinstance(controle_final_contexte, dict):
        reponse = controle_final_contexte.get(
            "reponse_humaine"
        )
        synthese = controle_final_contexte.get(
            "synthese"
        )

    correspondance_valide = (
        (reponse == "autorisee"
         and synthese == "autorisation_humaine_recue")
        or
        (reponse == "refusee"
         and synthese == "cycle_refuse_par_humain")
        or
        (reponse == "revision_demandee"
         and synthese == "cycle_en_revision_humaine")
    )

    if not contexte_valide:
        statut = "controle_final_b28_invalide"
        enregistrement = "cloture_non_enregistree"

    elif not correspondance_valide:
        statut = "correspondance_reponse_synthese_invalide"
        enregistrement = "cloture_non_enregistree"

    elif reponse == "autorisee":
        statut = "cloture_securisee_enregistree"
        enregistrement = "cloture_autorisee_humainement"

    elif reponse == "refusee":
        statut = "cloture_refusee_humainement_enregistree"
        enregistrement = "cloture_refusee_par_humain"

    elif reponse == "revision_demandee":
        statut = "cloture_revision_humaine_enregistree"
        enregistrement = "cloture_en_revision_humaine"

    else:
        statut = "reponse_humaine_inconnue"
        enregistrement = "cloture_non_enregistree"

    enregistrement_valide = (
        contexte_valide
        and correspondance_valide
        and reponse in {
            "autorisee",
            "refusee",
            "revision_demandee"
        }
    )

    return {
        "controle_final_b28_valide": contexte_valide,
        "reponse_humaine": reponse,
        "synthese": synthese,
        "enregistrement": enregistrement,
        "enregistrement_valide": enregistrement_valide,
        "statut": statut,

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_enregistrement_securise_cloture_cycle(
    enregistrement_contexte
):
    """
    B29 — Évalue l'enregistrement sécurisé de la clôture
    sans exécuter aucune action.
    """

    if not isinstance(enregistrement_contexte, dict):
        return None

    return {
        "controle_final_b28_valide":
            enregistrement_contexte.get(
                "controle_final_b28_valide",
                False
            ),

        "reponse_humaine":
            enregistrement_contexte.get(
                "reponse_humaine"
            ),

        "synthese":
            enregistrement_contexte.get(
                "synthese"
            ),

        "enregistrement":
            enregistrement_contexte.get(
                "enregistrement"
            ),

        "enregistrement_valide":
            enregistrement_contexte.get(
                "enregistrement_valide",
                False
            ),

        "statut":
            enregistrement_contexte.get(
                "statut",
                "controle_final_b28_invalide"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_enregistrement_securise_cloture_cycle(
    enregistrement_contexte
):
    """
    B29 — Produit le résumé final de l'enregistrement
    sécurisé de la clôture.
    """

    evaluation = (
        mia26_evaluer_enregistrement_securise_cloture_cycle(
            enregistrement_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "enregistrement_valide":
            evaluation.get(
                "enregistrement_valide"
            ),

        "reponse_humaine":
            evaluation.get(
                "reponse_humaine"
            ),

        "enregistrement":
            evaluation.get(
                "enregistrement"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 29
# ============================================================

# ============================================================
# MIA V26 — BRIQUE 30
# CONFIRMATION SECURISEE DE FIN DE CYCLE
# ============================================================

def mia26_analyser_confirmation_securisee_fin_cycle(
    enregistrement_cloture_contexte=None
):
    """
    B30 — Confirme de manière sécurisée la fin logique du cycle.

    Cette fonction :
    - exige un enregistrement B29 valide ;
    - exige une clôture correctement enregistrée ;
    - vérifie la cohérence entre la réponse humaine et
      l'enregistrement de clôture ;
    - confirme uniquement la fin logique du cycle ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation automatique ;
    - ne déclenche aucune action ;
    - interdit toute exécution automatique.
    """

    contexte_valide = (
        isinstance(enregistrement_cloture_contexte, dict)
        and enregistrement_cloture_contexte.get(
            "controle_final_b28_valide"
        ) is True
        and enregistrement_cloture_contexte.get(
            "enregistrement_valide"
        ) is True
        and enregistrement_cloture_contexte.get(
            "execution_autorisee"
        ) is False
        and enregistrement_cloture_contexte.get(
            "execution_interdite"
        ) is True
    )

    reponse = None
    synthese = None
    enregistrement = None

    if isinstance(enregistrement_cloture_contexte, dict):
        reponse = enregistrement_cloture_contexte.get(
            "reponse_humaine"
        )
        synthese = enregistrement_cloture_contexte.get(
            "synthese"
        )
        enregistrement = enregistrement_cloture_contexte.get(
            "enregistrement"
        )

    correspondance_valide = (
        contexte_valide
        and (
            (
                reponse == "autorisee"
                and synthese == "autorisation_humaine_recue"
                and enregistrement == "cloture_autorisee_humainement"
            )
            or
            (
                reponse == "refusee"
                and synthese == "cycle_refuse_par_humain"
                and enregistrement == "cloture_refusee_par_humain"
            )
            or
            (
                reponse == "revision_demandee"
                and synthese == "cycle_en_revision_humaine"
                and enregistrement == "cloture_en_revision_humaine"
            )
        )
    )

    if not contexte_valide:
        statut = "enregistrement_b29_invalide"
        confirmation = "fin_cycle_non_confirmee"

    elif not correspondance_valide:
        statut = "correspondance_reponse_enregistrement_invalide"
        confirmation = "fin_cycle_non_confirmee"

    elif reponse == "autorisee":
        statut = "fin_cycle_logique_confirmee"
        confirmation = "cycle_termine_logiquement"

    elif reponse == "refusee":
        statut = "fin_cycle_refus_humain_confirmee"
        confirmation = "cycle_termine_apres_refus_humain"

    elif reponse == "revision_demandee":
        statut = "fin_cycle_revision_humaine_confirmee"
        confirmation = "cycle_termine_en_revision_humaine"

    else:
        statut = "reponse_humaine_inconnue"
        confirmation = "fin_cycle_non_confirmee"

    confirmation_valide = (
        contexte_valide
        and correspondance_valide
        and confirmation in {
            "cycle_termine_logiquement",
            "cycle_termine_apres_refus_humain",
            "cycle_termine_en_revision_humaine"
        }
    )

    return {
        "enregistrement_b29_valide": contexte_valide,
        "reponse_humaine": reponse,
        "enregistrement": enregistrement,
        "correspondance_valide": correspondance_valide,
        "confirmation": confirmation,
        "confirmation_valide": confirmation_valide,
        "statut": statut,

        # ----------------------------------------------------
        # BLOCAGE DE SECURITE
        # ----------------------------------------------------
        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_evaluer_confirmation_securisee_fin_cycle(
    confirmation_contexte
):
    """
    B30 — Évalue la confirmation sécurisée de fin de cycle
    sans exécuter aucune action.
    """

    if not isinstance(confirmation_contexte, dict):
        return None

    return {
        "enregistrement_b29_valide":
            confirmation_contexte.get(
                "enregistrement_b29_valide",
                False
            ),

        "reponse_humaine":
            confirmation_contexte.get(
                "reponse_humaine"
            ),

        "enregistrement":
            confirmation_contexte.get(
                "enregistrement"
            ),

        "correspondance_valide":
            confirmation_contexte.get(
                "correspondance_valide",
                False
            ),

        "confirmation":
            confirmation_contexte.get(
                "confirmation",
                "fin_cycle_non_confirmee"
            ),

        "confirmation_valide":
            confirmation_contexte.get(
                "confirmation_valide",
                False
            ),

        "statut":
            confirmation_contexte.get(
                "statut",
                "enregistrement_b29_invalide"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


def mia26_resumer_confirmation_securisee_fin_cycle(
    confirmation_contexte
):
    """
    B30 — Produit le résumé final de la confirmation
    sécurisée de fin de cycle.
    """

    evaluation = (
        mia26_evaluer_confirmation_securisee_fin_cycle(
            confirmation_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "confirmation_valide":
            evaluation.get(
                "confirmation_valide"
            ),

        "reponse_humaine":
            evaluation.get(
                "reponse_humaine"
            ),

        "enregistrement":
            evaluation.get(
                "enregistrement"
            ),

        "confirmation":
            evaluation.get(
                "confirmation"
            ),

        "correspondance_valide":
            evaluation.get(
                "correspondance_valide"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V26 — BRIQUE 30
# ============================================================

# ============================================================
# MIA V27 — BRIQUE 31
# PREPARATION SECURISEE DU CYCLE SUIVANT
# ============================================================

def mia27_preparer_cycle_suivant(
    confirmation_fin_cycle_contexte=None
):
    """
    B31 — Prépare de manière sécurisée un contexte
    pour un éventuel cycle suivant.

    Cette fonction :
    - exige une confirmation B30 valide ;
    - exige que le cycle précédent soit terminé logiquement ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne crée aucune autorisation automatique ;
    - ne modifie aucune donnée source ;
    - interdit toute exécution automatique.
    """

    contexte_valide = (
        isinstance(confirmation_fin_cycle_contexte, dict)
        and confirmation_fin_cycle_contexte.get(
            "confirmation_valide"
        ) is True
        and confirmation_fin_cycle_contexte.get(
            "confirmation"
        ) == "cycle_termine_logiquement"
        and confirmation_fin_cycle_contexte.get(
            "execution_autorisee"
        ) is False
        and confirmation_fin_cycle_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b30_valide": False,
            "cycle_precedent_termine": False,
            "preparation_valide": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "preparation_cycle_suivant_bloquee"
        }

    return {
        "b30_valide": True,
        "cycle_precedent_termine": True,
        "preparation_valide": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "cycle_suivant_prepare_securitairement"
    }


def mia27_evaluer_preparation_cycle_suivant(
    preparation_contexte
):
    """
    B31 — Évalue la préparation du cycle suivant
    sans démarrer ni exécuter aucune action.
    """

    if not isinstance(preparation_contexte, dict):
        return None

    return {
        "b30_valide": preparation_contexte.get(
            "b30_valide",
            False
        ),
        "cycle_precedent_termine":
            preparation_contexte.get(
                "cycle_precedent_termine",
                False
            ),
        "preparation_valide":
            preparation_contexte.get(
                "preparation_valide",
                False
            ),
        "nouveau_cycle_demarre":
            preparation_contexte.get(
                "nouveau_cycle_demarre",
                False
            ),
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut":
            preparation_contexte.get(
                "statut",
                "preparation_cycle_suivant_bloquee"
            )
    }


def mia27_resumer_preparation_cycle_suivant(
    preparation_contexte
):
    """
    B31 — Produit le résumé de la préparation sécurisée
    du cycle suivant.
    """

    evaluation = (
        mia27_evaluer_preparation_cycle_suivant(
            preparation_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "b30_valide":
            evaluation.get("b30_valide"),

        "cycle_precedent_termine":
            evaluation.get(
                "cycle_precedent_termine"
            ),

        "preparation_valide":
            evaluation.get(
                "preparation_valide"
            ),

        "nouveau_cycle_demarre":
            evaluation.get(
                "nouveau_cycle_demarre"
            ),

        "statut":
            evaluation.get("statut"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V27 — BRIQUE 31
# ============================================================

# ============================================================
# MIA V28 — BRIQUE 32
# CONTROLE DE COHERENCE DE LA PREPARATION DU CYCLE SUIVANT
# ============================================================

def mia28_controler_preparation_cycle_suivant(
    preparation_cycle_suivant_contexte=None
):
    """
    B32 — Contrôle la cohérence de la préparation produite
    par B31.

    Cette fonction :
    - exige une préparation B31 valide ;
    - vérifie la cohérence de la transition B30 → B31 ;
    - vérifie que le cycle précédent est terminé ;
    - vérifie que le nouveau cycle n'est pas démarré ;
    - interdit toute exécution automatique ;
    - ne déclenche aucune action ;
    - ne crée aucune autorisation automatique ;
    - ne modifie aucune donnée source.
    """

    contexte_valide = (
        isinstance(preparation_cycle_suivant_contexte, dict)
        and preparation_cycle_suivant_contexte.get(
            "b30_valide"
        ) is True
        and preparation_cycle_suivant_contexte.get(
            "cycle_precedent_termine"
        ) is True
        and preparation_cycle_suivant_contexte.get(
            "preparation_valide"
        ) is True
        and preparation_cycle_suivant_contexte.get(
            "nouveau_cycle_demarre"
        ) is False
        and preparation_cycle_suivant_contexte.get(
            "execution_autorisee"
        ) is False
        and preparation_cycle_suivant_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b31_valide": False,
            "transition_b30_b31_coherente": False,
            "cycle_precedent_termine": False,
            "preparation_coherente": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "controle_valide": False,
            "statut": "controle_preparation_cycle_suivant_bloque"
        }

    return {
        "b31_valide": True,
        "transition_b30_b31_coherente": True,
        "cycle_precedent_termine": True,
        "preparation_coherente": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_valide": True,
        "statut": "preparation_cycle_suivant_coherente"
    }


def mia28_evaluer_controle_preparation_cycle_suivant(
    controle_contexte
):
    """
    B32 — Évalue le contrôle de cohérence sans
    démarrer ni exécuter aucune action.
    """

    if not isinstance(controle_contexte, dict):
        return None

    return {
        "b31_valide": controle_contexte.get(
            "b31_valide",
            False
        ),
        "transition_b30_b31_coherente":
            controle_contexte.get(
                "transition_b30_b31_coherente",
                False
            ),
        "cycle_precedent_termine":
            controle_contexte.get(
                "cycle_precedent_termine",
                False
            ),
        "preparation_coherente":
            controle_contexte.get(
                "preparation_coherente",
                False
            ),
        "nouveau_cycle_demarre":
            controle_contexte.get(
                "nouveau_cycle_demarre",
                False
            ),
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_valide":
            controle_contexte.get(
                "controle_valide",
                False
            ),
        "statut":
            controle_contexte.get(
                "statut",
                "controle_preparation_cycle_suivant_bloque"
            )
    }


def mia28_resumer_controle_preparation_cycle_suivant(
    controle_contexte
):
    """
    B32 — Produit le résumé du contrôle sécurisé
    de la préparation du cycle suivant.
    """

    evaluation = (
        mia28_evaluer_controle_preparation_cycle_suivant(
            controle_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "b31_valide":
            evaluation.get("b31_valide"),

        "transition_b30_b31_coherente":
            evaluation.get(
                "transition_b30_b31_coherente"
            ),

        "cycle_precedent_termine":
            evaluation.get(
                "cycle_precedent_termine"
            ),

        "preparation_coherente":
            evaluation.get(
                "preparation_coherente"
            ),

        "nouveau_cycle_demarre":
            evaluation.get(
                "nouveau_cycle_demarre"
            ),

        "controle_valide":
            evaluation.get(
                "controle_valide"
            ),

        "statut":
            evaluation.get("statut"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V28 — BRIQUE 32
# ============================================================

# ============================================================
# MIA V29 — BRIQUE 33
# CONTROLE GLOBAL DE LA TRANSITION VERS LE CYCLE SUIVANT
# ============================================================

def mia29_controler_coherence_cycle_suivant(
    coherence_cycle_suivant_contexte=None
):
    """
    B33 — Contrôle la cohérence globale de la transition
    B30 → B31 → B32.

    Cette fonction :
    - exige une confirmation valide de B30 ;
    - exige une préparation valide de B31 ;
    - exige une préparation cohérente validée par B32 ;
    - vérifie que le cycle précédent est terminé ;
    - vérifie qu'aucun nouveau cycle n'est démarré ;
    - interdit toute exécution automatique ;
    - ne déclenche aucune action ;
    - ne crée aucune autorisation automatique ;
    - ne modifie aucune donnée source.
    """

    contexte_valide = (
        isinstance(coherence_cycle_suivant_contexte, dict)
        and coherence_cycle_suivant_contexte.get(
            "b31_valide"
        ) is True
        and coherence_cycle_suivant_contexte.get(
            "transition_b30_b31_coherente"
        ) is True
        and coherence_cycle_suivant_contexte.get(
            "cycle_precedent_termine"
        ) is True
        and coherence_cycle_suivant_contexte.get(
            "preparation_coherente"
        ) is True
        and coherence_cycle_suivant_contexte.get(
            "controle_valide"
        ) is True
        and coherence_cycle_suivant_contexte.get(
            "nouveau_cycle_demarre"
        ) is False
        and coherence_cycle_suivant_contexte.get(
            "execution_autorisee"
        ) is False
        and coherence_cycle_suivant_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b32_valide": False,
            "transition_globale_coherente": False,
            "cycle_precedent_termine": False,
            "preparation_cycle_suivant_coherente": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "controle_global_valide": False,
            "statut": "coherence_cycle_suivant_bloquee"
        }

    return {
        "b32_valide": True,
        "transition_globale_coherente": True,
        "cycle_precedent_termine": True,
        "preparation_cycle_suivant_coherente": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_global_valide": True,
        "statut": "coherence_cycle_suivant_validee"
    }


def mia29_evaluer_coherence_cycle_suivant(
    coherence_contexte
):
    """
    B33 — Évalue la cohérence globale sans démarrer
    ni exécuter aucune action.
    """

    if not isinstance(coherence_contexte, dict):
        return None

    return {
        "b32_valide": coherence_contexte.get(
            "b32_valide",
            False
        ),
        "transition_globale_coherente":
            coherence_contexte.get(
                "transition_globale_coherente",
                False
            ),
        "cycle_precedent_termine":
            coherence_contexte.get(
                "cycle_precedent_termine",
                False
            ),
        "preparation_cycle_suivant_coherente":
            coherence_contexte.get(
                "preparation_cycle_suivant_coherente",
                False
            ),
        "nouveau_cycle_demarre":
            coherence_contexte.get(
                "nouveau_cycle_demarre",
                False
            ),
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_global_valide":
            coherence_contexte.get(
                "controle_global_valide",
                False
            ),
        "statut":
            coherence_contexte.get(
                "statut",
                "coherence_cycle_suivant_bloquee"
            )
    }


def mia29_resumer_coherence_cycle_suivant(
    coherence_contexte
):
    """
    B33 — Produit le résumé sécurisé du contrôle
    global de la transition vers le cycle suivant.
    """

    evaluation = (
        mia29_evaluer_coherence_cycle_suivant(
            coherence_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "b32_valide":
            evaluation.get("b32_valide"),

        "transition_globale_coherente":
            evaluation.get(
                "transition_globale_coherente"
            ),

        "cycle_precedent_termine":
            evaluation.get(
                "cycle_precedent_termine"
            ),

        "preparation_cycle_suivant_coherente":
            evaluation.get(
                "preparation_cycle_suivant_coherente"
            ),

        "nouveau_cycle_demarre":
            evaluation.get(
                "nouveau_cycle_demarre"
            ),

        "controle_global_valide":
            evaluation.get(
                "controle_global_valide"
            ),

        "statut":
            evaluation.get("statut"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V29 — BRIQUE 33
# ============================================================

# ============================================================
# MIA V29 — BRIQUE 33
# CONTROLE GLOBAL DE LA TRANSITION VERS LE CYCLE SUIVANT
# ============================================================



# ============================================================
# FIN MIA V29 — BRIQUE 33
# ============================================================

# ============================================================
# MIA V30 — BRIQUE 34
# CONTROLE D'INTEGRITE DU CYCLE SUIVANT
# ============================================================

def mia30_controler_integrite_cycle_suivant(
    integrite_cycle_suivant_contexte=None
):
    """
    B34 — Contrôle l'intégrité de la transition validée par B33.

    Cette fonction :
    - exige une validation globale de B33 ;
    - exige une transition globale cohérente ;
    - exige que le cycle précédent soit terminé ;
    - exige que la préparation du cycle suivant soit cohérente ;
    - vérifie qu'aucun nouveau cycle n'est démarré ;
    - interdit toute exécution automatique ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source.
    """

    contexte_valide = (
        isinstance(integrite_cycle_suivant_contexte, dict)
        and integrite_cycle_suivant_contexte.get(
            "controle_global_valide"
        ) is True
        and integrite_cycle_suivant_contexte.get(
            "transition_globale_coherente"
        ) is True
        and integrite_cycle_suivant_contexte.get(
            "cycle_precedent_termine"
        ) is True
        and integrite_cycle_suivant_contexte.get(
            "preparation_cycle_suivant_coherente"
        ) is True
        and integrite_cycle_suivant_contexte.get(
            "nouveau_cycle_demarre"
        ) is False
        and integrite_cycle_suivant_contexte.get(
            "execution_autorisee"
        ) is False
        and integrite_cycle_suivant_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b33_valide": False,
            "integrite_cycle_suivant_validee": False,
            "transition_globale_coherente": False,
            "cycle_precedent_termine": False,
            "preparation_cycle_suivant_coherente": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "controle_integrite_valide": False,
            "statut": "integrite_cycle_suivant_bloquee"
        }

    return {
        "b33_valide": True,
        "integrite_cycle_suivant_validee": True,
        "transition_globale_coherente": True,
        "cycle_precedent_termine": True,
        "preparation_cycle_suivant_coherente": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_integrite_valide": True,
        "statut": "integrite_cycle_suivant_validee"
    }


def mia30_evaluer_integrite_cycle_suivant(
    integrite_contexte
):
    """
    B34 — Évalue l'intégrité sans démarrer
    ni exécuter aucune action.
    """

    if not isinstance(integrite_contexte, dict):
        return None

    return {
        "b33_valide": integrite_contexte.get(
            "b33_valide",
            False
        ),
        "integrite_cycle_suivant_validee":
            integrite_contexte.get(
                "integrite_cycle_suivant_validee",
                False
            ),
        "transition_globale_coherente":
            integrite_contexte.get(
                "transition_globale_coherente",
                False
            ),
        "cycle_precedent_termine":
            integrite_contexte.get(
                "cycle_precedent_termine",
                False
            ),
        "preparation_cycle_suivant_coherente":
            integrite_contexte.get(
                "preparation_cycle_suivant_coherente",
                False
            ),
        "nouveau_cycle_demarre":
            integrite_contexte.get(
                "nouveau_cycle_demarre",
                False
            ),
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_integrite_valide":
            integrite_contexte.get(
                "controle_integrite_valide",
                False
            ),
        "statut":
            integrite_contexte.get(
                "statut",
                "integrite_cycle_suivant_bloquee"
            )
    }


def mia30_resumer_integrite_cycle_suivant(
    integrite_contexte
):
    """
    B34 — Produit le résumé sécurisé du contrôle
    d'intégrité du cycle suivant.
    """

    evaluation = mia30_evaluer_integrite_cycle_suivant(
        integrite_contexte
    )

    if evaluation is None:
        return None

    return {
        "b33_valide":
            evaluation.get("b33_valide"),

        "integrite_cycle_suivant_validee":
            evaluation.get(
                "integrite_cycle_suivant_validee"
            ),

        "transition_globale_coherente":
            evaluation.get(
                "transition_globale_coherente"
            ),

        "cycle_precedent_termine":
            evaluation.get(
                "cycle_precedent_termine"
            ),

        "preparation_cycle_suivant_coherente":
            evaluation.get(
                "preparation_cycle_suivant_coherente"
            ),

        "nouveau_cycle_demarre":
            evaluation.get(
                "nouveau_cycle_demarre"
            ),

        "controle_integrite_valide":
            evaluation.get(
                "controle_integrite_valide"
            ),

        "statut":
            evaluation.get("statut"),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V30 — BRIQUE 34
# ============================================================

# ============================================================
# MIA V31 — BRIQUE 35
# CONTROLE DE COHERENCE POST-INTEGRITE
# ============================================================

def mia31_controler_coherence_post_integrite(
    coherence_post_integrite_contexte=None
):
    """
    B35 — Contrôle la cohérence de l'état après validation
    de l'intégrité par B34.

    La brique :
    - exige une intégrité du cycle suivant validée par B34 ;
    - exige une transition globale cohérente ;
    - exige que le cycle précédent soit terminé ;
    - exige une préparation cohérente du cycle suivant ;
    - vérifie qu'aucun nouveau cycle n'est démarré ;
    - interdit toute exécution automatique ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source.
    """

    contexte_valide = (
        isinstance(coherence_post_integrite_contexte, dict)
        and coherence_post_integrite_contexte.get(
            "controle_integrite_valide"
        ) is True
        and coherence_post_integrite_contexte.get(
            "integrite_cycle_suivant_validee"
        ) is True
        and coherence_post_integrite_contexte.get(
            "transition_globale_coherente"
        ) is True
        and coherence_post_integrite_contexte.get(
            "cycle_precedent_termine"
        ) is True
        and coherence_post_integrite_contexte.get(
            "preparation_cycle_suivant_coherente"
        ) is True
        and coherence_post_integrite_contexte.get(
            "nouveau_cycle_demarre"
        ) is False
        and coherence_post_integrite_contexte.get(
            "execution_autorisee"
        ) is False
        and coherence_post_integrite_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b34_valide": False,
            "coherence_post_integrite_validee": False,
            "integrite_cycle_suivant_validee": False,
            "transition_globale_coherente": False,
            "cycle_precedent_termine": False,
            "preparation_cycle_suivant_coherente": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "controle_coherence_post_integrite_valide": False,
            "statut": "coherence_post_integrite_bloquee"
        }

    return {
        "b34_valide": True,
        "coherence_post_integrite_validee": True,
        "integrite_cycle_suivant_validee": True,
        "transition_globale_coherente": True,
        "cycle_precedent_termine": True,
        "preparation_cycle_suivant_coherente": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "controle_coherence_post_integrite_valide": True,
        "statut": "coherence_post_integrite_validee"
    }


def mia31_evaluer_coherence_post_integrite(
    coherence_post_integrite_contexte=None
):
    """
    B35 — Évalue le résultat du contrôle de cohérence
    post-intégrité.
    """

    resultat = mia31_controler_coherence_post_integrite(
        coherence_post_integrite_contexte
    )

    return {
        "coherence_post_integrite_validee":
            resultat.get("coherence_post_integrite_validee") is True,
        "controle_coherence_post_integrite_valide":
            resultat.get("controle_coherence_post_integrite_valide") is True,
        "execution_autorisee":
            resultat.get("execution_autorisee") is True,
        "execution_interdite":
            resultat.get("execution_interdite") is True,
        "statut": resultat.get("statut")
    }


def mia31_resumer_coherence_post_integrite(
    coherence_post_integrite_contexte=None
):
    """
    B35 — Résume le contrôle de cohérence post-intégrité.
    """

    resultat = mia31_controler_coherence_post_integrite(
        coherence_post_integrite_contexte
    )

    return {
        "b34_valide": resultat.get("b34_valide") is True,
        "coherence_post_integrite_validee":
            resultat.get("coherence_post_integrite_validee") is True,
        "controle_coherence_post_integrite_valide":
            resultat.get("controle_coherence_post_integrite_valide") is True,
        "nouveau_cycle_demarre":
            resultat.get("nouveau_cycle_demarre") is True,
        "execution_autorisee":
            resultat.get("execution_autorisee") is True,
        "execution_interdite":
            resultat.get("execution_interdite") is True,
        "statut": resultat.get("statut")
    }

# ============================================================
# FIN MIA V31 — BRIQUE 35
# ============================================================

# ============================================================
# MIA V32 — BRIQUE 36
# VALIDATION FINALE DE LA TRANSITION VERS LE CYCLE SUIVANT
# ============================================================

def mia32_controler_validation_finale_transition_cycle_suivant(
    transition_finale_contexte=None
):
    """
    B36 — Validation finale de la chaîne de transition
    B30 → B31 → B32 → B33 → B34 → B35.

    Cette fonction :
    - exige la confirmation valide de B30 ;
    - exige la préparation valide de B31 ;
    - exige la cohérence validée de B32 ;
    - exige la cohérence globale validée de B33 ;
    - exige l'intégrité validée de B34 ;
    - exige la cohérence post-intégrité validée de B35 ;
    - vérifie que le cycle précédent est terminé ;
    - vérifie qu'aucun nouveau cycle n'est démarré ;
    - interdit toute exécution automatique ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation automatique.
    """

    contexte_valide = (
        isinstance(transition_finale_contexte, dict)

        and transition_finale_contexte.get(
            "confirmation_b30_valide"
        ) is True

        and transition_finale_contexte.get(
            "preparation_b31_valide"
        ) is True

        and transition_finale_contexte.get(
            "controle_b32_valide"
        ) is True

        and transition_finale_contexte.get(
            "controle_b33_valide"
        ) is True

        and transition_finale_contexte.get(
            "controle_b34_valide"
        ) is True

        and transition_finale_contexte.get(
            "controle_b35_valide"
        ) is True

        and transition_finale_contexte.get(
            "cycle_precedent_termine"
        ) is True

        and transition_finale_contexte.get(
            "nouveau_cycle_demarre"
        ) is False

        and transition_finale_contexte.get(
            "execution_autorisee"
        ) is False

        and transition_finale_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "chaine_b30_b35_valide": False,
            "confirmation_b30_valide": False,
            "preparation_b31_valide": False,
            "controle_b32_valide": False,
            "controle_b33_valide": False,
            "controle_b34_valide": False,
            "controle_b35_valide": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "validation_finale_transition_valide": False,
            "transition_suivante_admissible": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "validation_finale_transition_bloquee"
        }

    return {
        "chaine_b30_b35_valide": True,
        "confirmation_b30_valide": True,
        "preparation_b31_valide": True,
        "controle_b32_valide": True,
        "controle_b33_valide": True,
        "controle_b34_valide": True,
        "controle_b35_valide": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "validation_finale_transition_valide": True,
        "transition_suivante_admissible": True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "validation_finale_transition_validee"
    }


def mia32_evaluer_validation_finale_transition_cycle_suivant(
    transition_contexte=None
):
    """
    B36 — Évalue uniquement la validation finale
    de la transition sans exécuter aucune action.
    """

    if not isinstance(transition_contexte, dict):
        return None

    return {
        "chaine_b30_b35_valide":
            transition_contexte.get(
                "chaine_b30_b35_valide",
                False
            ),

        "confirmation_b30_valide":
            transition_contexte.get(
                "confirmation_b30_valide",
                False
            ),

        "preparation_b31_valide":
            transition_contexte.get(
                "preparation_b31_valide",
                False
            ),

        "controle_b32_valide":
            transition_contexte.get(
                "controle_b32_valide",
                False
            ),

        "controle_b33_valide":
            transition_contexte.get(
                "controle_b33_valide",
                False
            ),

        "controle_b34_valide":
            transition_contexte.get(
                "controle_b34_valide",
                False
            ),

        "controle_b35_valide":
            transition_contexte.get(
                "controle_b35_valide",
                False
            ),

        "cycle_precedent_termine":
            transition_contexte.get(
                "cycle_precedent_termine",
                False
            ),

        "nouveau_cycle_demarre":
            transition_contexte.get(
                "nouveau_cycle_demarre",
                False
            ),

        "validation_finale_transition_valide":
            transition_contexte.get(
                "validation_finale_transition_valide",
                False
            ),

        "transition_suivante_admissible":
            transition_contexte.get(
                "transition_suivante_admissible",
                False
            ),

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            transition_contexte.get(
                "statut",
                "validation_finale_transition_bloquee"
            )
    }


def mia32_resumer_validation_finale_transition_cycle_suivant(
    transition_contexte=None
):
    """
    B36 — Produit le résumé sécurisé de la validation
    finale de la transition vers le cycle suivant.
    """

    evaluation = (
        mia32_evaluer_validation_finale_transition_cycle_suivant(
            transition_contexte
        )
    )

    if evaluation is None:
        return None

    return {
        "chaine_b30_b35_valide":
            evaluation.get(
                "chaine_b30_b35_valide"
            ),

        "validation_finale_transition_valide":
            evaluation.get(
                "validation_finale_transition_valide"
            ),

        "transition_suivante_admissible":
            evaluation.get(
                "transition_suivante_admissible"
            ),

        "cycle_precedent_termine":
            evaluation.get(
                "cycle_precedent_termine"
            ),

        "nouveau_cycle_demarre":
            evaluation.get(
                "nouveau_cycle_demarre"
            ),

        "statut":
            evaluation.get(
                "statut"
            ),

        "execution_autorisee": False,
        "execution_interdite": True
    }


# ============================================================
# FIN MIA V32 — BRIQUE 36
# ============================================================


# ============================================================
# MIA V33 — BRIQUE 37
# CONTRÔLE D'OUVERTURE SÉCURISÉE DU CYCLE SUIVANT
# ============================================================

def mia33_controler_ouverture_cycle_suivant(
    ouverture_cycle_suivant_contexte=None
):
    """
    B37 — Contrôle l'admissibilité d'ouverture du cycle suivant.

    La brique :
    - exige la validation finale de B36 ;
    - exige que la transition suivante soit admissible ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit déjà démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B37 constate uniquement l'admissibilité.
    """

    contexte_valide = (
        isinstance(ouverture_cycle_suivant_contexte, dict)
        and ouverture_cycle_suivant_contexte.get(
            "validation_finale_transition_valide"
        ) is True
        and ouverture_cycle_suivant_contexte.get(
            "transition_suivante_admissible"
        ) is True
        and ouverture_cycle_suivant_contexte.get(
            "cycle_precedent_termine"
        ) is True
        and ouverture_cycle_suivant_contexte.get(
            "nouveau_cycle_demarre"
        ) is False
        and ouverture_cycle_suivant_contexte.get(
            "execution_autorisee"
        ) is False
        and ouverture_cycle_suivant_contexte.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b36_valide": False,
            "validation_finale_transition_valide": False,
            "transition_suivante_admissible": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "ouverture_cycle_suivant_validee": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "ouverture_cycle_suivant_bloquee"
        }

    return {
        "b36_valide": True,
        "validation_finale_transition_valide": True,
        "transition_suivante_admissible": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "ouverture_cycle_suivant_validee": True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "ouverture_cycle_suivant_validee"
    }


def mia33_evaluer_ouverture_cycle_suivant(
    ouverture_cycle_suivant_contexte=None
):
    """
    B37 — Évalue l'ouverture sans démarrer le cycle.
    """

    resultat = mia33_controler_ouverture_cycle_suivant(
        ouverture_cycle_suivant_contexte
    )

    return {
        "b36_valide":
            resultat.get("b36_valide") is True,
        "validation_finale_transition_valide":
            resultat.get(
                "validation_finale_transition_valide"
            ) is True,
        "transition_suivante_admissible":
            resultat.get(
                "transition_suivante_admissible"
            ) is True,
        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "ouverture_cycle_suivant_validee":
            resultat.get(
                "ouverture_cycle_suivant_validee"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


def mia33_resumer_ouverture_cycle_suivant(
    ouverture_cycle_suivant_contexte=None
):
    """
    B37 — Résumé sécurisé de l'ouverture du cycle suivant.
    """

    resultat = mia33_controler_ouverture_cycle_suivant(
        ouverture_cycle_suivant_contexte
    )

    return {
        "b36_valide":
            resultat.get("b36_valide") is True,
        "ouverture_cycle_suivant_validee":
            resultat.get(
                "ouverture_cycle_suivant_validee"
            ) is True,
        "transition_suivante_admissible":
            resultat.get(
                "transition_suivante_admissible"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


# ============================================================
# FIN MIA V33 — BRIQUE 37
# ============================================================

# ============================================================
# MIA V34 — BRIQUE 38
# PRÉPARATION SÉCURISÉE DU CONTEXTE DU CYCLE SUIVANT
# ============================================================

def mia34_preparer_contexte_cycle_suivant(
    contexte_ouverture_cycle_suivant=None
):
    """
    B38 — Prépare le contexte logique du cycle suivant.

    La brique :
    - exige la validation de B37 ;
    - exige que l'ouverture du cycle suivant soit validée ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit déjà démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B38 prépare uniquement un contexte logique sécurisé.
    """

    contexte_valide = (
        isinstance(contexte_ouverture_cycle_suivant, dict)
        and contexte_ouverture_cycle_suivant.get(
            "b36_valide"
        ) is True
        and contexte_ouverture_cycle_suivant.get(
            "validation_finale_transition_valide"
        ) is True
        and contexte_ouverture_cycle_suivant.get(
            "transition_suivante_admissible"
        ) is True
        and contexte_ouverture_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and contexte_ouverture_cycle_suivant.get(
            "ouverture_cycle_suivant_validee"
        ) is True
        and contexte_ouverture_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and contexte_ouverture_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and contexte_ouverture_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b37_valide": False,
            "ouverture_cycle_suivant_validee": False,
            "contexte_cycle_suivant_prepare": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "preparation_contexte_cycle_suivant_bloquee"
        }

    return {
        "b37_valide": True,
        "ouverture_cycle_suivant_validee": True,
        "contexte_cycle_suivant_prepare": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "contexte_cycle_suivant_prepare"
    }


def mia34_evaluer_contexte_cycle_suivant(
    contexte_ouverture_cycle_suivant=None
):
    """
    B38 — Évalue la préparation du contexte
    sans démarrer le cycle suivant.
    """

    resultat = mia34_preparer_contexte_cycle_suivant(
        contexte_ouverture_cycle_suivant
    )

    return {
        "b37_valide":
            resultat.get("b37_valide") is True,

        "ouverture_cycle_suivant_validee":
            resultat.get(
                "ouverture_cycle_suivant_validee"
            ) is True,

        "contexte_cycle_suivant_prepare":
            resultat.get(
                "contexte_cycle_suivant_prepare"
            ) is True,

        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


def mia34_resumer_contexte_cycle_suivant(
    contexte_ouverture_cycle_suivant=None
):
    """
    B38 — Résumé sécurisé de la préparation
    du contexte du cycle suivant.
    """

    resultat = mia34_preparer_contexte_cycle_suivant(
        contexte_ouverture_cycle_suivant
    )

    return {
        "b37_valide":
            resultat.get("b37_valide") is True,

        "ouverture_cycle_suivant_validee":
            resultat.get(
                "ouverture_cycle_suivant_validee"
            ) is True,

        "contexte_cycle_suivant_prepare":
            resultat.get(
                "contexte_cycle_suivant_prepare"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


# ============================================================
# FIN MIA V34 — BRIQUE 38
# ============================================================


# ============================================================
# MIA V34 — BRIQUE 39
# CONTRÔLE DE COHÉRENCE DU CONTEXTE DU CYCLE SUIVANT
# ============================================================

def mia34_controler_coherence_contexte_cycle_suivant(
    contexte_cycle_suivant=None
):
    """
    B39 — Contrôle la cohérence du contexte préparé par B38.

    La brique :
    - exige la validation de B37 ;
    - exige l'ouverture validée du cycle suivant ;
    - exige la préparation valide du contexte par B38 ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit déjà démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B39 contrôle uniquement la cohérence logique du contexte préparé.
    """

    contexte_valide = (
        isinstance(contexte_cycle_suivant, dict)
        and contexte_cycle_suivant.get(
            "b37_valide"
        ) is True
        and contexte_cycle_suivant.get(
            "ouverture_cycle_suivant_validee"
        ) is True
        and contexte_cycle_suivant.get(
            "contexte_cycle_suivant_prepare"
        ) is True
        and contexte_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and contexte_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and contexte_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and contexte_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b38_valide": False,
            "contexte_cycle_suivant_prepare": False,
            "coherence_contexte_cycle_suivant_validee": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "coherence_contexte_cycle_suivant_bloquee"
        }

    return {
        "b38_valide": True,
        "contexte_cycle_suivant_prepare": True,
        "coherence_contexte_cycle_suivant_validee": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "coherence_contexte_cycle_suivant_validee"
    }


def mia34_evaluer_coherence_contexte_cycle_suivant(
    contexte_cycle_suivant=None
):
    """
    B39 — Évalue la cohérence du contexte
    sans démarrer le cycle suivant.
    """

    resultat = mia34_controler_coherence_contexte_cycle_suivant(
        contexte_cycle_suivant
    )

    return {
        "b38_valide":
            resultat.get("b38_valide") is True,

        "contexte_cycle_suivant_prepare":
            resultat.get(
                "contexte_cycle_suivant_prepare"
            ) is True,

        "coherence_contexte_cycle_suivant_validee":
            resultat.get(
                "coherence_contexte_cycle_suivant_validee"
            ) is True,

        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


def mia34_resumer_coherence_contexte_cycle_suivant(
    contexte_cycle_suivant=None
):
    """
    B39 — Résumé sécurisé du contrôle de cohérence
    du contexte du cycle suivant.
    """

    resultat = mia34_controler_coherence_contexte_cycle_suivant(
        contexte_cycle_suivant
    )

    return {
        "b38_valide":
            resultat.get("b38_valide") is True,

        "coherence_contexte_cycle_suivant_validee":
            resultat.get(
                "coherence_contexte_cycle_suivant_validee"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


# ============================================================
# FIN MIA V34 — BRIQUE 39
# ============================================================

# ============================================================
# MIA V34 — BRIQUE 40
# CONTRÔLE D'INTÉGRITÉ DU CONTEXTE COHÉRENT
# ============================================================

def mia34_controler_integrite_contexte_cycle_suivant(
    contexte_coherent_cycle_suivant=None
):
    """
    B40 — Contrôle l'intégrité du contexte cohérent produit par B39.

    La brique :
    - exige la validation de B38 ;
    - exige la cohérence validée par B39 ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit déjà démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B40 contrôle uniquement l'intégrité logique du contexte.
    """

    contexte_valide = (
        isinstance(
            contexte_coherent_cycle_suivant,
            dict
        )
        and contexte_coherent_cycle_suivant.get(
            "b38_valide"
        ) is True
        and contexte_coherent_cycle_suivant.get(
            "contexte_cycle_suivant_prepare"
        ) is True
        and contexte_coherent_cycle_suivant.get(
            "coherence_contexte_cycle_suivant_validee"
        ) is True
        and contexte_coherent_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and contexte_coherent_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and contexte_coherent_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and contexte_coherent_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b39_valide": False,
            "coherence_contexte_cycle_suivant_validee": False,
            "integrite_contexte_cycle_suivant_validee": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "integrite_contexte_cycle_suivant_bloquee"
        }

    return {
        "b39_valide": True,
        "coherence_contexte_cycle_suivant_validee": True,
        "integrite_contexte_cycle_suivant_validee": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "integrite_contexte_cycle_suivant_validee"
    }


def mia34_evaluer_integrite_contexte_cycle_suivant(
    contexte_coherent_cycle_suivant=None
):
    """
    B40 — Évalue l'intégrité du contexte
    sans démarrer le cycle suivant.
    """

    resultat = mia34_controler_integrite_contexte_cycle_suivant(
        contexte_coherent_cycle_suivant
    )

    return {
        "b39_valide":
            resultat.get("b39_valide") is True,

        "coherence_contexte_cycle_suivant_validee":
            resultat.get(
                "coherence_contexte_cycle_suivant_validee"
            ) is True,

        "integrite_contexte_cycle_suivant_validee":
            resultat.get(
                "integrite_contexte_cycle_suivant_validee"
            ) is True,

        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


def mia34_resumer_integrite_contexte_cycle_suivant(
    contexte_coherent_cycle_suivant=None
):
    """
    B40 — Résumé sécurisé du contrôle d'intégrité
    du contexte cohérent du cycle suivant.
    """

    resultat = mia34_controler_integrite_contexte_cycle_suivant(
        contexte_coherent_cycle_suivant
    )

    return {
        "b39_valide":
            resultat.get("b39_valide") is True,

        "integrite_contexte_cycle_suivant_validee":
            resultat.get(
                "integrite_contexte_cycle_suivant_validee"
            ) is True,

        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,

        "execution_autorisee": False,
        "execution_interdite": True,

        "statut":
            resultat.get("statut")
    }


# ============================================================
# FIN MIA V34 — BRIQUE 40
# ============================================================

# ============================================================
# MIA V34 — BRIQUE 41
# VALIDATION FINALE D'INTÉGRITÉ DU CONTEXTE DU CYCLE SUIVANT
# ============================================================

def mia34_controler_validation_finale_integrite_contexte_cycle_suivant(
    contexte_integre_cycle_suivant=None
):
    """
    B41 — Valide définitivement l'intégrité du contexte produit par B40.

    La brique :
    - exige la validation de B40 ;
    - exige l'intégrité validée par B40 ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit déjà démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B41 effectue uniquement une validation logique finale sécurisée.
    """

    contexte_valide = (
        isinstance(contexte_integre_cycle_suivant, dict)
        and contexte_integre_cycle_suivant.get(
            "b39_valide"
        ) is True
        and contexte_integre_cycle_suivant.get(
            "integrite_contexte_cycle_suivant_validee"
        ) is True
        and contexte_integre_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and contexte_integre_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and contexte_integre_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and contexte_integre_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b40_valide": False,
            "integrite_contexte_cycle_suivant_validee": False,
            "validation_finale_integrite_contexte_validee": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut": "validation_finale_integrite_contexte_cycle_suivant_bloquee"
        }

    return {
        "b40_valide": True,
        "integrite_contexte_cycle_suivant_validee": True,
        "validation_finale_integrite_contexte_validee": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": "validation_finale_integrite_contexte_cycle_suivant_validee"
    }


def mia34_evaluer_validation_finale_integrite_contexte_cycle_suivant(
    contexte_integre_cycle_suivant=None
):
    """
    B41 — Évalue la validation finale d'intégrité
    sans démarrer le cycle suivant.
    """

    resultat = (
        mia34_controler_validation_finale_integrite_contexte_cycle_suivant(
            contexte_integre_cycle_suivant
        )
    )

    return {
        "b40_valide": resultat.get("b40_valide") is True,
        "integrite_contexte_cycle_suivant_validee":
            resultat.get(
                "integrite_contexte_cycle_suivant_validee"
            ) is True,
        "validation_finale_integrite_contexte_validee":
            resultat.get(
                "validation_finale_integrite_contexte_validee"
            ) is True,
        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


def mia34_resumer_validation_finale_integrite_contexte_cycle_suivant(
    contexte_integre_cycle_suivant=None
):
    """
    B41 — Résumé sécurisé de la validation finale
    d'intégrité du contexte du cycle suivant.
    """

    resultat = (
        mia34_controler_validation_finale_integrite_contexte_cycle_suivant(
            contexte_integre_cycle_suivant
        )
    )

    return {
        "b40_valide":
            resultat.get("b40_valide") is True,
        "validation_finale_integrite_contexte_validee":
            resultat.get(
                "validation_finale_integrite_contexte_validee"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


# ============================================================
# FIN MIA V34 — BRIQUE 41
# ============================================================



# ============================================================
# MIA V35 — BRIQUE 42
# SCELLEMENT SECURISE DU CONTEXTE VALIDE DU CYCLE SUIVANT
# ============================================================

def mia35_controler_scellement_contexte_cycle_suivant(
    validation_finale_contexte_cycle_suivant=None
):
    """
    B42 — Scelle logiquement le contexte validé par B41.

    La brique :
    - exige la validation de B40 ;
    - exige l'intégrité validée du contexte ;
    - exige la validation finale de B41 ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B42 effectue uniquement un scellement logique sécurisé.
    """

    contexte_valide = (
        isinstance(
            validation_finale_contexte_cycle_suivant,
            dict
        )
        and validation_finale_contexte_cycle_suivant.get(
            "b40_valide"
        ) is True
        and validation_finale_contexte_cycle_suivant.get(
            "integrite_contexte_cycle_suivant_validee"
        ) is True
        and validation_finale_contexte_cycle_suivant.get(
            "validation_finale_integrite_contexte_validee"
        ) is True
        and validation_finale_contexte_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and validation_finale_contexte_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and validation_finale_contexte_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and validation_finale_contexte_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b41_valide": False,
            "validation_finale_integrite_contexte_validee": False,
            "scellement_contexte_cycle_suivant_valide": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut":
                "scellement_contexte_cycle_suivant_bloque"
        }

    return {
        "b41_valide": True,
        "validation_finale_integrite_contexte_validee": True,
        "scellement_contexte_cycle_suivant_valide": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut":
            "scellement_contexte_cycle_suivant_valide"
    }


def mia35_evaluer_scellement_contexte_cycle_suivant(
    validation_finale_contexte_cycle_suivant=None
):
    """
    B42 — Évalue le scellement logique du contexte
    sans démarrer le cycle suivant.
    """

    resultat = (
        mia35_controler_scellement_contexte_cycle_suivant(
            validation_finale_contexte_cycle_suivant
        )
    )

    return {
        "b41_valide":
            resultat.get("b41_valide") is True,
        "validation_finale_integrite_contexte_validee":
            resultat.get(
                "validation_finale_integrite_contexte_validee"
            ) is True,
        "scellement_contexte_cycle_suivant_valide":
            resultat.get(
                "scellement_contexte_cycle_suivant_valide"
            ) is True,
        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


def mia35_resumer_scellement_contexte_cycle_suivant(
    validation_finale_contexte_cycle_suivant=None
):
    """
    B42 — Résumé sécurisé du scellement du contexte
    validé par B41.
    """

    resultat = (
        mia35_controler_scellement_contexte_cycle_suivant(
            validation_finale_contexte_cycle_suivant
        )
    )

    return {
        "b41_valide":
            resultat.get("b41_valide") is True,
        "scellement_contexte_cycle_suivant_valide":
            resultat.get(
                "scellement_contexte_cycle_suivant_valide"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


# ============================================================
# FIN MIA V35 — BRIQUE 42
# ============================================================

# ============================================================
# MIA V35 — BRIQUE 43
# CONTROLE DE CONFORMITE DU SCELLEMENT DU CONTEXTE
# ============================================================

def mia35_controler_conformite_scellement_contexte_cycle_suivant(
    scellement_contexte_cycle_suivant=None
):
    """
    B43 — Contrôle la conformité du scellement validé par B42.

    La brique :
    - exige la validation de B41 ;
    - exige la validation du scellement B42 ;
    - exige que le cycle précédent soit terminé ;
    - exige qu'aucun nouveau cycle ne soit démarré ;
    - interdit toute exécution automatique ;
    - ne démarre aucun nouveau cycle ;
    - ne déclenche aucune action ;
    - ne modifie aucune donnée source ;
    - ne crée aucune autorisation d'exécution.

    B43 effectue uniquement un contrôle logique sécurisé.
    """

    contexte_valide = (
        isinstance(
            scellement_contexte_cycle_suivant,
            dict
        )
        and scellement_contexte_cycle_suivant.get(
            "b41_valide"
        ) is True
        and scellement_contexte_cycle_suivant.get(
            "scellement_contexte_cycle_suivant_valide"
        ) is True
        and scellement_contexte_cycle_suivant.get(
            "cycle_precedent_termine"
        ) is True
        and scellement_contexte_cycle_suivant.get(
            "nouveau_cycle_demarre"
        ) is False
        and scellement_contexte_cycle_suivant.get(
            "execution_autorisee"
        ) is False
        and scellement_contexte_cycle_suivant.get(
            "execution_interdite"
        ) is True
    )

    if not contexte_valide:
        return {
            "b42_valide": False,
            "scellement_contexte_cycle_suivant_valide": False,
            "conformite_scellement_contexte_cycle_suivant_validee": False,
            "cycle_precedent_termine": False,
            "nouveau_cycle_demarre": False,
            "execution_autorisee": False,
            "execution_interdite": True,
            "statut":
                "conformite_scellement_contexte_cycle_suivant_bloquee"
        }

    return {
        "b42_valide": True,
        "scellement_contexte_cycle_suivant_valide": True,
        "conformite_scellement_contexte_cycle_suivant_validee": True,
        "cycle_precedent_termine": True,
        "nouveau_cycle_demarre": False,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut":
            "conformite_scellement_contexte_cycle_suivant_validee"
    }


def mia35_evaluer_conformite_scellement_contexte_cycle_suivant(
    scellement_contexte_cycle_suivant=None
):
    """
    B43 — Évalue la conformité du scellement
    sans démarrer le cycle suivant.
    """

    resultat = (
        mia35_controler_conformite_scellement_contexte_cycle_suivant(
            scellement_contexte_cycle_suivant
        )
    )

    return {
        "b42_valide":
            resultat.get("b42_valide") is True,
        "scellement_contexte_cycle_suivant_valide":
            resultat.get(
                "scellement_contexte_cycle_suivant_valide"
            ) is True,
        "conformite_scellement_contexte_cycle_suivant_validee":
            resultat.get(
                "conformite_scellement_contexte_cycle_suivant_validee"
            ) is True,
        "cycle_precedent_termine":
            resultat.get(
                "cycle_precedent_termine"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


def mia35_resumer_conformite_scellement_contexte_cycle_suivant(
    scellement_contexte_cycle_suivant=None
):
    """
    B43 — Résumé sécurisé du contrôle de conformité
    du scellement produit par B42.
    """

    resultat = (
        mia35_controler_conformite_scellement_contexte_cycle_suivant(
            scellement_contexte_cycle_suivant
        )
    )

    return {
        "b42_valide":
            resultat.get("b42_valide") is True,
        "conformite_scellement_contexte_cycle_suivant_validee":
            resultat.get(
                "conformite_scellement_contexte_cycle_suivant_validee"
            ) is True,
        "nouveau_cycle_demarre":
            resultat.get(
                "nouveau_cycle_demarre"
            ) is True,
        "execution_autorisee": False,
        "execution_interdite": True,
        "statut": resultat.get("statut")
    }


# ============================================================
# FIN MIA V35 — BRIQUE 43
# ============================================================

# ============================================================
# MIA V36 — IMPORTATION LOCALE TXT / MD
# ============================================================

def mia36_importer_fichier(chemin, type_souvenir="connaissance", importance=3):
    """
    Importe un fichier TXT ou MD dans la table documents.
    Ne modifie aucune table existante.
    """

    if not isinstance(chemin, str) or not chemin.strip():
        return {"statut": "erreur", "raison": "chemin_invalide"}

    chemin = os.path.abspath(os.path.expanduser(chemin))

    if not os.path.isfile(chemin):
        return {"statut": "erreur", "raison": "fichier_introuvable"}

    extension = os.path.splitext(chemin)[1].lower()

    if extension not in (".txt", ".md"):
        return {
            "statut": "erreur",
            "raison": "format_non_supporte",
            "format": extension
        }

    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
    except Exception as e:
        return {
            "statut": "erreur",
            "raison": "lecture_impossible",
            "detail": str(e)
        }

    contenu = contenu.strip()

    if not contenu:
        return {"statut": "erreur", "raison": "fichier_vide"}

    titre = os.path.splitext(os.path.basename(chemin))[0]
    now = datetime.datetime.now().isoformat()

    try:
        importance = int(importance)
    except (TypeError, ValueError):
        importance = 3

    if importance < 1 or importance > 5:
        importance = 3

    c = sqlite3.connect(DB)

    c.execute(
        """
        INSERT INTO documents
        (title, content, source, created_at, updated_at, type, importance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            titre,
            contenu,
            os.path.basename(chemin),
            now,
            now,
            type_souvenir,
            importance
        )
    )

    document_id = c.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    c.commit()
    c.close()

    return {
        "statut": "importe",
        "document_id": document_id,
        "titre": titre,
        "source": os.path.basename(chemin),
        "type": type_souvenir,
        "importance": importance,
        "taille": len(contenu)
    }


# ============================================================
# MIA V36 — IMPORTATION LOCALE TXT / MD
# ============================================================


# ============================================================
# MIA V37 — CONTROLE DES DOUBLONS AVANT IMPORTATION
# ============================================================

def mia37_verifier_doublon_fichier(chemin):
    """
    Vérifie si un fichier TXT ou MD est déjà présent dans documents.
    Ne modifie aucune donnée.
    """

    if not isinstance(chemin, str) or not chemin.strip():
        return {
            "statut": "erreur",
            "raison": "chemin_invalide"
        }

    chemin = os.path.abspath(os.path.expanduser(chemin))

    if not os.path.isfile(chemin):
        return {
            "statut": "erreur",
            "raison": "fichier_introuvable"
        }

    extension = os.path.splitext(chemin)[1].lower()

    if extension not in (".txt", ".md"):
        return {
            "statut": "erreur",
            "raison": "format_non_supporte"
        }

    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read().strip()
    except Exception as e:
        return {
            "statut": "erreur",
            "raison": "lecture_impossible",
            "detail": str(e)
        }

    if not contenu:
        return {
            "statut": "erreur",
            "raison": "fichier_vide"
        }

    nom = os.path.basename(chemin)

    c = sqlite3.connect(DB)

    resultat = c.execute(
        """
        SELECT id, title, source, type, statut, importance
        FROM documents
        WHERE source=? AND content=?
        LIMIT 1
        """,
        (nom, contenu)
    ).fetchone()

    c.close()

    if resultat:
        return {
            "statut": "doublon",
            "document_id": resultat[0],
            "titre": resultat[1],
            "source": resultat[2],
            "type": resultat[3],
            "statut_document": resultat[4],
            "importance": resultat[5]
        }

    return {
        "statut": "nouveau",
        "source": nom,
        "taille": len(contenu)
    }


# ============================================================
# MIA V38 — IMPORTATION SECURISEE SANS DOUBLON
# ============================================================

def mia38_importer_fichier_securise(
    chemin,
    type_souvenir="connaissance",
    importance=3
):
    """
    Importe un fichier TXT ou MD uniquement s'il n'existe pas déjà.
    Utilise le contrôle V37 puis l'importation V36.
    Ne modifie aucune table.
    """

    controle = mia37_verifier_doublon_fichier(chemin)

    if controle.get("statut") == "doublon":
        return {
            "statut": "non_importe",
            "raison": "doublon",
            "document_id": controle.get("document_id"),
            "titre": controle.get("titre"),
            "source": controle.get("source")
        }

    if controle.get("statut") != "nouveau":
        return controle

    resultat = mia36_importer_fichier(
        chemin,
        type_souvenir=type_souvenir,
        importance=importance
    )

    if resultat.get("statut") != "importe":
        return resultat

    return {
        "statut": "importe_securise",
        "document_id": resultat.get("document_id"),
        "titre": resultat.get("titre"),
        "source": resultat.get("source"),
        "type": resultat.get("type"),
        "importance": resultat.get("importance"),
        "taille": resultat.get("taille")
    }


# ============================================================
# MIA V39.1 — MEMOIRE EVOLUTIVE
# ============================================================

def mia39_enregistrer_evolution(
    titre,
    contenu,
    source="ALKAH-BRAIN",
    type_souvenir="connaissance",
    importance=3
):
    """
    Enregistre une nouvelle évolution d'une connaissance
    sans supprimer les connaissances précédentes.
    """

    if not isinstance(titre, str) or not titre.strip():
        return {
            "statut": "erreur",
            "raison": "titre_invalide"
        }

    if not isinstance(contenu, str) or not contenu.strip():
        return {
            "statut": "erreur",
            "raison": "contenu_invalide"
        }

    try:
        importance = int(importance)
    except (TypeError, ValueError):
        importance = 3

    if importance < 1 or importance > 5:
        importance = 3

    now = datetime.datetime.now().isoformat()

    c = sqlite3.connect(DB)

    c.execute(
        """
        INSERT INTO documents
        (title, content, source, created_at, updated_at, type, importance)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            titre.strip(),
            contenu.strip(),
            source,
            now,
            now,
            type_souvenir,
            importance
        )
    )

    document_id = c.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    c.commit()
    c.close()

    return {
        "statut": "evolution_enregistree",
        "document_id": document_id,
        "titre": titre.strip(),
        "source": source,
        "type": type_souvenir,
        "importance": importance
    }


# ============================================================
# MIA V39.2 — TRAÇABILITE DE L'EVOLUTION DES CONNAISSANCES
# ============================================================

def mia39_lier_evolution(document_id_ancien, document_id_nouveau):
    """
    Lie une nouvelle connaissance à la connaissance précédente.

    Utilise la table relations existante.
    Ne modifie ni ne supprime les documents.
    """

    if not isinstance(document_id_ancien, int):
        return {
            "statut": "erreur",
            "raison": "ancien_id_invalide"
        }

    if not isinstance(document_id_nouveau, int):
        return {
            "statut": "erreur",
            "raison": "nouveau_id_invalide"
        }

    if document_id_ancien == document_id_nouveau:
        return {
            "statut": "erreur",
            "raison": "meme_document"
        }

    c = sqlite3.connect(DB)

    ancien = c.execute(
        "SELECT id FROM documents WHERE id=?",
        (document_id_ancien,)
    ).fetchone()

    nouveau = c.execute(
        "SELECT id FROM documents WHERE id=?",
        (document_id_nouveau,)
    ).fetchone()

    if not ancien:
        c.close()
        return {
            "statut": "erreur",
            "raison": "ancien_document_introuvable"
        }

    if not nouveau:
        c.close()
        return {
            "statut": "erreur",
            "raison": "nouveau_document_introuvable"
        }

    relation_existante = c.execute(
        """
        SELECT id
        FROM relations
        WHERE source_id=?
          AND relation=?
          AND target_id=?
        LIMIT 1
        """,
        (
            document_id_ancien,
            "evolution_vers",
            document_id_nouveau
        )
    ).fetchone()

    if relation_existante:
        c.close()
        return {
            "statut": "deja_lie",
            "relation_id": relation_existante[0]
        }

    now = datetime.datetime.now().isoformat()

    c.execute(
        """
        INSERT INTO relations
        (source_id, relation, target_id, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            document_id_ancien,
            "evolution_vers",
            document_id_nouveau,
            now
        )
    )

    relation_id = c.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    c.commit()
    c.close()

    return {
        "statut": "evolution_liee",
        "relation_id": relation_id,
        "ancien_document_id": document_id_ancien,
        "nouveau_document_id": document_id_nouveau,
        "relation": "evolution_vers"
    }


# ============================================================
# MIA V39.3 — LECTURE DE L'HISTORIQUE D'EVOLUTION
# ============================================================

def mia39_lire_historique(document_id):
    """
    Lit les versions précédentes et suivantes d'une connaissance.
    Ne modifie aucune donnée.
    """

    if not isinstance(document_id, int):
        return {
            "statut": "erreur",
            "raison": "document_id_invalide"
        }

    c = sqlite3.connect(DB)

    document = c.execute(
        """
        SELECT id, title, content, source, type, statut, importance,
               created_at, updated_at
        FROM documents
        WHERE id=?
        """,
        (document_id,)
    ).fetchone()

    if not document:
        c.close()
        return {
            "statut": "erreur",
            "raison": "document_introuvable"
        }

    precedentes = c.execute(
        """
        SELECT d.id, d.title, d.content, d.source,
               d.type, d.statut, d.importance,
               d.created_at, d.updated_at
        FROM relations r
        JOIN documents d ON r.source_id = d.id
        WHERE r.target_id=?
          AND r.relation='evolution_vers'
        ORDER BY d.id
        """,
        (document_id,)
    ).fetchall()

    suivantes = c.execute(
        """
        SELECT d.id, d.title, d.content, d.source,
               d.type, d.statut, d.importance,
               d.created_at, d.updated_at
        FROM relations r
        JOIN documents d ON r.target_id = d.id
        WHERE r.source_id=?
          AND r.relation='evolution_vers'
        ORDER BY d.id
        """,
        (document_id,)
    ).fetchall()

    c.close()

    historique = []

    for ligne in precedentes:
        historique.append({
            "id": ligne[0],
            "titre": ligne[1],
            "contenu": ligne[2],
            "source": ligne[3],
            "type": ligne[4],
            "statut": ligne[5],
            "importance": ligne[6],
            "created_at": ligne[7],
            "updated_at": ligne[8],
            "position": "precedente"
        })

    historique.append({
        "id": document[0],
        "titre": document[1],
        "contenu": document[2],
        "source": document[3],
        "type": document[4],
        "statut": document[5],
        "importance": document[6],
        "created_at": document[7],
        "updated_at": document[8],
        "position": "actuelle"
    })

    for ligne in suivantes:
        historique.append({
            "id": ligne[0],
            "titre": ligne[1],
            "contenu": ligne[2],
            "source": ligne[3],
            "type": ligne[4],
            "statut": ligne[5],
            "importance": ligne[6],
            "created_at": ligne[7],
            "updated_at": ligne[8],
            "position": "suivante"
        })

    return {
        "statut": "historique_lu",
        "document_id": document_id,
        "nombre_versions": len(historique),
        "historique": historique
    }


# ============================================================
# MIA V39.4 — IDENTIFICATION DE LA VERSION ACTUELLE
# ============================================================

def mia39_identifier_version_actuelle(document_id):
    """
    Identifie la version la plus récente d'une connaissance
    à partir des relations evolution_vers.
    Ne modifie aucune donnée.
    """

    if not isinstance(document_id, int):
        return {
            "statut": "erreur",
            "raison": "document_id_invalide"
        }

    c = sqlite3.connect(DB)

    document = c.execute(
        """
        SELECT id, title, content, source, type, statut, importance,
               created_at, updated_at
        FROM documents
        WHERE id=?
        """,
        (document_id,)
    ).fetchone()

    if not document:
        c.close()
        return {
            "statut": "erreur",
            "raison": "document_introuvable"
        }

    actuel = document

    visites = set()
    courant_id = document_id

    while courant_id not in visites:
        visites.add(courant_id)

        suivant = c.execute(
            """
            SELECT d.id, d.title, d.content, d.source,
                   d.type, d.statut, d.importance,
                   d.created_at, d.updated_at
            FROM relations r
            JOIN documents d ON r.target_id = d.id
            WHERE r.source_id=?
              AND r.relation='evolution_vers'
            ORDER BY d.id DESC
            LIMIT 1
            """,
            (courant_id,)
        ).fetchone()

        if not suivant:
            break

        actuel = suivant
        courant_id = suivant[0]

    c.close()

    return {
        "statut": "version_actuelle_identifiee",
        "document_demande": document_id,
        "version_actuelle": {
            "id": actuel[0],
            "titre": actuel[1],
            "contenu": actuel[2],
            "source": actuel[3],
            "type": actuel[4],
            "statut": actuel[5],
            "importance": actuel[6],
            "created_at": actuel[7],
            "updated_at": actuel[8]
        },
        "nombre_versions_parcourues": len(visites)
    }


# ============================================================
# MIA V40 — RESUME STRUCTURE DE L'EVOLUTION
# ============================================================

def mia40_resumer_evolution(document_id):
    """
    Produit un résumé structuré de l'évolution d'une connaissance.
    Utilise l'historique V39.3.
    Ne modifie aucune donnée.
    """

    historique = mia39_lire_historique(document_id)

    if historique.get("statut") != "historique_lu":
        return historique

    versions = historique.get("historique", [])

    if not versions:
        return {
            "statut": "erreur",
            "raison": "historique_vide"
        }

    premiere = versions[0]
    actuelle = None

    for version in versions:
        if version.get("position") == "actuelle":
            actuelle = version
            break

    if actuelle is None:
        actuelle = versions[-1]

    evolution = []

    for version in versions:
        evolution.append({
            "id": version.get("id"),
            "titre": version.get("titre"),
            "contenu": version.get("contenu"),
            "source": version.get("source"),
            "importance": version.get("importance"),
            "position": version.get("position"),
            "created_at": version.get("created_at")
        })

    return {
        "statut": "resume_evolution_genere",
        "document_id": document_id,
        "nombre_versions": len(versions),
        "premiere_version": {
            "id": premiere.get("id"),
            "titre": premiere.get("titre"),
            "created_at": premiere.get("created_at")
        },
        "version_actuelle": {
            "id": actuelle.get("id"),
            "titre": actuelle.get("titre"),
            "contenu": actuelle.get("contenu"),
            "importance": actuelle.get("importance"),
            "updated_at": actuelle.get("updated_at")
        },
        "evolution": evolution
    }


# ============================================================
# MIA V40.1 — CORRECTION DE LA VERSION ACTUELLE
# ============================================================

def mia40_1_resumer_evolution(document_id):
    """
    Produit un résumé cohérent de l'évolution d'une connaissance.
    Utilise V39.3 pour l'historique et V39.4 pour identifier
    la dernière version.
    Ne modifie aucune donnée.
    """

    historique = mia39_lire_historique(document_id)

    if historique.get("statut") != "historique_lu":
        return historique

    versions = historique.get("historique", [])

    if not versions:
        return {
            "statut": "erreur",
            "raison": "historique_vide"
        }

    actuelle_resultat = mia39_identifier_version_actuelle(document_id)

    if actuelle_resultat.get("statut") != "version_actuelle_identifiee":
        return actuelle_resultat

    actuelle = actuelle_resultat.get("version_actuelle", {})

    evolution = []

    for version in versions:
        position = "historique"

        if version.get("id") == actuelle.get("id"):
            position = "actuelle"

        evolution.append({
            "id": version.get("id"),
            "titre": version.get("titre"),
            "contenu": version.get("contenu"),
            "source": version.get("source"),
            "importance": version.get("importance"),
            "position": position,
            "created_at": version.get("created_at")
        })

    premiere = versions[0]

    return {
        "statut": "resume_evolution_genere",
        "document_id": document_id,
        "nombre_versions": len(versions),
        "premiere_version": {
            "id": premiere.get("id"),
            "titre": premiere.get("titre"),
            "created_at": premiere.get("created_at")
        },
        "version_actuelle": {
            "id": actuelle.get("id"),
            "titre": actuelle.get("titre"),
            "contenu": actuelle.get("contenu"),
            "importance": actuelle.get("importance"),
            "updated_at": actuelle.get("updated_at")
        },
        "evolution": evolution
    }


# ============================================================
# MIA V41 — DETECTION D'ACTUALISATION D'UNE CONNAISSANCE
# ============================================================

def mia41_detecter_actualisation(titre, contenu, seuil_similarite=95):
    """
    Détermine si une information est nouvelle, identique
    ou constitue une évolution d'une connaissance existante.

    Ne modifie aucune donnée.
    """

    if not isinstance(titre, str) or not titre.strip():
        return {
            "statut": "erreur",
            "raison": "titre_invalide"
        }

    if not isinstance(contenu, str) or not contenu.strip():
        return {
            "statut": "erreur",
            "raison": "contenu_invalide"
        }

    try:
        seuil_similarite = float(seuil_similarite)
    except (TypeError, ValueError):
        seuil_similarite = 95

    c = sqlite3.connect(DB)

    candidats = c.execute(
        """
        SELECT id, title, content, source, type, statut, importance
        FROM documents
        WHERE title=?
        ORDER BY id DESC
        """,
        (titre.strip(),)
    ).fetchall()

    c.close()

    if not candidats:
        return {
            "statut": "nouvelle",
            "raison": "aucune_connaissance_correspondante",
            "titre": titre.strip()
        }

    meilleur = None
    meilleure_similarite = -1

    for candidat in candidats:
        score = calculer_similarite_document(
            titre.strip(),
            contenu.strip(),
            candidat[1],
            candidat[2]
        )

        try:
            score = float(score)
        except (TypeError, ValueError):
            continue

        if score > meilleure_similarite:
            meilleure_similarite = score
            meilleur = candidat

    if meilleur is None:
        return {
            "statut": "a_verifier",
            "raison": "comparaison_impossible",
            "titre": titre.strip()
        }

    if meilleure_similarite >= seuil_similarite:
        statut = "identique"
    else:
        statut = "evolution"

    return {
        "statut": statut,
        "titre": titre.strip(),
        "document_existant": {
            "id": meilleur[0],
            "titre": meilleur[1],
            "contenu": meilleur[2],
            "source": meilleur[3],
            "type": meilleur[4],
            "statut": meilleur[5],
            "importance": meilleur[6]
        },
        "similarite": meilleure_similarite,
        "seuil": seuil_similarite
    }


# ============================================================
# MIA V42.1 — COMPARATEUR DE STRATEGIES
# ============================================================

def mia42_comparer_strategies(strategies):
    """
    Compare plusieurs stratégies de manière déterministe
    et transparente.

    Chaque stratégie doit contenir :
    - nom
    - avantages
    - inconvenients

    Ne modifie aucune donnée.
    """

    if not isinstance(strategies, list):
        return {
            "statut": "erreur",
            "raison": "strategies_invalides"
        }

    if len(strategies) < 2:
        return {
            "statut": "erreur",
            "raison": "au_moins_deux_strategies_requises"
        }

    resultat = []

    for index, strategie in enumerate(strategies, 1):

        if not isinstance(strategie, dict):
            continue

        nom = strategie.get("nom", "")
        avantages = strategie.get("avantages", [])
        inconvenients = strategie.get("inconvenients", [])

        if not isinstance(nom, str) or not nom.strip():
            continue

        if not isinstance(avantages, list):
            avantages = []

        if not isinstance(inconvenients, list):
            inconvenients = []

        resultat.append({
            "rang_entree": index,
            "nom": nom.strip(),
            "nombre_avantages": len(avantages),
            "nombre_inconvenients": len(inconvenients),
            "avantages": avantages,
            "inconvenients": inconvenients
        })

    if len(resultat) < 2:
        return {
            "statut": "erreur",
            "raison": "strategies_insuffisantes"
        }

    return {
        "statut": "comparaison_strategies_generee",
        "nombre_strategies": len(resultat),
        "strategies": resultat
    }


# ============================================================
# MIA V42.2 — EVALUATION TRANSPARENTE DES STRATEGIES
# ============================================================

def mia42_2_evaluer_strategies(strategies):
    """
    Evalue plusieurs stratégies avec un score simple et
    transparent basé sur le nombre d'avantages et
    d'inconvénients.

    Le calcul ne constitue pas une décision automatique.
    La décision finale reste humaine.

    Ne modifie aucune donnée.
    """

    comparaison = mia42_comparer_strategies(strategies)

    if comparaison.get("statut") != "comparaison_strategies_generee":
        return comparaison

    resultats = []

    for strategie in comparaison.get("strategies", []):

        avantages = strategie.get("nombre_avantages", 0)
        inconvenients = strategie.get("nombre_inconvenients", 0)

        score = avantages - inconvenients

        if score > 0:
            evaluation = "favorable"
        elif score < 0:
            evaluation = "defavorable"
        else:
            evaluation = "equilibree"

        resultats.append({
            "rang_entree": strategie.get("rang_entree"),
            "nom": strategie.get("nom"),
            "avantages": avantages,
            "inconvenients": inconvenients,
            "score": score,
            "evaluation": evaluation
        })

    return {
        "statut": "evaluation_strategies_generee",
        "nombre_strategies": len(resultats),
        "methode": "avantages_moins_inconvenients",
        "decision_automatique": False,
        "strategies": resultats
    }


# ============================================================
# MIA V43 — CLASSEMENT TRANSPARENT DES STRATEGIES
# ============================================================

def mia43_classer_strategies(strategies):
    """
    Classe les stratégies selon leur score d'évaluation.

    Utilise V42.2.
    Le classement est déterministe et transparent.
    MIA ne prend pas automatiquement la décision finale.

    Ne modifie aucune donnée.
    """

    evaluation = mia42_2_evaluer_strategies(strategies)

    if evaluation.get("statut") != "evaluation_strategies_generee":
        return evaluation

    classees = list(evaluation.get("strategies", []))

    classees.sort(
        key=lambda strategie: (
            strategie.get("score", 0),
            -strategie.get("rang_entree", 0)
        ),
        reverse=True
    )

    for rang, strategie in enumerate(classees, 1):
        strategie["rang"] = rang

    recommandation = None

    if classees:
        meilleure = classees[0]

        recommandation = {
            "nom": meilleure.get("nom"),
            "score": meilleure.get("score"),
            "evaluation": meilleure.get("evaluation"),
            "base": "score_transparent",
            "decision_automatique": False
        }

    return {
        "statut": "classement_strategies_genere",
        "nombre_strategies": len(classees),
        "methode": "classement_par_score",
        "decision_automatique": False,
        "recommandation": recommandation,
        "strategies": classees
    }


# ============================================================
# MIA V44 — SYNTHESE TRANSPARENTE DE DECISION
# ============================================================

def mia44_synthetiser_decision(strategies):
    """
    Produit une synthèse structurée à partir du classement V43.

    MIA présente une recommandation et les alternatives.
    La décision finale reste humaine.

    Ne modifie aucune donnée.
    """

    classement = mia43_classer_strategies(strategies)

    if classement.get("statut") != "classement_strategies_genere":
        return classement

    classees = classement.get("strategies", [])
    recommandation = classement.get("recommandation")

    alternatives = []

    for strategie in classees:
        if (
            recommandation
            and strategie.get("nom") == recommandation.get("nom")
        ):
            continue

        alternatives.append({
            "rang": strategie.get("rang"),
            "nom": strategie.get("nom"),
            "score": strategie.get("score"),
            "evaluation": strategie.get("evaluation")
        })

    return {
        "statut": "synthese_decision_generee",
        "nombre_strategies": len(classees),
        "methode": "synthese_du_classement_v43",
        "recommandation": recommandation,
        "alternatives": alternatives,
        "decision_automatique": False
    }


# ============================================================
# MIA V45 — EXPLICATION DE LA RECOMMANDATION
# ============================================================

def mia45_expliquer_recommandation(strategies):
    """
    Explique de manière transparente pourquoi une stratégie
    est recommandée.

    Utilise la synthèse V44.
    Ne crée pas de nouveau score.
    Ne prend pas de décision automatique.
    Ne modifie aucune donnée.
    """

    synthese = mia44_synthetiser_decision(strategies)

    if synthese.get("statut") != "synthese_decision_generee":
        return synthese

    recommandation = synthese.get("recommandation")

    if not recommandation:
        return {
            "statut": "erreur",
            "raison": "recommandation_absente"
        }

    alternatives = synthese.get("alternatives", [])

    raisons = [
        "strategie_classee_en_premiere_position",
        "score_le_plus_eleve",
        "evaluation_favorable"
    ]

    return {
        "statut": "explication_recommandation_generee",
        "strategie_recommandee": recommandation.get("nom"),
        "score": recommandation.get("score"),
        "evaluation": recommandation.get("evaluation"),
        "raisons": raisons,
        "nombre_alternatives": len(alternatives),
        "decision_automatique": False
    }


# ============================================================
# MIA V46 — STRUCTURE COMMUNE D'UNE CONNAISSANCE MULTIMODALE
# ============================================================

def mia46_structurer_connaissance_multimodale(
    titre,
    contenu,
    modalite="texte",
    source=None,
    metadata=None
):
    """
    Prépare une connaissance multimodale dans une structure
    commune et transparente.

    Modalités prévues :
    texte, document, image, audio, video.

    Cette fonction ne modifie aucune donnée.
    """

    modalites_valides = {
        "texte",
        "document",
        "image",
        "audio",
        "video"
    }

    if not isinstance(titre, str) or not titre.strip():
        return {
            "statut": "erreur",
            "raison": "titre_invalide"
        }

    if not isinstance(contenu, str) or not contenu.strip():
        return {
            "statut": "erreur",
            "raison": "contenu_invalide"
        }

    if not isinstance(modalite, str):
        return {
            "statut": "erreur",
            "raison": "modalite_invalide"
        }

    modalite = modalite.strip().lower()

    if modalite not in modalites_valides:
        return {
            "statut": "erreur",
            "raison": "modalite_non_supportee",
            "modalite": modalite,
            "modalites_valides": sorted(modalites_valides)
        }

    if source is not None and not isinstance(source, str):
        source = str(source)

    if metadata is None:
        metadata = {}

    if not isinstance(metadata, dict):
        return {
            "statut": "erreur",
            "raison": "metadata_invalide"
        }

    return {
        "statut": "connaissance_multimodale_structuree",
        "titre": titre.strip(),
        "contenu": contenu.strip(),
        "modalite": modalite,
        "source": source,
        "metadata": metadata,
        "evolution_possible": True,
        "donnees_modifiees": False
    }



# ============================================================
# MIA V47 — ACTUALISATION MULTIMODALE D'UNE CONNAISSANCE
# ============================================================

def mia47_actualiser_connaissance_multimodale(
    titre,
    contenu,
    modalite="texte",
    source=None,
    metadata=None,
    seuil_similarite=95
):
    """
    Analyse une connaissance multimodale et détermine
    si elle est nouvelle, identique ou en évolution.

    Utilise :
    - V46 pour structurer la connaissance
    - V41 pour détecter l'actualisation

    Ne modifie aucune donnée.
    """

    structure = mia46_structurer_connaissance_multimodale(
        titre,
        contenu,
        modalite=modalite,
        source=source,
        metadata=metadata
    )

    if structure.get("statut") != "connaissance_multimodale_structuree":
        return structure

    actualisation = mia41_detecter_actualisation(
        titre,
        contenu,
        seuil_similarite=seuil_similarite
    )

    if actualisation.get("statut") not in {
        "nouvelle",
        "identique",
        "evolution",
        "a_verifier"
    }:
        return actualisation

    return {
        "statut": "actualisation_multimodale_analysee",
        "titre": structure.get("titre"),
        "contenu": structure.get("contenu"),
        "modalite": structure.get("modalite"),
        "source": structure.get("source"),
        "metadata": structure.get("metadata"),
        "actualisation": actualisation,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V48 — TRACE DE PROVENANCE MULTIMODALE
# ============================================================

def mia48_tracer_provenance_multimodale(connaissance):
    """
    Génère une trace transparente d'une connaissance multimodale.
    Ne modifie aucune donnée.
    """

    import datetime

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    return {
        "statut": "provenance_multimodale_tracee",
        "titre": connaissance.get("titre"),
        "modalite": connaissance.get("modalite"),
        "source": connaissance.get("source"),
        "metadata": connaissance.get("metadata", {}),
        "date_analyse": datetime.datetime.now().isoformat(),
        "donnees_modifiees": False
    }


# ============================================================
# MIA V49 — RECHERCHE UNIFIEE DE CONNAISSANCES MULTIMODALES
# ============================================================

def mia49_rechercher_connaissances_multimodales(
    connaissances,
    requete,
    modalite=None
):
    """
    Recherche dans une collection de connaissances
    multimodales avec un filtre optionnel de modalité.

    Modalités :
    texte, document, image, audio, video.

    La recherche est volontairement simple et transparente :
    elle vérifie la présence de la requête dans le titre
    ou le contenu.

    Ne modifie aucune donnée.
    """

    if not isinstance(connaissances, list):
        return {
            "statut": "erreur",
            "raison": "connaissances_invalides"
        }

    if not isinstance(requete, str) or not requete.strip():
        return {
            "statut": "erreur",
            "raison": "requete_invalide"
        }

    if modalite is not None:
        modalites_valides = {
            "texte",
            "document",
            "image",
            "audio",
            "video"
        }

        if not isinstance(modalite, str):
            return {
                "statut": "erreur",
                "raison": "modalite_invalide"
            }

        modalite = modalite.strip().lower()

        if modalite not in modalites_valides:
            return {
                "statut": "erreur",
                "raison": "modalite_non_supportee"
            }

    terme = requete.strip().lower()
    resultats = []

    for connaissance in connaissances:

        if not isinstance(connaissance, dict):
            continue

        if modalite is not None:
            if connaissance.get("modalite") != modalite:
                continue

        titre = str(connaissance.get("titre", "")).lower()
        contenu = str(connaissance.get("contenu", "")).lower()

        if terme in titre or terme in contenu:
            resultats.append({
                "titre": connaissance.get("titre"),
                "contenu": connaissance.get("contenu"),
                "modalite": connaissance.get("modalite"),
                "source": connaissance.get("source"),
                "metadata": connaissance.get("metadata", {})
            })

    return {
        "statut": "recherche_multimodale_effectuee",
        "requete": requete.strip(),
        "modalite": modalite,
        "nombre_resultats": len(resultats),
        "resultats": resultats,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V50 — RECHERCHE AVEC PROVENANCE MULTIMODALE
# ============================================================

def mia50_rechercher_avec_provenance_multimodale(
    connaissances,
    requete,
    modalite=None
):
    """
    Recherche une connaissance multimodale et ajoute
    sa trace de provenance.

    Utilise :
    - V49 pour la recherche
    - V48 pour la provenance

    Ne modifie aucune donnée.
    """

    recherche = mia49_rechercher_connaissances_multimodales(
        connaissances,
        requete,
        modalite=modalite
    )

    if recherche.get("statut") != "recherche_multimodale_effectuee":
        return recherche

    resultats = []

    for connaissance in recherche.get("resultats", []):

        provenance = mia48_tracer_provenance_multimodale(
            connaissance
        )

        resultats.append({
            "connaissance": connaissance,
            "provenance": provenance
        })

    return {
        "statut": "recherche_provenance_multimodale_effectuee",
        "requete": recherche.get("requete"),
        "modalite": recherche.get("modalite"),
        "nombre_resultats": len(resultats),
        "resultats": resultats,
        "donnees_modifiees": False
    }




# ============================================================
# MIA V51 — EVALUATION DE FIABILITE MULTIMODALE
# ============================================================

def mia51_evaluer_fiabilite_multimodale(connaissance):
    """
    Évalue de manière transparente la fiabilité apparente
    d'une connaissance multimodale.

    Critères :
    - titre présent
    - contenu présent
    - modalité valide
    - source présente
    - metadata présentes

    Cette fonction ne modifie aucune donnée.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    score = 0
    criteres = {}

    titre_ok = bool(
        isinstance(connaissance.get("titre"), str)
        and connaissance.get("titre").strip()
    )

    contenu_ok = bool(
        isinstance(connaissance.get("contenu"), str)
        and connaissance.get("contenu").strip()
    )

    modalites_valides = {
        "texte",
        "document",
        "image",
        "audio",
        "video"
    }

    modalite_ok = connaissance.get("modalite") in modalites_valides

    source_ok = bool(
        isinstance(connaissance.get("source"), str)
        and connaissance.get("source").strip()
    )

    metadata_ok = isinstance(
        connaissance.get("metadata", {}),
        dict
    )

    criteres["titre"] = titre_ok
    criteres["contenu"] = contenu_ok
    criteres["modalite"] = modalite_ok
    criteres["source"] = source_ok
    criteres["metadata"] = metadata_ok

    for valeur in criteres.values():
        if valeur:
            score += 1

    score_pourcentage = score * 20

    if score_pourcentage >= 80:
        niveau = "eleve"
    elif score_pourcentage >= 60:
        niveau = "moyen"
    else:
        niveau = "faible"

    return {
        "statut": "fiabilite_multimodale_evaluee",
        "score": score,
        "score_pourcentage": score_pourcentage,
        "niveau": niveau,
        "criteres": criteres,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V52 — SYNTHESE DE CONNAISSANCES MULTIMODALES
# ============================================================

def mia52_synthetiser_connaissances_multimodales(connaissances):
    """
    Regroupe plusieurs connaissances multimodales
    dans une synthèse structurée et transparente.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissances, list):
        return {
            "statut": "erreur",
            "raison": "connaissances_invalides"
        }

    synthese = []

    for connaissance in connaissances:

        if not isinstance(connaissance, dict):
            continue

        synthese.append({
            "titre": connaissance.get("titre"),
            "contenu": connaissance.get("contenu"),
            "modalite": connaissance.get("modalite"),
            "source": connaissance.get("source"),
            "metadata": connaissance.get("metadata", {})
        })

    return {
        "statut": "synthese_multimodale_effectuee",
        "nombre_connaissances": len(synthese),
        "connaissances": synthese,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V53 — COMPARAISON DE CONNAISSANCES MULTIMODALES
# ============================================================

def mia53_comparer_connaissances_multimodales(
    connaissance_a,
    connaissance_b
):
    """
    Compare deux connaissances multimodales
    de manière simple, transparente et non destructive.

    Vérifie :
    - titre
    - contenu
    - modalité
    - source
    - metadata

    Ne modifie aucune donnée.
    """

    if not isinstance(connaissance_a, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_a_invalide"
        }

    if not isinstance(connaissance_b, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_b_invalide"
        }

    champs = [
        "titre",
        "contenu",
        "modalite",
        "source",
        "metadata"
    ]

    comparaison = {}

    for champ in champs:
        comparaison[champ] = (
            connaissance_a.get(champ)
            == connaissance_b.get(champ)
        )

    champs_identiques = sum(
        1 for valeur in comparaison.values()
        if valeur
    )

    score_pourcentage = champs_identiques * 20

    if score_pourcentage == 100:
        relation = "identiques"
    elif score_pourcentage >= 60:
        relation = "tres_similaires"
    elif score_pourcentage >= 20:
        relation = "partiellement_similaires"
    else:
        relation = "differentes"

    return {
        "statut": "comparaison_multimodale_effectuee",
        "comparaison": comparaison,
        "champs_identiques": champs_identiques,
        "score_pourcentage": score_pourcentage,
        "relation": relation,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V54 — CONSOLIDATION DES CONNAISSANCES MULTIMODALES
# ============================================================

def mia54_consolider_connaissances_multimodales(connaissances):
    """
    Détermine quelles connaissances multimodales peuvent
    être considérées comme consolidées.

    Utilise V51 pour évaluer leur fiabilité.

    Une connaissance est consolidée si son score de
    fiabilité est supérieur ou égal à 80 %.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissances, list):
        return {
            "statut": "erreur",
            "raison": "connaissances_invalides"
        }

    consolidees = []
    non_consolidees = []

    for connaissance in connaissances:

        if not isinstance(connaissance, dict):
            continue

        evaluation = mia51_evaluer_fiabilite_multimodale(
            connaissance
        )

        element = {
            "connaissance": connaissance,
            "fiabilite": evaluation
        }

        if evaluation.get("score_pourcentage", 0) >= 80:
            consolidees.append(element)
        else:
            non_consolidees.append(element)

    return {
        "statut": "consolidation_multimodale_effectuee",
        "nombre_consolidees": len(consolidees),
        "nombre_non_consolidees": len(non_consolidees),
        "consolidees": consolidees,
        "non_consolidees": non_consolidees,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V55 — DETECTION DES CONFLITS DE CONNAISSANCES
# ============================================================

def mia55_detecter_conflits_connaissances_multimodales(
    connaissances
):
    """
    Détecte les conflits entre connaissances multimodales.

    Deux connaissances sont considérées en conflit si elles
    possèdent le même titre mais un contenu différent.

    MIA signale le conflit sans décider quelle connaissance
    est correcte.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissances, list):
        return {
            "statut": "erreur",
            "raison": "connaissances_invalides"
        }

    conflits = []

    for i in range(len(connaissances)):
        connaissance_a = connaissances[i]

        if not isinstance(connaissance_a, dict):
            continue

        for j in range(i + 1, len(connaissances)):
            connaissance_b = connaissances[j]

            if not isinstance(connaissance_b, dict):
                continue

            titre_a = connaissance_a.get("titre")
            titre_b = connaissance_b.get("titre")

            contenu_a = connaissance_a.get("contenu")
            contenu_b = connaissance_b.get("contenu")

            if (
                isinstance(titre_a, str)
                and isinstance(titre_b, str)
                and titre_a.strip().lower()
                == titre_b.strip().lower()
                and contenu_a != contenu_b
            ):
                conflits.append({
                    "titre": titre_a,
                    "connaissance_a": connaissance_a,
                    "connaissance_b": connaissance_b,
                    "source_a": connaissance_a.get("source"),
                    "source_b": connaissance_b.get("source"),
                    "conflit": True
                })

    return {
        "statut": "conflits_multimodaux_detectes",
        "nombre_conflits": len(conflits),
        "conflits": conflits,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V56 — VERSIONNAGE DES CONNAISSANCES
# ============================================================

def mia56_versionner_connaissance(
    connaissance,
    nouvelle_information,
    numero_version
):
    """
    Crée une nouvelle version d'une connaissance
    sans supprimer la version précédente.

    L'ancienne connaissance est conservée dans
    'version_precedente'.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    if not isinstance(nouvelle_information, str):
        return {
            "statut": "erreur",
            "raison": "nouvelle_information_invalide"
        }

    if not nouvelle_information.strip():
        return {
            "statut": "erreur",
            "raison": "nouvelle_information_invalide"
        }

    if not isinstance(numero_version, int):
        return {
            "statut": "erreur",
            "raison": "numero_version_invalide"
        }

    nouvelle_connaissance = {
        "titre": connaissance.get("titre"),
        "contenu": nouvelle_information.strip(),
        "modalite": connaissance.get("modalite"),
        "source": connaissance.get("source"),
        "metadata": connaissance.get("metadata", {}),
        "version": numero_version,
        "version_precedente": connaissance
    }

    return {
        "statut": "connaissance_versionnee",
        "ancienne_version": connaissance,
        "nouvelle_version": nouvelle_connaissance,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V57 — HISTORIQUE DES VERSIONS
# ============================================================

def mia57_obtenir_historique_versions(connaissance):
    """
    Reconstruit l'historique des versions d'une connaissance.

    Parcourt la version actuelle puis les versions précédentes
    conservées dans 'version_precedente'.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    historique = []
    courante = connaissance

    while isinstance(courante, dict):

        historique.append({
            "version": courante.get("version", 1),
            "titre": courante.get("titre"),
            "contenu": courante.get("contenu"),
            "modalite": courante.get("modalite"),
            "source": courante.get("source")
        })

        precedente = courante.get("version_precedente")

        if not isinstance(precedente, dict):
            break

        courante = precedente

    return {
        "statut": "historique_versions_obtenu",
        "nombre_versions": len(historique),
        "historique": historique,
        "donnees_modifiees": False
    }




# ============================================================
# MIA V58 — SELECTION D'UNE VERSION DE CONNAISSANCE
# ============================================================

def mia58_selectionner_version_connaissance(
    connaissance,
    numero_version
):
    """
    Recherche une version précise d'une connaissance
    dans son historique.

    Parcourt la version actuelle puis les versions précédentes
    conservées dans 'version_precedente'.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    if not isinstance(numero_version, int):
        return {
            "statut": "erreur",
            "raison": "numero_version_invalide"
        }

    courante = connaissance

    while isinstance(courante, dict):

        version = courante.get("version", 1)

        if version == numero_version:
            return {
                "statut": "version_trouvee",
                "version": version,
                "connaissance": courante,
                "donnees_modifiees": False
            }

        precedente = courante.get("version_precedente")

        if not isinstance(precedente, dict):
            break

        courante = precedente

    return {
        "statut": "version_non_trouvee",
        "version_recherchee": numero_version,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V59 — COMPARAISON ENTRE VERSIONS
# ============================================================

def mia59_comparer_versions_connaissance(
    connaissance,
    version_a,
    version_b
):
    """
    Compare deux versions d'une même connaissance.

    Utilise l'historique conservé dans 'version_precedente'.
    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    if not isinstance(version_a, int):
        return {
            "statut": "erreur",
            "raison": "version_a_invalide"
        }

    if not isinstance(version_b, int):
        return {
            "statut": "erreur",
            "raison": "version_b_invalide"
        }

    resultat_a = mia58_selectionner_version_connaissance(
        connaissance,
        version_a
    )

    resultat_b = mia58_selectionner_version_connaissance(
        connaissance,
        version_b
    )

    if resultat_a.get("statut") != "version_trouvee":
        return {
            "statut": "version_a_non_trouvee",
            "version_recherchee": version_a,
            "donnees_modifiees": False
        }

    if resultat_b.get("statut") != "version_trouvee":
        return {
            "statut": "version_b_non_trouvee",
            "version_recherchee": version_b,
            "donnees_modifiees": False
        }

    connaissance_a = resultat_a.get("connaissance", {})
    connaissance_b = resultat_b.get("connaissance", {})

    champs = [
        "titre",
        "contenu",
        "modalite",
        "source",
        "metadata"
    ]

    comparaison = {}

    for champ in champs:
        comparaison[champ] = (
            connaissance_a.get(champ)
            == connaissance_b.get(champ)
        )

    champs_identiques = sum(
        1 for valeur in comparaison.values()
        if valeur
    )

    score_pourcentage = champs_identiques * 20

    return {
        "statut": "comparaison_versions_effectuee",
        "version_a": version_a,
        "version_b": version_b,
        "comparaison": comparaison,
        "champs_identiques": champs_identiques,
        "score_pourcentage": score_pourcentage,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V60 — IDENTIFICATION DE LA VERSION LA PLUS RECENTE
# ============================================================

def mia60_identifier_version_recente(connaissance):
    """
    Identifie la version la plus récente d'une connaissance.

    Parcourt la connaissance actuelle et son historique
    conservé dans 'version_precedente'.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    courante = connaissance
    version_recente = courante

    while isinstance(courante, dict):

        version = courante.get("version", 1)
        version_actuelle = version_recente.get("version", 1)

        if isinstance(version, int) and version > version_actuelle:
            version_recente = courante

        precedente = courante.get("version_precedente")

        if not isinstance(precedente, dict):
            break

        courante = precedente

    return {
        "statut": "version_recente_identifiee",
        "version": version_recente.get("version", 1),
        "connaissance": version_recente,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V61 — VERIFICATION DE L'HISTORIQUE EVOLUTIF
# ============================================================

def mia61_verifier_historique_evolutif(connaissance):
    """
    Vérifie si une connaissance possède un historique
    de plusieurs versions.

    Une connaissance possède un historique évolutif si
    une ou plusieurs versions précédentes sont présentes
    dans 'version_precedente'.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    nombre_versions = 1
    courante = connaissance

    while isinstance(courante, dict):

        precedente = courante.get("version_precedente")

        if not isinstance(precedente, dict):
            break

        nombre_versions += 1
        courante = precedente

    historique_present = nombre_versions > 1

    return {
        "statut": "verification_historique_effectuee",
        "historique_present": historique_present,
        "nombre_versions": nombre_versions,
        "donnees_modifiees": False
    }


# ============================================================
# MIA V62 — IDENTIFICATION DE LA VERSION RECENTE FIABLE
# ============================================================

def mia62_identifier_version_recente_fiable(connaissance):
    """
    Identifie la version la plus récente considérée comme fiable.

    Parcourt la version actuelle puis les versions précédentes
    conservées dans 'version_precedente'.

    Utilise V51 pour évaluer la fiabilité de chaque version.

    Une version est considérée comme fiable si son score de
    fiabilité est supérieur ou égal à 80 %.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide"
        }

    versions_evaluees = []
    courante = connaissance

    while isinstance(courante, dict):

        evaluation = mia51_evaluer_fiabilite_multimodale(
            courante
        )

        score = evaluation.get("score_pourcentage", 0)

        versions_evaluees.append({
            "connaissance": courante,
            "fiabilite": evaluation,
            "score_pourcentage": score
        })

        precedente = courante.get("version_precedente")

        if not isinstance(precedente, dict):
            break

        courante = precedente

    versions_fiables = [
        element
        for element in versions_evaluees
        if element.get("score_pourcentage", 0) >= 80
    ]

    if not versions_fiables:
        return {
            "statut": "aucune_version_fiable",
            "nombre_versions_evaluees": len(versions_evaluees),
            "donnees_modifiees": False
        }

    version_recente_fiable = versions_fiables[0]

    return {
        "statut": "version_recente_fiable_identifiee",
        "version": version_recente_fiable[
            "connaissance"
        ].get("version", 1),
        "connaissance": version_recente_fiable[
            "connaissance"
        ],
        "fiabilite": version_recente_fiable[
            "fiabilite"
        ],
        "score_pourcentage": version_recente_fiable[
            "score_pourcentage"
        ],
        "nombre_versions_evaluees": len(versions_evaluees),
        "donnees_modifiees": False
    }


# ============================================================
# MIA V63 — VALIDATION DE LA VERSION RECENTE FIABLE
# ============================================================

def mia63_valider_version_recente_fiable(connaissance):
    """
    Valide qu'une version récente fiable peut être utilisée.

    Utilise MIA62 pour identifier la version récente considérée
    comme fiable.

    La validation exige un score de fiabilité supérieur ou égal
    à 80 %.

    Ne modifie aucune donnée source.
    """

    if not isinstance(connaissance, dict):
        return {
            "statut": "erreur",
            "raison": "connaissance_invalide",
            "donnees_modifiees": False
        }

    resultat = mia62_identifier_version_recente_fiable(connaissance)

    if not isinstance(resultat, dict):
        return {
            "statut": "erreur",
            "raison": "resultat_mia62_invalide",
            "donnees_modifiees": False
        }

    if resultat.get("statut") != "version_recente_fiable_identifiee":
        return {
            "statut": "version_recente_fiable_non_validee",
            "raison": resultat.get("statut", "statut_inconnu"),
            "nombre_versions_evaluees": resultat.get(
                "nombre_versions_evaluees", 0
            ),
            "donnees_modifiees": False
        }

    score = resultat.get("score_pourcentage", 0)

    if not isinstance(score, (int, float)):
        return {
            "statut": "version_recente_fiable_non_validee",
            "raison": "score_invalide",
            "donnees_modifiees": False
        }

    if score < 80:
        return {
            "statut": "version_recente_fiable_non_validee",
            "raison": "score_insuffisant",
            "score_pourcentage": score,
            "donnees_modifiees": False
        }

    return {
        "statut": "version_recente_fiable_validee",
        "version": resultat.get("version", 1),
        "connaissance": resultat.get("connaissance"),
        "fiabilite": resultat.get("fiabilite"),
        "score_pourcentage": score,
        "nombre_versions_evaluees": resultat.get(
            "nombre_versions_evaluees", 0
        ),
        "donnees_modifiees": False
    }



# ============================================================
# MIA V65 — PHASE 2 — BRIQUE 1 : SYSTEME MULTI-AGENTS
# ============================================================

def mia65_agent_recherche(question):
    """
    Agent Recherche V65.

    Responsabilité :
    rechercher les connaissances pertinentes dans
    le coeur existant d'ALKAH-BRAIN.

    Ne modifie aucune donnée.
    """
    if not isinstance(question, str) or not question.strip():
        return {
            "agent": "recherche",
            "statut": "erreur",
            "resultat": None,
            "donnees_modifiees": False
        }

    resultat = mia_interroger(question.strip())

    return {
        "agent": "recherche",
        "statut": "termine",
        "resultat": resultat,
        "donnees_modifiees": False
    }


def mia65_agent_analyse(question, resultat_recherche=None):
    """
    Agent Analyse V65.

    Analyse les connaissances déjà récupérées.
    Ne remplace pas le moteur de décision V64.
    """
    if not isinstance(question, str) or not question.strip():
        return {
            "agent": "analyse",
            "statut": "erreur",
            "resultat": None,
            "donnees_modifiees": False
        }

    if resultat_recherche is None:
        resultat_recherche = mia_interroger(question.strip())

    souvenirs = []

    if isinstance(resultat_recherche, dict):
        souvenirs = resultat_recherche.get("souvenirs", [])

    return {
        "agent": "analyse",
        "statut": "termine",
        "resultat": {
            "question": question.strip(),
            "nombre_connaissances": len(souvenirs),
            "souvenirs": souvenirs
        },
        "donnees_modifiees": False
    }


def mia65_agent_memoire(question):
    """
    Agent Mémoire V65.

    Consulte la mémoire d'apprentissage existante
    sans modifier celle-ci.
    """
    if not isinstance(question, str) or not question.strip():
        return {
            "agent": "memoire",
            "statut": "erreur",
            "resultat": None,
            "donnees_modifiees": False
        }

    memoires = mia_charger_memoires_apprentissage_sqlite()

    resultats = mia_rechercher_memoire_apprentissage(
        question.strip(),
        memoires
    )

    selection = mia_selectionner_meilleure_memoire_securisee(
        resultats
    )

    contexte = mia_preparer_contexte_memoire_selectionnee(
        selection
    )

    return {
        "agent": "memoire",
        "statut": "termine",
        "resultat": {
            "nombre_memoires": len(memoires),
            "nombre_resultats": len(resultats),
            "selection": selection,
            "contexte": contexte
        },
        "donnees_modifiees": False
    }


def mia65_agent_verification(
    question,
    recherche=None,
    analyse=None,
    memoire=None
):
    """
    Agent Vérification V65.

    Vérifie la structure des résultats produits
    par les autres agents.

    Aucun agent ne peut modifier les données sources.
    """
    erreurs = []

    if recherche is not None and not isinstance(recherche, dict):
        erreurs.append("recherche_invalide")

    if analyse is not None and not isinstance(analyse, dict):
        erreurs.append("analyse_invalide")

    if memoire is not None and not isinstance(memoire, dict):
        erreurs.append("memoire_invalide")

    return {
        "agent": "verification",
        "statut": "valide" if not erreurs else "invalide",
        "erreurs": erreurs,
        "question": question,
        "donnees_modifiees": False
    }


def mia65_orchestrer_agents(question):
    """
    Orchestrateur Multi-Agents V65 — Brique 1.

    Coordonne :
        1. Recherche
        2. Analyse
        3. Mémoire
        4. Vérification

    Cette première version reste indépendante du pipeline
    principal V64.
    """
    if not isinstance(question, str) or not question.strip():
        return {
            "statut": "erreur",
            "question": question,
            "agents": {},
            "donnees_modifiees": False
        }

    question = question.strip()

    recherche = mia65_agent_recherche(question)

    resultat_recherche = recherche.get("resultat")

    analyse = mia65_agent_analyse(
        question,
        resultat_recherche
    )

    memoire = mia65_agent_memoire(question)

    verification = mia65_agent_verification(
        question,
        recherche,
        analyse,
        memoire
    )

    return {
        "statut": (
            "termine"
            if verification.get("statut") == "valide"
            else "verification_echec"
        ),
        "question": question,
        "agents": {
            "recherche": recherche,
            "analyse": analyse,
            "memoire": memoire,
            "verification": verification
        },
        "donnees_modifiees": False
    }

# ============================================================
# FIN MIA V65 — BRIQUE 1 MULTI-AGENTS
# ============================================================

# ============================================================
# MIA V66 — PHASE 2 — BRIQUE 2 : GESTIONNAIRE D'OUTILS
# ============================================================

def mia66_creer_registre_outils():
    """
    Crée un registre isolé des outils disponibles pour MIA.

    Le registre ne modifie aucune donnée du coeur ALKAH-BRAIN.
    """
    return {
        "version": "V66",
        "outils": {},
        "nombre_outils": 0,
        "donnees_modifiees": False
    }


def mia66_valider_outil(outil):
    """
    Vérifie la structure minimale d'un outil MIA.
    """
    if not isinstance(outil, dict):
        return {
            "valide": False,
            "erreurs": ["outil_invalide"],
            "donnees_modifiees": False
        }

    champs_obligatoires = [
        "nom",
        "description",
        "fonction",
        "autorise"
    ]

    erreurs = [
        f"champ_absent:{champ}"
        for champ in champs_obligatoires
        if champ not in outil
    ]

    if "nom" in outil and (
        not isinstance(outil["nom"], str)
        or not outil["nom"].strip()
    ):
        erreurs.append("nom_invalide")

    if "fonction" in outil and not callable(outil["fonction"]):
        erreurs.append("fonction_non_callable")

    if "autorise" in outil and not isinstance(
        outil["autorise"], bool
    ):
        erreurs.append("autorisation_invalide")

    return {
        "valide": not erreurs,
        "erreurs": erreurs,
        "donnees_modifiees": False
    }


def mia66_enregistrer_outil(registre, outil):
    """
    Enregistre un outil uniquement après validation.
    """
    validation = mia66_valider_outil(outil)

    if not validation["valide"]:
        return {
            "succes": False,
            "statut": "outil_refuse",
            "validation": validation,
            "donnees_modifiees": False
        }

    if outil.get("autorise") is not True:
        return {
            "succes": False,
            "statut": "outil_refuse",
            "raison": "outil_non_autorise",
            "donnees_modifiees": False
        }

    if not isinstance(registre, dict):
        return {
            "succes": False,
            "statut": "registre_invalide",
            "donnees_modifiees": False
        }

    nom = outil["nom"].strip()

    if nom in registre["outils"]:
        return {
            "succes": False,
            "statut": "outil_deja_enregistre",
            "nom": nom,
            "donnees_modifiees": False
        }

    registre["outils"][nom] = outil
    registre["nombre_outils"] = len(registre["outils"])

    return {
        "succes": True,
        "statut": "outil_enregistre",
        "nom": nom,
        "nombre_outils": registre["nombre_outils"],
        "donnees_modifiees": True
    }


def mia66_rechercher_outil(registre, nom):
    """
    Recherche un outil dans le registre sans l'exécuter.
    """
    if not isinstance(registre, dict):
        return {
            "trouve": False,
            "outil": None,
            "raison": "registre_invalide",
            "donnees_modifiees": False
        }

    if not isinstance(nom, str) or not nom.strip():
        return {
            "trouve": False,
            "outil": None,
            "raison": "nom_invalide",
            "donnees_modifiees": False
        }

    outil = registre.get("outils", {}).get(nom.strip())

    return {
        "trouve": outil is not None,
        "outil": outil,
        "raison": (
            "outil_trouve"
            if outil is not None
            else "outil_inconnu"
        ),
        "donnees_modifiees": False
    }


def mia66_executer_outil(registre, nom, *args, **kwargs):
    """
    Exécute uniquement un outil enregistré et explicitement autorisé.

    Aucun outil inconnu ou non autorisé ne peut être exécuté.
    """
    recherche = mia66_rechercher_outil(registre, nom)

    if not recherche["trouve"]:
        return {
            "succes": False,
            "statut": "execution_refusee",
            "raison": "outil_inconnu",
            "resultat": None,
            "donnees_modifiees": False
        }

    outil = recherche["outil"]

    if outil.get("autorise") is not True:
        return {
            "succes": False,
            "statut": "execution_refusee",
            "raison": "outil_non_autorise",
            "resultat": None,
            "donnees_modifiees": False
        }

    fonction = outil.get("fonction")

    if not callable(fonction):
        return {
            "succes": False,
            "statut": "execution_refusee",
            "raison": "fonction_non_callable",
            "resultat": None,
            "donnees_modifiees": False
        }

    try:
        resultat = fonction(*args, **kwargs)

        return {
            "succes": True,
            "statut": "execution_terminee",
            "nom": nom.strip(),
            "resultat": resultat,
            "donnees_modifiees": False
        }

    except Exception as erreur:
        return {
            "succes": False,
            "statut": "execution_erreur",
            "raison": str(erreur),
            "resultat": None,
            "donnees_modifiees": False
        }


# ============================================================
# FIN MIA V66 — BRIQUE 2 : GESTIONNAIRE D'OUTILS
# ============================================================

# ============================================================
# MIA V67 — PHASE 2 — BRIQUE 3 : MOTEUR D'AUTOMATISATION
# ============================================================

def mia67_creer_plan_automatisation():
    """
    Crée un plan d'automatisation isolé.
    """
    return {
        "version": "V67",
        "statut": "nouveau",
        "taches": [],
        "resultats": [],
        "nombre_taches": 0,
        "donnees_modifiees": False
    }


def mia67_valider_tache(tache):
    """
    Vérifie la structure minimale d'une tâche.
    """
    if not isinstance(tache, dict):
        return {
            "valide": False,
            "erreurs": ["tache_invalide"],
            "donnees_modifiees": False
        }

    champs_obligatoires = [
        "nom",
        "outil",
        "args",
        "kwargs"
    ]

    erreurs = [
        f"champ_absent:{champ}"
        for champ in champs_obligatoires
        if champ not in tache
    ]

    if "nom" in tache and (
        not isinstance(tache["nom"], str)
        or not tache["nom"].strip()
    ):
        erreurs.append("nom_invalide")

    if "outil" in tache and (
        not isinstance(tache["outil"], str)
        or not tache["outil"].strip()
    ):
        erreurs.append("outil_invalide")

    if "args" in tache and not isinstance(tache["args"], (list, tuple)):
        erreurs.append("args_invalides")

    if "kwargs" in tache and not isinstance(tache["kwargs"], dict):
        erreurs.append("kwargs_invalides")

    return {
        "valide": not erreurs,
        "erreurs": erreurs,
        "donnees_modifiees": False
    }


def mia67_ajouter_tache(plan, tache):
    """
    Ajoute une tâche uniquement après validation.
    """
    if not isinstance(plan, dict):
        return {
            "succes": False,
            "statut": "plan_invalide",
            "donnees_modifiees": False
        }

    validation = mia67_valider_tache(tache)

    if not validation["valide"]:
        return {
            "succes": False,
            "statut": "tache_refusee",
            "validation": validation,
            "donnees_modifiees": False
        }

    plan.setdefault("taches", [])

    plan["taches"].append(dict(tache))
    plan["nombre_taches"] = len(plan["taches"])

    return {
        "succes": True,
        "statut": "tache_ajoutee",
        "nom": tache["nom"].strip(),
        "nombre_taches": plan["nombre_taches"],
        "donnees_modifiees": True
    }


def mia67_executer_plan(plan, registre):
    """
    Exécute séquentiellement un plan uniquement
    via le Gestionnaire d'outils V66.

    Toute tâche échouée provoque un arrêt sécurisé.
    Aucun appel direct de fonction n'est autorisé.
    """
    if not isinstance(plan, dict):
        return {
            "succes": False,
            "statut": "plan_invalide",
            "resultats": [],
            "donnees_modifiees": False
        }

    if not isinstance(registre, dict):
        return {
            "succes": False,
            "statut": "registre_invalide",
            "resultats": [],
            "donnees_modifiees": False
        }

    resultats = []

    for tache in plan.get("taches", []):
        validation = mia67_valider_tache(tache)

        if not validation["valide"]:
            resultat = {
                "succes": False,
                "statut": "tache_refusee",
                "nom": tache.get("nom"),
                "validation": validation,
                "donnees_modifiees": False
            }
            resultats.append(resultat)
            return {
                "succes": False,
                "statut": "arret_securise",
                "resultats": resultats,
                "nombre_execute": len(resultats),
                "donnees_modifiees": False
            }

        resultat = mia66_executer_outil(
            registre,
            tache["outil"],
            *tache["args"],
            **tache["kwargs"]
        )

        resultats.append({
            "nom": tache["nom"],
            "outil": tache["outil"],
            "resultat": resultat,
            "donnees_modifiees": False
        })

        if resultat.get("succes") is not True:
            return {
                "succes": False,
                "statut": "arret_securise",
                "raison": resultat.get("raison"),
                "resultats": resultats,
                "nombre_execute": len(resultats),
                "donnees_modifiees": False
            }

    plan["resultats"] = resultats
    plan["statut"] = "termine"

    return {
        "succes": True,
        "statut": "execution_terminee",
        "resultats": resultats,
        "nombre_execute": len(resultats),
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V67 — BRIQUE 3 : MOTEUR D'AUTOMATISATION
# ============================================================

# ============================================================
# MIA V68 — PHASE 2 — BRIQUE 4 : ENVIRONNEMENT DE TEST
# ============================================================

def mia68_creer_environnement_test():
    """
    Crée un environnement de test isolé pour MIA.
    Aucun état du moteur réel n'est modifié.
    """
    return {
        "version": "V68",
        "statut": "nouveau",
        "tests": [],
        "resultats": [],
        "nombre_tests": 0,
        "nombre_reussis": 0,
        "nombre_echecs": 0,
        "donnees_modifiees": False
    }


def mia68_valider_test(test):
    """
    Vérifie la structure minimale d'un test.
    """
    if not isinstance(test, dict):
        return {
            "valide": False,
            "erreurs": ["test_invalide"],
            "donnees_modifiees": False
        }

    champs_obligatoires = [
        "nom",
        "fonction"
    ]

    erreurs = [
        f"champ_absent:{champ}"
        for champ in champs_obligatoires
        if champ not in test
    ]

    if "nom" in test and (
        not isinstance(test["nom"], str)
        or not test["nom"].strip()
    ):
        erreurs.append("nom_invalide")

    if "fonction" in test and not callable(test["fonction"]):
        erreurs.append("fonction_non_callable")

    return {
        "valide": not erreurs,
        "erreurs": erreurs,
        "donnees_modifiees": False
    }


def mia68_ajouter_test(environnement, test):
    """
    Ajoute un test uniquement après validation.
    """
    if not isinstance(environnement, dict):
        return {
            "succes": False,
            "statut": "environnement_invalide",
            "donnees_modifiees": False
        }

    validation = mia68_valider_test(test)

    if not validation["valide"]:
        return {
            "succes": False,
            "statut": "test_refuse",
            "validation": validation,
            "donnees_modifiees": False
        }

    environnement.setdefault("tests", [])

    environnement["tests"].append(dict(test))
    environnement["nombre_tests"] = len(environnement["tests"])

    return {
        "succes": True,
        "statut": "test_ajoute",
        "nom": test["nom"].strip(),
        "nombre_tests": environnement["nombre_tests"],
        "donnees_modifiees": True
    }


def mia68_executer_test(test):
    """
    Exécute un test isolé et capture toute erreur.
    """
    validation = mia68_valider_test(test)

    if not validation["valide"]:
        return {
            "succes": False,
            "statut": "test_refuse",
            "validation": validation,
            "donnees_modifiees": False
        }

    try:
        resultat = test["fonction"]()

        return {
            "succes": True,
            "statut": "test_reussi",
            "nom": test["nom"].strip(),
            "resultat": resultat,
            "donnees_modifiees": False
        }

    except Exception as erreur:
        return {
            "succes": False,
            "statut": "test_echoue",
            "nom": test["nom"].strip(),
            "raison": str(erreur),
            "resultat": None,
            "donnees_modifiees": False
        }


def mia68_executer_environnement_test(environnement):
    """
    Exécute tous les tests séquentiellement.
    Les erreurs sont capturées individuellement.
    """
    if not isinstance(environnement, dict):
        return {
            "succes": False,
            "statut": "environnement_invalide",
            "resultats": [],
            "donnees_modifiees": False
        }

    resultats = []
    nombre_reussis = 0
    nombre_echecs = 0

    for test in environnement.get("tests", []):
        resultat = mia68_executer_test(test)
        resultats.append(resultat)

        if resultat.get("succes") is True:
            nombre_reussis += 1
        else:
            nombre_echecs += 1

    environnement["resultats"] = resultats
    environnement["nombre_reussis"] = nombre_reussis
    environnement["nombre_echecs"] = nombre_echecs
    environnement["statut"] = "termine"

    return {
        "succes": nombre_echecs == 0,
        "statut": "tests_termines",
        "resultats": resultats,
        "nombre_tests": len(resultats),
        "nombre_reussis": nombre_reussis,
        "nombre_echecs": nombre_echecs,
        "donnees_modifiees": False
    }


def mia68_generer_rapport_test(environnement):
    """
    Génère un rapport synthétique contrôlé de l'environnement de test.
    """
    if not isinstance(environnement, dict):
        return {
            "succes": False,
            "statut": "environnement_invalide",
            "rapport": None,
            "donnees_modifiees": False
        }

    total = environnement.get("nombre_tests", 0)
    reussis = environnement.get("nombre_reussis", 0)
    echecs = environnement.get("nombre_echecs", 0)

    return {
        "succes": True,
        "statut": "rapport_genere",
        "rapport": {
            "version": environnement.get("version"),
            "statut": environnement.get("statut"),
            "nombre_tests": total,
            "nombre_reussis": reussis,
            "nombre_echecs": echecs,
            "taux_reussite": (
                (reussis / total) * 100
                if total > 0
                else 0
            )
        },
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V68 — BRIQUE 4 : ENVIRONNEMENT DE TEST
# ============================================================


# ============================================================
# MIA V69 — PHASE 2 — BRIQUE 5 : VALIDATION DES TESTS
# ============================================================

def mia69_creer_validation_test():
    """
    Crée une structure isolée de validation des tests.
    Aucun état du moteur réel n'est modifié.
    """
    return {
        "version": "V69",
        "statut": "nouveau",
        "validations": [],
        "nombre_validations": 0,
        "nombre_valides": 0,
        "nombre_invalides": 0,
        "donnees_modifiees": False
    }


def mia69_valider_resultat_test(resultat):
    """
    Vérifie la structure minimale d'un résultat de test.
    """
    if not isinstance(resultat, dict):
        return {
            "valide": False,
            "erreurs": ["resultat_invalide"],
            "donnees_modifiees": False
        }

    erreurs = []

    if "succes" not in resultat:
        erreurs.append("champ_absent:succes")

    if "statut" not in resultat:
        erreurs.append("champ_absent:statut")

    if "donnees_modifiees" not in resultat:
        erreurs.append("champ_absent:donnees_modifiees")

    if "succes" in resultat and not isinstance(
        resultat["succes"], bool
    ):
        erreurs.append("succes_invalide")

    if "statut" in resultat and (
        not isinstance(resultat["statut"], str)
        or not resultat["statut"].strip()
    ):
        erreurs.append("statut_invalide")

    if "donnees_modifiees" in resultat and (
        resultat["donnees_modifiees"] is not False
    ):
        erreurs.append("modification_interdite")

    return {
        "valide": not erreurs,
        "erreurs": erreurs,
        "donnees_modifiees": False
    }


def mia69_enregistrer_validation(
    validation,
    resultat_test
):
    """
    Enregistre uniquement un résultat de test valide.
    """
    if not isinstance(validation, dict):
        return {
            "succes": False,
            "statut": "validation_invalide",
            "donnees_modifiees": False
        }

    controle = mia69_valider_resultat_test(resultat_test)

    if not controle["valide"]:
        return {
            "succes": False,
            "statut": "resultat_refuse",
            "validation": controle,
            "donnees_modifiees": False
        }

    validation.setdefault("validations", [])
    validation["validations"].append(dict(resultat_test))

    validation["nombre_validations"] = len(
        validation["validations"]
    )

    if resultat_test["succes"] is True:
        validation["nombre_valides"] += 1
    else:
        validation["nombre_invalides"] += 1

    return {
        "succes": True,
        "statut": "validation_enregistree",
        "nombre_validations": validation["nombre_validations"],
        "donnees_modifiees": True
    }


def mia69_analyser_validation(validation):
    """
    Produit une analyse contrôlée des validations enregistrées.
    """
    if not isinstance(validation, dict):
        return {
            "succes": False,
            "statut": "validation_invalide",
            "analyse": None,
            "donnees_modifiees": False
        }

    total = validation.get("nombre_validations", 0)
    valides = validation.get("nombre_valides", 0)
    invalides = validation.get("nombre_invalides", 0)

    return {
        "succes": True,
        "statut": "analyse_terminee",
        "analyse": {
            "version": validation.get("version"),
            "nombre_validations": total,
            "nombre_valides": valides,
            "nombre_invalides": invalides,
            "taux_validite": (
                (valides / total) * 100
                if total > 0
                else 0
            )
        },
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V69 — BRIQUE 5 : VALIDATION DES TESTS
# ============================================================


# ============================================================
# MIA V70 — PHASE 2 — BRIQUE 6 : JOURNALISATION DES TESTS
# ============================================================

def mia70_creer_journal_test():
    """
    Crée un journal isolé pour tracer les tests.
    Aucun état du moteur réel n'est modifié.
    """
    return {
        "version": "V70",
        "statut": "nouveau",
        "evenements": [],
        "nombre_evenements": 0,
        "nombre_succes": 0,
        "nombre_echecs": 0,
        "donnees_modifiees": False
    }


def mia70_valider_evenement_test(evenement):
    """
    Vérifie la structure minimale d'un événement de test.
    """
    if not isinstance(evenement, dict):
        return {
            "valide": False,
            "erreurs": ["evenement_invalide"],
            "donnees_modifiees": False
        }

    erreurs = []

    if "nom" not in evenement:
        erreurs.append("champ_absent:nom")

    if "statut" not in evenement:
        erreurs.append("champ_absent:statut")

    if "succes" not in evenement:
        erreurs.append("champ_absent:succes")

    if "donnees_modifiees" not in evenement:
        erreurs.append("champ_absent:donnees_modifiees")

    if "nom" in evenement and (
        not isinstance(evenement["nom"], str)
        or not evenement["nom"].strip()
    ):
        erreurs.append("nom_invalide")

    if "statut" in evenement and (
        not isinstance(evenement["statut"], str)
        or not evenement["statut"].strip()
    ):
        erreurs.append("statut_invalide")

    if "succes" in evenement and not isinstance(
        evenement["succes"], bool
    ):
        erreurs.append("succes_invalide")

    if "donnees_modifiees" in evenement and (
        evenement["donnees_modifiees"] is not False
    ):
        erreurs.append("modification_interdite")

    return {
        "valide": not erreurs,
        "erreurs": erreurs,
        "donnees_modifiees": False
    }


def mia70_enregistrer_evenement_test(journal, evenement):
    """
    Enregistre uniquement un événement valide.
    """
    if not isinstance(journal, dict):
        return {
            "succes": False,
            "statut": "journal_invalide",
            "donnees_modifiees": False
        }

    validation = mia70_valider_evenement_test(evenement)

    if not validation["valide"]:
        return {
            "succes": False,
            "statut": "evenement_refuse",
            "validation": validation,
            "donnees_modifiees": False
        }

    journal.setdefault("evenements", [])
    journal["evenements"].append(dict(evenement))

    journal["nombre_evenements"] = len(
        journal["evenements"]
    )

    if evenement["succes"] is True:
        journal["nombre_succes"] += 1
    else:
        journal["nombre_echecs"] += 1

    return {
        "succes": True,
        "statut": "evenement_enregistre",
        "nombre_evenements": journal["nombre_evenements"],
        "donnees_modifiees": True
    }


def mia70_verifier_integrite_journal_test(journal):
    """
    Vérifie la cohérence interne du journal de tests.
    """
    if not isinstance(journal, dict):
        return {
            "succes": False,
            "statut": "journal_invalide",
            "donnees_modifiees": False
        }

    evenements = journal.get("evenements", [])
    succes = journal.get("nombre_succes", 0)
    echecs = journal.get("nombre_echecs", 0)
    total = journal.get("nombre_evenements", 0)

    coherence = (
        isinstance(evenements, list)
        and total == len(evenements)
        and succes + echecs == total
    )

    return {
        "succes": coherence,
        "statut": (
            "integrite_ok"
            if coherence
            else "integrite_invalide"
        ),
        "nombre_evenements": total,
        "nombre_succes": succes,
        "nombre_echecs": echecs,
        "donnees_modifiees": False
    }


def mia70_generer_rapport_journal_test(journal):
    """
    Génère un rapport final contrôlé du journal.
    """
    if not isinstance(journal, dict):
        return {
            "succes": False,
            "statut": "journal_invalide",
            "rapport": None,
            "donnees_modifiees": False
        }

    total = journal.get("nombre_evenements", 0)
    succes = journal.get("nombre_succes", 0)
    echecs = journal.get("nombre_echecs", 0)

    return {
        "succes": True,
        "statut": "rapport_genere",
        "rapport": {
            "version": journal.get("version"),
            "statut": journal.get("statut"),
            "nombre_evenements": total,
            "nombre_succes": succes,
            "nombre_echecs": echecs,
            "taux_succes": (
                (succes / total) * 100
                if total > 0
                else 0
            )
        },
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V70 — BRIQUE 6 : JOURNALISATION DES TESTS
# ============================================================

# ============================================================
# MIA V71 — PHASE 2 — BRIQUE 7
# DETERMINATION DES CONTRAINTES DU CONTEXTE
# ============================================================

def mia71_determiner_contraintes_contexte(precision_besoin=None):
    """
    B7 — Détermine les contraintes explicitement présentes
    dans le contexte déjà validé.

    Cette fonction :
    - n'invente aucune contrainte ;
    - ne prend aucune décision ;
    - ne déclenche aucune action ;
    - ne modifie pas le coeur du moteur.
    """

    contexte_valide = (
        isinstance(precision_besoin, dict)
        and precision_besoin.get("analyse_valide") is True
        and precision_besoin.get("classification_valide") is True
        and precision_besoin.get("besoin_valide") is True
        and precision_besoin.get("precision_valide") is True
    )

    if not contexte_valide:
        return {
            "analyse_valide": False,
            "classification_valide": False,
            "besoin_valide": False,
            "precision_valide": False,
            "contraintes_valide": False,
            "contraintes_identifiees": False,
            "statut": "contraintes_contexte_invalides",
            "contexte": None,
            "elements": [],
            "classification": "contexte_non_classifiable",
            "besoin": None,
            "besoin_precis": None,
            "contraintes": [],
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    contexte = precision_besoin.get("contexte")
    elements = precision_besoin.get("elements", [])
    classification = precision_besoin.get(
        "classification",
        "contexte_non_classifiable"
    )
    besoin = precision_besoin.get("besoin")
    besoin_precis = precision_besoin.get("besoin_precis")

    contraintes = []

    if isinstance(contexte, dict):
        for cle, valeur in contexte.items():
            if "contrainte" in str(cle).lower():
                contraintes.append({
                    "type": str(cle),
                    "valeur": valeur
                })

    contraintes_identifiees = len(contraintes) > 0

    if contraintes_identifiees:
        statut = "contraintes_contexte_identifiees"
    else:
        statut = "aucune_contrainte_contexte_identifiee"

    return {
        "analyse_valide": True,
        "classification_valide": True,
        "besoin_valide": True,
        "precision_valide": True,
        "contraintes_valide": True,
        "contraintes_identifiees": contraintes_identifiees,
        "statut": statut,
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,

        # Sécurité B7
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia71_evaluer_contraintes_contexte(contraintes_contexte):
    """
    B7 — Évalue les contraintes identifiées.
    Aucune action n'est exécutée.
    """

    if not isinstance(contraintes_contexte, dict):
        return {
            "succes": False,
            "statut": "contraintes_contexte_invalides",
            "evaluation": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    contraintes_valide = (
        contraintes_contexte.get("analyse_valide") is True
        and contraintes_contexte.get("classification_valide") is True
        and contraintes_contexte.get("besoin_valide") is True
        and contraintes_contexte.get("precision_valide") is True
        and contraintes_contexte.get("contraintes_valide") is True
    )

    return {
        "succes": contraintes_valide,
        "statut": (
            "evaluation_contraintes_terminee"
            if contraintes_valide
            else "evaluation_contraintes_invalide"
        ),
        "evaluation": {
            "contraintes_identifiees":
                contraintes_contexte.get(
                    "contraintes_identifiees",
                    False
                ),
            "nombre_contraintes":
                len(contraintes_contexte.get("contraintes", [])),
            "contraintes":
                contraintes_contexte.get("contraintes", [])
        } if contraintes_valide else None,

        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia71_resumer_contraintes_contexte(contraintes_contexte):
    """
    B7 — Produit le résumé final des contraintes.
    """

    evaluation = mia71_evaluer_contraintes_contexte(
        contraintes_contexte
    )

    if not evaluation.get("succes"):
        return {
            "succes": False,
            "statut": "resume_contraintes_invalide",
            "resume": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": True,
        "statut": "resume_contraintes_termine",
        "resume": evaluation.get("evaluation"),
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V71 — BRIQUE 7
# ============================================================

# ============================================================
# MIA V72 — PHASE 2 — BRIQUE 8
# DETERMINATION DU NIVEAU DE PRIORITE DU CONTEXTE
# ============================================================

def mia72_determiner_priorite_contexte(contraintes_contexte=None):
    """
    B8 — Détermine le niveau de priorité du contexte.

    Cette fonction :
    - utilise uniquement les informations déjà validées par B1 à B7 ;
    - ne crée aucune information externe ;
    - ne prend aucune décision opérationnelle ;
    - ne déclenche aucune action ;
    - ne modifie pas le coeur du moteur.
    """

    contexte_valide = (
        isinstance(contraintes_contexte, dict)
        and contraintes_contexte.get("analyse_valide") is True
        and contraintes_contexte.get("classification_valide") is True
        and contraintes_contexte.get("besoin_valide") is True
        and contraintes_contexte.get("precision_valide") is True
        and contraintes_contexte.get("contraintes_valide") is True
    )

    if not contexte_valide:
        return {
            "analyse_valide": False,
            "classification_valide": False,
            "besoin_valide": False,
            "precision_valide": False,
            "contraintes_valide": False,
            "priorite_valide": False,
            "statut": "priorite_contexte_invalide",
            "contexte": None,
            "elements": [],
            "classification": "contexte_non_classifiable",
            "besoin": None,
            "besoin_precis": None,
            "contraintes": [],
            "priorite": "priorite_non_determinable",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    contexte = contraintes_contexte.get("contexte")
    elements = contraintes_contexte.get("elements", [])
    classification = contraintes_contexte.get(
        "classification",
        "contexte_non_classifiable"
    )
    besoin = contraintes_contexte.get("besoin")
    besoin_precis = contraintes_contexte.get("besoin_precis")
    contraintes = contraintes_contexte.get("contraintes", [])

    # --------------------------------------------------------
    # Détermination prudente de la priorité.
    # Seule une priorité explicitement présente dans le
    # contexte est retenue.
    # --------------------------------------------------------

    priorite = "normale"

    if isinstance(contexte, dict):
        valeur_priorite = contexte.get("priorite")

        if isinstance(valeur_priorite, str):
            valeur = valeur_priorite.strip().lower()

            if valeur in {
                "critique",
                "urgente",
                "haute",
                "moyenne",
                "normale",
                "basse"
            }:
                priorite = valeur

    priorite_valide = True

    return {
        "analyse_valide": True,
        "classification_valide": True,
        "besoin_valide": True,
        "precision_valide": True,
        "contraintes_valide": True,
        "priorite_valide": priorite_valide,
        "statut": "priorite_contexte_determinee",
        "contexte": contexte,
        "elements": elements,
        "classification": classification,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "contraintes": contraintes,
        "priorite": priorite,

        # Sécurité B8
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia72_evaluer_priorite_contexte(priorite_contexte):
    """
    B8 — Évalue la détermination du niveau de priorité.

    Cette fonction :
    - vérifie uniquement la validité de B8 ;
    - n'exécute aucune action ;
    - ne modifie aucune donnée du moteur.
    """

    if not isinstance(priorite_contexte, dict):
        return {
            "succes": False,
            "statut": "priorite_contexte_invalide",
            "evaluation": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    priorite_valide = (
        priorite_contexte.get("analyse_valide") is True
        and priorite_contexte.get("classification_valide") is True
        and priorite_contexte.get("besoin_valide") is True
        and priorite_contexte.get("precision_valide") is True
        and priorite_contexte.get("contraintes_valide") is True
        and priorite_contexte.get("priorite_valide") is True
    )

    return {
        "succes": priorite_valide,
        "statut": (
            "evaluation_priorite_terminee"
            if priorite_valide
            else "evaluation_priorite_invalide"
        ),
        "evaluation": {
            "priorite": priorite_contexte.get(
                "priorite",
                "priorite_non_determinable"
            ),
            "priorite_valide": priorite_valide
        } if priorite_valide else None,
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia72_resumer_priorite_contexte(priorite_contexte):
    """
    B8 — Produit le résumé final du niveau de priorité.
    """

    evaluation = mia72_evaluer_priorite_contexte(
        priorite_contexte
    )

    if not evaluation.get("succes"):
        return {
            "succes": False,
            "statut": "resume_priorite_invalide",
            "resume": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": True,
        "statut": "resume_priorite_termine",
        "resume": evaluation.get("evaluation"),
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V72 — BRIQUE 8
# ============================================================

# ============================================================
# MIA V73 — PHASE 2 — BRIQUE 9
# DETERMINATION DU TYPE DE REPONSE
# ============================================================

def mia73_determiner_type_reponse(priorite_contexte=None):
    """B9 — Détermine le type de réponse à partir du contexte validé.
    Aucune génération, décision opérationnelle ou exécution.
    """
    valide = (
        isinstance(priorite_contexte, dict)
        and priorite_contexte.get("analyse_valide") is True
        and priorite_contexte.get("classification_valide") is True
        and priorite_contexte.get("besoin_valide") is True
        and priorite_contexte.get("precision_valide") is True
        and priorite_contexte.get("contraintes_valide") is True
        and priorite_contexte.get("priorite_valide") is True
    )

    if not valide:
        return {
            "analyse_valide": False,
            "classification_valide": False,
            "besoin_valide": False,
            "precision_valide": False,
            "contraintes_valide": False,
            "priorite_valide": False,
            "type_reponse_valide": False,
            "statut": "type_reponse_invalide",
            "type_reponse": "type_reponse_non_determinable",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    besoin = priorite_contexte.get("besoin")
    besoin_precis = priorite_contexte.get("besoin_precis")

    type_reponse = "directe"

    texte = str(besoin_precis or besoin or "").lower()

    if any(x in texte for x in ("expliquer", "explication", "pourquoi", "comment")):
        type_reponse = "explication"
    elif any(x in texte for x in ("conseil", "recommander", "recommandation")):
        type_reponse = "conseil"
    elif any(x in texte for x in ("analyser", "analyse", "évaluer", "evaluation")):
        type_reponse = "analyse"
    elif any(x in texte for x in ("orienter", "orientation", "choisir", "options")):
        type_reponse = "orientation"

    return {
        "analyse_valide": True,
        "classification_valide": True,
        "besoin_valide": True,
        "precision_valide": True,
        "contraintes_valide": True,
        "priorite_valide": True,
        "type_reponse_valide": True,
        "statut": "type_reponse_determine",
        "type_reponse": type_reponse,
        "besoin": besoin,
        "besoin_precis": besoin_precis,
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia73_evaluer_type_reponse(type_reponse_contexte):
    """B9 — Vérifie uniquement la validité du type de réponse."""
    if not isinstance(type_reponse_contexte, dict):
        return {
            "succes": False,
            "statut": "type_reponse_invalide",
            "evaluation": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    valide = (
        type_reponse_contexte.get("analyse_valide") is True
        and type_reponse_contexte.get("classification_valide") is True
        and type_reponse_contexte.get("besoin_valide") is True
        and type_reponse_contexte.get("precision_valide") is True
        and type_reponse_contexte.get("contraintes_valide") is True
        and type_reponse_contexte.get("priorite_valide") is True
        and type_reponse_contexte.get("type_reponse_valide") is True
    )

    return {
        "succes": valide,
        "statut": (
            "evaluation_type_reponse_terminee"
            if valide else "evaluation_type_reponse_invalide"
        ),
        "evaluation": {
            "type_reponse": type_reponse_contexte.get(
                "type_reponse",
                "type_reponse_non_determinable"
            ),
            "type_reponse_valide": valide
        } if valide else None,
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia73_resumer_type_reponse(type_reponse_contexte):
    """B9 — Produit le résumé final du type de réponse."""
    evaluation = mia73_evaluer_type_reponse(type_reponse_contexte)

    if not evaluation.get("succes"):
        return {
            "succes": False,
            "statut": "resume_type_reponse_invalide",
            "resume": None,
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": True,
        "statut": "resume_type_reponse_termine",
        "resume": evaluation.get("evaluation"),
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


# ============================================================
# FIN MIA V73 — BRIQUE 9
# ============================================================

# ============================================================
# MIA V74 — BRIQUE 10 : STRUCTURE DE REPONSE
# ============================================================

def mia74_structurer_reponse(determination):
    """
    Construit une structure de réponse contrôlée à partir
    de la détermination V73.

    Cette brique ne génère aucun contenu et ne modifie
    aucune donnée externe.
    """
    if not isinstance(determination, dict):
        return {
            "structure_valide": False,
            "succes": False,
            "statut": "structure_reponse_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    type_reponse = determination.get("type_reponse")

    types_valides = {
        "explication",
        "conseil",
        "analyse",
        "orientation",
        "directe"
    }

    valide = type_reponse in types_valides

    structure = {
        "type_reponse": type_reponse,
        "introduction": True,
        "corps": True,
        "conclusion": True
    }

    return {
        "structure_reponse": structure,
        "structure_valide": valide,
        "succes": valide,
        "statut": (
            "structure_reponse_terminee"
            if valide
            else "structure_reponse_invalide"
        ),
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia74_evaluer_structure_reponse(structure):
    if not isinstance(structure, dict):
        return {
            "succes": False,
            "statut": "evaluation_structure_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": structure.get("structure_valide") is True,
        "statut": "evaluation_structure_reponse_terminee",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia74_resumer_structure_reponse(structure):
    if not isinstance(structure, dict):
        return {
            "succes": False,
            "statut": "resume_structure_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": structure.get("structure_valide") is True,
        "statut": "resume_structure_reponse_termine",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }

# ============================================================
# FIN MIA V74 — BRIQUE 10
# ============================================================

# ============================================================
# MIA V75 — BRIQUE 11 : CONTROLE DE COHERENCE
# ============================================================

def mia75_controler_coherence_reponse(structure):
    """
    Vérifie la cohérence interne de la structure de réponse V74.

    Cette brique ne génère aucun contenu et ne modifie
    aucune donnée externe.
    """
    if not isinstance(structure, dict):
        return {
            "coherence_valide": False,
            "succes": False,
            "statut": "controle_coherence_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    structure_reponse = structure.get("structure_reponse")

    if not isinstance(structure_reponse, dict):
        return {
            "coherence_valide": False,
            "succes": False,
            "statut": "structure_reponse_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    type_reponse = structure_reponse.get("type_reponse")

    champs_requis = {
        "introduction",
        "corps",
        "conclusion"
    }

    champs_present = all(
        champ in structure_reponse
        for champ in champs_requis
    )

    champs_actifs = all(
        structure_reponse.get(champ) is True
        for champ in champs_requis
    )

    types_valides = {
        "explication",
        "conseil",
        "analyse",
        "orientation",
        "directe"
    }

    coherence = (
        type_reponse in types_valides
        and champs_present
        and champs_actifs
        and structure.get("structure_valide") is True
    )

    return {
        "coherence_valide": coherence,
        "succes": coherence,
        "statut": (
            "controle_coherence_reponse_termine"
            if coherence
            else "controle_coherence_reponse_echec"
        ),
        "type_reponse": type_reponse,
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia75_evaluer_coherence_reponse(controle):
    if not isinstance(controle, dict):
        return {
            "succes": False,
            "statut": "evaluation_coherence_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": controle.get("coherence_valide") is True,
        "statut": "evaluation_coherence_reponse_terminee",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia75_resumer_coherence_reponse(controle):
    if not isinstance(controle, dict):
        return {
            "succes": False,
            "statut": "resume_coherence_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": controle.get("coherence_valide") is True,
        "statut": "resume_coherence_reponse_termine",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }

# ============================================================
# FIN MIA V75 — BRIQUE 11
# ============================================================

# ============================================================
# MIA V76 — BRIQUE 12 : VALIDATION FINALE DE LA REPONSE
# ============================================================

def mia76_valider_reponse_finale(controle_coherence):
    """
    Valide la réponse après le contrôle de cohérence V75.

    Cette brique est uniquement décisionnelle :
    aucune génération, aucune exécution et aucune
    modification de données externes.
    """

    if not isinstance(controle_coherence, dict):
        return {
            "validation_finale_valide": False,
            "succes": False,
            "statut": "validation_finale_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    coherence_valide = (
        controle_coherence.get("coherence_valide") is True
    )

    validation = coherence_valide

    return {
        "validation_finale_valide": validation,
        "succes": validation,
        "statut": (
            "validation_finale_reponse_terminee"
            if validation
            else "validation_finale_reponse_echec"
        ),
        "type_reponse": controle_coherence.get("type_reponse"),
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia76_evaluer_validation_finale(validation):
    if not isinstance(validation, dict):
        return {
            "succes": False,
            "statut": "evaluation_validation_finale_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": (
            validation.get("validation_finale_valide") is True
        ),
        "statut": "evaluation_validation_finale_terminee",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }


def mia76_resumer_validation_finale(validation):
    if not isinstance(validation, dict):
        return {
            "succes": False,
            "statut": "resume_validation_finale_invalide",
            "execution_autorisee": False,
            "execution_interdite": True,
            "donnees_modifiees": False
        }

    return {
        "succes": (
            validation.get("validation_finale_valide") is True
        ),
        "statut": "resume_validation_finale_termine",
        "execution_autorisee": False,
        "execution_interdite": True,
        "donnees_modifiees": False
    }

# ============================================================
# FIN MIA V76 — BRIQUE 12
# ============================================================
