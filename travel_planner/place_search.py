import requests

from travel_planner.data import NAVER_LOCAL_SEARCH_URL, NAVER_RESTAURANT_DISPLAY_COUNT


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

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    params = {
        "query": f"{city} 맛집",
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
            "message": f"0 results for query={city} 맛집",
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
