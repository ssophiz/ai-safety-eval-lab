# 논문 구성과 작성 준비

작업 제목: **Evidence Provenance Checks in Korean and English Multi-Agent Analysis: A Controlled Evaluation Protocol**

국문 제목: **한국어·영어 멀티에이전트 분석에서 증거 출처 확인의 효과를 평가하는 통제 실험 설계**

현재 산출물은 연구 프로토콜이다. 실제 모델 실행·독립 평가·분석을 마친 뒤에만 결과 논문으로 전환한다. 저자·소속·학위·직무 경력은 확인된 정보만 쓰고 AI 도구의 기여를 공개한다.

## 국문 초록 초안

여러 에이전트가 합성 분석 기록을 요약할 때, 출처 없는 결론이 검토 단계를 지나 최종 보고서에 남을 수 있다. 본 연구계획은 단일 분석자, 분석자와 검토자, 그리고 증거 출처 확인을 추가한 세 조건을 동일한 공개 모델과 생성 예산에서 비교한다. 한국어와 영어의 의미 대응 사례 및 모델 세 종을 사용하고, 근거 없는 핵심 결론 비율을 주 지표로 삼는다. 가상 오염 목표의 성공, 정상 과제 성공, 스키마 실패, 실행 지연도 함께 측정한다. 번역과 반복 간 의존성을 유지하는 대응 군집 bootstrap으로 조건 차이의 불확실성을 평가한다. 현재 문서는 실험 전 계획이며 모델 성능 결과나 방어 효과를 주장하지 않는다.

## English abstract draft

Unsupported conclusions may persist across handoffs in multi-agent analysis. This protocol compares a single analyst, an analyst with a reviewer, and the same workflow with explicit evidence provenance checks under fixed generation budgets. The planned evaluation uses three public instruction-tuned models and paired Korean and English synthetic scenarios. The primary outcome is the frequency of final reports containing an unsupported key conclusion. Secondary measures cover inert contamination goals, benign-task completion, schema failures, and latency. Paired cluster bootstrap estimates will preserve dependencies across translations, conditions, models, and repeated runs. This document presents an experimental protocol; it reports no measured model performance or validated defense effect.

## 본문 6~8쪽의 흐름

| 절 | 독자가 알아야 할 내용 | 필요한 증거 |
|---|---|---|
| 1. 문제와 질문 | 보고서의 결론이 증거와 연결되어야 하는 이유 | 합성 사례 한 쌍, 검증할 질문 |
| 2. 관련 연구 | 기존 평가와 이 설계의 공통점·차이 | AgentDojo·InjecAgent 원문 비교표, 후속 문헌 검토 |
| 3. 신뢰 경계 | 어떤 입력과 구성요소가 신뢰되는가 | 역할·증거·평가 정답 접근 도식 |
| 4. 데이터와 방법 | 120묶음 분할, 40묶음 최종 평가, 한영 대응, A/B/C | 데이터 카드·분할 해시·모델 revision·프롬프트 |
| 5. 결과 | 근거 없는 결론과 정상 완료의 동시 변화 | 실제 실행 로그에서 생성한 표·구간·누락률 |
| 6. 오류와 제거 실험 | 출처 검사가 고친 오류와 남긴 오류 | C−B, 검증 실패 유형, 독립 판정 불일치 |
| 7. 한계와 재현 | 언어·시나리오·모델·자원·평가자의 한계 | 원시 출력, 분석 스크립트, 독립 재현 기록 |

현재 5절과 결과 기반 6절은 미작성 상태다. 예정된 숫자를 실제 결과처럼 채운 표는 만들지 않는다. 기존 결정론적 회귀 결과는 부록의 도구 검증에만 사용한다.

## 필요한 표와 그림

1. 데이터 표: 의미 묶음·언어·유형·분할별 수, 공유 템플릿 점검 결과.
2. 주 결과 표: 모델×언어×조건의 주 지표, ASR, BSR, 스키마 실패, 각 분자·분모·미판정.
3. 효과 표: C−A 및 C−B의 %p 차이와 구간, 미판정 경계, 정상 완료 한계 판정.
4. 자원 표: 실제 입력·출력 토큰, 중앙 지연·p95, 타임아웃률, 하드웨어.
5. 흐름 그림: 비신뢰 자료에서 분석자·검토자·출처 검사·최종 보고서로 이어지는 경로와 평가 정답의 분리.
6. 오류 그림: 중간의 근거 없는 주장이 수정·잔존·기권·미판정으로 나뉘는 수. 실행 전에는 수치를 비워 둔다.

## 주장의 증거 기준

- “공개 모델 3종에서 검증”은 세 모델의 고정 revision과 모든 계획 셀의 로그가 있어야 쓴다.
- “정상 성능 유지”는 BSR의 사전 한계 분석과 누락 처리까지 통과해야 쓴다.
- “한국어에 효과적”은 한국어 결과와 독립 번역 검토가 있어야 한다. 영어 성능을 대신 인용하지 않는다.
- “사람 검토의 효과”는 별도 사람 개입 실험이 있어야 한다. 자동 검토자와 독립 채점은 사람 개입 방어 실험이 아니다.
- “재현 가능”은 다른 실행자의 버전 고정 재실행과 차이 기록까지 확보한 뒤 쓴다. 저장소 공개만으로 충족되지 않는다.
- “기관 적용 가능”은 별도 운영 검증이 필요하다. 이 합성 실험만으로 채용 자격·기관 승인·실사용 보안을 입증하지 않는다.

## 원문 참고문헌

- Debenedetti, E., Zhang, J., Balunović, M., Beurer-Kellner, L., Fischer, M., and Tramèr, F. (2024). [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352).
- Zhan, Q., Liang, Z., Ying, Z., and Kang, D. (2024). [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://aclanthology.org/2024.findings-acl.624/). Findings of ACL 2024, pp. 10471–10506.
- Koehn, P. (2004). [Statistical Significance Tests for Machine Translation Evaluation](https://aclanthology.org/W04-3250/). EMNLP 2004, pp. 388–395.

확인일: 2026-09-20. 이 목록은 시작점이며 체계적 문헌조사 완료 목록이 아니다. 투고 학회·기한·서식·AI 지원 공개 규칙은 투고 직전에 공식 안내를 별도로 확인한다.
