import json

import requests
from flask import request

MONITOR_URL = "http://127.0.0.1:5200/api/events"


def record_request(response):
    event = {
        "method": request.method,
        "path": request.path,
        "status_code": response.status_code,
    }
    print(json.dumps(event, ensure_ascii=False), flush=True)
    try:
        result = requests.post(MONITOR_URL, json=event, timeout=0.5)
        result.raise_for_status()
    except requests.RequestException:
        # 감시 서비스 장애가 일반 서비스의 원래 응답을 막지 않도록 한다.
        pass
    return response


def register_request_logging(app):
    app.after_request(record_request)
