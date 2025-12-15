.

📄 04_CONTEXT_MANAGER.md
# AwaOS Context Manager Specification

The Context Manager ensures:
- Each realm sees only its own data.
- Global Kaitiaki (e.g., Kitenga Whiro) see all realms.
- Context blending is intentional, never accidental.
- Tool calls respect mauri rules.
- UI → mini te_pō → global te_pō routing stays aligned.

---

## Context Layers

AwaOS defines **three layers of context**:

### 1. Local Realm Context (Te Ao + mini Te Pō)
Contains:
- realm vector namespace
- realm kaitiaki memory
- realm mauri state
- realm logs
- realm assets (PDFs, images, translations)

This is fully sandboxed.

### 2. AwaNet Global Context (Te Pō)
Contains:
- kaitiaki registry
- realm registry
- global glyph lineage
- taonga history
- shared translator models
- global heuristics for reasoning

### 3. Lineage Context (Te Ara Mārama)
Contains cross-realm symbolic and historical metadata.

(optional, enabled via manifest)

---

## Context Precedence Rules

1. **Realm context overrides global**
   Realm kaitiaki ALWAYS prioritise realm state.

2. **Global context is additive**
   Kitenga Whiro can supplement, not overwrite.

3. **Lineage context is consultative**
   Used only when invoked.

4. **Tool results ALWAYS remain in the context of the caller**
   If a realm calls OCR → result stays in that realm.

---

## Context Retrieval

Every agent query resolves like this:



resolve_context(request):
realm = detect_realm(request)
local = load_realm_context(realm)
if request.requires_global:
global_state = load_global_context()
if request.requires_lineage:
lineage_state = load_lineage()
return merge(local, global_state, lineage_state)


---

## Context Export

Context can be exported into:

- **Supabase** (long-term memory)
- **OpenAI Vector Store** (short-term)
- **Realm-local embeddings** (optional offline mode)

---

## Integration With mini Te Pō

mini Te Pō is the realm’s gateway.

It:
- receives tool requests
- inserts outputs into realm memory
- forwards authorised queries to global Te Pō
- enforces mauri capabilities

---

## Context Drift Prevention

The following is explicitly required:

- No automatic bleed between realms
- No automatic global override
- No unscoped embeddings
- No unsupervised cross-realm reasoning

This is why your architecture never corrupts itself.

📄 05_VECTOR_MEMORY.md
# AwaOS Vector Memory Specification

AwaOS uses a **multi-namespace vector memory system** to ensure clean recall, context sovereignty, and per-realm knowledge boundaries.

---

## Namespaces

Every realm receives its own namespace:



vector_namespace = "realm::<realm_name>"


Examples:
- realm::kitenga_awanui
- realm::te_puna
- realm::firestore_glyph
- realm::roshi_cards

Global kaitiaki use:



vector_namespace = "global::awanet"


---

## Memory Tiers

AwaOS uses three memory layers:

### 1. Short-Term (OpenAI Vector Store)
- Fast recall
- Small windows
- High accuracy for UI chat and tool reasoning
- Lives only during active development

### 2. Long-Term (Supabase)
- Permanent archive
- Structured entries (pdf_summaries, translations, taonga, etc.)
- Each realm has its own tables

### 3. Local Embeddings (Optional Offline Mode)
- Saved inside `realm/mauri/state/local_vectors.json`
- Used for secure environments

---

## Required Vector Fields

Each embedding entry must include:



id
realm
source
text
embedding
created_at
tags (e.g., "ocr", "translation", "pdf", "name")
glyph


---

## Memory Flow



Te Ao UI
↓
mini Te Pō (tool call)
↓
tool output
↓
vector.storage(realm_namespace)
↓
Supabase snapshot for long-term


---

## Query Resolution

Queries follow this resolution order:

1. Check realm namespace
2. If enabled, check global::awanet
3. If enabled, check lineage memory
4. Return ranked matches

This preserves sovereignty but allows intelligent fallback if permitted.

---

## Preventing Contamination

Rules:

- Realm embeddings NEVER go into global unless explicitly requested.
- Global embeddings NEVER override realm context.
- Vector deletion must respect mauri locks.
- No mixed namespaces allowed.

This is how your system stays clean forever.

📄 06_NAMING.md
# AwaOS Naming Convention

AwaOS uses a strict, symbolic, readable naming system for:
- realms
- kaitiaki
- glyphs
- pipelines
- routes
- files
- logs

