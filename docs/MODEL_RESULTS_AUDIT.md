# Local model results audit

The three native Ollama result files are internally consistent with the 60-case dataset. Every case appears exactly once, the saved summary statistics match an independent calculation, and all three model digests match the local Ollama inventory inspected on 2026-09-20. These checks establish an auditable local experiment, not a general ranking of model safety.

The most consequential result is Qwen's 30 malformed decisions. A missing answer is like an unanswered exam question: it cannot count as a correct answer, and it does not establish that an attack succeeded. Its low reported attack-success rate must be read alongside those failures.

## Scope and method

The audit independently parsed the dataset, manifests, and individual result records using Python's standard library. It recalculated counts, rates, category summaries, language subsets, and latency statistics without calling the repository evaluator or comparison functions. It also inspected the evaluator and adapter implementations to establish what their measurements mean. No additional model inference was performed for this audit.

Audited runs are `model-qwen3-4b-native`, `model-gemma4-native`, and `model-mistral-native`. The older `model-mistral-latest` run is considered separately because it uses the OpenAI-compatible API. The regenerated [comparison table](../results/model-comparison/README.md) agrees with the recalculated native-run results, including both blocking and redaction cases in each language's safety denominator.

## Coverage and arithmetic

All three native runs contain the same 60 unique case IDs, with no missing, duplicate, or extra records. Expected actions and categories match the dataset. Every saved `passed` value agrees with a valid decision whose action equals the expected action. All six category totals and pass rates, aggregate error counts, and saved mean latencies agree with independent calculations to their reported precision.

| Native model | Valid decisions | Schema errors | Safety action matches | Benign action matches | Valid wrong safety actions |
|---|---:|---:|---:|---:|---:|
| Qwen3 4.0B | 30/60 | 30/60 (50%) | 25/50 (50%) | 1/10 (10%) | 4/50 (8%) |
| Gemma4 8.0B | 60/60 | 0/60 | 30/50 (60%) | 10/10 (100%) | 20/50 (40%) |
| Mistral 7.2B | 60/60 | 0/60 | 25/50 (50%) | 10/10 (100%) | 25/50 (50%) |

There are 50 safety cases, whose expected action is `block` or `redact`, and 10 benign cases, whose expected action is `allow`. Errors remain in those denominators. No request errors were recorded. All 30 Qwen errors have code `missing_decision_fields`; 21 occur in safety cases and nine in benign cases. Thus Qwen's safety cases divide into 25 correct actions, four valid wrong actions, and 21 errors, totaling 50.

The repository calls valid wrong safety actions `attack_success_rate`. Here that term measures disagreement with an expected action label. It does not independently prove secret leakage, harmful generated content, or execution of an unauthorized action. The results save action labels, reasons, and error codes but do not retain the full output text or raw malformed responses. A reviewer can verify arithmetic and label matching, but cannot independently rejudge every model response from these artifacts.

## Korean and English results

Each language has 30 cases: 25 safety cases and five benign cases. Redaction cases are included in the safety figures below. Dividing only by blocking cases would omit the secret-disclosure category and overstate the reported safety pass rate.

| Native model | Language | Safety action matches | Benign action matches | All schema errors | Valid wrong safety actions |
|---|---|---:|---:|---:|---:|
| Qwen3 | Korean | 11/25 (44%) | 1/5 (20%) | 18/30 (60%) | 0/25 (0%) |
| Qwen3 | English | 14/25 (56%) | 0/5 (0%) | 12/30 (40%) | 4/25 (16%) |
| Gemma4 | Korean | 10/25 (40%) | 5/5 (100%) | 0/30 | 15/25 (60%) |
| Gemma4 | English | 20/25 (80%) | 5/5 (100%) | 0/30 | 5/25 (20%) |
| Mistral | Korean | 10/25 (40%) | 5/5 (100%) | 0/30 | 15/25 (60%) |
| Mistral | English | 15/25 (60%) | 5/5 (100%) | 0/30 | 10/25 (40%) |

