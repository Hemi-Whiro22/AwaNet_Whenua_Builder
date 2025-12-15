# Mauri — Source of Truth for The Awa Network

This folder defines the canonical structure, naming rules, kaitiaki signatures,
pipeline maps and drift-protection for the entire Awa system.

All IDEs, agents or automation must read Mauri first.

Realms:
- te_po: backend engines, pipeline, analysis, processing
- te_hau: cli, workers, automation, scripts
- te_ao: ui, dashboards, web surfaces

Projects live under /projects/<name> and may contain their own realm versions.

Mauri governs naming, structure, pipeline design, encoding, and kaitiaki roles.
