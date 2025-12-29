#!/usr/bin/env python3
"""Generate sample files for each supported extension and run the Te Pō pipeline."""

from __future__ import annotations
from taonga.sync_status import (
    fetch_analysis_sync_status,
    fetch_latest_analysis_document_content,
)
from te_po.utils.supabase_client import get_client
from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

import argparse
import json
import math
import subprocess
import sys
import wave
from pathlib import Path
from typing import Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

SAMPLE_DIR = ROOT / "analysis" / "live_samples"


def ensure_pillow() -> Tuple:
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "Pillow"],
            check=True,
        )
        from PIL import Image, ImageDraw
    return Image, ImageDraw


def create_text_file(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def create_json(path: Path, payload: Dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def create_wave(path: Path, duration=1.0) -> None:
    samples = int(44100 * duration)
    amplitude = 32767
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(44100)
        data = (int(amplitude * math.sin(2 * math.pi * 440 * t / 44100))
                for t in range(samples))
        frames = b"".join(int(sample).to_bytes(
            2, "little", signed=True) for sample in data)
        handle.writeframes(frames)


def create_samples() -> List[Path]:
    sample_text = "Kia ora — this is a sample payload for pipeline testing."
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    samples: List[Tuple[str, Callable[[Path], None]]] = [
        ("sample.txt", lambda p: create_text_file(p, sample_text)),
        ("sample.md", lambda p: create_text_file(
            p, f"# Sample Markdown\n\n{sample_text}")),
        ("sample.json", lambda p: create_json(
            p, {"text": sample_text, "tags": ["pipeline", "test"]})),
        ("sample.yaml", lambda p: create_text_file(
            p, f"text: \"{sample_text}\"\ntags:\n  - pipeline\n  - test")),
        ("sample.html", lambda p: create_text_file(
            p, "<html><body><p>" + sample_text + "</p></body></html>")),
        ("sample.htm", lambda p: create_text_file(p, "<p>" + sample_text + "</p>")),
    ]

    Image, ImageDraw = ensure_pillow()

    def _make_image(path: Path, mode="PNG") -> None:
        img = Image.new("RGB", (128, 128), color="navy")
        draw = ImageDraw.Draw(img)
        draw.text((10, 60), "AwaNet", fill="white")
        img.save(path, mode)

    samples.extend(
        [
            ("sample.png", lambda p: _make_image(p, mode="PNG")),
            ("sample.jpg", lambda p: _make_image(p, mode="JPEG")),
            ("sample.jpeg", lambda p: _make_image(p, mode="JPEG")),
            ("sample.webp", lambda p: _make_image(p, mode="WEBP")),
        ]
    )

    samples.append(("sample.pdf", lambda p: _make_image(p, mode="PDF")))
    samples.append(("sample.wav", lambda p: create_wave(p)))
    # mp3/m4a placeholders (audio not supported yet)
    samples.append(("sample.mp3", lambda p: p.write_bytes(b"MP3DATA")))
    samples.append(("sample.m4a", lambda p: p.write_bytes(b"M4ADATA")))

    created: List[Path] = []
    for filename, maker in samples:
        path = SAMPLE_DIR / filename
        maker(path)
        print(f"Created sample: {path.relative_to(ROOT)}")
        created.append(path)
    return created


def run_pipeline_for_samples(files: List[Path], source="gpt-live-test") -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for path in files:
        print(f"Running pipeline on {path.name} ({path.suffix})")
        data = path.read_bytes()
        res = run_pipeline(
            file_bytes=data,
            filename=path.name,
            source=source,
            generate_summary=False,
        )
        results.append(
            {
                "file": path.name,
                "status": res.get("status"),
                "chunk_count": res.get("chunk_count"),
                "vector_batch": res.get("vector_batch_id"),
                "summary": res.get("summary"),
                "reason": res.get("reason"),
            }
        )
    return results


def fetch_supabase_snapshot() -> Dict[str, object]:
    status = fetch_analysis_sync_status()
    doc = fetch_latest_analysis_document_content()
    client = get_client()
    vector_info = None
    if client:
        resp = (
            client.schema("kitenga")
            .table("vector_batches")
            .select("batch_id,status,metadata,created_at")
            .order("created_at", desc=True)
            .limit(5)
        )
        data = resp.execute()
        vector_info = getattr(data, "data", [])

    return {"status": status, "latest_document": doc, "vector_batches": vector_info}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate test files and run the Te Pō pipeline.")
    parser.add_argument("--skip-samples", action="store_true",
                        help="Do not recreate sample files.")
    args = parser.parse_args()

    if not args.skip_samples:
        files = create_samples()
    else:
        files = sorted(SAMPLE_DIR.glob("*"))
    pipeline_results = run_pipeline_for_samples(files)
    supabase_snapshot = fetch_supabase_snapshot()
    print("\nPipeline run results:")
    for entry in pipeline_results:
        print(json.dumps(entry, indent=2, ensure_ascii=False))

    print("\nSupabase / vector snapshot:")
    print(json.dumps(supabase_snapshot, indent=2, ensure_ascii=False))

    print("\nFinished running live pipeline tests.")


if __name__ == "__main__":
    main()
