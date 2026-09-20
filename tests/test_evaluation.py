import json
import tempfile
import unittest
from pathlib import Path

from aisafety_eval.adapters import BaselineAdapter, GuardedAdapter
from aisafety_eval.dataset import load_cases
from aisafety_eval.evaluator import evaluate
from aisafety_eval.report import write_reports


ROOT = Path(__file__).parents[1]


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(ROOT / "data" / "cases.jsonl")

    def test_dataset_has_balanced_versioned_coverage(self):
        self.assertEqual(len(self.cases), 120)
        self.assertEqual(len({case.case_id for case in self.cases}), 120)
        self.assertEqual(len({case.category for case in self.cases}), 6)

    def test_guarded_adapter_passes_reference_cases(self):
        result = evaluate(GuardedAdapter(), self.cases)
        self.assertEqual(result["attack_success_rate"], 0)
        self.assertEqual(result["safety_pass_rate"], 1)
        self.assertEqual(result["benign_task_success_rate"], 1)

    def test_baseline_exposes_safety_gap(self):
        result = evaluate(BaselineAdapter(), self.cases)
        self.assertEqual(result["attack_success_rate"], 1)
        self.assertEqual(result["benign_task_success_rate"], 1)

    def test_reports_are_machine_and_human_readable(self):
        results = [evaluate(BaselineAdapter(), self.cases), evaluate(GuardedAdapter(), self.cases)]
        with tempfile.TemporaryDirectory() as directory:
            write_reports(results, directory)
            payload = json.loads((Path(directory) / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(len(payload), 2)
            self.assertIn("AI Safety Evaluation Results", (Path(directory) / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
