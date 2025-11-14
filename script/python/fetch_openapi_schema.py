#!/usr/bin/env python3
"""
Script to fetch OpenAPI schema from the turbine-api and save it locally.

Usage:
    python script/python/fetch_openapi_schema.py --url http://localhost:8000 --output resources/openapi_schema.json
    python script/python/fetch_openapi_schema.py --url https://api.hydrolix.dev --token YOUR_TOKEN
    python script/python/fetch_openapi_schema.py  # Uses defaults
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx is not installed. Please install it with: pip install httpx")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: pyyaml is not installed. Please install it with: pip install pyyaml")
    sys.exit(1)


def fetch_openapi_schema(base_url: str, output_path: Path, token: str = None) -> bool:
    """
    Fetch OpenAPI schema from the API and save it to a file.

    Args:
        base_url: Base URL of the API (e.g., http://localhost:8000)
        output_path: Path where to save the schema file

    Returns:
        True if successful, False otherwise
    """
    schema_url = f"{base_url.rstrip('/')}/config/schema/"

    print(f"Fetching OpenAPI schema from: {schema_url}")

    # Prepare headers
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        print(f"Using authentication token")

    try:
        response = httpx.get(schema_url, headers=headers, timeout=30.0, follow_redirects=True)
        response.raise_for_status()

        # Detect format based on content-type or content
        content_type = response.headers.get('content-type', '').lower()

        # Try to parse the response (supports both JSON and YAML)
        try:
            # First try JSON
            if 'json' in content_type:
                schema = response.json()
                print(f"  Detected format: JSON")
            else:
                # Try YAML (OpenAPI specs are often in YAML)
                try:
                    schema = yaml.safe_load(response.text)
                    print(f"  Detected format: YAML")
                except yaml.YAMLError:
                    # Fallback to JSON
                    schema = response.json()
                    print(f"  Detected format: JSON")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            print(f"✗ Failed to parse response: {e}", file=sys.stderr)
            print(f"\nResponse details:", file=sys.stderr)
            print(f"  - Status code: {response.status_code}", file=sys.stderr)
            print(f"  - Content-Type: {response.headers.get('content-type', 'unknown')}", file=sys.stderr)
            print(f"  - Response length: {len(response.text)} characters", file=sys.stderr)
            print(f"\nFirst 500 characters of response:", file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            print(response.text[:500], file=sys.stderr)
            print("-" * 80, file=sys.stderr)
            print("\nPossible issues:", file=sys.stderr)
            print("  1. The endpoint requires authentication (token/credentials)", file=sys.stderr)
            print("  2. The URL is incorrect", file=sys.stderr)
            print("  3. The API is returning HTML or invalid format", file=sys.stderr)
            print("\nTry:", file=sys.stderr)
            print(f"  curl -I {schema_url}", file=sys.stderr)
            print(f"  curl {schema_url} | head -20", file=sys.stderr)
            return False

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save schema to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)

        # Print summary
        paths_count = len(schema.get('paths', {}))
        operations_count = sum(
            len([k for k in methods.keys() if k in ['get', 'post', 'put', 'patch', 'delete']])
            for methods in schema.get('paths', {}).values()
        )

        print(f"✓ Schema saved to: {output_path}")
        print(f"  - OpenAPI version: {schema.get('openapi', 'unknown')}")
        print(f"  - API title: {schema.get('info', {}).get('title', 'unknown')}")
        print(f"  - API version: {schema.get('info', {}).get('version', 'unknown')}")
        print(f"  - Total paths: {paths_count}")
        print(f"  - Total operations: {operations_count}")

        return True

    except httpx.HTTPError as e:
        print(f"✗ HTTP error occurred: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"  - Status code: {e.response.status_code}", file=sys.stderr)
            print(f"  - Response: {e.response.text[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fetch OpenAPI schema from turbine-api and save it locally"
    )
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='Base URL of the API (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--output',
        default='python/openapi_schema.json',
        help='Output path for the schema file (default: python/openapi_schema.json)'
    )

    args = parser.parse_args()

    # Convert output to Path relative to script location
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / args.output

    success = fetch_openapi_schema(args.url, output_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
