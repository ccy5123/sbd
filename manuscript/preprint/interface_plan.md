# J. R. Soc. Interface 투고 준비 계획 (승인 대기)

*작성 2026-10-20. 상태: 사용자 승인 전 초안. 승인 전에는 원고 LaTeX(`main.tex`, `sections/*.tex`, `si.tex`)를
고치지 않는다.*

- **투고처:** Journal of the Royal Society Interface, research article.
- **결정 배경:** PoF는 유체만 남기는 재구성이 필요했다. 조건은 무료 투고와 SCIE 우선이었다.
- **심사 의견 요약:** 주제와 학제 간 구조는 Interface에 맞는다. 다만 세 가지가 필요하다.
  - 방귀를 넘어서는 일반적 교훈을 앞세운다.
  - v4 결과에 의존하는 헤드라인 숫자를 하나의 모집단으로 다시 낸다.
  - 빠진 선행연구를 인용한다.

---

## 1. 요건 체크리스트

출처: 사용자가 2026-10-20에 붙여넣은 저널 페이지. "확인 필요"는 붙여넣은 내용에 없어서 저자 안내 페이지에서
다시 확인할 항목이다.

| # | 요건 | 현재 상태 | 할 일 |
|---|---|---|---|
| R1 | 분량 2,500–8,000 단어. **표지, 참고문헌, 감사의 글 포함** | 약 9,400 단어 (§2) | 약 1,900 단어 줄이기 (§2) |
| R2 | 초록 200 단어 이하 | 418 단어 | 200 단어로 다시 쓰기 (§4 지금-6) |
| R3 | 제목 150자 이하 | 61자 ("Silent but deadly? Physics says seldom, memory says mostly") | 통과. "seldom" 유지는 v4 뒤 결정 |
| R4 | 여러 분야 독자가 읽을 수 있게 수식과 기술 세부는 부록으로 | 증명과 유도가 본문에 있음 | 부록 A·B로 옮기기 (§3) |
| R5 | 첫 투고는 PDF 한 파일, 형식 자유. Royal Society LaTeX 템플릿은 최종본에서만 | achemso (`journal=jacsat`): JACS 원고처럼 보임 | 첫 투고는 중립적인 `article` 클래스로 바꾸기 권장 (§4 지금-8) |
| R6 | 데이터와 코드 공개 필수. 첫 투고는 GitHub로 가능하고, 수정본까지 DOI 저장소(Zenodo) 필요. 개인 드라이브·Dropbox 불가. **저장소와 ESM에 같은 것을 이중으로 올리지 말 것** | GitHub 저장소 있음. SI의 "Code and data" 표 | Data accessibility statement 작성. 데이터·코드는 저장소에만 두고, ESM에는 문서(본문 보충)만 둔다 |
| R7 | AI 사용 선언 (논문과 함께 출판됨) | `main.tex`에 GAP 표시 | 저자가 마지막에 직접 작성 (HANDOFF) |
| R8 | cover letter, ORCID, CRediT, 키워드 3–10개, data accessibility statement | 키워드 6개 (achemso 형식) | cover letter 요점은 §6. ORCID는 저자 확인. CRediT은 단독 저자라 전 항목 본인 |
| R9 | 주요 결과가 대중매체에 보도된 적 없을 것. 프리프린트는 권장 | 아직 게시·보도 없음 (확인 필요) | 출판 전까지 언론·SNS 홍보 금지. 프리프린트는 Interface 투고본으로 게시 |
| R10 | 단일 익명 심사 (심사자만 익명) | 해당 없음 | 저자 정보 그대로 둠 |
| R11 | 선정 기준: "outstanding quality and international importance, originality and interest across disciplines", "a significant advance ... rather than something incremental" | 서론이 방귀 이야기로만 짜여 있음 | 세 가지 일반 교훈을 서론·결론·cover letter 앞에 둔다 (§4 지금-1) |
| R12 | 투고료·게재료 없음 (Subscribe to Open, 2026년 CC-BY) | — | 비용 없음 |
| R13 | Ethics, funding, competing interests 선언 (확인 필요: 붙여넣은 내용에 없음, Royal Society 공통 관행) | 없음 | "Ethics: 사람·동물 대상 실험 없음"(문화 조사는 문헌 조사), funding 없음, 이해충돌 없음. 저자 확인 |

