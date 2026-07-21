"""Brand knowledge assets, document ingestion, and ACL-aware retrieval.

This module is deliberately self-contained: it layers brand assets on the
existing Knowledge service and does not write to SAP or Core systems.
"""
from __future__ import annotations

import hashlib
import mimetypes
import re
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


SUPPORTED_TYPES = {".docx", ".pdf", ".md", ".markdown"}
BRAND_FIELDS = ("brand_id", "brand_name", "positioning", "origin", "target_user", "product_lines",
                "scenarios", "selling_points", "competitors", "sales_tips", "recommendations",
                "source_traceability")


@dataclass(frozen=True)
class BrandEntity:
    brand_id: str
    brand_name: str
    positioning: str
    origin: str
    target_user: tuple[str, ...]
    product_lines: tuple[str, ...]
    scenarios: tuple[str, ...]
    selling_points: tuple[str, ...]
    competitors: tuple[str, ...]
    sales_tips: tuple[str, ...]
    recommendations: tuple[str, ...]
    source_traceability: tuple[dict, ...]

    def payload(self):
        return asdict(self)


@dataclass(frozen=True)
class BrandDocument:
    document_id: str
    brand_id: str
    filename: str
    content_type: str
    text: str
    metadata: dict
    citations: tuple[dict, ...]
    organization_id: str
    visibility: str
    department_id: str | None = None


def _lines(text):
    return tuple(item.strip() for item in re.split(r"[\n；;]", text) if item.strip())


def default_brands():
    """Curated starter records; retailer-facing claims remain source-attributed."""
    return (
        BrandEntity("kailas", "KAILAS 凯乐石", "专业山地户外品牌", "中国", _lines("登山、攀岩、徒步爱好者；重视专业装备的户外用户"), _lines("攀登；徒步；跑山；滑雪；户外服装"), _lines("高海拔登山；攀岩；徒步穿越；越野跑"), _lines("山地专业性；多场景产品体系；户外社群认同"), _lines("MAMMUT；THE NORTH FACE；ARC'TERYX"), _lines("先确认海拔、天气和行程强度；用分层穿衣和装备匹配解释选择"), _lines("高海拔或技术型山地活动优先介绍对应专业系列"), ({"source": "brand_seed", "location": "brand:kailas", "version": "m4.2"},)),
        BrandEntity("mammut", "MAMMUT 猛犸象", "高山与安全导向的专业户外品牌", "瑞士", _lines("登山、攀岩、滑雪及重视安全性能的专业用户"), _lines("硬壳服装；保暖层；攀登装备；雪地装备；背包"), _lines("阿尔卑斯式登山；攀岩；冰雪；技术徒步"), _lines("高山运动积淀；安全装备心智；技术防护"), _lines("KAILAS；ARC'TERYX；THE NORTH FACE"), _lines("询问是否涉及攀登、冰雪或暴露环境；说明安全装备需结合实际用途选择"), _lines("技术登山、冰雪和安全装备需求可优先推荐"), ({"source": "brand_seed", "location": "brand:mammut", "version": "m4.2"},)),
        BrandEntity("osprey", "OSPREY", "以背负系统为核心的户外背包品牌", "美国", _lines("徒步、旅行、露营和重视背负舒适度的用户"), _lines("徒步背包；旅行包；骑行包；日用包；水袋"), _lines("长线徒步；多日露营；旅行；通勤骑行"), _lines("贴合背负；容量分层；收纳组织；不同身型与行程选择"), _lines("DEUTER；GREGORY；KAILAS"), _lines("先量躯干长度并确认负重、天数和装备体积；现场试背后再选容量"), _lines("多日徒步优先按负重和行程推荐容量，并完成试背调节"), ({"source": "brand_seed", "location": "brand:osprey", "version": "m4.2"},)),
    )


