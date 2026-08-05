import requests

from travel_planner.data import (
    CITY_ADMIN_SUFFIXES,
    CITY_ALIASES,
    NAVER_LOCAL_SEARCH_URL,
    NAVER_RESTAURANT_DISPLAY_COUNT,
)


def normalize_city(city):
    """LLM이 반환한 도시명 표기를 검색어로 쓰기 좋은 표준 표기로 정규화한다.

    예: "제주도"/"제주특별자치도" -> "제주", "부산광역시" -> "부산".
    별칭 표에 없으면 행정구역 접미사(시/도/광역시 등)를 떼어낸 결과를 쓰고,
    그마저도 없으면 입력을 그대로 돌려준다(빈 문자열이 되는 경우는 원본 유지).
    """
    stripped = city.strip()
    if stripped in CITY_ALIASES:
        return CITY_ALIASES[stripped]

    for suffix in CITY_ADMIN_SUFFIXES:
        if stripped.endswith(suffix) and len(stripped) > len(suffix):
            candidate = stripped[: -len(suffix)]
            return CITY_ALIASES.get(candidate, candidate)

    return stripped


def search_restaurants(client_id, client_secret, city):
    """도시(또는 키워드) 기준으로 맛집을 검색한다.

    반환값: (restaurants, error)
    - 성공(0건 포함): (list, None)
    - 실패(인증/네트워크 등): ([], {"step": ..., "type": ..., "message": ...})
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
    params = {
        "query": f"{normalized_city} 맛집",
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
            "message": f"0 results for query={normalized_city} 맛집",
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
