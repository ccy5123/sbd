# 소리 없는 방귀가 더 독한가: 성분·확산·지각 연구와 실내 기류 시뮬레이션으로 본 통념 검증

[이름] · 작성일 2026년 [월] [일]

<!-- 제출 전 지울 것: [ ] 표시는 저자가 채울 자리. 본문(초록~결론) 분량은 count_chars.py로 확인. -->

## 초록

"소리 없는 방귀가 더 독하다"는 통념이 실제 냄새 노출과 맞는지 검토하였다. 방귀 냄새의 성분, 몸 주변 기류에 의한 확산, 냄새 지각과 기억에 관한 문헌 25편(비공식 자료 1편 포함)을 세 주제로 나누어 비교하였다. 문헌으로 답할 수 없는 부분은 저자의 미출간 전산유체역학(CFD) 시뮬레이션과 몬테카를로 계산으로 보완하였다. 성분 연구에서는 소리와 냄새 물질(황화합물)이 서로 다른 요인에 의해 정해지고, 소리가 클수록 냄새가 약하게 강하다는 비공식 자료만 있었다. 확산 연구와 시뮬레이션에서는 조용한 방출이 몸의 상승 기류에 실려 옆 사람의 코를 비껴가는 경우가 많았다. 실제 빈도로 가중한 시뮬레이션에서 옆 사람에게 조용한 방귀가 더 독하게 느껴지는 경우는 0.4%, 소리 나는 방귀가 더 독한 경우는 6.8%였다. 그러나 냄새를 맡았을 때만 조용한 방귀를 기억한다는 선택 효과를 적용하면, 기억에 남은 비교의 91.5%가 "조용한 쪽이 더 독했다"가 되었다. 결론적으로 이 통념은 옆 사람의 실제 노출에 대해서는 대체로 틀렸고, 기억의 선택 효과가 그 믿음을 만든다. 방출자 본인의 코처럼 조용한 방출이 몸 가까이 머무는 조건에서는 조용한 방귀가 더 독한 경우가 늘어나지만, 그때에도 소리 나는 방귀가 더 자주 독하다.

## 제1장 서론

### 제1절 연구의 배경과 목적

조용한 방귀가 더 독하다는 믿음은 오래되고 널리 퍼져 있다. 영어에는 1970년대부터 "silent but deadly"라는 표현이 쓰였고, 영화 「세 얼간이」에서도 소리 없이 지독한 방귀를 뀌는 인물이 조용한 쪽이 가장 치명적이라고 말한다. 한국어에도 "소리 없는 방귀가 더 독하다"는 말이 있다. 1811년 영국의 속어 사전(Grose 1811)은 비슷한 말을 "귀보다 코에 더 분명한" 방출로 풀이하였다. 저자가 32개 언어의 사전과 속담을 조사한 결과(미출간), 조용한 방귀와 소리 나는 방귀를 구분하는 단어는 적어도 다섯 어족에 있었고, 조용한 쪽이 더 고약하다는 주장은 중국어와 영어 속담에 명시되어 있었다. 이처럼 서로 독립된 문화에서 같은 믿음이 생겼다면, 그 원인이 사람에게 공통된 무언가에 있을 가능성이 크다. 그러나 이 주장을 직접 검증한 연구는 찾지 못하였다.

이 통념은 두 부분이 모두 모호하다. "소리 없는"은 괄약근이 진동하지 않아 물리적으로 소리가 나지 않는 경우와, 소리가 났지만 주변 소음에 묻혀 들리지 않은 경우를 함께 가리킨다. "독하다"는 코에 닿는 농도의 최댓값, 들이마신 총량, 기억에 남은 인상 중 어느 것이든 될 수 있다. 이 글에서는 "독하다"를 **냄새로 지각된 강도**로 정의한다. 냄새를 맡지 못한 방귀의 독함은 0으로 보고, 두 방귀를 모두 맡았다면 감각의 최소 식별 차이(약 28%)보다 강한 쪽을 더 독하다고 본다.

