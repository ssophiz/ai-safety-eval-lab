# AI Safety Evaluation Lab

A dependency-free evaluation harness for RAG and tool-using AI systems. It measures safety failures and normal-task regressions before and after controls are applied.

## Why this exists

Safety claims need reproducible evidence. This repository stores versioned test cases, runs the same cases against a baseline and a guarded adapter, and generates JSON and Markdown reports.

The included adapters are deterministic reference implementations. They make the evaluation pipeline testable without API keys. Replace them with a local or hosted model adapter when evaluating a real system.

## Coverage

- Direct and indirect prompt injection
- Untrusted RAG instructions
- Secret and personal-data disclosure
- Tool authorization boundaries
- Excessive agency and approval requirements
- Benign-task regression

The taxonomy maps cases to OWASP Top 10 for LLM Applications 2025 and MITRE ATLAS where applicable.

## Run

```bash
python tools/generate_dataset.py
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aisafety_eval.cli --cases data/cases.jsonl --out results
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python tools/generate_dataset.py
python -m unittest discover -s tests -v
python -m aisafety_eval.cli --cases data/cases.jsonl --out results
```

## Metrics

- Attack success rate: unsafe cases that the system failed to block or redact
- Safety pass rate: unsafe cases handled as expected
- Benign task success rate: safe cases that remained usable
- Per-category pass rate
- Mean evaluation latency

## Repository layout

```text
data/cases.jsonl          Versioned evaluation set
src/aisafety_eval/        Adapters, controls, evaluator, CLI
tests/                    Runnable checks
docs/                     Threat model and reports
```

## Responsible use

The cases use synthetic secrets, accounts, and documents. Do not add real credentials, personal data, confidential prompts, or operational law-enforcement material.
