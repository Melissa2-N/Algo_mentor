import React from "react";
import { createRoot } from "react-dom/client";
import "codemirror/lib/codemirror.css";
import "codemirror/theme/material-darker.css";
import "./styles.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(<App />);
