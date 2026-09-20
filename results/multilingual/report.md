# AI Safety Evaluation Results

| Adapter | Cases | Attack success | Safety pass | Benign success | Mean latency |
|---|---:|---:|---:|---:|---:|
| baseline | 60 | 100.00% | 0.00% | 100.00% | 0.0011 ms |
| guarded | 60 | 0.00% | 100.00% | 100.00% | 0.0027 ms |

## Category results

### baseline

| Category | Passed | Total | Pass rate |
|---|---:|---:|---:|
| approval_boundary | 0 | 10 | 0.00% |
| benign | 10 | 10 | 100.00% |
| direct_injection | 0 | 10 | 0.00% |
| indirect_injection | 0 | 10 | 0.00% |
| secret_disclosure | 0 | 10 | 0.00% |
| unauthorized_tool | 0 | 10 | 0.00% |

### guarded

| Category | Passed | Total | Pass rate |
|---|---:|---:|---:|
| approval_boundary | 10 | 10 | 100.00% |
| benign | 10 | 10 | 100.00% |
| direct_injection | 10 | 10 | 100.00% |
| indirect_injection | 10 | 10 | 100.00% |
| secret_disclosure | 10 | 10 | 100.00% |
| unauthorized_tool | 10 | 10 | 100.00% |
