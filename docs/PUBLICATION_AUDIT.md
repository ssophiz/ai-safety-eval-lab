# Publication audit

Audit date: 2026-09-20

The model-backed results may be published as preliminary synthetic policy-decision experiments. They do not establish production safety, disclosure prevention, redaction quality, tool-execution safety, or statistical superiority.

## Passed checks

- No common API-key, private-key, email, or local user-path patterns were found in the publication candidates.
- Every native model run contains all 60 case IDs without duplicates.
- Dataset and model digests match the local Ollama registry.
- Schema failures remain in the denominator and are reported separately.
- Korean and English safety rates include both `block` and `redact` expectations.
- Raw HTTP envelopes, generated output, and thinking traces are not stored.

## Disclosed limitations

- Parsed model-generated `reasons` are retained verbatim. The inputs are synthetic and the retained reasons were scanned for common sensitive-data patterns.
- The evaluator scores the policy decision label. It does not inspect generated output for semantic leakage or verify whether a tool executed.
- Each observation is one temperature-zero run against a local quantized model. Temperature zero does not prove determinism.
- The 60 records contain repeated templates. Excluding IDs, each language has 10 unique inputs and six unique prompts.
- Qwen produced 30 schema failures. Its low observed attack-success rate cannot be interpreted as stronger safety.
- Latency includes the local host and is not a hardware-independent model ranking.

## Release requirement

Each published run must include a manifest that validates the adapter name and case count, binds the dataset and result files with SHA-256, and records the public source revision, model digest, Ollama version, command, and capture time.
