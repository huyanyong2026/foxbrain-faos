"""Validate the SAP-to-FoxBrain understanding layer against the Lab dictionary."""

import argparse
import json
from pathlib import Path


def field_reference(reference):
    if "." not in reference:
        return None
    return tuple(reference.split(".", 1))


def validate(mapping, dictionary):
    available = {
        (column["table_name"], column["column_name"])
        for column in dictionary["columns"]
    }
    tables = {table["table_name"] for table in dictionary["tables"]}
    errors = []
    confirmed = mapping.get("confirmed_mappings", [])
    if len(confirmed) != 25:
        errors.append(f"expected 25 confirmed mappings, found {len(confirmed)}")
    for table, object_type, _ in confirmed:
        if table not in tables:
            errors.append(f"confirmed source table missing: {table}")
        if object_type not in mapping["objects"] and object_type not in {
            "company", "contract", "employee", "finance", "inventory", "purchase", "sales"
        }:
            errors.append(f"unknown object type: {object_type}")
    for object_type, definition in mapping["objects"].items():
        if not definition.get("business_meaning"):
            errors.append(f"{object_type}: missing business meaning")
        if not definition.get("ai_query_fields"):
            errors.append(f"{object_type}: missing AI query fields")
        mapped_names = set(definition.get("field_mapping", {}))
        for ai_field in definition.get("ai_query_fields", []):
            if ai_field not in mapped_names:
                errors.append(f"{object_type}: AI field not mapped: {ai_field}")
        for source in definition.get("sources", []):
            if source not in tables:
                errors.append(f"{object_type}: source table missing: {source}")
        references = list(definition.get("source_key", []))
        references += list(definition.get("field_mapping", {}).values())
        for relation in definition.get("relationships", []):
            references.extend((relation["from"], relation["to_key"]))
        for reference in references:
            parsed = field_reference(reference)
            if parsed and parsed not in available:
                errors.append(f"{object_type}: source field missing: {reference}")
    return {
        "valid": not errors,
        "errors": errors,
        "confirmed_mapping_count": len(confirmed),
        "priority_object_count": len(mapping["objects"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", type=Path, default=Path("config/sap_business_object_mappings.json"))
    parser.add_argument("--dictionary", type=Path, default=Path("sap-lab-output/sap_business_dictionary.json"))
    args = parser.parse_args()
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    dictionary = json.loads(args.dictionary.read_text(encoding="utf-8"))
    result = validate(mapping, dictionary)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
