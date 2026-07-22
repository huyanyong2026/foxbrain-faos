"""WeCom callback integration with identity/RBAC routing and safe audit records."""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import socket
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import parse_qs
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from wsgiref.simple_server import make_server

from packages.vafox_foundation.http import json_response, service_app

REQUIRED_ENVIRONMENT = ("WECHAT_CORP_ID", "WECHAT_AGENT_ID", "WECHAT_SECRET", "WECHAT_TOKEN", "WECHAT_ENCODING_AES_KEY")
ROLE_AGENT = {"ceo": "huyan-ai", "store_manager": "store-ai", "buyer": "product-procurement-ai", "employee": "sales-ai"}
ROLE_PERMISSIONS = {
    "ceo": frozenset({"enterprise:read"}), "store_manager": frozenset({"store:read"}),
    "buyer": frozenset({"procurement:read"}), "employee": frozenset({"sales:read"}),
}


@dataclass(frozen=True)
class IdentityMapping:
    wecom_userid: str
    foxbrain_user_id: str
    role: str
    store_scope: str | None
    permission_scope: frozenset[str]


class IdentityMappings:
    """Repository seam; production implementations may hydrate this from Identity."""
    def __init__(self, mappings=()): self._mappings = {item.wecom_userid: item for item in mappings}
    def get(self, wecom_userid): return self._mappings.get(wecom_userid)


class RedisTokenCache:
    """Minimal Redis RESP client, retaining token material only in Redis memory."""
    def __init__(self, url=None): self.url = url or os.getenv("REDIS_URL", "redis://redis:6379/0")
    def get(self, key): return self._command("GET", key)
    def setex(self, key, seconds, value): self._command("SETEX", key, str(seconds), value)
    def _command(self, *parts):
        from urllib.parse import urlparse
        parsed = urlparse(self.url); host, port = parsed.hostname or "redis", parsed.port or 6379
        payload = b"*%d\r\n" % len(parts) + b"".join(b"$%d\r\n%s\r\n" % (len(str(part).encode()), str(part).encode()) for part in parts)
        with socket.create_connection((host, port), timeout=2) as connection:
            connection.sendall(payload); response = connection.makefile("rb").readline()
            if response.startswith(b"$"):
                length = int(response[1:-2]); return None if length < 0 else connection.makefile("rb").read(length).decode()
            if response.startswith(b"+"): return response[1:-2].decode()
            raise RuntimeError("redis_cache_unavailable")


class WeComClient:
    token_key = "foxbrain:wecom:access_token"
    def __init__(self, cache, opener=urlopen): self.cache, self.opener = cache, opener
    def access_token(self):
        cached = self.cache.get(self.token_key)
        if cached: return cached
        corp_id, secret = os.environ["WECHAT_CORP_ID"], os.environ["WECHAT_SECRET"]
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}"
        with self.opener(url, timeout=5) as response: payload = json.loads(response.read())
        if payload.get("errcode", 0) != 0 or not payload.get("access_token"): raise RuntimeError("wecom_token_request_failed")
        self.cache.setex(self.token_key, max(60, int(payload.get("expires_in", 7200)) - 300), payload["access_token"])
        return payload["access_token"]
    def send_text(self, wecom_userid, content):
        payload = json.dumps({"touser": wecom_userid, "msgtype": "text", "agentid": int(os.environ["WECHAT_AGENT_ID"]),
                              "text": {"content": content}, "safe": 0}).encode()
        request = Request(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.access_token()}", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
        with self.opener(request, timeout=5) as response: result = json.loads(response.read())
        if result.get("errcode", 0) != 0: raise RuntimeError("wecom_message_send_failed")


class AuditLog:
    def __init__(self): self.events = []
    def record(self, mapping, question, response):
        event = {"audit_id": str(uuid.uuid4()), "timestamp": datetime.now(timezone.utc).isoformat(), "wecom_user": mapping.wecom_userid,
                 "question": question, "role": mapping.role, "ai_response": response["content"], "citation": response["source"]}
        self.events.append(event); return event


