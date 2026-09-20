# Threat Model

## System

The evaluated system receives a user prompt, retrieves optional context, and may request a tool. A policy layer decides whether to allow, block, or redact the response.

## Assets

- System and developer instructions
- Credentials and personal data
- Tool permissions
- Retrieved documents and their provenance
- Human approval boundaries
- Evaluation results and audit logs

## Trust boundaries

1. User input enters the application.
2. Retrieved documents cross from external storage into model context.
3. Model output crosses into tools and downstream systems.
4. High-impact actions cross a human-approval boundary.

## Evaluated threats

| Threat | Expected control | Reference |
|---|---|---|
| Direct prompt injection | Instruction hierarchy and policy decision | OWASP LLM01 |
| Indirect prompt injection | Treat retrieved instructions as untrusted data | OWASP LLM01, MITRE ATLAS |
| Secret disclosure | Output detection and redaction | OWASP LLM02 |
| Unauthorized tool use | Capability allowlist and least privilege | OWASP LLM06 |
| Excessive agency | Human approval for high-impact actions | OWASP LLM06, NIST AI RMF |
| Safety regression | Benign-task success measurement | NIST AI RMF Measure |

## Assumptions and limits

- The reference adapter uses deterministic rules and is not a substitute for model-level controls.
- Synthetic cases do not predict every real deployment failure.
- A perfect score on this dataset is not evidence of general safety.
- Real evaluations should add adaptive attacks, multilingual cases, model variance, and production telemetry.
