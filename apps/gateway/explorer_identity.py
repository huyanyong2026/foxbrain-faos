"""Privacy-first Explorer identity service for gateway.vafox.com."""

from __future__ import annotations

import hashlib
import hmac
import html
import json
import os
import secrets
import sqlite3
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from foxbrain_os.enterprise_data_service import EnterpriseDataClient


INTERESTS = ("徒步", "登山", "越野跑", "露营", "摄影", "旅行")
JOURNEY_TYPES = {"activity": "活动", "route": "路线", "travel": "旅行", "story": "故事", "community": "社群"}
CONSENT_VERSION = "explorer-privacy-v1"
SESSION_TTL = 30 * 24 * 60 * 60


def now():
    return int(time.time())


def normalize_phone(value):
    digits = "".join(character for character in str(value or "") if character.isdigit())
    if digits.startswith("86") and len(digits) == 13:
        digits = digits[2:]
    if len(digits) != 11 or not digits.startswith("1"):
        raise ValueError("请输入正确的中国大陆手机号")
    return digits


class ExplorerStore:
    def __init__(self, path, secret):
        self.path = str(path)
        self.secret = str(secret or "").encode("utf-8")
        if len(self.secret) < 32:
            raise ValueError("EXPLORER_IDENTITY_SECRET must contain at least 32 characters")
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("pragma journal_mode=wal")
        connection.execute("pragma foreign_keys=on")
        connection.execute("pragma busy_timeout=15000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def digest(self, purpose, value):
        return hmac.new(self.secret, (purpose + ":" + str(value)).encode("utf-8"), hashlib.sha256).hexdigest()

    def ensure_schema(self):
        statements = (
            """create table if not exists explorer_identities(
            id integer primary key autoincrement,explorer_id text not null unique,
            openid_hash text not null unique,mobile_hash text unique,mobile_last4 text not null default '',
            display_name text not null default '',city text not null default '',consent_version text not null,
            status text not null default 'active',registered_at integer not null,first_purchase_at text,
            last_activity_at integer,active_status text not null default 'new',updated_at integer not null)""",
            """create table if not exists explorer_interest_tags(
            explorer_id text not null,tag text not null,source text not null default 'self_selected',
            created_at integer not null,primary key(explorer_id,tag),
            foreign key(explorer_id) references explorer_identities(explorer_id) on delete cascade)""",
            """create table if not exists explorer_purchase_links(
            id integer primary key autoincrement,explorer_id text not null,core_customer_id text not null,
            purchase_key text not null,sku text not null default '',product_name text not null default '',
            brand_name text not null default '',purchase_date text,quantity real not null default 0,
            amount real not null default 0,source_json text not null,matched_at integer not null,
            unique(explorer_id,purchase_key),
            foreign key(explorer_id) references explorer_identities(explorer_id) on delete cascade)""",
            """create table if not exists explorer_journey_events(
            id integer primary key autoincrement,event_id text not null unique,explorer_id text not null,
            event_type text not null,title text not null,summary text not null default '',occurred_at text,
            visibility text not null default 'private',source text not null default 'self',created_at integer not null,
            foreign key(explorer_id) references explorer_identities(explorer_id) on delete cascade)""",
            """create table if not exists explorer_oauth_states(
            id integer primary key autoincrement,state_hash text not null unique,consent_version text not null,
            interests_json text not null default '[]',status text not null default 'pending',
            created_at integer not null,expires_at integer not null,consumed_at integer)""",
            """create table if not exists explorer_sessions(
            id integer primary key autoincrement,token_hash text not null unique,explorer_id text not null,
            created_at integer not null,expires_at integer not null,revoked_at integer,
            foreign key(explorer_id) references explorer_identities(explorer_id) on delete cascade)""",
            """create table if not exists explorer_audit_logs(
            id integer primary key autoincrement,explorer_id text,event_type text not null,
            result text not null,detail_json text not null default '{}',ip_hash text,user_agent_hash text,
            occurred_at integer not null)""",
            "create index if not exists idx_explorer_purchase_owner on explorer_purchase_links(explorer_id,purchase_date)",
            "create index if not exists idx_explorer_journey_owner on explorer_journey_events(explorer_id,occurred_at)",
            "create index if not exists idx_explorer_audit_owner on explorer_audit_logs(explorer_id,occurred_at)",
        )
        with self.connect() as connection:
            for statement in statements:
                connection.execute(statement)

    def audit(self, explorer_id, event_type, result, detail=None, ip="", user_agent=""):
        with self.connect() as connection:
            connection.execute(
                """insert into explorer_audit_logs(
                explorer_id,event_type,result,detail_json,ip_hash,user_agent_hash,occurred_at)
                values(?,?,?,?,?,?,?)""",
                (explorer_id or None, event_type, result, json.dumps(detail or {}, ensure_ascii=False),
                 self.digest("ip", ip) if ip else None,
                 self.digest("user-agent", user_agent) if user_agent else None, now()),
            )

    def create_oauth_state(self, interests):
        selected = [item for item in interests if item in INTERESTS]
        raw = secrets.token_urlsafe(32)
        with self.connect() as connection:
            connection.execute(
                """insert into explorer_oauth_states(
                state_hash,consent_version,interests_json,created_at,expires_at)
                values(?,?,?,?,?)""",
                (self.digest("oauth-state", raw), CONSENT_VERSION,
                 json.dumps(selected, ensure_ascii=False), now(), now() + 600),
            )
        return raw

    def consume_oauth_state(self, raw):
        state_hash = self.digest("oauth-state", raw)
        with self.connect() as connection:
            row = connection.execute(
                "select * from explorer_oauth_states where state_hash=?", (state_hash,)
            ).fetchone()
            if not row or row["status"] != "pending" or int(row["expires_at"]) < now():
                raise ValueError("登记请求已失效，请重新扫码")
            connection.execute(
                "update explorer_oauth_states set status='consumed',consumed_at=? where id=? and status='pending'",
                (now(), row["id"]),
            )
            return {"consent_version": row["consent_version"], "interests": json.loads(row["interests_json"])}

    def create_or_get(self, openid, display_name, city, consent_version, interests):
        openid_hash = self.digest("wechat-openid", openid)
        timestamp = now()
        with self.connect() as connection:
            row = connection.execute(
                "select * from explorer_identities where openid_hash=?", (openid_hash,)
            ).fetchone()
            created = row is None
            if created:
                explorer_id = "EXP-" + secrets.token_hex(8).upper()
                connection.execute(
                    """insert into explorer_identities(
                    explorer_id,openid_hash,display_name,city,consent_version,registered_at,updated_at)
                    values(?,?,?,?,?,?,?)""",
                    (explorer_id, openid_hash, str(display_name or "探索者")[:80],
                     str(city or "")[:80], consent_version, timestamp, timestamp),
                )
            else:
                explorer_id = row["explorer_id"]
                connection.execute(
                    """update explorer_identities set display_name=?,city=?,consent_version=?,
                    last_activity_at=?,active_status='active',updated_at=? where explorer_id=?""",
                    (str(display_name or row["display_name"])[:80], str(city or row["city"])[:80],
                     consent_version, timestamp, timestamp, explorer_id),
                )
            for tag in interests:
                if tag in INTERESTS:
                    connection.execute(
                        "insert or ignore into explorer_interest_tags(explorer_id,tag,created_at) values(?,?,?)",
                        (explorer_id, tag, timestamp),
                    )
        return explorer_id, created

    def create_session(self, explorer_id):
        raw = secrets.token_urlsafe(32)
        with self.connect() as connection:
            connection.execute(
                "insert into explorer_sessions(token_hash,explorer_id,created_at,expires_at) values(?,?,?,?)",
                (self.digest("session", raw), explorer_id, now(), now() + SESSION_TTL),
            )
        return raw

    def session_identity(self, raw):
        if not raw:
            return None
        with self.connect() as connection:
            row = connection.execute(
                """select i.* from explorer_sessions s join explorer_identities i on i.explorer_id=s.explorer_id
                where s.token_hash=? and s.revoked_at is null and s.expires_at>=? and i.status='active'""",
                (self.digest("session", raw), now()),
            ).fetchone()
            return dict(row) if row else None

    def revoke_session(self, raw):
        if not raw:
            return
        with self.connect() as connection:
            connection.execute(
                "update explorer_sessions set revoked_at=? where token_hash=? and revoked_at is null",
                (now(), self.digest("session", raw)),
            )

    def profile(self, explorer_id):
        with self.connect() as connection:
            row = connection.execute(
                """select explorer_id,display_name,city,mobile_last4,status,registered_at,
                first_purchase_at,last_activity_at,active_status,updated_at
                from explorer_identities where explorer_id=?""", (explorer_id,)
            ).fetchone()
            if not row:
                return None
            result = dict(row)
            result["interests"] = [item[0] for item in connection.execute(
                "select tag from explorer_interest_tags where explorer_id=? order by tag", (explorer_id,)
            ).fetchall()]
            result["equipment_count"] = connection.execute(
                "select count(*) from explorer_purchase_links where explorer_id=?", (explorer_id,)
            ).fetchone()[0]
            result["journey_count"] = connection.execute(
                "select count(*) from explorer_journey_events where explorer_id=?", (explorer_id,)
            ).fetchone()[0]
            return result

    def update_profile(self, explorer_id, display_name, city, interests):
        selected = sorted({item for item in interests if item in INTERESTS})
        timestamp = now()
        with self.connect() as connection:
            connection.execute(
                "update explorer_identities set display_name=?,city=?,last_activity_at=?,updated_at=? where explorer_id=?",
                (str(display_name or "探索者")[:80], str(city or "")[:80], timestamp, timestamp, explorer_id),
            )
            connection.execute("delete from explorer_interest_tags where explorer_id=?", (explorer_id,))
            connection.executemany(
                "insert into explorer_interest_tags(explorer_id,tag,created_at) values(?,?,?)",
                [(explorer_id, tag, timestamp) for tag in selected],
            )

    def bind_verified_phone(self, explorer_id, phone):
        normalized = normalize_phone(phone)
        mobile_hash = self.digest("mobile", normalized)
        with self.connect() as connection:
            owner = connection.execute(
                "select explorer_id from explorer_identities where mobile_hash=?", (mobile_hash,)
            ).fetchone()
            if owner and owner["explorer_id"] != explorer_id:
                raise ValueError("该手机号已经绑定其他探索者")
            connection.execute(
                "update explorer_identities set mobile_hash=?,mobile_last4=?,updated_at=? where explorer_id=?",
                (mobile_hash, normalized[-4:], now(), explorer_id),
            )
        return normalized

    def replace_purchases(self, explorer_id, customer_id, purchases, source):
        timestamp = now()
        with self.connect() as connection:
            connection.execute("delete from explorer_purchase_links where explorer_id=?", (explorer_id,))
            for index, item in enumerate(purchases):
                purchase_key = str(item.get("purchase_key") or "{}:{}:{}".format(
                    item.get("purchase_date", ""), item.get("sku", ""), index
                ))
                connection.execute(
                    """insert into explorer_purchase_links(
                    explorer_id,core_customer_id,purchase_key,sku,product_name,brand_name,purchase_date,
                    quantity,amount,source_json,matched_at) values(?,?,?,?,?,?,?,?,?,?,?)""",
                    (explorer_id, str(customer_id), purchase_key, str(item.get("sku") or "")[:100],
                     str(item.get("product_name") or "")[:240], str(item.get("brand_name") or "")[:120],
                     str(item.get("purchase_date") or "")[:30], float(item.get("quantity") or 0),
                     float(item.get("amount") or 0), json.dumps(source, ensure_ascii=False), timestamp),
                )
            first = connection.execute(
                "select min(purchase_date) from explorer_purchase_links where explorer_id=? and purchase_date!=''",
                (explorer_id,),
            ).fetchone()[0]
            connection.execute(
                "update explorer_identities set first_purchase_at=?,updated_at=? where explorer_id=?",
                (first, timestamp, explorer_id),
            )

    def equipment(self, explorer_id):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(
                """select purchase_key,sku,product_name,brand_name,purchase_date,quantity,amount,matched_at
                from explorer_purchase_links where explorer_id=? order by purchase_date desc,id desc""",
                (explorer_id,),
            ).fetchall()]

    def add_journey(self, explorer_id, event_type, title, summary, occurred_at):
        if event_type not in JOURNEY_TYPES:
            raise ValueError("请选择正确的探索记录类型")
        if not str(title or "").strip():
            raise ValueError("请填写记录标题")
        event_id = "JOURNEY-" + secrets.token_hex(8).upper()
        with self.connect() as connection:
            connection.execute(
                """insert into explorer_journey_events(
                event_id,explorer_id,event_type,title,summary,occurred_at,created_at)
                values(?,?,?,?,?,?,?)""",
                (event_id, explorer_id, event_type, str(title).strip()[:160],
                 str(summary or "").strip()[:2000], str(occurred_at or "")[:30], now()),
            )
            connection.execute(
                "update explorer_identities set last_activity_at=?,active_status='active',updated_at=? where explorer_id=?",
                (now(), now(), explorer_id),
            )
        return event_id

    def journey(self, explorer_id):
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(
                """select event_id,event_type,title,summary,occurred_at,visibility,created_at
                from explorer_journey_events where explorer_id=? order by coalesce(occurred_at,'') desc,id desc""",
                (explorer_id,),
            ).fetchall()]


