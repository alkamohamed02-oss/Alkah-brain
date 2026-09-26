"use strict";

/*
 * MIA — ALKAH-BRAIN
 * Pont Interface V1
 *
 * Mode actuel : PREPARATION
 * Connexion API : DESACTIVEE
 * Execution automatique : DESACTIVEE
 * Autorisation utilisateur : REQUISE
 */

const MIA_BRIDGE_V12_VERSION = "V1.2";

const MIA_BRIDGE_CONFIG = Object.freeze({
  connexion_api_preparee: true,
  execution_automatique: false,
  lecture_seule: true,
  autorisation_utilisateur: true
});

function miaBridgeStatut() {
  return {
    version: MIA_BRIDGE_V12_VERSION,
    actif: true,
    mode: "API_PREPARATION",
    ...MIA_BRIDGE_CONFIG
  };
}

console.log("MIA BRIDGE V1 : PRET");
console.log("CONNEXION_API = DESACTIVEE");
console.log("EXECUTION_AUTOMATIQUE = DESACTIVEE");
console.log("LECTURE_SEULE = ACTIVE");
console.log("AUTORISATION_UTILISATEUR = REQUISE");


/* =========================================================
 * MIA BRIDGE V1.1 — API PREPARATION
 * Connexion prévue vers 127.0.0.1:8765
 *
 * IMPORTANT :
 * - ce fichier est ISOLÉ
 * - non chargé par index.html
 * - aucune exécution automatique
 * - aucune commande système
 * - aucune modification des versions protégées
 * ========================================================= */

const MIA_API_URL = "http://127.0.0.1:8765";

function miaBridgeApiConfiguration() {
  return Object.freeze({
    version: MIA_BRIDGE_V12_VERSION,
    api_url: MIA_API_URL,
    execution_automatique: false,
    lecture_seule: true,
    autorisation_utilisateur: true
  });
}

console.log("MIA BRIDGE V1.1 : PREPARATION API — AUCUNE CONNEXION ACTIVE");
console.log("API =", MIA_API_URL);
console.log("EXECUTION_AUTOMATIQUE = DESACTIVEE");
console.log("LECTURE_SEULE = ACTIVE");
console.log("AUTORISATION_UTILISATEUR = REQUISE");


/* =========================================================
 * MIA BRIDGE V1.2
 * API QUESTION — DEVELOPPEMENT ISOLE
 *
 * V1.0 OFFICIELLE : INTACTE
 * INDEX OFFICIEL : INTACT
 *
 * SECURITE :
 * - execution automatique = false
 * - autorisation utilisateur = true
 * - aucune commande système
 * - aucun lancement automatique
 *
 * L'appel API est possible uniquement par appel
 * explicite de miaBridgeV12EnvoyerQuestion().
 * ========================================================= */

const MIA_BRIDGE_V13_VERSION = "V1.3";
const MIA_BRIDGE_V13_MODE = "API_QUESTION_STRUCTURED";

function miaBridgeV12PreparerQuestion(question, sessionId) {
  if (typeof question !== "string" || !question.trim()) {
    throw new Error("Question invalide.");
  }

  const session =
    typeof sessionId === "string" && sessionId.trim()
      ? sessionId.trim()
      : "session_interface_v12";

  return Object.freeze({
    endpoint: MIA_API_URL + "/api/question",
    method: "POST",
    payload: Object.freeze({
      question: question.trim(),
      session_id: session
    }),
    execution_automatique: false,
    autorisation_utilisateur: true
  });
}

let miaBridgeAbortController = null;
function miaBridgeV13ArreterQuestion() {
  if (miaBridgeAbortController) {
    miaBridgeAbortController.abort();
    miaBridgeAbortController = null;
    return true;
  }
  return false;
}

async function miaBridgeV13EnvoyerQuestion(question, sessionId) {
  const requete =
    miaBridgeV12PreparerQuestion(question, sessionId);

  miaBridgeAbortController = new AbortController();

  if (typeof miaDisqueEtat === "function") {
    miaDisqueEtat("arret");
  }

  const reponse = await fetch(
    requete.endpoint,
    {
      method: requete.method,
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requete.payload),
      cache: "no-store",
      signal: miaBridgeAbortController.signal
    }
  );

  const texte = await reponse.text();
  miaBridgeAbortController = null;

  let donnees = null;

  try {
    donnees = JSON.parse(texte);
  } catch (erreur) {
    donnees = null;
  }

  return Object.freeze({
    version: MIA_BRIDGE_V13_VERSION,
    http_status: reponse.status,
    ok: reponse.ok,
    question: question.trim(),
    session_id:
      typeof sessionId === "string" && sessionId.trim()
        ? sessionId.trim()
        : "session_interface_v12",
    reponse_brute: texte,
    donnees: donnees,
    execution_automatique: false,
    lecture_seule: true,
    autorisation_utilisateur: true
  });
}

console.log("MIA BRIDGE V1.3 : API QUESTION STRUCTUREE");
console.log("VERSION =", MIA_BRIDGE_V13_VERSION);
console.log("MODE =", MIA_BRIDGE_V13_MODE);
console.log("EXECUTION_AUTOMATIQUE = DESACTIVEE");
console.log("AUTORISATION_UTILISATEUR = REQUISE");
