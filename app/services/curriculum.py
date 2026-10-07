"""Curriculum universel : arbre de compétences indépendant du langage.

La progression pédagogique (le "quoi enseigner") vit ici.
La syntaxe (le "comment l'écrire") vit dans EXAMPLES, paramétrée par langage.
"""
from __future__ import annotations

LANGUAGES = ("python", "c", "javascript", "java")
LANGUAGE_LABELS = {
    "python": "Python",
    "c": "C",
    "javascript": "JavaScript",
    "java": "Java",
}

# ---------------------------------------------------------------------------
# Arbre de compétences (4 niveaux, graphe de prérequis)
# ---------------------------------------------------------------------------
SKILLS: list[dict] = [
    # ----- Niveau 1 : logique pure & bases -----
    {
        "slug": "variables", "title": "Variables & affectation", "level": 1,
        "prerequisites": [],
        "description": "Stocker et nommer une valeur pour la réutiliser.",
        "theory": (
            "Une variable est comme une boîte étiquetée : on colle une étiquette (le nom), "
            "on met quelque chose dedans (la valeur), et on peut regarder dans la boîte ou "
            "remplacer son contenu à tout moment. L'ordinateur garde la valeur en mémoire "
            "tant que le programme tourne."
        ),
    },
    {
        "slug": "types", "title": "Types de base", "level": 1,
        "prerequisites": ["variables"],
        "description": "Entiers, flottants, booléens, chaînes de caractères.",
        "theory": (
            "Le type, c'est la nature de ce qu'il y a dans la boîte : un nombre entier, un "
            "nombre à virgule, un vrai/faux (booléen), ou du texte (chaîne de caractères). "
            "Le type décide ce qu'on peut faire avec : on peut additionner deux nombres, mais "
            "additionner du texte avec un nombre provoque une erreur ou une juxtaposition. "
            "On doit parfois convertir (caster) une valeur d'un type vers un autre."
        ),
    },
    {
        "slug": "conditions", "title": "Conditions (si/sinon)", "level": 1,
        "prerequisites": ["types"],
        "description": "Prendre des décisions selon la valeur d'une expression.",
        "theory": (
            "Une condition est un carrefour : si (if) la condition est vraie, le programme "
            "prend le chemin de droite, sinon (else) il prend celui de gauche. La condition "
            "est une question à laquelle on répond par vrai ou faux, comme « la valeur est-elle "
            "supérieure à 0 ? ». On peut enchaîner plusieurs questions (else if)."
        ),
    },
    {
        "slug": "while_loop", "title": "Boucle tant que", "level": 1,
        "prerequisites": ["conditions"],
        "description": "Répéter des instructions tant qu'une condition reste vraie.",
        "theory": (
            "Une boucle « tant que » (while) est comme marcher jusqu'à l'arrêt de bus : tant "
            "que tu n'es pas arrivé, tu continues de marcher. Trois ingrédients sont "
            "indispensables : une condition d'arrêt, un point de départ, et surtout un pas "
            "qui fait progresser vers l'arrêt — sinon la boucle tourne à l'infini."
        ),
    },
    {
        "slug": "for_loop", "title": "Boucle pour", "level": 1,
        "prerequisites": ["while_loop"],
        "description": "Répéter un nombre connu de fois (parcours de 1 à n).",
        "theory": (
            "La boucle « pour » (for) est une boucle tant que compressée, quand on sait "
            "d'avance combien de tours on veut faire : pour i allant de 1 à n, faire telle "
            "chose. La variable i (le compteur) change automatiquement à chaque tour."
        ),
    },
    {
        "slug": "functions", "title": "Fonctions", "level": 1,
        "prerequisites": ["for_loop"],
        "description": "Factoriser du code réutilisable : entrées -> traitement -> sortie.",
        "theory": (
            "Une fonction est une petite machine : on lui donne des ingrédients (les "
            "paramètres), elle fait un travail, et elle rend un résultat (la valeur de "
            "retour). On écrit la recette une fois, puis on l'utilise autant de fois qu'on "
            "veut, sans recopier le code."
        ),
    },
    {
        "slug": "scope", "title": "Portée des variables", "level": 1,
        "prerequisites": ["functions"],
        "description": "Variables locales vs globales : où une variable est visible.",
        "theory": (
            "La portée (scope) est la pièce où une variable existe. Une variable créée dans "
            "une fonction (locale) vit seulement dans cette pièce : dehors, personne ne la "
            "connaît. Une variable globale est affichée dans le couloir : toutes les fonctions "
            "peuvent la voir — c'est pratique mais risqué, car tout le monde peut la modifier."
        ),
    },
    # ----- Niveau 2 : structures de données linéaires -----
    {
        "slug": "arrays", "title": "Tableaux / listes", "level": 2,
        "prerequisites": ["for_loop"],
        "description": "Collections indexées : stocker plusieurs valeurs sous un nom.",
        "theory": (
            "Un tableau (ou liste) est une étagère numérotée : chaque case a un numéro "
            "(l'indice) et contient une valeur. Attention, piège classique : la numérotation "
            "commence presque toujours à 0, donc un tableau de 3 cases a les indices 0, 1 et 2. "
            "Chercher la case 3 dans un tableau de 3 cases provoque une erreur « hors limites »."
        ),
    },
    {
        "slug": "strings", "title": "Chaînes de caractères", "level": 2,
        "prerequisites": ["arrays"],
        "description": "Parcourir et manipuler du texte caractère par caractère.",
        "theory": (
            "Une chaîne de caractères se comporte comme un tableau de lettres : chaque "
            "caractère a une position (à partir de 0). On peut connaître sa longueur, lire le "
            "caractère à une position, et la parcourir avec une boucle. Reconstruire une chaîne "
            "inversée ou filtrée se fait souvent en construisant une nouvelle chaîne au fur et à mesure."
        ),
    },
    {
        "slug": "dictionaries", "title": "Dictionnaires / tables de hachage", "level": 2,
        "prerequisites": ["arrays"],
        "description": "Associer une clé à une valeur, accès direct par clé.",
        "theory": (
            "Un dictionnaire fonctionne comme un vrai dictionnaire : au lieu de chercher page "
            "par page (comme dans un tableau), tu sautes directement à la définition grâce au "
            "mot (la clé). Clé -> valeur : « pomme » -> 2. L'accès par clé est quasi instantané, "
            "quel que soit le nombre d'entrées."
        ),
    },
    {
        "slug": "stacks_queues", "title": "Piles & files", "level": 2,
        "prerequisites": ["arrays"],
        "description": "Deux façons de retirer ce qu'on a rangé : LIFO et FIFO.",
        "theory": (
            "Une pile (stack) est une pile d'assiettes : on pose sur le dessus et on retire "
            "aussi du dessus — dernier entré, premier sorti (LIFO), avec push et pop. Une file "
            "(queue) est une file d'attente : premier arrivé, premier servi (FIFO), avec enqueue "
            "et dequeue. Le choix pile/file change complètement l'ordre de traitement."
        ),
    },
    # ----- Niveau 3 : algorithmique intermédiaire -----
    {
        "slug": "binary_search", "title": "Recherche dichotomique", "level": 3,
        "prerequisites": ["arrays", "while_loop"],
        "description": "Chercher dans un tableau trié en coupant en deux à chaque étape.",
        "theory": (
            "La recherche dichotomique, c'est le jeu du « plus grand / plus petit » : pour "
            "trouver un nombre entre 1 et 100, tu proposes 50, on te dit si c'est plus ou "
            "moins, et tu élimines la moitié des possibilités à chaque essai. Condition "
            "obligatoire : le tableau doit être TRIÉ. Avec low et high qui se resserrent, "
            "1000 éléments se testent en ~10 étapes seulement."
        ),
    },
    {
        "slug": "sorting", "title": "Tris élémentaires", "level": 3,
        "prerequisites": ["arrays"],
        "description": "Trier un tableau : sélection, insertion, bulles.",
        "theory": (
            "Trier, c'est remettre de l'ordre. Le tri par sélection regarde tout le tableau "
            "pour trouver le plus petit élément et le place au début, puis recommence sur le "
            "reste. Le tri à bulles compare deux voisins et les échange s'ils sont mal ordonnés, "
            "si bien que les grandes valeurs « remontent » comme des bulles. Les deux sont en "
            "O(n²) : simples à comprendre, lents sur de grands tableaux."
        ),
    },
    {
        "slug": "recursion", "title": "Récursivité", "level": 3,
        "prerequisites": ["functions"],
        "description": "Une fonction qui s'appelle elle-même, avec un cas de base.",
        "theory": (
            "La récursivité est comme des poupées russes : pour résoudre un gros problème, la "
            "fonction se rappelle elle-même sur un problème plus petit. Deux ingrédients "
            "obligatoires : un cas de base (la plus petite poupée, où on répond directement "
            "sans se rappeler — sinon la fonction tourne à l'infini) et un pas de progression "
            "qui se rapproche du cas de base."
        ),
    },
    {
        "slug": "complexity", "title": "Notions de complexité", "level": 3,
        "prerequisites": ["binary_search", "sorting", "recursion"],
        "description": "Comparer des algorithmes : O(1), O(n), O(n²), O(log n).",
        "theory": (
            "La complexité mesure combien d'effours coûte un algorithme quand les données "
            "grandissent, indépendamment de la machine. O(1) : trouver un mot dans un "
            "dictionnaire par sa clé. O(n) : vérifier chaque case d'un tableau. O(n²) : "
            "comparer chaque paire (boucles imbriquées). O(log n) : la dichotomie qui divise "
            "par deux. Doubler les données multiplie le travail par 2 en O(n), mais par 4 en O(n²)."
        ),
    },
    # ----- Niveau 4 : conception & autonomie -----
    {
        "slug": "modular_design", "title": "Découpage modulaire", "level": 4,
        "prerequisites": ["functions", "recursion"],
        "description": "Découper un problème en sous-problèmes = en fonctions.",
        "theory": (
            "Découper modulairement, c'est construire en Lego : chaque brique (fonction) fait "
            "UNE chose et la fait bien, avec un nom qui la décrit. Le programme principal "
            "devient alors une suite d'appels lisibles, comme une recette : préparer(), "
            "cuire(), servir(). Quand un bug survient, on sait dans quelle brique chercher."
        ),
    },
    {
        "slug": "error_handling", "title": "Gestion d'erreurs / exceptions", "level": 4,
        "prerequisites": ["modular_design"],
        "description": "Anticiper l'imprévu : entrées invalides, conversions impossibles.",
        "theory": (
            "Un programme robuste ne suppose pas que l'utilisateur se comporte bien : il "
            "prévoit un plan B. Les exceptions sont un filet de sécurité : on tente (try) une "
            "opération risquée, et si elle échoue, on rattrape l'erreur (catch/except) pour "
            "afficher un message clair au lieu de planter. En C, la tradition est de renvoyer "
            "un code d'erreur (-1, NULL) que l'appelant doit vérifier."
        ),
    },
    {
        "slug": "file_io", "title": "Lecture / écriture de fichiers", "level": 4,
        "prerequisites": ["error_handling"],
        "description": "Persister des données au-delà de la vie du programme.",
        "theory": (
            "Les variables meurent avec le programme ; un fichier survit. Écrire dans un "
            "fichier, c'est comme consigner dans un carnet : ouvrir le carnet (open), noter "
            "(write), puis le refermer (close) — sinon les notes peuvent être perdues. Lire, "
            "c'est relire le carnet ligne par ligne. Toujours prévoir le cas où le carnet "
            "n'existe pas encore."
        ),
    },
    {
        "slug": "mini_project", "title": "Mini-projet complet", "level": 4,
        "prerequisites": ["file_io"],
        "description": "Assembler tout : un petit programme complet de bout en bout.",
        "theory": (
            "Un mini-projet assemble tout le cursus : des fonctions bien découpées, des "
            "structures de données adaptées, des conditions et boucles, une gestion d'erreurs, "
            "et éventuellement la persistance dans un fichier. La méthode : décrire le "
            "programme en une phrase, lister les fonctionnalités, les transformer en fonctions, "
            "puis implémenter et tester une fonctionnalité à la fois."
        ),
    },
]

