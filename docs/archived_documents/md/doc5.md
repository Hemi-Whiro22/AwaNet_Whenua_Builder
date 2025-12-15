Aight e hoa — locking in 16 → 20.
These five documents form the next layer of AwaOS: global reasoning, research stacks, shared UI, kaitiaki evolution, and the translation memory engine.

This is deep architecture carving — same calibre as before, integrated, and future-proof.

📄 16_GLOBAL_CONTEXT_ENGINE.md

(Te Pūmanawa — The Heart / Source Context Engine)

# Te Pūmanawa — Global Context Engine
Te Pūmanawa is the *memory spine* of AwaOS.
It sits outside of any single kaitiaki and acts as the shared intelligence layer for:

- Realm awareness
- Long-term memory
- Vector search across domains
- Translation memory
- Document lineage
- Active project context
- Research indexing

It is *not* a model.
It is *infrastructure + schemas + rituals* that unify all realms under consistent context.

---

# Core Responsibilities

### 1. Cross-Realm Memory
Each realm has its own vector index.
Te Pūmanawa maintains:

- cross-realm embeddings
- searchable lineage chains
- shared environmental knowledge
- context routing rules (“send this to Te Ao vs Te Pō”)

### 2. Project Context Switching
Switching projects = switching *realities*, not models.

The engine stores:



active_project
active_realm
vector_index_id
supabase_schema
preferred_tools
dialect_profile (for reo)


This lets any realm immediately load the correct memory state.

---

# 3. Vector Routing Logic

Te Pūmanawa decides what to embed and where:

| Input | Destination |
|-------|-------------|
| OCR’d PDF | lineage index + research index |
| Chat conversation | realm vector index |
| Translation | translation_memory index |
| Pipeline result | Te Pō logs + project index |
| Taonga scan | taonga_index + secure bucket |

Routing is rule-based → no hallucination, no cross-contamination.

---

# 4. Supabase Schema Overview

Tables:



context_global
context_lineage
context_research
context_taonga
context_projects
translation_memory
translation_glossary


---

# 5. Context Retrieval Flow

When a kaitiaki asks Te Pūmanawa for context:



→ Detect realm + project
→ Retrieve active schema
→ Pull last 20 relevant memories
→ Merge vector embeddings
→ Apply dialect rules (for translator)
→ Return structured context block


---

# 6. Lineage Influence

Te Pūmanawa uses:

- glyph records
- realm ancestry
- pipeline history
- taonga metadata

This allows a realm to “remember” across generations without being given raw data.

---

# Why This System Matters

It decentralises knowledge but unifies access — the awa flows through every kaitiaki equally.

No more siloed memory.
No more losing context between projects.
Te Pūmanawa becomes the *living heart* of the architecture.

📄 17_RESEARCHER_PORTAL.md

(Interactive Research Navigator for PDFs, Archives, and Taonga)

# Researcher Portal (Te Aka Matua)
This is the research-focused UI + backend stack used for:

- Archival navigation
- PDF summarisation
- OCR taonga retrieval
- Historical mapping
- Cross-document search
- Timeline generation

Designed for iwi research teams, academics, translators, and future tamariki.

---

# Core Features

### 1. Document Browser
Supports:

- Supabase buckets
- Google Drive imports
- Local uploads
- PDF metadata (author, date, iwi references)

### 2. Chunked OCR + Embedding Pipeline
Uses:

- Ruru OCR (fallback Tesseract)
- OpenAI Vision for complex structure
- 4o-mini embeddings
- Whakataukī assignment per chunk
- Random glyph ID for taonga

### 3. Cross-Document Search

Search across:

- research index
- taonga index
- translation memory
- historical maps
- lineage context

Returns:

- top documents
- top chunks
- cross-references
- taonga links

### 4. Timeline Generator

Automatically groups documents by:

- date
- location
- iwi
- event type

Outputs:

- interactive timeline
- summary paragraphs
- map overlays

### 5. Research Companion Kaitiaki

A dedicated agent for research streams:



