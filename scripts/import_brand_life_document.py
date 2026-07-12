"""Import one local document into an isolated or deployed Brand Knowledge Vault."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from foxbrain_os.brand_life_engine import (
    extract_brand_document,
    register_brand_document,
    seed_kailas,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--brand", default="KAILAS")
    parser.add_argument("--confidentiality", choices=("public", "sensitive"), default="sensitive")
    args = parser.parse_args()
    if not args.file.exists():
        raise SystemExit("document not found")
    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    try:
        brand_id = seed_kailas(conn)
        extraction = extract_brand_document(args.file)
        result = register_brand_document(
            conn,
            brand_id,
            args.file.name,
            str(args.file),
            extraction["text"],
            confidentiality=args.confidentiality,
            processing_error=extraction["error"],
        )
        conn.commit()
        result["extraction_status"] = extraction["status"]
        result["extracted_characters"] = len(extraction["text"])
        print(json.dumps(result, ensure_ascii=False))
    finally:
        conn.close()


if __name__ == "__main__":
    main()