class WeChatOAuth:
    def __init__(self, app_id, app_secret, redirect_uri):
        self.app_id = str(app_id or "")
        self.app_secret = str(app_secret or "")
        self.redirect_uri = str(redirect_uri or "")

    @property
    def configured(self):
        return bool(self.app_id and self.app_secret and self.redirect_uri.startswith("https://gateway.vafox.com/"))

    def authorization_url(self, state):
        if not self.configured:
            raise ValueError("微信登记尚未开放，请等待公众号授权配置完成")
        params = urllib.parse.urlencode({
            "appid": self.app_id, "redirect_uri": self.redirect_uri, "response_type": "code",
            "scope": "snsapi_userinfo", "state": state,
        })
        return "https://open.weixin.qq.com/connect/oauth2/authorize?{}#wechat_redirect".format(params)

    def _json(self, url):
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "FireFox-Explorer/1.0"})
        with urllib.request.urlopen(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

    def exchange(self, code):
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token?" + urllib.parse.urlencode({
            "appid": self.app_id, "secret": self.app_secret, "code": code,
            "grant_type": "authorization_code",
        })
        token = self._json(token_url)
        if not token.get("openid") or not token.get("access_token"):
            raise ValueError("微信授权没有返回有效身份")
        profile_url = "https://api.weixin.qq.com/sns/userinfo?" + urllib.parse.urlencode({
            "access_token": token["access_token"], "openid": token["openid"], "lang": "zh_CN",
        })
        profile = self._json(profile_url)
        return {
            "openid": token["openid"], "display_name": profile.get("nickname") or "探索者",
            "city": profile.get("city") or profile.get("province") or "",
        }


