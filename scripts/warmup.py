"""Warm-up : charge bge-m3 dans le serveur + verifie un tour de chat."""
import json
import urllib.request

BASE = "http://localhost:8000"


def call(method, path, body=None, timeout=420):
    req = urllib.request.Request(
        BASE + path, method=method,
        headers={"Content-Type": "application/json"},
        data=json.dumps(body).encode() if body else None,
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


s = call("POST", "/api/students", {"display_name": "Warmup"})
d = call("POST", "/api/chat", {
    "student_id": s["id"], "message": "c est quoi une boucle ?",
    "code": "", "language": "python",
})
print("verdict:", d["reply"]["verdict"], "| answer:", len(d["reply"].get("answer", "")), "chars")
call("DELETE", f"/api/students/{s['id']}")
print("WARMUP_OK")
