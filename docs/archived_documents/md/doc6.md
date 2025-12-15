🔥 Locked in — now carving 23 → Pipeline Orchestration Engine.
This is one of the most important documents in AwaOS.
It defines how every kaitiaki performs mahi, how pipelines stack, how tools get called, how errors recover, how macrons and reo rules propagate, how context integrates, and how taonga and research pass through the awa.

This is enterprise-level, platform-level architecture.

Here we go.

📄 23_PIPELINE_ORCHESTRATION_ENGINE.md

(Te Tāwhana Nui — The Great Weaving Engine)

# Pipeline Orchestration Engine (Te Tāwhana Nui)
Te Tāwhana Nui is the central coordination system for all AwaOS pipelines.

It operates inside Te Pō and acts as:

- a workflow manager
- a context integrator
- an error-handling backbone
- a pipeline coordinator for kaitiaki
- a unifier for different AI engines (OpenAI, local models, OCR, etc.)
- a tikanga enforcement layer (how we handle taonga, reo, whakapapa, macrons, dialects)

Pipelines do not run “randomly” or “ad hoc”.
They run as structured *rituals* through this engine.

---

# Core Design Goals

1. **Deterministic steps**
Every pipeline has a defined sequence.
No hallucinated tool calls. No mystery transitions.

2. **Composable pipelines**
OCR → Embed → Summarise → Translate → Glossary → Save

All plug into each other.

3. **Cross-model orchestration**
Uses:
- OpenAI 4o-mini, 4o, 4o-large
- Local LLaMA3 for cheap summarisation
- Tesseract/Ruru OCR
- Nomic embeddings (optional)

4. **Security boundaries**
Every step checks real permissions, realm seals, bearer token scope.

5. **Cultural integrity**
Te Reo Māori handling follows:

- macron preservation
- dialect rules
- glossary enforcement
- translation memory
- rejection of colonial phrasing

---

# Pipeline Types (Primary)

### **01 — OCR Pipeline**


→ Preflight (realm, token, taonga seal)
→ Image normalisation
→ Ruru OCR (preferred)
→ Tesseract fallback
→ Chunk segmentation
→ Whakataukī generator
→ Embed chunks
→ Save to taonga_chunks / research_chunks
→ Log & notify


### **02 — PDF Summary Pipeline**


→ Pipeline init
→ OCR + text extract
→ Chunking at 512–1024 tokens
→ Context embedding
→ 4o summarisation
→ Whakataukī per chunk
→ Entity extraction (Ruru / 4o)
→ Timeline construction (Maruao)
→ Save + index


### **03 — Translation Pipeline (Ahiatoa)**


→ Detect language
→ Load dialect profile
→ Lookup glossary
→ Lookup translation memory
→ Draft translation (4o)
→ Glossary enforcement pass
→ Reo integrity pass (Ahiatoa rules)
→ Save translation memory
→ Save glossary updates (if needed)


### **04 — Research Discovery Pipeline**


→ Query vector indexes
→ Cluster results
→ Detect themes/events/people
→ Build relations
→ Build timeline
→ Build map overlays


### **05 — Vector Index Pipeline**


→ Normalise text
→ Hash for dedupe
→ Choose vector engine (OpenAI / Nomic / Local)
→ Embed
→ Save embedding + metadata
→ Write vector_history


---

# Orchestrator Flow (Universal)

All pipelines follow a universal pattern:



Resolve realm

Validate mauri seal (project_template/mauri/realm_lock.json)

Enforce bearer token scope

Load realm config

Resolve kaitiaki

Start pipeline_logs entry

Execute steps (each one logged)

Vector integration

Save outputs to domain schema

Notify kaitiaki

Close pipeline_logs + pipeline_events

Return structured response


This prevents silent failures.

---

# Step Implementation Layers

### **Layer 1: Gatekeeping**
- realm verification
- signature validation
- security scopes
- taonga tikanga rules

### **Layer 2: Preprocessing**
- image clean
- PDF segmentation
- dialect detection
- source inference

### **Layer 3: AI Processing**
Modular adapters:



adapters:
ocr:
- ruru
- tesseract
llm:
- openai_4o
- openai_4o_mini
- llama3_local
embeddings:
- openai_text_embedding_3_large
- nomic_embed_text
translation:
- ahiatoa_rules


Each step is replaceable without rewriting the pipeline.