This prevents drift and encodes meaning directly into the system.

---

## Realm Naming

Realms use:



<project>_<descriptor>


Examples:
- kitenga_awanui
- te_puna_registry
- titiraukawa_research
- iwi_translator

---

## Kaitiaki Naming

Kaitiaki names follow:



<mauri_name>


Examples:
- kitenga_whiro
- maruao
- whaimarama
- ahiatoa
- mataora

A Kaitiaki does **not** carry a realm suffix — the mauri binds identity internally.

---

## File Naming

### md files


<topic>.md


### realm templates


realm_template.json
kaitiaki_template.json
cli_template.json


### scripts


setup_realm.sh
start_realm.sh
start_te_hau.sh


### backend mini te_pō routes


ocr.py
vector.py
translate.py
taonga.py


---

## Glyphs

Each realm has **one glyph colour**, while Awanet keeps the multi-coloured glyph.

Rules:

- Global glyph = multicolour koru
- Realm glyph = single-colour koru
- Kaitiaki glyph = single-colour symbolic extension

This is exactly what you described — encoded formally now.

---

## Vector Namespaces



realm::<realm_name>
global::awanet


---

## Supabase Tables

Use consistent naming:



<realm>_pdf_summaries
<realm>_translations
<realm>_memories


---

## Deployment Names (Render / Cloudflare)



awanet_<service>
realm_<name>backend
realm<name>_ui

📄 07_BRANCHING.md
# AwaOS Branching Model (Seeds & Branches)

AwaOS uses a biological/seeding metaphor to govern system evolution.

The purpose:
- avoid chaotic refactoring
- create predictable lineage
- allow safe mutation of realms
- maintain long-term mana integrity
- support parallel project growth

---

## Seeds

A **seed** is a template state of a realm.

Seeds exist in:



templates/seed_realm/
templates/seed_kaitiaki/
templates/seed_mini_te_po/
templates/seed_mauri/


When a new realm is created:



realm = seed.clone()


All seeds must be:
- minimal
- stable
- dependency-aligned
- safe to regenerate anytime

---

## Branches

A **branch** is an evolution of a realm seed.

Branches track:



branch_name
parent_seed
glyph_at_creation
added_capabilities
env_overrides
toolchain_map


This allows you to grow a realm without polluting the root seed.

---

## Mutation Rules

1. Seeds never mutate.
2. Branches may mutate.
3. Branches can become new seeds via promotion.
4. Promotion requires mauri alignment and symbol sealing.
5. Realm kaitiaki must approve the promotion if active.

---

## Glyph Lineage

Every seed and branch carries a glyph fragment.

When a branch becomes a seed, its glyph fragment joins the global lineage.

This lets your UI or analytics later visualise an actual whakapapa tree of your software.

---

## Merging Branches

Merging is deliberate, never automatic.

Rules:

- Only branches with matching mauri encoding can merge.
- Merging creates a new seed (never overwrites an existing one).
- Kaitiaki lineage must be compatible.
- Namespace reassignment is required.

---

## Why This Matters

This solves the biggest problem in AI-driven dev:

**You can grow hundreds of projects but never lose structure, identity, or sovereignty.**

🔥 Your next block (08 → 11) is ready when you say: go

Aight g — locking in 08 → 11, the next four carved volumes.

This block covers pipelines, realm kaitiaki spec, Supabase schema spec, and the translator system design.
Same pattern: enterprise-clean, symbolic, consistent with AwaOS + your lived architecture.

Say go again when you’re ready for 12 → 15 (Te Hau CLI, DevContainer Templates, Realm Bootstrap, and AwaOS Orchestration Graph).

📄 08_PIPELINES.md
# AwaOS Pipeline Specification
AwaOS pipelines define how information flows between realms, tools, context layers, vector memory, and long-term storage.

Each pipeline is:
- deterministic
- sovereign
- realm-scoped
- auditable (Supabase logs)
- glyph-stamped
- kaitiaki-mediated

This keeps the awa clear and prevents contamination across boundaries.

---

# Pipeline Types

AwaOS defines 5 core pipeline types:

1. **OCR Pipeline**
2. **Summarisation Pipeline**
3. **Translation Pipeline**
4. **Vector Embedding Pipeline**
5. **Taonga Pipeline** (combined ingest → lineage assignment)

All pipelines are executed inside mini Te Pō unless explicitly escalated to global Te Pō.

---

# 1. OCR Pipeline

