"""Exemples de découverte : syntaxe générique montrée au PREMIER contact
avec une compétence, avant toute tentative.

Contrainte pédagogique : chaque exemple illustre la FORME syntaxique du
concept dans le langage choisi, mais reste volontairement DIFFERENT de la
solution de l'exercice de validation (données, sens du problème ou variante),
pour respecter le principe « jamais la solution complète ».
"""
from __future__ import annotations

DISCOVERY_EXAMPLES: dict[str, dict[str, str]] = {
    "variables": {
        "python": 'ville = "Lyon"\npopulation = 520000\nprint(ville, population)',
        "c": '#include <stdio.h>\n\nint main(void) {\n    char ville[] = "Lyon";\n    int population = 520000;\n    printf("%s : %d habitants\\n", ville, population);\n    return 0;\n}',
        "javascript": 'let ville = "Lyon";\nlet population = 520000;\nconsole.log(ville, population);',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        String ville = "Lyon";\n        int population = 520000;\n        System.out.println(ville + " : " + population + " habitants");\n    }\n}',
    },
    "types": {
        "python": 'texte = "12"\nnombre = int(texte)   # conversion texte -> entier\nprint(nombre + 8)     # 20',
        "c": '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void) {\n    char texte[] = "12";\n    int nombre = atoi(texte);   /* conversion texte -> entier */\n    printf("%d\\n", nombre + 8);   /* 20 */\n    return 0;\n}',
        "javascript": 'const texte = "12";\nconst nombre = Number(texte);   // conversion texte -> number\nconsole.log(nombre + 8);        // 20',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        String texte = "12";\n        int nombre = Integer.parseInt(texte);   // conversion\n        System.out.println(nombre + 8);   // 20\n    }\n}',
    },
    "conditions": {
        "python": 'age = 20\nif age >= 18:\n    print("majeur")\nelse:\n    print("mineur")',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int age = 20;\n    if (age >= 18) printf("majeur\\n");\n    else printf("mineur\\n");\n    return 0;\n}',
        "javascript": 'const age = 20;\nif (age >= 18) {\n  console.log("majeur");\n} else {\n  console.log("mineur");\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int age = 20;\n        if (age >= 18) System.out.println("majeur");\n        else System.out.println("mineur");\n    }\n}',
    },
    "while_loop": {
        "python": 'i = 3\nwhile i > 0:      # on decroit : le pas rapproche de la fin\n    print(i)\n    i = i - 1',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int i = 3;\n    while (i > 0) {\n        printf("%d\\n", i);\n        i = i - 1;   /* le pas rapproche de la fin */\n    }\n    return 0;\n}',
        "javascript": 'let i = 3;\nwhile (i > 0) {\n  console.log(i);\n  i = i - 1;   // le pas rapproche de la fin\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int i = 3;\n        while (i > 0) {\n            System.out.println(i);\n            i = i - 1;   // le pas rapproche de la fin\n        }\n    }\n}',
    },
    "for_loop": {
        "python": 'for i in range(1, 4):   # i vaut 1, 2, 3\n    print(i, "au carre vaut", i * i)',
        "c": '#include <stdio.h>\n\nint main(void) {\n    for (int i = 1; i < 4; i++)   /* i vaut 1, 2, 3 */\n        printf("%d au carre vaut %d\\n", i, i * i);\n    return 0;\n}',
        "javascript": 'for (let i = 1; i < 4; i++) {   // i vaut 1, 2, 3\n  console.log(i, "au carre vaut", i * i);\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        for (int i = 1; i < 4; i++) {   // i vaut 1, 2, 3\n            System.out.println(i + " au carre vaut " + (i * i));\n        }\n    }\n}',
    },
    "functions": {
        "python": 'def triple(x):\n    return x * 3\n\nprint(triple(4))   # 12',
        "c": '#include <stdio.h>\n\nint triple(int x) {\n    return x * 3;\n}\n\nint main(void) {\n    printf("%d\\n", triple(4));   /* 12 */\n    return 0;\n}',
        "javascript": 'function triple(x) {\n  return x * 3;\n}\n\nconsole.log(triple(4));   // 12',
        "java": 'public class Main {\n    static int triple(int x) {\n        return x * 3;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(triple(4));   // 12\n    }\n}',
    },
    "scope": {
        "python": 'compteur = 10          # variable globale\n\ndef decrementer():\n    global compteur    # autorise la modification\n    compteur = compteur - 1\n\ndecrementer()\ndecrementer()\nprint(compteur)        # 8',
        "c": '#include <stdio.h>\n\nint compteur = 10;   /* variable globale */\n\nvoid decrementer(void) {\n    compteur = compteur - 1;\n}\n\nint main(void) {\n    decrementer();\n    decrementer();\n    printf("%d\\n", compteur);   /* 8 */\n    return 0;\n}',
        "javascript": 'let compteur = 10;   // variable globale\n\nfunction decrementer() {\n  compteur = compteur - 1;\n}\n\ndecrementer();\ndecrementer();\nconsole.log(compteur);   // 8',
        "java": 'public class Main {\n    static int compteur = 10;   // attribut de classe\n\n    static void decrementer() {\n        compteur = compteur - 1;\n    }\n\n    public static void main(String[] args) {\n        decrementer();\n        decrementer();\n        System.out.println(compteur);   // 8\n    }\n}',
    },
    "arrays": {
        "python": 'notes = [12, 8, 15]\nplus_petite = notes[0]      # point de depart\nfor n in notes:\n    if n < plus_petite:\n        plus_petite = n     # nouveau minimum\nprint(plus_petite)          # 8',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int notes[3] = {12, 8, 15};\n    int plus_petite = notes[0];   /* point de depart */\n    for (int i = 1; i < 3; i++)\n        if (notes[i] < plus_petite)\n            plus_petite = notes[i];\n    printf("%d\\n", plus_petite);   /* 8 */\n    return 0;\n}',
        "javascript": 'const notes = [12, 8, 15];\nlet plusPetite = notes[0];   // point de depart\nfor (const n of notes) {\n  if (n < plusPetite) plusPetite = n;\n}\nconsole.log(plusPetite);   // 8',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int[] notes = {12, 8, 15};\n        int plusPetite = notes[0];   // point de depart\n        for (int n : notes) {\n            if (n < plusPetite) plusPetite = n;\n        }\n        System.out.println(plusPetite);   // 8\n    }\n}',
    },
    "strings": {
        "python": 'mot = "code"\nfor i in range(len(mot)):\n    print(i, "->", mot[i])   # chaque caractere avec sa position',
        "c": '#include <stdio.h>\n#include <string.h>\n\nint main(void) {\n    char mot[] = "code";\n    for (int i = 0; i < (int)strlen(mot); i++)\n        printf("%d -> %c\\n", i, mot[i]);\n    return 0;\n}',
        "javascript": 'const mot = "code";\nfor (let i = 0; i < mot.length; i++) {\n  console.log(i, "->", mot[i]);   // chaque caractere avec sa position\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        String mot = "code";\n        for (int i = 0; i < mot.length(); i++) {\n            System.out.println(i + " -> " + mot.charAt(i));\n        }\n    }\n}',
    },
    "dictionaries": {
        "python": 'ages = {"ana": 30, "tom": 25}\nnom = "tom"\nif nom in ages:              # verifier la cle avant d y acceder\n    print(nom, "a", ages[nom], "ans")',
        "c": '#include <stdio.h>\n#include <string.h>\n\nint main(void) {\n    char *noms[] = {"ana", "tom"};\n    int ages[] = {30, 25};\n    char cible[] = "tom";\n    for (int i = 0; i < 2; i++)\n        if (strcmp(noms[i], cible) == 0)\n            printf("%s a %d ans\\n", noms[i], ages[i]);\n    return 0;\n}',
        "javascript": 'const ages = { ana: 30, tom: 25 };\nconst nom = "tom";\nif (nom in ages) {   // verifier la cle avant d y acceder\n  console.log(nom, "a", ages[nom], "ans");\n}',
        "java": 'import java.util.HashMap;\nimport java.util.Map;\n\npublic class Main {\n    public static void main(String[] args) {\n        Map<String, Integer> ages = new HashMap<>();\n        ages.put("ana", 30);\n        ages.put("tom", 25);\n        String nom = "tom";\n        Integer age = ages.get(nom);\n        if (age != null) System.out.println(nom + " a " + age + " ans");\n    }\n}',
    },
    "stacks_queues": {
        "python": 'pile = []\npile.append("a")   # empiler\npile.append("b")\npile.append("c")\nprint(pile.pop())  # c : le dernier empile ressort en premier',
        "c": '#include <stdio.h>\n\nint main(void) {\n    char pile[10];\n    int top = -1;              /* pile vide */\n    pile[++top] = \'a\';         /* empiler */\n    pile[++top] = \'b\';\n    pile[++top] = \'c\';\n    printf("%c\\n", pile[top--]);   /* c : dernier entre, premier sorti */\n    return 0;\n}',
        "javascript": 'const pile = [];\npile.push("a");   // empiler\npile.push("b");\npile.push("c");\nconsole.log(pile.pop());   // c : le dernier empile ressort en premier',
        "java": 'import java.util.ArrayDeque;\nimport java.util.Deque;\n\npublic class Main {\n    public static void main(String[] args) {\n        Deque<String> pile = new ArrayDeque<>();\n        pile.push("a");   // empiler\n        pile.push("b");\n        pile.push("c");\n        System.out.println(pile.pop());   // c : dernier entre, premier sorti\n    }\n}',
    },
    "binary_search": {
        "python": '# le principe : proposer le milieu, eliminer la moitie\nbas, haut = 1, 100\nmilieu = (bas + haut) // 2\nprint("je propose", milieu)   # 50 : d un coup, la moitie des nombres est eliminee',
        "c": '#include <stdio.h>\n\nint main(void) {\n    /* le principe : proposer le milieu, eliminer la moitie */\n    int bas = 1, haut = 100;\n    int milieu = (bas + haut) / 2;\n    printf("je propose %d\\n", milieu);   /* 50 */\n    return 0;\n}',
        "javascript": '// le principe : proposer le milieu, eliminer la moitie\nlet bas = 1, haut = 100;\nlet milieu = Math.floor((bas + haut) / 2);\nconsole.log("je propose", milieu);   // 50',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        // le principe : proposer le milieu, eliminer la moitie\n        int bas = 1, haut = 100;\n        int milieu = (bas + haut) / 2;\n        System.out.println("je propose " + milieu);   // 50\n    }\n}',
    },
    "sorting": {
        "python": 'a, b = 5, 2\nif a > b:\n    a, b = b, a   # l echange : la brique de base de tous les tris\nprint(a, b)      # 2 5',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int a = 5, b = 2, tmp;\n    if (a > b) {          /* l echange : brique de base des tris */\n        tmp = a; a = b; b = tmp;\n    }\n    printf("%d %d\\n", a, b);   /* 2 5 */\n    return 0;\n}',
        "javascript": 'let a = 5, b = 2;\nif (a > b) {\n  [a, b] = [b, a];   // l echange : la brique de base de tous les tris\n}\nconsole.log(a, b);   // 2 5',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int a = 5, b = 2, tmp;\n        if (a > b) {   // l echange : brique de base des tris\n            tmp = a; a = b; b = tmp;\n        }\n        System.out.println(a + " " + b);   // 2 5\n    }\n}',
    },
    "recursion": {
        "python": 'def decompte(n):\n    if n == 0:        # cas de base : la plus petite poupée\n        print("partez !")\n        return\n    print(n)\n    decompte(n - 1)   # se rappelle sur un probleme plus petit\n\ndecompte(3)',
        "c": '#include <stdio.h>\n\nvoid decompte(int n) {\n    if (n == 0) {          /* cas de base */\n        printf("partez !\\n");\n        return;\n    }\n    printf("%d\\n", n);\n    decompte(n - 1);       /* appel recursif */\n}\n\nint main(void) {\n    decompte(3);\n    return 0;\n}',
        "javascript": 'function decompte(n) {\n  if (n === 0) {       // cas de base\n    console.log("partez !");\n    return;\n  }\n  console.log(n);\n  decompte(n - 1);     // appel recursif\n}\n\ndecompte(3);',
        "java": 'public class Main {\n    static void decompte(int n) {\n        if (n == 0) {        // cas de base\n            System.out.println("partez !");\n            return;\n        }\n        System.out.println(n);\n        decompte(n - 1);     // appel recursif\n    }\n\n    public static void main(String[] args) {\n        decompte(3);\n    }\n}',
    },
    "complexity": {
        "python": 'n = 3\ncompteur = 0\nfor i in range(n):            # une seule boucle : O(n)\n    compteur = compteur + 1\nprint("une boucle :", compteur)\n\ncompteur = 0\nfor i in range(n):            # deux boucles imbriquees : O(n^2)\n    for j in range(n):\n        compteur = compteur + 1\nprint("boucles imbriquees :", compteur)',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int n = 3, compteur = 0;\n    for (int i = 0; i < n; i++) compteur++;          /* O(n) */\n    printf("une boucle : %d\\n", compteur);\n    compteur = 0;\n    for (int i = 0; i < n; i++)                      /* O(n^2) */\n        for (int j = 0; j < n; j++) compteur++;\n    printf("boucles imbriquees : %d\\n", compteur);\n    return 0;\n}',
        "javascript": 'const n = 3;\nlet compteur = 0;\nfor (let i = 0; i < n; i++) compteur++;   // O(n)\nconsole.log("une boucle :", compteur);\n\ncompteur = 0;\nfor (let i = 0; i < n; i++) {             // O(n^2)\n  for (let j = 0; j < n; j++) compteur++;\n}\nconsole.log("boucles imbriquees :", compteur);',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int n = 3, compteur = 0;\n        for (int i = 0; i < n; i++) compteur++;   // O(n)\n        System.out.println("une boucle : " + compteur);\n        compteur = 0;\n        for (int i = 0; i < n; i++)               // O(n^2)\n            for (int j = 0; j < n; j++) compteur++;\n        System.out.println("boucles imbriquees : " + compteur);\n    }\n}',
    },
    "modular_design": {
        "python": 'def aire_carre(cote):\n    return cote * cote      # une brique = une responsabilite\n\ndef volume_cube(cote):\n    return aire_carre(cote) * cote   # composition de briques\n\nprint(volume_cube(3))       # 27',
        "c": '#include <stdio.h>\n\nint aire_carre(int cote) {\n    return cote * cote;    /* une brique = une responsabilite */\n}\n\nint volume_cube(int cote) {\n    return aire_carre(cote) * cote;   /* composition */\n}\n\nint main(void) {\n    printf("%d\\n", volume_cube(3));   /* 27 */\n    return 0;\n}',
        "javascript": 'function aireCarre(cote) {\n  return cote * cote;    // une brique = une responsabilite\n}\n\nfunction volumeCube(cote) {\n  return aireCarre(cote) * cote;   // composition de briques\n}\n\nconsole.log(volumeCube(3));   // 27',
        "java": 'public class Main {\n    static int aireCarre(int cote) {\n        return cote * cote;   // une brique = une responsabilite\n    }\n\n    static int volumeCube(int cote) {\n        return aireCarre(cote) * cote;   // composition\n    }\n\n    public static void main(String[] args) {\n        System.out.println(volumeCube(3));   // 27\n    }\n}',
    },
    "error_handling": {
        "python": 'try:\n    resultat = 10 / 0            # operation risquee\nexcept ZeroDivisionError:\n    print("division par zero !") # plan B au lieu de planter',
        "c": '#include <stdio.h>\n\nint diviser(int a, int b, int *resultat) {\n    if (b == 0) return -1;       /* plan B : code d erreur */\n    *resultat = a / b;\n    return 0;\n}\n\nint main(void) {\n    int r;\n    if (diviser(10, 0, &r) != 0)\n        printf("division par zero !\\n");\n    return 0;\n}',
        "javascript": 'try {\n  const resultat = 10 / 0;   // en JS : Infinity, pas d exception ici\n  if (!isFinite(resultat)) throw new Error("division par zero");\n  console.log(resultat);\n} catch (e) {\n  console.log("plan B :", e.message);\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        try {\n            int resultat = 10 / 0;   // operation risquee\n            System.out.println(resultat);\n        } catch (ArithmeticException e) {\n            System.out.println("division par zero !");   // plan B\n        }\n    }\n}',
    },
    "file_io": {
        "python": 'with open("journal.txt", "w") as f:   # ouvrir le carnet\n    f.write("ligne 1\\n")\n    f.write("ligne 2\\n")              # le with referme tout seul\n\nwith open("journal.txt", "r") as f:\n    for ligne in f:\n        print(ligne.strip())',
        "c": '#include <stdio.h>\n\nint main(void) {\n    FILE *f = fopen("journal.txt", "w");\n    if (f == NULL) return 1;      /* toujours verifier */\n    fprintf(f, "ligne 1\\n");\n    fprintf(f, "ligne 2\\n");\n    fclose(f);\n\n    f = fopen("journal.txt", "r");\n    char ligne[50];\n    while (fgets(ligne, sizeof(ligne), f) != NULL)\n        printf("%s", ligne);\n    fclose(f);\n    return 0;\n}',
        "javascript": 'const fs = require("fs");\n\nfs.writeFileSync("journal.txt", "ligne 1\\nligne 2\\n");\n\nconst contenu = fs.readFileSync("journal.txt", "utf8");\nfor (const ligne of contenu.split("\\n")) {\n  if (ligne) console.log(ligne);\n}',
        "java": 'import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        try (FileWriter w = new FileWriter("journal.txt")) {\n            w.write("ligne 1\\n");\n            w.write("ligne 2\\n");\n        }\n        try (BufferedReader r = new BufferedReader(new FileReader("journal.txt"))) {\n            String ligne;\n            while ((ligne = r.readLine()) != null)\n                System.out.println(ligne);\n        }\n    }\n}',
    },
    "mini_project": {
        "python": '# mini-liste de taches : fonctions + liste\ndef ajouter(taches, texte):\n    taches.append(texte)\n\ndef afficher(taches):\n    for i, t in enumerate(taches, 1):\n        print(i, "-", t)\n\ntaches = []\najouter(taches, "reviser les boucles")\najouter(taches, "terminer l exercice")\nafficher(taches)',
        "c": '#include <stdio.h>\n#include <string.h>\n\n#define MAX 10\n\nchar taches[MAX][50];\nint nb = 0;\n\nvoid ajouter(const char *texte) {\n    if (nb < MAX) strcpy(taches[nb++], texte);\n}\n\nvoid afficher(void) {\n    for (int i = 0; i < nb; i++)\n        printf("%d - %s\\n", i + 1, taches[i]);\n}\n\nint main(void) {\n    ajouter("reviser les boucles");\n    ajouter("terminer l exercice");\n    afficher();\n    return 0;\n}',
        "javascript": '// mini-liste de taches : fonctions + tableau\nfunction ajouter(taches, texte) {\n  taches.push(texte);\n}\n\nfunction afficher(taches) {\n  taches.forEach((t, i) => console.log(i + 1, "-", t));\n}\n\nconst taches = [];\najouter(taches, "reviser les boucles");\najouter(taches, "terminer l exercice");\nafficher(taches);',
        "java": 'import java.util.ArrayList;\nimport java.util.List;\n\npublic class Main {\n    static void ajouter(List<String> taches, String texte) {\n        taches.add(texte);\n    }\n\n    static void afficher(List<String> taches) {\n        for (int i = 0; i < taches.size(); i++)\n            System.out.println((i + 1) + " - " + taches.get(i));\n    }\n\n    public static void main(String[] args) {\n        List<String> taches = new ArrayList<>();\n        ajouter(taches, "reviser les boucles");\n        ajouter(taches, "terminer l exercice");\n        afficher(taches);\n    }\n}',
    },
}