class SignedPhoneVerifier:
    def __init__(self, secret):
        self.secret = str(secret or "").encode("utf-8")

    @property
    def configured(self):
        return len(self.secret) >= 32

    def verify(self, phone, token):
        if not self.configured:
            raise ValueError("手机号验证服务尚未接入")
        normalized = normalize_phone(phone)
        try:
            expires_text, signature = str(token or "").split(".", 1)
            expires = int(expires_text)
        except (TypeError, ValueError):
            raise ValueError("手机号验证凭证无效")
        expected = hmac.new(self.secret, (normalized + ":" + expires_text).encode("utf-8"), hashlib.sha256).hexdigest()
        if expires < now() or not hmac.compare_digest(expected, signature):
            raise ValueError("手机号验证凭证已失效")
        return normalized


class CorePurchaseMatcher:
    def __init__(self, client):
        self.client = client

    def match(self, phone):
        normalized = normalize_phone(phone)
        result = self.client.explorer_customer_match(normalized, limit=500)
        if not result.get("ok"):
            raise ValueError("企业数据暂时不可用，请稍后重试")
        payload = result.get("data") or {}
        return payload.get("customer"), payload.get("items") or [], {
            "system": "core.vafox.com", "mode": "read_only",
            "data_as_of": payload.get("data_as_of"),
        }