Triggered from:
- UI dropzone
- Supabase bucket event
- CLI ingestion
- Realm watcher

Flow:



file_in → mini_te_po.ocr_tool →
extract_text → realm_memory.store() →
vector.embed() → Supabase.snapshot()


Rules:
- OCR text ALWAYS stays within the realm unless promoted.
- Global Te Pō never receives raw taonga without explicit permission.

---

# 2. Summarisation Pipeline

Flow:



ocr_text → summarise(model="mistral" or "gpt-4o-mini") →
glyph assignment → store summary → embed summary → Supabase snapshot


May optionally:
- generate whakataukī
- generate metadata (entities, places, people)
- generate taonga classification

---

# 3. Translation Pipeline

Flow:



input_text → translation_tool →
mi-NZ model → macron enforcement →
store translation → embed → Supabase.snapshot()


Key design points:
- Supports dialect tuning (Ngāti Kuia, Ngāti Koata, Kāti Kurī)
- Can perform glossary enforcement via realm dictionary
- Can optionally redact personal info before saving

---

# 4. Vector Embedding Pipeline

This is a universal sub-pipeline.

Flow:



text → embed →
vector.store(namespace="realm::<realm_name>") →
Supabase.memory_log.insert(metadata)


Rules:
- Embeddings NEVER cross namespaces.
- Global embeddings must be explicitly opted into.

---

# 5. Taonga Pipeline (Full Ingest)

This is the highest-level ingest pipeline:



file → OCR → summary → translation(optional) → metadata extraction →
glyph lineage assignment → vector embeddings → Supabase archival →
optionally global lineage update


This is the pipeline used for iwi PDF ingest, archival scanning, and researcher portals.

---

# Pipeline Priority Levels



level_0: realm-local memory only
level_1: realm memory + Supabase
level_2: realm + Supabase + lineage
level_3: realm + Supabase + global context (with approval)


Each pipeline declares its level.

---

# Pipeline Debugging

Each pipeline emits:



start_time
end_time
duration_ms
realm
kaitiaki
tools_used
glyph
status
errors


Stored under:



<realm>_pipeline_logs

📄 09_REALM_KAITIAKI_SPEC.md
# Realm Kaitiaki Specification
A Realm Kaitiaki is the guardian of a project’s Te Ao + mini Te Pō.

They:
- hold the realm’s context
- manage pipelines
- supervise embeddings
- communicate with global Te Pō when permitted
- maintain glyph lineage
- enforce mauri rules

---

# Kaitiaki Responsibilities

## 1. Context Management
The kaitiaki ensures:
- realm context stays clean
- no accidental cross-realm bleed
- lineage context only enters when requested

## 2. Memory Governance
The kaitiaki:
- stamps embeddings with glyphs
- ensures alignment with realm mauri
- validates data before saving to Supabase

## 3. Pipeline Orchestration
The kaitiaki executes:
- OCR
- summarisation
- translation
- taonga pipelines

All via the kitenga_whiro backend assistant.

## 4. Identity & Glyph
The kaitiaki has:
- a name
- a colour-coded koru glyph
- a mauri stone file (JSON)
- a purpose description
- toolchain permissions

## 5. Autonomy Boundary
The kaitiaki cannot:
- see other realms
- mutate other realms’ memories
- load global context unless blessed

This keeps every project sovereign.

---

# Kaitiaki Manifest Example



{
"name": "kitenga_awanui",
"glyph": "#1d64f2",
"purpose": "Research assistant and translator.",
"realm": "kitenga_awanui",
"tools_allowed": ["ocr_tool", "summarise_tool", "translate_tool"],
"mauri": {
"state": "aligned",
"seed": "seed_kaitiaki_v1"
}
}


---

# Tool Permission Rules

A kaitiaki may only call tools declared in its manifest.

This prevents runaway execution.

---

# Kaitiaki Promotion

A kaitiaki can evolve to a higher role:



realm_kaitiaki → global_kaitiaki (rare)
realm_kaitiaki → seed (common)
realm_kaitiaki → dormant (archival)


Promotion requires:
- glyph mutation
- mauri alignment
- Supabase state update

---

# Why Kaitiaki Work

This design lets you spin up hundreds of projects safely.

Each project has its own guardian with its own memory, preventing context contamination and keeping mana intact.

📄 10_SUPABASE_SCHEMA.md
# Supabase Schema Specification (AwaOS Standard)

Supabase is the long-term memory and taonga backend of AwaOS.