연구 질문은 다음과 같다. **같은 사람이 실제로 내는 방귀들 가운데, 곁에 있는 사람에게 조용한 방귀가 소리 나는 방귀보다 더 독하게 느껴지는 경우가 더 많은가?** 이 질문에 답하려면 성분, 확산, 지각의 세 단계를 차례로 따라가야 한다.

### 제2절 검토한 문헌과 방법

**연구의 범위.** 건강한 성인의 방귀 성분과 양, 소리의 발생 기제, 사람 몸 주변의 대류 기류와 근접 오염원의 노출, 냄새의 탐지 역치와 주의, 착각 상관과 선택 편향에 관한 동료 심사 문헌을 대상으로 하였다. 출판 연도는 제한하지 않았다(1946–2021). 방귀 소리와 냄새를 함께 기록한 자료는 비공식 자료 1건뿐이어서 별도로 표시하고 포함하였다. 동물 연구와 구강 악취 연구는 측정 방법을 비교하는 데에만 사용하였다.

**연구의 방법.** 문헌은 OpenAlex와 PubMed에서 "flatus odour", "flatus composition", "human convective boundary layer", "odor threshold", "olfactory attention", "illusory correlation", "Berkson bias" 등의 검색어로 찾았다(검색 기간 2026년 10월). 모든 문헌은 DOI로 서지정보를 대조하고, 인용한 수치는 초록이나 원문에서 확인하였다. [라이너 스콜라 활용: 저자가 실제로 사용한 단계와 용도를 적는다. 예: 문헌 탐색 보완, 연구 간 결과 비교, 초안 다듬기.] 문헌 정리와 초안 작성에는 Claude(Anthropic)도 사용하였으며, 문헌의 실재와 인용 내용, 해석과 결론은 저자가 직접 확인하였다.

문헌이 직접 답하지 못하는 연결 고리, 즉 "방출된 가스가 옆 사람 코에 얼마나 닿는가"는 저자의 미출간 시뮬레이션으로 보완하였다. 오픈소스 CFD 코드 OpenFOAM으로 소파에 나란히 앉은 두 사람(세 가지 자세)과 마주 선 두 사람(정지 공기, 사무실 환기)을 계산하였다. 소리 나는 방출 두 종류와 조용한 방출 두 종류를 넣고, 각 코에서 방출 후 150초 동안의 최대 호흡 농도를 구하였다. 농도는 냄새 활성값(OAV, 탐지 역치의 배수)으로 나타냈다. 이어서 문헌의 분포로 방귀 2만 건을 생성하고, 장면은 실제로 머무는 시간(시간 사용 조사)으로 가중하였다. 관찰자는 냄새를 기다리는 사람(50% 탐지가 OAV 20)과 다른 일에 몰두한 사람(OAV 520)의 두 종류로 두었다. 이 결과는 동료 심사를 거치지 않았고 난류의 평균값(RANS)이므로, 문헌 근거와 구분하여 "시뮬레이션"으로 표시한다.

## 제2장 주제별 분석

### 제1절 성분: 소리와 냄새 물질은 따로 정해진다

