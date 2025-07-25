#!/usr/bin/env python3
"""
Coverage validation script.

This script analyzes coverage reports, identifies uncovered code paths,
and validates that coverage meets the required thresholds.
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Tuple, Set


def parse_coverage_xml(coverage_file: str) -> Dict[str, Any]:
    """Parse a coverage.xml file and extract coverage data."""
    if not os.path.exists(coverage_file):
        raise FileNotFoundError(f"Coverage file not found: {coverage_file}")
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    # Extract overall coverage
    coverage_data = {
        "line_rate": float(root.get("line-rate", 0)),
        "branch_rate": float(root.get("branch-rate", 0)),
        "lines_covered": int(root.get("lines-covered", 0)),
        "lines_valid": int(root.get("lines-valid", 0)),
        "branches_covered": int(root.get("branches-covered", 0)),
        "branches_valid": int(root.get("branches-valid", 0)),
        "timestamp": root.get("timestamp", ""),
        "packages": []
    }
    
    # Extract package data
    for package in root.findall(".//package"):
        package_name = package.get("name", "")
        
        package_data = {
            "name": package_name,
            "line_rate": float(package.get("line-rate", 0)),
            "branch_rate": float(package.get("branch-rate", 0)),
            "classes": []
        }
        
        # Extract class data
        for class_elem in package.findall(".//class"):
            class_name = class_elem.get("name", "")
            filename = class_elem.get("filename", "")
            
            class_data = {
                "name": class_name,
                "filename": filename,
                "line_rate": float(class_elem.get("line-rate", 0)),
                "branch_rate": float(class_elem.get("branch-rate", 0)),
                "lines": []
            }
            
            # Extract line data
            for line in class_elem.findall(".//line"):
                line_data = {
                    "number": int(line.get("number", 0)),
                    "hits": int(line.get("hits", 0)),
                    "branch": line.get("branch", "false") == "true"
                }
                
                class_data["lines"].append(line_data)
            
            package_data["classes"].append(class_data)
        
        coverage_data["packages"].append(package_data)
    
    return coverage_data


def find_uncovered_lines(coverage_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find uncovered lines in the coverage data."""
    uncovered_lines = []
    
    for package in coverage_data["packages"]:
        for class_data in package["classes"]:
            filename = class_data["filename"]
            
            for line in class_data["lines"]:
                if line["hits"] == 0:
                    uncovered_lines.append({
                        "filename": filename,
                        "line": line["number"],
                        "branch": line["branch"]
                    })
    
    # Sort by filename and line number
    uncovered_lines.sort(key=lambda x: (x["filename"], x["line"]))
    
    return uncovered_lines


def get_file_content(filename: str) -> List[str]:
    """Get the content of a file as a list of lines."""
    if not os.path.exists(filename):
        return []
    
    with open(filename, 'r') as f:
        return f.readlines()


def validate_coverage(
    coverage_data: Dict[str, Any],
    threshold: float = 0.8
) -> Tuple[bool, Dict[str, Any]]:
    """Validate that coverage meets the required threshold."""
    line_rate = coverage_data["line_rate"]
    lines_covered = coverage_data["lines_covered"]
    lines_valid = coverage_data["lines_valid"]
    
    # Calculate coverage percentage
    coverage_pct = line_rate * 100
    
    # Check if coverage meets threshold
    meets_threshold = line_rate >= threshold
    
    # Prepare validation result
    result = {
        "meets_threshold": meets_threshold,
        "coverage_pct": coverage_pct,
        "threshold_pct": threshold * 100,
        "lines_covered": lines_covered,
        "lines_valid": lines_valid,
        "missing_coverage": lines_valid - lines_covered
    }
    
    return meets_threshold, result


def find_untested_files(
    coverage_data: Dict[str, Any],
    source_dirs: List[str]
) -> List[str]:
    """Find source files that are not included in the coverage report."""
    # Get all Python files in source directories
    all_source_files = set()
    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            continue
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file))
                    all_source_files.add(rel_path)
    
    # Get files in coverage report
    covered_files = set()
    for package in coverage_data["packages"]:
        for class_data in package["classes"]:
            filename = class_data["filename"]
            covered_files.add(filename)
    
    # Find files not in coverage report
    untested_files = all_source_files - covered_files
    
    return sorted(list(untested_files))


