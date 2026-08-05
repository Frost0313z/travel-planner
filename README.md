# 🧭 travel-planner

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI-412991?logo=openai&logoColor=white)
![NAVER API HUB](https://img.shields.io/badge/place%20search-NAVER%20API%20HUB-03C75A?logo=naver&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

LLM API(OpenAI)와 지도/장소 검색 API(NAVER API HUB 지역 검색)를 조합해, 날짜 하나만 입력하면
**추천 여행지 → 날씨/행사 → 맛집 → 1일 일정**까지 담은 국내 여행 리포트를 자동으로 만들어주는 CLI 프로그램입니다.

Codyssey 대전 캠퍼스 "Python 응용: API 활용 국내 여행지 추천 프로그램 개발" 미션 결과물입니다.

## 목차

- [🚀 빠른 시작](#-빠른-시작)
- [📋 기능](#-기능)
- [🖥️ 실행 예시](#️-실행-예시)
- [🔑 API 키 설정 방법](#-api-키-설정-방법)
- [⚠️ API 키 유출 주의사항](#️-api-키-유출-주의사항)
- [📂 결과물 확인 방법](#-결과물-확인-방법)
- [🧱 프로젝트 구조](#-프로젝트-구조)
- [🛠️ 개발 환경 확인](#️-개발-환경-확인)
- [🧠 설계 노트](#-설계-노트)
- [📄 라이선스](#-라이선스)

## 🚀 빠른 시작

```bash
git clone https://github.com/Frost0313z/travel-planner.git
cd travel-planner

python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # macOS/Linux: .venv/bin/pip

cp .env.example .env   # 이후 .env에 실제 키 값 입력

python main.py --date "2026-03-15"
```

- Python 3.10 이상 필요
- `OPENAI_API_KEY`는 필수, `NAVER_CLIENT_ID`/`NAVER_CLIENT_SECRET`은 없어도 실행되지만 맛집 섹션이 "데이터 없음"으로 처리됩니다
- 실행하면 `results/2026-03-15_travel_plan.md`, `results/2026-03-15_travel_plan.json`이 생성됩니다

## 📋 기능

| 번호 | 기능 | 설명 |
|:---:|---|---|
| 1 | 🖊️ CLI 인자 파싱 | `--date "YYYY-MM-DD"` 필수 옵션, 형식이 틀리면 사용법 출력 후 종료 |
| 2 | 🌤️ 1차 추천 생성 (LLM) | 입력 날짜를 바탕으로 추천 도시/날씨/행사/추천 이유를 JSON으로 생성 |
| 3 | 🍽️ 맛집 검색 (지도/장소 API) | 추천 도시 기준으로 NAVER API HUB 지역 검색으로 맛집 최대 5곳 조회 |
| 4 | 📝 최종 리포트 생성 (LLM) | 1차 추천 + 맛집 목록 + 오류 목록을 종합해 Markdown 리포트 생성 |
| 5 | 💾 결과 저장 | `results/` 폴더에 원본 데이터 JSON과 최종 리포트 Markdown 저장 |
| 6 | 🛡️ 오류 처리 | API 키 미설정 시 즉시 종료, 장소 검색 실패 시 "데이터 없음"으로 계속 진행, LLM JSON 파싱/스키마 검증 실패 시 1회 재시도 |
| 7 | ⚡ 결과 캐싱 (보너스) | 같은 `--date`로 재실행 시 `results/`에 저장된 결과가 있으면 API 호출 없이 그대로 재사용 |

## 🖥️ 실행 예시

```
$ python main.py --date "2026-03-15"
[1/3] 1차 추천 생성 중(LLM)...
- recommended_city: "제주"
[2/3] 맛집 검색 중(지도/장소 API)...
- 맛집 5곳 검색 완료
[3/3] 최종 리포트 생성 중(LLM)...
- 리포트 생성 완료

완료! results\2026-03-15_travel_plan.md 를 확인하세요.
```

생성된 리포트(`results/2026-03-15_travel_plan.md`) 일부:

```markdown
# 2026-03-15 국내 여행 추천 리포트

## 추천 지역
제주

## 맛집 추천
- [둘레길 서귀포중문본점](https://www.instagram.com/number1_jeju?igsh=MXc3eXd3MTVwbjFndg==)
  주소: 제주특별자치도 서귀포시 천제연로 209-1 2층 둘레길
  카테고리: 음식점>양식
...
```

실제 실행 결과 전체는 [`results/2026-03-15_travel_plan.md`](results/2026-03-15_travel_plan.md), 원본 데이터는 [`results/2026-03-15_travel_plan.json`](results/2026-03-15_travel_plan.json)에서 확인할 수 있습니다.

날짜 형식이 잘못되면 사용법을 출력하고 종료합니다:

```
$ python main.py --date "2026/03/15"
usage: travel_planner [-h] --date DATE
travel_planner: error: 날짜 형식이 올바르지 않습니다: "2026/03/15" (예: --date "2026-03-15")
```

같은 날짜로 다시 실행하면 캐시를 사용해 API를 호출하지 않습니다:

```
$ python main.py --date "2026-03-15"
같은 날짜(2026-03-15)의 캐시된 결과를 재사용합니다 (API 호출 없음).
완료! results\2026-03-15_travel_plan.md 를 확인하세요.
```

### 1차 추천 JSON 스키마

`llm_client._has_expected_types()`가 아래 타입을 검증하며, 맞지 않으면 파싱 실패로 간주해 재시도합니다.

| 키 | 타입 | 예시 값 |
|---|---|---|
| `recommended_city` | `str` (빈 문자열 불가) | `"제주"` |
| `weather` | `str` | `"3월 중순 평균 15°C 내외"` |
| `events` | `list[str]` (1~3개 권장) | `["유채꽃 축제"]` |
| `reason` | `str` | `"봄꽃을 즐기기 좋은 시기입니다."` |

## 🔑 API 키 설정 방법

1. `.env.example`을 복사해 `.env`로 저장한다.
2. 아래 값을 채운다.
   - `OPENAI_API_KEY`: https://platform.openai.com/api-keys 에서 발급 (필수 — 없으면 프로그램이 즉시 종료되며 안내 메시지를 출력한다)
   - `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`: NAVER Cloud Platform 콘솔 → Application Services → **NAVER API HUB** → Application 등록 후 "인증 정보"에서 확인 (미설정 시 맛집 섹션만 "데이터 없음"으로 처리되고 프로그램은 계속 진행된다)
3. `.env`는 `.gitignore`에 등록되어 있어 저장소에 커밋되지 않는다.

### 🔧 지도 API 401/403 디버깅 체크리스트

`place_search.py` 실행 중 `AUTH_ERROR`(401/403)가 나면 아래 순서로 점검한다.

1. 헤더 이름 오타 확인 — 반드시 `X-NCP-APIGW-API-KEY-ID` / `X-NCP-APIGW-API-KEY` (구버전 `X-Naver-Client-Id`가 아님, [API 키 설정 방법](#-api-키-설정-방법) 참고)
2. NCP 콘솔에서 해당 Application이 **"검색"** API를 사용하도록 등록되어 있는지 확인
3. `.env`에 복사한 Client ID/Secret 앞뒤에 공백이나 줄바꿈이 섞이지 않았는지 확인
4. 쿼터 초과 여부 — NCP 콘솔의 Application 사용량 대시보드에서 확인
5. 위 항목을 모두 확인해도 실패하면 새 Application을 재발급받아 대체

이 체크리스트로도 해결되지 않으면 프로그램은 중단되지 않고 맛집 섹션을 "데이터 없음"으로 표기한 채 계속 진행한다.

## ⚠️ API 키 유출 주의사항

- API 키를 코드, README, 커밋 메시지, 로그, 결과물(`results/*.json`, `*.md`)에 직접 작성하지 않는다.
- 이 저장소의 모든 코드는 `os.getenv()`로만 키를 읽으며, 하드코딩된 키 값은 존재하지 않는다.
- 키가 실수로 커밋되었다면 즉시 해당 서비스 콘솔에서 키를 폐기(revoke)하고 재발급해야 한다 — `git revert`만으로는 이미 노출된 키 값 자체는 무효화되지 않는다.

## 📂 결과물 확인 방법

```bash
python main.py --date "2026-03-15"
```

- 콘솔에 `[1/3] → [2/3] → [3/3]` 진행 로그와 완료 메시지(결과 저장 경로)가 출력된다.
- `results/{date}_travel_plan.json`: 1차 추천 JSON, 맛집 검색 결과(0건 가능), 오류 요약(`errors`, 비어있어도 배열로 존재)을 포함한 원본 데이터.
- `results/{date}_travel_plan.md`: 추천 지역/이유, 날씨, 행사/축제, 맛집, 1일 일정, 오류 요약을 포함한 최종 리포트.
- `results/2026-03-15_travel_plan.{json,md}`는 OpenAI + NAVER API HUB 지역 검색 API를 실제로 호출해 얻은 예시 결과물이다 (맛집 5곳 포함 정상 케이스).
- 지도/장소 API 키가 없거나 인증에 실패해도 프로그램은 중단되지 않고 맛집 섹션을 "데이터 없음"으로 표기한 뒤 계속 진행한다 — 이 동작은 `git log`상 이전 커밋들에서 실제 실행 결과로도 확인할 수 있다.

## 🧱 프로젝트 구조

```
travel-planner/
├── main.py                   진입점 (stdout/stdin/stderr UTF-8 재설정 후 core.run 호출)
├── requirements.txt
├── .env.example               API 키 템플릿 (.env는 gitignore 대상)
├── results/                   실행 결과 저장 위치
└── travel_planner/
    ├── __init__.py
    ├── cli.py                 argparse 인자 파싱 + 날짜 형식 검증
    ├── config.py               .env 로드 + API 키 누락 시 안내 후 종료
    ├── data.py                 상수, LLM 프롬프트, API 엔드포인트
    ├── llm_client.py           OpenAI 연동 (1차 추천, 최종 리포트 생성, JSON 파싱 재시도)
    ├── place_search.py        NAVER API HUB 지역 검색 연동 (맛집 검색)
    ├── storage.py              결과 JSON/Markdown 저장
    └── core.py                 전체 파이프라인 오케스트레이션
```

## 🛠️ 개발 환경 확인

`python scripts/new_mission.py env-doc <이 프로젝트 경로> --write` 로 아래 구간을 채우세요.

<!-- ENV_EVIDENCE_START -->

`python -V`

```
Python 3.14.6
```

`git --version`

```
git version 2.55.0.windows.3
```

`git config user.name / user.email`

```
Drako_Dev
msong7618@gmail.com
```

`git log --oneline --graph --all`

```
* 534b48b feat: 결과 캐싱 보너스 과제 구현 (네이토 사전평가 #16 반영)
* f6e0e57 fix: 1차 추천 JSON 응답에 타입 검증 추가 (네이토 사전평가 #7 반영)
* 0e991a1 docs: 개발환경 증빙 git log를 최신 커밋까지 갱신
* 2f13f14 docs: 리드미를 배지/이모지/실행 예시 포함한 rich한 형태로 재작성
* d709a70 docs: 결과물 확인 안내 및 개발환경 증빙을 최신 커밋 이력으로 갱신
* 8b82669 fix: NAVER API HUB 지역 검색 엔드포인트를 실제 발급 키로 검증된 URL로 수정
* 734184f docs: README 사용법, API 키 설정, 설계 노트, 개발환경 증빙 작성
* 9f6807f fix: stderr UTF-8 재설정 및 리포트 제목/오류 요약 형식을 미션 예시에 맞춤
* 7da53d4 feat: 전체 파이프라인 오케스트레이션 (core.run) 구현
* b9a0c8f feat: 결과 저장 (JSON/Markdown) 구현
* f588b40 feat: 네이버 지역 검색 API 연동 - 맛집 검색 구현
* 8a78545 feat: LLM 연동 - 1차 추천 및 최종 리포트 생성 구현
* 86982a9 feat: CLI 인자 파싱, 날짜 검증, API 키 로드 구현
* 00466f1 chore: 의존성 정의 및 환경변수 템플릿 추가
* d9554c6 chore: 프로젝트 구조 초기화
```

<!-- ENV_EVIDENCE_END -->

## 🧠 설계 노트

- **데이터 구조를 이렇게 선택한 이유**: 1차 추천(JSON) → 맛집 검색(list[dict]) → 최종 리포트(Markdown str) 각 단계를 순수 함수 입출력으로 연결했다. 각 단계가 이전 단계의 반환값만 입력으로 받고 전역 상태를 공유하지 않아, 특정 단계(예: 지도 API)만 실패해도 나머지 파이프라인이 정상 동작함을 보장하기 쉽다. 오류는 `{"step", "type", "message"}` 형태의 리스트(`errors`)로 누적해 원본 JSON과 최종 리포트 양쪽에서 동일한 근거로 참조한다. 함수 시그니처는 `recommend_destination(api_key, date) -> dict`, `search_restaurants(client_id, secret, city) -> (list, error|None)`, `generate_report(api_key, date, recommendation, restaurants, errors) -> str`으로, 각 모듈 상단의 함수만 보면 입출력을 바로 알 수 있게 했다.
- **반복문·종료 조건을 이렇게 설계한 이유**: 이 프로그램은 대화형 메뉴 루프가 아니라 `--date` 인자를 받아 한 번 실행되고 종료되는 단발성 CLI다. 종료 조건은 "3단계(추천 → 검색 → 리포트)를 모두 마치고 결과를 저장했는가"이며, 각 단계는 자체 `try-except`로 감싸 한 단계의 예외가 프로그램 전체를 중단시키지 않고 다음 단계로 흐르도록 했다(단, 필수 키인 `OPENAI_API_KEY`가 아예 없는 경우만 예외적으로 즉시 종료한다).
- **브랜치를 나눈(혹은 나누지 않은) 기준**: 기능 단위(CLI 파싱, LLM 연동, 장소 검색, 저장, 오케스트레이션)로 커밋을 분리했다. 각 기능이 서로 다른 파일에 명확히 분리되어 있어 병렬 작업 시 충돌 가능성이 낮다고 판단해, 이번 미션에서는 단일 브랜치(main)에서 기능별 커밋으로 이력을 관리했다.
- **데이터 영속화 방안 제안**: 현재는 실행할 때마다 `results/{date}_travel_plan.{json,md}` 파일로 저장하고, 같은 date로 재실행하면 캐시를 재사용한다(아래 캐싱 항목 참고). 반복 조회가 더 잦아진다면 SQLite로 옮겨 `date`를 기본키로 하는 테이블에 원본 JSON을 저장하는 방식이 다음 단계다.
- **동명 항목·값 충돌 처리 정책**: 같은 `--date`로 재실행하면 캐시가 있을 때는 API를 호출하지 않고 기존 `results/{date}_travel_plan.*` 파일을 그대로 재사용한다(최신 결과를 덮어쓰지 않고 최초 실행 결과를 최종본으로 취급). 강제로 새로 생성하고 싶다면 해당 파일을 지우고 재실행하면 된다. 과거 실행 이력을 모두 보존하고 싶다면 파일명에 실행 시각(예: `{date}_{HHMMSS}`)을 추가하는 방식으로 확장할 수 있다.
- **지도/장소 API를 다른 제공자로 교체하기 쉽게 만든 방법**: `place_search.py`는 NAVER 전용 구현이지만, `core.py`는 이 모듈을 `search_restaurants(client_id, secret, city) -> (list, error)`라는 함수 시그니처로만 의존한다. 별도의 추상 클래스 없이도 이 시그니처를 지키는 모듈만 새로 만들어 `core.py`의 import 한 줄만 바꾸면 Kakao Local 등 다른 제공자로 교체할 수 있다 — 인터페이스를 무겁게 만들기보다 "교체 시 바뀌는 파일을 1개로 최소화"하는 쪽을 택했다.
- **GET/POST 선택 근거**: 장소 검색(`place_search.py`)은 상태를 바꾸지 않는 조회이므로 GET을 사용했다 — 같은 요청을 여러 번 보내도 안전(idempotent)하고 캐싱하기도 쉽다. LLM 호출(OpenAI SDK 내부)은 매 요청마다 새 텍스트를 생성하는 생성형 요청이라 멱등하지 않으므로 SDK가 내부적으로 POST를 사용한다 — 이 프로젝트 코드에서 직접 HTTP 메서드를 고르는 부분은 장소 검색뿐이라 그 근거만 명시한다.
- **LLM 출력에 JSON을 강제하는 이유**: 1차 추천 결과(`recommended_city` 등)는 다음 단계인 맛집 검색의 입력으로 그대로 쓰인다. 자연어 문장으로 받으면 도시명을 다시 추출하는 파싱 로직이 따로 필요하고 실패 가능성도 커지므로, 프롬프트에서 JSON 스키마를 강제해 `json.loads()` 한 번으로 바로 다음 단계에 넘길 수 있게 했다. 스키마가 깨지면(키 누락·타입 불일치) 재시도하도록 만들어 이 강제를 코드로도 검증한다.
- **맛집 0건일 때의 대체 전략(현재 한계)**: 지금은 0건이면 그대로 "데이터 없음"으로 표기하고 끝낸다. 근교 지역으로 검색어를 넓히거나 카테고리를 "맛집"에서 "음식점"으로 완화해 재검색하는 전략은 구현하지 않았다 — 재검색 자체가 또 다른 실패 지점을 늘리므로, 이번 범위에서는 "실패를 숨기지 않고 있는 그대로 보여준다"는 원칙을 우선했다.
- **추천 도시명 정규화의 한계**: LLM이 반환한 `recommended_city`를 그대로 검색어(`f"{city} 맛집"`)로 사용한다. "제주"/"제주도"/"제주시"처럼 같은 지역을 가리키는 다른 표기나, "강남"처럼 여러 지역에 걸친 이름에 대한 동음이의 처리·세부 지역 추출은 하지 않는다. 이번 미션의 핵심은 API 연동이라 판단해 우선순위에서 뒤로 뒀고, 실제 서비스라면 지역명 사전 매핑이나 지오코딩 API로 먼저 정규화하는 단계를 추가해야 한다.
- **키 노출 방지·회전**: `.env`가 커밋되지 않는지는 `git grep`으로 수동 확인했다(이 저장소의 모든 커밋에 대해 실제로 검사 완료). 반복적으로 검사하려면 pre-commit 훅에 `git diff --cached | grep -E "sk-|X-NCP"` 같은 패턴 검사를 추가할 수 있다. 키가 유출됐을 때는 `git revert`가 아니라 발급처 콘솔에서 즉시 키를 폐기(revoke)하고 재발급해야 하며, 운영 환경이라면 정기적인 키 회전이나 AWS Secrets Manager 같은 시크릿 관리 서비스 연동을 권장한다.
- **오류 이력 조회**: 지금은 실행 1회의 `errors`만 해당 실행의 JSON 파일에 남는다. 여러 번 실행한 이력을 모아서 보려면 `results/*.json`을 전부 읽어 `errors` 배열만 합치는 별도 집계 스크립트를 추가하면 된다(이번 범위에는 포함하지 않음).

## 📄 라이선스

[MIT](./LICENSE)