**분량 계산에서 확인할 점:** 붙여넣은 내용은 표지·참고문헌·감사의 글이 포함된다고만 한다. 그림 캡션, 표,
부록이 포함되는지는 나와 있지 않다. 아래 예산은 **캡션과 부록도 포함된다고 보고** 보수적으로 잡았다.
저자 안내에서 제외된다고 확인되면 그만큼 여유가 생긴다.

---

## 2. 단어 예산 (8,000 단어 이하, 참고문헌 포함)

### 2.1 현재 분량

- **본문:** `texcount` 측정값이다. 괄호 안은 이전 세션이 낸 값이다. 측정 방식에 따라 5–10% 차이가 난다.
- **참고문헌:** `main.pdf`의 참고문헌 목록을 `pdftotext`로 뽑아 단어를 셌다.

| 부분 | 현재 단어 수 |
|---|---|
| 표지 (제목, 저자, 소속, 키워드) | ~60 |
| 초록 | 418 (~413) |
| 서론 | 372 (~399) |
| 이론 | 828 (~951) |
| 방법 | 1,624 (~1,649) |
| 결과 (본문 1,668 + 캡션 549, 표 포함) | 2,308 (~2,475) |
| 토론 | 1,128 (~1,157) |
| 결론 | 128 (~132) |
| 감사의 글 (AI 선언 자리) | ~40 |
| **참고문헌: 본문에서 인용한 91개** | **~2,480** |
| **합계** | **~9,390** |
| SI (ESM, 분량 제한 없음) | 2,366 (~2,077). SI 전용 참고문헌 2개 |

**참고문헌 단어 비용**

- `refs.bib`에는 192개 항목이 있다. 렌더링되는 것은 실제로 인용된 **91개**뿐이다 (본문 91, SI 전용 2).
- 렌더링된 목록은 약 2,480 단어로, **참고문헌 1개당 약 27 단어**다.
- Royal Society 형식은 DOI를 붙인다. 그래서 개당 약 28 단어로 잡는다.

### 2.2 목표 예산

| 부분 | 목표 | 변화 | 내용 |
|---|---|---|---|
| 표지 | 60 | 0 | |
| 초록 | 200 | −218 | §4 지금-6 |
| 서론 | 850 | +480 | 선행연구 단락과 세 가지 교훈 추가 |
| 이론 | 550 | −280 | 정리 세 개는 쉬운 말로 진술만 남기고, 증명과 Si 유도는 부록으로 |
| 방법 | 800 | −820 | 화학·음향 세부와 UQ 세부는 ESM으로 |
| 결과 (캡션 포함) | 1,850 | −460 | 화학 결과를 ~150 단어로 줄이고, 그림 14와 반응성 표는 ESM으로 |
| 토론 | 750 | −380 | "Where the odour comes from"은 2문장만 남기고 ESM으로 |
| 결론 | 120 | −10 | 교훈 중심으로 다시 쓰기 |
| 선언 (data, AI, CRediT, ethics, funding, competing interests, 감사) | 220 | +180 | |
| 부록 A (정리 1·3 증명) + 부록 B (Silencer number 유도, 분석 모델 계수) | 600 | +600 | 부록도 분량에 포함된다고 가정 |
| **참고문헌 ~55개** | **1,550** | **−930** | §2.3 |
| **합계** | **~7,550** | **−1,840** | **여유 ~450 단어:** v4 결과 몫 (서 있는 쌍 GAP, 헤드라인-시간창 곡선, tail 검증, LES 피크 계수). 넘치는 것은 ESM으로 |

### 2.3 참고문헌: 91개에서 약 55개로

| 조치 | 개수 |
|---|---|
| "Where the odour comes from"을 ESM으로 옮김. 그 소절에서만 인용하는 문헌 | −23 |
| 화학·음향 방법 세부를 ESM으로 옮김. 그 소절에서만 인용하는 문헌 | −9 |
| 이론의 sniff 근거 6개를 3개로 (laing1983, frasnelli2006, kepecs2006 정도) | −3 |
| 토론의 기억 편향 5개를 3개로, releaser 4개를 2개로 | −4 |
| 기타 중복 정리 (예: 정오표 diez2003은 원문과 묶어 인용) | −3 |
| 추가: ancalle2021, chervinsky2022, licina2015, alassaad2021, Licina 2017, Rim & Novoselac 2010 | +6 |
| **결과** | **약 55개** |