**공통 결과.** 방귀 냄새는 미량의 황화합물이 결정한다. Suarez 등(1998)은 건강한 성인의 방귀에서 황화수소(평균 1.06 µmol/L), 메탄싸이올(0.21 µmol/L), 다이메틸설파이드(0.08 µmol/L)를 측정하였고, 냄새 판정자의 악취 점수는 황화수소 농도와 유의하게 상관하였다. Tangerman(2009)도 세 황화합물을 주된 냄새 물질로 정리하였다. 반면 방귀 부피의 대부분은 장내 발효로 생기는 수소, 이산화탄소, 메탄과 삼킨 공기의 질소이다. Suarez 등(1997)에 따르면 장내에서 생성된 가스가 방귀의 약 74%를 차지하고, 주된 가스의 종류도 사람마다 달랐다. 하루 방귀량은 476–1491 mL(중앙값 705 mL)이고 섬유를 뺀 식단에서는 하루 214 mL로 줄었다(Tomlin 등 1991). 횟수는 하루 약 10회(Furne & Levitt 1996)이므로 한 번에 수십 mL가 나온다. 냄새 물질은 다른 가스와 달리 쉽게 흡착된다. 숯을 넣은 방석은 황 가스의 90% 이상을 흡수했고(Suarez 등 1998), 평범한 옷도 30초 동안 황화물 가스의 약 22%를 걸러냈다(Ohge 등 2005). 즉 냄새는 방귀의 양이 아니라 미량 성분의 농도와, 그것이 옷이나 가구를 지나며 얼마나 남는가에 달려 있다.

**차이와 한계.** 소리는 이 성분과 다른 경로로 정해진다. 방귀 소리는 항문 피부가 트럼펫 연주자의 입술처럼 진동해서 난다고 보고되었으나(Ancalle 등 2021), 이는 학회 초록이며 측정 자료가 없다. 진동 여부는 방출 압력과 유속, 즉 양과 속도에 달려 있고, 황화합물 농도와는 직접 관련이 없다. 성분 연구는 모두 직장 튜브로 모은 시료를 분석하였기 때문에 방귀 한 번마다의 소리를 기록하지 않았다. 소리와 냄새를 함께 잰 자료는 동료 심사를 거치지 않은 개인 기록 1건뿐이다. 1,619건을 녹음하고 가스 센서로 냄새를 잰 이 자료에서 소리가 클수록 냄새가 아주 약하게 강했고(결정계수 0.016), 소리 없는 방출은 하나도 기록되지 않았다(Snyder 2020).

**표 1.** 성분 단계 문헌의 비교

| 문헌 | 대상과 방법 | 주요 결과 | 소리와의 관계 |
|---|---|---|---|
| Suarez 등 1998 | 건강한 성인, 직장 튜브 채집, 가스 분석과 냄새 판정 | 악취는 황화수소 농도와 가장 강하게 상관 | 기록하지 않음 |
| Suarez 등 1997 | 건강한 성인, 방귀 성분 분석 | 장내 생성 가스가 약 74%, 주된 가스는 사람마다 다름 | 기록하지 않음 |
| Tomlin 등 1991 | 건강한 자원자, 24시간 채집 | 하루 476–1491 mL, 식단에 따라 크게 변함 | 기록하지 않음 |
| Furne & Levitt 1996 | 건강한 성인, 배출 횟수 기록 | 하루 약 10회(정상 상한 20회) | 기록하지 않음 |
| Ohge 등 2005 | 옷과 냄새 차단 제품의 황화물 제거율 | 평범한 옷은 약 22% 제거 | 해당 없음 |
| Snyder 2020 (비공식) | 개인 기록 1,619건, 녹음과 가스 센서 | 소리가 클수록 냄새가 약간 강함 | 결정계수 0.016, 조용한 방출 없음 |

**종합.** 성분 문헌은 "조용한 방귀일수록 황화합물이 진하다"는 근거를 주지 않는다. 같은 농도라면 소리 나는 방귀가 대체로 더 크므로 냄새 물질의 총량도 더 많다. 그런데도 통념이 성립하려면 조용한 방귀가 더 적게 희석되어 코에 닿아야 한다. 이 문제는 다음 절에서 다룬다.

### 제2절 확산: 코까지 냄새를 나르는 것은 몸 주변 기류다

