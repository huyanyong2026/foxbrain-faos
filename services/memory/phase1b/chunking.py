"""Deterministic text normalization and chunking; no extraction is run in HTTP handlers."""
from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid
from dataclasses import dataclass

CHUNKER_VERSION = "recursive-whitespace-v1"

@dataclass(frozen=True)
class Chunk:
    id: str; index: int; text: str; char_start: int; char_end: int; token_count: int; content_sha256: str

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n"))

def chunk_text(memory_id: str, revision: int, text: str, target_tokens=512, overlap_tokens=64):
    if target_tokens < 1 or overlap_tokens < 0 or overlap_tokens >= target_tokens: raise ValueError("invalid chunk token limits")
    text = normalize_text(text); tokens = list(re.finditer(r"\S+", text)); result = []; start = 0
    while start < len(tokens):
        end = min(start + target_tokens, len(tokens)); first, last = tokens[start], tokens[end - 1]
        body = text[first.start():last.end()]; digest = hashlib.sha256(body.encode()).hexdigest()
        stable = uuid.uuid5(uuid.NAMESPACE_URL, f"{memory_id}:{revision}:{len(result)}:{digest}")
        result.append(Chunk(str(stable), len(result), body, first.start(), last.end(), end - start, digest))
        if end == len(tokens): break
        start = end - overlap_tokens
    return result
