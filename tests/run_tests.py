#!/usr/bin/env python3
"""
Test Runner for Weather MCP Server
Runs all tests in the correct order
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def run_all_tests():
    """Run all test suites"""
    print("🧪 Weather MCP Server Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Integration Tests
    print("\n1️⃣ Running Integration Tests...")
    try:
        from test_integration import WeatherIntegrationTest
        integration_test = WeatherIntegrationTest()
        await integration_test.run_all_tests()
        test_results.append(("Integration Tests", "✅ PASSED"))
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        test_results.append(("Integration Tests", f"❌ FAILED: {e}"))
    
    # Test 2: Deployment Tests
    print("\n2️⃣ Running Deployment Tests...")
    try:
        from test_deployment import test_deployment
        await test_deployment()
        test_results.append(("Deployment Tests", "✅ PASSED"))
    except Exception as e:
        print(f"❌ Deployment tests failed: {e}")
        test_results.append(("Deployment Tests", f"❌ FAILED: {e}"))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 40)
    passed = 0
    for test_name, result in test_results:
        print(f"{result}: {test_name}")
        if "PASSED" in result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(test_results)} test suites passed")
    
    if passed == len(test_results):
        print("🎉 All tests passed! System is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)