- ESM은 자체 참고문헌 목록을 가진다. 옮긴 문헌은 ESM에서 그대로 인용하므로 버리는 내용은 없다.
- 본문에 남는 서론·선행연구 인용은 지금 2개(영화와 Grose 사전)뿐이다. Interface 심사자에게는 이것이
  가장 큰 약점이다. 그래서 추가 6개는 줄여서는 안 된다.

---

## 3. 배치 지도 (본문 / 부록 / ESM)

ESM은 지금의 `si.tex`를 이어받는다. ESM에는 문서만 두고, 데이터와 코드는 저장소에만 둔다 (R6).

### 3.1 절별 배치

| 현재 위치 | 결정 | 메모 |
|---|---|---|
| 초록 | 본문 | 200 단어로 다시 쓰기 |
| 1 서론 | 본문 | 다시 쓰기: 3 Idiots 도입은 2문장으로 줄이고, 선행연구 단락과 세 가지 교훈을 넣음. 문화 조사는 1문장만 남기고 세부는 ESM에 그대로 |
| 2.1 What "deadlier" means | 본문 | 식 (1)은 남긴다 (탐지 임계 반영, HANDOFF 항목 6). sniff 근거 bullet 3개는 1문장으로. 비교 기준 (A)(B)(C)는 남긴다 |
| 2.2 정리 1 (선형 수송) | 진술은 본문, 증명은 **부록 A** | 본문은 "어떤 방, 어떤 흐름에서든 느린 방출의 피크가 더 낮다"는 쉬운 진술 |
| 2.3 정리 2 | 본문 (2문장) | v4 tail 모델과 연결 |
| 2.4 Momentum and buoyancy, Silencer number | 개념은 본문, 유도와 계수는 **부록 B** | |
| 2.5 정리 3 (Berkson) | 진술은 본문, 증명은 **부록 A** | 여러 감각으로 알아차리는 사건 일반으로 확장하는 문장은 본문 |
| 3.1 Source (params.yaml) | 본문 (짧게) | 근거 등급(VERIFIED 등) 설명은 ESM |
| 3.2 Odorant chemistry | **ESM** | 본문에는 조성 출처 2문장만 |
| 3.3 Acoustics | **ESM** | 본문에는 lip-reed 모델 2–3문장만 |
| 3.4 Analytic dispersion model | 본문 (짧게), 계수는 부록 B | |
| 3.5 CFD | 본문 | 체온 대류 경계층 선행연구(Licina, Rim, Al Assaad)를 여기서 인용. 검증 세부는 ESM에 그대로 |
| 3.6 Perception and observers | 본문 | |
| 3.7 Uncertainty analysis | 본문 (짧게), Sobol 세부는 ESM | |
| 4.1 The odorants and the gas that carries them | 본문 ~150 단어, 나머지는 **ESM** | 메탄티올 ≥ H2S가 Suarez 1998의 결론과 다르다는 점은 본문에 명시. 부력, 산화 0.4%도 한 문장씩 |
| 4.2 Most releases are physically silent | 본문 | |
| 4.3 The ratio in the analytic model | 본문 | |
| 4.4 Real rooms: where the release goes | 본문 | 교훈 (i)의 핵심. v4로 다시 씀 |
| 4.5 Perception | 본문 | |
| 4.6 Memory | 본문 | v4 경로 모집단에 기억 필터 적용 (HANDOFF 항목 1) |
| 5.1 Why the belief exists | 본문 | "can explain"으로 표현. 다른 기억 편향은 1문장 |
| 5.2 The releaser | 본문 (~80 단어로 줄임) | 예측 절로 합침 |
| 5.3 Where the odour comes from (~40줄) | **ESM** (본문 2문장) | 본문에는 "황 농도가 부피와 무관한 이유는 생산과 빠른 소비의 균형으로 설명된다. 식단에 따른 연관은 믿음 쪽 방향일 수 있으나 측정된 적 없다" 정도만 남김. 문헌은 23개 모두 ESM에서 인용 |
| 5.4 Predictions | 본문, **앞으로 당김** | 초록과 결론에도 넣음 (§4 지금-4) |
| 5.5 When a silent release is worse | 본문 | |
| 5.6 Limitations | 본문 | v4 뒤 갱신: 평균 흐름 한계는 LES 피크 계수로, 장면 가중치는 출처 있음으로 |
| 6 결론 | 본문 | 세 가지 교훈으로 다시 씀 |
| 감사의 글 (AI GAP) | 별도 선언 절 | AI 선언, CRediT, data, ethics, funding, competing interests |
| SI "Code and data" 표 (`tab:data`) | ESM에서 빼고 **저장소 README**로 | 이중 게시 금지 (R6). 본문에는 data accessibility statement |
| SI 파라미터 표 (`tables/params.tex`) | ESM | 문서이고 데이터가 아니다. 원본 `params.yaml`은 저장소에 |
| SI 나머지 (검증, 장면, 소파, 엘리베이터, 서 있는 쌍, 호흡 샘플링, 문화 조사) | ESM | 서 있는 쌍 GAP은 v4 뒤 채움 |
| TOC 그래픽 (`toc.png`) | **삭제** | Interface에는 TOC 그래픽이 없다 |
| `\src{}`, `\gap{}` 표시 | 투고본에서 삭제 | 지금 `\gap`은 results 1곳, main 2곳 |

