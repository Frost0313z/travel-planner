from travel_planner.cli import parse_args
from travel_planner.config import load_api_keys
from travel_planner.llm_client import generate_report, recommend_destination
from travel_planner.place_search import search_restaurants
from travel_planner.storage import save_results


def run():
    args = parse_args()
    keys = load_api_keys()
    errors = []

    recommendation = _step_recommend(keys, args.date, errors)
    restaurants = _step_search_restaurants(keys, recommendation, errors)
    report_markdown = _step_generate_report(keys, args.date, recommendation, restaurants, errors)

    raw_data = {
        "date": args.date,
        "recommendation": recommendation,
        "restaurants": restaurants,
        "errors": errors,
    }
    _, md_path = save_results(args.date, raw_data, report_markdown)

    print(f"\n완료! {md_path} 를 확인하세요.")


def _step_recommend(keys, date, errors):
    print("[1/3] 1차 추천 생성 중(LLM)...")
    try:
        recommendation = recommend_destination(keys.openai_key, date)
        print(f'- recommended_city: "{recommendation["recommended_city"]}"')
        return recommendation
    except Exception as exc:
        errors.append({"step": "recommend", "type": "LLM_ERROR", "message": str(exc)})
        print(f"- 오류: 1차 추천 생성 실패 ({exc})")
        return {"recommended_city": "", "weather": "", "events": [], "reason": ""}


def _step_search_restaurants(keys, recommendation, errors):
    print("[2/3] 맛집 검색 중(지도/장소 API)...")
    city = recommendation.get("recommended_city")
    if not city:
        print("- 추천 지역이 없어 맛집 검색을 건너뜁니다.")
        return []

    restaurants, place_error = search_restaurants(
        keys.naver_client_id, keys.naver_client_secret, city
    )
    if place_error:
        errors.append(place_error)
        print(f"- 오류: {place_error['type']} ({place_error['message']})")
        print("- 맛집 섹션은 '데이터 없음'으로 처리하고 계속 진행합니다.")
    else:
        print(f"- 맛집 {len(restaurants)}곳 검색 완료")
    return restaurants


def _step_generate_report(keys, date, recommendation, restaurants, errors):
    print("[3/3] 최종 리포트 생성 중(LLM)...")
    try:
        report_markdown = generate_report(
            keys.openai_key, date, recommendation, restaurants, errors
        )
        print("- 리포트 생성 완료")
        return report_markdown
    except Exception as exc:
        errors.append({"step": "report", "type": "LLM_ERROR", "message": str(exc)})
        print(f"- 오류: 리포트 생성 실패 ({exc})")
        return _fallback_report(date, recommendation, restaurants, errors)


def _fallback_report(date, recommendation, restaurants, errors):
    lines = [
        f"# {date} 국내 여행 추천 리포트",
        "## 추천 지역",
        recommendation.get("recommended_city") or "데이터 없음",
        "## 추천 이유",
        recommendation.get("reason") or "데이터 없음",
        "## 날씨 요약",
        recommendation.get("weather") or "데이터 없음",
        "## 행사/축제",
        "\n".join(f"- {e}" for e in recommendation.get("events", [])) or "데이터 없음",
        "## 맛집 추천",
        "\n".join(f"- {r['name']} ({r['address']})" for r in restaurants) or "데이터 없음",
        "## 오류 요약(errors)",
        "\n".join(f"- {e['step']}: {e['type']} - {e['message']}" for e in errors) or "없음",
    ]
    return "\n\n".join(lines)
