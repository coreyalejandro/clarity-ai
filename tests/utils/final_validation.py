#!/usr/bin/env python3
"""
Final integration testing and validation script.

This script performs a comprehensive validation of the entire project,
including running tests, checking coverage, validating CI configuration,
and verifying documentation.
"""

import os
import sys
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Tuple

# Import validation modules if available
try:
    from coverage_validator import parse_coverage_xml, validate_coverage
    from ci_validator import validate_workflow
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False


def run_command(command: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
        universal_newlines=True
    )
    
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def run_tests(pytest_args: List[str] = None) -> Dict[str, Any]:
    """Run the test suite and return results."""
    if pytest_args is None:
        pytest_args = ["--cov=clarity", "--cov-report=xml"]
    
    command = ["pytest"] + pytest_args
    
    start_time = time.time()
    exit_code, stdout, stderr = run_command(command)
    end_time = time.time()
    
    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "duration": end_time - start_time
    }


def check_coverage(coverage_file: str = "coverage.xml", threshold: float = 0.8) -> Dict[str, Any]:
    """Check test coverage against threshold."""
    if not os.path.exists(coverage_file):
        return {
            "success": False,
            "error": f"Coverage file not found: {coverage_file}"
        }
    
    if MODULES_AVAILABLE:
        try:
            coverage_data = parse_coverage_xml(coverage_file)
            meets_threshold, validation_result = validate_coverage(coverage_data, threshold)
            
            return {
                "success": meets_threshold,
                "coverage": validation_result["coverage_pct"],
                "threshold": validation_result["threshold_pct"],
                "lines_covered": validation_result["lines_covered"],
                "lines_valid": validation_result["lines_valid"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    else:
        # Fallback to simpler check
        command = ["coverage", "report", "--fail-under", str(int(threshold * 100))]
        exit_code, stdout, stderr = run_command(command)
        
        return {
            "success": exit_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }


def check_ci_config(workflow_file: str = ".github/workflows/ci.yml") -> Dict[str, Any]:
    """Check CI configuration."""
    if not os.path.exists(workflow_file):
        return {
            "success": False,
            "error": f"Workflow file not found: {workflow_file}"
        }
    
    if MODULES_AVAILABLE:
        try:
            issues = validate_workflow(workflow_file)
            
            return {
                "success": len(issues) == 0,
                "issues": issues
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    else:
        # Fallback to basic YAML validation
        command = ["python", "-c", "import yaml; yaml.safe_load(open('" + workflow_file + "'))"]
        exit_code, stdout, stderr = run_command(command)
        
        return {
            "success": exit_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }


def check_documentation() -> Dict[str, Any]:
    """Check documentation files."""
    required_docs = [
        "README.md",
        "tests/README.md"
    ]
    
    missing_docs = [doc for doc in required_docs if not os.path.exists(doc)]
    
    return {
        "success": len(missing_docs) == 0,
        "missing": missing_docs,
        "found": [doc for doc in required_docs if os.path.exists(doc)]
    }


def check_performance() -> Dict[str, Any]:
    """Run performance tests."""
    command = ["pytest", "tests/performance", "-v", "-m", "performance"]
    
    start_time = time.time()
    exit_code, stdout, stderr = run_command(command)
    end_time = time.time()
    
    return {
        "success": exit_code == 0,
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "duration": end_time - start_time
    }


def generate_validation_report(
    results: Dict[str, Any],
    output_file: str = "validation_report.md"
) -> str:
    """Generate a markdown report of validation results."""
    with open(output_file, 'w') as f:
        f.write("# Final Validation Report\n\n")
        
        # Overall status
        all_success = all(results[key]["success"] for key in results)
        
        if all_success:
            f.write("## ✅ All Validations Passed\n\n")
        else:
            f.write("## ❌ Some Validations Failed\n\n")
        
        # Test results
        f.write("## Test Results\n\n")
        test_results = results.get("tests", {})
        
        if test_results.get("success", False):
            f.write("✅ **Tests passed**\n\n")
        else:
            f.write("❌ **Tests failed**\n\n")
        
        f.write(f"- Duration: {test_results.get('duration', 0):.2f} seconds\n")
        f.write(f"- Exit code: {test_results.get('exit_code', 'N/A')}\n\n")
        
        # Coverage results
        f.write("## Coverage Results\n\n")
        coverage_results = results.get("coverage", {})
        
        if coverage_results.get("success", False):
            f.write("✅ **Coverage meets threshold**\n\n")
        else:
            f.write("❌ **Coverage below threshold**\n\n")
        
        if "error" in coverage_results:
            f.write(f"Error: {coverage_results['error']}\n\n")
        else:
            f.write(f"- Coverage: {coverage_results.get('coverage', 'N/A')}%\n")
            f.write(f"- Threshold: {coverage_results.get('threshold', 'N/A')}%\n")
            f.write(f"- Lines covered: {coverage_results.get('lines_covered', 'N/A')}\n")
            f.write(f"- Lines valid: {coverage_results.get('lines_valid', 'N/A')}\n\n")
        
        # CI configuration
        f.write("## CI Configuration\n\n")
        ci_results = results.get("ci", {})
        
        if ci_results.get("success", False):
            f.write("✅ **CI configuration valid**\n\n")
        else:
            f.write("❌ **CI configuration issues found**\n\n")
        
        if "error" in ci_results:
            f.write(f"Error: {ci_results['error']}\n\n")
        elif "issues" in ci_results:
            issues = ci_results["issues"]
            if issues:
                f.write(f"Found {len(issues)} issues:\n\n")
                for issue in issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
        
        # Documentation
        f.write("## Documentation\n\n")
        doc_results = results.get("documentation", {})
        
        if doc_results.get("success", False):
            f.write("✅ **Documentation complete**\n\n")
        else:
            f.write("❌ **Documentation incomplete**\n\n")
        
        if doc_results.get("missing"):
            f.write("Missing documentation files:\n\n")
            for doc in doc_results["missing"]:
                f.write(f"- {doc}\n")
            f.write("\n")
        
        # Performance
        f.write("## Performance Tests\n\n")
        perf_results = results.get("performance", {})
        
        if perf_results.get("success", False):
            f.write("✅ **Performance tests passed**\n\n")
        else:
            f.write("❌ **Performance tests failed**\n\n")
        
        f.write(f"- Duration: {perf_results.get('duration', 0):.2f} seconds\n")
        f.write(f"- Exit code: {perf_results.get('exit_code', 'N/A')}\n\n")
        
        # Summary
        f.write("## Summary\n\n")
        f.write("| Validation | Status |\n")
        f.write("|------------|--------|\n")
        
        for key, result in results.items():
            status = "✅ Passed" if result.get("success", False) else "❌ Failed"
            f.write(f"| {key.capitalize()} | {status} |\n")
    
    return output_file


def main():
    """Command-line interface for final validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Final validation tool")
    parser.add_argument("--output", default="validation_report.md", help="Output report file")
    parser.add_argument("--coverage-threshold", type=float, default=0.8, help="Coverage threshold (0.0-1.0)")
    parser.add_argument("--skip-performance", action="store_true", help="Skip performance tests")
    
    args = parser.parse_args()
    
    try:
        results = {}
        
        # Run tests
        print("Running tests...")
        results["tests"] = run_tests()
        
        # Check coverage
        print("Checking coverage...")
        results["coverage"] = check_coverage(threshold=args.coverage_threshold)
        
        # Check CI configuration
        print("Validating CI configuration...")
        results["ci"] = check_ci_config()
        
        # Check documentation
        print("Checking documentation...")
        results["documentation"] = check_documentation()
        
        # Run performance tests
        if not args.skip_performance:
            print("Running performance tests...")
            results["performance"] = check_performance()
        
        # Generate report
        report_file = generate_validation_report(results, args.output)
        print(f"Validation report generated: {report_file}")
        
        # Determine exit code
        all_success = all(results[key]["success"] for key in results)
        
        if all_success:
            print("✅ All validations passed!")
            sys.exit(0)
        else:
            print("❌ Some validations failed. See report for details.")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()