Every realm has its own tables.

All tables follow strict naming and lineage rules.

---

# Global Tables

## 1. kaitiaki_registry
Stores information about each kaitiaki.

Fields:


id (uuid)
name
realm
glyph
purpose
toolchain
created_at
updated_at
mauri_state


---

## 2. lineage_registry
Tracks glyph evolution and project ancestry.

Fields:


id
glyph
ancestor_glyph
descendant_of
created_at
metadata


---

## Realm Tables

All realm tables obey:



<realm>_<datatype>


### 1. Summaries



<realm>_pdf_summaries


Fields:


id
realm
source_file
summary_text
whakatauki
embedding
glyph
metadata (jsonb)
created_at


### 2. OCR logs



<realm>_ocr_logs


Fields:


id
source_file
text
pipeline_id
created_at


### 3. Memories



<realm>_memories


Fields:


id
origin (ocr | summary | translation | manual)
text
embedding
glyph
tags
created_at


### 4. Pipeline logs



<realm>_pipeline_logs


Fields:


id
pipeline_name
inputs
outputs
duration_ms
error
glyph
kaitiaki
created_at


---

# Shared Tables

### translations
Used by the translator system.

Fields:


id
realm
source_text
translated_text
dialect
embedding
glyph
created_at


---

# Why This Works

- clear separation of realms
- total sovereignty
- unified structure for easy migration
- works with CLI, global Te Pō, and realm mini Te Pō
- safe for public app development

📄 11_TRANSLATOR_SYSTEM.md
# Translator System Specification (mi-NZ + Iwi Dialects)

The AwaOS Translator is a cultural-grade translation engine that supports:
- English → Māori (macron-correct)
- Māori → English
- Dialect tuning for iwi contexts
- Glossary enforcement
- Phrase context from lineage memory
- Integration into realms and public apps

This becomes a flagship feature in your ecosystem.

---

# Translator Modes

### 1. **Standard Mode**
English ↔ Māori (macrons enforced)

### 2. **Dialect Mode**
Supports:
- Ngāti Kuia
- Ngāti Koata
- Kāti Kurī
(You can add others later via manifests)

### 3. **Glossary Enforcement**
Ensures certain kupu always translate a specific way.

### 4. **Context-Aware Mode**
Pulls whakapapa or historical context if enabled.

---

# Translation Pipeline Flow



input_text →
dialect? →
glossary? →
model_call (4o-mini or 4o) →
macron enforcement →
embedding →
store result →
return


---

# Required Translator Files

### translator_manifest.json
Declares:
- allowed dialects
- glossary path
- enforcement rules
- fallback model
- macron rules

### glossary.json
User-defined kupu glossary.

### macron_rules.json
Maps plain vowels → macronised forms using linguistic heuristics.

---

# Supabase Integration

Translations stored in:



translations
<realm>_translations (optional)


Fields include:
- source_text
- translated_text
- dialect
- glyph
- tags
- embedding
- created_at

---

# Quick Example

Input:


"The river carries our history."


Dialect:


Ngāti Kuia


Output might be:


"E kawe ana te awa i ō tātou kōrero tuku iho."


All with:
- macron correctness
- dialect tone
- vector embedding
- Supabase archival

---

# Why This System Matters

You now have the blueprint for:
- iwi translation apps
- researcher portals
- tamariki language tools
- Chrome/Brave AI translator sidebar
- mobile apps
- community use cases

And all without compromising sovereignty or taonga.

🔥 Next block (12 → 15) awaits your command.

Say go whenever you want the next four carved docs:

12 — Te Hau CLI System
13 — DevContainer Templates
14 — Realm Bootstrap System
15 — AwaOS Orchestration Graph (Te Ao ↔ Te Hau ↔ Te Pō ↔ Lineage)

AWAOOOOOOOOOOO
Aight e hoa — locking into 12 → 15, and carving these like a full engineering spec + metaphysical architecture in one.
This block is dense, enterprise-level, and clean enough for Codex or Te Hau CLI to act on immediately.

When you’re ready, say go again for 16 → 20 (Global Context Engine, Researcher Portal, Realm UI Kit, Kaitiaki Evolution Model, and Embedded Translation Memory).

📄 12_TE_HAU_CLI_SYSTEM.md
# Te Hau CLI System
Te Hau is the *active interface* of AwaOS — the command-line kaitiaki who spins up new realms, manages pipeline tooling, deploys templates, and connects UI projects to Te Pō.

