import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


def extract(endpoint, page_size=500):
    pages = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params={"page": page, "page_size": page_size},
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()

        pages.append((page, body["data"]))
        print(f"Fetched {endpoint} page {page}/{body['total_pages']} ({len(body['data'])} rows)")

        if page >= body["total_pages"]:
            break
        page += 1

    return pages