import csv
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_protocol_plan", ROOT / "tools" / "validate_protocol_plan.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ProtocolPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        target = self.root / "research" / "protocol-v0.1"
        shutil.copytree(ROOT / "research" / "protocol-v0.1", target)

    def test_checked_in_manifest_matches_plan(self):
        manifest = VALIDATOR.verify_manifest(ROOT)
        self.assertEqual(manifest["matrix"], {
            "cells": 18, "planned_runs": 2160,
            "planned_model_calls": 4320, "status": "not_run",
        })

    def test_changed_protocol_file_is_rejected(self):
        path = self.root / "research" / "protocol-v0.1" / "statistics_plan.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            VALIDATOR.verify_manifest(self.root)

    def _matrix_copy(self):
        path = self.root / "research" / "protocol-v0.1" / "experiment_matrix.csv"
        source = ROOT / "research" / "protocol-v0.1" / "experiment_matrix.csv"
        with source.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0])
        return path, rows, fields

    @staticmethod
    def _write_matrix(path, rows, fields):
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_inflated_run_count_is_rejected(self):
        path, rows, fields = self._matrix_copy()
        rows[0]["planned_runs"] = "121"
        self._write_matrix(path, rows, fields)
        with self.assertRaisesRegex(ValueError, "frozen draft value mismatch for planned_runs"):
            VALIDATOR.validate_matrix(path)

    def test_each_frozen_numeric_field_is_rejected_when_changed(self):
        fields_to_change = (
            "semantic_clusters", "benign_cases", "contaminated_cases", "repeats",
            "planned_model_calls", "max_generated_tokens_per_run",
        )
        for field in fields_to_change:
            with self.subTest(field=field):
                path, rows, fields = self._matrix_copy()
                rows[0][field] = str(int(rows[0][field]) + 1)
                self._write_matrix(path, rows, fields)
                with self.assertRaisesRegex(ValueError, f"frozen draft value mismatch for {field}"):
                    VALIDATOR.validate_matrix(path)

    def test_completed_status_is_rejected_independently(self):
        path, rows, fields = self._matrix_copy()
        rows[0]["status"] = "complete"
        self._write_matrix(path, rows, fields)
        with self.assertRaisesRegex(ValueError, "must remain explicitly not_run"):
            VALIDATOR.validate_matrix(path)

    def test_manifest_is_portable_across_newlines(self):
        before = VALIDATOR.build_manifest(self.root)
        path = self.root / "research" / "protocol-v0.1" / "README.md"
        normalized = path.read_bytes().replace(b"\r\n", b"\n")
        path.write_bytes(normalized.replace(b"\n", b"\r\n"))
        self.assertEqual(before, VALIDATOR.build_manifest(self.root))


if __name__ == "__main__":
    unittest.main()