def generate_coverage_report(
    coverage_data: Dict[str, Any],
    uncovered_lines: List[Dict[str, Any]],
    validation_result: Dict[str, Any],
    untested_files: List[str],
    output_file: str = "coverage_report.md"
) -> str:
    """Generate a markdown report of coverage analysis."""
    with open(output_file, 'w') as f:
        f.write("# Coverage Analysis Report\n\n")
        
        # Coverage summary
        f.write("## Coverage Summary\n\n")
        f.write(f"- **Overall Coverage**: {validation_result['coverage_pct']:.1f}%\n")
        f.write(f"- **Threshold**: {validation_result['threshold_pct']:.1f}%\n")
        f.write(f"- **Lines Covered**: {validation_result['lines_covered']}\n")
        f.write(f"- **Lines Valid**: {validation_result['lines_valid']}\n")
        f.write(f"- **Missing Coverage**: {validation_result['missing_coverage']}\n\n")
        
        if validation_result["meets_threshold"]:
            f.write("✅ **Coverage meets the required threshold**\n\n")
        else:
            f.write("❌ **Coverage does not meet the required threshold**\n\n")
        
        # Package coverage
        f.write("## Package Coverage\n\n")
        f.write("| Package | Coverage |\n")
        f.write("|---------|----------|\n")
        
        for package in coverage_data["packages"]:
            f.write(f"| {package['name']} | {package['line_rate']*100:.1f}% |\n")
        
        f.write("\n")
        
        # Untested files
        if untested_files:
            f.write("## Untested Files\n\n")
            f.write("The following files are not included in the coverage report:\n\n")
            
            for filename in untested_files:
                f.write(f"- `{filename}`\n")
            
            f.write("\n")
        
        # Uncovered lines
        if uncovered_lines:
            f.write("## Uncovered Lines\n\n")
            
            current_file = None
            for line_data in uncovered_lines:
                filename = line_data["filename"]
                line_num = line_data["line"]
                
                if filename != current_file:
                    if current_file is not None:
                        f.write("\n")
                    
                    f.write(f"### {filename}\n\n")
                    current_file = filename
                    
                    # Get file content
                    file_content = get_file_content(filename)
                    
                f.write(f"- Line {line_num}")
                
                # Show line content if available
                if 0 < line_num <= len(file_content):
                    line_content = file_content[line_num - 1].strip()
                    f.write(f": `{line_content}`")
                
                f.write("\n")
    
    return output_file


def main():
    """Command-line interface for coverage validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage validation tool")
    parser.add_argument("coverage_file", help="Coverage XML file")
    parser.add_argument("--threshold", type=float, default=0.8, help="Coverage threshold (0.0-1.0)")
    parser.add_argument("--source", nargs="+", default=["clarity"], help="Source directories to check")
    parser.add_argument("--output", default="coverage_report.md", help="Output report file")
    
    args = parser.parse_args()
    
    try:
        # Parse coverage data
        coverage_data = parse_coverage_xml(args.coverage_file)
        
        # Find uncovered lines
        uncovered_lines = find_uncovered_lines(coverage_data)
        
        # Validate coverage
        meets_threshold, validation_result = validate_coverage(coverage_data, args.threshold)
        
        # Find untested files
        untested_files = find_untested_files(coverage_data, args.source)
        
        # Generate report
        report_file = generate_coverage_report(
            coverage_data,
            uncovered_lines,
            validation_result,
            untested_files,
            args.output
        )
        
        print(f"Coverage report generated: {report_file}")
        print(f"Overall coverage: {validation_result['coverage_pct']:.1f}%")
        
        if not meets_threshold:
            print(f"❌ Coverage does not meet the threshold of {validation_result['threshold_pct']:.1f}%")
            sys.exit(1)
        else:
            print(f"✅ Coverage meets the threshold of {validation_result['threshold_pct']:.1f}%")
            sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()