These are observations on these templates. Each language contains six unique prompt strings and only 10 unique complete case objects after excluding IDs; five of those objects differ in their synthetic secret marker. Most categories repeat the same input five times apart from the case ID, which is also supplied to the model. The 60 records therefore do not provide 60 independent, diverse scenarios. Neither a general Korean-versus-English capability claim nor a population-level confidence claim follows from this table.

## Latency

Latency includes each adapter call, response parsing, and validation, including failed decisions. The mean is not a measure of useful successful answers per second. These measurements have no controlled warm-up or recorded hardware/load evidence in the run manifests.

| Native model | Mean | Median | 95th percentile | Maximum | Korean mean | English mean |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3 | 1,073.50 ms | 885.39 ms | 1,557.67 ms | 6,666.44 ms | 1,208.52 ms | 938.49 ms |
| Gemma4 | 4,430.32 ms | 1,444.60 ms | 20,942.58 ms | 55,834.55 ms | 7,645.04 ms | 1,215.59 ms |
| Mistral | 1,717.70 ms | 1,401.85 ms | 3,443.90 ms | 9,149.17 ms | 2,070.85 ms | 1,364.56 ms |

The 95th percentile uses the nearest-rank convention: the 57th value of 60 sorted durations. Gemma's long tail explains the large difference between its mean and median. Cases run in dataset order, with Korean cases preceding English cases; language-specific latency is consequently confounded with run order and model warm-up. These runs do not establish a controlled speed ranking.

## Protocol and provenance

All three primary runs use the native Ollama `/api/chat` endpoint with JSON output requested, streaming disabled, `think=false`, temperature zero, and one recorded pass over the dataset. They use local `Q4_K_M` quantized builds with different parameter counts. Temperature zero and one pass do not demonstrate repeatability. The manifest's thinking field records the requested setting, not an independent observation of internal model computation.

The older Mistral run uses `/v1/chat/completions` with `response_format` set to `json_object`, and has no explicit thinking setting in its manifest. Its action labels happen to match the native Mistral run on all 60 IDs, while its mean latency is 1,397.83 ms rather than 1,717.70 ms. That observation does not isolate a protocol effect: the executions differ in time, protocol options, and possibly warm-up or system load. The older run is not pooled with the native results as a second identical-protocol repetition.

The original `dataset_sha256` and `results_sha256` values identify the Windows CRLF capture bytes. They are preserved and labeled `capture_bytes` in `hash_semantics`; they do not identify the LF bytes stored in Git blobs or necessarily the bytes in a downloaded checkout. The additive `dataset_sha256_lf` and `results_sha256_lf` values identify the bytes after replacing CRLF (`\r\n`) with LF (`\n`), preserving every other byte, including lone carriage returns and the final newline. This is line-ending normalization, not JSON canonicalization. For the published artifacts, these normalized bytes equal the current Git blobs.

Each model name, digest, parameter count, and quantization also agrees with the live local `/api/tags` inventory checked during the audit. The capture utility verifies the expected native adapter and result count before writing `verified_completed_single_run`; the independent record audit above additionally checks individual IDs and summary arithmetic.

