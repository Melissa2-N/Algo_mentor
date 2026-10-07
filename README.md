# Algo mentor d'algorithmique — multi-langage

Tuteur pédagogique IA **local** qui enseigne l'algorithmique à un débutant complet
par la méthode socratique : jamais de code corrigé donné directement, uniquement
des indices qui poussent l'apprenant à comprendre par lui-même.

- **Langages** : Python, C, JavaScript, Java (l'apprenant choisit ; la progression
  pédagogique reste identique, seule la syntaxe change).
- **Orchestration** : FastAPI (local).
- **Suivi d'état** : PostgreSQL (compétences validées, notions fragiles, prochaine étape).
- **RAG** : PostgreSQL + pgvector, embeddings `bge-m3` (1024 dims), recherche hybride
  (distance cosinus `<=>` + filtres de métadonnées par langage).
- **Sandbox** : conteneur Docker éphémère par exécution (`--network none`, 128 Mo,
  1 CPU, timeout 3 s, utilisateur non-root, dossier temp détruit après exécution).
- **LLM** : Qwen via l'API DashScope (endpoint OpenAI-compatible) — seul appel externe.

## Démarrage rapide

### 1. Base de données (PostgreSQL + pgvector)

```bash
docker compose up -d
```

Le schéma (`init_db/01_schema.sql`) est appliqué automatiquement au premier
démarrage : tables `kb_chunks` (index HNSW), `skills` (19 compétences semées),
`students`, `student_skills`, `error_events`, `chat_messages`.

### 2. Configuration

```bash
copy .env.example .env
```

Puis éditez `.env` :

```
QWEN_API_KEY=sk-votre-cle-dashscope     # https://bailian.console.alibabacloud.com/
QWEN_MODEL=qwen-plus                    # ou qwen-max, qwen-turbo…
```

Le client Qwen est entièrement configurable : `QWEN_BASE_URL` (par défaut
`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`), `QWEN_API_KEY`, `QWEN_MODEL`.

### 3. Dépendances Python

```bash
pip install -r requirements.txt
```

### 4. Ingestion du curriculum dans pgvector

```bash
python scripts/ingest_curriculum.py
```

Première exécution : télécharge `bge-m3` (~2 Go) puis insère la théorie + les
exemples de syntaxe (4 langages × 19 compétences) dans `kb_chunks`.

### 4 bis. Ingestion de vos propres documents PDF

```bash
# aperçu sans insertion (sections détectées, concepts/niveaux inférés)
python scripts/ingest_documents.py --dry-run

# ingestion (par défaut : remplace les chunks d'origine document, garde le JSON)
python scripts/ingest_documents.py

# options utiles
python scripts/ingest_documents.py --mode append            # ajoute sans supprimer
python scripts/ingest_documents.py --no-llm-classify        # règles seules
python scripts/ingest_documents.py --overrides overrides.json  # corrections manuelles
```

- Déposez vos PDF dans `curriculum/pdfs/` ; le mapping fichier → langage est dans
  `curriculum/pdf_sources.json` (généré automatiquement au premier lancement :
  `python` → python, `java` → java, `c` → c, sinon `universal`).
- Chunking par section (titres détectés par taille/gras/numérotation, table des
  matières exclue), fusion des sections courtes, découpe des longues avec overlap.
- Concept + niveau déduits par alias FR vers les 19 compétences, avec repli LLM
  (votre endpoint Qwen) et overrides manuels possibles.
- Les chunks document portent `metadata.kind = "document"`, `source`, `page`,
  `detected_by` (rule/llm/override) — cohabitation avec les chunks du JSON.

### 5. Frontend React (build)

L'interface est une application **React (Vite)** compilée dans `frontend/dist`
puis servie par FastAPI. Après modification du code frontend :

```bash
cd frontend
npm install        # une seule fois
npm run build      # regénère dist/ (requis après chaque changement)
```

Pour développer avec rechargement à chaud (optionnel) :

```bash
cd frontend && npm run dev   # http://localhost:5173, proxy /api -> :8000
```

### 6. Lancer le tuteur

```bash
uvicorn app.main:app --reload --port 8000
```

Ouvrez http://localhost:8000 — l'interface comprend :
- un **éditeur de code** (CodeMirror) avec sélection du langage ;
- un **chatbot socratique** (théorie courte → exemple dans le langage choisi →
  pratique → indices en cas de blocage) ;
- le **suivi de progression** (compétences validées, niveau, notions fragiles).

Les images Docker des sandboxes sont tirées automatiquement à la première
exécution de chaque langage (`python:3.12-slim`, `node:20-alpine`, `gcc:14`,
`eclipse-temurin:17-jdk-alpine`).

## API

| Méthode | Route | Rôle |
|---|---|---|
| POST | `/api/chat` | Boucle pédagogique complète : exécution + tests, RAG, Qwen, mise à jour de l'état apprenant |
| POST | `/api/run` | Exécution simple dans la sandbox (avec tests si un exercice est précisé) |
| GET  | `/api/student` | Profil : compétences validées, niveau, notions fragiles, prochaine étape |
| POST | `/api/student/language` | Changer de langage |
| GET  | `/api/exercises` | Liste des exercices avec leurs instructions |

## Cursus (indépendant du langage)

| Niveau | Compétences |
|---|---|
| 1 — Logique pure & bases | variables, types, conditions, boucle tant que, boucle pour, fonctions, portée |
| 2 — Structures linéaires | tableaux/listes, chaînes, dictionnaires, piles & files |
| 3 — Algorithmique | dichotomie, tris élémentaires, récursivité, complexité |
| 4 — Conception & autonomie | découpage modulaire, gestion d'erreurs, fichiers, mini-projet |

## Architecture

```
Interface (React + Vite + CodeMirror, build servie par FastAPI)
        │
        ▼
Orchestrateur FastAPI ── app/services/tutor.py
   ├── Sandbox Docker (app/sandbox/runner.py)   : exécution isolée par langage
   ├── RAG pgvector (app/services/rag.py)       : bge-m3 + filtres langage
   ├── État apprenant (app/services/student_state.py) : PostgreSQL
   └── Qwen via DashScope (app/services/qwen_client.py) : mentor socratique
```
