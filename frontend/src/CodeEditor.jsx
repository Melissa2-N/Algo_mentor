import { useEffect, useRef } from "react";
import CodeMirror from "codemirror";
import "codemirror/mode/python/python.js";
import "codemirror/mode/clike/clike.js";
import "codemirror/mode/javascript/javascript.js";
import { CM_MODES, STARTER_CODE } from "./constants.js";

/**
 * Wrapper CodeMirror 5 : l'instance est créée une seule fois et exposée au
 * parent via editorRef (current.getValue / setValue / setMode).
 */
export default function CodeEditor({ editorRef, language }) {
  const hostRef = useRef(null);

  useEffect(() => {
    editorRef.current = CodeMirror(hostRef.current, {
      mode: CM_MODES[language] || "python",
      theme: "material-darker",
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      autoCloseBrackets: false,
      lineWrapping: true,
      value: STARTER_CODE[language] || "",
    });
    return () => {
      editorRef.current = null;
      hostRef.current.innerHTML = "";
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Changement de langage : mise à jour du mode de coloration
  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.setOption("mode", CM_MODES[language] || "python");
    }
  }, [language, editorRef]);

  return <div id="editor" ref={hostRef} />;
}
