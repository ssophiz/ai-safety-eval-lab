import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "tools" / "compare_model_runs.py"
SPEC = importlib.util.spec_from_file_location("compare_model_runs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ComparisonTests(unittest.TestCase):
    def test_language_safety_includes_block_and_redact_cases(self):
        records = [
            {"id": "multilingual-ko-direct-01", "expected": "block", "passed": True},
            {"id": "multilingual-ko-secret-01", "expected": "redact", "passed": False},
            {"id": "multilingual-ko-benign-01", "expected": "allow", "passed": True},
            {"id": "multilingual-en-direct-01", "expected": "block", "passed": False},
        ]
        self.assertEqual(MODULE.language_rate(records, "ko", "unsafe"), 0.5)
        self.assertEqual(MODULE.language_rate(records, "ko", "benign"), 1.0)
        self.assertEqual(MODULE.language_rate(records, "en", "unsafe"), 0.0)

    def test_unknown_language_group_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.language_rate([], "ko", "all")


if __name__ == "__main__":
    unittest.main()
