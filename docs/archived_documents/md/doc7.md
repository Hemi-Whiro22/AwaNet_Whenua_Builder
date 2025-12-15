Aight, this is the one, bro — the brain of the whole developer experience.
Te Hau is your personal operating system, your realm generator, your GitOps conductor, your context switcher, and your kaitiaki summoner.

This doc needs to be tight, predictable, scalable, and future-proof, because everything you build in the next decade — every realm, every UI, every kaitiaki — will flow through Te Hau.

Here we go.

📄 25_TE_HAU_CLI_RUNTIME_ARCHITECTURE.md

(The AwaNet Developer Operating System — CLI + Runtime + Ritual Engine)

# Te Hau — CLI & Runtime Architecture
Te Hau is the command-line brain of AwaOS.
It is the orchestrator for:

- Realm creation
- Realm evolution
- Deployment automation
- Local dev runtime
- Pipeline simulation
- Context management
- GitOps coordination
- Kaitiaki tooling
- Environment sealing
- API key injection
- Project bootstrapping

Te Hau is *where the developer becomes the carver*.

This document defines the architecture, commands, runtime, modules, and integrations that make Te Hau a true OS.

---

# 1. DESIGN PRINCIPLES

### 1.1 **Single Source of Truth**
Te Hau reads one manifest:



core_mauri/project.yaml


From this it resolves:

- active realm
- kaitiaki
- pipeline permissions
- Supabase schemas
- OpenAI vector indexes
- UI Kit version
- environment layout

### 1.2 **Stateless Execution**
All commands must work when run anywhere:

- local Ubuntu
- WSL
- DevContainer
- GitHub CI
- Cloudflare Worker
- Render builder

No hidden implicit state.

### 1.3 **Template-Driven**
Everything is generated from:



project_template/


This avoids rewriting logic.

### 1.4 **Realm Isolation**
Every command must maintain realm sovereignty.

Te Hau NEVER merges realms unless told to.

### 1.5 **Tikanga-Driven Safety**
Pipelines running on taonga require:

- double confirmation
- sealed logs
- audit events

---

# 2. CLI DIRECTORY STRUCTURE



te_hau/
cli.py
commands/
new_realm.py
evolve.py
pipeline.py
logs.py
context.py
deploy.py
seal.py
debug.py
core/
config_loader.py
manifest_parser.py
template_engine.py
token_generator.py
seal_validator.py
git_manager.py
cloudflare_api.py
render_api.py
supabase_api.py
openai_api.py
runtime/
process_manager.py
pipeline_simulator.py
hot_reload.py


---

# 3. RUNTIME MODULES

### 3.1 Manifest Loader
Reads:

- `project_template/template.config.json`
- `config/realm.json`
- `mauri/realm_lock.json`
- Global project.yaml

Validates:

- naming conventions
- glyph colours
- bearer scopes
- dialect profiles
- vector index existence

### 3.2 Template Engine
Handles file replacement:



{{REALM_NAME}}
{{REALM_ID}}
{{REALM_GLYPH}}
{{BEARER_KEY}}
{{VECTOR_INDEX_ID}}
{{RENDER_SERVICE_NAME}}
{{CF_ROUTE}}


Patches:

- .env
- realm.json
- proxy.toml
- docs
- GitHub workflows
- mini_te_po files

### 3.3 Seal Validator
Guarantees realm integrity:



hash(realm_lock.json)
== seal_hash in realm_registry


Rejects any realm with mismatched seals.

### 3.4 Git Manager
Handles:



git init
git add .
git commit
git push
git branch
git tag
git rollback <tag>


Used for:

- realm creation
- evolution commits
- rollback rituals
- version pinning for UI Kit

### 3.5 Cloudflare Manager
APIs for:

- Pages project creation
- env var injection
- route setup
- domain binding
- cache invalidation

### 3.6 Render Manager
APIs for:

- microservice creation
- region selection
- env var sync
- deploy triggers
- service health check

### 3.7 Supabase Manager
Handles:

- migrations
- table existence
- row-level policies
- schema validation
- vector index creation

### 3.8 Pipeline Simulator
Allows:



tehau pipeline test ocr --local
tehau pipeline inspect <pipeline_id>
tehau pipeline dry-run <pipeline_name>


This means you can simulate OCR, summary, translation, and research flows without deployment.

---

# 4. PRIMARY COMMANDS

---

## 4.1 `tehau new <realm>`

Creates a new Te Ao project realm.

### Actions:

- Copy project_template
- Apply templating
- Generate bearer key
- Create vector index
- Register realm with Te Pō
- Create Git repo
- Push to Cloudflare
- Create Render mini_te_po
- Seal realm
- Log lineage entry

Outputs a full working project:



