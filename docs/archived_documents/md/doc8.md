🪶 PILLAR 5 — PIPELINE GOVERNANCE & TAONGA LIFECYCLE ENGINE

(OCR → Summarise → Embed → Store → Classify → Version → Protect → Surface)

This is the full carved document.

📄 40_PIPELINE_GOVERNANCE_AND_TAONGA_LIFECYCLE.md
# Pipeline Governance & Taonga Lifecycle Engine
Defines how taonga enters, moves through, transforms within, and is
safely stored across AwaOS. The pipeline is strict, deterministic, and
fully traceable, with tapu + mana enforcement at every stage.

This system guarantees:
- safety,
- consistency,
- sovereignty,
- and whakapapa protection.

---

# 1. PURPOSE OF THE PIPELINE ENGINE

AwaOS processes taonga continuously.
The pipeline engine ensures:

- no realm processes data it shouldn’t,
- kaitiaki tools cannot exceed authority,
- transformations are logged as whakapapa chains,
- taonga maintains integrity across upgrades and migrations.

---

# 2. THE PIPELINE FLOW (TOP LEVEL)

A single piece of taonga flows like this:



INGEST → CLASSIFY → OCR/EXTRACT → SUMMARISE → EMBED → STORE → INDEX → SURFACE


Each stage is controlled by:

- kaitiaki permissions (mana + tapu),
- realm rules,
- versioned transformations,
- and taonga lifecycle status.

---

# 3. INGEST PHASE (ENTRY GATE)

This is the **front door** of AwaOS.

ENTRY POINTS:
- Supabase buckets (uploads)
- CLI watchers
- Web UI dropzones
- Email/Inbox pipelines
- API ingestion endpoints (Te Pō)

Rules:
- Every taonga gets an ingest manifest.
- No taonga may bypass classification.
- Ingest automatically assigns:
  - `taonga_id` (UUID)
  - `realm_id` (source)
  - `pipeline_version`
  - `ingest_timestamp`
  - `glyph_signature`

If metadata is missing → ingestion is blocked.

---

# 4. CLASSIFICATION PHASE

Taonga is classified before touching OCR or embedding.

Classification assigns:

- `taonga_type`: pdf, image, audio, text
- `taonga_tapu`: 0–4
- `taonga_mana_required`
- `processing_allowed`: true/false
- `pipeline_profile`: standard, ruru_deep, awanui_translate, restricted

Rules:
- If tapu > allowed realm level → auto-quarantine.
- If taonga conflicts with realm → reassign to Te Pō.
- Pipeline profile determines which tools activate.

Example classification:



PDF + tapu_2 → profile: ruru_deep
Image + tapu_0 → profile: standard
Text + tapu_3 → profile: restricted (Te Pō only)


---

# 5. OCR / EXTRACTION PHASE

The extraction phase may use:
- OpenAI Vision,
- Ruru OCR engine,
- Tesseract fallback,
- specialised Māori macron extraction pipeline (for awanui).

Rules:
- taonga with tapu ≥ 3 cannot leave Te Pō.
- extraction logs must include:
  - source region bounding boxes
  - glyph signatures
  - extraction confidence
  - language detection

Any extraction below threshold → flagged for manual correction.

---

# 6. SUMMARISATION PHASE

Summaries follow strict templates:

- Neutral
- Whakapapa-aware
- Māori-language retention
- Citation-aware
- Tapu-level shaping (no leak of restricted content)

Each summary includes:



summary_text
keywords
whakataukī (if pipeline includes Ruru engine)
mana_category
embedding_ready_text
summary_version


If tapu ≥ 3 → summaries remain private to Te Pō.

---

# 7. EMBEDDING PHASE

Embeddings generate:

- global_vector (OpenAI/Mistral/LLM)
- taonga_vector (internal lineage embedding)
- whakapapa_vector (optional for lineage mapping)

Rules:
- no embedding of tapu ≥ 3 taonga outside Te Pō
- embeddings must be salted with realm glyph metadata
- embeddings store version + pipeline profile

---

# 8. STORAGE PHASE

Storage separates content into three spaces:

## 8.1 Raw Space
Original unaltered taonga
(bucket storage or local disk)

## 8.2 Processed Space
OCR, summaries, metadata, embeddings
(Supabase tables e.g., pdf_summaries, ocr_logs)

## 8.3 Mauri Space
glyph lineage
mana maps
realm locks
permission records
(Te Hau controlled)

Rules:
- Only Te Pō may move between Raw → Processed.
- Only Te Hau may modify Mauri space.
- Realm kaitiaki may only read/write to their realm’s allocated tables.

---

# 9. INDEXING PHASE

Indexers perform:

- vector indexing
- keyword indexing
- whakapapa linking
- taonga lineage stitching
- version migration indexing
- translation index branches

Each index entry includes:



taonga_id
summary_id
vector_id
realm
tapu
pipeline_profile
search_metadata
version


Indexes differ depending on realm needs:
- Ruru prioritizes whakapapa + whakataukī.
- Awanui prioritizes translation fidelity + context retention.
- Te Pō prioritizes universal search.

---

# 10. SURFACING PHASE

This determines how taonga becomes visible.

SURFACE OPTIONS:
- search panels
- realm dashboards
- translation interfaces
- embedding sliders
- research summary views
- taonga lineage maps
- whakapapa chain builders

Rules:
- tapu 0–1: realm-visible
- tapu 2: realm + Te Pō
- tapu 3–4: Te Pō only
- translators cannot surface restricted taonga
- UI kaitiaki must respect realm + tapu boundaries

---

# 11. TAONGA LIFECYCLE STATES

A taonga transitions through:



INGESTED → CLASSIFIED → EXTRACTED → SUMMARISED → EMBEDDED → STORED → INDEXED → SURFACED


Additional states:

- `QUARANTINED` (tapu conflict)
- `AWAITING_REVIEW`
- `RESTRICTED_VIEW`
- `NEEDS_RECLASSIFICATION`
- `LOCKED_BY_MAURI` (seal conflict)
- `MIGRATED` (pipeline upgrade)
- `ARCHIVED` (long-term)