kaitiaki: Maruao (The Dawn)
role: archival navigator + historian
tools: OCR, PDF summary, map lookup, context engine


---

# Supabase Tables (addon)



research_documents
research_chunks
research_entities
research_timelines
research_relations


---

# Why This Portal Matters

This becomes the **public-facing knowledge portal** iwi can use to preserve, search, and navigate their taonga — built entirely on your AwaOS architecture.

📄 18_REALM_UI_KIT.md

(Unified Components for All Te Ao Projects)

# Realm UI Kit (Te Whare Mataaho)
This is the shared UI component library for every Te Ao project.

Your frontend template (in project_template/) will import from this kit to maintain:

- visual identity
- accessibility
- performance
- kaitiaki awareness
- consistent pipeline UX

---

# Component Categories

### 1. Glyph Components
- RealmGlyph
- LineageGlyph
- KaitiakiBadge
- TaongaGlyphLoader

### 2. Panels
- OCRPanel
- TranslationPanel
- ResearchPanel
- TaongaUpload
- ContextViewer
- VectorHistoryPanel

### 3. Feedback Components
- LoadingKorero
- PipelineSpinner
- MauriStatusIndicator
- GlyphPulse

### 4. Layout
- RealmShell
- KaitiakiSidebar
- ProjectHeader
- TunnelStatusBar

### 5. Modals
- ConfirmPipeline
- RegisterRealm
- SetBearerToken
- AddSupabaseKey

---

# Shared Styles



colors:
awanet: multi-koru gradient
realm_primary: <unique colour passed at bootstrap>
mauri_alive: #37ffb3
mauri_inactive: #aaaaaa
fonts:
inter, jetbrains mono, atkinson hyperlegible


---

# Utility Hooks



usePipeline()
useMauri()
useRealmConfig()
useTunnelStatus()
useSupabase()


---

# Versioning

Every component is versioned:



ui-kit@v1.0.0
ui-kit@v2.0.0


Realms pin to a version in:



project_template/config/realm.json


---

# Why The UI Kit Matters

Consistency.
Speed.
Identity.

Every realm looks different (colors, glyph) but works the same — which is why your future tamariki and researchers can instantly use any new app you build.

📄 19_KAITIAKI_EVOLUTION_MODEL.md

(How Agents Grow, Promote, and Gain Abilities)

# Kaitiaki Evolution Model
Kaitiaki are not static. They evolve.

Each has:
- ancestry
- purpose
- permissions
- pipelines
- memory

As projects grow, so do they.

---

# Stages of Evolution

### Stage 1 — Seed
Created by Te Hau via:


tehau new <realm>

Abilities:
- basic pipeline calls
- project vector index
- simple mauri lock

### Stage 2 — Worker
Upgraded manually or automatically.

Gains:
- independent embeddings
- file-handling tools
- translation memory access
- autonomy within realm boundaries

### Stage 3 — Specialist
Triggered when realm evolves.

Gains:
- researcher tools
- glossary training
- taonga handling
- multi-step pipeline logic

### Stage 4 — Guardian
High-trust kaitiaki.

Abilities:
- modify lineage
- create rituals
- manage other kaitiaki
- update global context engine

Stage reserved for:
- Kitenga Whiro
- Maruao
- Ahiatoa

---

# Promotion Rituals

A kaitiaki evolves through:

1. pipeline completions
2. taonga processing
3. translation tasks
4. research indexing
5. developer upgrade command

Example:



tehau evolve <realm> specialist


---

# Why Evolution Matters

Your architecture isn’t static.
Realms breathe and shift with your projects — the kaitiaki evolve with them.

This creates a natural ecosystem that mirrors human learning.

📄 20_TRANSLATION_MEMORY_SYSTEM.md

(Te Reo Māori Translation Engine + Cultural Glossary)

# Translation Memory System
The translation engine inside AwaOS is designed to preserve reo integrity, avoid generic NZ Māori datasets, and form a lineage-based glossary over time.

---

