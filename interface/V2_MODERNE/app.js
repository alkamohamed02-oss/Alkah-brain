"use strict";

/*
 * MIA — ALKAH-BRAIN
 * Interface V2 Moderne
 *
 * Interface locale.
 * Aucun lancement automatique d'action.
 * La validation humaine reste obligatoire.
 */

const startButton = document.getElementById("startButton");

function echapperHTML(texte) {
  return String(texte)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function ouvrirDialogueMIA() {
  const ancien = document.querySelector(".mia-dialogue");

  if (ancien) {
    ancien.remove();
  }

  const dialogue = document.createElement("section");
  dialogue.className = "mia-dialogue";

  dialogue.innerHTML = `
    <div class="mia-dialogue-backdrop"></div>

    <div class="mia-dialogue-box">
      <button class="mia-dialogue-close" aria-label="Retour">←</button>

      <div class="mia-dialogue-logo">
        <img src="mia_logo.png" alt="MIA">
      </div>

      <p class="kicker">MIA · ALKAH-BRAIN</p>

      <h2>Que souhaitez-vous faire ?</h2>

      <p class="mia-dialogue-intro">
        Expliquez votre besoin avec vos propres mots.
        MIA va analyser votre demande et vous accompagner.
      </p>

      <textarea
        id="miaQuestionV2"
        placeholder="Écrivez simplement votre question ou votre besoin..."
        rows="5"
      ></textarea>

      <div class="mia-dialogue-status" id="miaStatusV2">
        👤 Vous gardez la décision finale.
      </div>

      <button class="mia-send" id="miaSendV2">
        ✦ Demander à MIA
      </button>

      <div class="mia-security">
        🔒 Lecture seule · ⚡ Exécution automatique : OFF
      </div>

      <div class="mia-response" id="miaResponseV2"></div>
    </div>
  `;

  document.body.appendChild(dialogue);

  const fermer = () => dialogue.remove();

  dialogue
    .querySelector(".mia-dialogue-close")
    .addEventListener("click", fermer);

  dialogue
    .querySelector(".mia-dialogue-backdrop")
    .addEventListener("click", fermer);

  const input = dialogue.querySelector("#miaQuestionV2");
  const send = dialogue.querySelector("#miaSendV2");
  const status = dialogue.querySelector("#miaStatusV2");
  const response = dialogue.querySelector("#miaResponseV2");

  input.focus();

  async function envoyerQuestion() {
    const question = input.value.trim();

    if (!question) {
      input.focus();
      return;
    }

    miaDisqueEtat("recherche");
    send.disabled = true;
    status.textContent = "MIA analyse votre demande...";

    try {
      if (typeof miaBridgeV13EnvoyerQuestion !== "function") {
        throw new Error("Pont MIA indisponible.");
      }

      const resultat = await miaBridgeV13EnvoyerQuestion(
        question,
        "interface_V2_MODERNE"
      );

      if (!resultat || !resultat.ok || !resultat.donnees) {
        throw new Error("Réponse MIA invalide.");
      }

      const reponse =
        resultat.donnees.reponse ||
        "MIA n'a pas fourni de réponse.";

      response.insertAdjacentHTML("beforeend", `
        <div class="mia-response-card">
          <p><strong>Votre demande</strong></p>
          <p>${echapperHTML(question)}</p>

          <hr>

          <p><strong>Réponse de MIA</strong></p>
          <p>${echapperHTML(reponse)}</p>

          <div class="mia-validation">
            <p><strong>🧠 J’ai compris votre demande</strong></p>
            <p>Vous souhaitez travailler sur : <strong>${echapperHTML(resultat.donnees.dialogue_v12_13?.projet_actif || resultat.donnees.continuite_v12?.projet || "votre demande")}</strong></p>
            <p>${echapperHTML(resultat.donnees.decision_v12_13_3?.prochaine_action?.action || "MIA va préciser avec vous la prochaine étape.")}</p>
            <small>👤 Vous gardez toujours la décision finale · 🔒 Aucune action automatique</small>
          </div>
        </div>
      `);

      status.textContent = "✓ MIA a compris votre demande.";
      input.value = "";
      miaDisqueEtat("retour");
      send.disabled = false;
      const derniereReponse = response.lastElementChild;
      derniereReponse?.scrollIntoView({ behavior: "smooth", block: "center" });
      setTimeout(() => {
        window.scrollBy({ top: -140, behavior: "smooth" });
      }, 350);

      input.blur();

      const modifier = document.getElementById("miaModifierV2");
      const continuer = document.getElementById("miaContinuerV2");

      modifier?.addEventListener("click", () => {
        status.textContent = "✏️ Modifiez votre demande, puis envoyez-la à nouveau.";
        input.focus();
      });

      continuer?.addEventListener("click", async () => {
        status.textContent = "✓ Validation reçue. MIA prépare la suite…";
        continuer.textContent = "✓ Validé";
        continuer.disabled = true;
        modifier.disabled = true;

        try {
          const suite = await miaBridgeV13EnvoyerQuestion(
            "Je valide votre compréhension. Poursuivez avec ma demande : " + question,
            "interface_V2_MODERNE"
          );

          const suiteReponse =
            suite?.donnees?.continuite_v12?.prochaine_etape?.prochaine_etape ||
            suite?.donnees?.reponse ||
            "MIA est prête à poursuivre avec vous.";

          const suiteBloc = document.createElement("div");
          suiteBloc.className = "mia-next-step";
          suiteBloc.innerHTML = `
            <p><strong>➡️ Prochaine étape proposée par MIA</strong></p>
            <p>${echapperHTML(suiteReponse)}</p>
            <small>👤 Vous gardez toujours la décision finale · 🔒 Aucune action automatique</small>
            <div class="mia-followup">
              <textarea id="miaFollowupInput" placeholder="Écrivez votre réponse à MIA..."></textarea>
              <button id="miaFollowupSend" type="button">Envoyer à MIA</button>
            </div>
          `;

          const followupInput = suiteBloc.querySelector("#miaFollowupInput");
          const followupSend = suiteBloc.querySelector("#miaFollowupSend");

          followupSend?.addEventListener("click", async () => {
            const reponseUtilisateur = followupInput?.value.trim();

            if (!reponseUtilisateur) {
              followupInput?.focus();
              return;
            }

            followupSend.disabled = true;
            followupSend.textContent = "MIA analyse...";

            try {
              const suivi = await miaBridgeV13EnvoyerQuestion(
                reponseUtilisateur,
                "interface_V2_MODERNE"
              );

              const suiviReponse =
                suivi?.donnees?.reponse ||
                "MIA n'a pas fourni de réponse.";

              const suiviBloc = document.createElement("div");
              suiviBloc.className = "mia-followup-response";
              suiviBloc.innerHTML = `
                <p><strong>💬 Réponse de MIA</strong></p>
                <p>${echapperHTML(suiviReponse)}</p>
                <small>👤 Vous gardez toujours la décision finale · 🔒 Aucune action automatique</small>
              `;

              suiteBloc.appendChild(suiviBloc);
              followupInput.value = "";
              followupSend.textContent = "Envoyer à MIA";
              followupSend.disabled = false;
            } catch (erreur) {
              console.error("Erreur réponse MIA :", erreur);
              followupSend.textContent = "Réessayer";
              followupSend.disabled = false;
            }
          });

          response.querySelector(".mia-response-card")?.appendChild(suiteBloc);
          status.textContent = "✓ MIA a préparé la suite.";
        } catch (erreur) {
          console.error("Erreur suite MIA :", erreur);
          status.textContent = "✓ Validation enregistrée. MIA attend votre prochaine décision.";
        }
      });

    } catch (erreur) {
      if (erreur?.name === "AbortError") {
        status.textContent = "⏹️ Recherche arrêtée.";
        miaDisqueEtat("retour");
        send.disabled = false;
        return;
      }

      console.error("Erreur MIA :", erreur);

      status.textContent =
        "Impossible de joindre MIA pour le moment.";

      response.innerHTML = `
        <div class="mia-response-card">
          <p><strong>Connexion non disponible.</strong></p>
          <p>
            Vérifiez que le serveur local MIA est bien démarré
            sur le port 8765.
          </p>
        </div>
      `;

      send.disabled = false;
    }
  }

  send.addEventListener("click", envoyerQuestion);

  input.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      envoyerQuestion();
    }
  });
}

