You are operating inside "The Awa Network".
The canonical source of truth is located at /mauri.
Read mauri/mauri_anchor, then realms/*_anchor.json, then kaitiaki_signatures.json.

Folder meaning:
- te_po = backend engines (guardian: Whiro)
- te_hau = cli/automation (guardian: Whirimatea)
- te_ao = ui/dashboard (guardian: Papatuanuku)
- projects/<name> = standalone systems that inherit Awa structure

Rules:
- No drift from the Mauri structure.
- No cross-contamination between realms.
- te_po never contains UI.
- te_ao never contains backend logic.
- te_hau never modifies mauri.
- All new files must match the naming conventions in mauri/architecture.

Always check Mauri first.
Always align changes to Mauri before writing code.