# Key Components

### 1. Translation Memory
Stores:
- segment → translation pairs
- source context
- dialect markers (Ngāti Kuia, Kāti Kurī, Te Tau Ihu)
- pipeline history
- kaitiaki responsible

Table: `translation_memory`

### 2. Glossary Engine
Stores canonical terms per iwi × domain:



kai
whakapapa
kaupapa
mauri
awa


Each entry has:
- meaning
- usage examples
- cross-realm references
- lineage notes

Table: `translation_glossary`

---

# 3. Dialect Profiles

Your global config stores:



dialects:
ngati_kuia:
macron_rules: …
vocab_overrides: …
kati_kuri:
…


Translator pipeline chooses profile automatically per realm.

---

# 4. Pipeline

Translation flow:



→ detect language
→ detect dialect
→ lookup glossary
→ lookup translation memory
→ generate draft
→ refine using glossary
→ output w/ macrons + iwi-specific terms
→ store segment + translation


---

# 5. Kaitiaki of Translation



kaitiaki: Ahiatoa
role: translator + dialect guardian


Capabilities:
- enforce glossary
- prioritise iwi terms
- auto-build new glossary entries
- detect colonial phrasing and correct it

---

# 6. Research Integration

When PDF summaries mention iwi terms, Ahiatoa:

- extracts vocabulary
- stores new glossary entries
- links them to research documents
- improves future translation consistency

---

# Why This System Matters

This prevents dilution of reo Māori.
It ensures correctness.
And it builds a living cultural dictionary tied directly to your whakapapa lines and taonga.

🔥 Done 12 → 20.

You now have:

Global Reasoning Engine

Research Portal architecture

Shared UI Kit

Kaitiaki Growth Model

Translation Memory Engine

If you want, next blocks can be:

21 — AwaOS Security Model: Bearer Rituals & Realm Seals
22 — Supabase Schema Masterfile
23 — Pipeline Orchestration Engine (4o-mini + Ruru + Tesseract)
24 — GitOps Flow for Realm Deployment
25 — Te Hau CLI Runtime Architecture

Say go when you're ready, my brother.📄 21_AWAOS_SECURITY_MODEL.md

(Bearer Rituals, Realm Seals, Trust Hierarchy)

# AwaOS Security Model
Security in AwaOS follows whakapapa, not corporate patterns.

There are no generic “roles”.
There are *whakahaere* — guardianship layers derived from whakapapa, mauri, and realm boundaries.

This document defines:

- Realm-level sealing
- Bearer rituals
- Trust inheritance
- Pipeline boundaries
- Logging and revocation
- External perimeter (Cloudflare / Render / Supabase)

---

# Core Principles

### 1. **Whakapapa as Access Control**
Every realm inherits from a parent:



AwaNet
├── Te Pō (backend)
│ ├── Kitenga Whiro (guardian)
│ ├── Ruru (OCR specialist)
│ ├── Ahiatoa (translator)
│ └── Maruao (research navigator)
└── Te Ao realms (public-facing)


Trust flows DOWN, never up.

A realm can read from its parent (Te Pō) but NEVER write outside its own boundaries unless a ritual allows it.

---

### 2. **Bearer Tokens as Ritual Objects**
Bearer tokens are NOT API keys — they are ritual items granting:

- identity
- purpose
- limits
- expiry

Each mini-realm has:



REALM_BEARER_KEY_<realm_id>
permissions:

