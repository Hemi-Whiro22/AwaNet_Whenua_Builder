import os

from te_po.stealth_ocr import pipeline_context


def test_pipeline_context_hash_present_when_token_set():
    os.environ["PIPELINE_TOKEN"] = "abc123"
    ctx = pipeline_context("run-1")
    assert ctx["pipeline_run_id"] == "run-1"
    assert ctx["tokened"] is True
    assert "token_hash" in ctx


def test_pipeline_context_no_token():
    if "PIPELINE_TOKEN" in os.environ:
        del os.environ["PIPELINE_TOKEN"]
    ctx = pipeline_context("run-2")
    assert ctx["pipeline_run_id"] == "run-2"
    assert ctx["tokened"] is False
    assert "token_hash" not in ctx