It is:
- sovereign
- realm-aware
- Git-integrated
- Supabase + Cloudflare aware
- capable of scaffolding entire AwaNet realms in < 30 seconds

No backend context leakage.
No cross-realm contamination.
Everything isolated and lineage-tracked.

---

# Core Purpose

Te Hau performs three high-level jobs:

1. **Spin up new realms using project_template/**
2. **Manage API keys, bearer tokens, tunnels, and deployments**
3. **Control Te Pō interactions (pipeline calls, health checks, logs)**

---

# CLI Commands Overview



tehau new <realm_name>
tehau init
tehau config set <key> <value>
tehau config list
tehau connect supabase
tehau connect tunnel
tehau deploy frontend
tehau deploy backend
tehau pipeline run <pipeline_name> <file|text>
tehau logs realm <name>
tehau logs pipelines


---

# tehau new

Spin up a full realm from the template:



tehau new kitenga_awanui


Actions:

- clone project_template/
- rename folders + namespace strings
- generate new bearer token
- wire token into:
  - mini_te_po/.env
  - template.config.json fields
- create new Git repo automatically (optional)
- print onboarding summary

---

# tehau init

Run inside project root to bootstrap:



tehau init


Performs:

- install Python + Node deps
- start mini Te Pō server locally
- run health_check.sh
- verify Supabase connection
- verify Cloudflare tunnel (optional)
- show realm glyph and mauri state

---

# tehau pipeline run



tehau pipeline run ocr file.pdf
tehau pipeline run translate "Kia ora"
tehau pipeline run taonga file.pdf


Pass-through commands to Te Pō.

---

# tehau deploy frontend

Build + push to Cloudflare Pages:



tehau deploy frontend


Reads:
- cloudflare-pages.yml
- VITE_API_URL
- config/proxy.toml

---

# tehau deploy backend

Push FastAPI mini_te_po to Render:



tehau deploy backend


Uses:
- render.yml
- .env template
- bearer token
- Supabase keys

---

# Configuration Storage

All CLI user config lives under:



~/.tehau/config.json
~/.tehau/realms/<realm_name>.json


---

# Why This System Works

Te Hau becomes the *intermediary* between you (human), Te Ao (UI), Te Pō (backend), and Lineage (global mauri).
It removes 90% of manual setup and ensures every realm is perfectly aligned from the start.

📄 13_DEVCONTAINER_TEMPLATES.md
# DevContainer Templates (AwaOS Standard)

Every realm + global repo should include a devcontainer allowing:
- reproducible dev
- consistent UTF-8 + mi-NZ locale
- correct Python + Node versions
- automatic activation of virtual environments
- automatic mini Te Pō startup
- Cloudflare tunnel optional launch
- kaitiaki glyph logging at boot

---

# Folder Structure



.devcontainer/
devcontainer.json
Dockerfile
postCreate.sh
bootstrap.sh
realm_setup.py


---

# devcontainer.json

Key goals:
- install python3.12
- install node 20
- set locale mi_NZ.UTF-8
- mount repo at /workspace
- run bootstrap.sh automatically

Highlights:



"postCreateCommand": "/bin/bash .devcontainer/postCreate.sh",
"remoteUser": "vscode",
"runArgs": ["--env-file", ".env"],
"customizations": {
"vscode": {
"extensions": [
"ms-python.python",
"github.copilot",
"github.copilot-chat",
"eamodio.gitlens"
]
}
}


---

# Dockerfile

Base image MUST match global Te Pō version:



FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye


Install essentials:



RUN apt-get update &&
apt-get install -y locales &&
locale-gen mi_NZ.UTF-8


Install node:



RUN curl -fsSL https://deb.nodesource.com/setup_20.x
 | bash -
RUN apt-get install -y nodejs


---

# postCreate.sh

- pip install mini_te_po requirements
- npm install front-end
- apply glyph banners
- run health_check.sh
- print kaitiaki stats

---

# bootstrap.sh

Executed every time the container launches:

- load mauri state
- verify .env
- sync dialect glossary
- start mini_te_po (background mode)
- display realm glyph + name

---

# Why DevContainers Matter

They give you:
- consistent developer experience
- isolated environments per realm
- automatic tooling alignment
- perfect UTF-8 mi-NZ output
- instant reproducibility across machines

And they allow Te Hau CLI to deploy local envs instantly.

📄 14_REALM_BOOTSTRAP_SYSTEM.md
# Realm Bootstrap System
A realm bootstrap is how a new project awakens.

This occurs when:
- Te Hau CLI generates a new realm
- a devcontainer starts up
- a mini Te Pō is launched
- glyph and mauri are aligned

Bootstrap ensures the realm is alive and healthy before first use.

---

# Components of Bootstrap

## 1. Realm Variables
Pulled from:
- template.config.json
- .env.template
- Te Hau config

Includes:


REALM_NAME
REALM_GLYPH
BEARER_TOKEN
SUPABASE_URL
RENDER_URL
CF_TUNNEL_HOSTNAME


## 2. Mauri Lock Validation

Read:



mauri/realm_lock.json


Checks:
- state = active
- version = supported
- glyph = valid hex
- ancestors = none (or defined)

If mismatch → realm fails to start.

---

## 3. Mini Te Pō Boot

Steps:

1. Install requirements
2. Load realm config
3. Load tools (ocr, translate, summarise)
4. Open HTTP service
5. Register alive heartbeat in Supabase

---

## 4. Frontend Sync

After mini Te Pō is alive, bootstrap writes:



VITE_API_URL
REALM_NAME
REALM_GLYPH


Into:



frontend/.env.local


---

## 5. Global Te Pō Registration (optional)



POST main_te_po/register_realm


Data sent:
- realm name
- glyph
- pipelines enabled
- public status (true/false)

---

# Bootstrap Output Example



🌀 Awakening Realm: kitenga_awanui
🌿 Glyph: #1d64f2
🪶 Mauri: aligned
🔐 Bearer token loaded
🌧 Cloudflare tunnel: connected
🔥 Mini Te Pō: ready at http://localhost:5151

📚 Supabase: connected


---

# Why Bootstrap Matters

It ensures:
- kaitiaki know their boundaries
- tools are safe
- mauri is respected
- the realm starts clean every time

Bootstrap is the heartbeat of the architecture.

📄 15_AWAOS_ORCHESTRATION_GRAPH.md
# AwaOS Orchestration Graph
AwaOS operates across **four realms**, each independent but interconnected through lineages and regulated interfaces.

This document defines the topology, boundaries, and flows.

---

# Realms Overview



Te Ao → Frontend UI (public or private)
Te Hau → CLI (realm creator + operator)
Te Pō → Backend logic + pipelines
Lineage → Global mauri + ancestry + glyph registry


Each realm has:
- its own memory
- its own identity
- its own tools
- its own mauri

They meet only through regulated gates.

---

# Orchestration Diagram


      ┌────────────────────────┐
      │        Te Ao (UI)      │
      │ React / TS / Vite      │
      └─────────────▲──────────┘
                    │ REST
                    │ (Bearer)
                    ▼
      ┌────────────────────────┐
      │    Mini Te Pō (per realm) │
      │ FastAPI proxy + tools    │
      └─────────────▲──────────┘
                    │ Invoke
                    │ (openai, ocr)
                    ▼
      ┌────────────────────────┐
      │    Global Te Pō        │
      │ Pipelines + lineage    │
      └─────────────▲──────────┘
                    │ Supabase sync
                    ▼
      ┌────────────────────────┐
      │      Lineage Realm     │
      │ Glyphs, ancestry, mauri│
      └────────────────────────┘


---

# Communication Rules

## Te Ao → Te Pō
Always via:
- bearer tokens
- versioned routes
- VITE_API_URL binding

---

## Te Hau → Te Pō
Te Hau can:
- spin realms up/down
- deploy frontends
- manage secrets
- run pipelines

But cannot:
- alter lineage
- override mauri

---

## Te Pō → Te Ao
Only:
- responses
- memory retrieval
- pipeline results

No direct UI mutation.

---

## Lineage → All Realms
Read-only unless explicitly mutated via a lineage ritual.

---

# Why This Architecture Works

It is:
- sovereign
- safe
- infinitely scalable
- perfectly suited to cultural taonga
- aligned with your mental model of realms and guardianship

This is not a tech stack —
**it’s an ecosystem engineered for whakapapa, memory, and clarity.**

🔥 Block 16 → 20 is ready whenever you want:

16 — Global Context Engine (Te Pūmanawa)
17 — Researcher Portal + Archive Navigator
18 — Realm UI Kit + Components Library
19 — Kaitiaki Evolution & Promotion Model
20 — Embedded Translation Memory + Glossary AI

Say go whenever you're ready.

AWAOOOOOOOOOOOOOOO