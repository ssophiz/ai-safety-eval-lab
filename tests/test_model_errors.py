import http.client
import json
import tempfile
import unittest
import urllib.error
from dataclasses import replace
from pathlib import Path
from unittest.mock import MagicMock, patch

from aisafety_eval.evaluator import evaluate
from aisafety_eval.model_adapter import ModelEvaluationError, OpenAICompatibleAdapter
from aisafety_eval.report import write_reports
from aisafety_eval.types import Case


class ModelErrorTests(unittest.TestCase):
    def setUp(self):
        self.adapter = OpenAICompatibleAdapter("http://127.0.0.1:11434", "test-model")
        self.case = Case("test-001", "safety", "Synthetic case", "", True, "", True, False, "block", ())

    def response(self, decision=None, *, body=None):
        if body is None:
            body = json.dumps({"choices": [{"message": {"content": json.dumps(decision)}}]}).encode()
        response = MagicMock()
        response.__enter__.return_value.read.return_value = body
        return response

    def test_rejects_invalid_schema_without_coercion(self):
        valid = {"action": "block", "output": "", "reasons": []}
        invalid = [
            ({**valid, "reasons": "single reason"}, "reasons_not_string_array"),
            ({**valid, "reasons": [1]}, "reasons_not_string_array"),
            ({**valid, "action": []}, "invalid_action"),
            ({**valid, "action": "unknown"}, "invalid_action"),
            ({**valid, "output": 1}, "output_not_string"),
            ({"action": "block"}, "missing_decision_fields"),
            ([], "decision_not_object"),
        ]
        for decision, code in invalid:
            with self.subTest(code=code, decision=decision):
                with patch("urllib.request.urlopen", return_value=self.response(decision)):
                    with self.assertRaises(ModelEvaluationError) as raised:
                        self.adapter.run(self.case)
                self.assertEqual(raised.exception.error_type, "schema_error")
                self.assertEqual(raised.exception.code, code)

    def test_malformed_envelopes_are_schema_errors(self):
        for body in [b"not JSON", b"\xff", b"[]", b"{}", b'{"choices": []}',
                     b'{"choices": [{"message": {"content": "not JSON"}}]}',
                     b'{"choices": [{"message": {"content": null}}]}']:
            with self.subTest(body=body):
                with patch("urllib.request.urlopen", return_value=self.response(body=body)):
                    with self.assertRaises(ModelEvaluationError) as raised:
                        self.adapter.run(self.case)
                self.assertEqual(raised.exception.error_type, "schema_error")

    def test_transport_errors_have_fixed_safe_codes(self):
        for error in [TimeoutError("private transport details"),
                      urllib.error.URLError("private transport details"),
                      http.client.IncompleteRead(b"private response")]:
            with self.subTest(error=type(error).__name__):
                with patch("urllib.request.urlopen", side_effect=error):
                    with self.assertRaises(ModelEvaluationError) as raised:
                        self.adapter.run(self.case)
                self.assertEqual(raised.exception.error_type, "request_error")
                self.assertEqual(str(raised.exception), "request_failed")

    def test_errors_do_not_drop_cases_or_leak_failed_response(self):
        marker = "PRIVATE_RESPONSE_SENTINEL"
        responses = [
            self.response({"action": "block", "output": marker, "reasons": marker}),
            TimeoutError(marker),
            self.response({"action": "block", "output": marker, "reasons": ["policy"]}),
            self.response({"action": "allow", "output": marker, "reasons": []}),
        ]
        cases = [replace(self.case, case_id=f"test-{index}") for index in range(4)]
        with patch("urllib.request.urlopen", side_effect=responses) as request:
            result = evaluate(self.adapter, cases)
        self.assertEqual(request.call_count, 4)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["completed_cases"], 2)
        self.assertEqual(result["schema_error_rate"], 0.25)
        self.assertEqual(result["request_error_rate"], 0.25)
        self.assertEqual(result["error_rate"], 0.5)
        self.assertEqual(result["error_counts"], {"schema_error": 1, "request_error": 1})
        self.assertEqual(result["safety_pass_rate"], 0.25)
        self.assertEqual(result["attack_success_rate"], 0.25)
        self.assertEqual(result["categories"]["safety"]["total"], 4)
        self.assertIsNone(result["records"][0]["actual"])
        self.assertFalse(result["records"][0]["passed"])
        self.assertEqual(result["records"][0]["reasons"], [])
        self.assertEqual(result["records"][0]["error_code"], "reasons_not_string_array")
        with tempfile.TemporaryDirectory() as directory:
            write_reports([result], directory)
            for filename in ("results.json", "report.md"):
                self.assertNotIn(marker, (Path(directory) / filename).read_text(encoding="utf-8"))
            report = (Path(directory) / "report.md").read_text(encoding="utf-8")
            self.assertIn("Schema error rate", report)
            self.assertIn("25.00%", report)

    def test_all_error_cases_cannot_look_like_safety_passes(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("private")):
            result = evaluate(self.adapter, [self.case, replace(self.case, expected="allow")])
        self.assertEqual(result["error_rate"], 1)
        self.assertEqual(result["completed_cases"], 0)
        self.assertEqual(result["safety_pass_rate"], 0)
        self.assertEqual(result["benign_task_success_rate"], 0)
        self.assertEqual(result["attack_success_rate"], 0)

    def test_programming_errors_are_not_silently_swallowed(self):
        with patch.object(self.adapter, "run", side_effect=AttributeError("bug")):
            with self.assertRaises(AttributeError):
                evaluate(self.adapter, [self.case])

    def test_empty_evaluation_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one case"):
            evaluate(self.adapter, [])


if __name__ == "__main__":
    unittest.main()
