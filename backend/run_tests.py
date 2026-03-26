#!/usr/bin/env python3
"""
Script to run all tests with coverage report
"""
import subprocess
import sys


def run_tests():
    """Run pytest with coverage"""
    print("=" * 80)
    print("🧪 Running Ricoh Suite Backend Tests")
    print("=" * 80)
    print()
    
    # Install test dependencies
    print("📦 Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements_test.txt"])
    print("✅ Dependencies installed")
    print()
    
    # Run unit tests
    print("🔬 Running unit tests...")
    result_unit = subprocess.run([
        sys.executable, "-m", "pytest",
        "-v",
        "-m", "unit",
        "--tb=short"
    ])
    print()
    
    # Run integration tests
    print("🔗 Running integration tests...")
    result_integration = subprocess.run([
        sys.executable, "-m", "pytest",
        "-v",
        "-m", "integration",
        "--tb=short"
    ])
    print()
    
    # Run all tests with coverage
    print("📊 Running all tests with coverage...")
    result_coverage = subprocess.run([
        sys.executable, "-m", "pytest",
        "-v",
        "--cov=services",
        "--cov=api",
        "--cov=middleware",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--tb=short"
    ])
    print()
    
    print("=" * 80)
    if result_coverage.returncode == 0:
        print("✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed")
        sys.exit(1)
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
