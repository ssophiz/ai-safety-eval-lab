"""Validate the draft protocol matrix and its immutable planning files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


PROTOCOL_DIR = Path("research/protocol-v0.1")
PLAN_FILES = (
    "README.md", "research_question.md", "experiment_protocol.md",
    "statistics_plan.md", "paper_outline.md", "reproducibility_checklist.md",
    "experiment_matrix.csv",
)
MODELS = {
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "meta-llama/Llama-3.1-8B-Instruct",
}
LANGUAGES = {"ko", "en"}
CONDITIONS = {"A", "B", "C"}


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def validate_matrix(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 18:
        raise ValueError(f"matrix must have 18 rows, found {len(rows)}")
    expected_cells = {
        (model, language, condition)
        for model in MODELS for language in LANGUAGES for condition in CONDITIONS
    }
    actual_cells = {(r["model_id"], r["language"], r["condition"]) for r in rows}
    if actual_cells != expected_cells:
        raise ValueError("matrix must contain every model/language/condition cell exactly once")
    if len({r["cell_id"] for r in rows}) != 18:
        raise ValueError("cell_id values must be unique")

    integer_fields = (
        "semantic_clusters", "benign_cases", "contaminated_cases", "repeats",
        "planned_runs", "planned_model_calls", "max_generated_tokens_per_run",
    )
    expected_values = {
        "semantic_clusters": 40,
        "benign_cases": 20,
        "contaminated_cases": 20,
        "repeats": 3,
        "planned_runs": 120,
        "planned_model_calls": 240,
        "max_generated_tokens_per_run": 1536,
    }
    totals = {"planned_runs": 0, "planned_model_calls": 0}
    for row in rows:
        try:
            values = {field: int(row[field]) for field in integer_fields}
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{row.get('cell_id', '<unknown>')}: invalid integer field") from exc
        if values != expected_values:
            changed = [
                field for field in integer_fields
                if values[field] != expected_values[field]
            ]
            raise ValueError(
                f"{row['cell_id']}: frozen draft value mismatch for {', '.join(changed)}"
            )
        if values["semantic_clusters"] != values["benign_cases"] + values["contaminated_cases"]:
            raise ValueError(f"{row['cell_id']}: scenario counts do not sum")
        if values["planned_runs"] != values["semantic_clusters"] * values["repeats"]:
            raise ValueError(f"{row['cell_id']}: planned_runs arithmetic mismatch")
        if values["planned_model_calls"] != values["planned_runs"] * 2:
            raise ValueError(f"{row['cell_id']}: planned_model_calls arithmetic mismatch")
        if row["status"] != "not_run" or row["run_manifest"]:
            raise ValueError(f"{row['cell_id']}: draft matrix must remain explicitly not_run")
        if row["model_revision"] != "unresolved" or row["split"] != "test":
            raise ValueError(f"{row['cell_id']}: unresolved draft fields changed")
        totals["planned_runs"] += values["planned_runs"]
        totals["planned_model_calls"] += values["planned_model_calls"]
    if totals != {"planned_runs": 2160, "planned_model_calls": 4320}:
        raise ValueError(f"unexpected plan totals: {totals}")
    return {"cells": len(rows), **totals, "status": "not_run"}


def build_manifest(root: Path) -> dict:
    protocol = root / PROTOCOL_DIR
    return {
        "schema_version": 1,
        "kind": "draft_protocol_plan",
        "hash_semantics": "sha256 after CRLF-to-LF normalization",
        "files": {name: sha256_lf(protocol / name) for name in PLAN_FILES},
        "matrix": validate_matrix(protocol / "experiment_matrix.csv"),
        "claim_boundary": "This manifest verifies a not-run plan, not experimental results.",
    }


def verify_manifest(root: Path) -> dict:
    path = root / PROTOCOL_DIR / "plan_manifest.json"
    recorded = json.loads(path.read_text(encoding="utf-8"))
    expected = build_manifest(root)
    if recorded != expected:
        raise ValueError("plan_manifest.json does not match the current protocol plan")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = build_manifest(root)
    path = root / PROTOCOL_DIR / "plan_manifest.json"
    if args.write_manifest:
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE {path.relative_to(root)}")
    else:
        verify_manifest(root)
        print("OK draft protocol plan: 18 cells, 2,160 planned runs, 4,320 planned calls, all not_run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
