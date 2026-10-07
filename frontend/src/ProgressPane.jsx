import { LEVEL_NAMES } from "./constants.js";

function NextStep({ profile }) {
  const nxt = profile.next_skill;
  return (
    <div id="next-step" className="next-step">
      <strong>Prochaine étape</strong>
      {nxt ? (
        <div className="card">
          <b>{nxt.title}</b> (niveau {nxt.level})<br />{nxt.description}
        </div>
      ) : (
        <div className="card">Cursus complet — félicitations !</div>
      )}
    </div>
  );
}

function Fragile({ profile }) {
  const fragile = profile.fragile || {};
  const byKind = fragile.by_kind || [];
  const bySkill = fragile.by_skill || [];
  return (
    <div id="fragile" className="fragile">
      <strong>Notions fragiles</strong>
      {byKind.length || bySkill.length ? (
        <div>
          {byKind.map((r, i) => (
            <span key={`k${i}`} className="tag">{r.error_kind} ×{r.occurrences}</span>
          ))}
          {bySkill.map((r, i) => (
            <span key={`s${i}`} className="tag">{r.skill_slug} : {r.error_kind}</span>
          ))}
        </div>
      ) : (
        <div className="card" style={{ color: "var(--muted)" }}>Aucune erreur récurrente. Continue ainsi !</div>
      )}
    </div>
  );
}

const STATUS_BADGES = {
  validated_by_test: { cls: "badge-test", label: "✓ test" },
  auto_declared: { cls: "badge-declared", label: "◈ déclaré" },
};

function SkillsTree({ progressTree, onSelectSkill }) {
  return (
    <div id="skills-tree" className="skills-tree">
      {[1, 2, 3, 4].map((level) => {
        const skills = (progressTree || []).filter((s) => s.level === level);
        if (!skills.length) return null;
        return (
          <div key={level}>
            <div className="level-heading">{LEVEL_NAMES[level]}</div>
            {skills.map((s, i) => {
              const cls = s.validated
                ? s.status === "auto_declared" ? "validated auto-declared" : "validated"
                : s.unlocked ? "unlocked" : "locked";
              const badge = s.validated
                ? STATUS_BADGES[s.status] || STATUS_BADGES.validated_by_test
                : null;
              const clickable = s.validated && onSelectSkill;
              return (
                <div
                  key={i}
                  className={`skill ${cls}${clickable ? " clickable" : ""}`}
                  onClick={clickable ? () => onSelectSkill(s.slug) : undefined}
                  title={clickable
                    ? "Cliquer pour revenir sur cette compétence (découverte relancée, validations conservées)"
                    : undefined}
                  role={clickable ? "button" : undefined}
                >
                  <span className="dot" />
                  <span className="skill-title">{s.title}</span>
                  {badge && <span className={`skill-badge ${badge.cls}`}>{badge.label}</span>}
                </div>
              );
            })}
            {skills.some((s) => s.validated) && (
              <div className="level-hint">
                Clique une compétence acquise pour la retravailler.
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function ProgressPane({ profile, onSelectSkill }) {
  if (!profile) return <section className="progress-pane" />;
  return (
    <section className="progress-pane">
      <div className="pane-title"><span>Ma progression</span></div>
      <NextStep profile={profile} />
      <Fragile profile={profile} />
      <SkillsTree progressTree={profile.progress_tree} onSelectSkill={onSelectSkill} />
    </section>
  );
}
