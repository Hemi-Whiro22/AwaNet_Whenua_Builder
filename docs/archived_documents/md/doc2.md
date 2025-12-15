📘 DOCUMENT 2 — THE AWAOS BIBLE (MONOLITHIC FULL REWRITE)
The complete unified system specification for Realms, Kaitiaki, Mauri, Context, Branching, Vector Memory, Templates, Runtime, Sovereignty, and Expansion.
This is the “master doc” you can drop into Codex, CLI, MCP, Assistants, or Git.
AWAOS — FULL SYSTEM SPECIFICATION (MONOLITHIC)

A living operating system for cultural compute, sovereign intelligence, multi-realm orchestration, and kaitiaki-driven computation.

TABLE OF CONTENTS

Purpose & Vision of AwaOS

Foundational Concepts

Realms

Kaitiaki

Mauri

Context Manager

Seeds & Branches

Vector Memory

Templates

Runtime

Layered System Architecture

Te Pō

Te Ao

Te Hau

Mauri Layer

Naming Conventions

Realm Specification

Kaitiaki Specification

Mauri Engine Specification

Branching & Seed Specification

Vector Memory Specification

Context Routing Specification

Project Templates Specification

Sovereign Compute Pathways

Translator Module Specification

Security & Isolation

Realms → Backend Integration

GitOps & Automation

AwaOS Expansion Architecture

Appendices (Glossary + JSON Specs)

1. Purpose & Vision of AwaOS

AwaOS is a framework for building multi-realm knowledge systems powered by:

cultural values

sovereign compute

local + cloud hybrid intelligence

scalable multi-agent design

long-term memory

cross-realm orchestration

repeatable templates

AwaOS is not a monolithic app.
It is a living OS for Kaitiaki — each realm is independent, isolated, sovereign, but still capable of flowing into the greater awa.

The system is designed to support:

taonga preservation

iwi knowledge systems

translator services

OCR & archival pipelines

new business ventures

custom kaitiaki agents

frontends for whānau

hybrid local/offline compute

Every project sits inside its own Realm, guarded by its own Kaitiaki, bound by its own Mauri, driven by the AwaOS runtime.

2. Foundational Concepts
2.1 Realms

A Realm is a complete project container:

frontend (Te Ao)

mini backend (mini Te Pō proxy)

kaitiaki logic

Mauri identity

memory namespace

routes & hooks

glyphs / seals

state folder

vector index

A realm is sovereign — no realm can see another directly.

All cross-realm communication goes through:

Te Pō → Kaitiaki → Context Router

2.2 Kaitiaki

A Kaitiaki is a project-specific agent that:

embodies purpose

holds vector memory

enforces mauri

protects boundaries

controls tools

manages translations, OCR, indexing, UI responses

operates within the realm

delegates heavy tasks to Te Pō

Types:

Realm Kaitiaki

Scoped to one project

Has its own OpenAI Assistant (optional)

Has its own vector namespace

Has its own memory rules

Global Kaitiaki

Kitenga Whiro (Primary brain)

OCR/Ruru engine

Embedding engines

Translation logic shared system-wide

2.3 Mauri

Mauri is the identity system, defining:

what a realm is

what it can do

what tools are enabled

its glyph & lineage

its environment

its encoding rules

its vector scopes

its permissions

its cultural values

its runtime restrictions

Mauri is expressed as:

mauri/
  realm_lock.json
  den_manifest.json
  state/


Where:

realm_lock.json — binds Kaitiaki ↔ Realm
den_manifest.json — describes capabilities
state/ — runtime state & config

2.4 Context Manager

The bridge between Realms and the AwaOS backend.

It:

restricts what information can pass

performs memory routing

validates kaitiaki calling rules

enforces mauri-based logic

orchestrates long workflows

manages external tools

It is Te Ara Mārama — the path of knowledge between layers.

2.5 Seeds & Branches
Seeds

Seeds represent the base definitions for:

realms

kaitiaki

templates

ui

backend configurations

pipelines

They define initial form before divergence.

Branches

Branches represent:

new capabilities

new versions

new realms

expansions

project evolution

This mirrors Git but is conceptual and includes:

memory

mauri

glyph evolution

runtime logic

Seeds and branches allow AwaOS to evolve organically.

2.6 Vector Memory

Every realm has a private memory namespace:

awanet.<realm>.<kaitiaki>


Memory can be held in:

OpenAI vector store (fast recall)

Supabase vector db (long-term)

Local embedding index (sovereign compute)

Vector memory ensures:

project autonomy

no cross-pollution

deterministic recall

permanent taonga storage

2.7 Templates

Templates define the structure of a Realm:

project_template/
  te_ao/
  mini_te_po/
  mauri/
  config/
  scripts/
  docs/


Templates include:

stub backend proxy

new_realm.sh token generator

secrets manifest

deployment workflows

key placeholders

routes pointing to main Te Pō

optional starter kaitiaki

local devcontainer/docker config

Templates allow extremely fast realm creation.

2.8 Runtime

The AwaOS runtime follows this path:

Te Ao (UI)
  → mini Te Pō proxy (per-realm backend)
    → main Te Pō engine (global backend)
      → Kaitiaki (intelligence module)
        → Vector / Supabase / OCR / Translator
    ← back up the chain
  ← return to UI