def extract_text(path: Path) -> tuple[str, tuple[dict, ...]]:
    """Extract DOCX, text PDF (when pypdf is installed), or Markdown safely."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_TYPES:
        raise ValueError("unsupported_brand_document_type")
    if suffix in {".md", ".markdown"}:
        text = path.read_text(encoding="utf-8")
        return text, tuple({"location": f"line:{number}", "excerpt": line[:160]} for number, line in enumerate(text.splitlines(), 1) if line.strip())
    if suffix == ".docx":
        with zipfile.ZipFile(path) as archive:
            root = ElementTree.fromstring(archive.read("word/document.xml"))
        paragraphs = ["".join(node.text or "" for node in paragraph.iter() if node.tag.endswith("}t")) for paragraph in root.iter() if paragraph.tag.endswith("}p")]
        paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]
        return "\n".join(paragraphs), tuple({"location": f"paragraph:{i}", "excerpt": value[:160]} for i, value in enumerate(paragraphs, 1))
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("pdf_import_requires_pypdf") from error
    pages = PdfReader(str(path)).pages
    values = [page.extract_text() or "" for page in pages]
    return "\n".join(values), tuple({"location": f"page:{i}", "excerpt": value[:160]} for i, value in enumerate(values, 1) if value.strip())


class BrandKnowledgeStore:
    def __init__(self, brands=None):
        self.brands = {brand.brand_id: brand for brand in (brands or default_brands())}
        self.documents: list[BrandDocument] = []

    def import_document(self, path, brand_id, context, visibility="organization"):
        path = Path(path)
        if brand_id not in self.brands:
            raise KeyError("brand_not_found")
        if visibility not in {"private", "department", "organization"}:
            raise ValueError("invalid_visibility")
        text, citations = extract_text(path)
        raw = path.read_bytes()
        metadata = {"brand_id": brand_id, "filename": path.name, "content_sha256": hashlib.sha256(raw).hexdigest(),
                    "content_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                    "imported_at": datetime.now(timezone.utc).isoformat(), "imported_by": context.owner_id}
        document = BrandDocument(hashlib.sha256((brand_id + metadata["content_sha256"]).encode()).hexdigest()[:24], brand_id, path.name,
                                 metadata["content_type"], text, metadata, citations, context.organization_id, visibility, context.department_id)
        self.documents.append(document)
        return {"document_id": document.document_id, "metadata": metadata, "citations": list(citations), "acl": {"organization_id": document.organization_id, "visibility": visibility, "department_id": document.department_id}}

    @staticmethod
    def _can_read(context, document):
        return context.organization_id == document.organization_id and (document.visibility == "organization" or context.owner_id == document.metadata["imported_by"] or context.is_admin or (document.visibility == "department" and context.department_id == document.department_id))

    def search(self, query, context, brand_id=None, limit=10):
        terms = [term.lower() for term in query.split() if term.strip()]
        candidates = [brand for brand in self.brands.values() if not brand_id or brand.brand_id == brand_id]
        items = []
        for brand in candidates:
            payload = brand.payload()
            haystack = " ".join(str(value) for value in payload.values()).lower()
            score = sum(term in haystack for term in terms)
            if score:
                items.append({"brand": payload, "score": score,
                              "citation": brand.source_traceability[0]})
        for document in self.documents:
            if (brand_id and document.brand_id != brand_id) or not self._can_read(context, document):
                continue
            score = sum(term in document.text.lower() for term in terms)
            if score:
                items.append({"brand": self.brands[document.brand_id].payload(), "score": score, "citation": {"source": document.filename, **(document.citations[0] if document.citations else {"location": "document"})}, "document_id": document.document_id})
        return sorted(items, key=lambda item: (-item["score"], item["brand"]["brand_id"]))[:limit]

    def compare(self, brand_ids):
        if len(brand_ids) < 2 or len(brand_ids) > 3 or any(item not in self.brands for item in brand_ids):
            raise ValueError("invalid_brand_comparison")
        return [self.brands[item].payload() for item in brand_ids]

    def recommend(self, scenario, context, limit=3):
        return self.search(scenario, context, limit=limit)