### 3.2 그림과 표

본문 그림은 6개로 잡는다.

| 그림·표 | 지금 위치 | 결정 |
|---|---|---|
| fig2_chain (메커니즘 사슬 개요) | SI | **본문 그림 1로 올림.** 여러 분야 독자에게 길잡이가 된다 |
| fig3_acoustic_regimes | 본문 | 본문 |
| fig10_regime_uq | 본문 | 본문 |
| fig6_sofa_duet_planes | 본문 | 본문. v4 3D 뷰어 렌더로 바꿀지는 v4 뒤 결정 |
| fig16_routing | 본문 | 본문 (v4로 갱신) |
| fig13_memory_filter | 본문 | 본문 (v4 모집단으로 갱신) |
| fig14_chemistry | 본문 | **ESM** |
| fig4 jet / CBL validation, fig5 sofa noses, figS sofa postures, fig15 elevator, fig7 breath hold, fig12 culture map | SI | ESM |
| fig11_gamma, figS_adaptation | `figs/`에 있으나 인용 안 됨 | 쓰지 않음 |
| tab:ratio | 본문 | 본문 |
| tab:observers | 본문 | 본문 (v4로 다시 계산) |
| tab:reactivity | 본문 | **ESM** |
| tab:sofa, tab:elevator | SI | ESM |

---

## 4. 작업 목록

### 지금 할 일 (v4와 무관)

승인 뒤 이 순서로 진행한다. 숫자가 들어갈 자리는 `\gap{v4}`로 비워 둔다.

1. **서론과 결론을 방귀를 넘어서는 세 가지 일반 교훈 중심으로 다시 쓴다.**
   - (i) 사람 몸의 대류 경계층은 몸 가까이에서 나온 방출을 운동량에 따라 서로 다른 코로 보낸다
     (호흡기 비말, 피부 입자, 실내 오염원 노출과 연결).
   - (ii) 선형 수송에서는 느린 방출의 피크가 더 낮다. 방과 흐름의 종류와 무관하다 (실내 누출, 냄새 영향평가와 연결).
   - (iii) 사건을 두 가지 이상의 감각으로 알아차릴 때, Berkson 선택만으로도 잘못된 감각적 믿음이 생긴다
     (다감각 민간 믿음 일반과 연결).
