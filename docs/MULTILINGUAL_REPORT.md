# Multilingual Safety Regression Report

## Scope

The optional regression set contains 60 synthetic cases split evenly between Korean and English. Each language contributes five cases to each of six categories: benign requests, direct injection, indirect injection, synthetic secret disclosure, unauthorized tool use, and human-approval boundaries.

## Reference results

| Adapter | Cases | Attack success | Safety pass | Benign-task success |
|---|---:|---:|---:|---:|
| Baseline | 60 | 100.00% | 0.00% | 100.00% |
| Guarded | 60 | 0.00% | 100.00% | 100.00% |

These deterministic results verify the multilingual evaluation path and reference rules only. They are not evidence that a production model is generally safe.

## 한국어 요약

별도 회귀 데이터는 한국어 30건과 영어 30건으로 구성된다. 정상 요청, 직접·간접 프롬프트 인젝션, 합성 비밀정보 노출, 미승인 도구 사용, 사람 승인 경계를 언어별로 동일하게 포함한다.

기준선 구현의 공격 성공률은 100.00%, 방어형 참조 구현은 0.00%였으며 두 구현 모두 정상 과업 성공률은 100.00%였다. 이 결과는 고정된 합성 데이터와 결정론적 규칙의 회귀 검증 결과이며 실제 모델의 일반적인 안전성을 증명하지 않는다.
