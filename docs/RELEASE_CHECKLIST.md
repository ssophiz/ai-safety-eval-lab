# Model-results release checklist

- [x] Scan publication candidates for common secret and local-path patterns.
- [x] Confirm 60 unique IDs in every run.
- [x] Recompute overall and language metrics from case records.
- [x] Include block and redact cases in safety rates.
- [x] Keep schema failures in the denominator.
- [x] Add regression tests for transport, schema, and language aggregation errors.
- [x] Document retained model-generated reasons.
- [x] Describe the experiment as synthetic policy-decision evaluation.
- [x] Publish the tested harness revision (`e6e1aac2b3068c5f77e6f3743aa7c1ad6db8b2fb`).
- [x] Regenerate verified manifests against that public revision.
- [ ] Review the final staged result files and hashes.
- [ ] Push the results commit and verify the remote revision.
- [ ] Close the model-backed evaluation issue only after remote verification.
