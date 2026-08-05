import json
import os
from datetime import datetime

from travel_planner.data import RESULTS_DIR

ERROR_LOG_PATH = os.path.join(RESULTS_DIR, "errors_log.jsonl")


def result_paths(date):
    json_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.json")
    md_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.md")
    return json_path, md_path


def append_error_log(date, errors):
    """실행마다 발생한 errors를 results/errors_log.jsonl에 한 줄씩 누적한다.

    개별 실행의 errors는 그 실행의 결과 JSON에만 남기 때문에,
    여러 번 실행한 이력을 모아 보려면 이 로그 파일 하나만 읽으면 된다.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    entry = {
        "run_date": date,
        "executed_at": datetime.now().isoformat(timespec="seconds"),
        "errors": errors,
    }
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


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
