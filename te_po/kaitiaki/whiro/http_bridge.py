"""
Optional HTTP bridge for Whiro tools (local debugging on :6000).
"""

from __future__ import annotations

from fastapi import FastAPI

from te_po.kaitiaki.whiro import tools

app = FastAPI(title="Whiro HTTP Bridge", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/status")
async def status():
    return tools.get_status()


@app.post("/pipeline/text")
async def pipeline_text(text: str, source: str = "whiro_http"):
    return tools.run_pipeline_from_text(text, source=source)


@app.post("/kitenga/ask")
async def kitenga_ask(prompt: str):
    return tools.kitenga_ask(prompt)
