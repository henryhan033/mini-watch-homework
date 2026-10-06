from flask import Flask, request
from db import connect_db

app = Flask(__name__)
app.json.ensure_ascii = False


def classify_event(event):
    path = event["path"]
    status_code = event["status_code"]

    if path == "/auth/login":
        if status_code == 401:
            return "login_failure"
        if status_code == 200:
            return "login_success"

    return "http_request"


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.post("/api/events")
def create_event():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "이벤트를 JSON으로 보내 주세요."}, 400

    method = data.get("method")
    path = data.get("path")
    status_code = data.get("status_code")

    if not isinstance(method, str) or not method.strip():
        return {"error": "method가 필요합니다."}, 400
    if not isinstance(path, str) or not path.strip():
        return {"error": "path가 필요합니다."}, 400
    if not isinstance(status_code, int):
        return {"error": "status_code는 정수여야 합니다."}, 400

    event = {
        "method": method.strip(),
        "path": path.strip(),
        "status_code": status_code,
    }
    event_type = classify_event(event)

    with connect_db() as conn:
        row = conn.execute(
            """
            INSERT INTO http_events (method, path, status_code, event_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id, occurred_at, method, path, status_code, event_type
            """,
            (
                event["method"],
                event["path"],
                event["status_code"],
                event_type,
            ),
        ).fetchone()

    return row, 201


@app.get("/api/events")
def list_events():
    event_type = request.args.get("event_type")

    with connect_db() as conn:
        if event_type:
            rows = conn.execute(
                """
                SELECT id, occurred_at, method, path, status_code, event_type
                FROM http_events
                WHERE event_type = %s
                ORDER BY id DESC
                LIMIT 50
                """,
                (event_type,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, occurred_at, method, path, status_code, event_type
                FROM http_events
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()

    return rows, 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5200)
