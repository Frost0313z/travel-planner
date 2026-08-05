# travel-planner

LLM API와 지도/장소 검색 API를 조합해 국내 여행지를 추천하고 맛집 정보를 담은 여행 리포트를 생성하는 CLI 프로그램

## 목차

- [빠른 시작](#빠른-시작)
- [기능](#기능)
- [API 키 설정 방법](#api-키-설정-방법)
- [결과물 확인 방법](#결과물-확인-방법)
- [프로젝트 구조](#프로젝트-구조)
- [개발 환경 확인](#개발-환경-확인)
- [설계 노트](#설계-노트)
- [라이선스](#라이선스)

## 빠른 시작

```bash
python -m venv .venv
./.venv/Scripts/pip install -r requirements.txt   # macOS/Linux: .venv/bin/pip

cp .env.example .env   # 이후 .env에 실제 키 값 입력

python main.py --date "2026-03-15"
```

실행하면 `results/2026-03-15_travel_plan.md`, `results/2026-03-15_travel_plan.json`이 생성됩니다.

## 기능

| 번호 | 기능 | 설명 |
|---|---|---|
| 1 | CLI 인자 파싱 | `--date "YYYY-MM-DD"` 필수 옵션, 형식이 틀리면 사용법 출력 후 종료 |
| 2 | 1차 추천 생성 (LLM) | 입력 날짜를 바탕으로 추천 도시/날씨/행사/추천 이유를 JSON으로 생성 |
| 3 | 맛집 검색 (지도/장소 API) | 추천 도시 기준으로 NAVER API HUB 지역 검색으로 맛집 최대 5곳 조회 |
| 4 | 최종 리포트 생성 (LLM) | 1차 추천 + 맛집 목록 + 오류 목록을 종합해 Markdown 리포트 생성 |
| 5 | 결과 저장 | `results/` 폴더에 원본 데이터 JSON과 최종 리포트 Markdown 저장 |
| 6 | 오류 처리 | API 키 미설정 시 즉시 종료, 장소 검색 실패 시 "데이터 없음"으로 계속 진행, LLM JSON 파싱 실패 시 1회 재시도 |

## API 키 설정 방법

1. `.env.example`을 복사해 `.env`로 저장한다.
2. 아래 값을 채운다.
   - `OPENAI_API_KEY`: https://platform.openai.com/api-keys 에서 발급 (필수 — 없으면 프로그램이 즉시 종료되며 안내 메시지를 출력한다)
   - `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`: NAVER Cloud Platform 콘솔 → Application Services → **NAVER API HUB** → Application 등록 후 "인증 정보"에서 확인 (미설정 시 맛집 섹션만 "데이터 없음"으로 처리되고 프로그램은 계속 진행된다)
3. `.env`는 `.gitignore`에 등록되어 있어 저장소에 커밋되지 않는다.

### ⚠️ API 키 유출 주의사항

- API 키를 코드, README, 커밋 메시지, 로그, 결과물(`results/*.json`, `*.md`)에 직접 작성하지 않는다.
- 이 저장소의 모든 코드는 `os.getenv()`로만 키를 읽으며, 하드코딩된 키 값은 존재하지 않는다.
- 키가 실수로 커밋되었다면 즉시 해당 서비스 콘솔에서 키를 폐기(revoke)하고 재발급해야 한다 — `git revert`만으로는 이미 노출된 키 값 자체는 무효화되지 않는다.

## 결과물 확인 방법

```bash
python main.py --date "2026-03-15"
```

- 콘솔에 `[1/3] → [2/3] → [3/3]` 진행 로그와 완료 메시지(결과 저장 경로)가 출력된다.
- `results/{date}_travel_plan.json`: 1차 추천 JSON, 맛집 검색 결과(0건 가능), 오류 요약(`errors`, 비어있어도 배열로 존재)을 포함한 원본 데이터.
- `results/{date}_travel_plan.md`: 추천 지역/이유, 날씨, 행사/축제, 맛집, 1일 일정, 오류 요약을 포함한 최종 리포트.
- `results/2026-03-15_travel_plan.{json,md}`는 OpenAI + NAVER API HUB 지역 검색 API를 실제로 호출해 얻은 예시 결과물이다 (맛집 5곳 포함 정상 케이스).
- 지도/장소 API 키가 없거나 인증에 실패해도 프로그램은 중단되지 않고 맛집 섹션을 "데이터 없음"으로 표기한 뒤 계속 진행한다 — 이 동작은 `git log`상 이전 커밋들에서 실제 실행 결과로도 확인할 수 있다.

## 프로젝트 구조

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

## 개발 환경 확인

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

## 설계 노트

- **데이터 구조를 이렇게 선택한 이유**: 1차 추천(JSON) → 맛집 검색(list[dict]) → 최종 리포트(Markdown str) 각 단계를 순수 함수 입출력으로 연결했다. 각 단계가 이전 단계의 반환값만 입력으로 받고 전역 상태를 공유하지 않아, 특정 단계(예: 지도 API)만 실패해도 나머지 파이프라인이 정상 동작함을 보장하기 쉽다. 오류는 `{"step", "type", "message"}` 형태의 리스트(`errors`)로 누적해 원본 JSON과 최종 리포트 양쪽에서 동일한 근거로 참조한다.
- **반복문·종료 조건을 이렇게 설계한 이유**: 이 프로그램은 대화형 메뉴 루프가 아니라 `--date` 인자를 받아 한 번 실행되고 종료되는 단발성 CLI다. 종료 조건은 "3단계(추천 → 검색 → 리포트)를 모두 마치고 결과를 저장했는가"이며, 각 단계는 자체 `try-except`로 감싸 한 단계의 예외가 프로그램 전체를 중단시키지 않고 다음 단계로 흐르도록 했다(단, 필수 키인 `OPENAI_API_KEY`가 아예 없는 경우만 예외적으로 즉시 종료한다).
- **브랜치를 나눈(혹은 나누지 않은) 기준**: 기능 단위(CLI 파싱, LLM 연동, 장소 검색, 저장, 오케스트레이션)로 커밋을 분리했다. 각 기능이 서로 다른 파일에 명확히 분리되어 있어 병렬 작업 시 충돌 가능성이 낮다고 판단해, 이번 미션에서는 단일 브랜치(main)에서 기능별 커밋으로 이력을 관리했다.
- **데이터 영속화 방안 제안**: 현재는 실행할 때마다 `results/{date}_travel_plan.{json,md}` 파일로 저장한다. 반복 조회가 잦아진다면 SQLite로 옮겨 `date`를 기본키로 하는 테이블에 원본 JSON을 저장하고, 리포트는 필요 시 재생성하는 방식이 API 호출 비용을 줄이는 데 유리하다.
- **동명 항목·값 충돌 처리 정책**: 같은 `--date`로 재실행하면 `results/{date}_travel_plan.*` 파일을 덮어쓴다(최신 실행 결과가 항상 최종본이라는 원칙). 과거 실행 이력을 보존하고 싶다면 파일명에 실행 시각(예: `{date}_{HHMMSS}`)을 추가로 붙이는 방식으로 확장할 수 있다.

## 라이선스

[MIT](./LICENSE)
