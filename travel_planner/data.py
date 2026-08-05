RESULTS_DIR = "results"

OPENAI_MODEL = "gpt-4o-mini"

NAVER_LOCAL_SEARCH_URL = "https://openapi.naver.com/v1/search/local.json"
NAVER_RESTAURANT_DISPLAY_COUNT = 5

RECOMMENDATION_SYSTEM_PROMPT = (
    "너는 국내 여행 추천 전문가다. 사용자가 지정한 날짜를 기준으로, "
    "그 시기에 여행하기 좋은 국내 도시 한 곳을 추천한다. "
    "반드시 아래 JSON 스키마와 동일한 키를 갖는 JSON 객체 하나만 출력한다. "
    "다른 설명, 코드블록 표시(```) 없이 JSON 텍스트만 출력한다.\n"
    "{\n"
    '  "recommended_city": "도시 이름 (예: 제주)",\n'
    '  "weather": "해당 시기 일반적 날씨 요약",\n'
    '  "events": ["행사/축제 후보 1~3개"],\n'
    '  "reason": "추천 근거 2~4문장"\n'
    "}"
)

RECOMMENDATION_RETRY_SYSTEM_PROMPT = (
    "이전 응답이 올바른 JSON으로 파싱되지 않았다. "
    "recommended_city, weather, events, reason 네 개의 키만 담은 "
    "JSON 객체 하나만 다시 출력하라. 다른 텍스트는 절대 포함하지 마라."
)

REPORT_SYSTEM_PROMPT = (
    "너는 여행 리포트 작성 전문가다. 아래 입력 데이터(JSON)를 바탕으로 "
    "한국어 Markdown 형식의 최종 여행 리포트를 작성한다. "
    "입력 JSON의 date 값을 사용해 최상단에 '# {date} 국내 여행 추천 리포트' 형식의 "
    "제목(H1)을 작성한다. "
    "그 아래에 다음 순서의 섹션(##)을 모두 포함해야 한다: "
    "추천 지역, 추천 이유, 날씨 요약, 행사/축제, 맛집 추천, 1일 일정 제안, 오류 요약(errors). "
    "맛집 목록이 비어 있으면 '맛집 추천' 섹션에 '데이터 없음'이라고 표기한다. "
    "오류 목록이 비어 있으면 '오류 요약(errors)' 섹션에 '없음'이라고 표기한다. "
    "Markdown 본문만 출력하고 다른 설명은 덧붙이지 않는다."
)
