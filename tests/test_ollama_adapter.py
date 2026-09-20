import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from aisafety_eval.cli import main
from aisafety_eval.evaluator import evaluate
from aisafety_eval.model_adapter import ModelEvaluationError, OllamaNativeAdapter
from aisafety_eval.report import write_reports
from aisafety_eval.types import Case


class OllamaHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.requests.append((
            self.path,
            json.loads(self.rfile.read(int(self.headers["Content-Length"]))),
            self.headers.get("Authorization"),
        ))
        body = self.server.response_body
        self.send_response(self.server.response_status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


class OllamaAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), OllamaHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.endpoint = f"http://127.0.0.1:{self.server.server_port}"
        self.adapter = OllamaNativeAdapter(self.endpoint + "/", "qwen3:test", 2)
        self.case = Case("test-001", "safety", "Synthetic prompt", "Untrusted context",
                         False, "", True, False, "block", ())
        self.server.requests = []
        self.server.response_status = 200
        self.set_decision({"action": "block", "output": "Blocked.", "reasons": ["policy"]})

    def set_decision(self, decision):
        self.server.response_body = json.dumps({
            "message": {"content": json.dumps(decision), "thinking": "PRIVATE_THINKING"},
            "done": True,
        }).encode()

    def test_native_request_disables_thinking_and_streaming(self):
        with patch.dict(os.environ, {"AI_SAFETY_API_KEY": ""}):
            decision = self.adapter.run(self.case)
        path, payload, authorization = self.server.requests[0]
        self.assertEqual(path, "/api/chat")
        self.assertEqual(payload["model"], "qwen3:test")
        self.assertIs(payload["think"], False)
        self.assertIs(payload["stream"], False)
        self.assertEqual(payload["format"], "json")
        self.assertEqual(payload["options"], {"temperature": 0})
        self.assertNotIn("response_format", payload)
        self.assertNotIn("temperature", payload)
        self.assertIsNone(authorization)
        self.assertEqual(payload["messages"][0]["role"], "system")
        case_input = json.loads(payload["messages"][1]["content"])
        self.assertEqual(case_input["context"], self.case.context)
        self.assertIs(case_input["context_trusted"], False)
        self.assertNotIn("expected", case_input)
        self.assertEqual(decision.action, "block")
        self.assertEqual(decision.reasons, ("policy",))
        self.assertEqual(self.adapter.name, "ollama-native:qwen3:test")

    def test_strict_decision_errors_match_existing_adapter(self):
        valid = {"action": "block", "output": "", "reasons": []}
        invalid = [
            ({**valid, "reasons": "PRIVATE_RESPONSE"}, "reasons_not_string_array"),
            ({**valid, "reasons": [1]}, "reasons_not_string_array"),
            ({**valid, "action": []}, "invalid_action"),
            ({**valid, "output": 1}, "output_not_string"),
            ({"action": "block"}, "missing_decision_fields"),
            ([], "decision_not_object"),
        ]
        for decision, code in invalid:
            with self.subTest(code=code):
                self.set_decision(decision)
                with self.assertRaises(ModelEvaluationError) as raised:
                    self.adapter.run(self.case)
                self.assertEqual(raised.exception.error_type, "schema_error")
                self.assertEqual(raised.exception.code, code)

    def test_rejects_malformed_and_incomplete_native_envelopes(self):
        bodies = [
            (b"not JSON", "invalid_response_json"),
            (b"\xff", "invalid_response_json"),
            (b"[]", "invalid_response_envelope"),
            (b"{}", "invalid_response_envelope"),
            (b'{"done": false, "message": {"content": "{}"}}', "invalid_response_envelope"),
            (b'{"done": true, "message": {"content": null}}', "invalid_response_envelope"),
            (b'{"done": true, "message": {"content": "not JSON"}}', "invalid_response_envelope"),
            (b'{"done": true, "message": []}', "invalid_response_envelope"),
        ]
        for body, code in bodies:
            with self.subTest(body=body):
                self.server.response_body = body
                with self.assertRaises(ModelEvaluationError) as raised:
                    self.adapter.run(self.case)
                self.assertEqual(raised.exception.error_type, "schema_error")
                self.assertEqual(raised.exception.code, code)

    def test_http_failure_is_retained_without_private_details(self):
        self.server.response_status = 500
        self.server.response_body = b'{"error": "PRIVATE_SERVER_DETAIL"}'
        result = evaluate(self.adapter, [self.case, self.case])
        self.assertEqual(len(self.server.requests), 2)
        self.assertEqual(result["request_error_rate"], 1)
        self.assertEqual(result["completed_cases"], 0)
        self.assertEqual(result["records"][0]["error_code"], "request_failed")
        self.assertIsNone(result["records"][0]["actual"])
        self.assertNotIn("PRIVATE_SERVER_DETAIL", json.dumps(result))

    def test_authentication_and_response_text_are_not_written_to_reports(self):
        with patch.dict(os.environ, {"AI_SAFETY_API_KEY": "PRIVATE_API_KEY"}):
            result = evaluate(self.adapter, [self.case])
        self.assertEqual(self.server.requests[0][2], "Bearer PRIVATE_API_KEY")
        with tempfile.TemporaryDirectory() as directory:
            write_reports([result], directory)
            for filename in ("results.json", "report.md"):
                report = (Path(directory) / filename).read_text(encoding="utf-8")
                for marker in ("PRIVATE_API_KEY", "PRIVATE_THINKING", "Blocked."):
                    self.assertNotIn(marker, report)

    def test_cli_selects_native_protocol_and_writes_model_result(self):
        with tempfile.TemporaryDirectory() as directory:
            cases = Path(directory) / "cases.jsonl"
            cases.write_text(json.dumps({"id": "one", "category": "safety",
                                         "prompt": "Synthetic case", "expected": "block"}),
                             encoding="utf-8")
            output = Path(directory) / "results"
            argv = ["ai-safety-eval", "--cases", str(cases), "--out", str(output),
                    "--model-api", "ollama", "--model-endpoint", self.endpoint,
                    "--model", "qwen3:test", "--model-timeout", "2"]
            with patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()):
                main()
            results = json.loads((output / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(results[-1]["adapter"], "ollama-native:qwen3:test")
        self.assertEqual(results[-1]["completed_cases"], 1)
        self.assertEqual(self.server.requests[0][0], "/api/chat")


if __name__ == "__main__":
    unittest.main()
