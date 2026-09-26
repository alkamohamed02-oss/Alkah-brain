from http.server import BaseHTTPRequestHandler, HTTPServer
import json

from mia_passerelle import charger_alkah_brain

# ALKAH-BRAIN V12.96 — ROUTAGE SELECTIF
import importlib.util as _mia96_importlib_util
from pathlib import Path as _mia96_Path

_mia96_routeur_path = (
    _mia96_Path(__file__).resolve().parent
    / "developpement"
    / "V12.94.0"
    / "socle"
    / "mia_v12_94_routeur_progression.py"
)

_mia96_spec = _mia96_importlib_util.spec_from_file_location(
    "mia_v12_94_routeur_progression",
    _mia96_routeur_path
)

if _mia96_spec is None or _mia96_spec.loader is None:
    raise ImportError("Impossible de charger le routeur V12.94")

_mia96_routeur_module = _mia96_importlib_util.module_from_spec(
    _mia96_spec
)

_mia96_spec.loader.exec_module(_mia96_routeur_module)

mia96_router = _mia96_routeur_module.router
mia96_statut = _mia96_routeur_module.statut


# ALKAH-BRAIN V12.91 — pont de raccordement sécurisé
import importlib.util as _mia91_importlib_util
from pathlib import Path as _mia91_Path

_mia91_pont_path = (
    _mia91_Path(__file__).resolve().parent
    / "developpement"
    / "V12.91.0"
    / "socle"
    / "mia_v12_91_pont_serveur.py"
)

_mia91_spec = _mia91_importlib_util.spec_from_file_location(
    "mia_v12_91_pont_serveur",
    _mia91_pont_path
)

if _mia91_spec is None or _mia91_spec.loader is None:
    raise ImportError("Impossible de charger le pont V12.91")

_mia91_pont_module = _mia91_importlib_util.module_from_spec(
    _mia91_spec
)

_mia91_spec.loader.exec_module(_mia91_pont_module)

mia91_statut_pont = _mia91_pont_module.statut_pont

from mia_comprehension_conversation import mia_comprendre_demande
from mia_evolution_v3_v11 import mia_v3_agir
from mia_evolution_v3_v11 import mia_v5_creer_objectif, mia_v5_creer_plan
from mia_evolution_v3_v11 import mia_v6_comparer, mia_v6_decider
from mia_evolution_v3_v11 import mia_v7_structurer_projet, mia_v4_contexte, mia_v4_ajouter
from mia_evolution_v3_v11 import (
    mia_v8_agent, mia_v8_registre_agents,
    mia_v9_outil, mia_v9_registre_outils,
    mia_v10_automatisation, mia_v11_architecture
)


HOST = "127.0.0.1"
PORT = 8765


moteur = charger_alkah_brain()
from mia_v12_continuite import (
    mia_v12_continuite,
    mia_v12_statut_global
)
from mia_v12_integration import mia12_interroger_moteur

CONTEXTES_MIA_V4 = {}

REGISTRE_AGENTS_V8 = mia_v8_registre_agents()
REGISTRE_OUTILS_V9 = mia_v9_registre_outils()
ARCHITECTURE_V11 = mia_v11_architecture()


