import os
import sys

from dotenv import load_dotenv


class ApiKeys:
    def __init__(self, openai_key, naver_client_id, naver_client_secret):
        self.openai_key = openai_key
        self.naver_client_id = naver_client_id
        self.naver_client_secret = naver_client_secret

    @property
    def naver_configured(self):
        return bool(self.naver_client_id and self.naver_client_secret)


def load_api_keys():
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("[오류] OPENAI_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
        print(
            "  프로젝트 루트에 .env 파일을 만들고 아래 줄을 추가하세요:\n"
            "  OPENAI_API_KEY=your-openai-api-key",
            file=sys.stderr,
        )
        sys.exit(1)

    return ApiKeys(
        openai_key=openai_key,
        naver_client_id=os.getenv("NAVER_CLIENT_ID"),
        naver_client_secret=os.getenv("NAVER_CLIENT_SECRET"),
    )
