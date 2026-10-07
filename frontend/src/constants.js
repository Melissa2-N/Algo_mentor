export const STUDENT_KEY = "tutor.studentId";
export const ONBOARDING_KEY = "tutor.onboarding.";

export const STARTER_CODE = {
  python: "# Écris ton code ici…\n",
  c: "#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n",
  javascript: "// Écris ton code ici…\n",
  java: "public class Main {\n    public static void main(String[] args) {\n        \n    }\n}\n",
};

export const CM_MODES = {
  python: "python",
  c: "text/x-csrc",
  javascript: "javascript",
  java: "text/x-java",
};

export const VERDICT_LABELS = {
  discovery: "Nouvelle compétence — découverte",
  qa: "Explication — réponse du tuteur",
  awaiting_confirmation: "Tests réussis — en attente de ta confirmation",
  success: "Compétence validée !",
  partial: "Presque — continue",
  blocked: "Bloqué — indice",
};

export const LEVEL_NAMES = {
  1: "Niveau 1 — Logique pure & bases",
  2: "Niveau 2 — Structures de données",
  3: "Niveau 3 — Algorithmique",
  4: "Niveau 4 — Conception & autonomie",
};

export const ONBOARDING_LEVELS = [
  {
    level: 1,
    title: "Logique pure & bases",
    desc: "Variables, types, conditions, boucles et fonctions : les briques élémentaires de tout programme.",
  },
  {
    level: 2,
    title: "Structures de données",
    desc: "Tableaux, chaînes, dictionnaires, piles et files : organiser les données pour les manipuler efficacement.",
  },
  {
    level: 3,
    title: "Algorithmique intermédiaire",
    desc: "Recherche dichotomique, tris, récursivité et complexité : des algorithmes classiques et leur efficacité.",
  },
  {
    level: 4,
    title: "Conception & autonomie",
    desc: "Découpage modulaire, gestion d'erreurs, fichiers et mini-projets : construire des programmes complets.",
  },
];
