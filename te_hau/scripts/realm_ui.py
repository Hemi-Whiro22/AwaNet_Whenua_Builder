#!/usr/bin/env python3
"""
Realm Generator Web UI
FastAPI-based browser interface for generating specialized realms.
Access at: http://localhost:8888
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from generate_realm import RealmGenerator

# Initialize FastAPI app
app = FastAPI(title="Realm Generator UI", version="1.0.0")

# Get The_Awa_Network root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class RealmRequest(BaseModel):
    """Request model for realm generation."""
    name: str
    slug: str
    kaitiaki_name: str
    kaitiaki_role: str
    description: str = "Specialized realm for The Awa Network"
    push_to_git: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the realm generator UI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🏔️ Realm Generator</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 100%;
                padding: 40px;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .header h1 {
                font-size: 28px;
                color: #333;
                margin-bottom: 8px;
            }

            .header p {
                color: #666;
                font-size: 14px;
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
                font-size: 14px;
            }

            input[type="text"],
            input[type="email"],
            textarea,
            select {
                width: 100%;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.3s;
            }

            input[type="text"]:focus,
            input[type="email"]:focus,
            textarea:focus,
            select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            textarea {
                resize: vertical;
                min-height: 80px;
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            .section-title {
                font-size: 12px;
                font-weight: 700;
                color: #999;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-top: 25px;
                margin-bottom: 15px;
            }

            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 30px;
            }

            button {
                flex: 1;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }

            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }

            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }

            .btn-secondary:hover {
                background: #e0e0e0;
            }

            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 6px;
                font-size: 13px;
                line-height: 1.6;
                display: none;
            }

            .status.loading {
                background: #e3f2fd;
                color: #1976d2;
                display: block;
            }

            .status.success {
                background: #e8f5e9;
                color: #388e3c;
                display: block;
            }

            .status.error {
                background: #ffebee;
                color: #d32f2f;
                display: block;
            }

            .help-text {
                font-size: 12px;
                color: #999;
                margin-top: 6px;
            }

            .examples {
                background: #f9f9f9;
                border-left: 3px solid #667eea;
                padding: 15px;
                border-radius: 4px;
                margin-top: 25px;
                font-size: 12px;
            }

            .examples strong {
                display: block;
                margin-bottom: 8px;
                color: #333;
            }

            .example-item {
                margin-bottom: 8px;
                color: #666;
                font-family: monospace;
            }

            .example-item code {
                background: white;
                padding: 2px 6px;
                border-radius: 3px;
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏔️ Realm Generator</h1>
                <p>Create specialized realms for The Awa Network</p>
            </div>

            <form id="realmForm">
                <div class="section-title">Realm Details</div>

                <div class="form-group">
                    <label for="name">Realm Name *</label>
                    <input type="text" id="name" name="name" required placeholder="e.g., Cards Realm">
                    <div class="help-text">Human-readable name for your realm</div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="slug">Slug *</label>
                        <input type="text" id="slug" name="slug" required placeholder="e.g., cards_realm">
                        <div class="help-text">Folder name (lowercase, underscores)</div>
                    </div>
                </div>

                <div class="section-title">Kaitiaki Agent</div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="kaitiakiName">Agent Name *</label>
                        <input type="text" id="kaitiakiName" name="kaitiakiName" required placeholder="e.g., katu">
                        <div class="help-text">Codex name for the agent</div>
                    </div>

                    <div class="form-group">
                        <label for="kaitiakiRole">Agent Role *</label>
                        <input type="text" id="kaitiakiRole" name="kaitiakiRole" required placeholder="e.g., card_oracle">
                        <div class="help-text">System role/purpose</div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" placeholder="Describe the realm's purpose..."></textarea>
                    <div class="help-text">Optional realm description</div>
                </div>

                <div class="section-title">Optional Settings</div>

                <div class="form-group">
                    <label for="gitRepo">Git Repository URL</label>
                    <input type="text" id="gitRepo" name="gitRepo" placeholder="e.g., git@github.com:user/cards-realm.git">
                    <div class="help-text">Leave empty to skip git push</div>
                </div>

                <div class="button-group">
                    <button type="submit" class="btn-primary" id="generateBtn">Generate Realm</button>
                    <button type="reset" class="btn-secondary">Clear</button>
                </div>

                <div id="status" class="status"></div>
            </form>

            <div class="examples">
                <strong>Example Realms:</strong>
                <div class="example-item">🃏 <code>Cards Realm</code> - Slug: <code>cards_realm</code>, Agent: <code>katu</code></div>
                <div class="example-item">🌐 <code>Translator Realm</code> - Slug: <code>translator_realm</code>, Agent: <code>whare-whakamaori</code></div>
                <div class="example-item">🔊 <code>Audio Realm</code> - Slug: <code>audio_realm</code>, Agent: <code>korero</code></div>
            </div>
        </div>

        <script>
            const form = document.getElementById('realmForm');
            const statusDiv = document.getElementById('status');
            const generateBtn = document.getElementById('generateBtn');

            // Auto-generate slug from name
            document.getElementById('name').addEventListener('input', function() {
                const slug = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9\\s]/g, '')
                    .replace(/\\s+/g, '_')
                    .trim();
                document.getElementById('slug').value = slug;
            });

            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                const formData = {
                    name: document.getElementById('name').value,
                    slug: document.getElementById('slug').value,
                    kaitiaki_name: document.getElementById('kaitiakiName').value,
                    kaitiaki_role: document.getElementById('kaitiakiRole').value,
                    description: document.getElementById('description').value,
                    push_to_git: document.getElementById('gitRepo').value || null
                };

                generateBtn.disabled = true;
                statusDiv.className = 'status loading';
                statusDiv.innerHTML = '⏳ Generating realm... This may take a moment...';

                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });

                    const result = await response.json();

                    if (!response.ok) {
                        throw new Error(result.detail || 'Generation failed');
                    }

                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = `
                        ✅ <strong>Realm generated successfully!</strong><br>
                        📁 Location: <code>${result.realm_dir}</code><br>
                        🤖 Kaitiaki: <code>${result.kaitiaki_name}</code><br>
                        <br>
                        The realm is now visible in VS Code. Start developing!
                    `;

                    form.reset();
                } catch (error) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = `❌ Error: ${error.message}`;
                } finally {
                    generateBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """


@app.post("/api/generate")
async def generate_realm(request: RealmRequest):
    """Generate a new realm."""
    try:
        # Validate inputs
        if not request.name or not request.slug:
            raise ValueError("Name and slug are required")

        # Create generator
        generator = RealmGenerator(project_root=PROJECT_ROOT)

        # Generate realm (run in thread pool to avoid blocking)
        success = await asyncio.to_thread(
            generator.generate,
            name=request.name,
            slug=request.slug,
            kaitiaki_name=request.kaitiaki_name,
            kaitiaki_role=request.kaitiaki_role,
            description=request.description,
            push_to_git=request.push_to_git
        )

        if not success:
            raise RuntimeError("Realm generation failed")

        return JSONResponse({
            "status": "success",
            "realm_dir": str(PROJECT_ROOT / request.slug),
            "kaitiaki_name": request.kaitiaki_name,
            "message": f"Realm '{request.name}' generated successfully"
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get system status."""
    return {
        "service": "Realm Generator UI",
        "version": "1.0.0",
        "project_root": str(PROJECT_ROOT),
        "status": "ready"
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("🏔️  Realm Generator UI")
    print("="*60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Access at:    http://localhost:8888")
    print("="*60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8888)
