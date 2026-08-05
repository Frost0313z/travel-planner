import argparse
from datetime import datetime


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="travel_planner",
        description="LLM API와 지도/장소 검색 API로 국내 여행지를 추천하는 CLI 프로그램",
    )
    parser.add_argument(
        "--date",
        required=True,
        help='여행 날짜, "YYYY-MM-DD" 형식 (예: 2026-03-15)',
    )
    args = parser.parse_args(argv)

    if not is_valid_date(args.date):
        parser.error(f'날짜 형식이 올바르지 않습니다: "{args.date}" (예: --date "2026-03-15")')

    return args


def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False