**공통 결과.** 빠르게 분출되는 기체는 주변 공기를 빨아들이며 희석되고, 축 농도는 거리에 반비례해 떨어진다(Dowling & Dimotakis 1990). 이 원리만 보면 천천히 새어 나오는 조용한 방귀가 덜 희석되어 더 독할 것 같다. 저자의 분석 모델(경로를 무시하고 코가 구름 중심에 있다고 가정)에서도 실제 방출량 기준으로 조용한 쪽이 더 진한 경우가 절반 가까이(48%)였다. 그러나 실내에서는 사람 몸 자체가 기류를 만든다. 체온으로 데워진 공기가 몸을 따라 올라가는 대류 경계층은 앉은 사람 앞에서 최대 약 0.16–0.24 m/s에 이르고 호흡 영역까지 이어진다(Licina 등 2014). 몸 가까이에서 나온 오염물은 이 기류를 타고 올라가므로, 같은 양이 방의 다른 곳에서 나올 때보다 본인의 호흡 노출이 훨씬 크다(Rim & Novoselac 2009, 2010; Licina 등 2017). 옷차림도 이 기류를 바꾸어, 두껍고 헐렁한 옷은 호흡 영역의 상승 속도를 약 40% 줄였다(Licina 등 2014).

**차이.** 기존 연구는 거의 모두 수동적으로 퍼지는 오염원과 그 사람 본인의 노출을 다루었다. 조용한 방귀는 이 조건에 가깝지만, 소리 나는 방귀는 빠른 제트이다. 또 통념이 말하는 피해자는 본인이 아니라 옆 사람이다. 환기 기류가 경계층과 부딪히면 코 앞 상승 속도가 0.185 m/s에서 0.10 m/s로 줄었다는 결과(Licina 등 2015)처럼, 경로는 자세와 환기에 따라 달라진다.

**시뮬레이션 보완.** 저자의 CFD에서는 방출 운동량과 경계층 운동량의 비(Π)가 경로를 갈랐다. Π는 방출이 몸의 상승 기류를 "밀어낼" 만큼 센지를 나타내는 무차원 수로, 1보다 작으면 기류에 실려 가고 훨씬 크면 기류를 뚫고 나간다. 소파에 앉은 경우 Π가 가장 작은 느린 조용한 방출(Π≈0.5)은 경계층에 실려 방출자 쪽으로 올라갔고, 옆 사람 코에는 같은 질량(92 mL) 기준 OAV 0.05–0.23에 그쳤다. 반면 Π가 수백인 큰 소리 방출은 경계층을 뚫고 나가 옆 사람 코에 OAV 6–12로 닿았다. 실제 방출량으로 보면 바른 자세 소파에서 큰 소리 방출은 옆 사람 코에 OAV 16.9, 큰 조용한 방출은 0.09였다. 맨몸 다섯 장면 모두에서 옆 사람 코에 탐지 역치(OAV 1)를 넘은 조용한 방출은 없었다. 바지를 입히면 소리 나는 방출이 오히려 강해졌다. 마주 선 두 사람에서는 방출 종류와 관계없이 옆 사람 코의 농도가 낮았다. 서 있으면 엉덩이에서 코까지의 높이가 크고, 상대가 몸의 뒤쪽이 아니라 앞쪽에 있기 때문이다. 즉 Π 하나로 경로가 모두 정해지지는 않으며, 사람 사이의 배치와 거리가 두 번째 변수가 된다.

[그림 1 자리: 3D 뷰어에서 고른 장면. 소파에 앉은 두 사람, 조용한 방출 구름은 방출자 쪽으로 올라가고 소리 나는 방출 구름은 옆 사람에게 닿는 모습. 출처: 저자 시뮬레이션]

### 제3절 지각과 기억: 조용한 방귀는 냄새를 맡았을 때만 기억된다