<realm_name>/
te_ao (frontend)
mini_te_po (proxy backend)
docs
config
mauri
scripts


---

## 4.2 `tehau evolve <realm> <stage>`

Stages:
- seed
- worker
- specialist
- guardian

Updates:

- realm.json
- bearer scopes
- dialect rules
- UI Kit version
- vector index settings
- pipeline permissions

Creates GitOps PR automatically.

---

## 4.3 `tehau deploy <realm>`

Triggers:

- Cloudflare Pages build
- Render deploy
- seal validation
- Supabase schema migration
- context reload
- lineage update

---

## 4.4 `tehau pipeline run <realm> <pipeline>`

Runs OCR, translate, summary etc directly from CLI.

Used for debugging, testing, and local dev.

---

## 4.5 `tehau seal <realm>`

Recomputes the mauri seal hash.

Used when:

- glyph changes
- dialect changes
- kaitiaki changes
- pipeline permissions change

Rejects mismatches.

---

## 4.6 `tehau logs <realm>`

Fetches:

- pipeline logs
- project events
- context global
- taonga logs

---

## 4.7 `tehau context switch <realm>`

Sets the active development context.

Automatically rewires:

- env vars
- devcontainer
- OpenAI vector index
- Supabase schema
- UI tunnel
- backend target

---

# 5. TE HAU LOCAL DEV RUNTIME

### Hot Reload Server
Handles:

- local UI preview
- mini_te_po local dev
- auto-tunnel setup
- live function reloads
- pipeline simulator

Supports:



tehau dev <realm>


Which opens:

- localhost:5173 (frontend)
- localhost:8001 (mini_te_po)
- wss://dev.awanet (tunnel)

---

# 6. API KEY HANDLING & SECRET SAFETY

Te Hau handles secrets with tikanga.

- No secrets ever committed
- All env updates go through CLI
- All secrets stored in system keyring or `.env.local` (ignored)
- Realms only receive their scoped bearer token
- Guardian keys never leave Te Pō

---

# 7. FUTURE MODULES (Predefined Hooks)

### 7.1 Realm Intelligence Layer
Automated recommendations:

- “Realm is ready to evolve”
- “Vector index outdated”
- “Glossary needs update”

### 7.2 Kaitiaki Personalities
CLI can summon kaitiaki to “speak” during build output.

Example:



tehau evolve maruao specialist


Maruao will respond with:

“Ka ara te ata — the dawn rises.
Research pathways opened.”

### 7.3 Project Generators
Full stacks:

- Translator SaaS template
- Researcher Portal
- Taonga Scanner
- Master Dashboard

All bootstrapped from Te Hau.

---

# 8. WHY TE HAU EXISTS

Because AwaOS cannot scale on manual steps.

Te Hau:

- Removes human error
- Enforces realm tikanga
- Guarantees reproducibility
- Handles all deployment
- Manages bearer keys safely
- Orchestrates migrations
- Integrates with all cloud surfaces
- Makes realm creation a *ritual*

This is the developer OS that lets you scale to:

- 50 products
- 100 realms
- 1000 taonga
- 1M+ users

without losing identity, tikanga, or flow.



Next — if you want — we go into:

26 — MAURI VALIDATION ENGINE

the system that validates seals, realm ancestry, glyph lineage, and AI safety before any pipeline runs.

Say go if you want that carved.
Aight brother — this is the beating heart of AwaOS, the thing that will guard every realm, every kaitiaki, every taonga, every pipeline.

This is the Mauri Engine — the validator, the seal guardian, the whakapapa enforcer, the system that determines whether a realm is allowed to exist, run, deploy, or touch taonga.

This is where the tikanga sits.

This is what ensures nothing corrupts the system, no misaligned template, no drift, no wrong glyph, no mismatched pipeline, no unsafe assistant operation.

This is the doc that all other systems depend on.

📄 26_MAURI_VALIDATION_ENGINE.md
(Seal System • Lineage Registry • Realm Integrity Enforcer)
# Mauri Validation Engine
The Mauri Engine validates the integrity, whakapapa, glyph lineage, and operational safety of every realm and kaitiaki in AwaOS.

It is the first system invoked at:
- realm startup
- deployment
- pipeline invocation
- context switching
- evolution
- environment sealing
- taonga operations

If the Mauri Engine fails, the realm cannot proceed.

---

# 1. PURPOSE

The Mauri Engine ensures:

1. **Identity Integrity**
   Every realm knows who it is, where it belongs, and what lines it descends from.

2. **Glyph Consistency**
   Colours, runes, shapes, and the seal hash must match what is stored in the registry.

3. **Operational Safety**
   Pipelines cannot run unless:
   - realm is sealed
   - keys match registry scopes
   - dialect and pipeline configs align