Every realm is isolated and only communicates through authenticated channels.

3. Layered Architecture
Layer 1 — Te Pō (Global Backend Layer)

Responsibilities:

OCR

Translation

Embeddings

Memory indexing

Vector stores

Context routing

Tool calling

Realm auth

Supabase integration

On-device compute (optional)

Te Pō is the engine room — the deep intelligence layer.

Layer 2 — Te Ao (Frontend Realms)

Responsibilities:

user interaction

project workflows

UI

realm-focused tools

tunnel routing

Te Ao never talks directly to Te Pō.
It always passes through mini Te Pō for security and isolation.

Layer 3 — Te Hau (Operator / CLI Layer)

Responsibilities:

realm scaffolding

template duplication

secrets provisioning

branch creation

deployment

key rotation

GitOps

dev workflow

Te Hau is the developer realm — the builder.

Layer 4 — Mauri (Identity Layer)

Responsibilities:

realm locks

lineage

glyphs

capabilities

encoding rules

context permissions

purpose definition

Mauri defines the essence of a realm.

4. Naming Conventions

AwaOS uses a strict naming convention to maintain coherence:

<realm>_<kaitiaki>_<purpose>


Examples:

kitenga_awanui_translator

te_puna_reader

ruru_ocr_engine

Vector namespaces:

awanet.realm.kaitiaki


Supabase table prefixes:

<realm>_<feature>_logs
<realm>_vector_memory

5. Realm Specification

A Realm MUST contain:

realm/
  te_ao/
  mini_te_po/
  mauri/
  config/
  scripts/
  docs/


Plus optional:

vector_seed/
tests/
hooks/
assets/


Minimum requirements:

name

realm_lock.json

bearer_key

backend proxy

UI entry point

tunneling rules

deployment workflow

secrets manifest

6. Kaitiaki Specification

Each Kaitiaki MUST have:

identity:
  name
  realm
  purpose
  glyph
runtime:
  tools_enabled
  vector_namespace
  context_rules
memory:
  vector_store
  supabase_tables
integration:
  te_po_routes
  ui_panels


Optional:

OpenAI Assistant ID

personality scaffolding

historical glyph lineage

7. Mauri Engine Specification

Mauri is defined by:

Required Files:
mauri/realm_lock.json
mauri/den_manifest.json
mauri/state/

Functions:

enforce realm identity

restrict access

validate context flows

provide cultural logic

define translation ruleset

uphold taonga protection

manage encoding

Mauri is the sovereignty layer.

8. Branching & Seed Specification
Seeds define:

project start state

naming conventions

realm identity

base mauri

kaitiaki frame

tool availability

initial folder layout

Branches define:

new features

expanded kaitiaki

new business apps

dialect & translation evolutions

multi-agent chains

Branches can evolve independently.

9. Vector Memory Specification

Each realm has its own:

embedding model

vector namespace

memory depth

context rules

spotlight rules

semantic anchoring

Vector memory can be stored:

cloud

local

hybrid

Memory drift is prevented through strict namespacing.

10. Context Routing Specification

Context Manager enforces:

what can pass

what must not pass

what belongs to which realm

what may be summarised

what goes to vector

what triggers tool calling

Context routing follows:

realm → mini → global → tool → memory → global → mini → realm

11. Project Template Specification

Template includes:

.env template

new_realm.sh

mini backend proxy

devcontainer

dockerfile

realm seed folders

workflow templates

secrets manifest

master prompt

CI/CD pipeline

A realm can be created in:

./te_hau new realm_name

12. Sovereign Compute Pathways

AwaOS supports:

Cloud

OpenAI

Supabase

Render

Cloudflare

Hybrid

local Llama3 for embeddings

cloud OCR fallback

cloud summarisation

Fully Local

mistral-small summariser

llama3 8B q4

local vector store

offline OCR

This is the sovereignty guarantee.

13. Translator Module Specification

The Translator pipeline includes:

macron correction

UTF-8 enforcement

dialect variations

Māori → English

English → Māori

tone-aware translation

cultural safety filters

reliability scoring

Supabase logging

vector embedding of all translations

This module becomes a commercial offering:

Awanui Whakamaori API

14. Security & Isolation

Isolation is enforced through:

per-realm bearer keys

per-realm vector spaces

per-realm state

mini backend separation

no direct Te Ao → Te Pō connection

tunneling rules

revocable keys

realm locks

15. Realms → Backend Integration

Everything flows through:

mini_te_po/
  routes/
  auth/
  proxy/


Mini backend:

isolates the realm

rotates keys

handles proxy routing

forwards to main backend securely

16. GitOps & Automation

Tasks automated by Te Hau CLI:

scaffold realm

apply seeds

generate keys

set env

register realm with Te Pō

create repo

push template

configure Cloudflare Pages

configure Render backend

set project metadata

initialise vector memory

apply mauri locks

17. AwaOS Expansion Architecture

AwaOS can power:

iwi research clouds

taonga archives

Māori translation engines

interactive whakapapa

tamariki learning tools

commercial language APIs

scanner OCR apps

tourism knowledge platforms

cultural compute networks

AwaOS is built to scale.

18. Appendices

Full JSON examples, glyph spec, state templates, and placeholder definitions will live in the packaged version (Document 3).

END OF DOCUMENT 2