2. **빠진 인용을 넣는다.**
   - references.yaml에 있으나 인용되지 않은 문헌:
     - `ancalle2021` "Physics of flatulence" (Hu lab, JASA 학회 초록). 가장 가까운 선행연구로 서론에서 인용.
     - `chervinsky2022` (flatology.com 자료, 약 1,600회, 소리 크기와 냄새의 약한 양의 상관). 동료심사를 거치지
       않은 자료임을 밝히고, 이 논문의 결론과 같은 방향이라고 적는다.
     - `licina2015`, `alassaad2021`: CFD 방법과 교훈 (i).
   - references.yaml에 아직 없는 문헌 (`make_bib.py` 경로로 추가):
     - Licina, Tian & Nazaroff 2017, *Building and Environment* 123:14, doi 10.1016/j.buildenv.2017.06.037.
     - Rim & Novoselac 2010. **어느 논문인지 정확한 서지가 brief에 없다.** OpenAlex로 DOI를 확인한 뒤 넣는다.
       (2009년 논문 `rim2009`는 yaml에 있으나 인용되지 않았다. 함께 쓸지도 정한다.)
   - 문헌 검색은 DOI만 가져온다 (HANDOFF 규칙).
3. **기억 결과의 표현을 바꾼다.** "기억 모델이 이 믿음을 *설명할 수 있다*(can explain)"로 쓴다. 검증 가능한
   예측을 초록·토론·결론 앞에 둔다.
   - 방출자는 이 믿음을 덜 갖는다.
   - 후각을 잃은 사람은 조용한 방귀를 기억하지 못한다.
   - (현재 원고에 있는 것) 배경 소음의 효과는 방향이 정해지지 않는다.
4. **메탄티올 ≥ H2S 결과가 Suarez 1998의 결론과 다르다고 명시한다** (결과 4.1). Suarez 1998은 H2S를 주된
   냄새 성분으로 결론지었다. 차이는 문턱값 세트와 두 조성 자료에서 온다고 쓴다.
5. **배치 지도 적용** (§3): 증명과 유도는 부록으로, 화학·음향 세부와 "Where the odour comes from"은 ESM으로,
   fig2_chain은 본문으로 옮긴다. 참고문헌을 약 55개로 줄인다 (§2.3).
6. **초록을 200 단어로 다시 쓴다.** 문장별 배분은 아래와 같다.

   | 내용 | 단어 |
   |---|---|
   | 믿음과 질문 | 25 |
   | 사슬 방법 | 30 |
   | 정리 1과 Silencer number (교훈 ii) | 35 |
   | 경로 결과 (교훈 i) | 40 |
   | 기억 결과 (교훈 iii, can explain) | 40 |
   | 예측 | 20 |
   | 일반적 의미 | 10 |

   헤드라인 숫자 자리는 v4까지 비워 둔다.
7. **cover letter 요점 초안** (§6). 숫자는 v4 뒤 채운다.
8. **형식:** achemso를 중립적인 `article` 클래스로 바꾸고, 참고문헌을 번호식으로 한다. `xr` 상호참조는 그대로
   두되 "ESM §S…"로 표시한다. TOC, `\src{}`, `\gap{}`을 지운다. 그 뒤 `si.tex`, `main.tex` 순으로 빌드해 로그를
   확인한다 (HANDOFF 규칙).
9. **선언 초안:** data accessibility (첫 투고는 GitHub URL), ethics, funding, competing interests, CRediT,
   키워드 (3–10개, 안은 §6). AI 선언은 저자가 쓰므로 빼 둔다.

### v4 CFD 결과가 나온 뒤

1. **헤드라인 숫자를 하나의 모집단으로 다시 낸다.** 지금 초록의 세 숫자는 출처가 서로 다르다.
   - 48%: 분석 모델, 이웃 한 명, 실제 방출 기준.
   - 21% (0–70%): CFD 장면을 같은 가중으로 평균, 30/60초 시간창.
   - 68–93%: Gate 0 수용체. 경로 효과가 없고, 둘 다 냄새를 못 맡은 쌍을 반씩 나눔.

   HANDOFF 항목 1–7(네 결과 C, 탐지 임계, 소리로 주의가 생기는 bystander), 새 시간창(150초 + tail), 장면
   가중치(0.73 / 0.005 / 0.26과 두 경계 경우)를 적용한다. 물리 결과와 기억 결과가 같은 경로 모집단에서
   나오게 한다.
