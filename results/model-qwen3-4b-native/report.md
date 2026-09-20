# AI Safety Evaluation Results

| Adapter | Cases | Attack success | Safety pass | Benign success | Mean latency |
|---|---:|---:|---:|---:|---:|
| baseline | 60 | 100.00% | 0.00% | 100.00% | 0.0008 ms |
| guarded | 60 | 0.00% | 100.00% | 100.00% | 0.0021 ms |
| ollama-native:qwen3:4b | 60 | 8.00% | 50.00% | 10.00% | 1073.5017 ms |

## Model response reliability

| Adapter | Completed | Errors | Schema error rate | Request error rate |
|---|---:|---:|---:|---:|
| baseline | 60 | 0.00% | 0.00% | 0.00% |
| guarded | 60 | 0.00% | 0.00% | 0.00% |
| ollama-native:qwen3:4b | 30 | 50.00% | 50.00% | 0.00% |

Errors are failed attempts, not observed attack successes. All rates include failed attempts in their denominators; attack success and safety pass need not sum to 100% when errors occur.

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

### ollama-native:qwen3:4b

| Category | Passed | Total | Pass rate |
|---|---:|---:|---:|
| approval_boundary | 9 | 10 | 90.00% |
| benign | 1 | 10 | 10.00% |
| direct_injection | 0 | 10 | 0.00% |
| indirect_injection | 7 | 10 | 70.00% |
| secret_disclosure | 0 | 10 | 0.00% |
| unauthorized_tool | 9 | 10 | 90.00% |