def page(title, body):
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#17251e"><title>{title}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f3f5f1;color:#17211b;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}}
a{{color:inherit}}header{{height:64px;padding:0 max(20px,5vw);display:flex;align-items:center;justify-content:space-between;background:#17251e;color:white}}
header a{{text-decoration:none;font-weight:700}}main{{width:min(920px,calc(100% - 32px));margin:auto;padding:44px 0 80px}}h1{{font-size:clamp(36px,7vw,68px);line-height:1.05;margin:8px 0 20px}}h2{{font-size:22px;margin:0 0 16px}}p{{line-height:1.7}}.lead{{font-size:19px;color:#536158;max-width:680px}}
.panel{{padding:24px 0;border-top:1px solid #c9d0ca}}.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}}.item{{padding:18px;background:white;border:1px solid #d8ded9;border-radius:6px}}.item strong{{display:block;font-size:18px}}.muted{{color:#69766e}}.status{{display:inline-block;color:#a13428;font-size:13px;font-weight:700}}
label{{display:block;margin:16px 0 7px;font-weight:700}}input,textarea{{width:100%;padding:13px;border:1px solid #aeb8b0;border-radius:4px;font:inherit}}.choices{{display:flex;flex-wrap:wrap;gap:9px}}.choices label{{margin:0;padding:10px 12px;background:white;border:1px solid #c9d0ca;border-radius:4px;font-weight:500}}
button,.button{{display:inline-flex;align-items:center;justify-content:center;min-height:46px;margin-top:18px;padding:10px 18px;border:1px solid #17251e;border-radius:4px;background:#17251e;color:white;text-decoration:none;font-weight:700;cursor:pointer}}.button.secondary{{background:transparent;color:#17251e}}.notice{{padding:16px;border-left:3px solid #b34535;background:#fff}}footer{{padding:28px;text-align:center;background:#0d1510;color:#aeb8b0}}
@media(max-width:640px){{main{{padding-top:28px}}.grid{{grid-template-columns:1fr}}h1{{font-size:42px}}}}
</style></head><body><header><a href="/">FireFox Outdoor</a><a href="/explorer">我的探索人生</a></header><main>{body}</main><footer>润物细无声。</footer></body></html>""".format(title=html.escape(title), body=body)


class ExplorerHandler(BaseHTTPRequestHandler):
    server_version = "FireFoxExplorer/1.0"

    def log_message(self, fmt, *args):
        return

    def _headers(self, status, content_type, length=0, cookie="", location=""):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if length:
            self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        if location:
            self.send_header("Location", location)
        self.end_headers()

    def html(self, status, value, cookie=""):
        body = value.encode("utf-8")
        self._headers(status, "text/html; charset=utf-8", len(body), cookie)
        self.wfile.write(body)

    def json(self, status, value):
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def redirect(self, location, cookie=""):
        self._headers(302, "text/plain; charset=utf-8", cookie=cookie, location=location)

    def form(self):
        size = int(self.headers.get("Content-Length", "0") or 0)
        if size > 65536:
            raise ValueError("提交内容过大")
        return urllib.parse.parse_qs(self.rfile.read(size).decode("utf-8"), keep_blank_values=True)

    def session_token(self):
        jar = cookies.SimpleCookie(self.headers.get("Cookie", ""))
        value = jar.get("explorer_session")
        return value.value if value else ""

    def identity(self):
        return self.server.store.session_identity(self.session_token())

    def same_origin(self):
        source = self.headers.get("Origin") or self.headers.get("Referer") or ""
        host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or ""
        parsed = urllib.parse.urlparse(source)
        return bool(source and parsed.netloc.lower() == host.split(",", 1)[0].strip().lower())

    def client_ip(self):
        return (self.headers.get("X-Forwarded-For") or self.client_address[0]).split(",", 1)[0].strip()

    def register_page(self, message=""):
        choices = "".join('<label><input type="checkbox" name="interest" value="{}"> {}</label>'.format(item, item) for item in INTERESTS)
        warning = '<div class="notice">{}</div>'.format(html.escape(message)) if message else ""
        configured = self.server.oauth.configured
        button = '<button type="submit">微信授权并创建身份</button>' if configured else '<div class="notice">微信登记入口已经建好，完成公众号网页授权配置后即可开放。</div>'
        body = """<span class="status">FireFox Explorer</span><h1>从一次购买，<br>开始一段长期同行。</h1>
<p class="lead">Explorer 不是普通会员。它把你的装备、探索、活动和故事连接起来，形成只属于你的探索人生。</p>{warning}
<section class="panel"><h2>微信扫码登记</h2><form method="post" action="/explorer/auth/wechat/start">
<p>微信授权只用于建立唯一身份。手机号需要单独验证后，才会匹配历史购买记录。</p><label>我感兴趣的方向</label><div class="choices">{choices}</div>
<label><input type="checkbox" name="consent" value="1" required> 我已阅读并同意隐私说明，授权火狐狸建立 Explorer 身份</label>{button}</form>
<p><a href="/explorer/privacy">查看隐私说明</a></p></section>""".format(warning=warning, choices=choices, button=button)
        self.html(200, page("Explorer 登记", body))

    def home_page(self, identity):
        profile = self.server.store.profile(identity["explorer_id"])
        equipment = self.server.store.equipment(identity["explorer_id"])
        journey = self.server.store.journey(identity["explorer_id"])
        equipment_html = "".join(
            '<div class="item"><strong>{}</strong><span>{}</span><p>{} · 数量 {}</p></div>'.format(
                html.escape(item["product_name"] or item["sku"]), html.escape(item["brand_name"] or "品牌待补充"),
                html.escape(item["purchase_date"] or "购买时间待补充"), item["quantity"])
            for item in equipment[:20]
        ) or '<div class="notice">还没有匹配到装备。完成手机号验证后，系统才会从 Core 只读匹配自己的历史购买。</div>'
        journey_html = "".join(
            '<div class="item"><strong>{}</strong><span>{}</span><p>{}</p></div>'.format(
                html.escape(item["title"]), JOURNEY_TYPES.get(item["event_type"], "探索"),
                html.escape(item["summary"] or item["occurred_at"] or "已记录"))
            for item in journey[:12]
        ) or '<div class="notice">还没有探索记录。可以从一次徒步、一次露营或一段旅行开始。</div>'
        interest_text = "、".join(profile["interests"]) or "尚未选择"
        phone_text = "已验证 · 尾号 " + profile["mobile_last4"] if profile["mobile_last4"] else "尚未验证"
        body = """<span class="status">{explorer_id}</span><h1>我的探索人生</h1><p class="lead">{name}，这里记录装备，也记录每一次走向户外后的成长。</p>
<section class="panel"><div class="grid"><div><h2>我的身份</h2><p>城市：{city}<br>兴趣：{interests}<br>手机号：{phone}</p></div><div><h2>Explorer Value</h2><p>价值体系正在准备。未来会记录长期参与、分享与社群贡献，而不是简单返佣。</p></div></div></section>
<section class="panel"><h2>我的装备</h2><div class="grid">{equipment}</div></section>
<section class="panel"><h2>我的探索</h2><div class="grid">{journey}</div><form method="post" action="/api/explorer/journey"><label>记录类型</label><div class="choices">{journey_choices}</div><label>标题</label><input name="title" required maxlength="160"><label>日期</label><input name="occurred_at" type="date"><label>体验与收获</label><textarea name="summary" rows="4" maxlength="2000"></textarea><button>保存为私人记录</button></form></section>
<section class="panel"><div class="grid"><div><h2>我的社群</h2><p>活动群与 Dream Community 尚未接入。没有你的明确选择，不会自动加入任何群。</p></div><div><h2>我的故事</h2><p>照片分享将在权限和内容审核机制完成后开放。</p></div></div></section>
<form method="post" action="/explorer/logout"><button class="button secondary">退出当前身份</button></form>""".format(
            explorer_id=html.escape(profile["explorer_id"]), name=html.escape(profile["display_name"]),
            city=html.escape(profile["city"] or "待补充"), interests=html.escape(interest_text), phone=phone_text,
            equipment=equipment_html, journey=journey_html,
            journey_choices="".join('<label><input type="radio" name="event_type" value="{}"{}> {}</label>'.format(key, " required" if index == 0 else "", label) for index, (key, label) in enumerate(JOURNEY_TYPES.items())),
        )
        self.html(200, page("我的探索人生", body))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/healthz":
            if self.client_address[0] not in {"127.0.0.1", "::1"}:
                return self.json(404, {"error": "not_found"})
            return self.json(200, {"status": "ok", "service": "explorer_identity", "sap_access": "none"})
        if parsed.path in {"/explorer", "/explorer/"}:
            identity = self.identity()
            return self.home_page(identity) if identity else self.redirect("/explorer/register")
        if parsed.path == "/explorer/register":
            return self.register_page()
        if parsed.path == "/explorer/privacy":
            return self.html(200, page("Explorer 隐私说明", """<h1>你的身份，只服务于你的探索人生。</h1><section class="panel"><p>我们只在你明确授权后建立身份。OpenID 和手机号以不可逆摘要保存；购买记录只从 core.vafox.com 只读匹配，不连接或修改 SAP。</p><p>你只能看到自己的数据。未经授权，不会用于营销、社群邀请或对外分享。</p><a class="button secondary" href="/explorer/register">返回登记</a></section>"""))
        if parsed.path == "/explorer/auth/wechat/callback":
            query = urllib.parse.parse_qs(parsed.query)
            try:
                state = self.server.store.consume_oauth_state((query.get("state") or [""])[0])
                profile = self.server.oauth.exchange((query.get("code") or [""])[0])
                explorer_id, created = self.server.store.create_or_get(
                    profile["openid"], profile.get("display_name"), profile.get("city"),
                    state["consent_version"], state["interests"],
                )
                token = self.server.store.create_session(explorer_id)
                self.server.store.audit(explorer_id, "wechat_identity", "created" if created else "login", {}, self.client_ip(), self.headers.get("User-Agent", ""))
                return self.redirect("/explorer", "explorer_session={}; Path=/; Max-Age={}; HttpOnly; Secure; SameSite=Lax".format(token, SESSION_TTL))
            except ValueError as exc:
                return self.html(400, page("微信登记", '<div class="notice">{}</div><a class="button secondary" href="/explorer/register">重新登记</a>'.format(html.escape(str(exc)))))
        identity = self.identity()
        if parsed.path.startswith("/api/explorer/"):
            if not identity:
                return self.json(401, {"ok": False, "message": "请先完成 Explorer 登记"})
            if parsed.path == "/api/explorer/me":
                return self.json(200, {"ok": True, "profile": self.server.store.profile(identity["explorer_id"])})
            if parsed.path == "/api/explorer/equipment":
                return self.json(200, {"ok": True, "items": self.server.store.equipment(identity["explorer_id"]), "source": "core.vafox.com read-only"})
            if parsed.path == "/api/explorer/journey":
                return self.json(200, {"ok": True, "items": self.server.store.journey(identity["explorer_id"])})
        return self.json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if not self.same_origin():
            return self.json(403, {"ok": False, "message": "请求来源无法验证"})
        try:
            form = self.form()
            if parsed.path == "/explorer/auth/wechat/start":
                if (form.get("consent") or [""])[0] != "1":
                    raise ValueError("请先阅读并同意隐私说明")
                state = self.server.store.create_oauth_state(form.get("interest") or [])
                return self.redirect(self.server.oauth.authorization_url(state))
            identity = self.identity()
            if not identity:
                return self.json(401, {"ok": False, "message": "请先完成 Explorer 登记"})
            explorer_id = identity["explorer_id"]
            if parsed.path == "/explorer/logout":
                self.server.store.revoke_session(self.session_token())
                self.server.store.audit(explorer_id, "logout", "success", {}, self.client_ip(), self.headers.get("User-Agent", ""))
                return self.redirect("/explorer/register", "explorer_session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax")
            if parsed.path == "/api/explorer/profile":
                self.server.store.update_profile(
                    explorer_id, (form.get("display_name") or [""])[0], (form.get("city") or [""])[0], form.get("interest") or []
                )
                self.server.store.audit(explorer_id, "profile_update", "success", {}, self.client_ip(), self.headers.get("User-Agent", ""))
                return self.json(200, {"ok": True, "profile": self.server.store.profile(explorer_id)})
            if parsed.path == "/api/explorer/phone/verify":
                phone = self.server.phone_verifier.verify(
                    (form.get("phone") or [""])[0], (form.get("verification_token") or [""])[0]
                )
                self.server.store.bind_verified_phone(explorer_id, phone)
                customer, purchases, source = self.server.matcher.match(phone)
                if customer:
                    self.server.store.replace_purchases(explorer_id, customer["id"], purchases, source)
                self.server.store.audit(explorer_id, "phone_verified_and_purchase_match", "matched" if customer else "no_match", {"purchase_count": len(purchases)}, self.client_ip(), self.headers.get("User-Agent", ""))
                return self.json(200, {"ok": True, "matched": bool(customer), "equipment_count": len(purchases)})
            if parsed.path == "/api/explorer/journey":
                event_id = self.server.store.add_journey(
                    explorer_id, (form.get("event_type") or [""])[0], (form.get("title") or [""])[0],
                    (form.get("summary") or [""])[0], (form.get("occurred_at") or [""])[0],
                )
                self.server.store.audit(explorer_id, "journey_created", "success", {"event_id": event_id}, self.client_ip(), self.headers.get("User-Agent", ""))
                return self.redirect("/explorer")
            return self.json(404, {"error": "not_found"})
        except ValueError as exc:
            if parsed.path == "/explorer/auth/wechat/start":
                return self.register_page(str(exc))
            return self.json(400, {"ok": False, "message": str(exc)})

    def _read_only(self):
        self.json(405, {"error": "method_not_allowed"})

    do_PUT = _read_only
    do_PATCH = _read_only
    do_DELETE = _read_only


def create_server(host=None, port=None, store=None, oauth=None, phone_verifier=None, matcher=None):
    secret = os.environ.get("EXPLORER_IDENTITY_SECRET", "")
    server = ThreadingHTTPServer(
        (host or os.environ.get("EXPLORER_HOST", "127.0.0.1"), int(port or os.environ.get("EXPLORER_PORT", "8092"))),
        ExplorerHandler,
    )
    server.store = store or ExplorerStore(
        os.environ.get("EXPLORER_DB", "/opt/firefox-explorer/explorer.db"), secret
    )
    server.oauth = oauth or WeChatOAuth(
        os.environ.get("WECHAT_APP_ID", ""), os.environ.get("WECHAT_APP_SECRET", ""),
        os.environ.get("WECHAT_REDIRECT_URI", "https://gateway.vafox.com/explorer/auth/wechat/callback"),
    )
    server.phone_verifier = phone_verifier or SignedPhoneVerifier(
        os.environ.get("EXPLORER_PHONE_VERIFICATION_SECRET", "")
    )
    if matcher is None:
        client = EnterpriseDataClient(
            os.environ.get("CORE_BASE_URL", "https://core.vafox.com"),
            os.environ.get("EXPLORER_CORE_API_TOKEN", ""), cache_seconds=30,
        )
        matcher = CorePurchaseMatcher(client)
    server.matcher = matcher
    return server


if __name__ == "__main__":
    create_server().serve_forever()
