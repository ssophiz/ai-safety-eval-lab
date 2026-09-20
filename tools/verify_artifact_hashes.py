"""Verify published artifacts across LF and CRLF checkouts (standard library only)."""

import argparse
import hashlib
import json
from pathlib import Path


def sha256_lf(data: bytes) -> str:
    """Replace CRLF with LF; preserve all other bytes, including lone CR and EOF."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def verify_manifest(path: Path, root: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    root = root.resolve()
    for artifact in ("dataset", "results"):
        if manifest["hash_semantics"][artifact + "_sha256"] != "capture_bytes":
            raise ValueError(f"{artifact}: missing capture-byte hash label")
        if manifest["hash_semantics"][artifact + "_sha256_lf"] != "crlf_to_lf_bytes":
            raise ValueError(f"{artifact}: unsupported LF hash semantics")
        artifact_path = (root / manifest[artifact]).resolve()
        if not artifact_path.is_relative_to(root):
            raise ValueError(f"{artifact}: path must be within the repository root")
        actual = sha256_lf(artifact_path.read_bytes())
        expected = manifest[artifact + "_sha256_lf"]
        if actual != expected:
            raise ValueError(f"{artifact}: LF SHA-256 mismatch: expected {expected}, got {actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="*", type=Path,
                        help="manifest paths relative to --root (default: all native runs)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifests = args.manifests or sorted(root.glob("results/model-*-native/manifest.json"))
    if not manifests:
        parser.error("no manifests found")
    failed = False
    for path in manifests:
        path = root / path
        try:
            verify_manifest(path, root)
        except (OSError, ValueError, KeyError, TypeError) as error:
            print(f"FAIL {path}: {error}")
            failed = True
        else:
            print(f"OK {path}: dataset and results LF SHA-256 verified")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
