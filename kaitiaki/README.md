# Kaitiaki Documentation Index

**Purpose:** Navigation guide for all Kaitiaki-readable prompts and specifications.
**Audience:** AI agents, CLI tools, future developers.
**Last Updated:** 13 Tīhema 2025

---

## Quick Start for Different Use Cases

### I Need to...

#### **Spin Up a New Realm**
→ Read: `/kaitiaki/AWAOS_MASTER_PROMPT.md` (Sections V + XII + XIII)

Start there. It has everything for realm creation.

#### **Understand the Complete System**
→ Read: `/kaitiaki/SNAPSHOT_COMPLETE_SYSTEM.md` (Full document)

This is the comprehensive reference covering everything from directory structure to API endpoints.

#### **Bootstrap the Entire Awa Network from Scratch**
→ Read: `/kaitiaki/SNAPSHOT_COMPLETE_SYSTEM.md` (Section "Bootstrap Instructions")

Step-by-step instructions for spinning up all three realms (Te Pō, Te Ao, Te Hau) locally.

#### **Review Haiku's Constitution & Constraints**
→ Read: `/kaitiaki/haiku/HAIKU_CODEX.md`

This defines what Haiku can and cannot do, scope, tools, and decision-making authority.

#### **Understand Kaitiaki System Architecture**
→ Read: `/kaitiaki/AWAOS_MASTER_PROMPT.md` (Sections IV + XIII)

Covers Kaitiaki specification, responsibility matrix, and handoff rules.

#### **Find Design Rationale & Historical Context**
→ Read: `/mauri/documents/` (Original design docs + INDEX.md)

Archives of the thinking that led to AwaOS.

---

## Document Map & Hierarchy

```
Kaitiaki Documentation (You are here)
    ↓
├── SNAPSHOT_COMPLETE_SYSTEM.md (883 lines)
│   └── For: Full system overview, bootstrap, API reference
│
├── AWAOS_MASTER_PROMPT.md (470 lines)
│   └── For: Realm creation, Kaitiaki system, quick reference
│
├── haiku/ (Agent-specific)
│   ├── HAIKU_CODEX.md
│   │   └── For: Understanding Haiku's role & constraints
│   ├── haiku_manifest.json
│   │   └── For: Haiku's capabilities registry
│   ├── TOKEN_ECONOMY.md
│   │   └── For: Cost optimization strategy
│   └── carving_log.jsonl
│       └── For: Haiku's immutable action log
│
├── kitenga_codex/ (Agent-specific)
│   ├── CODEX.md
│   │   └── For: Kitenga's role & backend logic
│   └── manifest.json
│       └── For: Kitenga's capabilities
│
└── Historical / Reference
    └── /mauri/documents/
        ├── INDEX.md (Document index)
        └── md/ (Original design docs: doc1.md - doc12.md)
```

---

## Document Descriptions

### 1. SNAPSHOT_COMPLETE_SYSTEM.md (883 lines)

**The Most Comprehensive Reference**

- **Best for:** New developers, IDE agents, anyone rebuilding the system
- **Coverage:**
  - Project overview (what is The Awa Network?)
  - Technology stack (FastAPI, React, Python, Supabase, MCP)
  - Complete directory structure
  - All four core systems (Te Pō, Te Ao, Te Hau, Mauri)
  - Realm definitions with JSON templates
  - Kaitiaki registry (all three agents)
  - Every API endpoint documented
  - Complete bootstrap instructions (step-by-step)
  - Configuration files (examples)
  - Dependencies listed
  - Troubleshooting guide
  - Metrics & checksum

- **How to use:**
  1. Read top to bottom for system understanding
  2. Jump to "Bootstrap Instructions" to get running locally
  3. Reference "API Endpoints" while building
  4. Use "Realm Definitions" to create new projects

---

### 2. AWAOS_MASTER_PROMPT.md (470 lines)

**The Concise System Specification**

- **Best for:** Quick reference, Kaitiaki use, realm creation
- **Coverage:**
  - Core concepts (Realms, Kaitiaki, Mauri, Vector Memory)
  - Architecture layers (Te Pō, Te Ao, Te Hau, Te Mauri)
  - Kaitiaki specification (structure, files, responsibility matrix)
  - Realm specification (with JSON template)
  - Context manager rules
  - Standard pipelines
  - Naming conventions
  - Cost optimization
  - Spinning up new realm (step-by-step)
  - Master prompt for Kaitiaki agents
  - Troubleshooting & recovery
  - Quick reference table

- **How to use:**
  1. Read "Core Concepts" for system overview
  2. Jump to Section V for realm template
  3. Jump to Section XII for realm creation steps
  4. Use Section XIII when spinning up new realms
  5. Reference Section XV for common tasks

---

