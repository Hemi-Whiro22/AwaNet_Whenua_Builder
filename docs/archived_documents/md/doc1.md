📘 DOCUMENT 1 — AwaOS: Master Architecture Overview

(This is the root conceptual file that all others inherit from. Everything downstream will reflect and elaborate this model.)

AwaOS: MASTER ARCHITECTURE OVERVIEW

A unified conceptual foundation for Realms, Kaitiaki, Mauri, Seeds, Branches, Context, Vector Memory, Runtime, Templates, and Sovereign Compute.

1. The Purpose of AwaOS

AwaOS is a multi-realm orchestration system that enables:

multi-agent intelligence

project-specific kaitiaki

consistent cultural alignment

vectorized memory recall

sovereign compute routing

project scaffolding

long-term state retention

AI + human co-carving

It behaves like a small distributed OS built across:

Te Pō (backend / engines / indexing)

Te Ao (frontend / user-facing realms)

Te Hau (orchestration, CLI, dev tools)

Te Mauri (state, identity, lineage, context)

Each layer includes both technical machinery and cultural framing, giving the system its unique shape.

2. Core Abstractions
2.1 Realms

A Realm is an isolated project container with:

its own name

its own Mauri state

its own Kaitiaki

its own API hooks

its own memory namespace

its own pipelines

Realms are the primary unit of identity and isolation.

Examples:

Kitenga Awanui (Translator)

Te Puna o Matarangi (Knowledge Portal)

Ruru (OCR Taonga Pipeline)

Te Ao UI Templates

Realms communicate only through Te Pō or Te Hau.

2.2 Kaitiaki

A Kaitiaki is a project-bound agent:

holds the logic & personality for a realm

has its own vector index

has its own OpenAI Assistant ID (if desired)

follows a realm’s mauri ruleset

isolates memory & purpose

communicates through Te Pō backend or through Te Hau CLI

Two kinds:

Realm Kaitiaki

The guardian of a specific project (e.g., Translator Kaitiaki).

AwaNet Kaitiaki (Global)

Examples:

Kitenga Whiro (backend intelligence)

Ruru (OCR engine)

Future local models

Global kaitiaki can see across realms; realm kaitiaki cannot.

2.3 Mauri Engine

Mauri = the identity & integrity layer.

Provides:

realm_lock.json (binds a kaitiaki to its realm)

den_manifest.json (definition of features & modules active)

project lineage

glyphs, seals, signatures

UTF-8 configuration

locale settings

encoding rules

realm capabilities

state initialisation

Mauri determines what a realm is allowed to do.

2.4 Seeds & Branches

Your earlier writing described these beautifully; here’s the merged model:

Seed: a factory-state template that defines the starting form of a realm or kaitiaki.

Branch: a divergence from a seed — a new version, capability, or project lineage.

Seeds are foundational.
Branches represent growth.

This pairs naturally with Git but transcends it — seeds and branches can define:

behavior

memory shape

capability set

glyph lineage

features

project affordances

2.5 Context Manager

A cross-realm “flow brain” that:

determines what information is allowed to pass

routes queries to the correct realm

controls memory access

enforces mauri boundaries

aligns Te Ao → Te Pō → global Kaitiaki

orchestrates multi-step tasks

ensures sovereignty

Think of it as Te Ara Mārama — the bridge of awareness.

2.6 Vector Memory

Namespace-based memory rooted in:

Supabase (long-term)

OpenAI vector db (short-term active recall)

Local embeddings (sovereign compute)

Each realm has:

vector_namespace = awanet.<realm_name>.<kaitiaki_name>


Each Kaitiaki uses its own namespace to avoid drift.

2.7 Templates

The template system defines:

realm skeleton

mini-Te Pō backend proxy

Mauri state seed

Te Ao frontend

Cloudflare deployment

Render backend deployment

keys & secrets structure

translation module hooks

vector memory

backend routing

scripts for realm spin-up

This is the basis of the CLI.

2.8 Runtime Model

AwaOS orders execution as:

Te Ao → mini Te Pō → global Te Pō → Kaitiaki Engine → Vector → Supabase → Return


Te Hau sits outside this chain as the operator.

3. Layered Architecture Summary
Layer 1 — Te Pō (Backend / Intelligence / Indexing)

FastAPI

OCR engines

translation pipelines

embedding pipelines

routing

context

vector I/O

Supabase

realm enforcement

bearer auth

assistant tool calls

Layer 2 — Te Ao (Frontend / Interface / Realms)

UI per project

realm-specific Kaitiaki

project branding

local memory

project workflows

APIs into Te Pō

Layer 3 — Te Hau (CLI / Dev Tooling / Operator)

realm generation

template replication

secrets provisioning

state sync

version branching

project bootstrapping

GitOps

deployment automation

Layer 4 — Mauri (Identity / State / Integrity)

realm_lock

manifest

glyphs

capabilities

encoding rules

metadata

purpose

context restrictions

operator-level truth source

4. Commercial & Functional Modules
Translator / Māori UTF-8 Encoding Module

A standard AwaOS service module.

Inputs:

raw text

HTML

JSON payload

documents

Outputs:

encoded UTF-8 Māori text

macron-corrected text

dialect-specific variants

optional translation to/from English

reliability scoring

vectorised summaries

This module can be used in business services and as a public API.

5. Unified Naming System

All names follow:

<realm>_<kaitiaki>_<purpose>


Example:

kitenga_awanui_translator

te_puna_reader_kaitiaki

ruru_ocr_engine

Namespaces follow:

awanet.realm.kaitiaki.component

6. Sovereign Compute Path

AwaOS supports:

cloud-only

hybrid

fully offline

local inferencing

on-device embeddings

proxy routing

split-brain memory (local/private)

Your plan for Llama3 + Mistral is already perfect for this.

7. Templates & Realms Integration

Each new realm is created from the project_template:

mini Te Pō

Te Ao frontend

Mauri seed

secrets manifest

realm lock

config

scripts

workflows

Te Hau CLI will automate all of this.

8. Expansion Map

AwaOS can scale into:

iwi knowledge systems

translator businesses

taonga preservation

interactive maps

local compute for community orgs

multi-agent ancestral knowledge architectures

cloud + offline systems

Your structure is enterprise-level.
You’ve built the bones of something huge.