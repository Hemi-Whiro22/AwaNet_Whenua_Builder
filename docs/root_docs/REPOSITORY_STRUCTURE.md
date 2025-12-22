# The Awa Network - Repository Structure

```
.
├── boot.sh
├── docker-compose.yaml
├── docs/
│   ├── architecture/
│   │   ├── MCP_ALIGNMENT.md
│   │   ├── MCP_TEST_REPORT.md
│   │   └── PROJECT_SCAN.md
│   ├── archived_architecture/
│   │   ├── awa_structure.json
│   │   ├── codex_alignment_prompt.md
│   │   ├── drift_protection.json
│   │   ├── mauri_anchor.md
│   │   ├── naming_conventions.json
│   │   └── versioning_rules.json
│   ├── archived_documents/
│   │   ├── INDEX.md
│   │   ├── md/
│   │   ├── pdfs/
│   │   └── sql/
│   ├── COMPLETE_WORKFLOW.md
│   ├── CONTEXT.md
│   ├── guides/
│   │   ├── DEVELOPMENT.md
│   │   ├── GUARDIANS.md
│   │   ├── LLAMA3.md
│   │   └── MCP_SETUP.md
│   ├── INDEX.md
│   ├── MAURI_CONTEXT.md
│   ├── PROJECT_TEMPLATE_STRUCTURE.md
│   ├── REALM_GENERATOR.md
│   ├── REALM_ISOLATION.md
│   ├── REALM_SYSTEM.md
│   └── reference/
│       ├── API_CONTRACTS.md
│       ├── GLOSSARY.md
│       └── STATE_MANAGEMENT.md
├── kaitiaki/
│   ├── AWAOS_MASTER_PROMPT.md
│   ├── haiku/
│   │   ├── haiku_carving_log.jsonl
│   │   ├── HAIKU_CODEX.md
│   │   ├── haiku_manifest.json
│   │   ├── haiku_state.json
│   │   ├── QUICKSTART.md
│   │   ├── README.md
│   │   └── TOKEN_ECONOMY.md
│   ├── HAIKU_CODEX.md
│   ├── kitenga_codex/
│   │   ├── bootstrap.py
│   │   ├── __init__.py
│   │   ├── kitenga_manifest.json
│   │   ├── logs/
│   │   ├── start_kitenga.py
│   │   ├── state/
│   │   └── tools/
│   ├── README.md
│   ├── SNAPSHOT_COMPLETE_SYSTEM.md
│   └── te_kitenga_nui/
│       └── te_kitenga_nui_manifest.json
├── LICENSE
├── realms/                         # ← Spawned realms live here
│   ├── .gitkeep
│   ├── README.md
│   └── {realm_slug}/               # Generated realm folders
│       ├── .devcontainer/
│       ├── .env
│       ├── mauri/
│       ├── realm.config.json
│       ├── README.md
│       └── te_po_proxy/
├── mauri/
│   ├── archived/
│   │   ├── kaitiaki-intake/
│   │   ├── kaitiaki_legacy/
│   │   ├── legacy_configs/
│   │   ├── mauri_legacy/
│   │   ├── scripts/
│   │   └── shared/
│   ├── global_env.json
│   ├── kaitiaki/
│   │   ├── kaitiaki_signatures.json
│   │   ├── model_registry.json
│   │   ├── model_registry_raw.json
│   │   └── te_kitenga_nui.json
│   ├── kaitiaki_templates/
│   │   ├── haiku.yaml
│   │   ├── KITENGA_CONFIGURATION.md
│   │   ├── kitenga_whiro.yaml
│   │   ├── README.md
│   │   └── te_kitenga_nui.yaml
│   ├── realm_lock.json
│   ├── realms/
│   │   ├── realm_lock.json
│   │   ├── te_ao/
│   │   ├── te_hau/
│   │   └── te_po/
│   ├── scripts/
│   │   └── compile_kaitiaki.py
│   ├── state/
│   │   ├── supabase_schema.json
│   │   ├── supabase_tables.json
│   │   ├── te_ao_state.json
│   │   ├── te_hau_state.json
│   │   ├── te_po_carving_log.jsonl
│   │   └── te_po_state.json
│   ├── te_kete/
│   │   ├── den_manifest.yaml
│   │   ├── domain_map.json
│   │   ├── glossary.json
│   │   ├── load_manifest.py
│   │   └── pipeline_map.json
│   └── whakapapa_seal.json
├── README.md
├── REALM_GENERATOR_QUICKSTART.md
├── REALM_ISOLATION_SUMMARY.md
├── render.yaml
├── requirements.txt
├── run_dev.sh
├── scripts/
│   └── test_template.py
├── te_ao/
│   ├── config/
│   │   ├── README.md
│   │   └── tools.json
│   ├── dist/
│   │   ├── assets/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   └── koru.svg
│   ├── Dockerfile
│   ├── index.html
│   ├── __init__.py
│   ├── node_modules/ (201+ packages)
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.cjs
│   ├── public/
│   │   ├── favicon.ico
│   │   └── koru.svg
│   ├── README.md
│   ├── src/
│   │   ├── App.jsx
│   │   ├── assets/
│   │   ├── components/
│   │   ├── data/
│   │   ├── devui/
│   │   ├── hooks/
│   │   ├── index.css
│   │   ├── layouts/
│   │   ├── main.jsx
│   │   ├── mauri.js
│   │   └── panels/
│   ├── start_frontend.sh
│   ├── state/
│   │   └── state.yaml
│   ├── tailwind.config.cjs
│   └── vite.config.js
├── te_hau/
│   ├── app.py
│   ├── awa/
│   │   ├── bus.py
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── whakapapa.py
│   ├── cli/
│   │   ├── awanui.py
│   │   ├── commands/
│   │   ├── devui.py
│   │   ├── hau.py
│   │   ├── __init__.py
│   │   ├── start_whakairo.py
│   │   └── utils.py
│   ├── config/
│   │   └── hau_config.yaml
│   ├── core/
│   │   ├── ai.py
│   │   ├── branching.py
│   │   ├── context.py
│   │   ├── fs.py
│   │   ├── healing.py
│   │   ├── infra.py
│   │   ├── __init__.py
│   │   ├── kaitiaki.py
│   │   ├── orchestrator.py
│   │   ├── pipeline.py
│   │   ├── protocol.py
│   │   ├── renderer.py
│   │   ├── secrets.py
│   │   ├── security.py
│   │   └── supabase.py
│   ├── Dockerfile
│   ├── __init__.py
│   ├── mauri/
│   │   ├── glyph.py
│   │   ├── __init__.py
│   │   └── seal.py
│   ├── models/
│   │   └── __init__.py
│   ├── project_template/
│   │   ├── archetypes.json
│   │   ├── config/
│   │   ├── docs/
│   │   ├── mauri/
│   │   ├── requirements.txt
│   │   ├── scripts/
│   │   ├── STRUCTURE.md
│   │   ├── te_ao/
│   │   ├── te_hau/
│   │   ├── template.config.json
│   │   └── te_po_proxy/
│   ├── README.md
│   ├── requirements.txt
│   ├── scripts/
│   │   ├── generate_realm.py
│   │   ├── realm_ui.py
│   │   └── verify_realm_isolation.sh
│   ├── sdk/
│   │   ├── compiler.py
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── types.py
│   ├── services/
│   │   ├── awa_bus.py
│   │   ├── __init__.py
│   │   ├── kaitiaki_store.py
│   │   ├── mauri.py
│   │   ├── sound.py
│   │   └── tepo_api.py
│   ├── start_tehau.sh
│   ├── state.yaml
│   ├── translator/
│   │   ├── ahiatoa.py
│   │   ├── core.py
│   │   ├── glossary.py
│   │   └── __init__.py
│   ├── util/
│   │   └── __init__.py
│   ├── verbs/
│   │   ├── awa.py
│   │   ├── branch.py
│   │   ├── cluster.py
│   │   ├── context.py
│   │   ├── deploy.py
│   │   ├── evolve.py
│   │   ├── glyph.py
│   │   ├── heal.py
│   │   ├── infra.py
│   │   ├── __init__.py
│   │   ├── init.py
│   │   ├── kaitiaki.py
│   │   ├── new.py
│   │   ├── pipeline.py
│   │   ├── seal.py
│   │   ├── security.py
│   │   └── translate.py
│   └── whakairo_codex/
│       ├── logs/
│       ├── mcp/
│       ├── README.md
│       ├── record_carve.py
│       ├── state/
│       ├── sync_carver_context.py
│       └── whakairo_manifest.json
├── te_po/
│   ├── assistants/
│   │   ├── create_kitenga_whiro.py
│   │   └── create_qa_assistant.py
│   ├── core/
│   │   ├── config.py
│   │   ├── env_loader.py
│   │   ├── __init__.py
│   │   ├── kitenga_backend.py
│   │   ├── main.py
│   │   ├── README.md
│   │   └── SECURITY.md
│   ├── __init__.py
│   ├── main.py
│   ├── mauri.py
│   ├── models/
│   │   ├── auth_models.py
│   │   ├── file_profile.py
│   │   ├── __init__.py
│   │   ├── intake_models.py
│   │   ├── memory_models.py
│   │   ├── reo_models.py
│   │   └── vector_models.py
│   ├── openai_assistants.json
│   ├── openai_tools.json
│   ├── pipeline/
│   │   ├── cards/
│   │   ├── chunker/
│   │   ├── cleaner/
│   │   ├── embedder/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   ├── metrics.py
│   │   ├── ocr/
│   │   ├── orchestrator/
│   │   ├── queue.py
│   │   ├── research/
│   │   ├── supabase_writer/
│   │   └── worker.py
│   ├── README.md
│   ├── render.yaml
│   ├── routes/
│   │   ├── assistant.py
│   │   ├── assistants_meta.py
│   │   ├── awa_protocol.py
│   │   ├── cards.py
│   │   ├── chat.py
│   │   ├── dev.py
│   │   ├── documents.py
│   │   ├── __init__.py
│   │   ├── intake.py
│   │   ├── kitenga_backend.py
│   │   ├── kitenga_tool_router.py
│   │   ├── llama3.py
│   │   ├── logs.py
│   │   ├── memory.py
│   │   ├── metrics.py
│   │   ├── ocr.py
│   │   ├── pipeline.py
│   │   ├── reo.py
│   │   ├── research.py
│   │   ├── roshi.py
│   │   ├── sell.py
│   │   ├── state.py
│   │   ├── status.py
│   │   └── vector.py
│   ├── run_tests.sh
│   ├── schema_drift_report.json
│   ├── scripts/
│   │   ├── audit_supabase.py
│   │   ├── clear_supabase_tables.py
│   │   ├── export_supabase.py
│   │   ├── poll_vector_batches.py
│   │   ├── rebuild_state.py
│   │   ├── register_kitenga_tools.py
│   │   ├── smoke_test.py
│   │   ├── snapshot_supabase_tables.py
│   │   ├── start_dev.sh
│   │   ├── storage_drift_check.py
│   │   ├── sync_mauri_supabase.py
│   │   └── sync_storage_supabase.py
│   ├── services/
│   │   ├── chat_memory.py
│   │   ├── __init__.py
│   │   ├── local_storage.py
│   │   ├── memory_service.py
│   │   ├── ocr_service.py
│   │   ├── reo_service.py
│   │   ├── summary_service.py
│   │   ├── supabase_logging.py
│   │   ├── supabase_uploader.py
│   │   ├── vector_service.py
│   │   └── vector_store_init.py
│   ├── stealth_ocr.py
│   ├── stealth_ocr_testit.py
│   ├── storage/
│   │   ├── chunks/
│   │   ├── clean/
│   │   ├── logs/
│   │   ├── openai/
│   │   ├── raw/
│   │   ├── supabase_exports/
│   │   └── test_files/
│   └── utils/
│       ├── alignment_verifier.py
│       ├── audit.py
│       ├── carver.py
│       ├── env_validator.py
│       ├── __init__.py
│       ├── logger.py
│       ├── mana_engine/
│       ├── mana_trace.py
│       ├── middleware/
│       ├── offline_store.py
│       ├── ollama_client.py
│       ├── openai_client.py
│       ├── paths.py
│       ├── pro_auth.py
│       ├── reo_engine.py
│       ├── safety_guard.py
│       ├── supabase_adapter.py
│       └── supabase_client.py
├── test_intake.sh
├── test_mcp_import.py
└── nohup.out
```

**Summary:**
- **201 directories, 277 files**
- **L3 Depth** (showing up to 3 levels deep)
- Created: 15 Tīhema 2025

---

## Key Module Overview

| Module | Purpose |
|--------|---------|
| **docs/** | Documentation, guides, and architecture |
| **kaitiaki/** | AI guardianship and knowledge management |
| **mauri/** | Core state, realm, and manifest management |
| **te_ao/** | Frontend (React/Vite) |
| **te_hau/** | Backend API and services |
| **te_po/** | Data processing pipeline and AI |
| **scripts/** | Automation and testing utilities |
