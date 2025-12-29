You are bootstrapping a mini Te Pō realm. Always:

1. Copy `project_template/.env.template` → `.env` and set a unique `HUMAN_BEARER_KEY`.
2. Run `project_template/scripts/bootstrap.sh` to install dependencies and register Kitenga.
3. Use `project_template/STRUCTURE.md` as the canonical reference for folders and routing.
4. Deploy `te_ao` via Cloudflare Pages (`npm run build` → `dist/`).
5. (Optional) Deploy `project_template/mini_te_po` to your chosen backend platform once ready.
6. Confirm connectivity with `project_template/scripts/health_check.sh`.
7. Rotate bearer tokens per realm and register them in the main Te Pō backend.
8. Use `project_template/template.config.json` as the single source of placeholders/secrets for automation (e.g., Te Hau CLI).***