4. **Drift Prevention**
   Protects against:
   - template drift
   - naming drift
   - bearers drifting from scopes
   - mismatched env names
   - corrupted migrations

5. **Kaitiaki Sovereignty**
   Each kaitiaki operates ONLY within its assigned realm and cannot interfere with others.

6. **Taonga Protection**
   Any pipeline touching taonga requires:
   - higher-seal
   - audit trail
   - lineage stamp

---

# 2. FILES & REGISTERS

The Mauri Engine reads from:



core_mauri/project.yaml
core_mauri/realm_registry.json
mauri/realm_lock.json
mauri/glyph.json
mauri/dialect.json
mauri/pipeline_scopes.json
mauri/seal_hash.txt


The system NEVER writes to the registry directly — only Te Hau can.

---

# 3. VALIDATION SEQUENCE

The validation flow runs in the following order:

## 3.1 Realm Identity Check
Validates:

- realm_name
- realm_id (ULID)
- version
- project lineage

Fails if mismatch with registry.

---

## 3.2 Glyph Integrity Check

Checks:

- primary colour
- accent colour
- rune ID
- SVG hash
- glyph version

Rejects any UI or kaitiaki using the wrong glyph.

---

## 3.3 Seal Verification

The most important part.

Flow:



hash(realm_lock.json)
== seal_hash in realm_registry.json


If mismatch →
❌ **BLOCK ALL OPERATIONS**

Explanation:
The realm has diverged from its sealed state.
Possible drift, corruption, or unauthorised change.

This protects the entire Awa.

---

## 3.4 Environment Match

Validates:

- SUPABASE_URL
- SUPABASE_SERVICE_KEY
- OPENAI_API_KEY
- BEARER_KAITIAKI
- REALM_VECTOR_ID
- RENDER_SERVICE_ID
- CLOUDFLARE_PROJECT

Rejects if any variable is missing, malformed, or unregistered.

---

## 3.5 Pipeline Scope Check

Each kaitiaki has a scope:



read
write
infer
translate
summarise
vector
taonga
guardian


Each pipeline declares required scope.

If kaitiaki scope < pipeline requirement →
❌ block pipeline
✔ suggest evolution

This prevents UI kaitiaki from running guardian-level taonga operations.

---

## 3.6 Dialect & Translator Safety

Each realm defines:

- default dialect
- orthographic rules
- macron policy
- whakapapa reference tables
- prohibited word mappings

Validation ensures:

- translator cannot output forbidden lexical forms
- pipeline respects dialect matches
- taonga requiring iwi-specific vocab loads the correct profile

---

## 3.7 Migration Safety Check

Runs before deployment:

- check for missing migrations
- check for corrupted SQL
- check for destructive changes
- check for vector schema mismatch

If unsafe:
❌ block deploy

---

# 4. HASHING MODEL

The Mauri Engine uses a deterministic hashing chain:



seal_hash = hash256(
realm_lock.json +
glyph.json +
pipeline_scopes.json +
dialect.json +
registry_version +
realm_version
)


This means ANY change to:

- colours
- dialect
- pipelines
- permissions

forces a reseal.

---

# 5. RITUAL: RESEALING A REALM

A realm should be resealed only when:

- glyph changes
- realm evolves
- dialect expands
- pipeline updated
- bearer scope increased
- backend upgraded
- security tightened

The resealing process:

1. Developer runs:


tehau seal <realm>


2. Te Hau computes new seal hash.

3. Registry updates.

4. Old seal archived in lineage.

No realm runs without a seal.

---

# 6. WHAKAPAPA VALIDATION

Each realm has a whakapapa tree:



AwaNet
├── Te Hau (root kaitiaki)
├── Te Pō (backend engine)
├── Te Ao (public UI realm)
└── Realm_X
├── Kaitiaki_1
├── Kaitiaki_2
└── pipelines...


Validation ensures:

- no circular ancestry
- no invalid adoption
- Realm_X inherits only allowed attributes
- Kaitiaki only inherits from its realm’s lineage

---

# 7. TAONGA PROTECTION & AUDIT TRAIL

Operations involving taonga require:

- `guardian` scope
- sealed realm
- active audit log

Audit includes:

- timestamp
- kaitiaki ID
- pipeline used
- source file ID
- vector output hash
- translation/summary snippets
- Supabase record ID
- glyph stamp

Stored in:



supabase.table: taonga_audit


---

# 8. ERROR MODES

## ❌ MAURI_SEAL_MISMATCH
Realm cannot operate.

## ❌ REALM_DIVERGENCE
Registry and local realm disagree on version or ancestry.

## ❌ PIPELINE_SCOPE_UNMET
Kaitiaki attempted to use a pipeline above its authority.

## ❌ DIALECT_CONFLICT
Translator attempted output not allowed.

