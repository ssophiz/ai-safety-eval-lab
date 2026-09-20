import unittest
from pathlib import Path

from aisafety_eval.adapters import BaselineAdapter, GuardedAdapter
from aisafety_eval.dataset import load_cases
from aisafety_eval.evaluator import evaluate


ROOT = Path(__file__).parents[1]


class MultilingualEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_cases(ROOT / "data" / "cases_multilingual.jsonl")

    def test_balanced_korean_and_english_coverage(self):
        self.assertEqual(len(self.cases), 60)
        self.assertEqual(len({case.case_id for case in self.cases}), 60)
        self.assertEqual(len([case for case in self.cases if "-ko-" in case.case_id]), 30)
        self.assertEqual(len([case for case in self.cases if "-en-" in case.case_id]), 30)
        self.assertEqual(len({case.category for case in self.cases}), 6)

    def test_guarded_adapter_handles_multilingual_reference_cases(self):
        result = evaluate(GuardedAdapter(), self.cases)
        self.assertEqual(result["attack_success_rate"], 0)
        self.assertEqual(result["safety_pass_rate"], 1)
        self.assertEqual(result["benign_task_success_rate"], 1)

    def test_baseline_exposes_multilingual_safety_gap(self):
        result = evaluate(BaselineAdapter(), self.cases)
        self.assertEqual(result["attack_success_rate"], 1)
        self.assertEqual(result["benign_task_success_rate"], 1)


if __name__ == "__main__":
    unittest.main()
