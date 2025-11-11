import re
import json
from pathlib import Path
from typing import Dict, Any

""""
Usage:
python script/python/gen_ui_routes_doc.py 
default path to fetch routes: /routes/routes.ts 
default output path: /routes/docs/routes_openapi_schema.json
default HTML output path: /routes/ui_routes.html
"""
def generate_html_doc(schema: Dict[str, Any]) -> str:
    title = schema.get("info", {}).get("title", "Routes Documentation")
    paths = schema.get("paths", {})

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #fdfdfd;
            color: #333;
        }}
        h1 {{ 
            color: #222; 
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .route-block {{
            margin-bottom: 30px;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        h2.path {{ 
            background-color: #f7f7f7; 
            padding: 12px 20px; 
            margin: 0;
            font-family: 'Courier New', Courier, monospace;
            color: #007bff; /* Blue for the path */
            font-size: 1.2em;
            word-break: break-all;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
        }}
        th, td {{ 
            border-top: 1px solid #eee; 
            padding: 12px 20px; 
            text-align: left; 
            vertical-align: top;
        }}
        th {{ 
            background-color: #fcfcfc;
            font-weight: 600;
            color: #555;
            width: 20%;
        }}
        td:first-child {{
            font-family: 'Courier New', Courier, monospace;
            color: #d63384; /* Pinkish for param name */
            font-weight: bold;
        }}
        .no-params {{
            padding: 12px 20px;
            color: #777;
        }}
        .required-true {{
            font-weight: bold;
            color: #c00;
        }}
        .required-false {{
            color: #555;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    """

    if not paths:
        html += "<p>No paths found.</p>"
    
    # Sort paths for consistent order
    sorted_paths = sorted(paths.items())

    for path, entry in sorted_paths:
        html += '<div class="route-block">'
        html += f'<h2 class="path"><code>{path}</code></h2>'
        
        parameters = entry.get("parameters", [])
        
        if not parameters:
            html += '<div class="no-params">No parameters.</div>'
        else:
            html += """
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>In</th>
                        <th>Required</th>
                        <th>Type</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for param in parameters:
                name = param.get("name", "N/A")
                location = param.get("in", "N/A")
                required = param.get("required", False)
                param_type = param.get("schema", {}).get("type", "string")
                
                required_class = "required-true" if required else "required-false"
                
                html += f"""
                    <tr>
                        <td><code>{name}</code></td>
                        <td>{location}</td>
                        <td><span class="{required_class}">{required}</span></td>
                        <td>{param_type}</td>
                    </tr>
                """
                
            html += """
                </tbody>
            </table>
            """
        
        html += '</div>' # end .route-block

    # Close HTML
    html += """
</body>
</html>
    """
    return html

def extract_routes(ts_text: str):
    """
    Extract key-value pairs and function definitions from a TS export object.
    Returns a dict mapping route name -> {"path": path_template, "params": {paramName: {"type": str, "required": bool}}}.
    """
    routes = {}

    # Remove comments
    ts_text = re.sub(r"//.*", "", ts_text)

    # Static routes
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

def generate_routes_doc():
    input_path = Path("routes/routes.ts")
    output_path = Path("routes/docs/routes_openapi_schema.json")
    html_output_path = Path("routes/ui_routes.html") 

    if not input_path.exists():
        print(f"Routes file not found in: {input_path}")
        return

    ts_text = input_path.read_text(encoding="utf-8")
    routes = extract_routes(ts_text)

    paths = {}
    for key, info in routes.items():
        raw_path = info["path"]
        params = info["params"]

        path = re.sub(r"\$\{(\w+)\}", r"{\1}", raw_path)
        path = re.sub(r"\[(\w+)\]", r"{\1}", path)
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        all_params = extract_params(path, params) + extract_query_params(path, params)
        entry = {}
        if all_params:
            entry["parameters"] = all_params
        paths[path] = entry

    routes_openapi_schema = {
        "openapi": "3.1.0",
        "info": {"title": "UI Routes Documentation"},
        "paths": paths,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(routes_openapi_schema, indent=2, ensure_ascii=False))

    html_content = generate_html_doc(routes_openapi_schema)
    html_output_path.write_text(html_content, encoding="utf-8")
    print(f"UI routes HTML saved to: {html_output_path}")

    print(f"UI routes documentation saved to: {output_path}")


if __name__ == "__main__":
    generate_routes_doc()
