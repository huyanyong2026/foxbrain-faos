import json
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app


def respond(environ, start_response):
    try: request = json.loads(environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)) or b"{}")
    except json.JSONDecodeError: return json_response(start_response, 400, {"error": "invalid_json"}), 400
    question, agent = str(request.get("question", "")).strip(), str(request.get("agent", "")).strip()
    if not question or not agent: return json_response(start_response, 400, {"error": "question_and_agent_required"}), 400
    return json_response(start_response, 200, {"title": agent, "content": f"{agent}：已收到您的问题“{question}”。请结合实时经营数据进行人工核实。", "source": "FoxBrain AI Runtime", "confidence": "medium"}), 200

app = service_app("ai", {("POST", "/api/v1/ai/respond"): respond})
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