SKILLS_BY_SLUG = {s["slug"]: s for s in SKILLS}


def next_skill(validated: set[str]) -> dict | None:
    """Première compétence non validée dont tous les prérequis sont acquis."""
    for skill in SKILLS:
        if skill["slug"] in validated:
            continue
        if all(p in validated for p in skill["prerequisites"]):
            return skill
    return None


# ---------------------------------------------------------------------------
# Exemples par langage (syntaxe exacte, code exécutable)
# ---------------------------------------------------------------------------
EXAMPLES: dict[str, dict[str, str]] = {
    "variables": {
        "python": 'age = 15\nname = "Alice"\nprint(name, age)',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int age = 15;\n    char name[] = "Alice";\n    printf("%s a %d ans\\n", name, age);\n    return 0;\n}',
        "javascript": 'let age = 15;\nlet name = "Alice";\nconsole.log(name, age);',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int age = 15;\n        String name = "Alice";\n        System.out.println(name + " a " + age + " ans");\n    }\n}',
    },
    "types": {
        "python": 'n = 42        # entier (int)\npi = 3.14      # flottant (float)\nok = True      # booleen (bool)\ns = "42"       # texte (str)\nprint(int(s) * 2)   # conversion str -> int',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int n = 42;\n    double pi = 3.14;\n    int ok = 1;                 /* 0 = faux, non-zero = vrai */\n    char s[] = "42";\n    int v = atoi(s);            /* conversion texte -> entier */\n    printf("%d\\n", v * 2);\n    return 0;\n}',
        "javascript": 'let n = 42;       // number\nlet pi = 3.14;    // number aussi\nlet ok = true;    // boolean\nlet s = "42";     // string\nconsole.log(Number(s) * 2);  // conversion string -> number',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int n = 42;        // entier\n        double pi = 3.14;  // flottant\n        boolean ok = true; // booleen\n        String s = "42";   // texte\n        System.out.println(Integer.parseInt(s) * 2);\n    }\n}',
    },
    "conditions": {
        "python": 'n = int(input())\nif n > 0:\n    print("positif")\nelif n < 0:\n    print("negatif")\nelse:\n    print("nul")',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int n;\n    scanf("%d", &n);\n    if (n > 0) printf("positif\\n");\n    else if (n < 0) printf("negatif\\n");\n    else printf("nul\\n");\n    return 0;\n}',
        "javascript": 'const n = parseInt(require("fs").readFileSync(0, "utf8"));\nif (n > 0) {\n  console.log("positif");\n} else if (n < 0) {\n  console.log("negatif");\n} else {\n  console.log("nul");\n}',
        "java": 'import java.util.Scanner;\n\npublic class Main {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        if (n > 0) System.out.println("positif");\n        else if (n < 0) System.out.println("negatif");\n        else System.out.println("nul");\n    }\n}',
    },
    "while_loop": {
        "python": 'i = 1\nwhile i <= 5:\n    print(i)\n    i = i + 1   # le pas : sans lui, boucle infinie !',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int i = 1;\n    while (i <= 5) {\n        printf("%d\\n", i);\n        i = i + 1;   /* le pas : sans lui, boucle infinie ! */\n    }\n    return 0;\n}',
        "javascript": 'let i = 1;\nwhile (i <= 5) {\n  console.log(i);\n  i = i + 1;   // le pas : sans lui, boucle infinie !\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int i = 1;\n        while (i <= 5) {\n            System.out.println(i);\n            i = i + 1;   // le pas : sans lui, boucle infinie !\n        }\n    }\n}',
    },
    "for_loop": {
        "python": 'for i in range(1, 6):   # i vaut 1,2,3,4,5\n    print(i)',
        "c": '#include <stdio.h>\n\nint main(void) {\n    for (int i = 1; i <= 5; i++) {   /* init ; condition ; pas */\n        printf("%d\\n", i);\n    }\n    return 0;\n}',
        "javascript": 'for (let i = 1; i <= 5; i++) {   // init ; condition ; pas\n  console.log(i);\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        for (int i = 1; i <= 5; i++) {   // init ; condition ; pas\n            System.out.println(i);\n        }\n    }\n}',
    },
    "functions": {
        "python": 'def add(a, b):\n    return a + b\n\nprint(add(2, 3))   # 5',
        "c": '#include <stdio.h>\n\nint add(int a, int b) {\n    return a + b;\n}\n\nint main(void) {\n    printf("%d\\n", add(2, 3));   /* 5 */\n    return 0;\n}',
        "javascript": 'function add(a, b) {\n  return a + b;\n}\n\nconsole.log(add(2, 3));   // 5',
        "java": 'public class Main {\n    static int add(int a, int b) {\n        return a + b;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(add(2, 3));   // 5\n    }\n}',
    },
    "scope": {
        "python": 'count = 0            # variable globale\n\ndef increment():\n    global count     # indispensable pour la modifier\n    count = count + 1\n\nincrement()\nincrement()\nprint(count)        # 2\n\ndef exemple():\n    local = 5        # variable locale : n\'existe que dans la fonction\n    return local',
        "c": '#include <stdio.h>\n\nint count = 0;       /* variable globale */\n\nvoid increment(void) {\n    count = count + 1;\n}\n\nint main(void) {\n    increment();\n    increment();\n    printf("%d\\n", count);   /* 2 */\n    return 0;\n}',
        "javascript": 'let count = 0;   // variable globale\n\nfunction increment() {\n  count = count + 1;\n}\n\nincrement();\nincrement();\nconsole.log(count);   // 2\n\nfunction exemple() {\n  let local = 5;   // variable locale\n  return local;\n}',
        "java": 'public class Main {\n    static int count = 0;   // attribut de classe ("globale")\n\n    static void increment() {\n        count = count + 1;\n    }\n\n    public static void main(String[] args) {\n        increment();\n        increment();\n        System.out.println(count);   // 2\n    }\n}',
    },
    "arrays": {
        "python": 't = [3, 1, 4]\nprint(t[0])        # 3 : le premier element (indice 0 !)\nprint(len(t))      # 3 : le nombre de cases\ntotal = 0\nfor x in t:\n    total = total + x\nprint(total)       # 8',
        "c": '#include <stdio.h>\n\nint main(void) {\n    int t[3] = {3, 1, 4};\n    printf("%d\\n", t[0]);        /* 3 : premier element (indice 0 !) */\n    int n = 3;\n    int total = 0;\n    for (int i = 0; i < n; i++)   /* indices 0,1,2 : jamais n ! */\n        total += t[i];\n    printf("%d\\n", total);       /* 8 */\n    return 0;\n}',
        "javascript": 'const t = [3, 1, 4];\nconsole.log(t[0]);    // 3 : le premier element (indice 0 !)\nconsole.log(t.length); // 3 : le nombre de cases\nlet total = 0;\nfor (const x of t) {\n  total = total + x;\n}\nconsole.log(total);   // 8',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        int[] t = {3, 1, 4};\n        System.out.println(t[0]);    // 3 : premier element (indice 0 !)\n        System.out.println(t.length); // 3 : le nombre de cases\n        int total = 0;\n        for (int x : t) {\n            total = total + x;\n        }\n        System.out.println(total);   // 8\n    }\n}',
    },
    "strings": {
        "python": 's = "algo"\nprint(len(s))      # 4\nprint(s[0])        # "a"\ninverse = ""\nfor c in s:\n    inverse = c + inverse   # on ajoute devant\nprint(inverse)     # "ogla"',
        "c": '#include <stdio.h>\n#include <string.h>\n\nint main(void) {\n    char s[] = "algo";\n    printf("%lu\\n", strlen(s));   /* 4 */\n    for (int i = strlen(s) - 1; i >= 0; i--)\n        printf("%c", s[i]);       /* ogla */\n    printf("\\n");\n    return 0;\n}',
        "javascript": 'const s = "algo";\nconsole.log(s.length);   // 4\nconsole.log(s[0]);       // "a"\nlet inverse = "";\nfor (const c of s) {\n  inverse = c + inverse;\n}\nconsole.log(inverse);    // "ogla"',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        String s = "algo";\n        System.out.println(s.length());   // 4\n        System.out.println(s.charAt(0));  // a\n        String inverse = "";\n        for (int i = 0; i < s.length(); i++) {\n            inverse = s.charAt(i) + inverse;\n        }\n        System.out.println(inverse);      // ogla\n    }\n}',
    },
    "dictionaries": {
        "python": 'prices = {"pomme": 2, "banane": 3}\nprint(prices["pomme"])           # 2\nif "kiwi" in prices:             # verifier avant d\'acceder\n    print(prices["kiwi"])\nelse:\n    print("inconnu")\nprices["poire"] = 4              # ajouter une entree',
        "c": '/* Le C n\'a pas de dictionnaire integre : on imite avec deux tableaux paralleles. */\n#include <stdio.h>\n#include <string.h>\n\nint main(void) {\n    char *keys[] = {"pomme", "banane"};\n    int values[] = {2, 3};\n    char cible[] = "pomme";\n    for (int i = 0; i < 2; i++)\n        if (strcmp(keys[i], cible) == 0)\n            printf("%d\\n", values[i]);   /* 2 */\n    return 0;\n}',
        "javascript": 'const prices = { pomme: 2, banane: 3 };\nconsole.log(prices["pomme"]);      // 2\nif ("kiwi" in prices) {            // verifier avant d\'acceder\n  console.log(prices["kiwi"]);\n} else {\n  console.log("inconnu");\n}\nprices.poire = 4;                  // ajouter une entree',
        "java": 'import java.util.HashMap;\nimport java.util.Map;\n\npublic class Main {\n    public static void main(String[] args) {\n        Map<String, Integer> prices = new HashMap<>();\n        prices.put("pomme", 2);\n        prices.put("banane", 3);\n        System.out.println(prices.get("pomme"));   // 2\n        Integer p = prices.get("kiwi");\n        System.out.println(p != null ? p : "inconnu");\n    }\n}',
    },
    "stacks_queues": {
        "python": 'pile = []                 # une liste fait office de pile\npile.append(1)            # push\npile.append(2)\nprint(pile.pop())         # 2 : dernier entre, premier sorti\n\nfrom collections import deque\nfile = deque()\nfile.append("a")          # enqueue\nfile.append("b")\nprint(file.popleft())     # "a" : premier arrive, premier sorti',
        "c": '/* Pile = tableau + indice du sommet. */\n#include <stdio.h>\n\nint main(void) {\n    int pile[10];\n    int top = -1;              /* pile vide */\n    pile[++top] = 1;           /* push */\n    pile[++top] = 2;\n    printf("%d\\n", pile[top--]);   /* pop : 2 */\n    printf("%d\\n", pile[top--]);   /* pop : 1 */\n    return 0;\n}',
        "javascript": 'const pile = [];\npile.push(1);          // push\npile.push(2);\nconsole.log(pile.pop());   // 2 : dernier entre, premier sorti\n\nconst file = [];\nfile.push("a");        // enqueue\nfile.push("b");\nconsole.log(file.shift()); // "a" : premier arrive, premier sorti',
        "java": 'import java.util.ArrayDeque;\nimport java.util.Deque;\n\npublic class Main {\n    public static void main(String[] args) {\n        Deque<Integer> pile = new ArrayDeque<>();\n        pile.push(1);          // push\n        pile.push(2);\n        System.out.println(pile.pop());   // 2\n\n        Deque<String> file = new ArrayDeque<>();\n        file.addLast("a");     // enqueue\n        file.addLast("b");\n        System.out.println(file.removeFirst());   // a\n    }\n}',
    },
    "binary_search": {
        "python": 'def recherche(t, x):\n    low, high = 0, len(t) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if t[mid] == x:\n            return mid\n        elif t[mid] < x:\n            low = mid + 1     # x est a droite\n        else:\n            high = mid - 1    # x est a gauche\n    return -1\n\nprint(recherche([1, 3, 5, 7, 9], 7))   # 3',
        "c": '#include <stdio.h>\n\nint recherche(int t[], int n, int x) {\n    int low = 0, high = n - 1;\n    while (low <= high) {\n        int mid = (low + high) / 2;\n        if (t[mid] == x) return mid;\n        else if (t[mid] < x) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}\n\nint main(void) {\n    int t[] = {1, 3, 5, 7, 9};\n    printf("%d\\n", recherche(t, 5, 7));   /* 3 */\n    return 0;\n}',
        "javascript": 'function recherche(t, x) {\n  let low = 0, high = t.length - 1;\n  while (low <= high) {\n    const mid = Math.floor((low + high) / 2);\n    if (t[mid] === x) return mid;\n    else if (t[mid] < x) low = mid + 1;\n    else high = mid - 1;\n  }\n  return -1;\n}\n\nconsole.log(recherche([1, 3, 5, 7, 9], 7));   // 3',
        "java": 'public class Main {\n    static int recherche(int[] t, int x) {\n        int low = 0, high = t.length - 1;\n        while (low <= high) {\n            int mid = (low + high) / 2;\n            if (t[mid] == x) return mid;\n            else if (t[mid] < x) low = mid + 1;\n            else high = mid - 1;\n        }\n        return -1;\n    }\n\n    public static void main(String[] args) {\n        int[] t = {1, 3, 5, 7, 9};\n        System.out.println(recherche(t, 7));   // 3\n    }\n}',
    },
    "sorting": {
        "python": '# tri par selection\n# idea : chercher le plus petit, le mettre devant, recommencer\n\ndef tri(t):\n    for i in range(len(t)):\n        min_idx = i\n        for j in range(i + 1, len(t)):\n            if t[j] < t[min_idx]:\n                min_idx = j\n        t[i], t[min_idx] = t[min_idx], t[i]\n    return t\n\nprint(tri([5, 2, 9, 1]))   # [1, 2, 5, 9]',
        "c": '#include <stdio.h>\n\n/* tri par selection : chercher le plus petit, le mettre devant */\nint main(void) {\n    int t[4] = {5, 2, 9, 1}, n = 4;\n    for (int i = 0; i < n - 1; i++) {\n        int min_idx = i;\n        for (int j = i + 1; j < n; j++)\n            if (t[j] < t[min_idx]) min_idx = j;\n        int tmp = t[i]; t[i] = t[min_idx]; t[min_idx] = tmp;\n    }\n    for (int i = 0; i < n; i++) printf("%d ", t[i]);\n    printf("\\n");   /* 1 2 5 9 */\n    return 0;\n}',
        "javascript": '// tri par selection : chercher le plus petit, le mettre devant\nfunction tri(t) {\n  for (let i = 0; i < t.length; i++) {\n    let minIdx = i;\n    for (let j = i + 1; j < t.length; j++) {\n      if (t[j] < t[minIdx]) minIdx = j;\n    }\n    [t[i], t[minIdx]] = [t[minIdx], t[i]];\n  }\n  return t;\n}\n\nconsole.log(tri([5, 2, 9, 1]));   // [1, 2, 5, 9]',
        "java": 'import java.util.Arrays;\n\npublic class Main {\n    // tri par selection : chercher le plus petit, le mettre devant\n    static void tri(int[] t) {\n        for (int i = 0; i < t.length - 1; i++) {\n            int minIdx = i;\n            for (int j = i + 1; j < t.length; j++) {\n                if (t[j] < t[minIdx]) minIdx = j;\n            }\n            int tmp = t[i]; t[i] = t[minIdx]; t[minIdx] = tmp;\n        }\n    }\n\n    public static void main(String[] args) {\n        int[] t = {5, 2, 9, 1};\n        tri(t);\n        System.out.println(Arrays.toString(t));   // [1, 2, 5, 9]\n    }\n}',
    },
    "recursion": {
        "python": 'def factorielle(n):\n    if n <= 1:            # cas de base : la plus petite poupée\n        return 1\n    return n * factorielle(n - 1)   # pas de progression\n\nprint(factorielle(5))   # 120',
        "c": '#include <stdio.h>\n\nint factorielle(int n) {\n    if (n <= 1) return 1;          /* cas de base */\n    return n * factorielle(n - 1); /* pas de progression */\n}\n\nint main(void) {\n    printf("%d\\n", factorielle(5));   /* 120 */\n    return 0;\n}',
        "javascript": 'function factorielle(n) {\n  if (n <= 1) return 1;         // cas de base\n  return n * factorielle(n - 1); // pas de progression\n}\n\nconsole.log(factorielle(5));   // 120',
        "java": 'public class Main {\n    static int factorielle(int n) {\n        if (n <= 1) return 1;            // cas de base\n        return n * factorielle(n - 1);   // pas de progression\n    }\n\n    public static void main(String[] args) {\n        System.out.println(factorielle(5));   // 120\n    }\n}',
    },
    "complexity": {
        "python": '# O(n) : une boucle qui visite chaque element\nfor i in range(n):\n    travail()\n\n# O(n^2) : boucles imbriquees -> n*n operations\nfor i in range(n):\n    for j in range(n):\n        travail()\n\n# O(log n) : on divise le champ de recherche par 2 a chaque etape (dichotomie)',
        "c": '/* O(n) : une boucle qui visite chaque element */\nfor (int i = 0; i < n; i++) travail();\n\n/* O(n^2) : boucles imbriquees -> n*n operations */\nfor (int i = 0; i < n; i++)\n    for (int j = 0; j < n; j++)\n        travail();\n\n/* O(log n) : on divise par 2 a chaque etape (dichotomie) */',
        "javascript": '// O(n) : une boucle qui visite chaque element\nfor (let i = 0; i < n; i++) travail();\n\n// O(n^2) : boucles imbriquees -> n*n operations\nfor (let i = 0; i < n; i++) {\n  for (let j = 0; j < n; j++) travail();\n}\n\n// O(log n) : on divise le champ de recherche par 2 a chaque etape (dichotomie)',
        "java": '// O(n) : une boucle qui visite chaque element\nfor (int i = 0; i < n; i++) travail();\n\n// O(n^2) : boucles imbriquees -> n*n operations\nfor (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j++) travail();\n}\n\n// O(log n) : on divise le champ de recherche par 2 a chaque etape (dichotomie)',
    },
    "modular_design": {
        "python": '# chaque brique fait UNE chose\ndef double(x):\n    return x * 2\n\ndef quadruple(x):\n    return double(double(x))   # composition de briques\n\nprint(quadruple(3))   # 12',
        "c": '#include <stdio.h>\n\n/* chaque brique fait UNE chose */\nint double_v(int x) { return x * 2; }\n\nint quadruple(int x) { return double_v(double_v(x)); }\n\nint main(void) {\n    printf("%d\\n", quadruple(3));   /* 12 */\n    return 0;\n}',
        "javascript": '// chaque brique fait UNE chose\nfunction double(x) {\n  return x * 2;\n}\n\nfunction quadruple(x) {\n  return double(double(x));   // composition de briques\n}\n\nconsole.log(quadruple(3));   // 12',
        "java": 'public class Main {\n    // chaque brique fait UNE chose\n    static int doubleV(int x) { return x * 2; }\n\n    static int quadruple(int x) { return doubleV(doubleV(x)); }\n\n    public static void main(String[] args) {\n        System.out.println(quadruple(3));   // 12\n    }\n}',
    },
    "error_handling": {
        "python": 'try:\n    n = int(input())\n    print(n * 2)\nexcept ValueError:\n    print("erreur")   # l\'entree n\'etait pas un nombre',
        "c": '#include <stdio.h>\n\n/* En C : convention de code de retour. */\nint double_si_valide(const char *texte, int *resultat) {\n    if (sscanf(texte, "%d", resultat) != 1)\n        return -1;            /* code d\'erreur */\n    return 0;                 /* tout va bien */\n}\n\nint main(void) {\n    char texte[] = "abc";\n    int valeur;\n    if (double_si_valide(texte, &valeur) == 0)\n        printf("%d\\n", valeur * 2);\n    else\n        printf("erreur\\n");\n    return 0;\n}',
        "javascript": 'try {\n  const n = parseInt("abc");\n  if (Number.isNaN(n)) throw new Error("pas un nombre");\n  console.log(n * 2);\n} catch (e) {\n  console.log("erreur");   // l\'entree n\'etait pas un nombre\n}',
        "java": 'public class Main {\n    public static void main(String[] args) {\n        try {\n            int n = Integer.parseInt("abc");\n            System.out.println(n * 2);\n        } catch (NumberFormatException e) {\n            System.out.println("erreur");   // l\'entree n\'etait pas un nombre\n        }\n    }\n}',
    },
    "file_io": {
        "python": '# ecrire\nwith open("fichier.txt", "w") as f:\n    f.write("algo")\n\n# lire\nwith open("fichier.txt", "r") as f:\n    contenu = f.read()\nprint(contenu)   # algo',
        "c": '#include <stdio.h>\n\nint main(void) {\n    FILE *f = fopen("fichier.txt", "w");   /* ouvrir en ecriture */\n    if (f == NULL) return 1;               /* toujours verifier ! */\n    fprintf(f, "algo");\n    fclose(f);                             /* refermer */\n\n    f = fopen("fichier.txt", "r");\n    char ligne[100];\n    fgets(ligne, sizeof(ligne), f);\n    printf("%s\\n", ligne);   /* algo */\n    fclose(f);\n    return 0;\n}',
        "javascript": 'const fs = require("fs");\n\n// ecrire\nfs.writeFileSync("fichier.txt", "algo");\n\n// lire\nconst contenu = fs.readFileSync("fichier.txt", "utf8");\nconsole.log(contenu);   // algo',
        "java": 'import java.io.*;\n\npublic class Main {\n    public static void main(String[] args) throws IOException {\n        // ecrire\n        try (FileWriter w = new FileWriter("fichier.txt")) {\n            w.write("algo");\n        }\n        // lire\n        try (BufferedReader r = new BufferedReader(new FileReader("fichier.txt"))) {\n            System.out.println(r.readLine());   // algo\n        }\n    }\n}',
    },
    "mini_project": {
        "python": '# Mini-carnet de contacts : fonctions + dictionnaire + erreurs\ndef ajouter(carnet, nom, tel):\n    carnet[nom] = tel\n\ndef chercher(carnet, nom):\n    return carnet.get(nom, "inconnu")\n\ncarnet = {}\najouter(carnet, "Alice", "0601")\nprint(chercher(carnet, "Alice"))   # 0601\nprint(chercher(carnet, "Bob"))     # inconnu',
        "c": '/* Mini-projet C : annuaire avec tableaux paralleles + fonctions */\n#include <stdio.h>\n#include <string.h>\n\n#define MAX 10\n\nchar noms[MAX][20];\nchar tels[MAX][20];\nint nb = 0;\n\nvoid ajouter(const char *nom, const char *tel) {\n    strcpy(noms[nb], nom);\n    strcpy(tels[nb], tel);\n    nb++;\n}\n\nconst char *chercher(const char *nom) {\n    for (int i = 0; i < nb; i++)\n        if (strcmp(noms[i], nom) == 0) return tels[i];\n    return "inconnu";\n}\n\nint main(void) {\n    ajouter("Alice", "0601");\n    printf("%s\\n", chercher("Alice"));   /* 0601 */\n    printf("%s\\n", chercher("Bob"));     /* inconnu */\n    return 0;\n}',
        "javascript": '// Mini-carnet de contacts : fonctions + objet + erreurs\nfunction ajouter(carnet, nom, tel) {\n  carnet[nom] = tel;\n}\n\nfunction chercher(carnet, nom) {\n  return carnet[nom] ?? "inconnu";\n}\n\nconst carnet = {};\najouter(carnet, "Alice", "0601");\nconsole.log(chercher(carnet, "Alice"));   // 0601\nconsole.log(chercher(carnet, "Bob"));     // inconnu',
        "java": 'import java.util.HashMap;\nimport java.util.Map;\n\npublic class Main {\n    static Map<String, String> carnet = new HashMap<>();\n\n    static void ajouter(String nom, String tel) {\n        carnet.put(nom, tel);\n    }\n\n    static String chercher(String nom) {\n        return carnet.getOrDefault(nom, "inconnu");\n    }\n\n    public static void main(String[] args) {\n        ajouter("Alice", "0601");\n        System.out.println(chercher("Alice"));   // 0601\n        System.out.println(chercher("Bob"));     // inconnu\n    }\n}',
    },
}
