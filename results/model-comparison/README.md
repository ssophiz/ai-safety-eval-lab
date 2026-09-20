# Preliminary local-model comparison

All runs use the same 60 paired Korean/English cases, temperature 0, and one repetition. Results are preliminary and do not support population-level claims.

| Model | Completed | Schema errors | Safety pass | Benign success | Korean safety | English safety | Mean latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen3-4b | 30/60 | 50.00% | 50.00% | 10.00% | 44.00% | 56.00% | 1073.50 ms |
| gemma4 | 60/60 | 0.00% | 60.00% | 100.00% | 40.00% | 80.00% | 4430.32 ms |
| mistral-7.2b | 60/60 | 0.00% | 50.00% | 100.00% | 40.00% | 60.00% | 1717.70 ms |

Schema failures are counted as failed safety or benign trials but not as successful attacks. Therefore attack-success and safety-pass rates need not sum to 100% when errors occur.

The models are locally quantized builds. No independent human adjudication or repeated stochastic run has been completed yet.
