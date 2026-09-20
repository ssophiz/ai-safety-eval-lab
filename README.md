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

The core dataset contains 120 synthetic cases: 20 benign cases and 20 cases for each of five safety categories. A separate balanced dataset contains 60 Korean and English regression cases.

## Quick start

Linux and macOS:

```bash
python tools/generate_dataset.py
python tools/generate_multilingual_dataset.py
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m aisafety_eval.cli --cases data/cases.jsonl --out results
```

PowerShell:

```powershell
python tools/generate_dataset.py
python tools/generate_multilingual_dataset.py
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

## Evaluate a local or hosted model

The optional adapter supports OpenAI-compatible chat-completions endpoints. It is disabled by default, so the test suite and reference evaluation require no network access or API key.

```bash
PYTHONPATH=src python -m aisafety_eval.cli \
  --model-endpoint http://127.0.0.1:11434 \
  --model local-model \
  --model-timeout 60 \
  --out results/model-run
```

If an endpoint requires authentication, place the token in `AI_SAFETY_API_KEY`. The adapter reads it only when sending the request and does not write it to reports or logs.

For Ollama, select its native `/api/chat` protocol explicitly. For example, with
`qwen3:8b` already installed in your running local Ollama service:

```bash
PYTHONPATH=src python -m aisafety_eval.cli \
  --model-api ollama \
  --model-endpoint http://127.0.0.1:11434 \
  --model qwen3:8b \
  --model-timeout 120 \
  --out results/model-qwen3-native
```

PowerShell (after setting `$env:PYTHONPATH = "src"`):

```powershell
python -m aisafety_eval.cli --model-api ollama --model-endpoint http://127.0.0.1:11434 --model qwen3:8b --model-timeout 120 --out results/model-qwen3-native
```

The native adapter sends `think: false`, `stream: false`, `format: "json"`,
and `options: {"temperature": 0}` on every request. Disabling thinking is
intended for models that support this option, such as Qwen3. Temperature zero
reduces sampling variation; it does not guarantee identical outputs across
model versions, runtimes, or hardware. Record those details for comparisons.
See the [Ollama chat API](https://docs.ollama.com/api/chat).

Native results use the adapter name `ollama-native:<model>`. The adapter requires
a completed response (`done: true`), reads only `message.content`, and applies
the same strict decision validation and error codes described below. Thinking
text and raw responses are not written to reports. Without `--model-api ollama`,
the existing OpenAI-compatible protocol remains the default.

The model must return a JSON object with `action`, `output`, and `reasons`. Valid actions are `allow`, `block`, and `redact`.

The schema is strict: `output` is a string and `reasons` is an array of strings.
A string-valued `reasons` (including a single reason) is recorded as a schema
error rather than silently coerced into a valid decision. Missing fields,
invalid actions, and malformed JSON are also schema errors. HTTP and connection
failures are request errors. Each failed case is retained and evaluation
continues with the next case, without retrying or dropping it.

JSON records contain `error_type` and a fixed `error_code`; failed cases have
`actual: null`, `passed: false`, and empty `reasons`. The harness does not write
the raw HTTP response, rejected model text, or exception messages to reports.
For valid decisions, parsed reasons are retained as before. Summary JSON and
Markdown include schema and request error rates. Inspect these alongside
safety scores: an unavailable model cannot establish safety.

## Preliminary local-model experiment

Three locally installed quantized models were each run once against the same 60 Korean/English regression records through the Ollama native adapter. Temperature was zero and thinking was disabled.

| Model | Valid decisions | Schema errors | Safety pass | Benign success | Korean safety | English safety |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3 4B Q4_K_M | 30/60 | 50.00% | 50.00% | 10.00% | 44.00% | 56.00% |
| Gemma4 8B Q4_K_M | 60/60 | 0.00% | 60.00% | 100.00% | 40.00% | 80.00% |
| Mistral 7.2B Q4_K_M | 60/60 | 0.00% | 50.00% | 100.00% | 40.00% | 60.00% |

These are single-run policy-decision agreement results, not general model rankings. Qwen's 30 schema failures count as failed trials and make its low observed attack-success rate unsuitable as evidence of stronger safety. The 60 records repeat authored templates; excluding IDs, each language has 10 unique inputs and six unique prompts. Parsed model-generated reasons are retained, but raw HTTP envelopes, generated output, and thinking traces are not.

See the [comparison](results/model-comparison/README.md), [independent recomputation](docs/MODEL_RESULTS_AUDIT.md), and per-run manifests for exact digests, commands, and limitations.

## Metrics

- Attack success rate: valid decisions that differ from the expected action, divided by all unsafe cases attempted (a synthetic label mismatch proxy, not a confirmed exploit)
- Safety pass rate: proportion of unsafe cases handled as expected
- Benign-task success rate: proportion of safe cases that remained usable
- Per-category pass rate
- Mean evaluation latency
- Schema error rate: invalid responses divided by all cases attempted
- Request error rate: failed model requests divided by all cases attempted
- Error rate, error counts by type, and number of completed decisions

Safety, benign-task, and category pass rates include error cases as failed
attempts in their denominators. Schema and request errors are not counted as
observed attack successes, so attack success plus safety pass can be below
100%. No automatic retries are made. These metrics describe this versioned
synthetic dataset; a low attack success rate with high errors is not evidence
of a secure model.

## Documentation

- [Threat model](docs/THREAT_MODEL.md)
- [Korean evaluation report](docs/REPORT_KO.md)
- [English executive summary](docs/EXECUTIVE_SUMMARY_EN.md)
- [Multilingual regression report](docs/MULTILINGUAL_REPORT.md)
- [Contribution guide](CONTRIBUTING.md)

Applicable cases map to the OWASP Top 10 for LLM Applications 2025, MITRE ATLAS, and the NIST AI Risk Management Framework.

## Repository layout

```text
data/cases.jsonl       Versioned synthetic evaluation set
data/cases_multilingual.jsonl  Korean and English regression set
src/aisafety_eval/     Adapters, controls, evaluator, reports, and CLI
tests/                 Reproducible checks
tools/                 Dataset generator
docs/                  Threat model and bilingual reports
results/               Reference JSON and Markdown outputs
```

## Responsible use

All included credentials, accounts, documents, and personal data are synthetic. Do not add real credentials, personal data, confidential prompts, malware, or operational law-enforcement material.
