import argparse
import hashlib
import json
import platform
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args()

    endpoint = args.endpoint.rstrip("/")
    with urllib.request.urlopen(f"{endpoint}/api/tags", timeout=10) as response:
        models = json.load(response)["models"]
    model = next((item for item in models if item["name"] == args.model), None)
    if model is None:
        raise SystemExit(f"model not found: {args.model}")

    with urllib.request.urlopen(f"{endpoint}/api/version", timeout=10) as response:
        ollama_version = json.load(response)["version"]

    data = args.dataset.read_bytes()
    result_bytes = args.results.read_bytes()
    result_payload = json.loads(result_bytes)
    if not isinstance(result_payload, list) or not result_payload:
        raise SystemExit("results must contain a non-empty adapter result list")
    adapter_result = result_payload[-1]
    expected_adapter = f"ollama-native:{args.model}"
    if adapter_result.get("adapter") != expected_adapter:
        raise SystemExit(f"expected adapter {expected_adapter}")
    case_count = sum(1 for line in data.decode("utf-8").splitlines() if line.strip())
    if adapter_result.get("total") != case_count or len(adapter_result.get("records", [])) != case_count:
        raise SystemExit("result case count does not match dataset")

    manifest = {
        "experiment_status": "verified_completed_single_run" if args.repetitions == 1 else "verified_completed_repeated_run",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_revision": args.source_revision,
        "model": model["name"],
        "model_digest": model["digest"],
        "parameter_size": model["details"].get("parameter_size"),
        "quantization": model["details"].get("quantization_level"),
        "dataset": args.dataset.as_posix(),
        "dataset_sha256": hashlib.sha256(data).hexdigest(),
        "dataset_sha256_lf": hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest(),
        "results": args.results.as_posix(),
        "results_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "results_sha256_lf": hashlib.sha256(result_bytes.replace(b"\r\n", b"\n")).hexdigest(),
        "hash_semantics": {
            "dataset_sha256": "capture_bytes",
            "results_sha256": "capture_bytes",
            "dataset_sha256_lf": "crlf_to_lf_bytes",
            "results_sha256_lf": "crlf_to_lf_bytes",
        },
        "case_count": case_count,
        "temperature": 0,
        "thinking": False,
        "repetitions": args.repetitions,
        "python": sys.version.split()[0],
        "ollama": ollama_version,
        "platform": platform.platform(),
        "command": args.command,
        "limitations": [
            "local quantized model",
            "no independent human adjudication",
            "single run" if args.repetitions == 1 else "limited repetitions",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