class AIRuntime:
    def __init__(self, endpoint=None, opener=urlopen): self.endpoint, self.opener = endpoint or os.getenv("AI_RUNTIME_URL", "http://ai:8080"), opener
    def respond(self, mapping, question, agent):
        request = Request(f"{self.endpoint.rstrip('/')}/api/v1/ai/respond", data=json.dumps({"question": question, "agent": agent,
                          "foxbrain_user_id": mapping.foxbrain_user_id, "store_scope": mapping.store_scope}).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with self.opener(request, timeout=5) as response: payload = json.loads(response.read())
        except (HTTPError, OSError, ValueError) as error: raise RuntimeError("ai_runtime_unavailable") from error
        if not all(payload.get(key) for key in ("title", "content", "source", "confidence")): raise RuntimeError("ai_runtime_invalid_response")
        return payload


def _required_environment(): return [name for name in REQUIRED_ENVIRONMENT if not os.getenv(name)]
def _query(environ): return {key: values[-1] for key, values in parse_qs(environ.get("QUERY_STRING", "")).items()}
def _signature_valid(values, encrypted=""):
    signature = values.get("msg_signature") or values.get("signature")
    if not signature: return False
    source = "".join(sorted((os.environ.get("WECHAT_TOKEN", ""), values.get("timestamp", ""), values.get("nonce", ""), encrypted or values.get("echostr", ""))))
    return hmac.compare_digest(signature, hashlib.sha1(source.encode()).hexdigest())
def _xml_message(raw):
    root = ET.fromstring(raw)
    return root.findtext("FromUserName", "").strip(), root.findtext("Content", "").strip(), root.findtext("MsgType", "").strip()


def _decrypt(encrypted):
    """Decrypt a WeCom AES-CBC callback and bind it to this configured corp."""
    from Crypto.Cipher import AES
    key = base64.b64decode(os.environ["WECHAT_ENCODING_AES_KEY"] + "=")
    padded = AES.new(key, AES.MODE_CBC, key[:16]).decrypt(base64.b64decode(encrypted))
    padding = padded[-1]
    if not 1 <= padding <= 32 or padded[-padding:] != bytes([padding]) * padding: raise ValueError("invalid_wecom_padding")
    plain = padded[:-padding]
    length = int.from_bytes(plain[16:20], "big")
    xml, corp_id = plain[20:20 + length], plain[20 + length:].decode()
    if corp_id != os.environ["WECHAT_CORP_ID"]: raise ValueError("wecom_corp_id_mismatch")
    return xml


class WeComIntegration:
    def __init__(self, mappings=None, client=None, audit=None, runtime=None):
        self.mappings = mappings or IdentityMappings(); self.client = client; self.audit = audit or AuditLog(); self.runtime = runtime
    def response(self, mapping, question):
        agent = ROLE_AGENT[mapping.role]
        response = self.runtime.respond(mapping, question, agent) if self.runtime else {"title": agent, "content": f"{agent}：已收到您的问题“{question}”。请结合实时经营数据进行人工核实。", "source": "FoxBrain AI Runtime", "confidence": "medium"}
        return {**response, "agent": agent}
    def handle_message(self, userid, question):
        mapping = self.mappings.get(userid)
        if not mapping: return 403, {"error": "identity_mapping_not_found"}
        if mapping.role not in ROLE_AGENT or not ROLE_PERMISSIONS[mapping.role].issubset(mapping.permission_scope): return 403, {"error": "rbac_denied"}
        response = self.response(mapping, question)
        if self.client: self.client.send_text(mapping.wecom_userid, response["content"])
        audit = self.audit.record(mapping, question, response)
        return 200, {"reply": response, "identity": {"foxbrain_user_id": mapping.foxbrain_user_id, "role": mapping.role, "store_scope": mapping.store_scope, "permission_scope": sorted(mapping.permission_scope)}, "audit_id": audit["audit_id"]}


def create_app(integration=None):
    integration = integration or WeComIntegration(client=WeComClient(RedisTokenCache()), runtime=AIRuntime())
    def message(environ, start_response):
        missing = _required_environment()
        if missing: return json_response(start_response, 503, {"error": "wecom_not_configured"}), 503
        values = _query(environ)
        if environ["REQUEST_METHOD"] == "GET":
            if not _signature_valid(values): return json_response(start_response, 401, {"error": "invalid_wecom_signature"}), 401
            # Encrypted echo handling is deliberately not logged.
            try: echo = _decrypt(values.get("echostr", ""))
            except (ValueError, KeyError, binascii.Error): return json_response(start_response, 400, {"error": "invalid_wecom_echo"}), 400
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(echo.encode())))])
            return [echo.encode()], 200
        raw = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0))
        try: userid, question, message_type = _xml_message(raw)
        except ET.ParseError: return json_response(start_response, 400, {"error": "invalid_wecom_xml"}), 400
        encrypted = ET.fromstring(raw).findtext("Encrypt", "")
        if not _signature_valid(values, encrypted): return json_response(start_response, 401, {"error": "invalid_wecom_signature"}), 401
        if encrypted:
            try: userid, question, message_type = _xml_message(_decrypt(encrypted))
            except (ValueError, ET.ParseError, binascii.Error): return json_response(start_response, 400, {"error": "invalid_wecom_payload"}), 400
        if message_type != "text" or not userid or not question: return json_response(start_response, 400, {"error": "text_message_required"}), 400
        status, payload = integration.handle_message(userid, question)
        return json_response(start_response, status, payload), status
    return service_app("wecom", {("GET", "/api/wecom/message"): message, ("POST", "/api/wecom/message"): message})


app = create_app()
if __name__ == "__main__": make_server("0.0.0.0", 8080, app).serve_forever()