## ❌ UNSAFE_MIGRATION
Preventing accidental data loss.

## ❌ INVALID_ENV_STATE
Missing or incorrect variables.

Each error suggests:

- resolution steps
- reseal options
- or realm rebuild

---

# 9. SUCCESS CONDITION

A realm is considered **alive** when:

- Seal validated
- Glyph verified
- Env aligned
- Registry matched
- Pipeline scopes safe
- Dialect loaded
- Migration validated

Then the Mauri Engine returns:



{
"alive": true,
"realm": "<realm_name>",
"glyph": "<glyph_id>",
"pipeline_ready": true,
"taonga_guard": true
}


This is what Te Hau uses to decide if a deployment or pipeline is allowed.

---

# 10. WHY THIS MATTERS

This is the system that stops:
- misalignment
- corruption
- drift
- accidental destructive operations
- unauthorised kaitiaki access
- unsafe translations
- breaking taonga integrity
- backend confusion
- realm collapse

It is the cultural and technical firewall of the Awa.

Without the Mauri Engine, AwaOS cannot grow safely.

With it, AwaOS becomes unbreakable.
🌑 AWAOS — THE FIVE PILLARS OF MAURI INFRASTRUCTURE
Pillar 1 — Mauri Validation Engine (done)

Seal system, drift detection, glyph verification, scope enforcement.

Pillar 2 — Realm Registry & Lineage System (next)

Defines how realms are born, evolve, connect, inherit, or retire.
This is the whakapapa map of the entire AwaOS.

Pillar 3 — Glyph Protocol & Visual Identity Engine

How glyphs are assigned, versioned, hashed, coloured, used, and retired.
Includes Koru lineage rules and per-realm flavicons.

Pillar 4 — Kaitiaki Sovereignty & Permission Model

Defines the authority levels, contexts, scopes, and containment rules for every agent.
Prevents cross-realm bleed and keeps each Kaitiaki acting only within its rightful space.

Pillar 5 — Pipeline Architecture & Safety Kernel

OCR, Translator, Vector Embedder, Taonga Summaries, AI pipelines —
the safety, runtime, and transformation rules.
This one is the operational spine.

Your request: “go next”
So we continue with Pillar 2.

This is the Realm Registry & Lineage System.
The map of the Awa.
The whakapapa of every Kaitiaki and every project you will ever make.

📄 27_REALM_REGISTRY_AND_LINEAGE_SYSTEM.md
(Whakapapa Map • Realm Lifecycle • Ancestry Enforcement)
# Realm Registry & Lineage System
The Realm Registry stores the whakapapa structure for AwaOS.
Every realm, every kaitiaki, every pipeline inherits identity and authority from this system.

It explains:
- where realms come from
- who their parents are
- what attributes they inherit
- what they are allowed to become
- who they are allowed to command
- when they can evolve
- when they must retire

This is the whakapapa layer — the map of the awa.

---

# 1. PURPOSE

The Realm Registry ensures:

1. **No realm exists without whakapapa.**
2. **Every realm has a unique purpose.**
3. **Attributes are inherited correctly.**
4. **No realm becomes something it shouldn’t.**
5. **Kaitiaki cannot exceed the authority of their lineage.**
6. **Te Hau always sits at the root.**
7. **Te Pō always sits below Te Hau but outside Te Ao.**
8. **Te Ao realms cannot mutate backend attributes.**
9. **Custom realms are always children, never siblings of Te Hau.**

---

# 2. FILES & REGISTERS

The lineage system loads from:



core_mauri/realm_registry.json
core_mauri/project.yaml
mauri/realm_lock.json
mauri/lineage_map.json


This defines:
- realms
- ancestry
- version
- descendants
- allowed evolutions
- allowed scopes
- glyph assignments
- pipeline permissions

---

# 3. REALM STRUCTURE

Every realm must define:



{
"realm_name": "Te Ao",
"realm_id": "ulid",
"parent": "Te Hau",
"generation": 2,
"glyph": "koru-blue",
"dialect": "mi-NZ",
"default_vector_id": "...",
"allowed_scopes": ["read", "infer"],
"allowed_pipelines": ["ocr-lite", "summary-lite"],
"status": "active"
}


This keeps the realm contained, safe, and aligned.

---

# 4. ROOT REALMS

AwaOS has three primordial realms:

## **4.1 Te Hau (Root)**
- Identity engine
- Glyph authority
- Realm registry
- Sealing and resealing
- CLI control
- Dev containers and templates

Everything flows from Te Hau.

---

## **4.2 Te Pō (Backend Engine)**
- FastAPI pipelines
- Summaries
- Translations
- OCR tooling
- Vector embedding
- Supabase operations

It is the unseen machinery of the awa.

---