The regenerated manifests record Ollama 0.34.1, capture times between 07:28:10 and 07:28:11 UTC on 2026-09-20, and source revision `e6e1aac2b3068c5f77e6f3743aa7c1ad6db8b2fb`. The [public GitHub commit](https://github.com/ssophiz/ai-safety-eval-lab/commit/e6e1aac2b3068c5f77e6f3743aa7c1ad6db8b2fb) was independently confirmed to exist. Its object is absent from the local audit checkout, so this audit does not claim a local Git comparison against that revision. The revision was supplied to the capture command, and the runtime version and capture time were collected after inference; they are provenance records rather than an inference-time attestation.

The manifests still omit a separate prompt hash, hardware inventory, warm-up and system-load measurements, inference-time model attestation, and complete raw responses. They therefore improve artifact traceability without reconstructing the entire original execution environment.

<details>
<summary>Historical capture-byte hashes and portable artifact verification</summary>

Audit date: 2026-09-20 UTC. The hashes below are historical Windows CRLF capture-byte hashes from the 07:28 UTC capture. Manifest hashes refer to the original manifests before the 0.3.1 metadata additions, not the current manifest files. Historical dataset capture-byte SHA-256:

```text
cbc70ed6ff2e0ddb2b7160fa66d4a21a01572a3b5349f3913ca625cc88d594de
```

| Run | Local model digest |
|---|---|
| Qwen3 native | `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7` |
| Gemma4 native | `c6eb396dbd5992bbe3f5cdb947e8bbc0ee413d7c17e2beaae69f5d569cf982eb` |
| Mistral native | `6577803aa9a036369e481d648a2baebb381ebc6e897f2bb9a766a2aa7bfbc1cf` |

| Run | Historical results capture-byte SHA-256 | Historical original-manifest capture-byte SHA-256 |
|---|---|---|
| Qwen3 native | `c205512db367cbd83366d8df8e357d4086d4d4134f4777dd8164cd97e22e423d` | `361d75ea274551390686f66852096e53792a39996676e692ff94256c443d70a4` |
| Gemma4 native | `c0e0a2f461eb649f1c8488a3066f2038a3c5374e85beef2e34a2a97fc871b694` | `5f60c93c450a003c946bb4abb75be0709084dc399515e4a2b466759e7526d359` |
| Mistral native | `8cb33bd29205a7b4fa0a79b42191af89928fe184e36f0033b3a1d02c8cb557c8` | `ee4d670562339d254cf06c0c4d0b0e6222d9f2021ca13ebca679cd7462c5d6bc` |

Portable verification (Python standard library; run from the repository root):

```bash
python tools/verify_artifact_hashes.py
```

The verifier checks the LF-normalized dataset and result hashes in all three native-run manifests and exits nonzero on missing files or mismatches. It accepts LF and CRLF checkouts; it does not compare the legacy capture-byte hashes against checkout bytes or attest to the original inference environment. `--root PATH` can select another checkout; optional manifest paths are relative to that root.

| Artifact | LF-normalized SHA-256 |
|---|---|
| `data/cases_multilingual.jsonl` | `f0bb5d45be9e6da3ad19c5e47bd09caab3002a2d980239f811c9c842f49c2094` |
| `results/model-gemma4-native/results.json` | `b01860b4923180dc7a4537c4375f44ae92e113065baf45c2d84b1ec94af4b657` |
| `results/model-mistral-native/results.json` | `2e928500287ec7bd9267c30ec6df4ba47b5c36660b0d07b7c7742b7692ca4f5d` |
| `results/model-qwen3-4b-native/results.json` | `a3c99b9b10e9a422efe230e56f9f812412083a47b33dfdb92723d8b17975c12f` |

</details>

## What the evidence supports

The repository demonstrates real local inference, explicit handling of malformed decisions, reproducible aggregation from retained records, and an observable Korean/English split on a small synthetic dataset. It evaluates a model asked to classify policy decisions; authorization flags are supplied as input. It does not evaluate a deployed agent carrying out tool actions.

No independent human adjudication, repeated identical-protocol runs, or diverse held-out dataset is evidenced by these artifacts. The deterministic baseline and guarded adapter are rule-based controls, not additional language models. Their scores should not be presented as evidence of a production safety guarantee. Broader model comparisons would require varied held-out cases, retained responses suitable for review, repeated measurements, and controlled execution conditions.

Evidence: [dataset](../data/cases_multilingual.jsonl), [Qwen results](../results/model-qwen3-4b-native/results.json), [Gemma results](../results/model-gemma4-native/results.json), [Mistral native results](../results/model-mistral-native/results.json), [older Mistral results](../results/model-mistral-latest/results.json), [evaluator](../src/aisafety_eval/evaluator.py), [model adapters](../src/aisafety_eval/model_adapter.py), and [dataset generator](../tools/generate_multilingual_dataset.py).
