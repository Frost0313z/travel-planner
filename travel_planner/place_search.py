import requests

from travel_planner.data import (
    CITY_ADMIN_SUFFIXES,
    CITY_ALIASES,
    NAVER_LOCAL_SEARCH_URL,
    NAVER_RESTAURANT_DISPLAY_COUNT,
)

# 1차 검색이 0건이면 이 키워드로 한 번 더(카테고리를 넓혀서) 재검색한다.
BROADENED_KEYWORD = "음식점"


def normalize_city(city):
    """LLM이 반환한 도시명 표기를 검색어로 쓰기 좋은 표준 표기로 정규화한다.

    예: "제주도"/"제주특별자치도" -> "제주", "부산광역시" -> "부산".
    별칭 표에 없으면 행정구역 접미사(시/도/광역시 등)를 떼어낸 결과를 쓰고,
    그마저도 없으면 입력을 그대로 돌려준다(빈 문자열이 되는 경우는 원본 유지).

    접미사를 뗀 결과가 1글자면 지명이 아니라 오탐일 가능성이 높아
    (예: "독도"에서 "도"를 떼면 "독"이 되어버림) 원본을 그대로 둔다.
    """
    stripped = city.strip()
    if stripped in CITY_ALIASES:
        return CITY_ALIASES[stripped]

    for suffix in CITY_ADMIN_SUFFIXES:
        if stripped.endswith(suffix) and len(stripped) - len(suffix) >= 2:
            candidate = stripped[: -len(suffix)]
            return CITY_ALIASES.get(candidate, candidate)

    return stripped


def search_restaurants(client_id, client_secret, city):
    """도시(또는 키워드) 기준으로 맛집을 검색한다.

    반환값: (restaurants, error)
    - 성공(0건 포함): (list, None)
    - 실패(인증/네트워크 등): ([], {"step": ..., "type": ..., "message": ...})

    1차 검색("{도시} 맛집")이 0건이면, 검색어를 넓혀 "{도시} 음식점"으로
    한 번 더 시도한 뒤에도 0건이면 EMPTY_RESULT로 보고한다.
    """
    if not client_id or not client_secret:
        return [], {
            "step": "place_search",
            "type": "AUTH_ERROR",
            "message": "NAVER_CLIENT_ID/NAVER_CLIENT_SECRET이 설정되지 않았습니다.",
        }

    normalized_city = normalize_city(city)
    if normalized_city != city:
        print(f"- 도시명 정규화: \"{city}\" -> \"{normalized_city}\"")

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    restaurants, error = _query(headers, normalized_city, "맛집")
    if error is None or error["type"] != "EMPTY_RESULT":
        return restaurants, error

    print(f'- "{normalized_city} 맛집" 0건, "{normalized_city} {BROADENED_KEYWORD}"로 재검색합니다...')
    broadened_restaurants, broadened_error = _query(headers, normalized_city, BROADENED_KEYWORD)
    if broadened_error is None:
        return broadened_restaurants, None

    return [], {
        "step": "place_search",
        "type": "EMPTY_RESULT",
        "message": f'0 results for "{normalized_city} 맛집" and "{normalized_city} {BROADENED_KEYWORD}" (재검색 포함 2회 시도)',
    }


def _query(headers, city, keyword):
    """단일 검색어로 NAVER 지역 검색 API를 1회 호출한다."""
    params = {
        "query": f"{city} {keyword}",
        "display": NAVER_RESTAURANT_DISPLAY_COUNT,
    }

    try:
        response = requests.get(
            NAVER_LOCAL_SEARCH_URL, headers=headers, params=params, timeout=10
        )
    except requests.RequestException as exc:
        return [], {
            "step": "place_search",
            "type": "NETWORK_ERROR",
            "message": str(exc),
        }

    if response.status_code in (401, 403):
        return [], {
            "step": "place_search",
            "type": "AUTH_ERROR",
            "message": f"HTTP {response.status_code}: {response.text[:200]}",
        }

    if response.status_code != 200:
        return [], {
            "step": "place_search",
            "type": "REQUEST_ERROR",
            "message": f"HTTP {response.status_code}: {response.text[:200]}",
        }

    items = response.json().get("items", [])
    if not items:
        return [], {
            "step": "place_search",
            "type": "EMPTY_RESULT",
            "message": f"0 results for query={city} {keyword}",
        }

    return [_to_restaurant(item) for item in items], None


def _to_restaurant(item):
    return {
        "name": _strip_tags(item.get("title", "")),
        "address": item.get("roadAddress") or item.get("address", ""),
        "category": item.get("category", ""),
        "url": item.get("link", ""),
        "x": item.get("mapx", ""),
        "y": item.get("mapy", ""),
    }


def _strip_tags(text):
    return text.replace("<b>", "").replace("</b>", "")
