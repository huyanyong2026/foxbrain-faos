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
CEO_AGENT = "huyan-ceo-intelligence"
ROLE_AGENT = {"ceo": CEO_AGENT, "store_manager": "store-intelligence", "buyer": "procurement-intelligence", "purchaser": "procurement-intelligence", "employee": "sales-intelligence"}
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
    def __init__(self, mappings=(), ceo_userids=()):
        self._mappings = {item.wecom_userid: item for item in mappings}
        # An identity source may explicitly designate the CEO before its role
        # claims are refreshed.  This must still take the CEO-only route.
        self._ceo_userids = frozenset(ceo_userids) | frozenset(
            item.wecom_userid for item in self._mappings.values() if item.role.lower() == "ceo"
        )
    def get(self, wecom_userid): return self._mappings.get(wecom_userid)
    def is_ceo(self, mapping): return mapping.wecom_userid in self._ceo_userids or mapping.role.lower() == "ceo"


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
    def __init__(self, endpoint=None, opener=urlopen): self.endpoint, self.opener = endpoint or os.getenv("AI_RUNTIME_URL", "http://ai-runtime:8080"), opener
    def query(self, mapping, question, agent, is_ceo_identity=False):
        """Call the FoxBrain Runtime boundary; this adapter never calls Dify."""
        role = "ceo" if is_ceo_identity else mapping.role
        payload = {"user_id": mapping.foxbrain_user_id, "wecom_user_id": mapping.wecom_userid,
                   "role": role, "scope": {"permissions": sorted(mapping.permission_scope), "data_scope": mapping.store_scope}, "query": question}
        request = Request(f"{self.endpoint.rstrip('/')}/api/runtime/wecom/query", data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with self.opener(request, timeout=5) as response: result = json.loads(response.read())
        except (HTTPError, OSError, ValueError) as error: raise RuntimeError("foxbrain_runtime_unavailable") from error
        if not all(key in result for key in ("answer", "sources", "citation", "confidence", "audit_id")):
            raise RuntimeError("foxbrain_runtime_invalid_response")
        return {"title": agent, "content": result["answer"], "source": "FoxBrain Runtime", "confidence": result["confidence"],
                "sources": result["sources"], "citation": result["citation"], "audit_id": result["audit_id"]}
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
        is_ceo_identity = self.mappings.is_ceo(mapping)
        agent = CEO_AGENT if is_ceo_identity else ROLE_AGENT[mapping.role]
        # A CEO message must never be replaced by a generic response when the
        # intelligence runtime is unavailable.
        if is_ceo_identity and not self.runtime:
            raise RuntimeError("ceo_intelligence_unavailable")
        # ``respond`` remains as an injection seam for legacy test doubles only.
        # Production AIRuntime uses the Runtime query contract above.
        if self.runtime and hasattr(self.runtime, "query"):
            response = self.runtime.query(mapping, question, agent, is_ceo_identity)
        elif self.runtime:
            response = self.runtime.respond(mapping, question, agent, is_ceo_identity)
        else:
            response = {"title": agent, "content": f"经营摘要：暂无可验证的经营数据。\n数据依据：未返回业务证据。\n风险：数据缺失。\nAI建议：请先同步数据。\nCitation：FoxBrain Runtime", "source": "FoxBrain AI Runtime", "confidence": "low"}
        # Kept only for downstream clients that still display the former label;
        # routing itself is always the explicit FoxBrain Intelligence route.
        legacy_agent = {"store-intelligence": "store-ai", "procurement-intelligence": "product-procurement-ai", "sales-intelligence": "sales-ai"}.get(agent)
        return {**response, "agent": agent, **({"legacy_agent": legacy_agent} if legacy_agent else {})}
    def handle_message(self, userid, question):
        mapping = self.mappings.get(userid)
        if not mapping: return 403, {"error": "identity_mapping_not_found"}
        is_ceo_identity = self.mappings.is_ceo(mapping)
        required_permissions = ROLE_PERMISSIONS["ceo"] if is_ceo_identity else ROLE_PERMISSIONS.get(mapping.role)
        if not required_permissions or not required_permissions.issubset(mapping.permission_scope): return 403, {"error": "rbac_denied"}
        try:
            response = self.response(mapping, question)
        except RuntimeError as error:
            if is_ceo_identity:
                return 503, {"error": "ceo_intelligence_unavailable"}
            raise error
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
    return service_app("wecom", {
        ("GET", "/api/wecom/message"): message, ("POST", "/api/wecom/message"): message,
        ("GET", "/api/wework/callback"): message, ("POST", "/api/wework/callback"): message,
    })


app = create_app()
if __name__ == "__main__": make_server("0.0.0.0", 8080, app).serve_forever()
