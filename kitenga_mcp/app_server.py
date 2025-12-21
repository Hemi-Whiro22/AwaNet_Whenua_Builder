from fastapi import FastAPI

def create_app() -> FastAPI:
    """Create the base FastAPI app for Kitenga's MCP system."""
    app = FastAPI(title="Kitenga MCP App", version="1.0.0")

    @app.get("/")
    async def root():
        return {"message": "Kitenga MCP base app running"}

    return app
# =========================================================