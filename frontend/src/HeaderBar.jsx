export default function HeaderBar({
  students, studentId, onStudentChange, onNewProfile, onDeleteProfile,
  language, onLanguageChange, exercises, exerciseSlug, onExerciseChange,
  profile, onAbout,
}) {
  return (
    <header>
      <div className="brand">
        <h1>TAlgo Mentor</h1>
        <span className="subtitle">Algorithmique — Python · C · JavaScript · Java</span>
      </div>
      <div className="header-controls">
        <label htmlFor="profile-select">Profil</label>
        <select
          id="profile-select"
          value={studentId ?? ""}
          onChange={(e) => onStudentChange(Number(e.target.value))}
        >
          {students.map((s) => (
            <option key={s.id} value={s.id}>
              {s.display_name} ({s.validated_count})
            </option>
          ))}
        </select>
        <button className="btn btn-small" onClick={onNewProfile} title="Créer un nouveau profil apprenant">+ Nouveau</button>
        <button className="btn btn-small" onClick={onDeleteProfile} title="Supprimer le profil actif (avec confirmation)">Supprimer</button>

        <label htmlFor="language-select">Langage</label>
        <select id="language-select" value={language} onChange={(e) => onLanguageChange(e.target.value)}>
          <option value="python">Python</option>
          <option value="c">C</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
        </select>

        <label htmlFor="exercise-select">Exercice</label>
        <select id="exercise-select" value={exerciseSlug} onChange={(e) => onExerciseChange(e.target.value)}>
          <option value="">— Prochaine étape du cursus —</option>
          {exercises.map((ex) => (
            <option key={ex.slug} value={ex.slug}>{ex.title}</option>
          ))}
        </select>

        {profile && (
          <span id="level-badge" className="level-badge">
            Niveau {profile.level} · {profile.validated_skills.length}/{profile.total_skills} compétences
          </span>
        )}
        <button id="btn-onboarding" className="btn btn-small" onClick={onAbout} title="À propos : qu'est-ce que l'algorithmique, et les 4 niveaux du cursus">?</button>
      </div>
    </header>
  );
}
