import { useState } from "react";
import { ONBOARDING_LEVELS } from "./constants.js";

/**
 * Écran d'introduction (onboarding) : contenu statique, zéro appel API.
 * `progressTree` permet d'afficher le compteur de compétences validées par
 * niveau quand on le rouvre via le bouton « ? ».
 * `onStart(level)` transmet le niveau de départ choisi (1 par défaut).
 */
export default function OnboardingModal({ open, progressTree, onStart }) {
  const [startLevel, setStartLevel] = useState(1);
  if (!open) return null;

  const started = (progressTree || []).some((s) => s.validated);
  const byLevel = (lv) => (progressTree || []).filter((s) => s.level === lv);
  const validatedIn = (lv) => byLevel(lv).filter((s) => s.validated).length;

  return (
    <div className={`modal-overlay${open ? "" : " hidden"}`}>
      <div className="modal onb-modal">
        <h2>Bienvenue — qu'est-ce que l'algorithmique ?</h2>
        <p className="onb-intro">
          Programmer, c'est d'abord <b>raisonner</b> : découper un problème en étapes
          précises que la machine peut exécuter. C'est ça, l'algorithmique — la logique
          derrière un programme, <b>indépendante du langage</b>. Python, C, JavaScript
          ou Java ne sont que des façons différentes d'écrire la même logique : ici,
          tu choisiras ton langage, mais la progression restera la même.
        </p>
        <p className="onb-sub">Ton parcours se fait en 4 niveaux :</p>
        <div className="onb-levels">
          {ONBOARDING_LEVELS.map((lv) => (
            <div key={lv.level} className="onb-level">
              <div className="onb-level-head">
                <span className="onb-level-num">Niveau {lv.level}</span>
                <span className="onb-level-title">{lv.title}</span>
                {started && (
                  <span className="onb-progress">
                    {validatedIn(lv.level)}/{byLevel(lv.level).length}
                  </span>
                )}
              </div>
              <p>{lv.desc}</p>
            </div>
          ))}
        </div>
        <p className="onb-hint">
          À chaque compétence : une théorie courte avec une image, un exemple dans ton
          langage, puis à toi d'écrire le code — je ne donnerai jamais la solution
          directement, seulement des indices pour te faire trouver.
        </p>
        <div className="onb-start-level">
          <label className="onb-level-question">
            Tu débutes complètement, ou tu veux commencer à un niveau précis ?
          </label>
          <div className="onb-level-options" role="radiogroup">
            {ONBOARDING_LEVELS.map((lv) => (
              <label key={lv.level} className="onb-level-option">
                <input
                  type="radio"
                  name="start-level"
                  value={lv.level}
                  checked={startLevel === lv.level}
                  onChange={() => setStartLevel(lv.level)}
                />
                <span>Niveau {lv.level} — {lv.title}</span>
              </label>
            ))}
          </div>
          <p className="onb-level-warning">
            Si tu n'es pas sûr, commence au niveau 1 — chaque niveau suppose que tu
            maîtrises les précédents.
          </p>
        </div>
        <div className="modal-actions">
          <button
            id="btn-onboarding-start"
            className="btn btn-primary"
            onClick={() => onStart(startLevel)}
          >
            Commencer
          </button>
        </div>
      </div>
    </div>
  );
}
