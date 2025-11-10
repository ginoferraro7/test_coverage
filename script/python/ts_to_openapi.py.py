import re
import json
import sys

def parse_ts_routes(ts_content: str) -> dict:
    routes = {}

    # Elimina comentarios y espacios
    ts_content = re.sub(r'//.*', '', ts_content)
    ts_content = ts_content.strip()

    pattern = re.compile(r"(\w+)\s*:\s*(.+?)(?:,|\n|$)")

    for match in pattern.finditer(ts_content):
        key, value = match.groups()
        value = value.strip()

        # Si es una función tipo (param: type) => `...${param}...`
        if "=>" in value:
            func_match = re.search(r"\((.*?)\)\s*=>\s*`([^`]+)`", value)
            if func_match:
                params_def, template = func_match.groups()

                # Extrae parámetros y tipos
                param_types = {}
                for param in re.findall(r"(\w+)\s*:\s*(\w+)", params_def):
                    param_name, param_type = param
                    param_types[param_name] = param_type

                # Convierte ${param} → {param}
                route_template = re.sub(r"\$\{(\w+)\}", r"{\1}", template)

                routes[key] = {"path": route_template, "params": param_types}

        else:
            str_match = re.match(r"['\"]([^'\"]+)['\"]", value)
            if str_match:
                routes[key] = {"path": str_match.group(1), "params": {}}

    return routes


def ts_type_to_openapi(ts_type: str) -> str:
    """Convierte tipos de TypeScript a tipos OpenAPI."""
    mapping = {
        "string": "string",
        "number": "number",
        "boolean": "boolean",
        "any": "object",
        "Date": "string"
    }
    return mapping.get(ts_type, "string")  # default string


def generate_openapi(routes: dict) -> dict:
    paths = {}

    for name, info in routes.items():
        path = info["path"]
        params = info["params"]

        parameters = []
        for param_name, param_type in params.items():
            parameters.append({
                "name": param_name,
                "in": "path",
                "required": True,
                "schema": {"type": ts_type_to_openapi(param_type)}
            })

        paths[path] = {
            "get": {
                "summary": name,
                **({"parameters": parameters} if parameters else {}),
                "responses": {
                    "200": {"description": "OK"}
                }
            }
        }

    openapi_doc = {
        "openapi": "3.0.2",
        "info": {
            "title": "Auto-generated Routes API",
            "version": "1.0.0",
            "description": "API generada automáticamente a partir de rutas TypeScript."
        },
        "paths": paths
    }

    return openapi_doc


def main(ts_file, json_file):
    with open(ts_file, "r", encoding="utf-8") as f:
        ts_content = f.read()

    routes = parse_ts_routes(ts_content)
    openapi_json = generate_openapi(routes)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(openapi_json, f, ensure_ascii=False, indent=2)

    print(f"✅ Archivo OpenAPI generado: {json_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python ts_to_openapi.py <input.ts> <output.json>")
    else:
        main(sys.argv[1], sys.argv[2])
