"""Small Python 3.14 compatibility shim for the removed stdlib cgi.FieldStorage.

It supports the subset used by portal_v2: multipart/form-data file uploads,
field membership, item lookup, and getfirst().
"""

from __future__ import annotations

from dataclasses import dataclass
from email.parser import BytesParser
from email.policy import default


@dataclass
class MiniField:
    name: str
    value: str = ""
    filename: str | None = None
    file: object | None = None


class FieldStorage(dict):
    def __init__(self, fp=None, headers=None, environ=None, *_, **__):
        super().__init__()
        if fp is None or headers is None:
            return
        content_type = headers.get("Content-Type", "")
        length = int(headers.get("Content-Length", "0") or 0)
        body = fp.read(length) if length else b""
        if not content_type.lower().startswith("multipart/"):
            return
        message = BytesParser(policy=default).parsebytes(
            ("Content-Type: {}\r\nMIME-Version: 1.0\r\n\r\n".format(content_type)).encode("utf-8") + body
        )
        for part in message.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if not name:
                continue
            filename = part.get_filename()
            payload = part.get_payload(decode=True) or b""
            if filename:
                import io
                value = MiniField(name=name, filename=filename, file=io.BytesIO(payload))
            else:
                charset = part.get_content_charset() or "utf-8"
                value = MiniField(name=name, value=payload.decode(charset, errors="replace"))
            if name in self:
                current = dict.__getitem__(self, name)
                if isinstance(current, list):
                    current.append(value)
                else:
                    dict.__setitem__(self, name, [current, value])
            else:
                dict.__setitem__(self, name, value)

    def getfirst(self, key, default=None):
        if key not in self:
            return default
        value = dict.__getitem__(self, key)
        if isinstance(value, list):
            value = value[0]
        return value.value