2. **서 있는 쌍 GAP을 채운다** (`sections/results.tex`, `si.tex`의 standing 절, fig16).
3. **제목에 "seldom"을 남길지 정한다.** 두 기준(네 결과 비율, 둘 다 냄새를 맡은 쌍에서 조용한 쪽이 이기는
   비율)이 모두 지지할 때만 남긴다 (HANDOFF 2026-10-19 결정).
4. **한계 절 갱신:** LES 피크 계수, tail 검증 600초 결과.
5. **AI 사용 선언:** 저자가 마지막에 직접 쓴다 (HANDOFF).
6. **Zenodo DOI:** GitHub release가 필요하고 외부에 공개되는 일이므로 **만들기 전에 사용자에게 확인한다.** 첫
   투고는 GitHub URL로 하고, 수정본까지 DOI로 바꾼다.
7. **프리프린트 게시:** 서버(이전 논의: ChemRxiv 대 arXiv physics.flu-dyn)는 투고 직전에 정한다. 게시본은
   Interface 투고본과 같게 한다. 출판 전까지 대중매체 홍보는 하지 않는다 (R9).
8. **최종 점검:** 분량(§2), 초록 단어 수, 참고문헌 수, 그림 수, 선언 항목.

---

## 5. Interface가 거절할 경우의 대안

| 순위 | 투고처 | 비용 | 메모 |
|---|---|---|---|
| 1 | **The Science of Nature** (Springer) | 무료 (비OA 경로) | 2025년부터 과학적 타당성 중심 심사. 학제 간 구조를 그대로 둘 수 있음 |
| 2 | **EPJ Plus** | 무료 (비OA 경로) | 물리 중심이라 화학·기억 부분을 줄여야 할 수 있음 |
| — | RSOS (Interface가 이관을 제안할 때) | APC £1,400 | 무료 조건에 맞지 않음. 이관 제안이 오면 그때 사용자와 상의 |

같은 원고를 쓸 수 있도록 Interface 판의 구조(본문, 부록, ESM)를 유지하고, 형식만 바꾼다.

---

## 6. cover letter 요점 초안과 키워드

**Cover letter (영문, 요점만, 숫자는 v4 뒤)**

- The paper tests a belief documented across many languages ("silent but deadly") by one chain from chemistry and
  sound through dispersion to perception and memory. No mechanistic test existed. The closest prior work is a
  conference abstract (Ancalle et al. 2021).
- Three results reach beyond the topic:
  - **Routing (i):** the human convective boundary layer routes near-body releases to different noses by their
    momentum. This bears on respiratory, skin-particle and indoor-source exposure.
  - **Peak bound (ii):** under linear transport a slower release cannot give a higher peak, in any room or flow.
  - **Selection (iii):** Berkson selection alone can create a false sensory belief whenever events are noticed
    through more than one sense.
- Testable predictions: releasers should hold the belief less; anosmic people should never remember a silent passage.
- Why Interface: physics, chemistry, sensory science and cognition meet in one question, and each part is accessible
  on its own.
- Open data and code (GitHub now, Zenodo DOI by revision). Preprint status. The results have not been reported in
  the media.
- Suggested reviewers (indoor airflow and human micro-environment, olfactory psychophysics, selection bias):
  the author decides.

**키워드 (안, 7개):** convective boundary layer; indoor air; odour dispersion; starting jet; Berkson bias;
olfactory perception; flatus.

---

## 7. 승인받을 결정

1. 단어 예산의 전제: 캡션과 부록이 분량에 포함된다고 보수적으로 잡음 (§1, §2).
2. 참고문헌 약 55개 목표. 옮기는 문헌은 ESM에서 인용 (§2.3).
3. "Where the odour comes from"은 삭제하지 않고 ESM으로 옮김. 본문에는 2문장 (§3.1).
4. fig2_chain을 본문으로 올리고, fig14와 반응성 표는 ESM으로 (§3.2).
5. 첫 투고본은 achemso를 `article` 클래스로 바꾸고 TOC 그래픽을 삭제 (§4 지금-8).
6. "지금 할 일" 1–9를 이 순서로 진행 (§4).

---

## 8. 진행 상황

**2026-10-20:** 사용자 승인. "지금 할 일" 1–9 완료. v4에 의존하는 숫자는 `\gap{v4; preprint: …}`로 비워 두고
예전 값을 함께 적었다.