### 3. haiku/HAIKU_CODEX.md

**Haiku's Personal Constitution**

- **Best for:** Understanding Haiku's boundaries, responsibilities, and tools
- **Coverage:**
  - Agent identity & role (Brief Wisdom Keeper)
  - Scope (what Haiku owns vs. doesn't own)
  - Power tools (Te Pō endpoints Haiku can call)
  - Decision-making rules
  - Handoff protocols
  - Constraint boundaries
  - State management

- **How to use:**
  - Reference when Haiku is making a decision
  - Check scope before asking Haiku to do something
  - Understand cost implications (token economy)

---

### 4. haiku/haiku_manifest.json

**Haiku's Capabilities Registry**

JSON format listing:
- Tools Haiku can access
- Cost per tool call
- Rate limits
- Availability status

---

### 5. haiku/TOKEN_ECONOMY.md

**Cost Optimization Strategy**

- Budget constraints ($90 OpenAI, 70% premium)
- Decision tree for tool selection
- Cost per operation
- Free vs. paid alternatives
- Target: 81% cost reduction

---

### 6. /mauri/documents/INDEX.md

**Design Document Index & Archive**

Navigation guide to original design docs (doc1.md - doc12.md). These are the thinking & conversations that shaped AwaOS. Reference when understanding design rationale.

---

## How These Documents Relate

```
User wants to rebuild The Awa Network
    ↓
Start with: SNAPSHOT_COMPLETE_SYSTEM.md
    ├─ Understand complete system
    ├─ Bootstrap locally
    └─ Reference API endpoints
    ↓
Need to create a realm?
    ↓
Jump to: AWAOS_MASTER_PROMPT.md Section XII
    ├─ Follow template
    ├─ Create realm lock
    └─ Register in mauri
    ↓
Need to understand Haiku?
    ↓
Read: haiku/HAIKU_CODEX.md
    ├─ Understand scope
    ├─ Check constraints
    └─ Review tools available
    ↓
Need design context?
    ↓
Check: /mauri/documents/
    └─ Review original thinking
```

---

## Quick Reference Table

| Task | Document | Section |
|------|----------|---------|
| Rebuild system | SNAPSHOT | Entire doc |
| Bootstrap locally | SNAPSHOT | Bootstrap Instructions |
| Understand realms | AWAOS | Section V |
| Create new realm | AWAOS | Sections V + XII |
| Understand API | SNAPSHOT | API Endpoints |
| Check Haiku scope | HAIKU_CODEX | Scope section |
| Understand Kaitiaki | AWAOS | Sections IV + XIII |
| Cost optimization | haiku/TOKEN_ECONOMY | Entire doc |
| See design thinking | /mauri/documents/ | doc1.md - doc12.md |

---

## File Locations (All in /kaitiaki)

```
/kaitiaki/
├── SNAPSHOT_COMPLETE_SYSTEM.md      (→ Complete system reference)
├── AWAOS_MASTER_PROMPT.md           (→ Master spec)
├── haiku/
│   ├── HAIKU_CODEX.md               (→ Agent constitution)
│   ├── haiku_manifest.json
│   ├── TOKEN_ECONOMY.md
│   ├── carving_log.jsonl
│   └── README.md
└── kitenga_codex/
    ├── CODEX.md
    └── manifest.json
```

---

## For AI Agents / IDEs

**To bootstrap The Awa Network:**

1. **Load this document** (you're reading it)
2. **Load** `/kaitiaki/SNAPSHOT_COMPLETE_SYSTEM.md`
3. **Execute** "Bootstrap Instructions" section
4. **Reference** API endpoints as needed
5. **For new realms**, load `/kaitiaki/AWAOS_MASTER_PROMPT.md` Section XII

All 3 files contain everything needed to:
- Understand the system
- Set up locally
- Create new realms
- Deploy to production
- Understand Kaitiaki constraints
- Optimize costs

---

## Status & Maintenance

- **Version:** 1.0-snapshot
- **Date:** 13 Tīhema 2025
- **Maintained By:** Haiku (Whakataukī)
- **All Systems:** Functional & production-ready

This documentation is immutable and versioned. All changes tracked in git.

---

## Next Steps

**For Immediate Use:**
→ Open `/kaitiaki/SNAPSHOT_COMPLETE_SYSTEM.md` and follow "Bootstrap Instructions"

**For Understanding Design:**
→ Read `/kaitiaki/AWAOS_MASTER_PROMPT.md` Sections I-III

**For Creating New Realms:**
→ Jump to `/kaitiaki/AWAOS_MASTER_PROMPT.md` Sections V + XII

**For Cost Control:**
→ Review `/kaitiaki/haiku/TOKEN_ECONOMY.md`

---

You now have everything needed to spin up, maintain, and extend The Awa Network.