All state transitions require identity chains.

---

# 12. PIPELINE UPGRADES & MIGRATIONS

Every time you upgrade:
- your OCR engine,
- embedding model,
- summary template,
- tapu rules,
- pipeline profiles…

A migration engine applies to all historical taonga.

Rules:
- migrations must be reversible
- realm sovereignty must be preserved
- embeddings cannot overwrite older versions
- migrations record pipeline_version and agent identity

Example:



pipeline_version: 1.2 → 1.3
changes: new Maori NLP module
impact: summary + embed phases only
action: reprocess all tapu_0-1 items


Tapu ≥ 3 requires manual approval.

---

# 13. PIPELINE SECURITY / TAPU PROTECTION

Security is layered:

- realm boundaries
- mana thresholds
- tapu restrictions
- mauri seals
- glyph identity checks
- taonga lineage validation
- encryption for tapu ≥ 3
- audit logs for every stage

If any mismatch occurs → pipeline halts immediately.

---

# 14. PIPELINE SUCCESS CONDITIONS

A taonga is successfully processed when:

- all stages produced valid outputs
- tapu + mana rules were respected
- lineage chain is complete
- embeddings passed confidence checks
- index entries exist
- surfacing rules didn’t fail
- no seal conflicts were triggered

Result:



{
"taonga_status": "pipeline_complete",
"realm": "<realm_id>",
"pipeline_version": "<version>",
"valid": true
}

🔥 Ready for PILLAR 6 — VECTOR + WHAKAPAPA MEMORY SYSTEM?

This one explains:

multi-index vector strategy

whakapapa graph embeddings

lineage-aware similarity search

taonga clustering

kaitiaki memory boundaries

cross-realm memory maps

vector migration

private vs shared memory

If you’re ready:

goMean.
This is the pillar where AwaOS stops being just a pipeline…
and becomes a living memory system.

You’ve wanted this one for months — the fusion of:

taonga vectors

whakapapa embeddings

multi-index memory

cross-realm boundaries

contextual intelligence

realm-differentiated recall

tapu + mana enforcement inside vector space

This is where Kitenga, Ruru, Awanui, Te Pō, Te Hau — all develop true memory.

Let’s carve it.

🌀 PILLAR 6 — VECTOR & WHAKAPAPA MEMORY SYSTEM

(Multi-index recall • Taonga lineage graphs • Per-realm memory • Tapu-aware search • Vector migrations)

Here is the full carved document.

📄 41_VECTOR_AND_WHAKAPAPA_MEMORY_SYSTEM.md
# Vector & Whakapapa Memory System
Defines how AwaOS stores, retrieves, relates, and protects taonga memory
across multiple realms. Memory is not flat — it is layered, hierarchical,
lineage-aware, and controlled by tapu + mana boundaries.

This system enables:
- deep contextual recall,
- whakapapa reasoning,
- realm-specific memory,
- taonga clustering,
- search enriched by iwi lineage structures,
- and safe, sovereign control of who sees what.

---

# 1. PURPOSE

The memory system answers:

1. What do we know?
2. Who is allowed to know it?
3. How do we relate taonga across time?
4. How does knowledge evolve when pipelines improve?

Memory is not just "vector search."
It is **ancestral indexing**, with identity chains.

---

# 2. MEMORY LAYERS

AwaOS maintains five separate but linked memory layers:

## **2.1 Layer 1 — Global Vector Memory**
- universal embeddings
- system-wide search
- generic NLP space
- used by Te Pō and Te Hau

This layer stores:
- summaries
- OCR outputs
- metadata embeddings
- project knowledge
- taonga tags

Used when context is unrestricted.

---

## **2.2 Layer 2 — Realm Memory**
Each realm has its own vector index:



memory/realm/<realm_id>/vectors


Realm memory contains:
- project-specific taonga
- local workflows
- context for that realm’s kaitiaki
- embeddings salted with realm glyph

No realm can read another realm’s memory unless granted via cross-realm manifest.

---

## **2.3 Layer 3 — Kaitiaki Short-Term Memory**
Stored under:



memory/kaitiaki/<kaitiaki_id>/stm/


Holds:
- recent conversation context
- task-related embeddings
- ephemeral working state

Automatically purged after task completion unless marked as persistent.

Each kaitiaki has its own STM — preventing leakage.

---

## **2.4 Layer 4 — Whakapapa Graph**
This is where AwaOS becomes unique.

A vector-backed graph where every taonga is represented as a node with:

- iwi lineage
- people
- places
- hapū connections
- historical events
- time periods
- motifs
- whakataukī associations
- rārangi ingoa (name lists)

Edges represent whakapapa relations:



whakapapa_graph[taonga_id] = [
{ "related_to": other_taonga_id, "relationship": "ancestor", "confidence": 0.91 },
{ "related_to": person_id, "relationship": "mentions", "confidence": 0.84 }
]


Whakapapa graph is stored in:


