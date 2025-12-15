# Te Hau CLI Plan

This template is designed to be consumed by the Te Hau CLI. When the CLI gains the `new-project` command it should:

1. Copy `te_hau/project_template/` to the target directory.
2. Read `template.config.json` to know which placeholders and secrets to collect.
3. Run `scripts/new_realm.sh` with the gathered inputs (non-interactively).
4. Optionally run `scripts/bootstrap.sh` to install deps/register Kitenga.
5. Initialize git, create the first commit, and (optionally) set a remote.
6. Print a secrets checklist (matching `docs/secrets.md`) so the operator can store them in GitHub/Cloudflare.

### Required inputs
- Realm/project name.
- Cloudflare hostname, tunnel ID, tunnel name, Pages project.
- Pipeline token + bearer token (generated automatically).
- Optional: Supabase + OpenAI keys.

### Outputs
- Configured `.env` + `.env.template`.
- Updated `config/realm.json`, `config/proxy.toml`, `.github/workflows/cloudflare-pages.yml`.
- Git repo ready for push.
