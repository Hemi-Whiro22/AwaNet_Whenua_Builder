# Repository Tree

Base path: `/home/hemi-whiro/Titiraukawa/The_AwaNet/te_po`

```
te_po
├── Dockerfile
├── README.md
├── __init__.py
├── analysis
│   ├── mcp_tools_manifest.json
│   ├── mcp_tools_manifest.meta.json
│   ├── review_log_20260104_015356.md
│   ├── routes.json
│   ├── routes.md
│   ├── routes.meta.json
│   ├── routes_compact.md
│   ├── routes_compact.meta.json
│   ├── routes_summary.json
│   └── routes_summary.meta.json
├── app.py
├── assistants
│   ├── create_kitenga_whiro.py
│   └── create_qa_assistant.py
├── core
│   ├── .gitignore
│   ├── README.md
│   ├── SECURITY.md
│   ├── __init__.py
│   ├── awa_event_loop.py
│   ├── awa_gpt.py
│   ├── awa_realtime.py
│   ├── config.py
│   ├── env.example.txt
│   ├── env_loader.py
│   ├── kitenga_cards.py
│   ├── main.py
│   └── settings_loader.py
├── database
│   ├── __init__.py
│   ├── kitenga_db.py
│   ├── migrations_001_pipeline_jobs.sql
│   ├── postgres.py
│   └── supabase.py
├── diagnostics
│   ├── __init__.py
│   ├── awa_mana.py
│   ├── generate_repo_tree.py
│   ├── metadata.py
│   ├── run_repo_review.py
│   ├── sync_status.py
│   └── te_kaitiaki_o_nga_ahua_kawenga.py
├── docs
│   ├── archive
│   ├── changelogs
│   ├── diagnostics
│   │   ├── repo_tree.md
│   │   ├── review_log_20260103_221502.md
│   │   ├── review_log_20260103_221604.md
│   │   ├── routes.md
│   │   └── routes_compact.md
│   ├── diagrams
│   ├── guides
│   ├── modules
│   └── readme.md
├── kaitiaki
│   └── whiro
├── main.py
├── mauri
│   ├── context.json
│   ├── mcp_tools_manifest.json
│   ├── mcp_tools_manifest.meta.json
│   ├── routes.json
│   ├── routes.meta.json
│   ├── routes_compact.meta.json
│   ├── routes_summary.json
│   └── routes_summary.meta.json
├── mauri.py
├── migrations
│   ├── 001_create_project_state_tables.sql
│   ├── 001_realm_tables.sql
│   ├── 002_recall_logs.sql
│   └── 003_create_realms_table.sql
├── models
│   ├── __init__.py
│   ├── auth_models.py
│   ├── file_profile.py
│   ├── intake_models.py
│   ├── memory_models.py
│   ├── reo_models.py
│   └── vector_models.py
├── openai_assistants.json
├── pipeline
│   ├── __init__.py
│   ├── cards
│   │   └── card_upload_pipeline.py
│   ├── chunker
│   │   ├── __init__.py
│   │   └── chunk_engine.py
│   ├── cleaner
│   │   ├── __init__.py
│   │   └── text_cleaner.py
│   ├── custom_queue.py
│   ├── embedder
│   │   ├── __init__.py
│   │   └── embed_engine.py
│   ├── job_tracking.py
│   ├── jobs.py
│   ├── metrics.py
│   ├── ocr
│   │   ├── __init__.py
│   │   ├── ocr_engine.py
│   │   └── stealth_engine.py
│   ├── orchestrator
│   │   ├── __init__.py
│   │   └── pipeline_orchestrator.py
│   ├── research
│   │   ├── __init__.py
│   │   └── search_engine.py
│   ├── supabase_writer
│   │   ├── __init__.py
│   │   └── writer.py
│   ├── test_memory_logging.py
│   ├── test_supabase_connection.py
│   └── worker.py
├── requirements.txt
├── routes
│   ├── __init__.py
│   ├── assistant.py
│   ├── assistant_bridge.py
│   ├── assistants_meta.py
│   ├── automation.py
│   ├── awa.py
│   ├── awa_protocol.py
│   ├── cards.py
│   ├── chat.py
│   ├── cors_manager.py
│   ├── dev.py
│   ├── documents.py
│   ├── intake.py
│   ├── kitenga_backend.py
│   ├── kitenga_db.py
│   ├── kitenga_tool_router.py
│   ├── llama3.py
│   ├── logs.py
│   ├── memory.py
│   ├── metrics.py
│   ├── ocr.py
│   ├── pipeline.py
│   ├── realm_generator.py
│   ├── recall.py
│   ├── reo.py
│   ├── research.py
│   ├── roshi.py
│   ├── sell.py
│   ├── state.py
│   ├── status.py
│   └── vector.py
├── run_tests.sh
├── schema
│   ├── __init__.py
│   └── realms.py
├── schema_drift_report.json
├── scripts
│   ├── activate_table.py
│   ├── audit_supabase.py
│   ├── clear_supabase_tables.py
│   ├── export_supabase.py
│   ├── poll_vector_batches.py
│   ├── publish_state.py
│   ├── rebuild_state.py
│   ├── register_kitenga_tools.py
│   ├── smoke_test.py
│   ├── snapshot_supabase_tables.py
│   ├── start_dev.sh
│   ├── state_drift_check.py
│   ├── storage_drift_check.py
│   ├── sync_mauri_supabase.py
│   └── sync_storage_supabase.py
├── services
│   ├── __init__.py
│   ├── chat_memory.py
│   ├── local_storage.py
│   ├── memory_service.py
│   ├── ocr_service.py
│   ├── project_state_service.py
│   ├── realm_generator.py
│   ├── reo_service.py
│   ├── summary_service.py
│   ├── supabase_logging.py
│   ├── supabase_service.py
│   ├── supabase_uploader.py
│   ├── vector_service.py
│   └── vector_store_init.py
├── state
│   ├── __init__.py
│   └── read_state.py
├── state.yaml
├── stealth_ocr.py
├── stealth_ocr_testit.py
├── stealth_ocr_tests.py
├── storage
│   ├── chunks
│   │   ├── chunk_006a35fe496a4b94bf92030feb833a48.json
│   │   ├── chunk_02a8c2442c2144cda57204f8584e6154.json
│   │   ├── chunk_07a7f8ee9e334796b8003a7cf8b114af.json
│   │   ├── chunk_097de907909447ac8270c2abb6277e44.json
│   │   ├── chunk_0b16226201ee468a8e26420f54887313.json
│   │   ├── chunk_0c6d8b69446b45e5800abf765ea8dbf3.json
│   │   ├── chunk_1017fd826fcc487b829c2baf7d9bee25.json
│   │   ├── chunk_116699b5e8ff48a2bce484ec866fe053.json
│   │   ├── chunk_14073172b4194c5c973be34e881a59d4.json
│   │   ├── chunk_1413774e81d649e3811bf4bc61f12bf3.json
│   │   ├── chunk_1aaa1c6c2aea468592c3c8b89566356d.json
│   │   ├── chunk_1ee6e11a27fc4465a59d253450fac60a.json
│   │   ├── chunk_1f13f0979bca4fb9b3295712288b460a.json
│   │   ├── chunk_22ba7883bdbb4dd28615676e0b2a386f.json
│   │   ├── chunk_238476f7dec9400686195a5779dc4308.json
│   │   ├── chunk_244e32bbc190408fb5f5538c57d4e3a2.json
│   │   ├── chunk_25e6940c29e14e0bb3be1abe678b526d.json
│   │   ├── chunk_266f2a3d50c24e1b8c7847bdc978c7e7.json
│   │   ├── chunk_2a05301215ac4947b1fca71571e8af29.json
│   │   ├── chunk_2f6d334d1b0f44dbb02d7769be8f5551.json
│   │   ├── chunk_3f8f2a54f0b14bff95bd3faa6d84d01c.json
│   │   ├── chunk_413ae60b8b21409680f92e91e257c019.json
│   │   ├── chunk_46234cbe4f2e439e9eeaa9ed29413dbd.json
│   │   ├── chunk_484fe5afb3e14a9f8989d1fc9d13c920.json
│   │   ├── chunk_4d8a864dfee94b61b26ab93d8936e11e.json
│   │   ├── chunk_4ebf719134234684814d9dc937f25bf1.json
│   │   ├── chunk_597b0c983a7d482bbd459f53e5df4df5.json
│   │   ├── chunk_5c93b43d50964a0ca11ceb8c19608ccd.json
│   │   ├── chunk_62bd303250ca4846af6ec48e1f854f98.json
│   │   ├── chunk_66143e0a29834aafb88857f128f70925.json
│   │   ├── chunk_67d62fb060434a668f56f5fa55dc2dbc.json
│   │   ├── chunk_6d680a57bb9741cfa431bbab0ff1a27b.json
│   │   ├── chunk_6ddb9019ea7e40909dd858705e6cb62d.json
│   │   ├── chunk_6e9dcbf7b4e0480a8b739af42a441688.json
│   │   ├── chunk_737063909cd84090a1b17dec25861618.json
│   │   ├── chunk_77f8fcc19b154f0fa0a630f5689db604.json
│   │   ├── chunk_7a7abaf1e97b44d28a8741b66cfca978.json
│   │   ├── chunk_7c811dfb8bb946878b9e04ff11f617c0.json
│   │   ├── chunk_7e6adb2481614257a10e38dc0d00cf1c.json
│   │   ├── chunk_80a47c924de64fda9c0a31bbd8ebc620.json
│   │   ├── chunk_89d550fc9195446aa51a55650a660bb9.json
│   │   ├── chunk_8cbe42265b634cdf9f1d4a322640e149.json
│   │   ├── chunk_8dc50147401742899cc1bac29ae78b36.json
│   │   ├── chunk_8e60509315c64232b404206ed88e8c6e.json
│   │   ├── chunk_906edc53377f4f0295bd3ee9569d4ed9.json
│   │   ├── chunk_9727c42db81849bd979127bbee43e3db.json
│   │   ├── chunk_974366bf57974f7a9ce0c0fbdd661a9e.json
│   │   ├── chunk_9d707a509c9245bc96e47c5798f7e161.json
│   │   ├── chunk_9db785e4f80341fd9080e364c3cabbd7.json
│   │   ├── chunk_9ea291c9ccfc484e9b7704df3ee8a17f.json
│   │   ├── chunk_a55224d8d5ea4f2597d1597828d137c8.json
│   │   ├── chunk_a5abf6e2a8c94e01adc94b644188c309.json
│   │   ├── chunk_a7ad8df52ee04b13aa8d83c897a0f5d3.json
│   │   ├── chunk_a7c7884d16b649278131561efc4e7415.json
│   │   ├── chunk_b13270a301784c4587156994c2c51399.json
│   │   ├── chunk_b73677b637034e97afb52bf3df366033.json
│   │   ├── chunk_b7838576b4e84eebbba976d09ae7e8a1.json
│   │   ├── chunk_b91dde5f89a54d7297947bdd43fca8b3.json
│   │   ├── chunk_bb6e89f2d1834058bc3b55d9085ba196.json
│   │   ├── chunk_be4cf4d785e34b41aff2ef5e2eb9eb48.json
│   │   ├── chunk_be80a9dbacbf47a098c25915ead4af91.json
│   │   ├── chunk_c1736bb918ed4ac087a57cdedad4e523.json
│   │   ├── chunk_c53ff6e4e82c4409b9be939932b20647.json
│   │   ├── chunk_c80ef10d7d8349e6ade6dbc755421696.json
│   │   ├── chunk_c871f83aa88b4d738f9c8e5db1d65aad.json
│   │   ├── chunk_cb454c5c855c4a61a54bcd21b4d3dd07.json
│   │   ├── chunk_cf62556a44d6482194b8461388a78ceb.json
│   │   ├── chunk_d015b32a2a0d48f69b790095c05cebd5.json
│   │   ├── chunk_d373ad71facc4298ba8299d935f5e122.json
│   │   ├── chunk_d9e2511593ce41d5865a01bba56a8a46.json
│   │   ├── chunk_deee63210ade4105a0b32b393033cd7a.json
│   │   ├── chunk_e364509ac1dd400ba2323bd94df80128.json
│   │   ├── chunk_e5e5662950d14ff3a9f4dbf5ba9fe8d2.json
│   │   ├── chunk_e7971f0eee4b4690a9e2f1c68212f14c.json
│   │   ├── chunk_eadb240146ec45d89a26afbb2c4c2e34.json
│   │   ├── chunk_ec712e699130456b8dca22f931b9979a.json
│   │   ├── chunk_ef2c6165fb5149dfad230187f40b630e.json
│   │   ├── chunk_f43ab27166724a4282e34ab1b0144f27.json
│   │   ├── chunk_fa490035fc4e45d6a47f1cc3408811c4.json
│   │   ├── chunk_fd4b2881867f4174ae5b028b4303ceca.json
│   │   ├── chunk_fd7fc0fa6d034a9584633da51067cbcd.json
│   │   └── chunk_ff865c8860d54442906a28145b1affa5.json
│   ├── clean
│   ├── logs
│   │   ├── pipeline_20251224_035657_889d7df18faf4dc186bf9a72da6ea495.json
│   │   ├── pipeline_20251224_035657_88a92466b220404b8b30018ed1109eb8.json
│   │   ├── pipeline_20251224_035700_34c467aa6caf49e79bf5e9bdaec8a19d.json
│   │   ├── pipeline_20251224_035701_bfd84222bc9647b6937b14aa6377928b.json
│   │   ├── pipeline_20251224_035703_383f8e9d00d94617b28296b688617df6.json
│   │   ├── pipeline_20251224_035704_7fdf5cdfcb33465380321b3e209d1243.json
│   │   ├── pipeline_20251224_035705_0a5658ec1e88411485cffcf3b9c3af98.json
│   │   ├── pipeline_20251224_035707_52d4180f3e404930864372affc866d92.json
│   │   ├── pipeline_20251224_035708_c4a1a17f5b7a4d54b015e2da6c4a5c2f.json
│   │   ├── pipeline_20251224_035710_17b06b2ffdfc4ee986b8c84951431fc7.json
│   │   ├── pipeline_20251224_043357_1bc5e9b77809475c9a0d0c1e0b1e300b.json
│   │   ├── pipeline_20251224_043359_1358266e7c9b4a2d85ae990172d08315.json
│   │   ├── pipeline_20251224_043359_7769b30b6a0a4c7bb0e3ea2ec235b3d0.json
│   │   ├── pipeline_20251224_043401_0fb049dfb7d5409f948d0418d05c70d4.json
│   │   ├── pipeline_20251224_043402_2a9b0b24617f4fa98fe68115f8999bb3.json
│   │   ├── pipeline_20251224_043403_a658fb3af06345deb68ccc87087543aa.json
│   │   ├── pipeline_20251224_043404_8aa079c6a30149bf9dfa2340f88d2fab.json
│   │   ├── pipeline_20251224_043406_eac86f421ade4fe69b69cc04cae83604.json
│   │   ├── pipeline_20251224_043408_3f658110e5f445fbbb7df0e934d9ca30.json
│   │   ├── pipeline_20251224_043409_3d7acd25e9cc4fde9399bf667310a885.json
│   │   ├── pipeline_20251224_053113_df41a18c04e64fd7aa588029acbc0a00.json
│   │   ├── pipeline_20251224_053114_a6b11e58403945d2a6d2156a37f56c49.json
│   │   ├── pipeline_20251224_053116_35baa2b8d25d4edd8a20be42e8200058.json
│   │   ├── pipeline_20251224_053116_ad95a24755eb4eddb7e0e0afa8d54d43.json
│   │   ├── pipeline_20251224_053117_19a1218bf7d441fc8159c6659fe23ed0.json
│   │   ├── pipeline_20251224_053118_6299d0fe138b4a078dfe1ef1512ea712.json
│   │   ├── pipeline_20251224_053119_34cb50b1457f4cbbab48be3d643efc8e.json
│   │   ├── pipeline_20251224_053121_a842a824a2f3404cbc0395d5c8a3edb4.json
│   │   ├── pipeline_20251224_053122_afffc005172c4750b69c54fe715b178c.json
│   │   ├── pipeline_20251224_053123_be5c114497894309852ef46e6206c76e.json
│   │   ├── pipeline_20251224_060952_17d5d1ba39ae4fbfaff37eb41ddabc1e.json
│   │   ├── pipeline_20251224_060953_4fb659ba1b954a4b8ed6c96519ae07f4.json
│   │   ├── pipeline_20251224_060954_4d5af54ae21743f4ae4c4c8b38438132.json
│   │   ├── pipeline_20251224_060955_7671f09799704e5f87c5295365ae4e9c.json
│   │   ├── pipeline_20251224_060956_f47dfe61d9ad49f0ac303283960a40ab.json
│   │   ├── pipeline_20251224_060957_4cf03726a20240eb99a2f0bcf8c2d241.json
│   │   ├── pipeline_20251224_060958_5680d21a4027430097e210701d85605f.json
│   │   ├── pipeline_20251224_060959_a45feb2dc6a8486da1a6254510dfb454.json
│   │   ├── pipeline_20251224_061000_55fe002388f842998f36ebf78495979d.json
│   │   ├── pipeline_20251224_061001_1622df837f6b46c6aa32b2676e0114d6.json
│   │   ├── pipeline_20251224_061632_6b29b6b1f1a24bfbb67b07337918a237.json
│   │   ├── pipeline_20251224_061633_1ee6b0c49036403cbc445db54d67fdbb.json
│   │   ├── pipeline_20251224_061634_f8f015d9934e423eaaa9395511f770d7.json
│   │   ├── pipeline_20251224_061635_56fd888493d14420a3f8de9e9387fc2a.json
│   │   ├── pipeline_20251224_061636_f69c6391eb0b4561ba4a5047749c835c.json
│   │   ├── pipeline_20251224_061637_7f5f9edd56f146d98f6e743d95e0a25a.json
│   │   ├── pipeline_20251224_061638_7284d2343146482e8d8281052438e3bc.json
│   │   ├── pipeline_20251224_061639_2fedaf76005547e59c8e7b365dffe02d.json
│   │   ├── pipeline_20251224_061640_6c6636802e3847f2a95ac25608f93952.json
│   │   ├── pipeline_20251224_061641_7cae2c4dc4904b60b3facc3726f32dc4.json
│   │   ├── pipeline_20251224_072548_f52dea09632b4bb3a4982014a87ec217.json
│   │   ├── pipeline_20251224_072549_82228e93742d43dabd650f13d51af651.json
│   │   ├── pipeline_20251224_072550_e2bc3dbc64a84617b8596bf33ad655b1.json
│   │   ├── pipeline_20251224_072552_8185f617c29d457295c95836f4f3f743.json
│   │   ├── pipeline_20251224_072554_c539742b16154edb82790081569db5cb.json
│   │   ├── pipeline_20251224_072555_4504d1b4f8b94046963d6b7c97a06490.json
│   │   ├── pipeline_20251224_072557_4867737f91174d4681bb48b62cddf5da.json
│   │   ├── pipeline_20251224_072558_640c02e4b4e6437a9b0a260ef9fc9211.json
│   │   ├── pipeline_20251224_072559_a4dba2b2250948e0abb07b4c76533114.json
│   │   ├── pipeline_20251224_072600_3e5f5eeb98a542738d7d367a911d9a0d.json
│   │   ├── pipeline_20251224_072759_1f64b052b6cc4716b393bd88ee40a976.json
│   │   ├── pipeline_20251224_094818_ac37bf72174843caa1a071a06bb139d7.json
│   │   ├── pipeline_20251224_094845_9c8480628d754a84ab9845f86637bbf4.json
│   │   ├── pipeline_20251224_095845_283625644d3443e89cac42b358da5519.json
│   │   └── pipeline_20251224_095920_7f6390e47dff4351af04e75c06f5368b.json
│   ├── openai
│   │   └── koru_wolf_blue.json
│   └── raw
├── test_env_parsing.py
├── tests
│   ├── __init__.py
│   └── test_assistant_bridge.py
├── to_do.yaml
└── utils
    ├── __init__.py
    ├── alignment_verifier.py
    ├── audit.py
    ├── carver.py
    ├── env_validator.py
    ├── logger.py
    ├── mana_engine
    ├── mana_trace.py
    ├── middleware
    │   ├── __init__.py
    │   ├── auth_middleware.py
    │   └── utf8_enforcer.py
    ├── offline_store.py
    ├── ollama_client.py
    ├── openai_client.py
    ├── paths.py
    ├── pro_auth.py
    ├── recall_service.py
    ├── reo_engine.py
    ├── safety_guard.py
    ├── supabase_adapter.py
    └── supabase_client.py
```