import React, { useCallback, useEffect, useRef, useState } from "react";
import { api } from "./api.js";
import {
  ONBOARDING_KEY,
  STARTER_CODE,
  STUDENT_KEY,
} from "./constants.js";
import CodeEditor from "./CodeEditor.jsx";
import HeaderBar from "./HeaderBar.jsx";
import ChatPane from "./ChatPane.jsx";
import ProgressPane from "./ProgressPane.jsx";
import OnboardingModal from "./OnboardingModal.jsx";
import ProfileModal from "./ProfileModal.jsx";

export default function App() {
  const [students, setStudents] = useState([]);
  const [studentId, setStudentId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [language, setLanguage] = useState("python");
  const [exerciseSlug, setExerciseSlug] = useState("");
  const [exercises, setExercises] = useState([]);
  const [messages, setMessages] = useState([]);
  const [consoleLines, setConsoleLines] = useState([]);
  const [busy, setBusy] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  const editorRef = useRef(null);
  const onboardingTreeRef = useRef([]);

  // ---------- helpers ----------
  const getCode = () => (editorRef.current ? editorRef.current.getValue() : "");
  const setCode = (text) => editorRef.current && editorRef.current.setValue(text);

  const consoleAppend = useCallback((text, cls = "info") => {
    setConsoleLines((lines) => [...lines, { text, cls }]);
  }, []);

  const addSystemMessage = useCallback((text) => {
    setMessages((m) => [...m, { kind: "system", text }]);
  }, []);

  // ---------- chat / découverte ----------
  const doIntro = useCallback(
    async (lang = language, slug = exerciseSlug, sid = studentId) => {
      try {
        const data = await api("/api/chat", {
          method: "POST",
          body: JSON.stringify({
            message: "",
            code: "",
            language: lang,
            exercise_slug: slug || null,
            student_id: sid,
            intro: true,
          }),
        });
        setMessages((m) => [...m, { kind: "tutor", reply: data.reply }]);
      } catch (err) {
        addSystemMessage("Impossible d'afficher la découverte : " + err.message);
      }
    },
    [language, exerciseSlug, studentId, addSystemMessage]
  );

  const doHelp = useCallback(
    async (text) => {
      if (busy) return;
      const message = (text || "").trim();
      if (!message && !getCode().trim()) {
        addSystemMessage("Écris du code ou pose une question, puis réessaie.");
        return;
      }
      setBusy(true);
      if (message) setMessages((m) => [...m, { kind: "user", text: message }]);
      setThinking(true);
      try {
        const data = await api("/api/chat", {
          method: "POST",
          body: JSON.stringify({
            message,
            code: getCode(),
            language,
            exercise_slug: exerciseSlug || null,
            student_id: studentId,
          }),
        });
        if (data.test_results) {
          consoleAppend("— Tests exécutés par le tuteur —", "info");
          for (const t of data.test_results) {
            consoleAppend(
              `[${t.passed ? "✔ PASS" : "✘ FAIL"}] ${t.label}`,
              t.passed ? "ok" : "fail"
            );
            if (!t.passed) {
              consoleAppend(`   attendu : ${JSON.stringify(t.expected)} | obtenu : ${JSON.stringify(t.actual)}`, "fail");
              if (t.stderr) consoleAppend(`   stderr  : ${t.stderr.trim()}`, "fail");
            }
          }
        }
        setMessages((m) => [...m, { kind: "tutor", reply: data.reply }]);
        if (data.skill_validated) {
          addSystemMessage(
            `Compétence « ${data.exercise ? data.exercise.title : ""} » validée ! ` +
            `Prochaine étape : ${data.profile.next_skill ? data.profile.next_skill.title : "cursus terminé"}.`
          );
        }
        try {
          const refreshed = await api(`/api/student?student_id=${studentId}`);
          setProfile(refreshed);
        } catch { /* non bloquant */ }
      } catch (err) {
        addSystemMessage("Erreur : " + err.message);
      } finally {
        setThinking(false);
        setBusy(false);
      }
    },
    [busy, language, exerciseSlug, studentId, consoleAppend, addSystemMessage]
  );

  const doRun = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    consoleAppend(`— Exécution (${language})…`, "info");
    try {
      const result = await api("/api/run", {
        method: "POST",
        body: JSON.stringify({
          code: getCode(),
          language,
          student_id: studentId,
          exercise_slug: exerciseSlug || null,
        }),
      });
      if (result.mode === "tests") {
        for (const t of result.test_results) {
          consoleAppend(
            `[${t.passed ? "✔ PASS" : "✘ FAIL"}] ${t.label} — entrée: ${JSON.stringify(t.stdin)}`,
            t.passed ? "ok" : "fail"
          );
          if (!t.passed) {
            consoleAppend(`   attendu : ${JSON.stringify(t.expected)}`, "fail");
            consoleAppend(`   obtenu  : ${JSON.stringify(t.actual)}`, "fail");
            if (t.stderr) consoleAppend(`   stderr  : ${t.stderr.trim()}`, "fail");
          }
        }
        consoleAppend(
          result.all_passed
            ? "Tous les tests passent ! Réponds au tuteur dans le chat pour valider la compétence."
            : "Certains tests échouent — demande un indice au tuteur.",
          result.all_passed ? "ok" : "fail"
        );
      } else {
        const run = result.run;
        if (run.stdout) consoleAppend(run.stdout, run.ok ? "ok" : "fail");
        if (run.stderr) consoleAppend(run.stderr, "fail");
        if (!run.stdout && !run.stderr) consoleAppend("(aucune sortie)", "info");
        consoleAppend(`— terminé en ${run.duration_ms} ms (exit ${run.exit_code})`, "info");
      }
      const refreshed = await api(`/api/student?student_id=${studentId}`);
      setProfile(refreshed);
    } catch (err) {
      consoleAppend("Erreur : " + err.message, "fail");
    } finally {
      setBusy(false);
    }
  }, [busy, language, studentId, exerciseSlug, consoleAppend]);

  // ---------- profils ----------
  const maybeAutoOnboarding = useCallback((prof) => {
    if (!prof || !prof.id) return false;
    if (localStorage.getItem(ONBOARDING_KEY + prof.id) === "1") return false;
    if (prof.validated_skills.length > 0) return false;
    onboardingTreeRef.current = prof.progress_tree || [];
    setShowOnboarding(true);
    return true;
  }, []);

  const switchToStudent = useCallback(
    async (id) => {
      setStudentId(id);
      localStorage.setItem(STUDENT_KEY, String(id));
      const prof = await api(`/api/student?student_id=${id}`);
      setProfile(prof);
      setLanguage(prof.language);
      setExerciseSlug("");
      setMessages([]);
      setConsoleLines([]);
      setCode(STARTER_CODE[prof.language] || "");
      if (!maybeAutoOnboarding(prof)) {
        await doIntro(prof.language, "", id);
      }
    },
    [maybeAutoOnboarding, doIntro]
  );

  const createProfile = useCallback(
    async (name, lang) => {
      setShowProfileModal(false);
      try {
        const prof = await api("/api/students", {
          method: "POST",
          body: JSON.stringify({ display_name: name, language: lang }),
        });
        const data = await api("/api/students");
        setStudents(data.students);
        consoleAppend(`Profil « ${prof.display_name} » créé (id ${prof.id}).`, "info");
        await switchToStudent(prof.id);
      } catch (err) {
        addSystemMessage("Impossible de créer le profil : " + err.message);
      }
    },
    [consoleAppend, addSystemMessage, switchToStudent]
  );

  const deleteActiveProfile = useCallback(async () => {
    if (!studentId) return;
    const current = students.find((s) => s.id === studentId);
    const label = current ? `${current.display_name} (${current.validated_count})` : `profil ${studentId}`;
    const ok = window.confirm(
      `Supprimer définitivement le profil « ${label} » ?\n` +
      "Ses compétences validées, erreurs et historique de chat seront effacés."
    );
    if (!ok) return;
    try {
      await api(`/api/students/${studentId}`, { method: "DELETE" });
      localStorage.removeItem(STUDENT_KEY);
      const data = await api("/api/students");
      setStudents(data.students);
      if (data.students.length) await switchToStudent(data.students[0].id);
      consoleAppend("Profil supprimé.", "info");
    } catch (err) {
      addSystemMessage("Suppression impossible : " + err.message);
    }
  }, [studentId, students, consoleAppend, addSystemMessage, switchToStudent]);

  // ---------- actions header ----------
  const onLanguageChange = useCallback(
    async (lang) => {
      setLanguage(lang);
      if (studentId) {
        try {
          await api("/api/student/language", {
            method: "POST",
            body: JSON.stringify({ language: lang, student_id: studentId }),
          });
        } catch { /* non bloquant */ }
      }
      consoleAppend(`Langage changé : ${lang}`, "info");
    },
    [studentId, consoleAppend]
  );

  const onExerciseChange = useCallback(
    async (slug) => {
      setExerciseSlug(slug);
      const ex = exercises.find((e) => e.slug === slug);
      consoleAppend(
        slug ? `Exercice sélectionné : ${ex ? ex.title : slug}` : "Mode cursus : l'exercice de la prochaine étape sera utilisé.",
        "info"
      );
      await doIntro(language, slug, studentId);
    },
    [exercises, language, studentId, doIntro, consoleAppend]
  );

  const onStudentChange = useCallback(
    async (id) => {
      if (!id || id === studentId || busy) return;
      try {
        await switchToStudent(id);
        consoleAppend(`Profil changé (id ${id}).`, "info");
      } catch (err) {
        addSystemMessage("Impossible de changer de profil : " + err.message);
      }
    },
    [studentId, busy, switchToStudent, consoleAppend, addSystemMessage]
  );

  const onAbout = useCallback(() => {
    onboardingTreeRef.current = profile ? profile.progress_tree || [] : [];
    setShowOnboarding(true);
  }, [profile]);

  const onOnboardingStart = useCallback(
    async (startLevel) => {
      if (studentId) localStorage.setItem(ONBOARDING_KEY + studentId, "1");
      setShowOnboarding(false);
      try {
        if (startLevel > 1) {
          const res = await api("/api/student/start-level", {
            method: "POST",
            body: JSON.stringify({ student_id: studentId, level: startLevel }),
          });
          setProfile(res.profile);
          consoleAppend(
            `Départ au niveau ${startLevel} : ${res.declared_count} compétences ` +
            "des niveaux précédents marquées « acquises par déclaration ».",
            "info"
          );
        }
      } catch (err) {
        addSystemMessage("Impossible d'appliquer le niveau de départ : " + err.message);
      }
      // Première entrée dans la progression : lancer la découverte si le chat
      // est encore vide (le profil n'a pas encore vu sa première compétence).
      if (messages.length === 0) {
        await doIntro();
      }
    },
    [studentId, messages.length, doIntro, consoleAppend, addSystemMessage]
  );

  // Retour en arrière : cliquer une compétence déjà acquise pour en refaire
  // l'étape active (découverte relancée, validations suivantes conservées).
  const onSelectSkill = useCallback(
    async (slug) => {
      if (busy) return;
      const skill = (profile?.progress_tree || []).find((s) => s.slug === slug);
      if (!skill) return;
      setExerciseSlug(slug);
      addSystemMessage(
        `Retour sur « ${skill.title} » : découverte relancée. ` +
        "Tes autres validations sont conservées — si les tests passent, le statut est confirmé par la pratique."
      );
      await doIntro(language, slug, studentId);
    },
    [busy, profile, language, studentId, doIntro, addSystemMessage]
  );

  // ---------- init ----------
  useEffect(() => {
    (async () => {
      let initialProfile = null;
      try {
        const saved = localStorage.getItem(STUDENT_KEY);
        const data = await api("/api/students");
        setStudents(data.students);
        const target =
          (saved && data.students.find((s) => s.id === Number(saved))) ||
          data.students[0];
        if (!target) return;
        setStudentId(target.id);
        localStorage.setItem(STUDENT_KEY, String(target.id));
        initialProfile = await api(`/api/student?student_id=${target.id}`);
        setProfile(initialProfile);
        setLanguage(initialProfile.language);
        setCode(STARTER_CODE[initialProfile.language] || "");
      } catch (err) {
        addSystemMessage(
          "Base de données indisponible : " + err.message +
          " — lance `docker compose up -d` puis recharge la page."
        );
      }
      try {
        const data = await api("/api/exercises");
        setExercises(data.exercises);
      } catch (err) {
        consoleAppend("Impossible de charger les exercices : " + err.message, "info");
      }
      // Ouverture pédagogique : onboarding si nouveau profil, sinon découverte
      // directe de la première compétence (rien si la DB est indisponible).
      if (initialProfile && !maybeAutoOnboarding(initialProfile)) {
        await doIntro(initialProfile.language, "", initialProfile.id);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------- rendu ----------
  return (
    <>
      <HeaderBar
        students={students}
        studentId={studentId}
        onStudentChange={onStudentChange}
        onNewProfile={() => setShowProfileModal(true)}
        onDeleteProfile={deleteActiveProfile}
        language={language}
        onLanguageChange={onLanguageChange}
        exercises={exercises}
        exerciseSlug={exerciseSlug}
        onExerciseChange={onExerciseChange}
        profile={profile}
        onAbout={onAbout}
      />
      <main>
        <section className="editor-pane">
          <div className="pane-title">
            <span>Éditeur</span>
            <div className="editor-buttons">
              <button id="btn-run" className="btn" disabled={busy} onClick={doRun}
                title="Exécuter le code (avec tests si un exercice est sélectionné)">Exécuter</button>
              <button id="btn-help" className="btn btn-primary" disabled={busy} onClick={() => doHelp("")}
                title="Envoyer le code + un message au Algo mentor">Demander de l'aide</button>
            </div>
          </div>
          <CodeEditor editorRef={editorRef} language={language} />
          <div className="pane-title console-title">
            <span>Console &amp; tests</span>
            <button id="btn-clear-console" className="btn btn-small" onClick={() => setConsoleLines([])}>Effacer</button>
          </div>
          <Console lines={consoleLines} />
        </section>

        <ChatPane messages={messages} thinking={thinking} busy={busy} onSend={doHelp} />
        <ProgressPane profile={profile} onSelectSkill={onSelectSkill} />
      </main>

      <ProfileModal
        open={showProfileModal}
        onCancel={() => setShowProfileModal(false)}
        onCreate={createProfile}
      />
      <OnboardingModal
        open={showOnboarding}
        progressTree={onboardingTreeRef.current}
        onStart={onOnboardingStart}
      />
    </>
  );
}

function Console({ lines }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [lines]);
  return (
    <pre id="console" className="console" ref={ref}>
      {lines.map((l, i) => (
        <React.Fragment key={i}>
          <span className={l.cls}>{l.text}</span>
          {"\n"}
        </React.Fragment>
      ))}
    </pre>
  );
}
