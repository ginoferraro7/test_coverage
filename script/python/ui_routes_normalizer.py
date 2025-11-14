import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_base_from_route(route: str) -> (str, Optional[str], List[str]):
    if route == "/":
        return "root", None, []

    if "?" in route:
        path_part, query_part = route.split("?", 1)
    else:
        path_part, query_part = route, None

    segments = [s for s in path_part.split("/") if s]
    base = "_".join(segments) if segments else "root"

    return base, query_part, segments


def build_id(route: str) -> str:
    if route == "/":
        return "ui_root"

    path_part = route.split("?", 1)[0]
    segments = [s for s in path_part.split("/") if s]

    literal_segments = [
        s for s in segments
        if not (s.startswith("{") and s.endswith("}"))
    ]

    if not literal_segments:
        base = "root"
    else:
        base = "_".join(literal_segments)

    return f"ui_{base}"


def build_operation_id(route: str) -> str:
    base, query_part, _ = build_base_from_route(route)
    if query_part is not None:
        return f"{base}_?{query_part}"
    return base


def build_tags(route: str) -> List[str]:
    if route == "/":
        return []

    path_part = route.split("?", 1)[0]
    segments = [s for s in path_part.split("/") if s]

    if len(segments) == 0:
        return []
    if len(segments) == 1:
        return [segments[0]]
    if len(segments) == 2:
        return [segments[0]]
    return [segments[0], segments[1]]


def normalize_routes_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    paths = doc.get("paths", {})
    features: List[Dict[str, Any]] = []

    for route, path_item in sorted(paths.items(), key=lambda kv: kv[0]):
        if not isinstance(path_item, dict):
            path_item = {}

        feature_id = build_id(route)
        operation_id = build_operation_id(route)
        tags = build_tags(route)

        parameters = path_item.get("parameters")
        components = parameters if isinstance(parameters, list) else None

        feature = {
            "id": feature_id,
            "featureType": "uiPage",
            "description": "",
            "tags": tags,
            "spec": {
                "route": route,
                "path": None,
                "method": None,
                "operationId": operation_id,
                "components": components,
            },
        }

        features.append(feature)

    return {"features": features}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize UI routes JSON into features schema."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("routes/docs/routes_openapi_schema.json"),
        help="Input JSON file (default: routes/docs/routes_openapi_schema.json)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("normalized_schemas/ui_routes/normalized_ui_routes.json"),
        help="Output JSON file (default: normalized_schemas/ui_routes/normalized_ui_routes.json)",
    )

    args = parser.parse_args()

    doc = load_json(args.input)
    normalized = normalize_routes_doc(doc)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)
        print(f"Normalized UI routes schema saved to {args.output}")



if __name__ == "__main__":
    main()
