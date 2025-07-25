#!/usr/bin/env python3
"""
CI pipeline validation script.

This script validates the GitHub Actions CI pipeline configuration,
checks for common issues, and ensures all required jobs are present.
"""

import os
import sys
import yaml
from typing import Dict, List, Any, Set


def load_workflow_file(workflow_file: str) -> Dict[str, Any]:
    """Load a GitHub Actions workflow file."""
    if not os.path.exists(workflow_file):
        raise FileNotFoundError(f"Workflow file not found: {workflow_file}")
    
    with open(workflow_file, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in workflow file: {e}")


def validate_workflow_structure(workflow: Dict[str, Any]) -> List[str]:
    """Validate the basic structure of a workflow file."""
    issues = []
    
    # Check required fields
    if "name" not in workflow:
        issues.append("Missing 'name' field in workflow")
    
    if "on" not in workflow:
        issues.append("Missing 'on' field in workflow")
    
    if "jobs" not in workflow:
        issues.append("Missing 'jobs' field in workflow")
    elif not workflow["jobs"]:
        issues.append("No jobs defined in workflow")
    
    return issues


def validate_trigger_events(workflow: Dict[str, Any]) -> List[str]:
    """Validate the trigger events in a workflow."""
    issues = []
    
    # Check trigger events
    on_events = workflow.get("on", {})
    
    if not on_events:
        issues.append("No trigger events defined")
    
    # Common events to check for
    common_events = ["push", "pull_request"]
    found_events = set()
    
    if isinstance(on_events, list):
        found_events = set(on_events)
    elif isinstance(on_events, dict):
        found_events = set(on_events.keys())
    
    # Check for common events
    for event in common_events:
        if event not in found_events:
            issues.append(f"Common event '{event}' not configured")
    
    return issues


def validate_jobs(workflow: Dict[str, Any]) -> List[str]:
    """Validate the jobs in a workflow."""
    issues = []
    
    jobs = workflow.get("jobs", {})
    
    if not jobs:
        return ["No jobs defined"]
    
    # Check each job
    for job_id, job in jobs.items():
        # Check required fields
        if "runs-on" not in job:
            issues.append(f"Job '{job_id}' is missing 'runs-on' field")
        
        if "steps" not in job:
            issues.append(f"Job '{job_id}' is missing 'steps' field")
        elif not job["steps"]:
            issues.append(f"Job '{job_id}' has no steps")
        
        # Check for checkout step
        has_checkout = False
        for step in job.get("steps", []):
            if step.get("uses", "").startswith("actions/checkout"):
                has_checkout = True
                break
        
        if not has_checkout:
            issues.append(f"Job '{job_id}' is missing checkout step")
    
    return issues


def validate_matrix_strategy(workflow: Dict[str, Any]) -> List[str]:
    """Validate matrix strategy configuration."""
    issues = []
    
    jobs = workflow.get("jobs", {})
    
    for job_id, job in jobs.items():
        strategy = job.get("strategy", {})
        matrix = strategy.get("matrix", {})
        
        if matrix:
            # Check for Python versions
            python_versions = matrix.get("python-version", [])
            if not python_versions:
                issues.append(f"Job '{job_id}' has matrix strategy but no Python versions")
            elif len(python_versions) < 2:
                issues.append(f"Job '{job_id}' should test multiple Python versions")
            
            # Check fail-fast setting
            if strategy.get("fail-fast", True):
                issues.append(f"Job '{job_id}' has fail-fast enabled, which may stop all matrix jobs on failure")
    
    return issues


def validate_test_job(workflow: Dict[str, Any]) -> List[str]:
    """Validate the test job configuration."""
    issues = []
    
    jobs = workflow.get("jobs", {})
    
    # Find test job
    test_job = None
    test_job_id = None
    
    for job_id, job in jobs.items():
        if "test" in job_id.lower():
            test_job = job
            test_job_id = job_id
            break
    
    if not test_job:
        return ["No test job found"]
    
    # Check for pytest step
    has_pytest = False
    for step in test_job.get("steps", []):
        if step.get("name", "").lower().startswith("test") or "pytest" in str(step).lower():
            has_pytest = True
            break
    
    if not has_pytest:
        issues.append(f"Test job '{test_job_id}' is missing pytest step")
    
    # Check for coverage
    has_coverage = False
    for step in test_job.get("steps", []):
        if "cov" in str(step).lower() or "coverage" in str(step).lower():
            has_coverage = True
            break
    
    if not has_coverage:
        issues.append(f"Test job '{test_job_id}' is missing coverage step")
    
    return issues


def validate_artifact_upload(workflow: Dict[str, Any]) -> List[str]:
    """Validate artifact upload steps."""
    issues = []
    
    jobs = workflow.get("jobs", {})
    
    for job_id, job in jobs.items():
        has_artifact_upload = False
        
        for step in job.get("steps", []):
            if step.get("uses", "").startswith("actions/upload-artifact"):
                has_artifact_upload = True
                
                # Check for required fields
                if "name" not in step.get("with", {}):
                    issues.append(f"Job '{job_id}' has artifact upload without name")
                
                if "path" not in step.get("with", {}):
                    issues.append(f"Job '{job_id}' has artifact upload without path")
        
        # Only flag missing artifact upload for build jobs
        if "build" in job_id.lower() and not has_artifact_upload:
            issues.append(f"Build job '{job_id}' is missing artifact upload step")
    
    return issues


def validate_workflow(workflow_file: str) -> List[str]:
    """Validate a GitHub Actions workflow file."""
    try:
        workflow = load_workflow_file(workflow_file)
        
        issues = []
        issues.extend(validate_workflow_structure(workflow))
        issues.extend(validate_trigger_events(workflow))
        issues.extend(validate_jobs(workflow))
        issues.extend(validate_matrix_strategy(workflow))
        issues.extend(validate_test_job(workflow))
        issues.extend(validate_artifact_upload(workflow))
        
        return issues
    
    except Exception as e:
        return [f"Error validating workflow: {e}"]


def generate_validation_report(
    workflow_file: str,
    issues: List[str],
    output_file: str = "ci_validation_report.md"
) -> str:
    """Generate a markdown report of CI validation results."""
    with open(output_file, 'w') as f:
        f.write("# CI Pipeline Validation Report\n\n")
        
        f.write(f"## Workflow File\n\n")
        f.write(f"- **File**: `{workflow_file}`\n\n")
        
        if issues:
            f.write(f"## Issues Found ({len(issues)})\n\n")
            
            for i, issue in enumerate(issues, 1):
                f.write(f"{i}. {issue}\n")
            
            f.write("\n")
            f.write("❌ **Validation failed**\n\n")
        else:
            f.write("✅ **No issues found**\n\n")
            f.write("The CI pipeline configuration looks good!\n\n")
        
        f.write("## Recommendations\n\n")
        f.write("- Ensure all tests are run in the CI pipeline\n")
        f.write("- Configure coverage reporting and thresholds\n")
        f.write("- Set up notifications for failed builds\n")
        f.write("- Consider adding performance benchmarks\n")
        f.write("- Add code quality checks (linting, type checking)\n")
    
    return output_file


def main():
    """Command-line interface for CI validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CI pipeline validation tool")
    parser.add_argument("workflow_file", help="GitHub Actions workflow file")
    parser.add_argument("--output", default="ci_validation_report.md", help="Output report file")
    
    args = parser.parse_args()
    
    try:
        # Validate workflow
        issues = validate_workflow(args.workflow_file)
        
        # Generate report
        report_file = generate_validation_report(
            args.workflow_file,
            issues,
            args.output
        )
        
        print(f"CI validation report generated: {report_file}")
        
        if issues:
            print(f"❌ Found {len(issues)} issues in CI configuration")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            print("✅ CI configuration looks good!")
            sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()