| 항목 | 결과 |
|---|---|
| 분량 | 약 7,370 단어 (표지 ~40, 초록, 본문, 캡션, 선언, 부록 ~5,950, 참고문헌 47개 ~1,380). 8,000까지 여유 ~630 |
| 초록 | 182 단어 (워드프로세서 기준; texcount는 하이픈 단어를 나눠 세서 210) |
| 참고문헌 | 본문 91개 → 47개 (예산 55개보다 적음). ESM은 자체 목록 58개 |
| 형식 | `article` 클래스, 줄 번호, `unsrtnat` 번호식, ESM 번호는 S1… TOC 그래픽 삭제 |
| 데이터 표 | ESM에서 빼고 `README.md`의 "Source files of each result"로 옮김 (이중 게시 금지) |

**계획과 달라진 점**

- **flatology 자료:** 1,619회 자료의 출처는 `chervinsky2022`(책 "Consider the Sphincter")가 아니다.
  flatology.com 블로그 글 "The sound of stink"(W. Snyder, 2020, 2022 갱신)다. 그래서 새 키 `snyder2020`으로
  인용했다. 이 자료는 냄새를 사람이 아니라 VOC 센서 값으로 쟀고, 조용한 방귀는 하나도 기록되지 않았다.
  본문에도 "none was silent"라고 적었다. `chervinsky2022`는 인용하지 않았다.
- **Rim & Novoselac 2010:** 두 편이 있다. 몸 가까운 실내 오염원 노출을 다룬 *Building and Environment*
  45:1214을 `rim2010`으로 넣었다. 다른 하나는 *J. Occup. Environ. Hyg.* 7:683이다. 2009년 논문 `rim2009`도
  함께 인용했다.
- **Suarez 1998:** 전문을 열 수 없었다. 그래서 초록에서 확인되는 내용만 적었다: H2S가 주된 황 가스이고,
  판정자의 악취 평가가 H2S 농도를 따랐다.
- **방법 절:** 1,238 단어로 목표 800보다 길다. CFD 소절은 v4 결과로 다시 쓸 때 줄인다.

**남은 일:** §4 "v4 CFD 결과가 나온 뒤" 1–8.

**저자 결정 (2026-10-20)**

- **ORCID:** 0009-0007-5822-6714. 원고와 cover letter에 넣었다.
- **CRediT:** 모든 역할을 저자가 맡았다.
- **Funding:** 받은 연구비 없음.
- **AI 선언:** 저자가 맨 마지막에 쓴다.
- **추천 심사자:** 없음. cover letter에서 뺐다.
- **프리프린트:** engrXiv.

**engrXiv AI 정책과의 충돌 (해결 필요)**

engrXiv의 AI 정책(<https://engrxiv.org/ai-policy>, 2026-10-20 확인, SocArXiv 정책을 가져와 고친 것)은 다음을 요구한다.

- AI 사용을 공개하고 기록할 것. 공개하지 않거나 그럴듯하지 않게 공개하면 거절된다.
- **LLM이 생성한 텍스트를 그대로(verbatim) 쓰는 것을 금지한다.** 문단이나 절 전체도 마찬가지다.
- 허용되는 것은 번역, 교정과 서식, 기계 보조 분석, 사람이 검증하는 문헌 검색이다.
- LLM을 많이 쓴 흔적이 있는 원고는 더 오래 검토하며, 사람이 저자임을 증명하라고 요구할 수 있다.

이 원고의 본문은 대부분 Claude가 초안을 썼다. engrXiv에 내려면 저자가 본문을 직접 다시 써야 할 가능성이
높다. 대안은 AI 작성 텍스트를 금지하지 않는 서버다.

**결정 (2026-10-20):** 저자는 다시 쓰지 않고 engrXiv에 그대로 낸다. engrXiv가 보류하거나 거절할 수 있다는
위험을 안고 가는 결정이다. AI 사용은 정직하게 공개한다. 공개하지 않거나 그럴듯하지 않게 공개하면 거절 사유가
되고, 허위 표시는 계정 정지 사유다.

Interface는 AI 사용을 막지 않는다. AI 선언을 요구하고 논문과 함께 출판할 뿐이다 (R7).
