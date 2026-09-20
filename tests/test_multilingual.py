import importlib.util
import json
import unittest
from pathlib import Path

from aisafety_eval.adapters import BaselineAdapter, GuardedAdapter
from aisafety_eval.dataset import load_cases
from aisafety_eval.evaluator import evaluate


ROOT = Path(__file__).parents[1]

GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "generate_multilingual_dataset", ROOT / "tools" / "generate_multilingual_dataset.py"
)
GENERATOR = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR)


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

    def test_checked_in_dataset_matches_generator_and_documents_repetition(self):
        generated = GENERATOR.generate()
        recorded = [
            json.loads(line)
            for line in (ROOT / "data" / "cases_multilingual.jsonl")
            .read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(recorded, generated)
        for language in ("ko", "en"):
            rows = [row for row in recorded if f"-{language}-" in row["id"]]
            distinct_prompts = {row["prompt"] for row in rows}
            distinct_inputs = {
                json.dumps(
                    {key: value for key, value in row.items() if key != "id"},
                    sort_keys=True,
                    ensure_ascii=False,
                )
                for row in rows
            }
            self.assertEqual(len(rows), 30)
            self.assertEqual(len(distinct_prompts), 6)
            self.assertEqual(len(distinct_inputs), 10)

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
