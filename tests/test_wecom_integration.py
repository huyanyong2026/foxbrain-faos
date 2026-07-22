import hashlib
import io
import os

from services.wecom.app import AuditLog, IdentityMapping, IdentityMappings, WeComClient, WeComIntegration, create_app


def signature(**values):
    return hashlib.sha1("".join(sorted((os.environ["WECHAT_TOKEN"], values["timestamp"], values["nonce"], values.get("echostr", "")))).encode()).hexdigest()


def call(app, method, query, body=b""):
    result = []
    output = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": "/api/wecom/message", "QUERY_STRING": query, "wsgi.input": io.BytesIO(body), "CONTENT_LENGTH": str(len(body))}, lambda status, headers: result.append((status, headers))))
    return int(result[0][0].split()[0]), output


def setup_module():
    os.environ.update({"WECHAT_CORP_ID": "corp", "WECHAT_AGENT_ID": "1001", "WECHAT_SECRET": "secret", "WECHAT_TOKEN": "token", "WECHAT_ENCODING_AES_KEY": "a" * 43})


def test_wecom_token_is_cached_and_refreshable():
    class Cache:
        value = None
        def get(self, key): return self.value
        def setex(self, key, seconds, value): self.value, self.seconds = value, seconds
    class Response:
        def read(self): return b'{"errcode":0,"access_token":"access","expires_in":7200}'
        def __enter__(self): return self
        def __exit__(self, *args): pass
    cache = Cache(); client = WeComClient(cache, opener=lambda *args, **kwargs: Response())
    assert client.access_token() == client.access_token() == "access" and cache.seconds == 6900


def test_message_identity_rbac_routing_and_audit():
    audit = AuditLog(); mapping = IdentityMapping("u1", "fb-1", "store_manager", "nanshan", frozenset({"store:read"}))
    app = create_app(WeComIntegration(IdentityMappings([mapping]), audit=audit))
    values = {"timestamp": "1", "nonce": "n"}; sig = signature(**values)
    body = "<xml><FromUserName>u1</FromUserName><MsgType>text</MsgType><Content>今日销售</Content></xml>".encode()
    status, output = call(app, "POST", f"timestamp=1&nonce=n&msg_signature={sig}", body)
    assert status == 200 and b"store-ai" in output and audit.events[0]["wecom_user"] == "u1" and audit.events[0]["citation"] == "FoxBrain AI Runtime"


def test_rbac_denies_mapping_without_required_permission():
    app = create_app(WeComIntegration(IdentityMappings([IdentityMapping("u2", "fb-2", "ceo", None, frozenset())])))
    sig = signature(timestamp="1", nonce="n")
    body = "<xml><FromUserName>u2</FromUserName><MsgType>text</MsgType><Content>经营</Content></xml>".encode()
    status, _ = call(app, "POST", f"timestamp=1&nonce=n&msg_signature={sig}", body)
    assert status == 403
