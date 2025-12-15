# 📚 Awa Network Documentation

**Last Updated:** 2025-01-13 | **Version:** 1.0.0

Start here for navigation. All documentation is consolidated into core topics below.

## 🎯 Quick Links by Role

**I want to...**

- **Create a new realm** → [REALM_SYSTEM.md](./REALM_SYSTEM.md#creating-realms)
- **Understand the architecture** → [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Set up my dev environment** → [DEVELOPMENT.md](./DEVELOPMENT.md)
- **Work with Kaitiaki agents** → [KAITIAKI.md](./KAITIAKI.md)
- **Use the SDK compiler** → [SDK.md](./SDK.md)
- **Deploy to production** → [DEPLOYMENT.md](./DEPLOYMENT.md)
- **Fix an issue** → [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## 📖 Core Documentation

### [ARCHITECTURE.md](./ARCHITECTURE.md)
**System design and components**
- Three realms: Te Pō (backend), Te Ao (frontend), Te Hau (CLI)
- Mauri (state/knowledge)
- How they interact
- Technology stack

### [REALM_SYSTEM.md](./REALM_SYSTEM.md)
**Realm generation and isolation**
- Creating new realms via Web UI
- Realm isolation (DevContainers, environment separation)
- Realm structure and components
- Best practices

### [SDK.md](./SDK.md)
**SDK compiler and templates**
- Kaitiaki YAML templates
- Compilation process (YAML → JSON)
- Agent templates (Haiku, Kitenga, Te Kitenga Nui)
- Using the SDK in realms

### [KAITIAKI.md](./KAITIAKI.md)
**Agent system**
- What Kaitiaki agents are
- Agent roles and personas
- System prompts and capabilities
- State management

### [DEVELOPMENT.md](./DEVELOPMENT.md)
**Local development**
- Setting up dev environment
- Running services locally
- Testing realms
- Debugging tips

### [DEPLOYMENT.md](./DEPLOYMENT.md)
**Production deployment**
- Deploying to cloud (Render, Cloudflare)
- Environment configuration
- Scaling considerations
- Monitoring

### [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
**Common issues and solutions**
- DevContainer problems
- Realm isolation issues
- SDK compiler errors
- Performance issues

---

## 🗂️ What's Where

| Path | Purpose | Type |
|------|---------|------|
| `/docs/` | **All documentation** | Markdown |
| `/mauri/` | **JSON context state only** | JSON files |
| `/te_hau/` | **SDK, CLI, generators** | Python |
| `/te_po/` | **Main backend** | Python/FastAPI |
| `/te_ao/` | **Main frontend** | React/Vite |
| `/[realm_name]/` | **Generated realms** | Complete project |

---

## 📋 Documentation Rules

To prevent drift and confusion:

1. **Single source of truth** - Each topic has ONE document
2. **No duplicate docs** - If it exists elsewhere, link to it instead
3. **Version at top** - "Last Updated: YYYY-MM-DD | Version: X.Y.Z"
4. **Delete old docs** - If replacing an old doc, delete it immediately
5. **Link from INDEX** - All docs reachable from this page
6. **Update, don't add** - When docs need updating, modify the existing doc

---

## 🔄 Common Tasks

### Generate a new realm
```bash
cd /workspaces/The_Awa_Network/te_hau/scripts
python3 realm_ui.py
# Then http://localhost:8888
```
See: [REALM_SYSTEM.md](./REALM_SYSTEM.md#creating-realms)

### Start development environment
```bash
cd /workspaces/The_Awa_Network
# Open in VS Code with devcontainer
```
See: [DEVELOPMENT.md](./DEVELOPMENT.md)

### Compile Kaitiaki agents
```bash
python mauri/scripts/compile_kaitiaki.py --agent all
```
See: [SDK.md](./SDK.md)

### Deploy to production
See: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## 📞 Questions?

Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) first, then refer to the relevant core document.

**This is the single source of truth for Awa Network documentation.**
