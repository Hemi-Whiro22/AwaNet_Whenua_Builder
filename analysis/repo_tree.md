# Repository Tree

Base path: `/home/hemi-whiro/Titiraukawa/The_Awa_Network`

```
The_Awa_Network
├── .cloudflared
│   ├── cert.pem
│   ├── how_to_run.md
│   ├── kitenga_whiro.json
│   ├── kitenga_whiro_den.yml
│   └── kitenga_whiro_public.yml
├── .continue
│   ├── config.json
│   └── prompts
│       └── power_run.md
├── .devcontainer
│   ├── Dockerfile
│   ├── README.md
│   ├── cloudflare_start.sh
│   ├── devcontainer.json
│   └── post_create.sh
├── .dockerignore
├── .env
├── .env.example
├── .env.kitenga_whiro
├── .env.render
├── .github
├── .gitignore
├── .pytest_cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v
│       └── cache
│           ├── lastfailed
│           └── nodeids
├── .python-version
├── .vscode
│   ├── extension.json
│   └── settings.json
├── .well-known
│   ├── ai-plugin.json
│   ├── openapi-core.json
│   └── public_openai_tools.json
├── LICENSE
├── analysis
│   ├── REPO_REVIEW_PROMPT.md
│   ├── __init__.py
│   ├── generate_repo_tree.py
│   ├── kaitiaki_context_sync.py
│   ├── kaitiaki_sync_20251223_204003.json
│   ├── kaitiaki_sync_20251223_204519.json
│   ├── kaitiaki_sync_20251223_204811.json
│   ├── live_samples
│   │   ├── sample.htm
│   │   ├── sample.html
│   │   ├── sample.jpeg
│   │   ├── sample.jpg
│   │   ├── sample.json
│   │   ├── sample.m4a
│   │   ├── sample.md
│   │   ├── sample.mp3
│   │   ├── sample.pdf
│   │   ├── sample.png
│   │   ├── sample.txt
│   │   ├── sample.wav
│   │   ├── sample.webp
│   │   └── sample.yaml
│   ├── mcp_tools_manifest.json
│   ├── mcp_tools_manifest.meta.json
│   ├── metadata.py
│   ├── payload_map.json
│   ├── payload_map.md
│   ├── payload_map.meta.json
│   ├── repo_tree.md
│   ├── review_log_20251223_151258.md
│   ├── review_log_20251223_151317.md
│   ├── review_log_20251223_172105.md
│   ├── review_log_20251223_175703.md
│   ├── review_log_20251223_182404.md
│   ├── review_log_20251223_184502.md
│   ├── review_log_20251223_184900.md
│   ├── review_log_20251223_192144.md
│   ├── review_log_20251223_192419.md
│   ├── review_log_20251223_195213.md
│   ├── review_log_20251223_211602.md
│   ├── review_log_20251223_214940.md
│   ├── review_log_20251223_215559.md
│   ├── review_log_20251223_220052.md
│   ├── review_log_20251223_220648.md
│   ├── review_log_20251223_220709.md
│   ├── review_log_20251223_220748.md
│   ├── review_log_20251223_221424.md
│   ├── review_log_20251223_224348.md
│   ├── review_log_20251223_224437.md
│   ├── review_log_20251224_005222.md
│   ├── review_log_20251224_010346.md
│   ├── review_log_20251224_094908.md
│   ├── review_log_20251224_095546.md
│   ├── routes.json
│   ├── routes.md
│   ├── routes.meta.json
│   ├── routes_compact.md
│   ├── routes_compact.meta.json
│   ├── routes_summary.json
│   ├── routes_summary.meta.json
│   ├── run_repo_review.py
│   ├── sync_status.py
│   └── te_kaitiaki_o_nga_ahua_kawenga.py
├── app
│   └── openapi-core.json
├── boot.sh
├── detect_encoding.py
├── diagnostic_20251222_131548.log
├── docker-compose.yaml
├── docs
│   ├── CONTEXT_PACK.md
│   ├── CORS_AND_AUTH.md
│   ├── PROJECT_STATE_SYNC.md
│   ├── architecture
│   │   ├── MCP_ALIGNMENT.md
│   │   ├── MCP_TEST_REPORT.md
│   │   └── PROJECT_SCAN.md
│   ├── archived_architecture
│   │   ├── awa_structure.json
│   │   ├── codex_alignment_prompt.md
│   │   ├── drift_protection.json
│   │   ├── mauri_anchor.md
│   │   ├── naming_conventions.json
│   │   └── versioning_rules.json
│   ├── archived_documents
│   │   ├── INDEX.md
│   │   ├── md
│   │   │   ├── doc1.md
│   │   │   ├── doc10.md
│   │   │   ├── doc11.md
│   │   │   ├── doc12.md
│   │   │   ├── doc2.md
│   │   │   ├── doc3.md
│   │   │   ├── doc4.md
│   │   │   ├── doc5.md
│   │   │   ├── doc6.md
│   │   │   ├── doc7.md
│   │   │   ├── doc8.md
│   │   │   ├── doc9.md
│   │   │   └── mauri
│   │   │       └── archived
│   │   │           └── legacy_configs
│   │   ├── pdfs
│   │   │   ├── 1993_05_01_Ian_Lawlor_Wharekaho_Site_Sur.pdf
│   │   │   ├── 2019-Wananga-Te-Hikoi-ki-te-mautere-o-Matakana.pdf
│   │   │   ├── 2021-NZHC-1968.pdf
│   │   │   ├── 3628Taranaki-Iwi-Initialled-Deed-of-Settlement-7-Jul-2015.pdf
│   │   │   ├── 3_1_2_yeaRs_oF_FIeLdwoRK_aRCHaeoLoGy_at.pdf
│   │   │   ├── 56-65-1-PB.pdf
│   │   │   ├── 7_Ownership_or_Tenure_A_Case_Study_of_Tr.pdf
│   │   │   ├── AJHR_1936_I_G-06b_0011 (2).pdf
│   │   │   ├── A_possible_pre_Tasman_canoe_landing_site.pdf
│   │   │   ├── Appendix-18-Iwi-Interests-Report.pdf
│   │   │   ├── Archaeology_of_the_Bay_of_Plenty.pdf
│   │   │   ├── Archaeology_of_the_Bay_of_Plenty_Archaeo.pdf
│   │   │   ├── BOE-Rawiri-Hemi-G2.pdf
│   │   │   ├── Breaking_the_Barrier_Maori_religious_and.pdf
│   │   │   ├── Cultural_Resource_Management_Archaeology.pdf
│   │   │   ├── Customary_Maori_Freshwater_Fishing_Right.pdf
│   │   │   ├── Dual_Naming_Recognising_Landscape_Ident.pdf
│   │   │   ├── Enduring_traditions_and_contested_author.pdf
│   │   │   ├── Food_Fighting_and_Fortifications_in_Pre.pdf
│   │   │   ├── Harmsworth_G_R_2005_Good_practice_guidel.pdf
│   │   │   ├── How_Finance_Colonised_Aotearoa_A_Concise.pdf
│   │   │   ├── Huria-MatengaRecollections.pdf
│   │   │   ├── IN_THE_ENVIRONMENT_COURT.pdf
│   │   │   ├── Important_Privacy_Notice.pdf
│   │   │   ├── Indigenous_M_and_257_ori_values_and_pers.pdf
│   │   │   ├── Kaikoura_historical_background.pdf
│   │   │   ├── Lawlor_I_T_9_Mar_2018_Statement_of_evide.pdf
│   │   │   ├── Leach_B_F_2003_Depletion_and_Loss_of_the.pdf
│   │   │   ├── MCYST_5072181854_1_251003_143911 (1).pdf
│   │   │   ├── MCYST_5072181854_1_251003_143911.pdf
│   │   │   ├── Maori_oral_histories_and_the_impact_of_t.pdf
│   │   │   ├── Maori_oral_histories_and_the_recurring_i.pdf
│   │   │   ├── Mobile_space_times_and_the_rescaling_of (1).pdf
│   │   │   ├── Mobile_space_times_and_the_rescaling_of.pdf
│   │   │   ├── NgaHekenga20130920.pdf
│   │   │   ├── Payslip.pdf
│   │   │   ├── Pits_and_kumara_agriculture_in_the_South.pdf
│   │   │   ├── Pushing_the_process_A_whanau_journey_thr.pdf
│   │   │   ├── README.md
│   │   │   ├── Repatriation_reconciliation_and_the_inve.pdf
│   │   │   ├── Report_on_the_development_and_use_of_GIS.pdf
│   │   │   ├── Restitution_or_a_Loss_to_Science_Underst.pdf
│   │   │   ├── Rural_Areas_within_Twenty_Territorial_Lo.pdf
│   │   │   ├── Scanned_20250911-0133.pdf
│   │   │   ├── Sedentism_subsistence_and_socio_politica.pdf
│   │   │   ├── Settlement_Patterns_and_Indigenous_Agenc.pdf
│   │   │   ├── THE_CONTROL_ENVIRONMENTAL_SUSTAINABILITY (1).pdf
│   │   │   ├── THE_CONTROL_ENVIRONMENTAL_SUSTAINABILITY (2).pdf
│   │   │   ├── THE_CONTROL_ENVIRONMENTAL_SUSTAINABILITY.pdf
│   │   │   ├── Takapuneke_Conservation_Report.pdf
│   │   │   ├── Te-Mana-o-te-Wai-Factsheet (1).pdf
│   │   │   ├── Te-Mana-o-te-Wai-Factsheet.pdf
│   │   │   ├── Te_Awanui_Kaitiaki_Trust_Deed.pdf
│   │   │   ├── Te_Hokinga_Mai_O_Nga_Tupuna_Maori_Perspe.pdf
│   │   │   ├── Te_Mauri_o_te_Kaitiaki_Exploring_Te_Ao_M.pdf
│   │   │   ├── Te_Pareihe_and_the_Migration_to_Nukutaur.pdf
│   │   │   ├── Te_Tau_Ihu_Statutory_Acknowledgements.pdf
│   │   │   ├── Te_Whakatau_Kaupapa_Ngai_Tahu_Resource_M.pdf
│   │   │   ├── Te_Whakatau_Kaupapa_resource_mgmt_strate.pdf
│   │   │   ├── The_House_as_Ancestor_A_Tale_of_Maori_So.pdf
│   │   │   ├── The_Otago_Peninsula.pdf
│   │   │   ├── The_past_is_always_in_front_of_us_Locat.pdf
│   │   │   ├── Tribal_Membership_Governance_in_Australi.pdf
│   │   │   ├── Wayne_Hemi_Trustee_Profile.pdf
│   │   │   ├── Whakapapa_PDF_Snippets.csv
│   │   │   ├── Williams, Madi_Final PhD Thesis.pdf
│   │   │   ├── jps_admin,+jps_v127_sept_meihana_bradley.pdf
│   │   │   ├── pdf_tools.py
│   │   │   ├── qmc_creditlimit_explained.pdf
│   │   │   ├── thesis_access.pdf
│   │   │   └── uctions of knowledge that
│   │   │       └── nhave had detr.sty
│   │   └── sql
│   │       ├── dbs_cards.sql
│   │       ├── kitenga_schema.sql
│   │       ├── rongohia.sql
│   │       ├── supabase_canonical.md
│   │       ├── supabase_drop_candidates.sql
│   │       ├── supabase_policies.sql
│   │       └── supabase_schema.sql
│   ├── context
│   │   ├── CONTEXT.md
│   │   ├── MAURI_CONTEXT.md
│   │   ├── PROJECT_TEMPLATE_STRUCTURE.md
│   │   └── README.md
│   ├── guides
│   │   ├── DEVELOPMENT.md
│   │   ├── GUARDIANS.md
│   │   ├── LLAMA3.md
│   │   └── MCP_SETUP.md
│   ├── markdown_catalog.md
│   ├── realms
│   │   ├── README.md
│   │   ├── TE_PO
│   │   │   ├── PIPELINE_JOB_TRACKING_IMPLEMENTATION_SUMMARY.md
│   │   │   ├── PIPELINE_JOB_TRACKING_POSTGRES.md
│   │   │   ├── PIPELINE_JOB_TRACKING_QUICK_START.md
│   │   │   ├── QUEUE_MODE_SWITCH.md
│   │   │   ├── RENDER_POSTGRES_DEPLOYMENT.md
│   │   │   ├── TEPO_RENDER_DEPLOYMENT.md
│   │   │   ├── TEPO_RENDER_QUICK_START.md
│   │   │   ├── TE_PO_ANALYSIS_COMPLETE.md
│   │   │   ├── TE_PO_ARCHITECTURE_QUICKREF.md
│   │   │   ├── TE_PO_EXECUTIVE_SUMMARY.md
│   │   │   ├── TE_PO_MULTI_PROJECT_SETUP.md
│   │   │   ├── TE_PO_QUICK_START_CHECKLIST.md
│   │   │   ├── TE_PO_STANDALONE_INDEX.md
│   │   │   ├── TE_PO_STANDALONE_SCAN.md
│   │   │   └── TE_PO_VISUAL_ARCHITECTURE.md
│   │   └── TE_PO.md
│   ├── reference
│   │   ├── API_CONTRACTS.md
│   │   ├── GLOSSARY.md
│   │   └── STATE_MANAGEMENT.md
│   ├── root
│   │   ├── COMPLETE_WORKFLOW.md
│   │   ├── INDEX.md
│   │   ├── REALM_GENERATOR.md
│   │   ├── REALM_ISOLATION.md
│   │   └── REALM_SYSTEM.md
│   └── root_docs
│       ├── CHANGES_SUMMARY.md
│       ├── GPT_BUILD_INTEGRATION.md
│       ├── MASTER_SUMMARY.md
│       ├── POSTGRES_JOB_TRACKING_COMMIT_CHECKLIST.md
│       ├── QUEUE_MODE_CHECKLIST.md
│       ├── QUEUE_MODE_IMPLEMENTATION.md
│       ├── README.md
│       ├── REALM_GENERATOR_QUICKSTART.md
│       ├── REALM_ISOLATION_SUMMARY.md
│       ├── REFACTOR_INDEX.md
│       ├── REFACTOR_SUMMARY.md
│       ├── RENDER_COMMIT_READY.md
│       ├── REPOSITORY_STRUCTURE.md
│       ├── RUN_DEV_QUEUE_MODE.md
│       ├── TEPO_VERIFICATION.md
│       └── move_log.md
├── gpt_connect.yaml
├── kaitiaki
│   ├── AWAOS_MASTER_PROMPT.md
│   ├── HAIKU_CODEX.md
│   ├── README.md
│   ├── SNAPSHOT_COMPLETE_SYSTEM.md
│   ├── haiku
│   │   ├── HAIKU_CODEX.md
│   │   ├── QUICKSTART.md
│   │   ├── README.md
│   │   ├── TOKEN_ECONOMY.md
│   │   ├── haiku_carving_log.jsonl
│   │   ├── haiku_manifest.json
│   │   └── haiku_state.json
│   ├── kitenga_codex
│   │   ├── .env.kaitiaki
│   │   ├── __init__.py
│   │   ├── bootstrap.py
│   │   ├── kitenga_manifest.json
│   │   ├── logs
│   │   │   ├── awa_tunnel.log
│   │   │   ├── cloudflared.log
│   │   │   ├── kitenga_mcp.log
│   │   │   └── te_po.log
│   │   ├── start_kitenga.py
│   │   ├── state
│   │   └── tools
│   │       ├── file_tools.py
│   │       └── supabase_tools.py
│   └── te_kitenga_nui
│       └── te_kitenga_nui_manifest.json
├── kitenga_mcp
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── INDEX.md
│   ├── INTEGRATION_GUIDE.md
│   ├── INTEGRATION_SUMMARY.md
│   ├── Kitenga-Main-Js-main.code-workspace
│   ├── MIGRATION_FROM_FASTAPI.md
│   ├── QUICK_REFERENCE.md
│   ├── README.md
│   ├── SUMMARY.txt
│   ├── __init__.py
│   ├── app_server.py
│   ├── cloudflare
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   ├── config.yaml
│   ├── fastmcp_config.py
│   ├── git
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   ├── mcpserver.yaml
│   ├── memory.py
│   ├── openai
│   │   ├── openapi.json
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   ├── pipeline.py
│   ├── render
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   ├── shared
│   │   ├── __init__.py
│   │   ├── macrons.py
│   │   ├── memory.py
│   │   └── security.py
│   ├── supabase
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   ├── tepo
│   │   ├── openai_tools.json
│   │   ├── schema.json
│   │   ├── server.py
│   │   └── tools.json
│   └── tools
│       ├── README.md
│       ├── __init__.py
│       ├── manifest.json
│       ├── manifests
│       │   ├── cloudflare_tools.json
│       │   ├── git_commands_hardened.json
│       │   ├── openai_tools.json
│       │   ├── render_commands_hardened.json
│       │   ├── supabase_tools.json
│       │   └── tepo_tools.json
│       ├── openai.json
│       ├── openai_assistants.json
│       ├── openai_tools.json
│       └── render_service_map_template.json
├── logs
├── mauri
│   ├── .env.example
│   ├── archived
│   │   ├── .devcontainer.zip
│   │   ├── kaitiaki-intake
│   │   │   └── active
│   │   │       └── test_document_1764996338.md
│   │   ├── kaitiaki_legacy
│   │   │   ├── .gitkeep
│   │   │   ├── Services
│   │   │   │   ├── Cultural_Audit
│   │   │   │   ├── Ingest
│   │   │   │   ├── Reo
│   │   │   │   ├── Summaries
│   │   │   │   └── Vector_Search
│   │   │   ├── __init__.py
│   │   │   ├── config
│   │   │   ├── kaitiaki.py
│   │   │   ├── manifests
│   │   │   └── state
│   │   │       └── log_2025-11-30.json
│   │   ├── legacy_configs
│   │   │   ├── mauriold.json
│   │   │   └── openai.json
│   │   ├── mauri_legacy
│   │   │   ├── ProjectManifest.yaml
│   │   │   ├── README.txt
│   │   │   ├── config.py
│   │   │   ├── docs
│   │   │   │   ├── architecture
│   │   │   │   │   ├── ARCHITECTURE_DIAGRAM.md
│   │   │   │   │   ├── STRUCTURE_EXTENSION_SCAN.md
│   │   │   │   │   └── structure.md
│   │   │   │   ├── backend
│   │   │   │   ├── misc
│   │   │   │   │   ├── DELIVERY.md
│   │   │   │   │   └── SUPABASE_LINK.md
│   │   │   │   ├── reference
│   │   │   │   │   ├── CHECKLIST.md
│   │   │   │   │   ├── CLARIFICATION.md
│   │   │   │   │   ├── COMMANDS.sh.md
│   │   │   │   │   ├── DEEP_SCAN_ANALYSIS.md
│   │   │   │   │   ├── QUICK_REFERENCE.md
│   │   │   │   │   ├── STAGES_EXPLAINED.md
│   │   │   │   │   ├── TEPUNA_QUICK_REFERENCE.md
│   │   │   │   │   └── chat.md
│   │   │   │   └── ui
│   │   │   │       └── IWI_PORTAL_GUIDE.md
│   │   │   ├── global_env.json
│   │   │   ├── manifest
│   │   │   │   ├── glyph_manifest.json
│   │   │   │   └── kaitiaki_tree.json
│   │   │   ├── manifest.yaml
│   │   │   ├── prompts
│   │   │   │   ├── Respectful Scanner& Gaurdian.yaml
│   │   │   │   ├── Truth.yaml
│   │   │   │   ├── env directive.yaml
│   │   │   │   ├── enviroment_best_pratices.yaml
│   │   │   │   ├── final_codex_alignment.yaml
│   │   │   │   ├── manifest_controller.yaml
│   │   │   │   ├── manifest_maintainer.yaml
│   │   │   │   ├── restore_paths.yaml
│   │   │   │   └── verify_tiwhanawhana.yaml
│   │   │   ├── seals
│   │   │   │   ├── whakapapa.hash
│   │   │   │   └── whakapapa_seal.json
│   │   │   └── trace.json
│   │   ├── scripts
│   │   │   ├── __init__.py
│   │   │   ├── audit_encoding.py
│   │   │   ├── dev_autostart.sh
│   │   │   ├── generate_test_files_tepo.py
│   │   │   ├── init_env.sh
│   │   │   ├── query_tables.py
│   │   │   ├── sanitize_utf8.py
│   │   │   ├── scan_te_puna_schema.py
│   │   │   └── startup_cli.py
│   │   └── shared
│   │       ├── __init__.py
│   │       ├── awa_bus
│   │       │   ├── __init__.py
│   │       │   └── awa_events.py
│   │       └── mauri
│   │           └── mauri_stone.json
│   ├── kaitiaki
│   │   ├── kaitiaki_signatures.json
│   │   ├── model_registry.json
│   │   ├── model_registry_raw.json
│   │   └── te_kitenga_nui.json
│   ├── kaitiaki_templates
│   │   ├── KITENGA_CONFIGURATION.md
│   │   ├── README.md
│   │   ├── haiku.yaml
│   │   ├── kitenga_whiro.yaml
│   │   └── te_kitenga_nui.yaml
│   ├── openai_gpt.json
│   ├── prompts
│   │   ├── anaylisis.md
│   │   ├── gpt_context.md
│   │   └── state_update.md
│   ├── realms
│   │   ├── realm_lock.json
│   │   ├── researcher
│   │   │   └── manifest.json
│   │   ├── te_ao
│   │   │   ├── te_ao_anchor.json
│   │   │   └── te_ao_manifest.json
│   │   ├── te_hau
│   │   │   ├── te_hau_anchor.json
│   │   │   └── te_hau_manifest.json
│   │   ├── te_po
│   │   │   ├── den_manifest.json
│   │   │   ├── te_po_anchor.json
│   │   │   └── te_po_manifest.json
│   │   └── translator
│   │       └── manifest.json
│   ├── scripts
│   │   └── compile_kaitiaki.py
│   ├── services
│   │   ├── kitenga_backend.config.json
│   │   └── kitenga_whiro.config.json
│   ├── state
│   │   ├── supabase_schema.json
│   │   ├── supabase_tables.json
│   │   ├── te_ao_state.json
│   │   ├── te_hau_state.json
│   │   ├── te_po_carving_log.jsonl
│   │   └── te_po_state.json
│   └── te_kete
│       ├── den_manifest.yaml
│       ├── domain_map.json
│       ├── glossary.json
│       ├── kitenga_whiro.manifest.json
│       ├── load_manifest.py
│       └── pipeline_map.json
├── nohup.out
├── openai_tools.json
├── realm.json
├── realms
│   ├── .gitkeep
│   └── README.md
├── render.yaml
├── requirements.txt
├── run_dev.sh
├── scripts
│   ├── analysis_sync_status.py
│   ├── git_commit_pipeline.py
│   ├── kaitiaki_sanity.py
│   ├── live_tool_tester.py
│   ├── pipeline_sample_runner.py
│   ├── sync_storage_to_supabase.py
│   └── tests
│       ├── README.md
│       ├── generate_markdown_catalog.py
│       ├── run_all_tests.sh
│       ├── start_and_test.sh
│       ├── test_cors_auth.sh
│       ├── test_intake.sh
│       ├── test_live_tools.sh
│       ├── test_mcp_import.py
│       ├── test_pipeline_samples.sh
│       ├── test_queue_mode.py
│       ├── test_queue_mode_lite.py
│       ├── test_run_dev_queue_mode.sh
│       ├── test_state_sync.sh
│       ├── test_supabase_client.py
│       ├── test_supabase_connection.py
│       └── test_template.py
├── start_up.sh
├── te_ao
│   ├── .env
│   ├── Dockerfile
│   ├── README.md
│   ├── REFACTORED.md
│   ├── __init__.py
│   ├── config
│   │   ├── README.md
│   │   └── tools.json
│   ├── dev.log
│   ├── dist
│   │   ├── assets
│   │   │   ├── index-DcJLr3fP.js
│   │   │   ├── index-aCqboj1f.css
│   │   │   ├── inter-cyrillic-400-normal-HOLc17fK.woff
│   │   │   ├── inter-cyrillic-400-normal-obahsSVq.woff2
│   │   │   ├── inter-cyrillic-ext-400-normal-BQZuk6qB.woff2
│   │   │   ├── inter-cyrillic-ext-400-normal-DQukG94-.woff
│   │   │   ├── inter-greek-400-normal-B4URO6DV.woff2
│   │   │   ├── inter-greek-400-normal-q2sYcFCs.woff
│   │   │   ├── inter-greek-ext-400-normal-DGGRlc-M.woff2
│   │   │   ├── inter-greek-ext-400-normal-KugGGMne.woff
│   │   │   ├── inter-latin-400-normal-C38fXH4l.woff2
│   │   │   ├── inter-latin-400-normal-CyCys3Eg.woff
│   │   │   ├── inter-latin-ext-400-normal-77YHD8bZ.woff
│   │   │   ├── inter-latin-ext-400-normal-C1nco2VV.woff2
│   │   │   ├── inter-vietnamese-400-normal-Bbgyi5SW.woff
│   │   │   ├── inter-vietnamese-400-normal-DMkecbls.woff2
│   │   │   └── stone-koru-lv9Nht-r-Iv9Nht-r.png
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   └── koru.svg
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.cjs
│   ├── public
│   │   ├── favicon.ico
│   │   └── koru.svg
│   ├── src
│   │   ├── App.jsx
│   │   ├── assets
│   │   │   ├── AwaNet_Koru.svg
│   │   │   ├── favicon.ico
│   │   │   ├── koru.svg
│   │   │   ├── koru_spiral.svg
│   │   │   ├── stone-koru-lv9Nht-r.png
│   │   │   └── stone-koru.png
│   │   ├── components
│   │   │   ├── chat
│   │   │   │   ├── ChatInput.jsx
│   │   │   │   ├── ChatMessage.jsx
│   │   │   │   ├── HeaderBar.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── ToolResultCard.jsx
│   │   │   └── ui
│   │   │       ├── button.jsx
│   │   │       └── card.jsx
│   │   ├── data
│   │   │   └── public_schema_te_puna.json
│   │   ├── devui
│   │   │   ├── ChunkPanel.jsx
│   │   │   ├── CleanPanel.jsx
│   │   │   ├── DevCockpit.jsx
│   │   │   ├── DevMenu.jsx
│   │   │   ├── EmbedPanel.jsx
│   │   │   ├── OCRPanel.jsx
│   │   │   ├── OpenAIResults.jsx
│   │   │   ├── SummaryPanel.jsx
│   │   │   └── TranslatePanel.jsx
│   │   ├── hooks
│   │   │   ├── useApi.js
│   │   │   ├── useAwa.ts
│   │   │   ├── useEvents.ts
│   │   │   └── useIwiPortal.js
│   │   ├── index.css
│   │   ├── layouts
│   │   │   └── KitengaShell.jsx
│   │   ├── main.js
│   │   ├── main.jsx
│   │   ├── mauri.js
│   │   └── panels
│   │       ├── AdminPanel.jsx
│   │       ├── ApiTestPanel.jsx
│   │       ├── ChatPanel.jsx
│   │       ├── CulturalScanPanel.jsx
│   │       ├── IwiPortalPanel.jsx
│   │       ├── KaitiakiBuilderPanel.jsx
│   │       ├── KitengaDevHub.jsx
│   │       ├── KitengaPanel.jsx
│   │       ├── MemoryPanel.jsx
│   │       ├── OCRPanel.jsx
│   │       ├── PronunciationPanel.jsx
│   │       ├── RealmHealthPanel.tsx
│   │       ├── RealmStarterPanel.jsx
│   │       ├── ReoPanel.jsx
│   │       ├── ResearchPanel.tsx
│   │       ├── SummaryPanel.jsx
│   │       ├── TranslatePanel.jsx
│   │       ├── TranslationPanel.jsx
│   │       └── VectorSearchPanel.jsx
│   ├── start_frontend.sh
│   ├── state
│   │   └── state.yaml
│   ├── tailwind.config.cjs
│   └── vite.config.js
├── te_hau
│   ├── .env
│   ├── Dockerfile
│   ├── README.md
│   ├── __init__.py
│   ├── app.py
│   ├── awa
│   │   ├── __init__.py
│   │   ├── bus.py
│   │   ├── router.py
│   │   └── whakapapa.py
│   ├── cli
│   │   ├── __init__.py
│   │   ├── awanui.py
│   │   ├── commands
│   │   │   ├── __init__.py
│   │   │   ├── health.py
│   │   │   ├── ingest.py
│   │   │   ├── keys.py
│   │   │   ├── pronounce.py
│   │   │   ├── reo.py
│   │   │   ├── vector.py
│   │   │   └── whakapapa.py
│   │   ├── devui.py
│   │   ├── hau.py
│   │   ├── start_whakairo.py
│   │   └── utils.py
│   ├── config
│   │   └── hau_config.yaml
│   ├── core
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── branching.py
│   │   ├── context.py
│   │   ├── fs.py
│   │   ├── healing.py
│   │   ├── infra.py
│   │   ├── kaitiaki.py
│   │   ├── orchestrator.py
│   │   ├── pipeline.py
│   │   ├── protocol.py
│   │   ├── renderer.py
│   │   ├── secrets.py
│   │   ├── security.py
│   │   └── supabase.py
│   ├── mauri
│   │   ├── __init__.py
│   │   ├── glyph.py
│   │   └── seal.py
│   ├── models
│   │   └── __init__.py
│   ├── nohup.out
│   ├── project_template
│   │   ├── .devcontainer
│   │   │   ├── Dockerfile
│   │   │   ├── devcontainer.json
│   │   │   └── post_create.sh
│   │   ├── .env.template
│   │   ├── .github
│   │   │   └── workflows
│   │   │       ├── cloudflare-pages.yml
│   │   │       └── health-check.yml
│   │   ├── .vscode
│   │   │   ├── launch.json
│   │   │   └── settings.json
│   │   ├── STRUCTURE.md
│   │   ├── archetypes.json
│   │   ├── config
│   │   │   ├── proxy.toml
│   │   │   └── realm.json
│   │   ├── docs
│   │   │   ├── CLI_PLAN.md
│   │   │   ├── MASTER_PROMPT.md
│   │   │   └── secrets.md
│   │   ├── mauri
│   │   │   ├── kaitiaki_templates
│   │   │   │   ├── .gitkeep
│   │   │   │   └── realm.yaml
│   │   │   ├── realm_lock.json
│   │   │   └── state
│   │   │       └── den_manifest.json
│   │   ├── requirements.txt
│   │   ├── scripts
│   │   │   ├── bootstrap.sh
│   │   │   ├── health_check.sh
│   │   │   ├── new_realm.sh
│   │   │   └── seed_context.py
│   │   ├── te_ao
│   │   │   ├── index.html
│   │   │   └── src
│   │   │       ├── App.css
│   │   │       ├── App.jsx
│   │   │       ├── index.css
│   │   │       └── main.jsx
│   │   ├── te_hau
│   │   │   ├── __init__.py
│   │   │   └── cli.py
│   │   ├── te_po_proxy
│   │   │   ├── bootstrap.py
│   │   │   ├── main.py
│   │   │   └── requirements.txt
│   │   └── template.config.json
│   ├── requirements.txt
│   ├── scripts
│   │   ├── generate_realm.py
│   │   ├── generate_realm_old.py
│   │   ├── realm_ui.py
│   │   └── verify_realm_isolation.sh
│   ├── sdk
│   │   ├── __init__.py
│   │   ├── compiler.py
│   │   ├── loader.py
│   │   └── types.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── awa_bus.py
│   │   ├── kaitiaki_store.py
│   │   ├── mauri.py
│   │   ├── sound.py
│   │   └── tepo_api.py
│   ├── start_tehau.sh
│   ├── state.yaml
│   ├── translator
│   │   ├── __init__.py
│   │   ├── ahiatoa.py
│   │   ├── core.py
│   │   └── glossary.py
│   ├── util
│   │   └── __init__.py
│   ├── verbs
│   │   ├── __init__.py
│   │   ├── awa.py
│   │   ├── branch.py
│   │   ├── cluster.py
│   │   ├── context.py
│   │   ├── deploy.py
│   │   ├── evolve.py
│   │   ├── glyph.py
│   │   ├── heal.py
│   │   ├── infra.py
│   │   ├── init.py
│   │   ├── kaitiaki.py
│   │   ├── new.py
│   │   ├── pipeline.py
│   │   ├── seal.py
│   │   ├── security.py
│   │   └── translate.py
│   └── whakairo_codex
│       ├── README.md
│       ├── logs
│       │   └── README.md
│       ├── mcp
│       │   └── manifest.yaml
│       ├── record_carve.py
│       ├── state
│       │   └── README.md
│       ├── sync_carver_context.py
│       └── whakairo_manifest.json
├── te_po
│   ├── Dockerfile
│   ├── README.md
│   ├── __init__.py
│   ├── app.py
│   ├── assistants
│   │   ├── create_kitenga_whiro.py
│   │   └── create_qa_assistant.py
│   ├── core
│   │   ├── .gitignore
│   │   ├── README.md
│   │   ├── SECURITY.md
│   │   ├── __init__.py
│   │   ├── awa_event_loop.py
│   │   ├── awa_gpt.py
│   │   ├── awa_realtime.py
│   │   ├── config.py
│   │   ├── env.example.txt
│   │   ├── env_loader.py
│   │   ├── kitenga_cards.py
│   │   ├── main.py
│   │   └── settings_loader.py
│   ├── db
│   │   ├── __init__.py
│   │   ├── kitenga_db.py
│   │   ├── migrations_001_pipeline_jobs.sql
│   │   ├── postgres.py
│   │   └── supabase.py
│   ├── diagnostics
│   │   └── awa_mana.py
│   ├── main.py
│   ├── mauri.py
│   ├── mcp_tools
│   │   └── project_state.py
│   ├── migrations
│   │   ├── 001_create_project_state_tables.sql
│   │   ├── 001_realm_tables.sql
│   │   ├── 002_recall_logs.sql
│   │   └── 003_create_realms_table.sql
│   ├── models
│   │   ├── __init__.py
│   │   ├── auth_models.py
│   │   ├── file_profile.py
│   │   ├── intake_models.py
│   │   ├── memory_models.py
│   │   ├── reo_models.py
│   │   └── vector_models.py
│   ├── modules
│   ├── openai_assistants.json
│   ├── openai_tools.json
│   ├── pipeline
│   │   ├── __init__.py
│   │   ├── cards
│   │   │   └── card_upload_pipeline.py
│   │   ├── chunker
│   │   │   ├── __init__.py
│   │   │   └── chunk_engine.py
│   │   ├── cleaner
│   │   │   ├── __init__.py
│   │   │   └── text_cleaner.py
│   │   ├── custom_queue.py
│   │   ├── embedder
│   │   │   ├── __init__.py
│   │   │   └── embed_engine.py
│   │   ├── job_tracking.py
│   │   ├── jobs.py
│   │   ├── metrics.py
│   │   ├── ocr
│   │   │   ├── __init__.py
│   │   │   ├── ocr_engine.py
│   │   │   └── stealth_engine.py
│   │   ├── orchestrator
│   │   │   ├── __init__.py
│   │   │   └── pipeline_orchestrator.py
│   │   ├── research
│   │   │   ├── __init__.py
│   │   │   └── search_engine.py
│   │   ├── supabase_writer
│   │   │   ├── __init__.py
│   │   │   └── writer.py
│   │   ├── test_memory_logging.py
│   │   ├── test_supabase_connection.py
│   │   └── worker.py
│   ├── requirements.txt
│   ├── routes
│   │   ├── __init__.py
│   │   ├── assistant.py
│   │   ├── assistant_bridge.py
│   │   ├── assistants_meta.py
│   │   ├── awa.py
│   │   ├── awa_protocol.py
│   │   ├── cards.py
│   │   ├── chat.py
│   │   ├── cors_manager.py
│   │   ├── dev.py
│   │   ├── documents.py
│   │   ├── intake.py
│   │   ├── kitenga_backend.py
│   │   ├── kitenga_db.py
│   │   ├── kitenga_tool_router.py
│   │   ├── llama3.py
│   │   ├── logs.py
│   │   ├── memory.py
│   │   ├── metrics.py
│   │   ├── ocr.py
│   │   ├── pipeline.py
│   │   ├── realm_generator.py
│   │   ├── recall.py
│   │   ├── reo.py
│   │   ├── research.py
│   │   ├── roshi.py
│   │   ├── sell.py
│   │   ├── state.py
│   │   ├── status.py
│   │   └── vector.py
│   ├── run_tests.sh
│   ├── schema
│   │   ├── __init__.py
│   │   └── realms.py
│   ├── schema_drift_report.json
│   ├── scripts
│   │   ├── activate_table.py
│   │   ├── audit_supabase.py
│   │   ├── clear_supabase_tables.py
│   │   ├── export_supabase.py
│   │   ├── poll_vector_batches.py
│   │   ├── publish_state.py
│   │   ├── rebuild_state.py
│   │   ├── register_kitenga_tools.py
│   │   ├── smoke_test.py
│   │   ├── snapshot_supabase_tables.py
│   │   ├── start_dev.sh
│   │   ├── state_drift_check.py
│   │   ├── storage_drift_check.py
│   │   ├── sync_mauri_supabase.py
│   │   └── sync_storage_supabase.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── chat_memory.py
│   │   ├── local_storage.py
│   │   ├── memory_service.py
│   │   ├── ocr_service.py
│   │   ├── project_state_service.py
│   │   ├── realm_generator.py
│   │   ├── reo_service.py
│   │   ├── summary_service.py
│   │   ├── supabase_logging.py
│   │   ├── supabase_service.py
│   │   ├── supabase_uploader.py
│   │   ├── vector_service.py
│   │   └── vector_store_init.py
│   ├── state
│   │   ├── __init__.py
│   │   └── read_state.py
│   ├── state.yaml
│   ├── stealth_ocr.py
│   ├── stealth_ocr_testit.py
│   ├── stealth_ocr_tests.py
│   ├── storage
│   │   ├── chunks
│   │   │   ├── chunk_006a35fe496a4b94bf92030feb833a48.json
│   │   │   ├── chunk_02a8c2442c2144cda57204f8584e6154.json
│   │   │   ├── chunk_07a7f8ee9e334796b8003a7cf8b114af.json
│   │   │   ├── chunk_097de907909447ac8270c2abb6277e44.json
│   │   │   ├── chunk_0c6d8b69446b45e5800abf765ea8dbf3.json
│   │   │   ├── chunk_1017fd826fcc487b829c2baf7d9bee25.json
│   │   │   ├── chunk_116699b5e8ff48a2bce484ec866fe053.json
│   │   │   ├── chunk_14073172b4194c5c973be34e881a59d4.json
│   │   │   ├── chunk_1413774e81d649e3811bf4bc61f12bf3.json
│   │   │   ├── chunk_1aaa1c6c2aea468592c3c8b89566356d.json
│   │   │   ├── chunk_1ee6e11a27fc4465a59d253450fac60a.json
│   │   │   ├── chunk_1f13f0979bca4fb9b3295712288b460a.json
│   │   │   ├── chunk_22ba7883bdbb4dd28615676e0b2a386f.json
│   │   │   ├── chunk_238476f7dec9400686195a5779dc4308.json
│   │   │   ├── chunk_244e32bbc190408fb5f5538c57d4e3a2.json
│   │   │   ├── chunk_25e6940c29e14e0bb3be1abe678b526d.json
│   │   │   ├── chunk_266f2a3d50c24e1b8c7847bdc978c7e7.json
│   │   │   ├── chunk_2a05301215ac4947b1fca71571e8af29.json
│   │   │   ├── chunk_2f6d334d1b0f44dbb02d7769be8f5551.json
│   │   │   ├── chunk_3f8f2a54f0b14bff95bd3faa6d84d01c.json
│   │   │   ├── chunk_46234cbe4f2e439e9eeaa9ed29413dbd.json
│   │   │   ├── chunk_484fe5afb3e14a9f8989d1fc9d13c920.json
│   │   │   ├── chunk_4d8a864dfee94b61b26ab93d8936e11e.json
│   │   │   ├── chunk_4ebf719134234684814d9dc937f25bf1.json
│   │   │   ├── chunk_597b0c983a7d482bbd459f53e5df4df5.json
│   │   │   ├── chunk_5c93b43d50964a0ca11ceb8c19608ccd.json
│   │   │   ├── chunk_66143e0a29834aafb88857f128f70925.json
│   │   │   ├── chunk_67d62fb060434a668f56f5fa55dc2dbc.json
│   │   │   ├── chunk_6d680a57bb9741cfa431bbab0ff1a27b.json
│   │   │   ├── chunk_6ddb9019ea7e40909dd858705e6cb62d.json
│   │   │   ├── chunk_6e9dcbf7b4e0480a8b739af42a441688.json
│   │   │   ├── chunk_737063909cd84090a1b17dec25861618.json
│   │   │   ├── chunk_7a7abaf1e97b44d28a8741b66cfca978.json
│   │   │   ├── chunk_7e6adb2481614257a10e38dc0d00cf1c.json
│   │   │   ├── chunk_80a47c924de64fda9c0a31bbd8ebc620.json
│   │   │   ├── chunk_89d550fc9195446aa51a55650a660bb9.json
│   │   │   ├── chunk_8cbe42265b634cdf9f1d4a322640e149.json
│   │   │   ├── chunk_8dc50147401742899cc1bac29ae78b36.json
│   │   │   ├── chunk_8e60509315c64232b404206ed88e8c6e.json
│   │   │   ├── chunk_906edc53377f4f0295bd3ee9569d4ed9.json
│   │   │   ├── chunk_9727c42db81849bd979127bbee43e3db.json
│   │   │   ├── chunk_9d707a509c9245bc96e47c5798f7e161.json
│   │   │   ├── chunk_9db785e4f80341fd9080e364c3cabbd7.json
│   │   │   ├── chunk_9ea291c9ccfc484e9b7704df3ee8a17f.json
│   │   │   ├── chunk_a55224d8d5ea4f2597d1597828d137c8.json
│   │   │   ├── chunk_a5abf6e2a8c94e01adc94b644188c309.json
│   │   │   ├── chunk_a7ad8df52ee04b13aa8d83c897a0f5d3.json
│   │   │   ├── chunk_a7c7884d16b649278131561efc4e7415.json
│   │   │   ├── chunk_b13270a301784c4587156994c2c51399.json
│   │   │   ├── chunk_b73677b637034e97afb52bf3df366033.json
│   │   │   ├── chunk_b91dde5f89a54d7297947bdd43fca8b3.json
│   │   │   ├── chunk_bb6e89f2d1834058bc3b55d9085ba196.json
│   │   │   ├── chunk_be4cf4d785e34b41aff2ef5e2eb9eb48.json
│   │   │   ├── chunk_c1736bb918ed4ac087a57cdedad4e523.json
│   │   │   ├── chunk_c53ff6e4e82c4409b9be939932b20647.json
│   │   │   ├── chunk_c80ef10d7d8349e6ade6dbc755421696.json
│   │   │   ├── chunk_c871f83aa88b4d738f9c8e5db1d65aad.json
│   │   │   ├── chunk_cb454c5c855c4a61a54bcd21b4d3dd07.json
│   │   │   ├── chunk_cf62556a44d6482194b8461388a78ceb.json
│   │   │   ├── chunk_d015b32a2a0d48f69b790095c05cebd5.json
│   │   │   ├── chunk_d373ad71facc4298ba8299d935f5e122.json
│   │   │   ├── chunk_d9e2511593ce41d5865a01bba56a8a46.json
│   │   │   ├── chunk_deee63210ade4105a0b32b393033cd7a.json
│   │   │   ├── chunk_e5e5662950d14ff3a9f4dbf5ba9fe8d2.json
│   │   │   ├── chunk_e7971f0eee4b4690a9e2f1c68212f14c.json
│   │   │   ├── chunk_eadb240146ec45d89a26afbb2c4c2e34.json
│   │   │   ├── chunk_ec712e699130456b8dca22f931b9979a.json
│   │   │   ├── chunk_ef2c6165fb5149dfad230187f40b630e.json
│   │   │   ├── chunk_f43ab27166724a4282e34ab1b0144f27.json
│   │   │   ├── chunk_fa490035fc4e45d6a47f1cc3408811c4.json
│   │   │   ├── chunk_fd4b2881867f4174ae5b028b4303ceca.json
│   │   │   ├── chunk_fd7fc0fa6d034a9584633da51067cbcd.json
│   │   │   └── chunk_ff865c8860d54442906a28145b1affa5.json
│   │   ├── clean
│   │   ├── logs
│   │   │   ├── pipeline_20251224_035657_889d7df18faf4dc186bf9a72da6ea495.json
│   │   │   ├── pipeline_20251224_035657_88a92466b220404b8b30018ed1109eb8.json
│   │   │   ├── pipeline_20251224_035700_34c467aa6caf49e79bf5e9bdaec8a19d.json
│   │   │   ├── pipeline_20251224_035701_bfd84222bc9647b6937b14aa6377928b.json
│   │   │   ├── pipeline_20251224_035703_383f8e9d00d94617b28296b688617df6.json
│   │   │   ├── pipeline_20251224_035704_7fdf5cdfcb33465380321b3e209d1243.json
│   │   │   ├── pipeline_20251224_035705_0a5658ec1e88411485cffcf3b9c3af98.json
│   │   │   ├── pipeline_20251224_035707_52d4180f3e404930864372affc866d92.json
│   │   │   ├── pipeline_20251224_035708_c4a1a17f5b7a4d54b015e2da6c4a5c2f.json
│   │   │   ├── pipeline_20251224_035710_17b06b2ffdfc4ee986b8c84951431fc7.json
│   │   │   ├── pipeline_20251224_043357_1bc5e9b77809475c9a0d0c1e0b1e300b.json
│   │   │   ├── pipeline_20251224_043359_1358266e7c9b4a2d85ae990172d08315.json
│   │   │   ├── pipeline_20251224_043359_7769b30b6a0a4c7bb0e3ea2ec235b3d0.json
│   │   │   ├── pipeline_20251224_043401_0fb049dfb7d5409f948d0418d05c70d4.json
│   │   │   ├── pipeline_20251224_043402_2a9b0b24617f4fa98fe68115f8999bb3.json
│   │   │   ├── pipeline_20251224_043403_a658fb3af06345deb68ccc87087543aa.json
│   │   │   ├── pipeline_20251224_043404_8aa079c6a30149bf9dfa2340f88d2fab.json
│   │   │   ├── pipeline_20251224_043406_eac86f421ade4fe69b69cc04cae83604.json
│   │   │   ├── pipeline_20251224_043408_3f658110e5f445fbbb7df0e934d9ca30.json
│   │   │   ├── pipeline_20251224_043409_3d7acd25e9cc4fde9399bf667310a885.json
│   │   │   ├── pipeline_20251224_053113_df41a18c04e64fd7aa588029acbc0a00.json
│   │   │   ├── pipeline_20251224_053114_a6b11e58403945d2a6d2156a37f56c49.json
│   │   │   ├── pipeline_20251224_053116_35baa2b8d25d4edd8a20be42e8200058.json
│   │   │   ├── pipeline_20251224_053116_ad95a24755eb4eddb7e0e0afa8d54d43.json
│   │   │   ├── pipeline_20251224_053117_19a1218bf7d441fc8159c6659fe23ed0.json
│   │   │   ├── pipeline_20251224_053118_6299d0fe138b4a078dfe1ef1512ea712.json
│   │   │   ├── pipeline_20251224_053119_34cb50b1457f4cbbab48be3d643efc8e.json
│   │   │   ├── pipeline_20251224_053121_a842a824a2f3404cbc0395d5c8a3edb4.json
│   │   │   ├── pipeline_20251224_053122_afffc005172c4750b69c54fe715b178c.json
│   │   │   ├── pipeline_20251224_053123_be5c114497894309852ef46e6206c76e.json
│   │   │   ├── pipeline_20251224_060952_17d5d1ba39ae4fbfaff37eb41ddabc1e.json
│   │   │   ├── pipeline_20251224_060953_4fb659ba1b954a4b8ed6c96519ae07f4.json
│   │   │   ├── pipeline_20251224_060954_4d5af54ae21743f4ae4c4c8b38438132.json
│   │   │   ├── pipeline_20251224_060955_7671f09799704e5f87c5295365ae4e9c.json
│   │   │   ├── pipeline_20251224_060956_f47dfe61d9ad49f0ac303283960a40ab.json
│   │   │   ├── pipeline_20251224_060957_4cf03726a20240eb99a2f0bcf8c2d241.json
│   │   │   ├── pipeline_20251224_060958_5680d21a4027430097e210701d85605f.json
│   │   │   ├── pipeline_20251224_060959_a45feb2dc6a8486da1a6254510dfb454.json
│   │   │   ├── pipeline_20251224_061000_55fe002388f842998f36ebf78495979d.json
│   │   │   ├── pipeline_20251224_061001_1622df837f6b46c6aa32b2676e0114d6.json
│   │   │   ├── pipeline_20251224_061632_6b29b6b1f1a24bfbb67b07337918a237.json
│   │   │   ├── pipeline_20251224_061633_1ee6b0c49036403cbc445db54d67fdbb.json
│   │   │   ├── pipeline_20251224_061634_f8f015d9934e423eaaa9395511f770d7.json
│   │   │   ├── pipeline_20251224_061635_56fd888493d14420a3f8de9e9387fc2a.json
│   │   │   ├── pipeline_20251224_061636_f69c6391eb0b4561ba4a5047749c835c.json
│   │   │   ├── pipeline_20251224_061637_7f5f9edd56f146d98f6e743d95e0a25a.json
│   │   │   ├── pipeline_20251224_061638_7284d2343146482e8d8281052438e3bc.json
│   │   │   ├── pipeline_20251224_061639_2fedaf76005547e59c8e7b365dffe02d.json
│   │   │   ├── pipeline_20251224_061640_6c6636802e3847f2a95ac25608f93952.json
│   │   │   ├── pipeline_20251224_061641_7cae2c4dc4904b60b3facc3726f32dc4.json
│   │   │   ├── pipeline_20251224_072548_f52dea09632b4bb3a4982014a87ec217.json
│   │   │   ├── pipeline_20251224_072549_82228e93742d43dabd650f13d51af651.json
│   │   │   ├── pipeline_20251224_072550_e2bc3dbc64a84617b8596bf33ad655b1.json
│   │   │   ├── pipeline_20251224_072552_8185f617c29d457295c95836f4f3f743.json
│   │   │   ├── pipeline_20251224_072554_c539742b16154edb82790081569db5cb.json
│   │   │   ├── pipeline_20251224_072555_4504d1b4f8b94046963d6b7c97a06490.json
│   │   │   ├── pipeline_20251224_072557_4867737f91174d4681bb48b62cddf5da.json
│   │   │   ├── pipeline_20251224_072558_640c02e4b4e6437a9b0a260ef9fc9211.json
│   │   │   ├── pipeline_20251224_072559_a4dba2b2250948e0abb07b4c76533114.json
│   │   │   ├── pipeline_20251224_072600_3e5f5eeb98a542738d7d367a911d9a0d.json
│   │   │   ├── pipeline_20251224_072759_1f64b052b6cc4716b393bd88ee40a976.json
│   │   │   ├── pipeline_20251224_094818_ac37bf72174843caa1a071a06bb139d7.json
│   │   │   └── pipeline_20251224_094845_9c8480628d754a84ab9845f86637bbf4.json
│   │   ├── openai
│   │   │   └── koru_wolf_blue.json
│   │   └── raw
│   ├── templates
│   │   └── realm_template
│   │       ├── .env.template
│   │       ├── README.md
│   │       ├── config
│   │       │   └── realm.yaml
│   │       ├── docs
│   │       │   └── QUICKSTART.md
│   │       └── mauri
│   │           └── state.json
│   ├── test_env_parsing.py
│   ├── tests
│   │   ├── __init__.py
│   │   └── test_assistant_bridge.py
│   ├── to_do.yaml
│   └── utils
│       ├── __init__.py
│       ├── alignment_verifier.py
│       ├── audit.py
│       ├── carver.py
│       ├── env_validator.py
│       ├── logger.py
│       ├── mana_engine
│       ├── mana_trace.py
│       ├── middleware
│       │   ├── __init__.py
│       │   ├── auth_middleware.py
│       │   └── utf8_enforcer.py
│       ├── offline_store.py
│       ├── ollama_client.py
│       ├── openai_client.py
│       ├── paths.py
│       ├── pro_auth.py
│       ├── recall_service.py
│       ├── reo_engine.py
│       ├── safety_guard.py
│       ├── supabase_adapter.py
│       └── supabase_client.py
└── tepo_mcp_server.py
```