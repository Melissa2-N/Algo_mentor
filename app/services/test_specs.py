"""Exercices par compétence avec tests d'E/S (indépendants du langage).

Chaque exercice est validé en exécutant le code de l'apprenant dans la
sandbox avec chaque cas de test (stdin -> stdout attendu, comparé via strip()).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TestCase:
    stdin: str = ""
    expected: str = ""
    label: str = ""


@dataclass
class Exercise:
    slug: str            # = skill slug
    title: str
    instructions: str
    tests: list[TestCase] = field(default_factory=list)


EXERCISES: dict[str, Exercise] = {
    "variables": Exercise(
        slug="variables",
        title="Ta première boîte étiquetée",
        instructions=(
            "Crée deux variables : `prenom` qui contient \"Alice\" et `age` qui contient 15. "
            "Affiche ensuite EXACTEMENT : Bonjour Alice, tu as 15 ans\n"
            "(une seule ligne, avec les valeurs des variables, pas du texte en dur dans un seul print)."
        ),
        tests=[TestCase(expected="Bonjour Alice, tu as 15 ans", label="salutation exacte")],
    ),
    "types": Exercise(
        slug="types",
        title="Convertir un texte en nombre",
        instructions=(
            "Le programme reçoit un nombre sous forme de TEXTE (lire l'entrée standard). "
            "Convertis-le en vrai nombre, multiplie-le par 2 et affiche le résultat.\n"
            "Exemple : entrée `21` -> sortie `42`."
        ),
        tests=[
            TestCase(stdin="21", expected="42", label="21 * 2 = 42"),
            TestCase(stdin="7", expected="14", label="7 * 2 = 14"),
        ],
    ),
    "conditions": Exercise(
        slug="conditions",
        title="Le carrefour des nombres",
        instructions=(
            "Lis un nombre entier sur l'entrée standard et affiche :\n"
            "- `positif` s'il est strictement plus grand que 0\n"
            "- `negatif` s'il est strictement plus petit que 0\n"
            "- `nul` s'il vaut exactement 0."
        ),
        tests=[
            TestCase(stdin="8", expected="positif", label="8 -> positif"),
            TestCase(stdin="-3", expected="negatif", label="-3 -> negatif"),
            TestCase(stdin="0", expected="nul", label="0 -> nul"),
        ],
    ),
    "while_loop": Exercise(
        slug="while_loop",
        title="Compter avec un pas",
        instructions=(
            "Avec une boucle TANT QUE (while) uniquement, affiche les nombres de 1 à 5, "
            "un par ligne. Attention au pas de progression : sans lui, boucle infinie !"
        ),
        tests=[TestCase(expected="1\n2\n3\n4\n5", label="compte 1 a 5")],
    ),
    "for_loop": Exercise(
        slug="for_loop",
        title="La somme de 1 à n",
        instructions=(
            "Lis un entier n sur l'entrée, puis avec une boucle POUR (for), calcule la somme "
            "des entiers de 1 à n et affiche-la.\nExemple : entrée `10` -> sortie `55`."
        ),
        tests=[
            TestCase(stdin="10", expected="55", label="somme 1..10 = 55"),
            TestCase(stdin="1", expected="1", label="somme 1..1 = 1"),
        ],
    ),
    "functions": Exercise(
        slug="functions",
        title="Ta première machine",
        instructions=(
            "Écris une fonction `add(a, b)` qui RENVOIE (return) la somme de a et b. "
            "Dans le programme principal, lis deux entiers sur l'entrée, appelle la fonction "
            "et affiche son résultat.\nExemple : entrée `2 3` -> sortie `5`."
        ),
        tests=[
            TestCase(stdin="2 3", expected="5", label="add(2,3) = 5"),
            TestCase(stdin="10 -4", expected="6", label="add(10,-4) = 6"),
        ],
    ),
    "scope": Exercise(
        slug="scope",
        title="La variable du couloir",
        instructions=(
            "Crée une variable globale `count` initialisée à 0, et une fonction `increment()` "
            "qui l'augmente de 1. Appelle `increment()` trois fois, puis affiche `count`.\n"
            "Sortie attendue : `3`."
        ),
        tests=[TestCase(expected="3", label="compteur global = 3")],
    ),
    "arrays": Exercise(
        slug="arrays",
        title="Le plus grand de l'étagère",
        instructions=(
            "Le programme reçoit sur l'entrée : d'abord un entier n (le nombre de valeurs), "
            "puis n entiers. Range-les dans un tableau/liste et affiche le PLUS GRAND.\n"
            "Exemple : entrée `4` puis `3 8 2 7` -> sortie `8`."
        ),
        tests=[
            TestCase(stdin="4\n3 8 2 7", expected="8", label="max de 3 8 2 7"),
            TestCase(stdin="3\n-5 -2 -9", expected="-2", label="max de negatifs"),
        ],
    ),
    "strings": Exercise(
        slug="strings",
        title="Miroir de mots",
        instructions=(
            "Lis un mot sur l'entrée et affiche-le inversé, caractère par caractère "
            "(sans utiliser une fonction d'inversion toute faite).\n"
            "Exemple : entrée `algo` -> sortie `ogla`."
        ),
        tests=[
            TestCase(stdin="algo", expected="ogla", label="algo -> ogla"),
            TestCase(stdin="abc", expected="cba", label="abc -> cba"),
        ],
    ),
    "dictionaries": Exercise(
        slug="dictionaries",
        title="Le dictionnaire des prix",
        instructions=(
            "Construis un dictionnaire (clé -> valeur) avec : pomme -> 2, banane -> 3, poire -> 4. "
            "Lis un mot sur l'entrée : s'il est dans le dictionnaire, affiche son prix ; "
            "sinon affiche `inconnu`.\nExemple : entrée `pomme` -> sortie `2`."
        ),
        tests=[
            TestCase(stdin="pomme", expected="2", label="pomme -> 2"),
            TestCase(stdin="poire", expected="4", label="poire -> 4"),
            TestCase(stdin="kiwi", expected="inconnu", label="kiwi -> inconnu"),
        ],
    ),
    "stacks_queues": Exercise(
        slug="stacks_queues",
        title="Pile d'assiettes",
        instructions=(
            "Empile les nombres 1, 2, 3 sur une PILE (push), puis dépile-les tous (pop) en "
            "affichant chaque élément retiré, un par ligne.\n"
            "Sortie attendue (LIFO) : `3` puis `2` puis `1`."
        ),
        tests=[TestCase(expected="3\n2\n1", label="LIFO 3 2 1")],
    ),
    "binary_search": Exercise(
        slug="binary_search",
        title="Le jeu du plus ou moins",
        instructions=(
            "Le tableau trié [1, 3, 5, 7, 9, 11] est déjà défini dans ton programme. "
            "Lis un entier x sur l'entrée et trouve son INDICE par recherche dichotomique "
            "(couper en deux à chaque étape). Affiche l'indice, ou `-1` si absent.\n"
            "Exemple : entrée `7` -> sortie `2`."
        ),
        tests=[
            TestCase(stdin="7", expected="2", label="7 -> indice 2"),
            TestCase(stdin="11", expected="5", label="11 -> indice 5"),
            TestCase(stdin="4", expected="-1", label="4 -> absent"),
        ],
    ),
    "sorting": Exercise(
        slug="sorting",
        title="Range tes cartes",
        instructions=(
            "Lis 3 entiers sur l'entrée et affiche-les triés du plus petit au plus grand, "
            "séparés par des espaces. Implémente le tri toi-même (sélection ou bulles), "
            "sans la fonction de tri du langage.\nExemple : entrée `5 2 9` -> sortie `2 5 9`."
        ),
        tests=[
            TestCase(stdin="5 2 9", expected="2 5 9", label="5 2 9 -> 2 5 9"),
            TestCase(stdin="1 2 3", expected="1 2 3", label="deja trie"),
        ],
    ),
    "recursion": Exercise(
        slug="recursion",
        title="Poupées russes",
        instructions=(
            "Écris une fonction RÉCURSIVE `factorielle(n)` (elle s'appelle elle-même, avec un "
            "cas de base). Lis n sur l'entrée et affiche factorielle(n).\n"
            "Exemple : entrée `5` -> sortie `120`."
        ),
        tests=[
            TestCase(stdin="5", expected="120", label="5! = 120"),
            TestCase(stdin="0", expected="1", label="0! = 1 (cas de base)"),
        ],
    ),
    "complexity": Exercise(
        slug="complexity",
        title="Compter les operations",
        instructions=(
            "Lis un entier n. Un algorithme en O(n²) exécute une boucle imbriquée : "
            "compte le nombre total d'opérations (i de 1 à n, j de 1 à n) et affiche ce compteur.\n"
            "Exemple : entrée `4` -> sortie `16`."
        ),
        tests=[
            TestCase(stdin="4", expected="16", label="n^2 = 16"),
            TestCase(stdin="10", expected="100", label="n^2 = 100"),
        ],
    ),
    "modular_design": Exercise(
        slug="modular_design",
        title="Briques Lego",
        instructions=(
            "Écris DEUX fonctions : `double(x)` qui renvoie x*2, et `quadruple(x)` qui renvoie "
            "x*4 SANS écrire la multiplication — en composant `double` avec `double`. "
            "Lis un entier sur l'entrée et affiche quadruple(n).\nExemple : entrée `3` -> sortie `12`."
        ),
        tests=[
            TestCase(stdin="3", expected="12", label="quadruple(3) = 12"),
            TestCase(stdin="-5", expected="-20", label="quadruple(-5) = -20"),
        ],
    ),
    "error_handling": Exercise(
        slug="error_handling",
        title="Le plan B",
        instructions=(
            "Lis une ligne sur l'entrée. Si c'est un nombre valide, affiche son double ; "
            "sinon (sans faire planter le programme), affiche `erreur`.\n"
            "Exemples : entrée `5` -> `10` ; entrée `abc` -> `erreur`."
        ),
        tests=[
            TestCase(stdin="5", expected="10", label="5 -> 10"),
            TestCase(stdin="abc", expected="erreur", label="abc -> erreur"),
        ],
    ),
    "file_io": Exercise(
        slug="file_io",
        title="Le carnet qui survit",
        instructions=(
            "Écris le texte `algo` dans un fichier `fichier.txt`, referme-le, puis rouvre-le "
            "pour relire son contenu et l'afficher.\nSortie attendue : `algo`."
        ),
        tests=[TestCase(expected="algo", label="ecrit puis relit algo")],
    ),
    "mini_project": Exercise(
        slug="mini_project",
        title="Mini-carnet de contacts",
        instructions=(
            "Mini-projet final : lis deux lignes sur l'entrée (un nom, puis un téléphone), "
            "stocke-les dans une structure clé -> valeur grâce à une fonction `ajouter(...)`, "
            "puis affiche le contact avec une fonction `chercher(nom)` au format exact : "
            "`Contact: <nom> - <telephone>`."
        ),
        tests=[
            TestCase(stdin="Alice\n0601020304", expected="Contact: Alice - 0601020304", label="contact complet"),
        ],
    ),
}


def get_exercise(slug: str) -> Exercise | None:
    return EXERCISES.get(slug)
