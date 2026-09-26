"""ALKAH-BRAIN V12.27.0 — Qualification comparative des scénarios."""

from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class Scenario:
    nom: str
    score: float
    confiance: float = 0.0
    avantages: tuple[str, ...] = ()
    limites: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.nom.strip():
            raise ValueError("Nom obligatoire")
        if not 0 <= self.score <= 100:
            raise ValueError("Score entre 0 et 100")
        if not 0 <= self.confiance <= 100:
            raise ValueError("Confiance entre 0 et 100")


def normaliser_scenario(donnees: dict[str, Any]) -> Scenario:
    return Scenario(
        nom=str(donnees["nom"]),
        score=float(donnees.get("score", 0)),
        confiance=float(donnees.get("confiance", 0)),
        avantages=tuple(str(x) for x in donnees.get("avantages", ())),
        limites=tuple(str(x) for x in donnees.get("limites", ())),
    )


def qualifier_scenarios(
    scenarios: list[Scenario | dict[str, Any]],
) -> dict[str, Any]:
    if not scenarios:
        return {
            "statut": "vide",
            "nombre_scenarios": 0,
            "classement": [],
            "meilleur_scenario": None,
            "decision_automatique": False,
        }

    controles = []

    for element in scenarios:
        if isinstance(element, Scenario):
            controles.append(element)
        elif isinstance(element, dict):
            controles.append(normaliser_scenario(element))
        else:
            raise TypeError("Scénario invalide")

    classement = sorted(
        controles,
        key=lambda x: (x.score, x.confiance),
        reverse=True,
    )

    meilleur = classement[0]

    return {
        "statut": "ok",
        "nombre_scenarios": len(classement),
        "classement": [asdict(x) for x in classement],
        "meilleur_scenario": asdict(meilleur),
        "ecarts": [
            {
                "nom": x.nom,
                "ecart_avec_meilleur": round(meilleur.score - x.score, 4),
            }
            for x in classement
        ],
        "decision_automatique": False,
        "validation_humaine_requise": True,
    }


def resume_qualification(
    scenarios: list[Scenario | dict[str, Any]],
) -> str:
    resultat = qualifier_scenarios(scenarios)

    if resultat["statut"] == "vide":
        return "Aucun scénario à qualifier."

    meilleur = resultat["meilleur_scenario"]

    return "\n".join(
        [
            "QUALIFICATION COMPARATIVE DES SCENARIOS",
            f"Nombre de scénarios : {resultat['nombre_scenarios']}",
            f"Scénario en tête : {meilleur['nom']}",
            f"Score : {meilleur['score']}",
            f"Confiance : {meilleur['confiance']}",
            "Décision automatique : NON",
            "Validation humaine requise : OUI",
        ]
    )


__all__ = [
    "Scenario",
    "normaliser_scenario",
    "qualifier_scenarios",
    "resume_qualification",
]
