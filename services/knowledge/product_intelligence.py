"""Auditable, read-only Product Intelligence MVP domain service.

The store deliberately contains no connector capable of writing SAP, Core,
purchasing, order, inventory, or sales systems.  Publishing is an explicit
human-review action and all API advice remains non-executable.
"""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import PurePath

from services.memory.acl import can_access

SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".md", ".markdown", ".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_UPLOAD_ROLES = frozenset({"brand_partner", "procurement", "product_manager", "operation", "admin"})
ADVISORY_NOTICE = "库存、价格、尺码及实时场景请由员工核实；本建议需人工确认后使用。"


def now():
    return datetime.now(timezone.utc).isoformat()


def identifier(prefix):
    return f"{prefix}:{uuid.uuid4()}"


class ProductIntelligenceStore:
    """Small MVP store with immutable asset bytes and append-only audit events."""
    def __init__(self):
        self.assets, self.cards, self.audit_events = {}, {}, []

    def _audit(self, action, context, resource_id, detail=None):
        self.audit_events.append({"event_id": identifier("audit"), "at": now(), "action": action,
                                  "actor_id": context.owner_id, "organization_id": context.organization_id,
                                  "resource_id": resource_id, "detail": detail or {}})

    @staticmethod
    def _authorized_uploader(context):
        return bool(context.role_scopes & ALLOWED_UPLOAD_ROLES)

    def upload(self, context, filename, content, metadata):
        if not self._authorized_uploader(context):
            raise PermissionError("upload_role_required")
        suffix = PurePath(filename).suffix.lower()
        if not filename or suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError("unsupported_media_type")
        if not content or len(content) > 25 * 1024 * 1024:
            raise ValueError("invalid_asset_size")
        digest = hashlib.sha256(content).hexdigest()
        asset_id = identifier("ast")
        asset = {"asset_id": asset_id, "asset_version": "1", "filename": PurePath(filename).name,
                 "extension": suffix, "content_sha256": digest, "size_bytes": len(content),
                 "organization_id": context.organization_id, "owner_id": context.owner_id,
                 "department_id": context.department_id, "visibility": context.upload_visibility,
                 "metadata": {key: metadata.get(key) for key in ("asset_type", "brand_id", "source", "effective_from") if metadata.get(key) is not None},
                 "review_status": "Draft", "processing_status": "Processing", "created_at": now(),
                 "content": bytes(content), "chunks": [], "entities": []}
        self.assets[asset_id] = asset
        self._audit("asset_uploaded", context, asset_id, {"sha256": digest, "filename": asset["filename"]})
        self.process(context, asset_id)
        return asset

    def process(self, context, asset_id):
        asset = self.assets[asset_id]
        raw = asset["content"]
        # Text-native MVP parser: binary formats stay traceable and await a production parser/OCR adapter.
        text = raw.decode("utf-8", errors="replace") if asset["extension"] in {".md", ".markdown", ".txt"} else ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        asset["chunks"] = [{"chunk_id": identifier("chk"), "text": line,
                            "locator": f"#heading=source&lines={i}-{i}", "content_sha256": asset["content_sha256"]}
                           for i, line in enumerate(lines, 1)]
        brand = asset["metadata"].get("brand_id") or self._find_value(lines, "brand")
        model = self._find_value(lines, "model") or self._find_value(lines, "产品")
        series = self._find_value(lines, "series")
        category = self._find_value(lines, "category")
        if brand or model:
            citation = self._citation(asset, asset["chunks"][0] if asset["chunks"] else None)
            asset["entities"] = [{"entity_type": "Brand Entity", "value": brand, "citation": citation},
                                 {"entity_type": "Product Entity", "value": model, "citation": citation},
                                 {"entity_type": "Scenario Entity", "value": self._find_value(lines, "scenario"), "citation": citation}]
            asset["candidate"] = {"brand": brand or "unknown", "series": series or "unknown", "model": model or "unknown", "category": category or "unknown", "citation": citation}
        asset["processing_status"] = "Review"
        asset["review_status"] = "Review"
        self._audit("asset_processed", context, asset_id, {"chunks": len(asset["chunks"]), "entities": len(asset["entities"])})

    @staticmethod
    def _find_value(lines, key):
        pattern = re.compile(rf"^{re.escape(key)}\s*[:：]\s*(.+)$", re.I)
        for line in lines:
            match = pattern.match(line)
            if match: return match.group(1).strip()
        return None

    @staticmethod
    def _citation(asset, chunk):
        return {"citation_id": identifier("cit"), "asset_id": asset["asset_id"], "asset_version": asset["asset_version"],
                "content_sha256": asset["content_sha256"], "chunk_id": chunk.get("chunk_id") if chunk else None,
                "locator": chunk.get("locator") if chunk else "#document", "source": asset["filename"]}

    def asset(self, context, asset_id):
        asset = self.assets.get(asset_id)
        return asset if asset and can_access(context, asset) else None

    def review(self, context, asset_id, decision):
        asset = self.asset(context, asset_id)
        if not asset: return None
        if "product_manager" not in context.role_scopes and not context.is_admin:
            raise PermissionError("review_role_required")
        if decision not in {"approved", "returned", "rejected"}: raise ValueError("invalid_review_decision")
        if decision != "approved":
            asset["review_status"] = "Draft" if decision == "returned" else "Archived"
            self._audit(f"asset_{decision}", context, asset_id); return asset
        candidate = asset.get("candidate")
        if not candidate or candidate["brand"] == "unknown" or candidate["model"] == "unknown":
            raise ValueError("citation_or_identity_incomplete")
        card = self._card_from_candidate(asset, candidate)
        self.cards[card["product_id"]] = card
        asset["review_status"], asset["processing_status"] = "Published", "Published"
        self._audit("asset_published_after_human_review", context, asset_id, {"card_id": card["card_id"]})
        return asset

    def _card_from_candidate(self, asset, candidate):
        citation = candidate["citation"]
        model = candidate["model"]
        return {"card_id": identifier("pcd"), "product_id": f"prd:{candidate['brand']}:{model}".lower().replace(" ", "-"),
                "knowledge_version": "1", "review_status": "Published", "brand": candidate["brand"], "series": candidate["series"],
                "model": model, "category": candidate["category"], "positioning": "unknown", "technology": [], "scenario": [],
                "customer_profile": [], "selling_points": [], "gear_package": [], "citation": [citation],
                "confidence": {"level": "low", "score": 0.4, "limitations": ["MVP parser only extracted explicitly declared fields"]},
                "version": "1", "knowledge_as_of": now(), "asset_id": asset["asset_id"],
                "advisory_only_requires_human_approval": True, "human_review_required": True, "notice": ADVISORY_NOTICE}

    def get_card(self, context, product_id):
        card = self.cards.get(product_id)
        asset = self.assets.get(card["asset_id"]) if card else None
        return card if card and asset and can_access(context, asset) else None

    def search(self, context, query, limit=10):
        terms = [term.casefold() for term in query.split() if term]
        return [card for card in self.cards.values() if self.get_card(context, card["product_id"]) and
                all(term in json.dumps(card, ensure_ascii=False).casefold() for term in terms)][:limit]

    def recommend(self, context, scenario, need, limit=5):
        # Purely read-only matching; no inventory/sales system is queried or changed.
        cards = self.search(context, f"{scenario} {need}", limit) or self.search(context, need, limit)
        return {"scenario": scenario, "need": need, "items": cards,
                "recommendation_reason": "基于已发布且有 Citation 的产品资料；未执行任何业务动作。",
                "sales_data": {"status": "not_connected_read_only_mvp"}, "inventory": {"status": "not_connected_read_only_mvp"},
                "store_advice": "请由门店员工核实库存、价格、尺码和实际场景后决定。",
                "advisory_only_requires_human_approval": True, "notice": ADVISORY_NOTICE}