class MIAHandler(BaseHTTPRequestHandler):

    def _reponse(self, code, donnees):
        contenu = json.dumps(
            donnees,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        self.wfile.write(contenu)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/statut":
            self._reponse(
                200,
                {
                    "statut": "ok",
                    "moteur": "ALKAH-BRAIN",
                    "version": "V76"
                }
            )
        else:
            self._reponse(
                404,
                {"erreur": "Route introuvable"}
            )

    def do_POST(self):
        if self.path == "/api/memoire":
            try:
                longueur = int(self.headers.get("Content-Length", 0))
                donnees = json.loads(self.rfile.read(longueur).decode("utf-8"))
                question = str(donnees.get("question", "")).strip()
                resultat = moteur.mia_interroger(question)
                self._reponse(200, resultat)
            except Exception as e:
                self._reponse(500, {
                    "erreur": type(e).__name__,
                    "message": str(e)
                })
            return

        if self.path != "/api/question":
            self._reponse(
                404,
                {"erreur": "Route introuvable"}
            )
            return

        try:
            longueur = int(
                self.headers.get("Content-Length", 0)
            )

            donnees = json.loads(
                self.rfile.read(longueur).decode("utf-8")
            )

            question = str(
                donnees.get("question", "")
            ).strip()

            session_id = str(
                donnees.get("session_id", "session_principale")
            ).strip()

            if session_id not in CONTEXTES_MIA_V4:
                CONTEXTES_MIA_V4[session_id] = mia_v4_contexte()

            if not question:
                self._reponse(
                    400,
                    {"erreur": "Question vide"}
                )
                return

            # =================================================
            # V12.96 : ROUTAGE SELECTIF SERVEUR
            # =================================================
            # V12.94 decide de la voie fonctionnelle.
            # Le moteur historique reste intact comme fallback.
            # Aucune action irreversible n'est declenchee ici.

            routage_v12_96 = mia96_router(question)

            intention_conversationnelle = mia_comprendre_demande(question)

            action_v3 = mia_v3_agir(intention_conversationnelle)

            CONTEXTES_MIA_V4[session_id] = mia_v4_ajouter(
                CONTEXTES_MIA_V4[session_id],
                question,
                intention_conversationnelle,
                action_v3["action"]
            )

            integration_v1212 = mia12_interroger_moteur(
                question,
                moteur.mia_repondre,
                session_id=session_id,
                moteur_memoire=moteur,
                memoire_ecriture=True,
                intention_conversationnelle=intention_conversationnelle
            )

            contexte_v1212 = integration_v1212.get("contexte", {})
            if isinstance(contexte_v1212, dict):
                CONTEXTES_MIA_V4[session_id]["objectif"] = contexte_v1212.get("objectif_actif")
                CONTEXTES_MIA_V4[session_id]["projet"] = contexte_v1212.get("projet_actif")

            resultat = integration_v1212.get(
                "resultat_moteur",
                integration_v1212
            )

            # V12.96 : exposition du choix de routage
            if isinstance(resultat, dict):
                resultat["routage_v12_96"] = routage_v12_96

            # =================================================
            # V12.21 : EXPOSITION ORCHESTRATION MEMOIRE
            # =================================================
            # Détection uniquement.
            # Aucune écriture SQLite n'est autorisée ici.
            memoire_v12_21 = integration_v1212.get(
                "memoire_v12_21",
                {}
            )

            if isinstance(resultat, dict):
                resultat["memoire_v12_21"] = memoire_v12_21

            if isinstance(resultat, dict):
                resultat["dialogue_v12_12"] = {
                    "session_id": integration_v1212.get("session_id"),
                    "numero_tour": integration_v1212.get("numero_tour"),
                    "question_resolue": integration_v1212.get(
                        "question_resolue"
                    ),
                    "contexte": integration_v1212.get("contexte"),
                    "confirmation": integration_v1212.get(
                        "confirmation"
                    )
                }



            # =================================================
            # V12.13 : CONTINUITE DECISIONNELLE
            # =================================================
            # Exposition de la decision produite par la couche
            # V12.12.5 + V12.13.1.
            # Lecture seule : aucun changement de B34/V76/V12.11.

            decision_v12_13 = integration_v1212.get(
                "decision_v12_13",
                {}
            )

            if isinstance(resultat, dict):
                resultat["decision_v12_13"] = decision_v12_13

                resultat["dialogue_v12_13"] = {
                    "version": decision_v12_13.get("version"),
                    "continuation_detectee": decision_v12_13.get(
                        "continuation_detectee"
                    ),
                    "decisionnelle_active": decision_v12_13.get(
                        "decisionnelle_active"
                    ),
                    "projet_actif": decision_v12_13.get(
                        "projet_actif"
                    ),
                    "objectif_actif": decision_v12_13.get(
                        "objectif_actif"
                    ),
                    "sujet_actif": decision_v12_13.get(
                        "sujet_actif"
                    ),
                    "decision": decision_v12_13.get(
                        "decision"
                    ),
                    "horodatage": decision_v12_13.get(
                        "horodatage"
                    )
                }

            decision_v12_13_3 = integration_v1212.get("decision_v12_13_3", {})
            decision_v12_14 = integration_v1212.get("decision_v12_14", {})
            decision_v12_15 = integration_v1212.get("decision_v12_15", {})
            if isinstance(resultat, dict):
                resultat["decision_v12_13_3"] = decision_v12_13_3
                resultat["decision_v12_14"] = decision_v12_14
                resultat["decision_v12_15"] = decision_v12_15
            if isinstance(resultat, dict):
                resultat["intention_conversationnelle"] = intention_conversationnelle
                resultat["action_conversationnelle"] = action_v3["action"]
                resultat["prochaine_etape_conversationnelle"] = action_v3["prochaine_etape"]
                resultat["memoire_conversationnelle_v4"] = CONTEXTES_MIA_V4[session_id]

            # V5 : objectif et plan conversationnels
            if intention_conversationnelle in ("idee", "construction", "guide"):
                objectif_v5 = mia_v5_creer_objectif(question)
                resultat["objectif_v5"] = objectif_v5
                resultat["plan_v5"] = mia_v5_creer_plan(objectif_v5)

            # V6 : comparaison et aide à la décision
            if intention_conversationnelle == "comparaison":
                resultat["comparaison_v6"] = mia_v6_comparer(question)
                resultat["decision_v6"] = mia_v6_decider(resultat["comparaison_v6"])

            # V7 : structuration du projet
            if intention_conversationnelle in ("idee", "construction"):
                resultat["projet_structure_v7"] = mia_v7_structurer_projet(question)
            if "projet_structure_v7" in resultat:
                CONTEXTES_MIA_V4.setdefault(session_id, {})["structure_projet"] = resultat["projet_structure_v7"]

            # =================================================
            # V12 : CONTINUITE DU PROJET
            # =================================================

            contexte_v12 = dict(
                CONTEXTES_MIA_V4.get(session_id, {})
            )

            # =================================================
            # V12.12 : CONTEXTE DIALOGUE ACTIF
            # =================================================
            # La nouvelle couche dialogue V12.12 est la source
            # de continuité multi-tour. Ses informations sont
            # transmises en lecture au module V12 existant.
            dialogue_v1212 = integration_v1212.get(
                "contexte",
                {}
            )

            if isinstance(dialogue_v1212, dict):
                if dialogue_v1212.get("projet_actif"):
                    contexte_v12["projet"] = (
                        dialogue_v1212["projet_actif"]
                    )
                    contexte_v12["projet_actif"] = (
                        dialogue_v1212["projet_actif"]
                    )

                if dialogue_v1212.get("objectif_actif"):
                    contexte_v12["objectif"] = (
                        dialogue_v1212["objectif_actif"]
                    )
                    contexte_v12["objectif_actif"] = (
                        dialogue_v1212["objectif_actif"]
                    )

                if dialogue_v1212.get("sujet_actif"):
                    contexte_v12["sujet_actif"] = (
                        dialogue_v1212["sujet_actif"]
                    )

            # V5 : objectif et plan
            if "objectif_v5" in resultat:
                contexte_v12["objectif_v5"] = (
                    resultat["objectif_v5"]
                )
                contexte_v12["objectif"] = (
                    resultat["objectif_v5"]
                )

            if "plan_v5" in resultat:
                contexte_v12["plan_v5"] = (
                    resultat["plan_v5"]
                )
                contexte_v12["plan"] = (
                    resultat["plan_v5"]
                )

            # V7 : structure du projet
            if "projet_structure_v7" in resultat:
                contexte_v12["structure_projet"] = (
                    resultat["projet_structure_v7"]
                )

            # V12 : continuité réelle du projet
            # Lecture seule : on réutilise uniquement les informations
            # déjà présentes dans le contexte courant.
            if "structure_projet" not in contexte_v12:
                structure_existante = (
                    CONTEXTES_MIA_V4.get(session_id, {})
                    .get("structure_projet")
                )
                if structure_existante:
                    contexte_v12["structure_projet"] = (
                        structure_existante
                    )

            if "plan" not in contexte_v12:
                plan_existant = (
                    CONTEXTES_MIA_V4.get(session_id, {})
                    .get("plan")
                )
                if plan_existant:
                    contexte_v12["plan"] = plan_existant

            # =================================================
            # V12.9 : LECTURE DES MEMOIRES EXISTANTES
            # =================================================
            # Lecture seule depuis la mémoire V76.
            # Aucune écriture SQLite.
            chargeur_memoires_v12 = getattr(
                moteur,
                "mia_charger_memoires_apprentissage_sqlite",
                None
            )

            if callable(chargeur_memoires_v12):
                memoires_v12 = chargeur_memoires_v12()
            else:
                memoires_v12 = []

            # Les décisions ne sont transmises que si elles
            # existent déjà dans le résultat du moteur.
            decisions_v12 = [dict(zip(("id","document_id1","document_id2","score_global","confiance","signaux","raisons","decision","action","created_at"), d)) if isinstance(d, tuple) else d for d in (list(moteur.consulter_decisions()) if callable(getattr(moteur, "consulter_decisions", None)) else [])]

            for cle_decisions in (
                "decision_history",
                "decisions",
                "decisions_anterieures"
            ):
                valeur = resultat.get(cle_decisions)

                if isinstance(valeur, list):
                    decisions_v12.extend(valeur)

            resultat["continuite_v12"] = (
                mia_v12_continuite(
                    question,
                    contexte_v12.get("projet"),
                    contexte_v12,
                    decisions_v12,
                    memoires_v12
                )
            )

            resultat["statut_v12"] = mia_v12_statut_global()

            mission_v8_v10 = (
                contexte_v12.get("objectif")
                or contexte_v12.get("objectif_actif")
                or question
            )

            resultat["agent_v8"] = mia_v8_agent(
                intention_conversationnelle,
                mission_v8_v10
            )
            resultat["outils_v9"] = REGISTRE_OUTILS_V9
            resultat["automatisation_v10"] = mia_v10_automatisation(mission_v8_v10)
            resultat["architecture_v11"] = ARCHITECTURE_V11

            self._reponse(
                200,
                resultat
            )

        except Exception as e:
            self._reponse(
                500,
                {
                    "erreur": type(e).__name__,
                    "message": str(e)
                }
            )

    def log_message(self, format, *args):
        print("[MIA SERVEUR]", format % args)


print("======================================")
print("        SERVEUR MIA — ALKAH-BRAIN")
print("======================================")
print(f"Adresse : http://{HOST}:{PORT}")
print("Moteur  : ALKAH-BRAIN V76")
print("Statut  : SERVEUR PRÊT")
print("======================================")

serveur = HTTPServer((HOST, PORT), MIAHandler)

try:
    serveur.serve_forever()
except KeyboardInterrupt:
    print("\nArrêt du serveur MIA.")
    serveur.server_close()
