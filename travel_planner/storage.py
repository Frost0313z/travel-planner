import json
import os

from travel_planner.data import RESULTS_DIR


def save_results(date, raw_data, report_markdown):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    json_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(RESULTS_DIR, f"{date}_travel_plan.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    return json_path, md_path
