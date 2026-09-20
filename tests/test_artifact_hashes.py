import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VERIFIER = load_tool("verify_artifact_hashes")
CAPTURE = load_tool("capture_ollama_manifest")


class ArtifactHashTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifests = sorted(ROOT.glob("results/model-*-native/manifest.json"))
        self.assertEqual(len(self.manifests), 3)

    def copy_artifacts(self, newline):
        for source in self.manifests:
            target = self.root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            manifest = json.loads(source.read_bytes())
            for kind in ("dataset", "results"):
                path = self.root / manifest[kind]
                path.parent.mkdir(parents=True, exist_ok=True)
                data = (ROOT / manifest[kind]).read_bytes().replace(b"\r\n", b"\n")
                path.write_bytes(data.replace(b"\n", newline))

    def test_published_artifacts_verify_with_lf_and_crlf(self):
        for newline in (b"\n", b"\r\n"):
            with self.subTest(newline=newline):
                self.copy_artifacts(newline)
                for source in self.manifests:
                    VERIFIER.verify_manifest(self.root / source.relative_to(ROOT), self.root)

    def test_legacy_hashes_still_identify_crlf_capture_bytes(self):
        self.copy_artifacts(b"\r\n")
        for source in self.manifests:
            manifest = json.loads(source.read_bytes())
            for kind in ("dataset", "results"):
                data = (self.root / manifest[kind]).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), manifest[kind + "_sha256"])

    def test_normalization_preserves_other_bytes(self):
        data = '한글\r\n{"value": "\\r\\n"}\r\n'.encode("utf-8")
        digest = VERIFIER.sha256_lf(data)
        self.assertEqual(digest, hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest())
        for changed in (data + b" ", data[:-2], data.replace(b"\r\n", b"\r")):
            self.assertNotEqual(digest, VERIFIER.sha256_lf(changed))

    def test_changed_dataset_or_result_is_rejected(self):
        for kind in ("dataset", "results"):
            with self.subTest(kind=kind):
                self.copy_artifacts(b"\n")
                source = self.manifests[0]
                manifest = json.loads(source.read_bytes())
                artifact = self.root / manifest[kind]
                artifact.write_bytes(artifact.read_bytes() + b" ")
                with self.assertRaisesRegex(ValueError, kind + ": LF SHA-256 mismatch"):
                    VERIFIER.verify_manifest(self.root / source.relative_to(ROOT), self.root)

    def test_missing_artifact_is_rejected(self):
        self.copy_artifacts(b"\n")
        source = self.manifests[0]
        manifest = json.loads(source.read_bytes())
        (self.root / manifest["results"]).unlink()
        with self.assertRaises(FileNotFoundError):
            VERIFIER.verify_manifest(self.root / source.relative_to(ROOT), self.root)

    def test_unknown_normalization_is_rejected(self):
        self.copy_artifacts(b"\n")
        target = self.root / self.manifests[0].relative_to(ROOT)
        manifest = json.loads(target.read_bytes())
        manifest["hash_semantics"]["dataset_sha256_lf"] = "canonical_json"
        target.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported LF hash semantics"):
            VERIFIER.verify_manifest(target, self.root)

    def test_cli_success_and_failure_exit_codes(self):
        self.copy_artifacts(b"\r\n")
        command = [sys.executable, str(ROOT / "tools/verify_artifact_hashes.py"),
                   "--root", str(self.root)]
        good = subprocess.run(command, capture_output=True, text=True, cwd=self.root)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertEqual(good.stdout.count("OK "), 3)
        (self.root / "data/cases_multilingual.jsonl").write_bytes(b"{}\n")
        bad = subprocess.run(command, capture_output=True, text=True, cwd=self.root)
        self.assertEqual(bad.returncode, 1, bad.stdout + bad.stderr)
        self.assertIn("LF SHA-256 mismatch", bad.stdout)

    def test_cli_rejects_empty_repository(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/verify_artifact_hashes.py"),
             "--root", str(self.root)], capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("no manifests found", result.stderr)

    def test_capture_records_raw_and_portable_hashes(self):
        for newline in (b"\n", b"\r\n"):
            with self.subTest(newline=newline):
                dataset = self.root / "cases.jsonl"
                results = self.root / "results.json"
                output = self.root / "manifest.json"
                dataset.write_bytes(b'{"id": "test"}' + newline)
                results.write_bytes(json.dumps([
                    {"adapter": "ollama-native:test", "total": 1, "records": [{}]},
                ], indent=2).encode("utf-8").replace(b"\n", newline) + newline)
                argv = ["capture", "--model", "test", "--dataset", str(dataset),
                        "--results", str(results), "--output", str(output),
                        "--command", "test", "--source-revision", "test"]
                responses = [
                    {"models": [{"name": "test", "digest": "test", "details": {}}]},
                    {"version": "test"},
                ]
                with patch.object(sys, "argv", argv), patch.object(
                    CAPTURE.urllib.request, "urlopen",
                    side_effect=[io.BytesIO(json.dumps(value).encode()) for value in responses],
                ):
                    CAPTURE.main()
                manifest = json.loads(output.read_bytes())
                for kind, path in (("dataset", dataset), ("results", results)):
                    data = path.read_bytes()
                    self.assertEqual(manifest[kind + "_sha256"], hashlib.sha256(data).hexdigest())
                    self.assertEqual(manifest[kind + "_sha256_lf"], VERIFIER.sha256_lf(data))
                VERIFIER.verify_manifest(output, self.root)


if __name__ == "__main__":
    unittest.main()
