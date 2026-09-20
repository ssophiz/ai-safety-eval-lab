# Multilingual regression dataset card

`cases_multilingual.jsonl` is a deterministic Korean and English regression
fixture. It checks policy plumbing and error accounting; it is not a corpus of
60 independent attacks and does not support population-level model rankings.

## Composition

| Item | Korean | English | Total |
|---|---:|---:|---:|
| Records | 30 | 30 | 60 |
| Distinct case objects after removing only `id` | 10 | 10 | 20 |
| Distinct prompt strings | 6 | 6 | 12 |
| Categories | 6 | 6 | 6 shared |

The generator repeats templates to exercise report denominators. Some records
change only a synthetic identifier or a fabricated secret marker. Record count
therefore must not be presented as scenario diversity.

## Provenance and safety

Every record is authored synthetic data. The `DEMO_MULTI_*` strings are toy
markers, not credentials. The dataset contains no incident data, malware,
personal data, operational targets, or investigative material. Korean and
English prompts are paired by category, but no independent bilingual reviewer
has established equal difficulty.

## Reproduction

From the repository root:

```console
python tools/generate_multilingual_dataset.py
git diff --exit-code data/cases_multilingual.jsonl
```

The unit suite also compares `generate()` with the checked-in JSONL and asserts
the record, prompt, and distinct-input counts above.

## Limits

- The labels are authored policy expectations, not independently adjudicated truth.
- Template repetition creates dependent observations.
- Local model results are single recorded runs with model-specific quantization.
- This dataset does not measure forensic accuracy, semantic leakage, redaction quality, or tool execution.
