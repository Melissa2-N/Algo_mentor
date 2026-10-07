import { useState } from "react";

export default function ProfileModal({ open, onCancel, onCreate }) {
  const [name, setName] = useState("");
  const [language, setLanguage] = useState("python");

  const create = () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    onCreate(trimmed, language);
    setName("");
    setLanguage("python");
  };

  return (
    <div className={`modal-overlay${open ? "" : " hidden"}`}>
      <div className="modal">
        <h2>Nouveau profil apprenant</h2>
        <label htmlFor="profile-name">Nom du profil</label>
        <input
          id="profile-name"
          type="text"
          maxLength="60"
          placeholder="ex : Apprenant 2"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") create(); }}
          autoFocus
        />
        <label htmlFor="profile-language">Langage de départ</label>
        <select id="profile-language" value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="python">Python</option>
          <option value="c">C</option>
          <option value="javascript">JavaScript</option>
          <option value="java">Java</option>
        </select>
        <div className="modal-actions">
          <button className="btn" onClick={onCancel}>Annuler</button>
          <button className="btn btn-primary" onClick={create}>Créer</button>
        </div>
      </div>
    </div>
  );
}
