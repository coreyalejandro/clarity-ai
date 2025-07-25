"""
Test monitoring and maintenance utilities.

These utilities help track test health, detect flaky tests,
and analyze test results over time.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET


class TestResultTracker:
    """Track and analyze test results over time."""
    
    def __init__(self, results_dir: str = ".test_results"):
        """Initialize the tracker with a directory for storing results."""
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def save_test_results(self, results_file: str, run_id: Optional[str] = None) -> str:
        """Save test results from JUnit XML to a JSON file with metadata."""
        if not os.path.exists(results_file):
            raise FileNotFoundError(f"Results file not found: {results_file}")
        
        # Parse XML results
        tree = ET.parse(results_file)
        root = tree.getroot()
        
        # Extract test data
        test_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "run_id": run_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error": 0,
                "time": 0.0
            },
            "tests": []
        }
        
        # Process test suites
        for testsuite in root.findall(".//testsuite"):
            suite_name = testsuite.get("name", "unknown")
            
            # Update summary
            test_data["summary"]["total"] += int(testsuite.get("tests", 0))
            test_data["summary"]["passed"] += int(testsuite.get("passed", 0))
            test_data["summary"]["failed"] += int(testsuite.get("failures", 0))
            test_data["summary"]["skipped"] += int(testsuite.get("skipped", 0))
            test_data["summary"]["error"] += int(testsuite.get("errors", 0))
            test_data["summary"]["time"] += float(testsuite.get("time", 0))
            
            # Process test cases
            for testcase in testsuite.findall(".//testcase"):
                case_name = testcase.get("name", "unknown")
                class_name = testcase.get("classname", "unknown")
                time = float(testcase.get("time", 0))
                
                # Determine status
                status = "passed"
                message = ""
                
                if testcase.find("failure") is not None:
                    status = "failed"
                    failure = testcase.find("failure")
                    message = failure.get("message", "") if failure is not None else ""
                
                elif testcase.find("error") is not None:
                    status = "error"
                    error = testcase.find("error")
                    message = error.get("message", "") if error is not None else ""
                
                elif testcase.find("skipped") is not None:
                    status = "skipped"
                    skipped = testcase.find("skipped")
                    message = skipped.get("message", "") if skipped is not None else ""
                
                # Add test case data
                test_data["tests"].append({
                    "name": case_name,
                    "class": class_name,
                    "suite": suite_name,
                    "status": status,
                    "message": message,
                    "time": time
                })
        
        # Save to JSON file
        output_file = os.path.join(
            self.results_dir, 
            f"results_{test_data['run_id']}.json"
        )
        
        with open(output_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        return output_file
    
    def detect_flaky_tests(self, min_runs: int = 3, flaky_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """Detect potentially flaky tests based on historical results."""
        # Load all result files
        result_files = [
            os.path.join(self.results_dir, f)
            for f in os.listdir(self.results_dir)
            if f.startswith("results_") and f.endswith(".json")
        ]
        
        if not result_files:
            return []
        
        # Collect test results by test ID
        test_results = {}
        
        for result_file in result_files:
            with open(result_file, 'r') as f:
                data = json.load(f)
                
                for test in data["tests"]:
                    test_id = f"{test['class']}::{test['name']}"
                    
                    if test_id not in test_results:
                        test_results[test_id] = []
                    
                    test_results[test_id].append({
                        "run_id": data["run_id"],
                        "timestamp": data["timestamp"],
                        "status": test["status"],
                        "time": test["time"]
                    })
        
        # Analyze for flakiness
        flaky_tests = []
        
        for test_id, results in test_results.items():
            if len(results) < min_runs:
                continue
            
            # Count status occurrences
            status_counts = {}
            for result in results:
                status = result["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate flakiness score
            total_runs = len(results)
            if "passed" in status_counts and "failed" in status_counts:
                minority_status = min(status_counts["passed"], status_counts["failed"])
                flakiness_score = minority_status / total_runs
                
                if flakiness_score >= flaky_threshold:
                    class_name, test_name = test_id.split("::")
                    flaky_tests.append({
                        "test_id": test_id,
                        "class": class_name,
                        "name": test_name,
                        "flakiness_score": flakiness_score,
                        "total_runs": total_runs,
                        "passed": status_counts.get("passed", 0),
                        "failed": status_counts.get("failed", 0),
                        "skipped": status_counts.get("skipped", 0),
                        "error": status_counts.get("error", 0)
                    })
        
        # Sort by flakiness score (most flaky first)
        flaky_tests.sort(key=lambda x: x["flakiness_score"], reverse=True)
        
        return flaky_tests
    
    def generate_test_report(self, output_file: str = "test_report.md") -> str:
        """Generate a markdown report of test results and health."""
        # Load all result files
        result_files = [
            os.path.join(self.results_dir, f)
            for f in os.listdir(self.results_dir)
            if f.startswith("results_") and f.endswith(".json")
        ]
        
        if not result_files:
            with open(output_file, 'w') as f:
                f.write("# Test Report\n\nNo test results found.\n")
            return output_file
        
        # Sort by timestamp (newest first)
        result_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        
        # Load latest results
        with open(result_files[0], 'r') as f:
            latest_data = json.load(f)
        
        # Detect flaky tests
        flaky_tests = self.detect_flaky_tests()
        
        # Generate report
        with open(output_file, 'w') as f:
            f.write("# ClarityAI Test Report\n\n")
            
            # Latest run summary
            f.write(f"## Latest Test Run\n\n")
            f.write(f"- **Run ID**: {latest_data['run_id']}\n")
            f.write(f"- **Timestamp**: {latest_data['timestamp']}\n")
            f.write(f"- **Total Tests**: {latest_data['summary']['total']}\n")
            f.write(f"- **Passed**: {latest_data['summary']['passed']}\n")
            f.write(f"- **Failed**: {latest_data['summary']['failed']}\n")
            f.write(f"- **Skipped**: {latest_data['summary']['skipped']}\n")
            f.write(f"- **Errors**: {latest_data['summary']['error']}\n")
            f.write(f"- **Total Time**: {latest_data['summary']['time']:.2f} seconds\n\n")
            
            # Test health
            pass_rate = 0
            if latest_data['summary']['total'] > 0:
                pass_rate = latest_data['summary']['passed'] / latest_data['summary']['total'] * 100
            
            f.write(f"## Test Health\n\n")
            f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n")
            f.write(f"- **Total Test Runs**: {len(result_files)}\n")
            f.write(f"- **Flaky Tests**: {len(flaky_tests)}\n\n")
            
            # Failed tests
            failed_tests = [
                test for test in latest_data["tests"]
                if test["status"] in ["failed", "error"]
            ]
            
            if failed_tests:
                f.write(f"## Failed Tests\n\n")
                for test in failed_tests:
                    f.write(f"### {test['class']}::{test['name']}\n\n")
                    f.write(f"- **Status**: {test['status']}\n")
                    f.write(f"- **Message**: {test['message']}\n")
                    f.write(f"- **Time**: {test['time']:.3f} seconds\n\n")
            
            # Flaky tests
            if flaky_tests:
                f.write(f"## Flaky Tests\n\n")
                for test in flaky_tests:
                    f.write(f"### {test['test_id']}\n\n")
                    f.write(f"- **Flakiness Score**: {test['flakiness_score']:.2f}\n")
                    f.write(f"- **Total Runs**: {test['total_runs']}\n")
                    f.write(f"- **Passed**: {test['passed']}\n")
                    f.write(f"- **Failed**: {test['failed']}\n\n")
            
            # Slow tests
            slow_tests = sorted(
                latest_data["tests"],
                key=lambda x: x["time"],
                reverse=True
            )[:5]
            
            if slow_tests:
                f.write(f"## Slowest Tests\n\n")
                for test in slow_tests:
                    f.write(f"- **{test['class']}::{test['name']}**: {test['time']:.3f} seconds\n")
        
        return output_file


def main():
    """Command-line interface for test monitoring tools."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test monitoring and maintenance tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Track results command
    track_parser = subparsers.add_parser("track", help="Track test results")
    track_parser.add_argument("results_file", help="JUnit XML results file")
    track_parser.add_argument("--run-id", help="Optional run ID")
    track_parser.add_argument("--results-dir", default=".test_results", help="Results directory")
    
    # Detect flaky tests command
    flaky_parser = subparsers.add_parser("flaky", help="Detect flaky tests")
    flaky_parser.add_argument("--min-runs", type=int, default=3, help="Minimum runs to consider")
    flaky_parser.add_argument("--threshold", type=float, default=0.2, help="Flakiness threshold")
    flaky_parser.add_argument("--results-dir", default=".test_results", help="Results directory")
    
    # Generate report command
    report_parser = subparsers.add_parser("report", help="Generate test report")
    report_parser.add_argument("--output", default="test_report.md", help="Output file")
    report_parser.add_argument("--results-dir", default=".test_results", help="Results directory")
    
    args = parser.parse_args()
    
    if args.command == "track":
        tracker = TestResultTracker(args.results_dir)
        output_file = tracker.save_test_results(args.results_file, args.run_id)
        print(f"Test results saved to: {output_file}")
    
    elif args.command == "flaky":
        tracker = TestResultTracker(args.results_dir)
        flaky_tests = tracker.detect_flaky_tests(args.min_runs, args.threshold)
        
        if flaky_tests:
            print(f"Detected {len(flaky_tests)} potentially flaky tests:")
            for test in flaky_tests:
                print(f"- {test['test_id']}: {test['flakiness_score']:.2f} " +
                      f"({test['passed']} passed, {test['failed']} failed)")
        else:
            print("No flaky tests detected.")
    
    elif args.command == "report":
        tracker = TestResultTracker(args.results_dir)
        output_file = tracker.generate_test_report(args.output)
        print(f"Test report generated: {output_file}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()