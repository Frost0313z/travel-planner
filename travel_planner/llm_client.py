import json

from openai import OpenAI

from travel_planner.data import (
    OPENAI_MODEL,
    RECOMMENDATION_RETRY_SYSTEM_PROMPT,
    RECOMMENDATION_SYSTEM_PROMPT,
    REPORT_SYSTEM_PROMPT,
)

REQUIRED_RECOMMENDATION_KEYS = ("recommended_city", "weather", "events", "reason")


def recommend_destination(api_key, date):
    client = OpenAI(api_key=api_key)
    user_prompt = f"여행 날짜: {date}"

    raw_text = _chat(client, RECOMMENDATION_SYSTEM_PROMPT, user_prompt)
    parsed = _parse_recommendation_json(raw_text)
    if parsed is not None:
        return parsed

    # LLM JSON 파싱/스키마 검증 실패 시 1회 재시도
    print("- 1차 추천 응답이 스키마와 맞지 않아 재시도합니다 (최대 1회)...")
    retry_text = _chat(client, RECOMMENDATION_RETRY_SYSTEM_PROMPT, raw_text)
    parsed = _parse_recommendation_json(retry_text)
    if parsed is not None:
        return parsed

    raise ValueError(f"LLM 추천 결과를 JSON으로 파싱하지 못했습니다: {retry_text[:200]!r}")


def generate_report(api_key, date, recommendation, restaurants, errors):
    client = OpenAI(api_key=api_key)
    user_prompt = json.dumps(
        {
            "date": date,
            "recommendation": recommendation,
            "restaurants": restaurants,
            "errors": errors,
        },
        ensure_ascii=False,
    )
    return _chat(client, REPORT_SYSTEM_PROMPT, user_prompt)


def _chat(client, system_prompt, user_prompt):
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _parse_recommendation_json(text):
    cleaned = _strip_code_fence(text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    if not all(key in data for key in REQUIRED_RECOMMENDATION_KEYS):
        return None

    if not _has_expected_types(data):
        return None

    return data


def _has_expected_types(data):
    if not isinstance(data.get("recommended_city"), str) or not data["recommended_city"]:
        return False
    if not isinstance(data.get("weather"), str):
        return False
    if not isinstance(data.get("reason"), str):
        return False
    events = data.get("events")
    if not isinstance(events, list) or not all(isinstance(e, str) for e in events):
        return False
    return True


def _strip_code_fence(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