if (startButton) {
  startButton.addEventListener("click", ouvrirDialogueMIA);
}

/* Navigation douce */

document.querySelectorAll('nav a[href^="#"]').forEach((lien) => {
  lien.addEventListener("click", (event) => {
    const cible = document.querySelector(lien.getAttribute("href"));

    if (cible) {
      event.preventDefault();
      cible.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  });
});


const backButton = document.getElementById("backButton");

function miaDisqueEtat(etat) {
  if (!backButton) return;

  const etats = {
    retour: { symbole: "←", label: "Retour" },
    recherche: { symbole: "⌕", label: "Recherche" },
    arret: { symbole: "■", label: "Arrêt" }
  };

  const config = etats[etat] || etats.retour;
  backButton.textContent = config.symbole;
  backButton.setAttribute("aria-label", config.label);
  backButton.title = config.label;
  backButton.dataset.etat = etat;
}

backButton?.addEventListener("click", () => {
  const etat = backButton.dataset.etat || "retour";

  if (etat === "arret") {
    if (typeof miaBridgeV13ArreterQuestion === "function") {
      miaBridgeV13ArreterQuestion();
    }
    return;
  }

  if (etat === "retour") {
    const accueil = document.getElementById("accueil");
    if (accueil) accueil.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});

miaDisqueEtat("retour");

const menuButton = document.getElementById("menu");
const mobileMenu = document.getElementById("mobile");

if (menuButton && mobileMenu) {
  menuButton.addEventListener("click", () => {
    mobileMenu.style.display =
      mobileMenu.style.display === "flex" ? "none" : "flex";
  });
}
