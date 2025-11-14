import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def slug_from_path(path: str) -> str:
    slug = re.sub(r"[{}:/]+", "-", path).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug or "root"

def schema_ref_name(schema: Dict[str, Any]) -> Optional[str]:
    if not schema:
        return None
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if schema.get("type") == "array" and isinstance(schema.get("items"), dict):
        it = schema["items"]
        if "$ref" in it:
            return it["$ref"].split("/")[-1]
        return it.get("title") or it.get("type") or "object"
    return schema.get("title") or schema.get("type")

def is_array_schema(schema: Optional[Dict[str, Any]]) -> bool:
    return bool(schema and schema.get("type") == "array")

def pick_description(op: Dict[str, Any]) -> str:
    return (op.get("summary") or op.get("description") or "").strip()

def extract_request_body(op: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    rb = op.get("requestBody")
    if not rb:
        return None
    content = rb.get("content") or {}
    for ct in ("application/json", "application/*+json", "*/*"):
        if ct in content:
            schema = content[ct].get("schema") or {}
            return {
                "modelRef": schema_ref_name(schema),
                "isArray": is_array_schema(schema),
            }
    for _ct, v in content.items():
        schema = v.get("schema") or {}
        return {
            "modelRef": schema_ref_name(schema),
            "isArray": is_array_schema(schema),
        }
    return None

def extract_validations(op: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = []
    responses = op.get("responses") or {}
    for status, resp in responses.items():
        desc = (resp.get("description") or "").strip()
        model_ref = None
        is_arr = False

        content = resp.get("content") or {}
        schema = None
        for ct in ("application/json", "application/*+json", "*/*"):
            if ct in content:
                schema = content[ct].get("schema") or {}
                break
        if not schema and content:
            schema = next(iter(content.values())).get("schema") or {}

        if schema:
            model_ref = schema_ref_name(schema)
            is_arr = is_array_schema(schema)

        out.append({
            "status": status,
            "description": desc or None,
            "modelRef": model_ref,
            "isArray": is_arr if model_ref else False,
        })
    return out

def extract_components_from_parameters(op: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    params = op.get("parameters") or []
    return params or None

def build_id(method: str, path: str, op: Dict[str, Any]) -> str:
    opid = op.get("operationId")
    if opid:
        return f"api-{method.lower()}-{opid}"
    return f"api-{method.lower()}-{slug_from_path(path)}"

def normalize_operation(path: str, method: str, op: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": build_id(method, path, op),
        "featureType": "apiEndpoint",
        "description": pick_description(op) or None,
        "tags": op.get("tags") or [],
        "spec": {
            "path": path,
            "method": method.upper(),
            "operationId": op.get("operationId"),
            "requestBody": extract_request_body(op),
            "protocol": ["http"],
            "validations": extract_validations(op),
            "route": None,
            "components": extract_components_from_parameters(op),
        }
    }


HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}

def normalize_openapi(openapi: Dict[str, Any]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    paths = openapi.get("paths") or {}
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.lower() in HTTP_METHODS and isinstance(op, dict):
                results.append(normalize_operation(path, method, op))
    return results

def main():
    ap = argparse.ArgumentParser(description="Normalize API schema")

    ap.add_argument(
        "--input", "-i",
        type=Path,
        default=Path("script/python/openapi_schema.json"),
        help="Input OpenAPI JSON (default: script/python/openapi_schema.json)"
    )

    ap.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("normalized_schemas/api/normalized_api.json"),
        help="Output JSON file (default: normalized_schemas/api/normalized_api.json)"
    )

    args = ap.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    normalized = normalize_openapi(data)

    out = json.dumps(normalized, indent=2, ensure_ascii=False)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    args.output.write_text(out, encoding="utf-8")
    print(f"Normalized API schema saved to {args.output}")

if __name__ == "__main__":
    main()