**공통 결과.** 일반인의 냄새 탐지 역치는 훈련된 판정단보다 약 20배 높고(Amoore & Hautala 1983), 같은 사람 안에서도 순간마다 크게 변한다(Stevens 등 1988). 냄새를 예상하지 않는 사람은 역치의 약 26배가 되어야 절반이 반응한다(Whisman 등 1978; Amoore & Hautala 1983). 시각 과제에 주의를 빼앗기면 냄새를 알아차리지 못하는 상태가 오래 이어진다(Forster & Spence 2018). 직전에 냄새에 노출되었는지에 따라 탐지 역치가 최대 천 배까지 달라지기도 한다(Greenberg 등 2013). 대화나 텔레비전에 집중한 거실의 옆 사람은 대부분 이 '주의를 빼앗긴' 상태에 가깝다. 다만 주의가 바뀌어도 처음 느끼는 강도 자체는 크게 달라지지 않았다(Fallon 등 2018). 소리와 기대는 냄새 판단을 바꾼다. 어울리는 소리는 냄새의 쾌·불쾌 평가를 바꾸고(Seo & Hummel 2011), 냄새가 해롭다는 믿음은 지각된 강도와 증상 보고를 높인다(Dalton 1996).

**선택 효과.** 핵심은 무엇이 기억에 남는가이다. 소리 나는 방귀는 냄새를 맡지 못해도 들어서 알고, 조용한 방귀는 냄새를 맡았을 때에만 존재를 안다. 그러므로 기억 속 조용한 방귀는 처음부터 "냄새가 난 것"만 모인 표본이다. 두 경로 중 하나로만 알아차리는 사건만 고르면 실제로는 관련이 없는 두 성질이 관련 있어 보이는 이 현상은 Berkson(1946)의 선택 편향으로 알려져 있다(Snoep 등 2014). 또 드물고 눈에 띄는 조합(조용한데 지독함)은 실제보다 자주 일어났다고 기억되고(Hamilton & Gifford 1976), 사람들은 그럴듯한 연관을 실제 자료와 무관하게 보고한다(Chapman 1967).

**시뮬레이션 보완.** 방귀 2만 건을 앞 절의 장면에 흘려보내 같은 표본에서 물리와 기억을 함께 계산하였다(표 2). 생성된 방귀의 약 85%(가정에 따라 76–94%)는 물리적으로 조용하였다.

**표 2.** 옆 사람에게 조용한 방귀와 소리 나는 방귀를 짝지어 비교했을 때의 네 결과 (맨몸, 실제 빈도 가중, 단위 %, 출처: 저자 시뮬레이션)

| 관찰자 | 기준 | 둘 다 못 맡음 | 조용한 쪽이 더 독함 | 소리 나는 쪽이 더 독함 | 구별 안 됨 |
|---|---|---|---|---|---|
| 냄새를 기다리는 사람 | 실제 노출 | 92.8 | 0.4 | 6.8 | 0.0 |
| 냄새를 기다리는 사람 | 기억된 비교 | – | 91.5 | 7.7 | 0.9 |
| 다른 일에 몰두한 사람 | 실제 노출 | 98.5 | 0.1 | 1.4 | 0.0 |
| 다른 일에 몰두한 사람 | 기억된 비교 | – | 98.2 | 1.7 | 0.1 |

실제로는 소리 나는 쪽이 약 17배 자주 더 독하지만, 기억에서는 조용한 쪽이 90% 이상을 차지한다. 탐지 확률이 1에 가까워지면, 즉 모든 방귀를 맡게 되면 기억된 비율은 실제 비율(약 29%)로 내려간다. 따라서 이 결과는 정의상 정해진 값이 아니라 냄새를 드물게 맡는다는 조건에서 생기는 효과이다.

## 제3장 논의

**표 3.** 단계별 근거의 종합

| 단계 | 문헌 근거 | 저자 시뮬레이션 | 통념에 대한 판단 |
|---|---|---|---|
| 성분 | 냄새는 황화합물 농도가 결정, 소리와 직접 관련 없음(간접 근거) | 다루지 않음 | 지지 근거 없음 |
| 확산 | 몸 주변 상승 기류가 근접 오염원을 본인 호흡 영역으로 나름 | 조용한 방출은 옆 사람 코를 비껴감 | 옆 사람에게는 반대 |
| 지각과 기억 | 주의와 선택 편향이 드물고 눈에 띄는 조합을 과대 기억하게 함 | 기억된 비교의 91.5%가 조용한 쪽 | 믿음의 원인을 설명 |

