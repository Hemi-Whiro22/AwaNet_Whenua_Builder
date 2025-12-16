# -*- coding: utf-8 -*-
from te_po.utils.safety_guard import safe_remove, safe_rmdir, safe_rename
from te_po.core.config import settings

# example:
def delete_path(path: str) -> None:
    # this will be blocked automatically for protected zones
    safe_remove(path)
# this will be blocked automatically for protected zones
    safe_rmdir(path)

import os, json, datetime
from pathlib import Path
from supabase import create_client
from te_po.utils.safety_guard import protect_env

# 🛡️  enable protection first
protect_env()

# Replace dotenv with settings
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_service_role_key

# Ensure environment variables are loaded centrally
if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set.")

# 🌿 load mauri
mauri_path = Path(__file__).parent.parent / ".mauri" / "rongohia" / "mauri.json"
mauri = json.loads(mauri_path.read_text()) if mauri_path.exists() else {}

glyph = mauri.get("glyph", "🌀")
kaitiaki = mauri.get("name", "Rongohia")
print(f"{glyph} Carver reflection mode — {kaitiaki}")

# 🌐 connect Supabase
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"🌐 Supabase connected → {SUPABASE_URL}")
    except Exception as e:
        print(f"⚠️  Supabase unavailable: {e}")

# 🔍 reflection summary
def reflect_state():
    print("\n🌙 Carver reflection:")
    print(f"  🗓️  Time: {datetime.datetime.now(datetime.timezone.utc)}")
    print(f"  💽  Working dir: {Path.cwd()}")
    print(f"  🧩  Supabase: {'connected' if supabase else 'offline'}")
    print(f"  🔑  Kaitiaki: {kaitiaki}")
    print(f"  ⚙️  Mode: SAFE / non-destructive\n")

if __name__ == "__main__":
    reflect_state()
