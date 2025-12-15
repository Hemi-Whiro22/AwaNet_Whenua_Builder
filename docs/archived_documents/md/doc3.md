📁 DOCUMENT 3 — AWAOS PACKAGED MULTI-FILE SYSTEM (FULL DIRECTORY + FILE CONTENTS)
This is the enterprise version — the one made for Codex, CLIs, MCP servers, agents, render pipelines, and Git.
Each file below is carved clean, modular, AI-readable, human-understandable, and aligned with the Monolithic AwaOS Bible.
⚠️ STRUCTURE OF WHAT I WILL OUTPUT (Important for context window)

I will carve each file as a clean standalone module.

To avoid drift and maintain maximum clarity, I will output 4 files per message, then pause for your “go” before continuing.

This ensures:

No dilution

No truncation

Perfect hierarchy

Each file is usable individually

CLI + Codex + backend can parse reliably

📦 AwaOS Packaged Spec — Files in This Volume
AwaOS/
  00_INDEX.md
  01_REALMS.md
  02_KAITIAKI.md
  03_MAURI.md
  04_CONTEXT_MANAGER.md
  05_VECTOR_MEMORY.md
  06_NAMING.md
  07_BRANCHING.md
  08_RUNTIME.md
  09_TEMPLATES.md
  10_TRANSLATOR.md
  11_EXPANSION_PLAN.md
  12_SECURITY_MODEL.md
  13_API_DESIGN.md
  14_CLI_INTEGRATION.md


This is a complete software specification library.

🔥 NOW BEGINNING FILE CARVING

Below are the first 4 files:

📄 00_INDEX.md
# AwaOS Specification Index

This directory contains the full AwaOS system specification.
It is designed for:
- human architects
- AI agents (Codex, MCP, Kaitiaki)
- Te Hau CLI
- Realm scaffolding
- Backend extension
- Documentation generators

## Files

01_REALMS.md — Definition and structure of realms
02_KAITIAKI.md — Kaitiaki architecture and runtime
03_MAURI.md — Mauri engine specification
04_CONTEXT_MANAGER.md — Context flow rules
05_VECTOR_MEMORY.md — Vector namespace and memory
06_NAMING.md — Naming conventions
07_BRANCHING.md — Seeds and branches
08_RUNTIME.md — Execution flow
09_TEMPLATES.md — Realm template specification
10_TRANSLATOR.md — Māori translator module
11_EXPANSION_PLAN.md — Growth, commercialisation, future modules
12_SECURITY_MODEL.md — Realm isolation and auth design
13_API_DESIGN.md — Backend route definitions
14_CLI_INTEGRATION.md — Te Hau CLI specification

Use this index as the root for tooling or doc generation.

📄 01_REALMS.md
# AwaOS Realms Specification

A Realm is an isolated project container within AwaOS.

## Purpose of Realms
- Encapsulate state, identity, UI, backend proxy, and memory.
- Provide sovereign compute boundaries.
- Allow new projects to be generated from templates.
- Enable kaitiaki to operate with isolated context.

## Realm Structure



realm/
te_ao/ # UI layer
mini_te_po/ # Proxy backend
mauri/ # Identity + restrictions
config/ # Project configuration
scripts/ # bootstrap, keygen
docs/ # master prompt, secrets guide


## Required Realm Files
- mauri/realm_lock.json
- mauri/den_manifest.json
- .env (generated at spin-up)
- mini_te_po/main.py
- config/realm.json

## Realm Identity Fields

Each realm defines:



realm_name
realm_glyph
realm_purpose
vector_namespace
allowed_kaitiaki
deployment_targets
encoding_rules
mauri_capabilities


## Realm Lifecycle

1. Create from template
2. Assign bearer key
3. Register with main Te Pō backend
4. Link to a realm-specific Kaitiaki (optional)
5. Deploy Te Ao + mini Te Pō
6. Begin operation

📄 02_KAITIAKI.md
# Kaitiaki Specification

A Kaitiaki is the intelligence module of a Realm.

## Types of Kaitiaki

### Realm Kaitiaki
- Scoped to one realm
- Uses its own vector namespace
- Implements realm logic (translator, OCR, taonga sorter, etc.)

### Global Kaitiaki
- System-level intelligence
- Example: Kitenga Whiro
- Can observe all realms (under mauri rules)

## Required Kaitiaki Fields



identity:
name
realm
glyph
purpose

runtime:
tools_enabled
vector_namespace
context_rules
delegate_routes

memory:
long_term (supabase)
short_term (openai)
local_embeddings (optional)


## Kaitiaki Responsibilities

- Maintain cultural and technical alignment
- Enforce mauri rules
- Manage tool usage
- Communicate with mini Te Pō via secure API
- Provide reasoning for Te Ao UI
- Bind human + machine workflow

## Optional Integrations
- OpenAI Assistant ID
- Ruru OCR tools
- Translator toolchain
- Document pipelines

📄 03_MAURI.md
# Mauri Engine Specification

Mauri defines identity, integrity, and allowed capabilities for each realm.

## Purpose of Mauri
- Enforce sovereignty
- Protect taonga
- Restrict inter-realm leakage
- Bind a Kaitiaki to its realm
- Define encoding + translation rules
- Determine tool access

## Mauri Directory Structure



mauri/
realm_lock.json
den_manifest.json
state/


## realm_lock.json

Fields:



{
"realm_name": "",
"locked_kaitiaki": "",
"glyph": "",
"origin_seed": "",
"created_at": "",
"permissions": {
"vector_access": true,
"supabase_access": true,
"translator_module": false,
"ocr_module": false
}
}


## den_manifest.json

Defines realm-level behaviour:



{
"capabilities": {
"translation": false,
"ocr": false,
"embedding": true,
"offline_mode": false
},
"encoding": {
"mi_NZ": true,
"utf8": true,
"macron_rules": "default"
}
}


## state/

Used to store:
- runtime identity
- glyph lineage
- UI preferences
- local dev overrides

🔥 This is the first block of 4 files.

Say “go” to receive the next block:

04_CONTEXT_MANAGER.md → 07_BRANCHING.md