세 주제의 근거는 한 방향을 가리킨다. 성분 문헌은 소리와 냄새 물질이 따로 정해진다는 것을 보여 주고, 확산 문헌과 시뮬레이션은 조용한 방출이 옆 사람보다 방출자 쪽으로 간다는 것을 보여 준다. 지각 문헌은 그런데도 왜 반대의 믿음이 생기는지를 설명한다. 연구 결과가 엇갈리는 지점은 대부분 "누구의 코인가"와 "어떤 비교 기준인가"의 차이에서 온다. 경로를 무시한 분석 모델에서는 조용한 쪽이 이기는 경우가 48%였지만, 경로를 넣으면 0.4%로 줄었다. 방출자 본인의 코에서는 조용한 쪽이 더 독한 경우가 4.6%로 옆 사람보다 열 배 이상 많았다(소리 나는 쪽은 17.9%). 앉은 자세에서 조용한 방출이 경계층을 타고 본인 얼굴로 오기 때문이다. 그래도 본인의 코에서조차 소리 나는 쪽이 더 자주 독했다. 장면별로는 마주 선 두 사람에서만 조용한 쪽이 근소하게 앞섰는데(0.04% 대 0.00%), 이는 99.96%의 비교에서 둘 다 냄새를 맡지 못하는 수준의 차이이다.

결론이 가정에 얼마나 민감한지도 확인하였다. 탐지 확률 곡선의 기울기와 꼬리 모양(로지스틱, 역치 아래 0)을 바꿔도 소리 나는 쪽이 4–111배 자주 이겼고, 기억의 조용 우세는 62–100%였다. 방출 시간, 출구 크기, 소리가 나기 시작하는 압력을 바꾼 경우에도 방향은 같았다. 평균 농도 대신 순간 최고 농도를 쓰더라도, 조용한 방출에만 약 14배의 피크 계수가 붙어야 결과가 뒤집힌다.

근거의 수준은 단계마다 다르다. 성분과 지각 단계는 여러 실험 연구가 같은 방향을 보여 주지만 방귀를 직접 다룬 연구는 적고, 확산 단계에서 방귀를 직접 다룬 근거는 저자의 시뮬레이션뿐이다. 또 통념은 개인의 경험만으로 생기지 않는다. 사람들은 그럴듯한 연관이라면 자료와 무관하게 믿고 보고하므로(Chapman 1967), 한 번 말로 굳어진 통념은 각자의 기억 편향과 서로를 강화하며 전해질 수 있다.

이 결론에는 한계가 있다. 첫째, 방귀 한 번마다 소리와 냄새를 함께 측정한 동료 심사 연구가 없어 성분 단계의 근거가 간접적이다. 둘째, 시뮬레이션은 동료 심사 전이고 난류의 평균만 계산하였다. 순간 변동(LES)과 엘리베이터 장면은 계산 중이며, 앉은 사람의 상승 기류를 실측보다 40–56% 빠르게 예측한다는 점도 확인하였다. 셋째, 탐지 확률이 50% 아래인 영역은 측정 자료 밖으로 외삽한 것이다. 넷째, 기억의 선택 효과는 설명 가능성을 보인 것이며 설문으로 검증하지는 않았다. 이 설명이 맞다면, 냄새를 못 맡는 사람이나 방출자 본인은 이 통념을 덜 믿을 것이라는 예측을 검증해 볼 수 있다. 다른 조건으로 확장할 때에는 자세, 환기, 사람 사이 거리가 경로를 바꾼다는 점을 고려해야 한다. 마주 선 경우처럼 경로가 다르면 결과의 크기도 달라질 수 있다.

## 제4장 결론

