#!/usr/bin/env python3
"""Lightweight diagnostics runner for realm mauri/health.

This script avoids heavy external deps and uses the local
`te_hau.core.healing.SelfHealingEngine` to produce simple JSON
reports for `te_hau` and `te_po` realms into the repository
`analysis/` directory.
"""

import asyncio
import json
from pathlib import Path
from te_hau.core.healing import SelfHealingEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_DIR = REPO_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)


def run_diagnose(realm_path: str) -> dict:
	engine = SelfHealingEngine(Path(realm_path))
	report = asyncio.run(engine.diagnose())
	return report.to_dict()


def main():
	targets = ["te_hau", "te_po"]
	summary = {}
	for t in targets:
		try:
			summary[t] = run_diagnose(t)
		except Exception as e:
			summary[t] = {"error": str(e)}

	# Modify the output path for the diagnostics JSON report
	out = REPO_ROOT / 'mauri' / 'diagnostics_realms.json'
	out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
	print(f"Wrote diagnostics to {out}")


if __name__ == "__main__":
	main()