## **4.3 Te Ao (Public UI Realm)**
- React/Vite interfaces
- Extensions
- Render deployments
- Cloudflare tunnels
- User-facing kaitiaki

Te Ao can never mutate Te Pō or Te Hau.
It inherits only what is safe.

---

# 5. CUSTOM REALMS

A custom realm (e.g. `Kitenga_Awanui`, `Ruru_Research`, `TePuna_IwiPortal`) must declare:

- parent = Te Hau
- glyph = new colour
- pipeline scopes = limited
- dialect rules
- vector id
- kaitiaki list

Example:



{
"realm_name": "Kitenga_Awanui",
"parent": "Te Hau",
"allowed_scopes": ["read", "infer", "translate"],
"glyph": "koru-green",
"descendants": ["Awanui_Kaitiaki"],
"status": "active"
}


---

# 6. REALM LIFECYCLE

Realms transition through:



draft → active → sealed → evolving → resealed → archived


Definitions:

### **draft**
Created but unsealed, not allowed to run.

### **active**
Running, validated, pipelines allowed.

### **sealed**
Glyph locked, env locked, pipeline config locked.

### **evolving**
Realm changing scope, glyph, or kaitiaki.

### **resealed**
Updated and locked again.

### **archived**
Retired realm, artifacts preserved, no execution allowed.

---

# 7. KAITIAKI LINEAGE

Each kaitiaki is born inside a realm:



realm > kaitiaki > pipelines


A kaitiaki defines:

- name
- purpose
- allowed tools
- allowed scopes
- dialect rules
- glyph (inherits realm glyph unless overridden)
- vector id
- Supabase logs

Example:



{
"kaitiaki_name": "Awanui_Kaitiaki",
"realm": "Kitenga_Awanui",
"scopes": ["read", "infer"],
"pipelines": ["ocr-lite", "summary-lite"]
}


A UI kaitiaki must NEVER have taonga scope unless explicitly granted.

---

# 8. ANCESTRY RULES

These rules keep AwaOS safe:

### 8.1. No realm can be parentless except Te Hau.
### 8.2. No realm can inherit from Te Ao.
### 8.3. Te Pō cannot inherit from Te Ao.
### 8.4. Realms cannot be siblings of Te Hau.
### 8.5. Realm names must be globally unique.
### 8.6. Realm glyphs must be unique unless explicitly shared.
### 8.7. Scope inheritance must not exceed the parent.
### 8.8. Pipelines must not exceed the parent realm's authority.
### 8.9. Realm cannot reseal itself; only Te Hau can reseal realms.

---

# 9. VERSIONING & DRIFT CONTROL

Each realm has:

- realm_version
- migration_version
- glyph_version
- schema_version
- dialect_version

The registry stores these and the Mauri Engine checks them.

Drift example:



local realm_version: 3
registry realm_version: 2


→ ❌ BLOCK ALL EXECUTION

This prevents mismatched migrations or outdated templates from running.

---

# 10. REALM EVOLUTION

A realm can evolve only if:

- proposed parent allows evolution
- glyph changes reviewed
- scope changes approved
- dialect extended safely
- pipelines validated
- migrations pre-checked

Evolution always triggers reseal.

---

# 11. REALM TRAVEL & CROSS-REALM ACCESS

Cross-realm actions must be declared:



realm: "Kitenga_Awanui"
needs: ["Te_Pō.summary", "Te_Pō.ocr"]


Te Hau validates the request.

Te Pō decides if it will serve the other realm.

No realm can modify another realm.

---

# 12. REGISTRY FAILURE MODES

## ❌ INVALID_PARENT
Realm has no valid ancestor.

## ❌ UNDECLARED_REALM
Realm exists on disk but not in registry.

## ❌ SCOPE_OVERFLOW
Realm tries to inherit more authority than allowed.

## ❌ GLYPH_COLLISION
Two realms using same glyph without explicit sharing.

## ❌ DRIFT_DETECTED
Realm version mismatched.

## ❌ LONE_KAITIAKI
Kaitiaki not assigned to a realm.

## ❌ INVALID_STATUS
Realm lifecycle state corrupted.

---

# 13. SUCCESS CONDITION

A realm is **valid** when:

- parent confirmed
- glyph resolved
- kaitiaki registered
- scopes aligned
- dialect confirmed
- versions matched
- seal verified
- migrations safe

Then registry returns:



{
"realm_valid": true,
"realm": "<name>",
"generation": <n>,
"descendants": [...],
"glyph": "<glyph_id>"
}


---

# 14. WHY THIS MATTERS

Without lineage:

- kaitiaki lose identity
- pipelines become unsafe
- glyphs become meaningless
- taonga access becomes dangerous
- drift happens silently
- environments corrupt each other

With lineage:

- everything has a whakapapa
- realms grow in harmony
- authority is clear
- drift is impossible
- templates are reproducible
- AwaOS stays sovereign and safe



If you want Pillar 3: Glyph Protocol & Visual Identity Engine,
just say:

goNext is the one that binds identity, vision, sovereignty, and UI-level recognition:

🌈 PILLAR 3 — THE GLYPH PROTOCOL & VISUAL IDENTITY ENGINE

(Koru lineage • Realm colours • SVG sealing • Icon rules • Identity hashes)

This is the system that makes your entire AwaOS visually coherent, instantly recognisable, and safely enforceable across UI, backend, and kaitiaki.

📄 29_GLYPH_PROTOCOL_AND_VISUAL_IDENTITY_ENGINE.md
# Glyph Protocol & Visual Identity Engine
This document defines the AwaOS glyph system: the koru forms, colour lineage,
SVG constraints, glyph versioning, and the identity rules that ensure every
realm, kaitiaki, and project can be visually and cryptographically verified.

This engine ensures:
- each realm has a unique koru identity
- colours carry whakapapa meaning
- glyphs can be sealed, hashed, and validated
- UI and backend share the same visual truth
- taonga cannot be impersonated or mislabelled

---

# 1. PURPOSE

The glyph system is both:
- **visual identity** (what humans see), and
- **cryptographic identity** (what the Mauri Engine seals and verifies).

A glyph is:
- a koru,
- a colour lineage,
- a realm signature,
- a versioned SVG file,
- a hashed identity token.

A glyph cannot change without resealing by Te Hau.

---

# 2. GLYPH COMPONENTS

Each glyph has five layers:

1. **koru_base**
   The shape category (single-loop, double-loop, spiral).

2. **koru_variant**
   Style variant (e.g., "te_awatea", "te_moana", "te_ahi").

3. **realm_colour**
   Unique hex colour representing the realm lineage.

4. **glyph_svg**
   The actual SVG stored in `mauri/glyphs/<glyph_id>.svg`.

5. **glyph_hash**
   SHA-256 hash of the SVG + metadata, stored in `glyph_registry.json`.

---

# 3. GLYPH REGISTRY

Stored in:



core_mauri/glyph_registry.json


Each entry:

