import { useEffect, useRef } from "react";
import { VERDICT_LABELS } from "./constants.js";

function TutorMessage({ reply }) {
  const verdict = reply.verdict || "partial";
  return (
    <div className="msg tutor">
      <span className={`verdict ${verdict}`}>{VERDICT_LABELS[verdict] || verdict}</span>
      {reply.observation && <Section label="Observation" text={reply.observation} />}
      {reply.answer && <Section label="Réponse" text={reply.answer} />}
      {reply.theory && <Section label="Théorie" text={reply.theory} />}
      {reply.example && (
        <div className="section">
          <div className="label">Exemple de syntaxe (générique, à adapter)</div>
          <pre className="code-block">{reply.example}</pre>
        </div>
      )}
      {reply.problem && <Section label="Le problème à résoudre" text={reply.problem} />}
      {reply.hint && <Section label="Indice" text={reply.hint} />}
      {reply.next_step && <Section label="À toi de jouer" text={reply.next_step} />}
    </div>
  );
}

function Section({ label, text }) {
  return (
    <div className="section">
      <div className="label">{label}</div>
      {text}
    </div>
  );
}

export default function ChatPane({ messages, thinking, busy, onSend }) {
  const boxRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (boxRef.current) {
      boxRef.current.scrollTop = boxRef.current.scrollHeight;
    }
  }, [messages, thinking]);

  const send = () => {
    const text = inputRef.current.value.trim();
    onSend(text);
    inputRef.current.value = "";
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <section className="chat-pane">
      <div className="pane-title"><span>Algo mentor</span></div>
      <div id="chat-messages" className="chat-messages" ref={boxRef}>
        {messages.map((m, i) => {
          if (m.kind === "user") {
            return <div key={i} className="msg user">{m.text}</div>;
          }
          if (m.kind === "system") {
            return (
              <div key={i} className="msg tutor">
                <span className="verdict partial">Info</span>
                <div className="section">{m.text}</div>
              </div>
            );
          }
          return <TutorMessage key={i} reply={m.reply} />;
        })}
        {thinking && (
          <div className="msg tutor">
            <span className="verdict partial">Info</span>
            <div className="section">Le tuteur réfléchit (exécution sandbox + analyse)…</div>
          </div>
        )}
      </div>
      <div className="chat-input-row">
        <textarea
          ref={inputRef}
          rows="2"
          disabled={busy}
          placeholder="Pose une question au tuteur… (ex : je ne comprends pas pourquoi ma boucle est infinie)"
          onKeyDown={onKeyDown}
        />
        <button id="btn-send" className="btn btn-primary" disabled={busy} onClick={send}>Envoyer</button>
      </div>
    </section>
  );
}