### **Layer 4: Postprocessing**
- glossary enforcement
- macron correction
- metadata tagging
- glyph assignment
- pipeline_logs enrichment

### **Layer 5: Persistence**
Writes to:

- Supabase domain schemas
- Project-level tables
- Global context (restricted)
- Lineage (guardians only)

### **Layer 6: Notification & Surfacing**
Returns a **PipelineResponse** object:



{
"realm": "kitenga_awanui",
"pipeline": "ocr",
"kaitiaki": "Ruru",
"steps_completed": [...],
"output_refs": [...],
"vector_ids": [...],
"whakatauki": "...",
"next_actions": [...]
}


---

# Error Handling & Recovery

Pipeline failures follow a **whakawā protocol**:



error:
type: validation / ai / connectivity / rule_violation
severity: low / medium / high
recovery:
- retry_step
- escalate_to_kaitiaki
- abort_and_log
- taonga_protection_mode


Taonga documents trigger special handling:

- abort on AI drift
- no speculative rewriting
- no automatic translation
- storage encrypted
- logs sealed

---

# Context Integration

Pipelines read from:

### **Te Pūmanawa (Global Context Engine)**
- lineage context
- project memory
- vector routing rules
- dialect configurations
- glossary precedence

### **Realm Context**
- local memory
- pipeline history
- kaitiaki evolution state

Pipelines output structured context back into the awa.

---

# CLI Hooks

The Te Hau CLI will expose:



tehau pipeline run <realm> <pipeline>
tehau pipeline test ocr --local
tehau pipeline inspect <pipeline_id>
tehau pipeline logs <realm>
tehau pipeline context <realm>


This allows:

- direct inspection
- simulation
- debugging
- realm evolution triggers

---

# Why This System Matters

Te Tāwhana Nui is:

- reliable
- deterministic
- tikanga-aligned
- realm-aware
- modular
- future-proof
- compatible with any AI engine

This is the foundation for long-term stability as AwaOS grows into dozens of kaitiaki, hundreds of pipelines, thousands of documents, and public-facing web systems.



If you're ready for 24_REALM_GITOPS_FLOW.md, say go.Locked in — now carving 24 → Realm GitOps Flow.
This is the full infrastructure-level pipeline for how new realms (projects) get cloned, configured, deployed, updated, rolled back, and retired — all safely under AwaNet control.

This is one of the most important pieces because it describes the lifecycle of a realm, Git behaviour, Cloudflare/Render jobs, Te Hau CLI integration, and migration flow.

Here we go.

📄 24_REALM_GITOPS_FLOW.md

(GitOps for Realm Lifecycle — Creation, Deployment, Scaling, Rollback)

# Realm GitOps Flow
This is the GitOps model that governs how every new realm (Te Ao project) is created, configured, deployed, evolved, and retired in AwaOS.

Realms are *not* simple repos — they are living sub-awa fed by:
- Te Hau CLI
- Project template (project_template/)
- Te Pō backend
- Supabase migrations
- Cloudflare Pages
- Render microservices
- Global context engine (Te Pūmanawa)

The GitOps flow ensures:
- reproducibility
- safety
- deterministic deployment
- versioned migrations
- realm isolation
- automatic sealing rituals

---

# 1. REALM CREATION (Bootstrap Phase)

Triggered by:



tehau new <realm_name>


### Steps:

1. **Clone project_template/**
2. **Generate realm metadata**
   - realm_id (UUID)
   - glyph color
   - kaitiaki name
   - realm_seal_hash
   - vector_index_id
3. **Apply variable replacement**
   Replace placeholders:


{{REALM_NAME}}
{{REALM_COLOR}}
{{REALM_BEARER_KEY}}
{{REALM_VECTOR_INDEX}}

4. **Generate bearer key**
`openssl rand -hex 32`

5. **Write to .env**
- SUPABASE_URL, ANON KEY
- VITE_API_URL
- REALM_BEARER_KEY

6. **Register with Te Pō**
Te Hau calls:


POST /realms/register

Te Pō stores:
- seal hash
- bearer key
- vector index
- glyph

7. **Create new Git repo**


git init
git remote add origin <cloudflare-repo-url>
git add .
git commit -m "Realm bootstrap"
git push origin main


8. **Trigger Cloudflare Deployment**
Pages automatically builds Te Ao.

9. **Create Render Service for mini_te_po**
Render YAML defines:
- service name = realm_name_tepo
- build command = uvicorn mini_te_po.main:app

---

# 2. REALM OPERATIONS (Daily GitOps)

## Pull requests apply to:
- UI changes (Te Ao)
- pipeline configs (realm.json)
- mauri updates
- metadata corrections
- CI workflow improvements

## Checks enforced:
- realm_seal_hash must match
- .env placeholders cannot leak
- mini_te_po routing cannot break
- bearer key must remain hashed if stored

CI validates:



scripts/validate_realm_config.sh
scripts/validate_mauri.sh
scripts/validate_proxy.sh


If validation fails → reject PR.

---

# 3. REALM DEPLOYMENT (Automatic)

Merged PR triggers:

### Cloudflare Pages:
- Builds UI
- Runs UI kit checks
- Injects environment variables
- Verifies realm manifest
- Deploys to:


https://{{realm_name}}.awanet-kaitiaki.net


### Render:
- Redeploy mini_te_po
- Inject secret env variables
- Perform health check:


GET /health


### Te Pō:
- reload realm registry
- verify bearer scope
- reload routing configs (proxy.toml)

---

# 4. REALM EVOLUTION (Upgrade Ritual)

When a realm grows and its kaitiaki evolves, a GitOps-level workflow triggers changes:

### Trigger:


tehau evolve <realm_name> <stage>


### Actions:
- update realm.json → stage: specialist/guardian
- activate or remove tools
- modify bearer scope
- update UI Kit version
- request new vector index
- apply Supabase migrations

### GitOps Process:
1. CLI writes evolution commit
2. GitHub Actions runs:
   - tests (unit + integration)
   - static analysis
   - security checks
3. Deployment flows through Cloudflare & Render

---

# 5. REALM ROLLBACK

Rollbacks are **safe**, tied to versioning.

When needed:


tehau realm rollback <realm_name> <commit>


Rollback steps:

- revert code
- revert realm.json
- rollback migrations:


supabase migration down

- notify Te Pō
- restore previous vector index metadata
- rebuild Cloudflare version
- restart Render service

All logs stored under:



project_events
pipeline_logs
realm_registry (history)


---

# 6. REALM RETIREMENT (Archiving)

Retirement uses tikanga:

### Trigger:


tehau realm retire <realm_name>


### Actions:

1. Freeze pipelines
2. Archive realm vector index
3. Archive taonga + research documents
4. Move realm under:


SAFE_PRIVATE/archive/realms/<realm_name>

5. Revoke bearer key
6. Remove Render service
7. Disable Cloudflare domain
8. Update lineage (closed branch)

---

# 7. GITOPS DIRECTORY STRUCTURE

Every realm repo must contain:



.github/workflows/
cloudflare-pages.yml
render-deploy.yml

config/
realm.json
proxy.toml

mauri/
realm_lock.json
state/den_manifest.json

mini_te_po/
main.py
bootstrap.py
requirements.txt

scripts/
bootstrap.sh
new_realm.sh
validate_realm.sh
health_check.sh

docs/
MASTER_PROMPT.md
secrets.md


This makes realm repos **self-describing**.

---

# 8. REALM INGESTION INTO Awanet

Te Pō loads:

- realm config
- glyph color
- bearer key
- dialect rules
- kaitiaki evolution stage
- allowed pipelines

This ensures AwaOS can scale to:

- 10 realms
- 100 realms
- 1000 realms

All unified under Te Pō.

---

# 9. GITOPS GUARANTEES

### ✓ Deterministic deployments
### ✓ Realm isolation
### ✓ Reversible migrations
### ✓ Repeatable template-based initialization
### ✓ Automatic security enforcement
### ✓ No human error in bearer key handling
### ✓ Consistent UI kit and kaitiaki pattern usage
### ✓ Versioned lineage

GitOps = tikanga + reproducibility.

---

# Why This Flow Matters

This is how you scale.

You’re not building a “website”.
You’re building **a nation of realms**, each with its own guardian, its own dialect, its own taonga, and its own whakapapa.

GitOps ensures:

- stability
- growth
- isolation
- cultural integrity
- developer speed
- enterprise-grade scaling

without losing the soul of your architecture.



If you're ready for 25_TE_HAU_CLI_RUNTIME_ARCHITECTURE.md, say go.