```json
{
  "glyph_id": "koru-blue-tehau-v1",
  "realm": "Te Hau",
  "koru_base": "spiral",
  "koru_variant": "te_awatea",
  "hex": "#4aa8ff",
  "version": 1,
  "hash": "<sha256>",
  "status": "sealed"
}


Rules:

All glyphs must have unique glyph_id.

All glyphs must be sealed before realm activation.

Hash must match the stored SVG.

4. THE PRIMORDIAL GLYPHS

Three glyphs are eternal anchors:

4.1 Te Hau (The Source)

Base: spiral

Colour: blue

Meaning: origin, breath, flow

Status: immutable

4.2 Te Pō (The Engine)

Base: double-loop

Colour: charcoal / deep navy

Meaning: backend, unseen world, machinery of the awa

4.3 Te Ao (The Visible World)

Base: single-loop

Colour: light gradient or soft teal

Meaning: surface, UI, interaction

These three define all other glyphs via lineage rules.

5. CUSTOM REALM GLYPHS

A custom realm must define:

{
  "realm": "Kitenga_Awanui",
  "glyph_id": "koru-green-awanuiv1",
  "hex": "#24c86b",
  "koru_base": "spiral",
  "parent_glyph": "koru-blue-tehau-v1",
  "version": 1,
  "status": "active"
}


Rules:

Base must match parent realm.

Colour must be unique, unless explicitly inherited.

Version increments only on change to SVG or colour.

6. COLOUR LINEAGE RULES

Colours encode ancestry.

6.1 Realms must use a single dominant colour.
6.2 No two active realms may share a hex value.
6.3 Gradient use is restricted to Te Hau only.
6.4 Special glyph colours require Te Hau reseal approval.
6.5 Kaitiaki may use a lighter/darker tone of the parent realm colour.

Example:

Realm colour: #24c86b
Kaitiaki colour range:

lightened: #4ade80

darkened: #158f4a

7. SVG REQUIREMENTS

SVGs must satisfy:

no embedded scripts

no external resources

no filters that can be styled externally

minimal path count

deterministic ordering of attributes

canonical formatting

final file must hash identically across systems

Stored in:

mauri/glyphs/<glyph_id>.svg


SVG failures result in:

❌ hash mismatch

❌ unverifiable identity

❌ invalid seal

8. GLYPH VERSIONING AND MIGRATION

Each glyph has:

version

migration_version

last_modified

sealed_by

When a glyph is updated:

New SVG stored

New hash computed

Version incremented

Mauri Engine reseals

Realm status changes → evolving → resealed

9. GLYPH USAGE RULES

A glyph controls:

favicon

extension icon

realm marker in UI

backend identity logs

kaitiaki badges

taonga metadata watermark

Rules:

9.1 Realms must never display glyphs belonging to other realms.
9.2 Te Ao may not use Te Pō glyphs.
9.3 UI kaitiaki may not embed taonga glyphs.
9.4 Glyph changes must propagate through Render/CF deployments.
10. GLYPH-BASED AUTHENTICATION

When a request comes from a realm or kaitiaki:

identity = hash(realm_name + glyph_id + glyph_hash + realm_version)


Te Pō checks:

is glyph valid?

is realm status active?

does glyph hash match registry?

does version match registry?

If any mismatch:

→ ❌ identity spoofed
→ ❌ realm drifted
→ ❌ reject request

This prevents impersonation across realms.

11. GLYPH FAILURE MODES
Error	Meaning
GLYPH_HASH_MISMATCH	SVG changed unexpectedly
GLYPH_COLLISION	Colour or base conflict with another realm
INVALID_GLYPH_VERSION	Template drift
GLYPH_UNSEALED	Realm attempted to activate without sealing
REALM_GLYPH_NOT_FOUND	Missing glyph definition

All of these block activation.

12. SUCCESS CONDITION

A glyph is valid if:

unique

sealed

hashed

colour-unique

parent lineage valid

version correct

registered in glyph_registry.json

Then identity system returns:

{
  "glyph_valid": true,
  "glyph_id": "<id>",
  "hex": "<color>",
  "koru_base": "<spiral>",
  "version": <n>
}

13. WHY THIS MATTERS

Glyphs are:

identity

sovereignty

branding

cryptographic roots

cultural markers

safety boundaries

realm signatures

They tell the system:

who you are,

who you belong to,

what you may do,

where you may go,

what taonga you can touch.

Without glyphs, realms drift.
With glyphs, realms stand.


---

If you're ready for **Pillar 4 — Kaitiaki Sovereignty & Permission Model**, say:

**go**Aight my brother — now we step directly into the beating heart of AwaOS sovereignty.

Everything we built so far (Mauri Validation Engine, Realm Registry, Glyph Protocol) sets the stage for THIS pillar — the one that determines who can act, where, how, and under what authority.

This is the model that makes:

every realm safe

every kaitiaki distinct

every permission explicit

every action traceable

every boundary enforceable

This is PILLAR 4.

🛡️ PILLAR 4 — KAITIAKI SOVEREIGNTY & PERMISSION MODEL

(Roles • Authority chains • What each kaitiaki can touch • Realm-bound execution • Tapu/Mana enforcement)

Below is the carved document.

📄 39_KAITIAKI_SOVEREIGNTY_AND_PERMISSION_MODEL.md
# Kaitiaki Sovereignty & Permission Model
Defines how authority, roles, and operating boundaries work across AwaOS.
This system prevents unauthorized kaitiaki drift, cross-realm access,
identity spoofing, or taonga misclassification.

The model is rooted in:
- sovereignty per realm,
- delegated authority per kaitiaki,
- mana level enforcement,
- tapu boundaries,
- and strict permission maps.

This ensures no agent can exceed the authority of its realm or role.

---

# 1. PURPOSE

This permission engine answers four questions:

1. **Who may act?**
   (kaitiaki identity → glyph → realm → version)

2. **Where may they act?**
   (allowed realms, taonga classes, pipelines)

3. **How may they act?**
   (tools, memory access, embedding rights, OCR modes, translation tiers)

4. **Under what authority?**
   (mana/tapu levels, seals, delegated privileges)

Every action in AwaOS must satisfy all four.

---

# 2. PRINCIPLES OF SOVEREIGNTY

### 2.1 Realms are sovereign.
Each realm owns its:
- glyph,
- colour lineage,
- mauri boundary,
- logs,
- operational space.

No realm may overstep another without explicit delegation.

### 2.2 Kaitiaki derive authority from their realm.
Kaitiaki cannot outrank the realm that spawned them.

### 2.3 Permissions must be explicit.
No silent, assumed, or inherited permissions.

### 2.4 All actions are logged as identity + intention.
This protects taonga and maintains chain of trust.

---

# 3. THE SOVEREIGNTY HIERARCHY

AwaOS recognizes four authority strata:

## **3.1 Te Hau — Supreme Source Level**
- Can seal or unseal realms
- Can originate glyphs
- Can activate or deactivate kaitiaki
- Can change global mauri rules
- Has the ability to inject migrations

Only one entity sits at this level.

## **3.2 Te Pō — System Engine Level**
- Full control over pipelines, vector stores, OCR engines
- Manages taonga classification and storage
- Enforces permission boundaries
- Cannot alter Te Hau rules
- Cannot create new realms without Te Hau approval

This is your backend.

## **3.3 Realm Sovereigns — Project-Level Authority**
Each realm (e.g., `Kitenga_Awanui`, `Ruru`, `Te_Puna_AI`) has:

- its own glyph
- its own colour lineage
- its own kaitiaki
- its own mana boundaries
- controlled privilege within its domain

A realm sovereign cannot act outside its project.

## **3.4 Kaitiaki — Agents of a Realm**
Each kaitiaki:

- operates under a realm seal
- inherits only the permissions granted
- can be revoked instantly by realm sovereign
- cannot escape its realm boundary
- cannot override taonga tapu levels
- may carry additional tools

---

# 4. PERMISSION MAP STRUCTURE

Each kaitiaki has a permission map stored at:



mauri/permissions/<kaitiaki_id>.json


Example:

```json
{
  "kaitiaki": "Ruru",
  "realm": "Te_Po",
  "mana_level": 3,
  "permissions": {
    "ocr": true,
    "taonga_read": ["public", "restricted"],
    "taonga_write": ["public"],
    "embedding": true,
    "translation": ["level1", "level2"],
    "vector_insert": true,
    "vector_delete": false,
    "realm_switch": false,
    "tool_access": ["ocr_tool", "pdf_tool", "summarise_tool"]
  }
}

