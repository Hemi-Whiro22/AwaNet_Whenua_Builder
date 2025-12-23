# Helper for emitting Awa events
async def emit_awa_event(event_type: str, payload: dict, source: str = "kitenga", trace_id: str = None):
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    event = {
        "type": event_type,
        "source": source,
        "trace_id": trace_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    # You can add logic here to send the event to a webhook, log, etc.
    print(f"🌊 Emitting Awa event: {event_type} ({trace_id})")


# --- Top-level imports ---
import os
import json
import logging
import glob
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from te_po.utils.middleware.auth_middleware import apply_bearer_middleware

# --- Helper functions ---
async def embed_text(text):
    # TODO: Replace with real embedding logic
    return [0.0] * 1536

async def call_render_api(path, method="GET"):
    return {"status": "not_implemented", "path": path, "method": method}

async def log_tool_usage(domain, command, input_data, result, caller_meta):
    return str(uuid.uuid4())

def load_tool_manifests():
    base = Path(__file__).parent / "tools" / "manifests"
    merged = {}
    manifest_paths = list(base.glob("*.json"))
    root_manifest = Path(__file__).parent / "tools" / "manifest.json"
    if root_manifest.exists():
        manifest_paths.append(root_manifest)

    for path in manifest_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logging.warning(f"⚠️ Failed to load {path}: {e}")
            continue

        if isinstance(data, dict) and "tools" in data and "version" in data:
            domain = data.get("domain") or path.stem
            merged.setdefault(domain, {"tools": []})
            merged[domain]["tools"].extend(data.get("tools", []))
            continue

        for domain, content in data.items():
            if domain not in merged:
                merged[domain] = {"tools": []}
            if isinstance(content, dict) and "tools" in content:
                merged[domain]["tools"].extend(content["tools"])

    logging.info(f"✅ Loaded {len(merged)} tool domains from manifests")
    return merged

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO_ROOT
TOOLS_MANIFEST = load_tool_manifests()
OPENAPI_CORE_FILE = SCHEMA_DIR / "kitenga_mcp" / "openapi-core.json"

def create_app():
    import json, logging, glob, uuid, asyncio, datetime
    from pathlib import Path
    from typing import Optional
    from fastapi import FastAPI, HTTPException, Request, Header, status
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    try:
        import httpx
    except ImportError:
        httpx = None

    # Load config variables
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    VECTORS_TABLE = os.getenv("VECTORS_TABLE", "kitenga_vectors")
    SUPABASE_SCHEMA = os.getenv("SUPABASE_SCHEMA", "kitenga")
    RENDER_API_KEY = os.getenv("RENDER_API_KEY")
    RENDER_API_BASE = os.getenv("RENDER_API_BASE", "https://api.render.com/v1")
    SERVICE_START_TIME = datetime.datetime.utcnow()
    PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")

    app = FastAPI(
        title="Kitenga MCP Server",
        version="1.1.0",
        description="Core memory, tools, and protocol management for AwaNet and GPT orchestration."
    )
    apply_bearer_middleware(app)

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Auth middleware ---
    @app.middleware("http")
    async def verify_auth(request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
            token = auth_header.replace("Bearer ", "").strip()
            valid_tokens = [
                PIPELINE_TOKEN,
                os.getenv("RENDER_API_KEY"),
                os.getenv("GITHUB_TOKEN"),
                os.getenv("SUPABASE_SERVICE_KEY")
            ]
            if token not in valid_tokens:
                raise HTTPException(status_code=403, detail="Unauthorized: Invalid token.")
        response = await call_next(request)
        return response

    # --- Debug routes ---
    @app.get("/debug/routes", tags=["Debug"])
    async def debug_routes():
        return [{"path": r.path, "methods": list(r.methods)} for r in app.routes]

    # --- Minimal AWA diagnostic ---
    @app.post("/awa/loop/test", tags=["AWA"])
    async def awa_loop_test():
            return {
                "status": "ok",
                "message": "AWA loop test successful",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

    # --- MCP health ---
    @app.get("/health", tags=["MCP"])
    async def health():
            return {
                "status": "ok",
                "message": "Kitenga MCP operational",
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

    # --- Add more routes here as needed ---    # --------------------------------------------------------
    # 📥 /awa/protocol/event — inbound AwaNet → Kitenga
    # --------------------------------------------------------
    @app.post("/awa/protocol/event", tags=["AWA"])
    async def receive_awa_event(request: Request):
        data = await request.json()
        print(f"📥 Received Awa event: {data.get('type')} ({data.get('trace_id')})")

        # Example: handle a reauth or memory ping event from AwaNet
        if data.get("type") == "reauth_request":
            asyncio.create_task(emit_awa_event("reauth_ack", {"status": "ok"}, source="kitenga", trace_id=data.get("trace_id")))

            return {
                "status": "ok",
                "message": f"Received event {data.get('type')}",
                "event_type": data.get("type"),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

    # --------------------------------------------------------
    # 🌊 Awa Protocol Event Sync
    # --------------------------------------------------------
    AWA_NET_URL = os.getenv("AWA_NET_URL", "https://tiwhanawhana-backend.onrender.com")
    event_log = []

    # (Removed duplicate emit_awa_event definition)

    # --------------------------------------------------------
    # 🧪 /awa/memory/debug — inspect recent memory vectors
    # --------------------------------------------------------
    @app.get("/awa/memory/debug", tags=["AWA"])
    async def memory_debug():
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
                return {
                    "status": "disabled",
                    "message": "Supabase not configured.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{SUPABASE_URL}/rest/v1/{VECTORS_TABLE}?order=timestamp.desc&limit=5",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
                }
            )
        return {
            "status": "ok",
            "data": {"recent_vectors": r.json()},
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    # --------------------------------------------------------
    # 🔍 /awa/memory/search — vector similarity search
    # --------------------------------------------------------
    @app.post("/awa/memory/search", tags=["AWA"])
    async def search_memory(request: Request):
        data = await request.json()
        query = data.get("query")
        top_k = data.get("top_k", 5)
        threshold = data.get("threshold", 0.7)

        if not query:
                return JSONResponse(status_code=400, content={
                    "status": "error",
                    "message": "Missing 'query' in body.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })

        vector = await embed_text(query)

        # Call Supabase RPC function or REST vector search endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/match_vectors",
                headers={
                    "apikey": SUPABASE_SERVICE_ROLE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "query_embedding": vector,
                    "match_threshold": threshold,
                    "match_count": top_k,
                    "schema_name": SUPABASE_SCHEMA,
                    "table_name": VECTORS_TABLE
                }
            )
        return {
            "status": "ok",
            "data": response.json(),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    # --------------------------------------------------------
    # 📝 /awa/memory/add — add memory with embedding
    # --------------------------------------------------------
    @app.post("/awa/memory/add", tags=["AWA"])
    async def add_memory(request: Request):
        data = await request.json()
        content = data.get("content")
        metadata = data.get("metadata", {})
        trace_id = metadata.get("trace_id") or str(uuid.uuid4())

        if not content:
                return JSONResponse(status_code=400, content={
                    "status": "error",
                    "message": "Missing 'content' in body.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })

        # 1️⃣ Generate embedding
        vector = await embed_text(content)

        # 2️⃣ Insert into Supabase
        entry = {
            "trace_id": trace_id,
            "content": content,
            "metadata": metadata,
            "embedding": vector,
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{SUPABASE_URL}/rest/v1/{VECTORS_TABLE}",
                    headers={
                        "apikey": SUPABASE_SERVICE_ROLE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=entry,
                )
            # Emit protocol event after successful memory add
            await emit_awa_event("memory_added", entry, trace_id=trace_id)
            return {
                "status": "ok",
                "data": {"trace_id": trace_id},
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        except Exception as e:
            return JSONResponse(status_code=500, content={
                "status": "error",
                "message": f"Failed to save memory: {e}",
                "timestamp": datetime.datetime.utcnow().isoformat()
            })

    # --------------------------------------------------------
    # 💚 ROUTES (Root, MCP)
    # --------------------------------------------------------
    @app.get("/", tags=["Root"])
    async def root():
        """Root status route."""
        return {
            "status": "online",
            "message": "Kia ora — Kitenga MCP Core is running.",
            "routes": [
                "/mcp/health",
                "/mcp/tools/list",
                "/mcp/tools/describe",
                "/mcp/tools/call",
                "/mcp/memory/ping",
                "/mcp/reauth"
            ]
        }

    @app.get("/health", tags=["MCP"])
    async def health_check():
        """Render/GPT health check."""
        return {
            "status": "alive",
            "service": "Kitenga MCP Core",
            "kaitiaki": "Whiro",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "env": {
                "lang": os.getenv("LANG", "C.UTF-8"),
                "lc_all": os.getenv("LC_ALL", "C.UTF-8")
            }
        }

    @app.get("/tools/list", tags=["MCP"])
    async def list_tools_manifest():
        """List all loaded tool domains and their tools from merged manifest."""
        return {
            "status": "ok",
            "kaitiaki": "Kitenga Whiro",
            "tools": TOOLS_MANIFEST
        }

    def _schema_response():
        if not OPENAPI_CORE_FILE.exists():
            raise HTTPException(status_code=404, detail="OpenAPI core schema missing.")
        headers = {
            "X-Realm-Name": "Te Pō Assistant",
            "X-Realm-Owner": "AwaNet",
            "X-Realm-Version": "1.0.0"
        }
        return FileResponse(
            OPENAPI_CORE_FILE,
            media_type="application/json",
            headers=headers
        )

    @app.get("/openapi-core.json", include_in_schema=False)
    async def openapi_core():
        return _schema_response()

    @app.get("/.well-known/openapi-core.json", include_in_schema=False)
    async def openapi_core_well_known():
        return _schema_response()

    @app.get("/tools/describe", tags=["MCP"])
    async def describe_tools():
        if not TOOLS_MANIFEST:
            raise HTTPException(status_code=404, detail="No tools loaded in manifest.")
        description = {
            domain: [t["name"] for t in data["tools"]]
            for domain, data in TOOLS_MANIFEST.items()
        }
        return {"status": "success", "tools": description, "domains": list(description.keys())}

    @app.post("/tools/call", tags=["MCP"])
    async def call_tool(request: Request):
        data = await request.json()
        domain = data.get("domain")
        command = data.get("command") or data.get("tool")  # backward-compatible
        input_data = data.get("input", {})
        caller_meta = data.get("caller") or {"origin": "unknown"}

        if not domain or not command:
                return JSONResponse(status_code=400, content={
                    "status": "error",
                    "message": "Missing 'domain' or 'command' in request body.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })

        domain_data = TOOLS_MANIFEST.get(domain)
        if not domain_data:
                return JSONResponse(status_code=404, content={
                    "status": "error",
                    "message": f"Domain '{domain}' not found in tools manifest.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })

        tool_def = next((t for t in domain_data.get("tools", []) if t["name"] == command), None)
        if not tool_def:
                return JSONResponse(status_code=404, content={
                    "status": "error",
                    "message": f"Command '{command}' not found in '{domain}' tools.",
                    "timestamp": datetime.datetime.utcnow().isoformat()
                })

        # Live Render API integration
        try:
            if domain == "render":
                if command == "render_list_services":
                    result = await call_render_api("/services")
                elif command == "render_get_service":
                    service_id = input_data.get("service_id")
                    result = await call_render_api(f"/services/{service_id}")
                elif command == "render_deploy":
                    service_id = input_data.get("service_id")
                    result = await call_render_api(f"/services/{service_id}/deploys", method="POST")
                else:
                        return JSONResponse(status_code=400, content={
                            "status": "error",
                            "message": f"Unsupported Render command: {command}",
                            "timestamp": datetime.datetime.utcnow().isoformat()
                        })
            else:
                result = {"status": "pending", "message": f"No live handler for {domain}.{command}"}
        except Exception as e:
            result = {"status": "error", "message": str(e)}

        trace_id = await log_tool_usage(domain, command, input_data, result, caller_meta)
        headers = {"X-Trace-ID": trace_id}
        return JSONResponse(content={
            "status": "ok",
            "data": result,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }, headers=headers)

    @app.get("/memory/ping", tags=["MCP"])
    async def memory_ping():
        uptime = (datetime.datetime.utcnow() - SERVICE_START_TIME).total_seconds()
        health = {"uptime_seconds": uptime, "supabase_ok": False, "render_ok": False}

                    # Import or define all required globals for routes
                    # (Removed block with global and setup logic; handled at module level)
        # Supabase check
        if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.get(f"{SUPABASE_URL}/rest/v1/", headers={"apikey": SUPABASE_SERVICE_ROLE_KEY})
                    if r.status_code in (200, 401, 404):
                        health["supabase_ok"] = True
            except Exception:
                pass

        # Render check
        if RENDER_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    r = await client.get(f"{RENDER_API_BASE}/services", headers={"Authorization": f"Bearer {RENDER_API_KEY}"})
                    if r.status_code == 200:
                        health["render_ok"] = True
            except Exception:
                pass

        return {"status": "alive", "health": health, "timestamp": datetime.datetime.utcnow().isoformat()}

    return app

    # --- Debug diagnostics router ---
    from fastapi import APIRouter
    import httpx, datetime

    debug_router = APIRouter(prefix="/debug", tags=["Diagnostics"])

    @debug_router.get("/env")
    async def get_env():
        """Show sanitized env vars (masking sensitive keys)."""
        env_data = {}
        for key, value in os.environ.items():
            if any(secret in key.lower() for secret in ["key", "token", "secret", "password"]):
                env_data[key] = "***MASKED***"
            else:
                env_data[key] = value
        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "env": env_data
        }

    @debug_router.get("/routes")
    async def list_routes():
        """List all active routes."""
        route_list = []
        for route in app.routes:
            route_list.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
        return {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "routes": route_list,
            "count": len(route_list)
        }

    @debug_router.get("/health/full")
    async def full_health():
        """Comprehensive service health check."""
        status = {"timestamp": datetime.datetime.utcnow().isoformat()}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Supabase
                supabase_url = os.getenv("SUPABASE_URL")
                if supabase_url:
                    try:
                        res = await client.get(f"{supabase_url}/rest/v1", timeout=5)
                        status["supabase"] = "ok" if res.status_code < 500 else "error"
                    except Exception as e:
                        status["supabase"] = f"error:{e}"
                # Render
                try:
                    render_url = "https://api.render.com/v1/services"
                    res = await client.get(render_url)
                    status["render"] = "ok" if res.status_code == 200 else f"error:{res.status_code}"
                except Exception as e:
                    status["render"] = f"error:{e}"
                # OpenAI
                try:
                    import openai
                    openai_api_key = os.getenv("OPENAI_API_KEY")
                    if openai_api_key:
                        client_openai = openai.OpenAI(api_key=openai_api_key)
                        models = client_openai.models.list()
                        status["openai"] = "ok" if models else "error"
                    else:
                        status["openai"] = "no_api_key"
                except Exception as e:
                    status["openai"] = f"error:{e}"
        except Exception as e:
            status["error"] = str(e)
        return status

    app.include_router(debug_router)
    return app
# 🪶 FastAPI configuration
# --------------------------------------------------------
app = FastAPI(
    title="Kitenga MCP Core",
    version="1.1.0",
    description="Model Context Protocol bridge for Kitenga Whiro — Māori Intelligence Engine"
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kitenga_mcp")

# --------------------------------------------------------
# === CORS helpers for Render ===
# --------------------------------------------------------
STATIC_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "https://tiwhanawhana-backend.onrender.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=STATIC_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# 🔒 Bearer token middleware for /mcp routes
# --------------------------------------------------------
from fastapi import Request, HTTPException
PIPELINE_TOKEN = os.getenv("PIPELINE_TOKEN")

@app.middleware("http")
async def verify_auth(request: Request, call_next):
    # Apply auth only to /mcp routes
    if request.url.path.startswith("/mcp"):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")
        token = auth_header.replace("Bearer ", "").strip()
        # Allow either our internal pipeline token OR provider tokens
        valid_tokens = [
            PIPELINE_TOKEN,
            os.getenv("RENDER_API_KEY"),
            os.getenv("GITHUB_TOKEN"),
            os.getenv("SUPABASE_SERVICE_KEY")
        ]
        if token not in valid_tokens:
            raise HTTPException(status_code=403, detail="Unauthorized: Invalid token.")
    response = await call_next(request)
    return response


# --------------------------------------------------------
# 🧩 Dynamic tool manifest loader
# --------------------------------------------------------
def load_tool_manifests():
    base = Path(__file__).parent / "tools" / "manifests"
    merged = {}
    for path in glob.glob(str(base / "*.json")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for domain, content in data.items():
                    if domain not in merged:
                        merged[domain] = {"tools": []}
                    if isinstance(content, dict) and "tools" in content:
                        merged[domain]["tools"].extend(content["tools"])
        except Exception as e:
            logging.warning(f"⚠️ Failed to load {path}: {e}")
    logging.info(f"✅ Loaded {len(merged)} tool domains from {base}")
    return merged

TOOLS_MANIFEST = load_tool_manifests()

def supabase_client():
    """Return a Supabase client if configured, else None."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    # create_client is not defined; return None for now
    return None

def log_telemetry(domain, command, stdout, user=None):
    """Stub: Log tool-call telemetry to Supabase (optional)."""
    client = supabase_client()
    if client:
        try:
            data = {
                "domain": domain,
                "command": command,
                "stdout": stdout,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user": user or "unknown"
            }
            client.table("tool_telemetry").insert(data).execute()
        except Exception as e:
            logger.warning(f"Supabase telemetry failed: {e}")

    # Other routes
    @app.get("/", tags=["Root"])
    async def root():
        """Root status route."""
        return {
            "status": "online",
            "message": "Kia ora — Kitenga MCP Core is running.",
            "routes": [
                "/mcp/health",
                "/mcp/tools/list",
                "/mcp/tools/describe",
                "/mcp/tools/call",
                "/mcp/memory/ping",
                "/mcp/reauth"
            ]
        }

@app.get("/health", tags=["MCP"])
async def health_check():
    """Render/GPT health check."""
    return {
        "status": "alive",
        "service": "Kitenga MCP Core",
        "kaitiaki": "Whiro",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "env": {
            "lang": os.getenv("LANG", "C.UTF-8"),
            "lc_all": os.getenv("LC_ALL", "C.UTF-8")
        }
    }


@app.get("/tools/list", tags=["MCP"])
async def list_tools():
    """List all loaded tool domains and their tools from merged manifest."""
    return {
        "status": "ok",
        "kaitiaki": "Kitenga Whiro",
        "tools": TOOLS_MANIFEST
    }



# --------------------------------------------------------
# 🧭 /tools/describe — list all loaded tool domains and commands
# --------------------------------------------------------
@app.get("/tools/describe", tags=["MCP"])
async def describe_tools():
    if not TOOLS_MANIFEST:
        raise HTTPException(status_code=404, detail="No tools loaded in manifest.")
    description = {
        domain: [t["name"] for t in data["tools"]]
        for domain, data in TOOLS_MANIFEST.items()
    }
    return {"status": "success", "tools": description, "domains": list(description.keys())}



@app.post("/tools/call", tags=["MCP"])
async def call_tool(request: Request):
    data = await request.json()
    domain = data.get("domain")
    command = data.get("command") or data.get("tool")  # backward-compatible
    input_data = data.get("input", {})
    caller_meta = data.get("caller") or {"origin": "unknown"}

    if not domain or not command:
        raise HTTPException(status_code=400, detail="Missing 'domain' or 'command' in request body.")

    domain_data = TOOLS_MANIFEST.get(domain)
    if not domain_data:
        raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found in tools manifest.")

    tool_def = next((t for t in domain_data.get("tools", []) if t["name"] == command), None)
    if not tool_def:
        raise HTTPException(status_code=404, detail=f"Command '{command}' not found in '{domain}' tools.")


    # Live Render API integration
    try:
        if domain == "render":
            if command == "render_list_services":
                result = await call_render_api("/services")
            elif command == "render_get_service":
                service_id = input_data.get("service_id")
                result = await call_render_api(f"/services/{service_id}")
            elif command == "render_deploy":
                service_id = input_data.get("service_id")
                result = await call_render_api(f"/services/{service_id}/deploys", method="POST")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported Render command: {command}")
        else:
            result = {"status": "pending", "message": f"No live handler for {domain}.{command}"}
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    trace_id = await log_tool_usage(domain, command, input_data, result, caller_meta)
    headers = {"X-Trace-ID": trace_id}
    return JSONResponse(content=result, headers=headers)


# --------------------------------------------------------
# 💓 /mcp/memory/ping — health diagnostics
# --------------------------------------------------------

# --------------------------------------------------------
# 🧠 Future expansions (TODOs)
# --------------------------------------------------------
# - Telemetry metrics improvements (Supabase schema, richer logs)
# - Rate-limiting per client/IP for /mcp/tools/call
# - Health auto-report back to AwaNet dashboard
# - Auth middleware improvements (token expiry, scopes)
# - More robust error handling and validation

# --------------------------------------------------------
# === Static schema exposure for Render ===
# --------------------------------------------------------
app.mount("/", StaticFiles(directory=str(SCHEMA_DIR), html=False), name="repo_schema")
logger.info(f"✅ Static schema assets available at {SCHEMA_DIR}, '/' now serves JSON files like openai_tools.json.")


@app.middleware("http")
async def _json_content_safety(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.endswith(".json"):
        response.headers.setdefault("Content-Type", "application/json")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    return response

# --------------------------------------------------------
# 🧪 Testing instructions
# --------------------------------------------------------
# After deploy to Render, test with:
# curl https://kitenga-core-js.onrender.com/mcp/health
# curl https://kitenga-core-js.onrender.com/mcp/tools/list | jq
# curl https://kitenga-core-js.onrender.com/mcp/tools/describe?domain=render | jq
# curl -X POST https://kitenga-core-js.onrender.com/mcp/tools/call \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $PIPELINE_TOKEN" \
#   -d '{"domain":"git","command":"pull_repo"}' | jq

# --- Safety check for local run ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)
