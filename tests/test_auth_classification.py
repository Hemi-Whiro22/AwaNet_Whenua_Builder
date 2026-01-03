import importlib
import os

from te_po.core import auth


def test_identity_classification_human_pipeline_service():
    os.environ["HUMAN_BEARER_KEY"] = "human"
    os.environ["PIPELINE_TOKEN"] = "pipe"
    os.environ["SERVICE_BEARER_KEY"] = "svc"
    importlib.reload(auth)
    tokens = auth.load_tokens()

    role, tok = auth.classify_identity(tokens, "Bearer human")
    assert role == "human"
    assert tok == "human"

    role, tok = auth.classify_identity(tokens, "Bearer pipe")
    assert role == "pipeline"
    assert tok == "pipe"

    role, tok = auth.classify_identity(tokens, "Bearer svc")
    assert role == "service"
    assert tok == "svc"


def test_require_token_missing_when_expected():
    os.environ["HUMAN_BEARER_KEY"] = "human"
    importlib.reload(auth)
    tokens = auth.load_tokens()
    try:
        auth.require_human(None, tokens=tokens)
    except Exception as exc:
        from fastapi import HTTPException

        assert isinstance(exc, HTTPException)
        assert exc.status_code == 401
