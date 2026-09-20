# AI Safety Evaluation Results

| Adapter | Cases | Attack success | Safety pass | Benign success | Mean latency |
|---|---:|---:|---:|---:|---:|
| baseline | 120 | 100.00% | 0.00% | 100.00% | 0.0009 ms |
| guarded | 120 | 0.00% | 100.00% | 100.00% | 0.0047 ms |

## Category results

### baseline

| Category | Passed | Total | Pass rate |
|---|---:|---:|---:|
| benign | 20 | 20 | 100.00% |
| direct_prompt_injection | 0 | 20 | 0.00% |
| human_approval | 0 | 20 | 0.00% |
| indirect_prompt_injection | 0 | 20 | 0.00% |
| secret_disclosure | 0 | 20 | 0.00% |
| tool_authorization | 0 | 20 | 0.00% |

### guarded

| Category | Passed | Total | Pass rate |
|---|---:|---:|---:|
| benign | 20 | 20 | 100.00% |
| direct_prompt_injection | 20 | 20 | 100.00% |
| human_approval | 20 | 20 | 100.00% |
| indirect_prompt_injection | 20 | 20 | 100.00% |
| secret_disclosure | 20 | 20 | 100.00% |
| tool_authorization | 20 | 20 | 100.00% |
