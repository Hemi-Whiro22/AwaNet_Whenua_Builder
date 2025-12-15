# 🧪 DevContainer Runtime

The devcontainer keeps Te Pō + Te Hau SDK development consistent across laptops, Codespaces, and CI. It now wires in the `te_hau/project_template` so you can spin up SDK projects without manual bootstrapping.

---

## 📦 Folder Highlights
```text
.devcontainer/
├── devcontainer.json      # Container definition + features
├── Dockerfile             # Base Ubuntu image with tooling
├── post_create.sh         # Installs Python deps + editable Te Hau + te_ao npm packages
└── cloudflare_start.sh    # Helper to force DNS + launch cloudflared tunnel locally
```

## ⚙️ Post-create workflow
`post_create.sh` runs automatically after the container starts:
1. Upgrades `pip`.
2. Installs root `requirements.txt` plus `te_hau` in editable mode.
3. Loads any extra SDK deps from `te_hau/requirements.txt`.
4. Runs `npm install` inside `te_ao/` so the frontend is ready to build.

## 🧩 SDK project template
- Canonical template lives at `te_hau/project_template/` (mirrors `sdk_project_template` repo).
- `project_template/template.config.json` lists every placeholder + secret the future Te Hau CLI must fill.
- Scripts:
  - `project_template/scripts/new_realm.sh` prompts for realm name, Cloudflare tunnel, Render hostnames, etc.
  - `project_template/scripts/bootstrap.sh` installs deps and runs the MCP bootstrap.
  - `project_template/scripts/health_check.sh` pings the backend with the generated bearer token.

## 🌐 Cloudflare / Render automation
- `.github/workflows/cloudflare-pages.yml` and `render.yml` ship with placeholders (project name, service ID) so Te Hau CLI can push directly to Cloudflare Pages + Render.
- `project_template/config/proxy.toml` stores tunnel + service routing so the CLI only has to edit one file.

## 🤝 Contributing
When you change SDK bootstrap steps or template requirements, update this README and `post_create.sh` so new devcontainers stay in sync.***
