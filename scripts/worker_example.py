import time
import requests

API_ENDPOINT = "http://localhost:5000/trigger-alert"
CHECK_URL = "https://example.com"

while True:
    try:
        r = requests.get(CHECK_URL, timeout=5)
        if r.status_code != 200:
            raise Exception("Bad response")
    except Exception as e:
        try:
            requests.post(API_ENDPOINT, json={"error": str(e), "worker": "example"})
        except Exception as post_err:
            print(f"Failed to notify API: {post_err}")
    time.sleep(30)
