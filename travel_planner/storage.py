import json
import os

from travel_planner.data import RESULTS_DIR


def result_paths(date):
    json_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.json")
    md_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.md")
    return json_path, md_path


def load_cached_results(date):
    """같은 date로 이미 저장된 결과가 있으면 (raw_data, report_markdown)을 반환하고,
    없으면 None을 반환한다. API 호출 비용/시간을 아끼기 위한 캐시."""
    json_path, md_path = result_paths(date)
    if not (os.path.exists(json_path) and os.path.exists(md_path)):
        return None

    with open(json_path, encoding="utf-8") as f:
        raw_data = json.load(f)
    with open(md_path, encoding="utf-8") as f:
        report_markdown = f.read()

    return raw_data, report_markdown


def save_results(date, raw_data, report_markdown):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    json_path, md_path = result_paths(date)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    return json_path, md_path