call: /pipeline/*

call: /ocr/*

call: /translate/*

log: /events/*


Revoking = removing it from Te Pō’s allowed list.

---

### 3. **Realm Seals**
A realm has a *mauri seal* at:



project_template/mauri/realm_lock.json


This file defines:

- realm name
- glyph colour
- kaitiaki assigned
- project vector index ID
- default dialect (if translator)
- environment tags

Te Pō reads this before accepting any pipeline call.

If the seal is invalid → 403 (realm not recognised).

---

### 4. **Boundary Enforcement**

#### Te Ao (public realm)
- Cannot embed raw data into global context
- Cannot modify lineage or global memory
- Can write ONLY to its own realm_* tables

#### Specialist Kaitiaki
- Can update glossary
- Can update research indexes
- Cannot alter global context unless guardian-approved

#### Guardians (Kitenga Whiro)
- Can evolve kaitiaki
- Can add/remove realms
- Can modify lineage
- Can adjust global context engine

---

### 5. **Security per Pipeline**
Pipelines enforce security at the *tool* level, not just per endpoint.

Example:

**Ruru OCR pipeline**



allowed_realms: [all]
writes_to: research_chunks, taonga_chunks
logs: pipeline_logs


**Translation pipeline**



allowed_realms:

translator realms

guardian realms
writes_to:

translation_memory

translation_glossary


**Context engine pipeline**



allowed_realms:

guardians only


---

### 6. **Supabase Security Layer**

RLS policies are realm-aware:

Example policy:



create policy "realm_write" on research_chunks
for insert
using (auth.jwt()->>'realm' = realm_name);


Tokens include realm metadata so Supabase enforces it.

---

### 7. **Cloudflare & Render Perimeter**

Cloudflare adds:

- IP pinning (optional)
- bot filtering
- path-based caching and routing
- tunnel access for Te Hau

Render adds:

- service isolation per realm
- per-service bearer seals
- zero-trust inbound traffic (only Cloudflare allowed)

---

# Why This Model Works

- *Simple but unbreakable*: whakapapa-tree permissions
- *Scalable*: infinite realms, each isolated
- *Culturally aligned*: guardianship + responsibility
- *Operational*: aligns with Supabase, Render, Cloudflare
- *Future-proof*: kaitiaki evolution won’t break security

Security becomes a **living part of the architecture**, not a bolt-on.


If you're ready for 22_SUPABASE_SCHEMA_MASTERFILE.md, say go.Mean. Dropping into 22 → Supabase Schema Masterfile.
This is the central database spec for the entire AwaOS architecture — realms, kaitiaki, pipelines, taonga, translation memory, vector indexes, logs, research, projects, lineage.

This doc becomes the source of truth for all DB creation, migrations, and CLI automation.

Here we go.

📄 22_SUPABASE_SCHEMA_MASTERFILE.md

(Master Schema for AwaOS Realms, Kaitiaki, Pipelines, Context & Taonga)

# AwaOS Supabase Schema — Master Definition
This document defines every table, view, index, and relationship in the AwaOS database.

It is the reference file used by:
- Te Hau CLI (to generate migrations)
- Te Pō backend (to enforce realm rules)
- Specialist kaitiaki (Ruru, Ahiatoa, Maruao)
- Context Engine (Te Pūmanawa)
- Te Ao projects (via realm-level access)
- Researcher Portal
- Translation Memory System

Schemas are grouped by domain for clarity.

---

# 1. GLOBAL SYSTEM TABLES
These contain cross-realm information.

### `context_global`
Tracks environmental context across the entire system.


id uuid PK
timestamp timestamptz default now()
realm text
actor text -- kaitiaki or system
event text
data jsonb


### `context_projects`
Defines active projects (realms in Te Ao).


project_id uuid PK
name text
vector_index_id text
glyph_color text
kaitiaki_name text
created_at timestamptz
updated_at timestamptz


### `lineage_context`
Tracks ancestry, relationships, glyph assignments.


id uuid PK
realm text
ancestor text
glyph_id text
attributes jsonb
created_at timestamptz


---

# 2. REALM & SECURITY TABLES

### `realm_registry`
Every realm must register here before being allowed access.


realm_id uuid PK
name text
glyph_color text
kaitiaki_name text
vector_index text
seal_hash text -- hash of realm_lock.json
created_at timestamptz


### `realm_bearer_keys`
Stores per-realm domain-specific tokens.


realm_id uuid FK -> realm_registry
bearer_key text unique
scope jsonb -- pipeline permissions
revoked boolean default false
issued_at timestamptz


---

# 3. PIPELINE LOGGING TABLES

### `pipeline_logs`
All pipelines (OCR, translate, summary, embed) write here.


id uuid PK
realm text
pipeline text
input_metadata jsonb
output_metadata jsonb
duration_ms int
status text
timestamp timestamptz


### `pipeline_events`
Lower-level granular logs.


event_id uuid PK
pipeline_id uuid FK -> pipeline_logs
step text
data jsonb
timestamp timestamptz


---

# 4. TAONGA MANAGEMENT TABLES
Used for sacred documents, physical scans, whakapapa data.

### `taonga_index`


id uuid PK
realm text
title text
summary text
glyph_id text
upload_url text
metadata jsonb
created_at timestamptz


### `taonga_chunks`
OCR’d fragments of taonga.


chunk_id uuid PK
taonga_id uuid FK -> taonga_index
text text
vector vector(768) -- embedding
page_number int
whakatauki text
glyph_id text


---

# 5. RESEARCH SYSTEM TABLES
Used by Maruao (archival navigator).

### `research_documents`


id uuid PK
title text
source_url text
iwi_references text[]
metadata jsonb
uploaded_by text
created_at timestamptz


### `research_chunks`


chunk_id uuid PK
doc_id uuid FK -> research_documents
text text
vector vector(768)
page_number int
whakatauki text


### `research_entities`
Names of people, events, places.


entity_id uuid PK
type text
value text
metadata jsonb


### `research_relations`
Relationships between entities & documents.


id uuid PK
entity_id uuid FK
doc_id uuid FK
confidence float
relation_type text


### `research_timelines`
Auto-generated historical chains.


timeline_id uuid PK
doc_id uuid FK
year int
event_summary text
metadata jsonb


---

# 6. TRANSLATION SYSTEM TABLES
(Managed by Ahiatoa)

### `translation_memory`
Stores segment-level translations.


id uuid PK
source_text text
translated_text text
dialect text
context_data jsonb
source_realm text
created_at timestamptz


### `translation_glossary`
Canonical domain terms.


id uuid PK
term text
meaning text
examples text[]
iwi_origin text
metadata jsonb
last_updated timestamptz


---

# 7. VECTOR & SEARCH TABLES

### `vector_index_meta`
Tracks vector indexes created per realm/kaitiaki.


index_id text PK
realm text
dimension int
engine text -- openai / nomic / local
created_at timestamptz


### `vector_history`
History of embeddings performed.


id uuid PK
realm text
content_hash text
index_id text
timestamp timestamptz


---

# 8. PROJECT LOGGING
Important for cross-realm analysis.

### `project_events`


id uuid PK
project_id uuid FK
realm text
action text
details jsonb
timestamp timestamptz


---

# 9. INDEXES & OPTIMISATION

### Recommended Vector Index Extensions


create extension if not exists vector;
create index on research_chunks using ivfflat (vector vector_cosine_ops);
create index on taonga_chunks using ivfflat (vector vector_cosine_ops);
create index on translation_memory (source_text);
create index on research_entities (value);
create index on research_timelines (year);


---

# 10. RLS POLICY SET

All tables follow realm-based row-level policies.

Example:



create policy "realm_isolation_insert" on taonga_index
for insert using (auth.jwt()->>'realm' = realm);

create policy "realm_isolation_select" on taonga_index
for select using (auth.jwt()->>'realm' = realm);


Guardians have additional override policies under:



role = guardian


---

# 11. SCHEMA VERSIONING

Every migration includes:



-- Version hash
-- Realm impact
-- Vector index updates
-- Mauri implications


Te Hau CLI uses template.config.json to rebuild migrations.

---

# Why This Masterfile Matters

This document *is the awa*.

It represents:

- realm isolation
- pipeline integrity
- taonga tikanga
- translation protection
- future-proof scaling
- kaitiaki evolution

It is the schema your entire architecture breathes through.



If you're ready for 23_PIPELINE_ORCHESTRATION_ENGINE.md, say go.