5. MANA LEVELS

Mana defines what a kaitiaki can influence.

0 – harmless helper
1 – basic tools
2 – memory access (read)
3 – write access to project taonga
4 – pipeline ownership
5 – realm sovereign
6 – Te Pō advisory
7 – Te Hau seal privilege


Rules:

No kaitiaki may have mana higher than its realm.

No realm may exceed mana granted by Te Hau.

Mana inflation triggers security warnings.

6. TAPU LEVELS (Content Protection)

Tapu defines what content may be touched.

tapu_0 – open, public
tapu_1 – project-private
tapu_2 – restricted taonga
tapu_3 – whakapapa-protected
tapu_4 – sacred / mauri-core


Rules:

Only Te Hau can modify tapu level 4.

Only Te Pō can view but not alter level 3.

Realms cannot read taonga above their tapu access.

No kaitiaki may embed or summarize tapu > permitted level.

7. REALM BOUNDARIES

Every kaitiaki must operate inside:

<realm>/src/*
<realm>/mauri/*
<realm>/taonga/*


It cannot:

write to another realm

embed cross-realm metadata

read Te Pō’s backend logs

modify global mauri stones

impersonate another realm glyph

Boundary violations require:

403 response

tamper report

optional automatic isolation

8. CROSS-REALM ACCESS

A realm may request cross-realm access via:

cross_realm_manifest.json


The manifest must include:

requesting realm

target realm

reason

specific permissions

expiry timestamp

glyph signature

All cross-realm approvals require Te Hau sign-off.

9. TOOL PERMISSIONS

Tools are not global.
Tools belong to realms.

Each tool has:

required mana level

allowed realms

max tapu readable

resource cost

Examples:

OCR Tool
mana >= 1
tapu_read <= 2
allowed_realms: ["Te_Po", "Kitenga_Awanui"]

Vector Insert
mana >= 3
allowed_realms: ["Te_Po"]

Migration Tool
mana >= 6
allowed_realms: ["Te_Hau"]

10. SOVEREIGN IDENTITY CHAIN

Every action embeds:

actor_kaitiaki
→ realm
→ glyph signature
→ mana level
→ tapu context
→ tool id
→ timestamp


This creates an unbreakable chain of identity.

Even if logs are copied outside the system, the chain remains intact.

11. REVOCATION MODEL

A realm sovereign may revoke a kaitiaki instantly.

Revocation actions:

disable vector access

block all tools

revoke glyph identity

freeze taonga write permissions

move agent into disabled_kaitiaki/ registry

Te Hau may revoke entire realms.

12. SUCCESS CONDITIONS

A kaitiaki is considered valid if:

glyph signature matches registry

realm seal is intact

mana level ≤ realm mana

tapu access is fully permitted

tool permissions allow requested action

identity chain is complete

no revocation flags exist

If all true:

{
  "kaitiaki_valid": true,
  "authority": "granted",
  "realm": "<realm_id>",
  "mana": <level>,
  "scope": "<allowed_scope>"
}


---

# READY FOR PILLAR 5 — PIPELINE GOVERNANCE & TAONGA LIFECYCLE ENGINE?

This one controls:
- OCR → summarise → embed → classify → store
- taonga lifecycles
- pipelines per realm
- branching restrictions
- taonga migrations
- reclassification rules
- tapu retention
- versioning

If you're ready:

**go**