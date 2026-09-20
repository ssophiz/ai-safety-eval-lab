# Executive Summary

This project provides a reproducible safety evaluation pipeline for RAG and tool-using AI systems. It includes 120 synthetic cases covering benign behavior, direct and indirect prompt injection, synthetic-secret disclosure, unauthorized tools, and human-approval boundaries.

The same versioned dataset is applied to a permissive baseline and a guarded reference adapter. Reports track attack success, safety pass rate, benign-task success, category performance, and latency. The initial deterministic regression run shows a 100% attack success rate for the baseline and 0% for the guarded adapter while preserving all benign cases.

These scores validate the pipeline and reference rules only. They do not establish general model safety. The next milestone is integration with local open-source models, multilingual adaptive evaluations, repeated sampling, and human-review agreement.
