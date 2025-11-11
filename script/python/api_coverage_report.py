#!/usr/bin/env python3
"""
API Coverage Report Tool

Analyzes test coverage of API endpoints by comparing:
- operationIds from OpenAPI schema
- @apiOperation:{operationId} tags in BDD feature files

Usage:
    python script/python/api_coverage_report.py
    python script/python/api_coverage_report.py --schema resources/openapi_schema.json --features test/api/platform/features
    python script/python/api_coverage_report.py --format json --output coverage_report.json
    python script/python/api_coverage_report.py --format html --output coverage_report.html
    python script/python/api_coverage_report.py --format markdown --output coverage_report.md
    python script/python/api_coverage_report.py --save
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

@dataclass
class EndpointInfo:
    """Information about an API endpoint."""
    operation_id: str
    path: str
    method: str
    summary: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class CoverageReport:
    """Complete coverage report data."""
    total_endpoints: int
    covered_endpoints: int
    uncovered_endpoints: int
    coverage_percentage: float
    covered_operations: List[EndpointInfo]
    uncovered_operations: List[EndpointInfo]
    coverage_by_tag: Dict[str, dict]
    coverage_by_method: Dict[str, dict]


class OpenAPIParser:
    """Parse OpenAPI schema to extract operation IDs and endpoint information."""

    def __init__(self, schema_path: Path):
        self.schema_path = schema_path
        self.schema = self._load_schema()

    def _load_schema(self) -> dict:
        """Load OpenAPI schema from JSON file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"✗ Schema file not found: {self.schema_path}", file=sys.stderr)
            print(f"  Run: python script/python/fetch_openapi_schema.py", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in schema file: {e}", file=sys.stderr)
            sys.exit(1)

    def extract_operations(self) -> List[EndpointInfo]:
        """Extract all operations from OpenAPI schema."""
        operations = []
        paths = self.schema.get('paths', {})

        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    operation = path_item[method]
                    operation_id = operation.get('operationId', '')

                    if operation_id:
                        operations.append(EndpointInfo(
                            operation_id=operation_id,
                            path=path,
                            method=method.upper(),
                            summary=operation.get('summary', ''),
                            tags=operation.get('tags', [])
                        ))

        return operations


class FeatureFileParser:
    """Parse BDD feature files to extract operationId tags."""

    def __init__(self, features_dir: Path):
        self.features_dir = features_dir

    def extract_operation_tags(self) -> Dict[str, List[str]]:
        """
        Extract all @apiOperation:{operationId} tags from feature files.

        Returns:
            Dict mapping operationId to list of feature files that test it
        """
        operation_tags = defaultdict(list)
        feature_files = list(self.features_dir.rglob('*.feature'))

        # Pattern to match @apiOperation:{operationId} tags
        op_tag_pattern = re.compile(r'@apiOperation:(\w+)')

        for feature_file in feature_files:
            try:
                with open(feature_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = op_tag_pattern.findall(content)

                    for operation_id in matches:
                        relative_path = feature_file.relative_to(self.features_dir.parent.parent.parent)
                        operation_tags[operation_id].append(str(relative_path))

            except Exception as e:
                print(f"Warning: Could not read {feature_file}: {e}", file=sys.stderr)

        return dict(operation_tags)


class CoverageAnalyzer:
    """Analyze API test coverage."""

    def __init__(self, operations: List[EndpointInfo], operation_tags: Dict[str, List[str]]):
        self.operations = operations
        self.operation_tags = operation_tags

    def analyze(self) -> CoverageReport:
        """Perform coverage analysis."""
        covered_ops = []
        uncovered_ops = []

        for op in self.operations:
            if op.operation_id in self.operation_tags:
                covered_ops.append(op)
            else:
                uncovered_ops.append(op)

        total = len(self.operations)
        covered = len(covered_ops)
        coverage_pct = (covered / total * 100) if total > 0 else 0

        return CoverageReport(
            total_endpoints=total,
            covered_endpoints=covered,
            uncovered_endpoints=total - covered,
            coverage_percentage=coverage_pct,
            covered_operations=covered_ops,
            uncovered_operations=uncovered_ops,
            coverage_by_tag=self._calculate_coverage_by_tag(covered_ops, uncovered_ops),
            coverage_by_method=self._calculate_coverage_by_method(covered_ops, uncovered_ops)
        )

    def _calculate_coverage_by_tag(self, covered: List[EndpointInfo], uncovered: List[EndpointInfo]) -> Dict[str, dict]:
        """Calculate coverage grouped by API tags."""
        tag_stats = defaultdict(lambda: {'total': 0, 'covered': 0})

        for op in covered + uncovered:
            is_covered = op in covered
            for tag in op.tags:
                tag_stats[tag]['total'] += 1
                if is_covered:
                    tag_stats[tag]['covered'] += 1

        # Calculate percentages and status emoji
        for tag, stats in tag_stats.items():
            stats['percentage'] = (stats['covered'] / stats['total'] * 100) if stats['total'] > 0 else 0
            stats['status'] = self._get_status_emoji(stats['percentage'])

        return dict(tag_stats)

    def _calculate_coverage_by_method(self, covered: List[EndpointInfo], uncovered: List[EndpointInfo]) -> Dict[str, dict]:
        """Calculate coverage grouped by HTTP method."""
        method_stats = defaultdict(lambda: {'total': 0, 'covered': 0})

        for op in covered:
            method_stats[op.method]['total'] += 1
            method_stats[op.method]['covered'] += 1

        for op in uncovered:
            method_stats[op.method]['total'] += 1

        # Calculate percentages and status emoji
        for method, stats in method_stats.items():
            stats['percentage'] = (stats['covered'] / stats['total'] * 100) if stats['total'] > 0 else 0
            stats['status'] = self._get_status_emoji(stats['percentage'])

        return dict(method_stats)

    @staticmethod
    def _get_status_emoji(percentage: float) -> str:
        """Get status emoji based on coverage percentage."""
        if percentage >= 80:
            return "🟢"
        elif percentage >= 60:
            return "🟡"
        else:
            return "🔴"


class ReportFormatter:
    """Format coverage reports in different output formats."""

    @staticmethod
    def format_console(report: CoverageReport, operation_tags: Dict[str, List[str]]) -> str:
        """Format report for console output."""
        lines = []
        lines.append("=" * 80)
        lines.append("API ENDPOINT COVERAGE REPORT")
        lines.append("=" * 80)
        lines.append("")

        # Color Legend
        lines.append("COVERAGE STATUS LEGEND")
        lines.append("-" * 80)
        lines.append("  🟢 Green:  >= 80% coverage (Good)")
        lines.append("  🟡 Yellow: >= 60% coverage (Needs Improvement)")
        lines.append("  🔴 Red:    <  60% coverage (Critical)")
        lines.append("")

        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Endpoints:      {report.total_endpoints}")
        lines.append(f"Covered Endpoints:    {report.covered_endpoints}")
        lines.append(f"Uncovered Endpoints:  {report.uncovered_endpoints}")
        lines.append(f"Coverage:             {report.coverage_percentage:.2f}%")
        lines.append("")

        # Coverage by HTTP Method
        if report.coverage_by_method:
            lines.append("COVERAGE BY HTTP METHOD")
            lines.append("-" * 80)
            for method in sorted(report.coverage_by_method.keys()):
                stats = report.coverage_by_method[method]
                lines.append(f"  {stats['status']} {method:8s}  {stats['covered']:3d}/{stats['total']:3d}  ({stats['percentage']:5.1f}%)")
            lines.append("")

        # Coverage by API Tag
        if report.coverage_by_tag:
            lines.append("COVERAGE BY API TAG")
            lines.append("-" * 80)
            sorted_tags = sorted(report.coverage_by_tag.items(), key=lambda x: x[1]['percentage'], reverse=True)
            for tag, stats in sorted_tags:
                lines.append(f"  {stats['status']} {tag:20s}  {stats['covered']:3d}/{stats['total']:3d}  ({stats['percentage']:5.1f}%)")
            lines.append("")

        # Uncovered endpoints
        if report.uncovered_operations:
            lines.append("UNCOVERED ENDPOINTS")
            lines.append("-" * 80)
            lines.append(f"{'OperationId':<40s} {'Method':<8s} {'Path':<30s}")
            lines.append("-" * 80)

            for op in sorted(report.uncovered_operations, key=lambda x: (x.tags[0] if x.tags else '', x.operation_id)):
                tag_prefix = f"[{op.tags[0]}] " if op.tags else ""
                lines.append(f"{tag_prefix}{op.operation_id:<40s} {op.method:<8s} {op.path}")
            lines.append("")

        # Covered endpoints (optional, can be verbose)
        lines.append(f"COVERED ENDPOINTS ({len(report.covered_operations)} total)")
        lines.append("-" * 80)
        if report.covered_operations:
            for op in sorted(report.covered_operations, key=lambda x: x.operation_id)[:20]:
                feature_files = operation_tags.get(op.operation_id, [])
                lines.append(f"  ✓ {op.operation_id} ({op.method} {op.path})")
                for f in feature_files[:3]:  # Show first 3 files
                    lines.append(f"      → {f}")
            if len(report.covered_operations) > 20:
                lines.append(f"  ... and {len(report.covered_operations) - 20} more")
        lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def format_json(report: CoverageReport, operation_tags: Dict[str, List[str]]) -> str:
        """Format report as JSON."""
        data = {
            'legend': {
                'green': {'emoji': '🟢', 'threshold': '>= 80%', 'description': 'Good coverage'},
                'yellow': {'emoji': '🟡', 'threshold': '>= 60%', 'description': 'Needs improvement'},
                'red': {'emoji': '🔴', 'threshold': '< 60%', 'description': 'Critical - needs attention'}
            },
            'summary': {
                'total_endpoints': report.total_endpoints,
                'covered_endpoints': report.covered_endpoints,
                'uncovered_endpoints': report.uncovered_endpoints,
                'coverage_percentage': round(report.coverage_percentage, 2)
            },
            'coverage_by_method': report.coverage_by_method,
            'coverage_by_tag': report.coverage_by_tag,
            'covered_operations': [
                {
                    **asdict(op),
                    'tested_in_files': operation_tags.get(op.operation_id, [])
                }
                for op in report.covered_operations
            ],
            'uncovered_operations': [asdict(op) for op in report.uncovered_operations]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def format_html(report: CoverageReport, operation_tags: Dict[str, List[str]]) -> str:
        """Format report as HTML."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Coverage Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            min-width: 0; 
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-box.covered {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .stat-box.uncovered {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }}
        .stat-box h3 {{
            margin: 0;
            font-size: 2em;
            font-weight: bold;
        }}
        .stat-box p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            transition: width 0.3s ease;
        }}
        
        .progress-text {{
            position: relative;
            z-index: 1; /* keeps text above the fill */
            color: #000;
            min-width: 12%;
            padding-left: 8px;
            white-space: nowrap;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            table-layout: fixed;
            border-collapse: collapse;
        }}
        th {{
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
        }}
        td {{
            white-space: normal;
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
            word-break: break-all;
        }}
        
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .method {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85em;
        }}
        .method.GET {{ background-color: #61affe; color: white; }}
        .method.POST {{ background-color: #49cc90; color: white; }}
        .method.PUT {{ background-color: #fca130; color: white; }}
        .method.PATCH {{ background-color: #50e3c2; color: white; }}
        .method.DELETE {{ background-color: #f93e3e; color: white; }}
        .tag {{
            display: inline-block;
            background-color: #e0e0e0;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin: 2px;
        }}
        .covered-icon {{ color: #4CAF50; }}
        .uncovered-icon {{ color: #f44336; }}
        .file-link {{
            color: #667eea;
            font-size: 0.9em;
            margin-left: 20px;
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 API Endpoint Coverage Report</h1>

        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea;">
            <h3 style="margin-top: 0; color: #333;">Coverage Status Legend</h3>
            <div style="display: flex; gap: 30px; flex-wrap: wrap;">
                <div><strong>🟢 Green:</strong> ≥ 80% coverage (Good)</div>
                <div><strong>🟡 Yellow:</strong> ≥ 60% coverage (Needs Improvement)</div>
                <div><strong>🔴 Red:</strong> &lt; 60% coverage (Critical)</div>
            </div>
        </div>

        <div class="summary">
            <div class="stat-box">
                <h3>{report.total_endpoints}</h3>
                <p>Total Endpoints</p>
            </div>
            <div class="stat-box covered">
                <h3>{report.covered_endpoints}</h3>
                <p>Covered</p>
            </div>
            <div class="stat-box uncovered">
                <h3>{report.uncovered_endpoints}</h3>
                <p>Uncovered</p>
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {report.coverage_percentage}%">
                <span class="progress-text">{round(report.coverage_percentage)}% Coverage</span>
            </div>
            
        </div>

        <h2>📊 Coverage by HTTP Method</h2>
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Method</th>
                    <th>Total</th>
                    <th>Covered</th>
                    <th>Uncovered</th>
                    <th>Coverage</th>
                </tr>
            </thead>
            <tbody>
"""
        for method in sorted(report.coverage_by_method.keys()):
            stats = report.coverage_by_method[method]
            html += f"""
                <tr>
                    <td>{stats['status']}</td>
                    <td><span class="method {method}">{method}</span></td>
                    <td>{stats['total']}</td>
                    <td>{stats['covered']}</td>
                    <td>{stats['total'] - stats['covered']}</td>
                    <td>{stats['percentage']:.1f}%</td>
                </tr>
"""
        html += """
            </tbody>
        </table>

        <h2>🏷️ Coverage by API Tag</h2>
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Tag</th>
                    <th>Total</th>
                    <th>Covered</th>
                    <th>Uncovered</th>
                    <th>Coverage</th>
                </tr>
            </thead>
            <tbody>
"""
        sorted_tags = sorted(report.coverage_by_tag.items(), key=lambda x: x[1]['percentage'], reverse=True)
        for tag, stats in sorted_tags:
            html += f"""
                <tr>
                    <td>{stats['status']}</td>
                    <td><span class="tag">{tag}</span></td>
                    <td>{stats['total']}</td>
                    <td>{stats['covered']}</td>
                    <td>{stats['total'] - stats['covered']}</td>
                    <td>{stats['percentage']:.1f}%</td>
                </tr>
"""
        html += """
            </tbody>
        </table>

        <h2>❌ Uncovered Endpoints</h2>
        <table style='width: 100%; max-width: 100%; table-layout: fixed;'>
            <thead>
                <tr>
                    <th>Operation ID</th>
                    <th>Method</th>
                    <th>Path</th>
                    <th>Tags</th>
                </tr>
            </thead>
            <tbody>
"""
        for op in sorted(report.uncovered_operations, key=lambda x: x.operation_id):
            tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in op.tags])
            html += f"""
                <tr>
                    <td><span class="uncovered-icon">✗</span> {op.operation_id}</td>
                    <td><span class="method {op.method}">{op.method}</span></td>
                    <td><code>{op.path}</code></td>
                    <td>{tags_html}</td>
                </tr>
"""
        html += """
            </tbody>
        </table>

        <h2>✅ Covered Endpoints</h2>
        <table>
            <thead>
                <tr>
                    <th>Operation ID</th>
                    <th>Method</th>
                    <th>Path</th>
                    <th>Tested In</th>
                </tr>
            </thead>
            <tbody>
"""
        for op in sorted(report.covered_operations, key=lambda x: x.operation_id):
            feature_files = operation_tags.get(op.operation_id, [])
            files_html = '<br>'.join([f'<span class="file-link">→ {f}</span>' for f in feature_files[:5]])
            if len(feature_files) > 5:
                files_html += f'<br><span class="file-link">... and {len(feature_files) - 5} more</span>'

            html += f"""
                <tr>
                    <td><span class="covered-icon">✓</span> {op.operation_id}</td>
                    <td><span class="method {op.method}">{op.method}</span></td>
                    <td><code>{op.path}</code></td>
                    <td>{files_html}</td>
                </tr>
"""
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def format_markdown(report: CoverageReport, operation_tags: Dict[str, List[str]]) -> str:
        """Format report as Markdown."""
        lines = []
        lines.append("# API Endpoint Coverage Report")
        lines.append("")

        # Summary with badges
        coverage_badge = "🟢" if report.coverage_percentage >= 80 else "🟡" if report.coverage_percentage >= 60 else "🔴"
        lines.append(f"{coverage_badge} **Coverage: {report.coverage_percentage:.2f}%**")
        lines.append("")

        # Color Legend
        lines.append("## Coverage Status Legend")
        lines.append("")
        lines.append("| Status | Threshold | Description |")
        lines.append("|--------|-----------|-------------|")
        lines.append("| 🟢 Green | ≥ 80% | Good coverage |")
        lines.append("| 🟡 Yellow | ≥ 60% | Needs improvement |")
        lines.append("| 🔴 Red | < 60% | Critical - needs attention |")
        lines.append("")

        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|------:|")
        lines.append(f"| Total Endpoints | {report.total_endpoints} |")
        lines.append(f"| Covered Endpoints | {report.covered_endpoints} |")
        lines.append(f"| Uncovered Endpoints | {report.uncovered_endpoints} |")
        lines.append(f"| **Coverage Percentage** | **{coverage_badge} {report.coverage_percentage:.2f}%** |")
        lines.append("")

        # Coverage by HTTP Method
        if report.coverage_by_method:
            lines.append("## Coverage by HTTP Method")
            lines.append("")
            lines.append("| Method | Covered | Total | Percentage |")
            lines.append("|--------|--------:|------:|-----------:|")
            for method in sorted(report.coverage_by_method.keys()):
                stats = report.coverage_by_method[method]
                lines.append(f"| {stats['status']} {method} | {stats['covered']} | {stats['total']} | {stats['percentage']:.1f}% |")
            lines.append("")

        # Coverage by API Tag
        if report.coverage_by_tag:
            lines.append("## Coverage by API Tag")
            lines.append("")
            lines.append("| Tag | Covered | Total | Percentage |")
            lines.append("|-----|--------:|------:|-----------:|")
            sorted_tags = sorted(report.coverage_by_tag.items(), key=lambda x: x[1]['percentage'], reverse=True)
            for tag, stats in sorted_tags:
                lines.append(f"| {stats['status']} {tag} | {stats['covered']} | {stats['total']} | {stats['percentage']:.1f}% |")
            lines.append("")

        # Uncovered endpoints
        if report.uncovered_operations:
            lines.append(f"## Uncovered Endpoints ({len(report.uncovered_operations)} endpoints)")
            lines.append("")
            lines.append("| Operation ID | Method | Path | Tags |")
            lines.append("|-------------|--------|------|------|")
            for op in sorted(report.uncovered_operations, key=lambda x: x.operation_id):
                tags_str = ", ".join(op.tags) if op.tags else ""
                lines.append(f"| `{op.operation_id}` | {op.method} | `{op.path}` | {tags_str} |")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Report generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate API endpoint coverage report from OpenAPI schema and BDD tests"
    )
    parser.add_argument(
        '--schema',
        default='script/python/openapi_schema.json',
        help='Path to OpenAPI schema file (default: script/python/openapi_schema.json)'
    )
    parser.add_argument(
        '--features',
        default='test/api/platform/features',
        help='Path to features directory (default: test/api/platform/features)'
    )
    parser.add_argument(
        '--format',
        choices=['console', 'json', 'html', 'markdown'],
        default='html',
        help='Output format (default: console)'
    )
    parser.add_argument(
        '--save',
        help='Generates an html file into reports/api_archive with datetime.now()',
        action='store_true'
    )
    parser.add_argument(
        '--output',
        help='Output file path (default: stdout for console, or auto-named file for json/html/markdown)'
    )

    args = parser.parse_args()

    # Resolve paths relative to elessar-fmwk directory (script is in script/python/)
    script_dir = Path(__file__).parent.parent.parent
    schema_path = script_dir / args.schema
    features_path = script_dir / args.features
    report_dir = Path("reports/")
    report_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = Path("reports/api_archive")
    date_time_now = datetime.now().strftime("%Y-%m-%d")

    # Parse OpenAPI schema
    print(f"📖 Reading OpenAPI schema from: {schema_path}", file=sys.stderr)
    openapi_parser = OpenAPIParser(schema_path)
    operations = openapi_parser.extract_operations()
    print(f"   Found {len(operations)} operations", file=sys.stderr)

    # Parse feature files
    print(f"🔍 Scanning feature files in: {features_path}", file=sys.stderr)
    feature_parser = FeatureFileParser(features_path)
    operation_tags = feature_parser.extract_operation_tags()
    print(f"   Found {len(operation_tags)} operation IDs tagged in tests", file=sys.stderr)

    # Analyze coverage
    print(f"📊 Analyzing coverage...", file=sys.stderr)
    analyzer = CoverageAnalyzer(operations, operation_tags)
    report = analyzer.analyze()

    # Format report
    formatter = ReportFormatter()
    if args.format == 'console':
        output = formatter.format_console(report, operation_tags)
    elif args.format == 'json':
        output = formatter.format_json(report, operation_tags)
    elif args.format == 'html':
        output = formatter.format_html(report, operation_tags)
    elif args.format == 'markdown':
        output = formatter.format_markdown(report, operation_tags)

    # Saves api_coverage.html archive
    if args.save:
        output = formatter.format_html(report, operation_tags)
        archive_dir.mkdir(parents=True, exist_ok=True)
        output_path_archive = archive_dir / f"api_coverage_{date_time_now}.html"
        output_path = report_dir / "api_coverage.html"

        for path in [output_path, output_path_archive]:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(output)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✓ Report saved to: {output_path}", file=sys.stderr)
    else:
        if args.format == 'console':
            print(output)
        else:   
            if args.format == 'html':
                output_path = report_dir / "api_coverage.html"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                        
            else:
                # For other formats like json, keep the original behavior
                output_path = script_dir / f"coverage_report.{args.format}"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output)

            print(f"✓ Report saved to: {output_path}", file=sys.stderr)

if __name__ == '__main__':
    main()