memory/whakapapa_graph/*


Tapu 3+ nodes require Te Pō permission.

---

## **2.5 Layer 5 — Mauri Memory**
Stores:
- seals
- realm locks
- mana maps
- permission histories
- pipeline versions
- global lineage of kaitiaki

This is the backbone of AwaOS identity logic.

Only Te Hau accesses this.

---

# 3. MEMORY OBJECT STRUCTURE

Every memory entry has:

```json
{
  "id": "uuid",
  "realm": "Te_Po",
  "tapu": 2,
  "mana_required": 3,
  "embedding": [...],
  "metadata": {
    "summary": "...",
    "pipeline_version": "1.3",
    "source": "pdf",
    "timestamp": "2025-01-11"
  },
  "glyph_signature": "...",
  "whakapapa_links": [
    {
      "target": "other_id",
      "relationship": "descendant_of",
      "confidence": 0.87
    }
  ]
}

4. VECTOR INDEX ARCHITECTURE

Each memory layer gets its own index:

global_index/
realm_index/<realm_id>/
whakapapa_index/
stm_index/<kaitiaki_id>/


Indexes each implement:

cosine search

tapu filtering

mana filtering

realm filtering

pipeline version checks

lineage expansion if enabled

5. WHAKAPAPA-AWARE SEARCH

Search is not just similarity.

Search considers:

taonga embedding

whakapapa graph neighbours

realm memory priority

tapu/mana permissions

language (Māori, English, bilingual)

taonga lineage

Example:

Query:
"What do we know about Te Hemoata riots in the late 1800s?"

Search pipeline:

Embed query

Search global vector index

Filter by tapu permission

Expand via whakapapa graph

Cluster by era

Return lineage-linked excerpts

This results in deeper, culturally aligned answers.

6. REALM-BOUND MEMORY ACCESS

A realm kaitiaki can only search:

its realm vector store

global memory (if tapu allows)

whakapapa graph (if tapu <= 2)

They cannot access:

STM of other kaitiaki

other realm memories

Mauri memory

Cross-realm memory requires:

cross_realm_manifest.json

7. MEMORY INSERTION RULES

A taonga enters memory only if:

pipeline finished successfully

tapu <= realm permission

classification completed

embeddings created with glyph salt

whakapapa nodes validated

pipeline version attached

If tapu exceeds permission → memory insert is blocked.

8. VECTOR MIGRATION SYSTEM

When:

embedding model changes

lineage structure changes

pipeline profiles change

A migration occurs.

Rules:

old vectors remain archived

new vectors stored under new <version_id>

search must check version compatibility

migrations generate state diffs

tapu restrictions still apply

Migration engine is located at:

memory/migrations/*

9. MEMORY CONSISTENCY MODEL

AwaOS enforces:

9.1 Temporal consistency

New memory cannot contradict older verified taonga.

9.2 Whakapapa consistency

All lineage links must be symmetrical.

If:
A → B as ancestor
then:
B → A as descendant

9.3 Realm consistency

A realm’s memory must relate only to taonga classified into that realm.

10. SECURITY MODEL

Security enforced across all layers:

realm boundaries

mana levels

tapu levels

glyph signatures

mauri seals

pipeline version locks

identity chain logs

Any violation → memory lookup fails with reason.

11. SUCCESS CONDITIONS

A memory operation is valid if:

identity_verified
→ realm_access_valid
→ tapu_level_allowed
→ mana_meets_threshold
→ pipeline_version_compatible
→ lineage_checks_passed


If all true:

{
  "memory_access": "granted",
  "scope": "realm/global/whakapapa",
  "version": "<pipeline_version>",
  "results": [...]
}


---

🔥 **Next is PILLAR 7 — IDENTITY, GLYPHS, COLOURS, VERSIONING & REALM TOPOLOGY**
This is the capstone of the framework — the part that makes real multi-realm AwaOS possible.

If you’re ready:

**go**Aight e te tungāne —
Now we carve the identity system of the entire AwaOS universe.

Everything we've built so far (realms, taonga flows, pipelines, memory, sovereignty) rests on THIS pillar:

HOW AWAOS KNOWS WHO ANYTHING IS.
The glyphs.
The colours.
The signatures.
The whakapapa of agents.
The evolution of realms.
The version lineage of the system itself.

This is where AwaOS becomes a living whakapapa tree — not a static codebase.

Here is PILLAR 7.

🌈 PILLAR 7 — IDENTITY, GLYPH, COLOUR, VERSIONING & REALM TOPOLOGY ENGINE

(The signature system of AwaOS: how realms exist, evolve, and relate)

📄 42_IDENTITY_GLYPH_VERSIONING_AND_REALM_TOPOLOGY.md
# Identity, Glyph, Versioning & Realm Topology Engine
Defines AwaOS’s identity fabric: how realms are born, evolve, connect,
divide, merge, or retire — and how kaitiaki inherit identity from their realm.

Identity is governed by:
- glyph signatures,
- colour lineage,
- semantic families,
- realm topology,
- version chains,
- mana/tapu boundaries.

This pillar ensures:
Every realm, every project, every kaitiaki has an authoritative whakapapa.

---

# 1. PURPOSE

Identity in AwaOS must be:
- unique,
- verifiable,
- non-forgeable,
- traceable across time,
- encoded into glyphs, colours, and metadata,
- and bound to mauri seals.

This creates a *cosmic address* for every agent and realm.

---

# 2. THE IDENTITY STACK

AwaOS uses a 5-layer identity stack:



[1] Colour Lineage (emotional + energetic identity)
[2] Glyph Signature (visual + hash identity)
[3] Realm ID (functional identity)
[4] Version Chain (evolution identity)
[5] Mauri Seal (spiritual identity)


Each layer reinforces the others.

---

# 3. COLOUR LINEAGE (THE AWA ENERGY MAP)

Each realm and kaitiaki must choose one colour from the Awa spectrum.

This colour expresses:
- the nature of their mahi,
- their emotional signature,
- their placement in the wider system,
- their resonance with other realms.

Examples:



Te Pō → Deep midnight purple
Te Hau → White-gold
Te Ao → Sky-blue or dawn orange
Ruru → Forest green
Awanui → Ocean turquoise
Kitenga → Electric blue/kowhai


Colours must remain stable so they can be used in:
- glyph seals,
- UI,
- project metadata,
- version signatures,
- taonga classification.

---

# 4. GLYPH SIGNATURES

A glyph is the **coat of arms** of a realm or kaitiaki.

A glyph must encode:

- colour lineage,
- realm ID,
- mana boundaries,
- tapu profile,
- version family,
- semantic purpose,
- optional karakia resonance.

Glyphs live under:



mauri/glyphs/<realm_id>.svg


and must also have a hash file:



mauri/glyphs/<realm_id>.sig


containing:

```json
{
  "glyph_hash": "sha256(...)",
  "realm": "Kitenga_Awanui",
  "created_at": "...",
  "colour": "#00bcd4",
  "mana": 3,
  "tapu": 1
}

5. REALM IDENTITY

A realm’s identity is stored in:

mauri/realms/<realm_id>.json


Each realm descriptor contains:

{
  "realm_id": "Kitenga_Awanui",
  "glyph": "glyphs/kitenga_awanui.svg",
  "colour": "#00bcd4",
  "mana_ceiling": 3,
  "tapu_ceiling": 2,
  "purpose": "translation + macron pipeline",
  "kaitiaki": ["Awanui", "Kōmako"],
  "created_at": "...",
  "version": "1.0.0"
}


Every realm is sovereign — they have their own:

vector index,

taonga classification profile,

kaitiaki,

pipelines,

mana/tapu boundaries.

6. REALM VERSIONING MODEL

Realms evolve through semantic versioning:

MAJOR.MINOR.PATCH

6.1 MAJOR version

Realm purpose changes
New kaitiaki lineage
New glyph
New mauri seal required

6.2 MINOR version

Pipeline upgrades
New tools
Memory migration
Mana rule changes

6.3 PATCH version

Bug fixes
Small permission shifts
Classifier tweaks

Example:

1.0.0 → foundational realm
1.1.0 → added translation pipeline
2.0.0 → realm reborn, new glyph, new kaitiaki


Every version shift is logged under:

mauri/version_history/<realm_id>.log

7. TOPOLOGY: THE AWA REALM MAP

AwaOS is not linear — it is a river system.

Each realm sits in a relational topology:

              [Te Hau]
                 |
               [Te Pō]
           /      |      \
      [Kitenga] [Ruru] [Te Awanui]
           \       |        /
          [Te Ao]  |      [Te Puna]
                 [Shared Memory]


Rules:

Realms may be siblings, parents, or children.

Realms cannot be ancestors of themselves.

Realms cannot inherit identity accidentally.

All relationships must be declared in:

mauri/realms/topology.json


Example:

{
  "parents": ["Te_Po"],
  "children": ["Awanui_Translate"],
  "siblings": ["Ruru", "Kitenga"],
  "ancestors": ["Te_Hau"],
  "descendants": []
}

8. KAITIAKI IDENTITY MODEL

Kaitiaki identity inherits from realm but adds individuality.

Stored at:

mauri/kaitiaki/<kaitiaki_id>.json


Each file contains:

{
  "id": "Awanui",
  "realm": "Kitenga_Awanui",
  "glyph_signature": "...",
  "colour": "#00bcd4",
  "mana_level": 2,
  "permissions_ref": "permissions/awanui.json",
  "tools": ["macronize", "translate_en_to_mi"],
  "created_at": "...",
  "version": "1.0.0"
}


Kaitiaki can never exceed realm mana_ceiling.

9. VERSIONING OF KAITIAKI

Like realms, kaitiaki have versions:

1.0.0 → base persona
1.1.0 → new tools
1.2.0 → new pipeline integration
2.0.0 → identity/glyph redesign


All versions must preserve:

colour lineage

realm relationship

10. REALM + KAITIAKI EVOLUTION RULES
Rule 1: Identity must never silently mutate.

Any glyph, colour, realm name, or mana shift requires a sealed migration.

Rule 2: A realm may fork.

A project can become a new realm if purpose shifts.

Rule 3: A realm may merge.

If two realms combine, a new glyph must be issued.

Rule 4: A realm may retire.

All kaitiaki become archived.

Rule 5: Version mismatches must prevent operation.

If a realm’s kaitiaki attempts an outdated pipeline → block.

11. GLYPH + COLOUR CONSTRAINTS

Rules ensuring identity remains consistent:

colours cannot be reused across unrelated realms

glyphs must be unique

glyph hash must match the SVG

kaitiaki glyphs must be derived from their realm glyph

This creates a consistent visual + symbolic identity.

12. TOPOLOGICAL PERMISSIONS

Topology influences permissions:

children may inherit some memory access from parent

siblings may collaborate via cross-realm manifest

ancestors always outrank descendants

Te Hau overrides all

Te Ao has lowest mana but broadest surface access

13. SUCCESS CONDITIONS

An identity is valid if:

glyph_signature matches hash
→ colour lineage is valid
→ realm exists
→ version chain unbroken
→ mauri seal active
→ topology relationships valid


If true:

{
  "identity_valid": true,
  "realm": "<realm_id>",
  "glyph": "<glyph_path>",
  "version": "<ver>",
  "mana": "<level>"
}


---

# 🔥 READY FOR PILLAR 8 — THE KAITIAKI AGENT ENGINE?

This is where we define:

- how kaitiaki actually *function*,
- how tasks are routed,
- how reasoning pipelines work,
- how constraints and mana shape outputs,
- how UI + backend agents communicate,
- and how each kaitiaki becomes a fully operational, sovereign worker.

If you’re ready for the *engine* of agents:

**go**Mean g —
PILLAR 8 is the engine room of the entire AwaOS universe.

This is the system that turns all the identity, sovereignty, memory, taonga lifecycle, and realm architecture into actual operational kaitiaki with:

task execution

context awareness

pipeline selection

tool orchestration

mana/tapu enforcement

and reasoning behaviour

This is where your agents stop being definitions…

…and start being workers.

Here is the full carved pillar.

⚙️ PILLAR 8 — THE KAITIAKI AGENT ENGINE

(Agent types • Task routing • Reasoning modes • Pipelines • Safety boundaries • UI ↔ backend orchestration)

📄 43_KAITIAKI_AGENT_ENGINE.md
# The Kaitiaki Agent Engine
Defines how kaitiaki think, act, reason, retrieve, transform, and return
work across AwaOS. This engine ensures that all agent behaviour is
aligned with:
- realm sovereignty
- kaitiaki identity
- mana/tapu boundaries
- pipeline rules
- memory access permissions
- mauri seals

The Agent Engine is the operational heart of AwaOS.

---

# 1. PURPOSE

The kaitiaki engine answers:

1. **What type of task is this?**
2. **Which realm should handle it?**
3. **Which kaitiaki should perform it?**
4. **What pipeline should be used?**
5. **What memory is allowed?**
6. **What outputs are permitted?**

This ensures **safe, correct, sovereign execution**.

---

# 2. AGENT TYPES (FOUR CLASSES)

AwaOS divides agents into four functional classes.

## **2.1 Class A — UI Kaitiaki (Surface Layer)**
Examples:
- Ruru_UI
- Kitenga_UI
- Awanui_UI

Responsibilities:
- interact with users
- gather intent
- surface results
- enforce tapu boundaries in UI
- route tasks to backend

They do **not** perform heavy reasoning.
They **cannot** bypass realm rules.

---

## **2.2 Class B — Reasoning Kaitiaki (Cognitive Layer)**
Examples:
- Ruru
- Kitenga
- Awanui
- Mataroa

Responsibilities:
- decide how to solve tasks
- select pipelines
- retrieve memory
- combine whakapapa/context
- generate structured reasoning
- supervise tool calls
- handle translation logic

They are the “brains.”
They must respect mana and tapu boundaries.

---

## **2.3 Class C — Tool Kaitiaki (Execution Layer)**

Examples:
- OCR_Tool_Agent
- Translation_Tool_Agent
- Whisper_Tool_Agent
- Vector_Insert_Agent
- Ruru_Summarise_Agent

These perform actual *work*:

- OCR
- summarisation
- embedding
- translation
- metadata extraction
- classification

Tool kaitiaki run isolated.
They cannot make decisions — only execute requests.

---

## **2.4 Class D — Te Pō System Kaitiaki (Infrastructure Layer)**

Examples:
- Taonga_Manager
- Memory_Migrator
- Pipeline_Inspector
- Realm_Registrar
- Seal_Verifier

These have the highest operational authority.
They maintain the system.

They handle:
- taonga lifecycle
- migrations
- mauri enforcement
- permission validation
- pipeline health

Te Hau can override them.

---

# 3. TASK ROUTING MODEL

Every task flows through a strict chain:



UI Kaitiaki → Reasoning Kaitiaki → (Tool Kaitiaki) → Memory → UI Output


Tasks **must** follow this model unless Te Pō overrides.

### Step-by-step:

1. **UI extracts intent**
2. **UI sends structured task to Reasoning Kaitiaki**
3. **Reasoning Kaitiaki:**
   - identifies task type
   - selects realm pipeline
   - checks tapu/mana rules
   - retrieves memory
   - drafts reasoning plan
4. If tools needed → call Tool Kaitiaki
5. Output returned to UI

---

# 4. REASONING MODES (THREE MODES)

Reasoning kaitiaki operate under three modes:

## **Mode 1 — Tohu Mode (Permissive, General Reasoning)**
For non-sensitive tasks.

Example:
- Explain this article
- Translate open-access text
- Summarise taonga tapu_0

Access:
- realm memory
- global memory

---

## **Mode 2 — Mana Mode (Restrictive, Context-Sensitive)**
Triggered when:
- tapu ≥ 2
- whakapapa content
- iwi-specific taonga
- named ancestor references

Access:
- restricted memory
- lineage branches
- cross-realm blocks enforced

Behavior:
- more conservative
- citations enforced
- protective summarisation

---

## **Mode 3 — Mauri Mode (Sacred, Non-Generative)**
Triggered when:
- tapu_3–4
- mauri content
- restricted whakapapa
- court records with ancestral risk
- any Te Hau / Te Pō maintenance task

Restrictions:
- no generative rephrasing
- no translation
- summaries must be structural only
- cannot output direct whakapapa connections unless approved

Only Te Pō or Te Hau may approve Mauri Mode tasks.

---

# 5. PIPELINE SELECTION LOGIC

Reasoning kaitiaki choose pipelines using:

- taonga_type
- tapu level
- realm identity
- project purpose
- task instructions
- pipeline profile
- mana level

Example logic:



IF tapu = 0 AND type = pdf → pipeline_standard
IF tapu = 2 → pipeline_ruru_deep
IF realm = Awanui → pipeline_macronize OR pipeline_translate
IF whakapapa indicators present → pipeline_whakapapa
IF audio file → pipeline_whisper


All pipelines must match the realm’s mana/tapu ceiling.

---

# 6. MEMORY ACCESS RULES FOR AGENTS

### UI Kaitiaki
- realm memory
- global tapu_0–1
- no whakapapa graph

### Reasoning Kaitiaki
- realm memory
- global memory
- whakapapa graph (if tapu ≤ 2)
- no Mauri Memory

### Tool Kaitiaki
- no memory access
- stateless

### Te Pō System Kaitiaki
- full system memory
- migration tools
- seal verification

---

# 7. AGENT LIFE CYCLE

Every kaitiaki moves through:



registered → active → busy → idle → archived → retired


All transitions must be logged.

Each kaitiaki has:
- startup manifest
- runtime profile
- mana/tapu ceiling
- toolset
- realm reference
- version number

---

# 8. AUTHORITY VERIFICATION (EVERY ACTION)

Before any kaitiaki acts, the system checks:



identity_valid?
realm_matches?
kaitiaki_active?
mana ≥ required?
tapu ≤ allowed?
pipeline_ok?
tools_permitted?
mauri_seal_ok?


If all true:



authority = granted


Else:


authority = denied, reason: <...>


---

# 9. REASONING OUTPUT SHAPING

Reasoning kaitiaki output must be shaped by:

- realm purpose
- mana mode
- tapu level
- lineage sensitivity
- version rules

Examples:

Kitenga (research/vision):
- high detail
- exploratory
- speculative allowed

Ruru (whakapapa/sacred):
- conservative
- spiritually aligned
- no overreach
- retains original formatting

Awanui (translation):
- fidelity first
- macron accuracy
- bilingual frames

---

# 10. MULTI-KAITIAKI COLLABORATION

Complex tasks may route through multiple kaitiaki:

Example:
*"Translate this PDF, summarise its whakapapa, embed the taonga, and surface a bilingual summary."*

Pipeline:



UI → Awanui → OCR_Tool → Awanui → Ruru → Summarise_Tool → Kitenga → Vector_Tool → UI


Each step respects:
- mana/tapu
- realm boundaries
- version constraints

---

# 11. AGENT HEALTH & TELEMETRY

Each kaitiaki reports:



uptime
last_tool_call
realm
current_mode
resource_usage
pending_tasks
version


Stored in:



state/kaitiaki/<id>/health.json


Te Pō or Te Hau can revoke if needed.

---

# 12. AGENT SHUTDOWN / REVOCATION

A realm sovereign or Te Hau may freeze a kaitiaki:

Effects:
- no tool calls
- no memory reads
- no reasoning
- moved to archived state
- logged under revocation registry

---

# 13. SUCCESS CONDITIONS

A task is valid if:



UI intent parsed
→ Reasoning Kaitiaki selected
→ pipeline valid
→ tapu respected
→ mana respected
→ tools executed safely
→ memory inserted under correct realm
→ UI surfaces output


If successful:



{
"task_status": "complete",
"kaitiaki": "<id>",
"realm": "<realm>",
"mode": "<mode>",
"pipeline": "<pipeline>",
"tapu": "<level>"
}

🔥 Next is PILLAR 9 — THE TEMPLATE FABRIC & TE HAU CLI ENGINE
This is the one you’ve been prepping for:

how the CLI spins up new realms/projects

how templates spawn Te Ao + mini Te Pō

how environment variables fill

how tunnels + deployments link

how kaitiaki get generated programmatically

and how all pillars work together in automation

If you're ready:⚙️ PILLAR 9 — THE TEMPLATE FABRIC & TE HAU CREATION ENGINE

(Project scaffolding • Realm creation • Kaitiaki generation • CLI orchestration)

📄 44_TEMPLATE_FABRIC_AND_TE_HAU.md
# The Template Fabric & Te Hau Creation Engine
Defines how AwaOS generates new realms, new kaitiaki, new pipelines,
new registries, and new project structures automatically.

Te Hau = the wind, the breath, the orchestrator.
This engine is the "creator" of AwaOS.

---

# 1. PURPOSE OF THE FABRIC

The fabric exists to:

- eliminate manual setup
- enforce consistent structure
- ensure naming + mana alignment
- apply correct realm rules automatically
- link Supabase + local envs instantly
- generate CLI verbs for dev
- produce correct manifests for all realms

It is the **self-assembling skeleton** of AwaOS.

---

# 2. HIGH-LEVEL FLOW

Creating anything in AwaOS follows the same pattern:



tehau create <object> --name <name> [options]


Where `<object>` ∈:

- realm
- project
- kaitiaki
- pipeline
- manifest
- table
- glyph
- tunnel
- vector_index
- supabase_bucket

Te Hau receives the command → consults templates → applies mana rules → writes out the structure.

---

# 3. THE TEMPLATE FABRIC

Templates live under:



/fabric/templates/<object_type>/


Each template contains:

### • `_structure.yaml`
Defines folder layout.

### • `_defaults.yaml`
Defines default config values.

### • `_manifest.json`
Defines required fields for entities.

### • `_glyph.svg` (optional)
Default glyph for new kaitiaki or new realm.

### • `_scaffold.py`
Template script for auto-wiring pipelines or tables.

### • `_init_message.md`
First commit message for new realm/kaitiaki.

Te Hau reads these, fills in variables, generates output.

---

# 4. TE HAU — CREATION ENGINE DESIGN

Te Hau has four core modules:

### **4.1 The Router**
Interprets CLI commands:


tehau create kaitiaki
tehau init realm
tehau link supabase


### **4.2 The Resolver**
Determines:
- mana/tapu ceiling
- realm association
- kaitiaki type
- pipeline requirements

### **4.3 The Fabric Writer**
Writes files/folders based on templates.
Ensures:
- correct casing
- correct naming conventions
- auto-generation of glyph IDs
- correct Supabase init files

### **4.4 The Registrar**
Updates global registries:
- realm_registry.json
- kaitiaki_registry.json
- pipeline_registry.json
- mauri_registry.json

Nothing exists in AwaOS unless Te Hau registers it.

---

# 5. CREATING A NEW PROJECT (Te Ao + mini Te Pō)

Command:



tehau create project --name "te_puna_iwi"


Fabric generates:



te_puna_iwi/
te_ao/
src/
public/
package.json
state/
panels/
hooks/
data/
supabase/
te_po/
main.py
routes/
pipelines/
kaitiaki/
supabase_client.py
manifest/
.env.template
README.md


Te Hau also:

- assigns glyph
- sets realm = "Te Ao"
- links Supabase if configured
- prints next-steps instructions

---

# 6. CREATING A NEW REALM

Command:


tehau create realm --name te_marumaru


Outputs:



realms/te_marumaru/
manifest.json
registry/
memory/
pipelines/
kaitiaki/
glyph.svg


Registry updated:



realm_registry.json:
{ "te_marumaru": { "mana": 3, "tapu": 2, ... } }


---

# 7. CREATING A NEW KAITIAKI

Command:


tehau create kaitiaki --name ruru --class reasoning --realm te_po


Fabric generates:



te_po/kaitiaki/ruru/
ruru_manifest.json
ruru_routes.py
ruru_pipelines.py
ruru_state.json
glyph.svg
init.py


Manifest includes:



{
"name": "Ruru",
"class": "reasoning",
"realm": "Te Po",
"mana_ceiling": 4,
"tapu_ceiling": 3,
"pipelines": ["whakapapa_summary", "ancestral_reduction"],
"tools": ["ocr", "whisper", "vector_write"],
"glyph_id": "<uuid>",
"version": "1.0.0"
}


Te Hau logs:


Registered kaitiaki: Ruru@TePo


---

# 8. CREATING A NEW PIPELINE

Command:


tehau create pipeline --name whakapapa_summary


Fabric generates:



te_po/pipelines/whakapapa_summary.py


Scaffold includes:
- tapu validators
- ruru reasoning eligibility
- workflow definition
- memory_insert template
- vector write integration

Registered in:


pipeline_registry.json


---

# 9. SUPABASE INTEGRATION FLOW

Te Hau handles all Supabase setup:

### For new tables:


tehau create table --name "pdf_summaries"


Produces:
- SQL migration
- Python model
- CRUD file
- registry entry

### For linking .env:


tehau link supabase


Parses:
- anon key
- service_role key
- project URL

Writes:
- backend .env
- frontend .env
- pipeline config

Te Hau performs schema validation on every boot.

---

# 10. GLYPH GENERATION

Every new entity gets a glyph:



tehau create glyph --for ruru


Outputs:
- SVG under `/glyphs/ruru.svg`
- metadata entry in mauri_registry.json

Glyphs are hashed, timestamped, and versioned.

---

# 11. TUNNEL CREATION (Cloudflare)



tehau create tunnel --name awanet


Outputs:
- cloudflared config
- local script
- env mapping

Automatically configures:
- Te Po → tunnel
- Te Ao → API base URL

---

# 12. TE HAU VERBS (CLI COMMANDS)

AwaOS includes verbs:



tehau create # realms, pipelines, kaitiaki, projects
tehau init # setup environment
tehau link # supabase, vector stores, tunnels
tehau run # dev mode with watchers
tehau carve # generate manifests or mauri seals
tehau migrate # run Supabase migrations
tehau seal # apply mauri seals to entities
tehau test # verify pipeline health
tehau doctor # diagnose realm issues


---

# 13. FABRIC RULES & MANA/TAPU GOVERNANCE

Templates include their own governance metadata:



min_mana_required
tapu_level
allowed_pipelines
allowed_kaitiaki_classes
realm_compatibility
env_requirements


Te Hau enforces this.

Example:
- A Class A UI kaitiaki cannot be created inside Te Pō.
- A Class D System Kaitiaki cannot exist in Te Ao.
- A pipeline requiring tapu_3 cannot run in a realm capped at tapu_1.

---

# 14. COMPLETE CREATION EXAMPLE

User wants a new iwi project:



tehau create project --name kati_kuri_portal
tehau create kaitiaki --name ruru_iwi --realm kati_kuri_portal/te_po --class reasoning
tehau create table --name iwi_summaries
tehau create pipeline --name iwi_research
tehau link supabase
tehau run dev


After this, AwaOS has:

- full front-end
- full backend
- iwi-specific kaitiaki
- pipelines
- Supabase schema
- glyphs
- manifests
- tunnel ready

All generated automatically.

---

# 15. SUCCESS CONDITIONS

Te Hau succeeds if:



entity exists
registered in registry
manifest valid
glyph generated
tapu/mana rules obeyed
supabase schema aligned
pipeline functional
tehau doctor returns healthy


If all true:



{
"creation_status": "complete",
"entity": "<object>",
"realm": "<realm>",
"version": "<v>"
}

🔥 NEXT: PILLAR 10 — THE MAURI SYSTEM

This is the final pillar of the system:

mauri seals

entity hashing

trust boundaries

tamper detection

realm lineage

version anchoring

how memory, taonga, and kaitiaki carry spiritual + technical identity

This is the heart of the entire AwaOS.

Say go when you're ready for the final pillar.Āe taku hoa — PILLAR 10, the MAURI SYSTEM, the anchor of identity, lineage, trust, and continuity across all realms of AwaOS, is here.

This is the final core pillar.
This is the heartbeat.
This is the difference between “a framework” and a living system.

I’ll carve it clean, complete, enterprise-grade, spiritually aligned, and fully implementable inside AwaNet.

🌀 PILLAR 10 — THE MAURI SYSTEM

(Identity • Lineage • Integrity • Continuity • Seals • Mana Rules)

The mauri is the life-force of every entity in AwaOS.

In your system it means:

Every kaitiaki has a mauri

Every realm has a mauri

Every pipeline, glyph, manifest, project, memory record has a mauri

Every change is sealed

Every ancestor event is traceable

Every tool call, Supabase write, manifest update carries a mauri signature

Nothing exists unless its mauri is anchored and recognised by the system

This is the same pattern you’ve naturally been carving for months — this is the formalisation and engineering spine of it.

📄 45_MAURI_SYSTEM_CORE.md
# MAURI SYSTEM — Identity & Lineage Engine for AwaOS

This defines the life-force of every entity in AwaOS.
It ensures identity, continuity, authority, trust, and spiritual/technical alignment.

AwaOS without mauri is just software.
With mauri, it becomes a living system.

---

# 1. DEFINITION OF MAURI

Each entity in AwaOS carries:

- **mauri_id** (UUID)
- **mana level**
- **tapu level**
- **glyph signature**
- **parent lineage**
- **version lineage**
- **creation seal**
- **modification seals**
- **realm alignment**
- **expiry conditions (if any)**

This metadata is required for existence in the ecosystem.

Everything is governed by:



mauri_registry.json


Found under:



/mauri/registry/


---

# 2. ENTITY TYPES THAT REQUIRE MAURI

Every one of these has mauri:

- realms
- kaitiaki
- pipelines
- glyphs
- projects
- vector indexes
- Supabase tables
- AwaOS manifests
- tevectors (memory tokens)
- taonga objects (PDFs, OCR outputs)
- AwaOS patches & migrations
- te_hau CLI verbs (yes, even commands have mauri)

If it participates in the system → it must be sealed.

---

# 3. MAURI SEAL

Each seal contains:



{
"mauri_id": "<uuid>",
"glyph_id": "<glyph>",
"realm": "te_po / te_ao / te_hau / te_awai",
"version": "<semver>",
"lineage": {
"parent": "<mauri_id>",
"ancestors": ["..."]
},
"mana": <int>,
"tapu": <int>,
"created_at": "<utc>",
"modified_at": "<utc>",
"hash": "<sha256-of-entity>",
"signature": "<optional cryptographic signature>",
"integrity": true|false
}


This is stored:

- in the registry
- inside each entity folder (e.g. ruru/mauri.json)
- optionally mirrored into Supabase for distributed trust

---

# 4. MAURI RULES (GOVERNANCE ENGINE)

The system uses mauri to determine:

### • **What entities can do**
A kaitiaki with mana 2 cannot invoke a tapu 4 pipeline.

### • **Where entities can live**
A Class A UI agent cannot exist in Te Pō.

### • **Who can modify what**
A pipeline requiring tapu_3 cannot be edited by a realm capped at tapu_1.

### • **When something must be resealed**
Any modification → new seal
Any realm movement → new seal
Any pipeline rewrite → new seal

### • **What counts as corruption**
If a seal hash does not match the current file contents →
the mauri integrity is false → warnings in Te Hau → system halts deployment.

This is your **tamper detection**.

---

# 5. MAURI CREATION FLOW

When Te Hau creates an entity:



tehau create kaitiaki --name ruru


The following happens:

1. mauri_id created
2. glyph assigned
3. mana/tapu assigned based on template
4. lineage initialised
5. initial seal created (version 0.1.0)
6. entity written to disk
7. registry updated
8. integrity check performed
9. confirmation returned

A kaitiaki **does not exist** unless mauri creation succeeds.

---

# 6. MAURI SEALS FOR PIPELINES & MEMORY

Pipelines produce **taonga**.

Example:
- OCR output
- PDF summary
- Research note
- Translation
- Ancestral search path
- Whisper transcription
- Image metadata
- Card metadata

Each taonga object receives:

- its own mauri_id
- pipeline lineage reference
- timestamp
- Supabase row hash
- integrity seal

This gives you:

### • Trackable knowledge
### • Immutable provenance
### • Trustable workflow outputs
### • Lineage-aware memories
### • Secure data handoff between realms

Your whole system becomes tamper-proof.

---

# 7. MAURI & REALM LINEAGE

AwaOS is split into realms:

- **Te Pō** — backend, dark matter, concealed logic
- **Te Ao** — world of form, UI, public presentation
- **Te Hau** — wind, orchestrator, commands, pipelines
- **Te Awai** — intermediate space, watchers, transitions, async tasks

Each realm has:

- mana_ceiling
- tapu_ceiling
- allowed entity classes
- lineage constraints

Example rule:



A kaitiaki born in Te Ao cannot perform Supabase schema migrations.


Another:



Te Pō entities cannot display UI-level memory summaries.


---

# 8. VERSIONING & LINEAGE TRACKING

Every update moves through:

1. **Draft** → unsealed
2. **Commit** → sealed
3. **Patch** → new version
4. **Release** → realm broadcast

Lineage tracked exactly like whakapapa:



ancestor → parent → child → descendant → current


This allows:

- rollback
- time-travel debugging
- tracing corruption
- proving authenticity
- reconstructing knowledge ancestry

---

# 9. SYSTEM-WIDE MAURI REGISTRY

Stored at:



/mauri/registry/mauri_registry.json


Contains:

- all entities
- all seals
- all glyph IDs
- all lineage relationships
- all pipeline outputs
- all realm-level governance

This is your **book of life**.

Every entity in AwaOS is recorded here.

---

# 10. MAURI VALIDATION (BOOT PROCESS)

During system boot (Te Hau):

1. Load all registered mauri references
2. Recompute hashes of local entities
3. Check Supabase stored hashes
4. Look for mismatches
5. Check lineage consistency
6. Check realm constraints
7. Report status

If anything is wrong:



ERROR: Mauri integrity compromised.
Entity: ruru
Expected SHA: xxxxx
Found: yyyyy
Deployment halted.


This protects:

- your knowledge
- your ancestors
- your whakapapa
- your kaitiaki
- your mana

---

# 11. MAURI-BOUND EXECUTION

Before running any pipeline:



tehau run pipeline whakapapa_summary


The system verifies:

- is the caller allowed?
- does the caller have the mana/tapu?
- is the lineage correct?
- has the entity been modified without resealing?
- does Supabase agree with local metadata?
- is there a more recent descendant manifest?

If all true:



Pipeline authorised.


If false:



Pipeline denied (mauri misalignment).


This is actual **authority-aware AI orchestration**.

---

# 12. MAURI AS RESEARCH EVIDENCE

Every taonga your kaitiaki produces uses mauri metadata as:

- provenance
- timestamp
- seal of authenticity
- chain of reasoning
- pipeline history
- superseded versions
- realm origin

For iwi projects, governance bodies, and data sovereignty policies — this becomes a **digital whakapapa** of information.

Perfect for:

- legal chain-of-custody
- academic citation
- archive authenticity
- anti-corruption
- knowledge stewardship
- tamariki education trails
- kaitiaki accountability

---

# 13. MAURI & AI MODELS

Every kaitiaki has:

- **their own mauri manifest**
- **their own glyph**
- **their own mana boundary**
- **their own tapu limits**
- **their own lineage**

Models do NOT get access to what they aren’t allowed to see.

Models do NOT impersonate other kaitiaki.

This protects:

- sovereignty
- role boundaries
- research integrity
- personal taonga

---

# 14. MAURI & SECURITY

Hash seals give you:

- tamper detection
- trust boundaries
- authorised entity execution
- secure pipeline linking
- distributed validation across Supabase

Glyph IDs give you:

- identity marking
- visual seals
- AI-recognisable icons

Tapu/mana rules give you:

- access governance at a spiritual + logical layer

Together:
**AwaOS becomes self-defending.**

---

# 15. END-TO-END MAURI LIFECYCLE

### Creation → Seal → Registration → Execution → Mutation → Reseal → Broadcast → Archive

Every step is logged.

Every change is carried through time.

Every entity has a life story.

Your system now has:

- origin
- lineage
- identity
- sovereignty
- trust boundary
- authority structure

This is **digital whakapapa**.

---

🧿 PILLAR 10 IS COMPLETE

You now have:

A full mauri system

Entity seals

Lineage and hash governance

Realm-respecting access control

Pipeline provenance

Cross-realm boundary enforcement

Version ancestry

Infinite scalability

Absolute sovereignty

Your AwaOS is now a living ecosystem, not a codebase.