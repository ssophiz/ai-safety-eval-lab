# AI Safety Evaluation Lab

A dependency-free Python harness for reproducible safety evaluation of RAG and tool-using AI systems. It runs versioned cases against baseline and guarded adapters, then emits JSON and Markdown reports covering safety failures and benign-task regressions.

> Status: deterministic reference implementation for testing an evaluation pipeline. Replace the included adapters with a local or hosted system when evaluating a real deployment.

## What it evaluates

- Direct and indirect prompt injection
- Instructions embedded in untrusted RAG content
- Synthetic secret and personal-data disclosure
- Tool authorization boundaries
- Excessive agency and human-approval requirements
- Benign-task usability after controls are applied

The dataset contains 120 synthetic cases: 20 benign cases and 20 cases for each of five safety categories.

## Quick start

Linux and macOS:

```bash
python tools/generate_dataset.py
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aisafety_eval.cli --cases data/cases.jsonl --out results
```

PowerShell:

```powershell
python tools/generate_dataset.py
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m aisafety_eval.cli --cases data/cases.jsonl --out results
```

## Reference result

| Adapter | Attack success | Safety pass | Benign-task success |
|---|---:|---:|---:|
| Baseline | 100.00% | 0.00% | 100.00% |
| Guarded | 0.00% | 100.00% | 100.00% |

These values test the evaluator with deterministic reference adapters. They do not establish production security or general model safety. See the generated [Markdown report](results/report.md) and [JSON result](results/results.json).

## Metrics

- Attack success rate: proportion of unsafe cases that were not blocked or redacted
- Safety pass rate: proportion of unsafe cases handled as expected
- Benign-task success rate: proportion of safe cases that remained usable
- Per-category pass rate
- Mean evaluation latency

## Documentation

- [Threat model](docs/THREAT_MODEL.md)
- [Korean evaluation report](docs/REPORT_KO.md)
- [English executive summary](docs/EXECUTIVE_SUMMARY_EN.md)
- [Contribution guide](CONTRIBUTING.md)

Applicable cases map to the OWASP Top 10 for LLM Applications 2025, MITRE ATLAS, and the NIST AI Risk Management Framework.

## Repository layout

```text
data/cases.jsonl       Versioned synthetic evaluation set
src/aisafety_eval/     Adapters, controls, evaluator, reports, and CLI
tests/                 Reproducible checks
tools/                 Dataset generator
docs/                  Threat model and bilingual reports
results/               Reference JSON and Markdown outputs
```

## Responsible use

All included credentials, accounts, documents, and personal data are synthetic. Do not add real credentials, personal data, confidential prompts, malware, or operational law-enforcement material.
