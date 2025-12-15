from fastapi import FastAPI

from te_po.core.env_loader import load_env, enforce_utf8_locale
from te_po.routes import status, chat, vector


def create_app() -> FastAPI:
    load_env()
    enforce_utf8_locale()

    app = FastAPI(title="Te Pō Proxy - Read Backend Proxy")
    app.include_router(status.router)
    app.include_router(chat.router, prefix="/chat")
    app.include_router(vector.router, prefix="/vector")
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
