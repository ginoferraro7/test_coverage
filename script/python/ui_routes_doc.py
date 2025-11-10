import re
import json
import sys
from pathlib import Path


def extract_routes(ts_text: str):
    """
    Extract key-value pairs and function definitions from a TS export object.
    Returns a dict mapping route name -> {"path": path_template, "params": {paramName: {"type": str, "required": bool}}}.
    """
    routes = {}

    # Remove comments
    ts_text = re.sub(r"//.*", "", ts_text)

    # Simple static routes
    for key, value in re.findall(r'(\w+):\s*[\'"]([^\'"]+)[\'"]', ts_text):
        routes[key] = {"path": value, "params": {}}

    # Function routes with TS types
    func_pattern = re.compile(r'(\w+):\s*\(([^)]*)\)\s*=>\s*`([^`]+)`', re.DOTALL)
    for key, params_str, template in func_pattern.findall(ts_text):
        param_types = {}
        # Match param name, optional flag, and type
        for match in re.findall(r'(\w+)(\??):\s*([\w\[\]|]+)', params_str):
            param_name, optional, ts_type = match
            param_types[param_name] = {
                "type": ts_type.strip(),
                "required": optional != "?"
            }

        route = re.sub(r"\$\{(\w+)\}", r"{\1}", template)
        routes[key] = {"path": route, "params": param_types}

    return routes


def ts_type_to_openapi(ts_type: str) -> str:
    mapping = {
        "string": "string",
        "number": "number",
        "boolean": "boolean",
        "any": "object",
        "Date": "string"
    }
    return mapping.get(ts_type, "string")


def extract_params(path: str, params: dict):
    """
    Detect {param} placeholders and return OpenAPI parameter definitions
    using the actual TypeScript types and optional flags.
    """
    found_params = re.findall(r"\{(\w+)\}", path)
    parameters = []
    for p in found_params:
        ts_info = params.get(p, {"type": "string", "required": True})
        parameters.append({
            "name": p,
            "in": "path",
            "required": ts_info.get("required", True),
            "schema": {"type": ts_type_to_openapi(ts_info.get("type", "string"))}
        })
    return parameters


def extract_query_params(path: str, params: dict):
    """
    Detect query parameters like ?table_id=${tableId}&data=${tableName}
    and return OpenAPI parameter objects with correct TS types and required flags.
    """
    query_params = []
    if "?" in path:
        query = path.split("?", 1)[1]
        for q in query.split("&"):
            key = q.split("=")[0]
            match = re.search(r"\$\{(\w+)\}", q)
            var_name = match.group(1) if match else None
            ts_info = params.get(var_name, {"type": "string", "required": False})
            if key:
                query_params.append({
                    "name": key,
                    "in": "query",
                    "required": ts_info.get("required", False),
                    "schema": {"type": ts_type_to_openapi(ts_info.get("type", "string"))}
                })
    return query_params


def generate_openapi(routes_ts_path: str, output_path: str):
    ts_text = Path(routes_ts_path).read_text(encoding="utf-8")
    routes = extract_routes(ts_text)

    paths = {}
    for key, info in routes.items():
        raw_path = info["path"]
        params = info["params"]

        # Replace JS-style ${param} with {param}
        path = re.sub(r"\$\{(\w+)\}", r"{\1}", raw_path)
        # Replace Next.js-like [param] with {param}
        path = re.sub(r"\[(\w+)\]", r"{\1}", path)
        # Remove trailing slashes (except root)
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        # Extract all parameters (path + query)
        all_params = extract_params(path, params) + extract_query_params(path, params)

        entry = {}
        if all_params:
            entry["parameters"] = all_params
        paths[path] = entry

    openapi_schema = {
        "openapi": "3.1.0",
        "info": {"title": "UI Routes Schema Doc"},
        "paths": paths,
    }

    Path(output_path).write_text(json.dumps(openapi_schema, indent=2, ensure_ascii=False))
    print(f"OpenAPI-like schema saved to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_openapi_from_routes_ts.py <routes.ts> <output.json>")
        sys.exit(1)

    generate_openapi(sys.argv[1], sys.argv[2])