"소리 없는 방귀가 더 독하다"는 통념은 곁에 있는 사람이 실제로 맡는 냄새에 대해서는 대체로 틀렸다. 냄새 물질은 소리와 따로 정해지고, 조용한 방출은 몸의 상승 기류를 타고 옆 사람의 코를 비껴가는 경우가 많다. 실제 빈도로 가중하면 옆 사람에게 소리 나는 방귀가 더 독한 경우가 조용한 방귀보다 약 17배 많다. 그런데도 이 믿음이 널리 퍼진 것은 조용한 방귀가 냄새를 맡았을 때만 기억에 남기 때문이다. 이 선택 효과만으로 기억 속 비교의 90% 이상이 "조용한 쪽이 더 독했다"가 된다. 즉 물리로 보면 드물지만, 기억으로는 대부분 그렇다. 조용한 방귀가 더 독한 경우가 가장 많아지는 것은 앉은 자세에서 방출자 본인의 코처럼 조용한 방출이 몸 가까이 머무는 경우이지만, 이때에도 소리 나는 방귀가 더 자주 독하다.

## 참고문헌

- Amoore, J. E., & Hautala, E. (1983). Odor as an aid to chemical safety: odor thresholds compared with threshold limit values and volatilities for 214 industrial chemicals in air and water dilution. *Journal of Applied Toxicology*, 3(6), 272–290. https://doi.org/10.1002/jat.2550030603
- Ancalle, D. S., Finn, C. L., Jiang, N., Stewart, S. A., & Hu, D. L. (2021). Physics of flatulence. *Journal of the Acoustical Society of America*, 150(4_Supplement), A164 (학회 초록). https://doi.org/10.1121/10.0007996
- Berkson, J. (1946). Limitations of the application of fourfold table analysis to hospital data. *Biometrics Bulletin*, 2(3), 47–53. https://doi.org/10.2307/3002000
- Chapman, L. J. (1967). Illusory correlation in observational report. *Journal of Verbal Learning and Verbal Behavior*, 6(1), 151–155. https://doi.org/10.1016/S0022-5371(67)80066-5
- Dalton, P. (1996). Odor perception and beliefs about risk. *Chemical Senses*, 21(4), 447–458. https://doi.org/10.1093/chemse/21.4.447
- Dowling, D. R., & Dimotakis, P. E. (1990). Similarity of the concentration field of gas-phase turbulent jets. *Journal of Fluid Mechanics*, 218, 109–141. https://doi.org/10.1017/S0022112090000945
- Fallon, N. B., Giesbrecht, T., & Stančák, A. (2018). Attentional modulation of desensitization to odor. *Attention, Perception, & Psychophysics*, 80, 1064–1071. https://doi.org/10.3758/s13414-018-1539-2
- Forster, S., & Spence, C. (2018). "What smell?" Temporarily loading visual attention induces a prolonged loss of olfactory awareness. *Psychological Science*, 29(10), 1642–1652. https://doi.org/10.1177/0956797618781325
- Furne, J. K., & Levitt, M. D. (1996). Factors influencing frequency of flatus emission by healthy subjects. *Digestive Diseases and Sciences*, 41(8), 1631–1635. https://doi.org/10.1007/BF02087912
- Greenberg, M. I., Curtis, J. A., & Vearrier, D. (2013). The perception of odor is not a surrogate marker for chemical exposure: a review of factors influencing human odor perception. *Clinical Toxicology*, 51(2), 70–76. https://doi.org/10.3109/15563650.2013.767908
- Grose, F. (1811). *Dictionary of the Vulgar Tongue*. London (항목 'fice', 공유 저작물).
- Hamilton, D. L., & Gifford, R. K. (1976). Illusory correlation in interpersonal perception: a cognitive basis of stereotypic judgments. *Journal of Experimental Social Psychology*, 12(4), 392–407. https://doi.org/10.1016/S0022-1031(76)80006-6
- Licina, D., Pantelic, J., Melikov, A., Sekhar, C., & Tham, K. W. (2014). Experimental investigation of the human convective boundary layer in a quiescent indoor environment. *Building and Environment*, 75, 79–91. https://doi.org/10.1016/j.buildenv.2014.01.016
- Licina, D., Melikov, A., Sekhar, C., & Tham, K. W. (2015). Human convective boundary layer and its interaction with room ventilation flow. *Indoor Air*, 25(1), 21–35. https://doi.org/10.1111/ina.12120
- Licina, D., Tian, Y., & Nazaroff, W. W. (2017). Inhalation intake fraction of particulate matter from localized indoor emissions. *Building and Environment*, 123, 14–22. https://doi.org/10.1016/j.buildenv.2017.06.037
- Rim, D., & Novoselac, A. (2009). Transport of particulate and gaseous pollutants in the vicinity of a human body. *Building and Environment*, 44(9), 1840–1849. https://doi.org/10.1016/j.buildenv.2008.12.009
- Rim, D., & Novoselac, A. (2010). Ventilation effectiveness as an indicator of occupant exposure to particles from indoor sources. *Building and Environment*, 45(5), 1214–1224. https://doi.org/10.1016/j.buildenv.2009.11.004
- Seo, H.-S., & Hummel, T. (2011). Auditory-olfactory integration: congruent or pleasant sounds amplify odor pleasantness. *Chemical Senses*, 36(3), 301–309. https://doi.org/10.1093/chemse/bjq129
- Snoep, J. D., Morabia, A., Hernández-Díaz, S., Hernán, M. A., & Vandenbroucke, J. P. (2014). Commentary: a structural approach to Berkson's fallacy and a guide to a history of opinions about it. *International Journal of Epidemiology*, 43(2), 515–521. https://doi.org/10.1093/ije/dyu026
- Snyder, W. (2020, 2022 갱신). The sound of stink. flatology.com (블로그, 동료 심사 없음). https://flatology.com/the-sound-of-stink/
- Stevens, J. C., Cain, W. S., & Burke, R. J. (1988). Variability of olfactory thresholds. *Chemical Senses*, 13(4), 643–653. https://doi.org/10.1093/chemse/13.4.643
- Suarez, F. L., Furne, J. K., Springfield, J., & Levitt, M. D. (1997). Insights into human colonic physiology obtained from the study of flatus composition. *American Journal of Physiology – Gastrointestinal and Liver Physiology*, 272(5), G1028–G1033. https://doi.org/10.1152/ajpgi.1997.272.5.G1028
- Suarez, F. L., Springfield, J. R., & Levitt, M. D. (1998). Identification of gases responsible for the odour of human flatus and evaluation of a device purported to reduce this odour. *Gut*, 43(1), 100–104. https://doi.org/10.1136/gut.43.1.100
- Tangerman, A. (2009). Measurement and biological significance of the volatile sulfur compounds hydrogen sulfide, methanethiol and dimethyl sulfide in various biological matrices. *Journal of Chromatography B*, 877, 3366–3377. https://doi.org/10.1016/j.jchromb.2009.05.026
- Tomlin, J., Lowis, C., & Read, N. W. (1991). Investigation of normal flatus production in healthy volunteers. *Gut*, 32(6), 665–669. https://doi.org/10.1136/gut.32.6.665
- Whisman, M. L., Goetzinger, J. W., & Cotton, F. O. (1978). Odorant evaluation: a study of ethanethiol and tetrahydrothiophene as warning agents in propane. *Environmental Science & Technology*, 12, 1285–1288. https://doi.org/10.1021/es60147a003
- [저자] (2026). 미출간 시뮬레이션: 소파와 서 있는 두 사람의 방귀 확산 CFD(OpenFOAM 13, RANS)와 몬테카를로 계산. 동료 심사 전. [공개 저장소나 프리프린트가 생기면 주소 기입]
