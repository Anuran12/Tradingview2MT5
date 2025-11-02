#!/usr/bin/env python3
"""
Test script for TradingView to MT5 Automated Trading System
Validates all components and their integration
"""

import os
import time
import requests
import json
import sys
from datetime import datetime

def test_mt5_bridge():
    """Test MT5 Bridge service"""
    print("🔍 Testing MT5 Bridge Service...")

    base_url = "http://localhost:5000"

    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")

            if health_data.get('mt5_connected'):
                print("✅ MT5 connection: Connected")
            else:
                print("❌ MT5 connection: Disconnected")
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False

        # Test account endpoint
        response = requests.get(f"{base_url}/account", timeout=10)
        if response.status_code == 200:
            account_data = response.json()
            print(f"✅ Account info retrieved: Balance ${account_data.get('balance', 'N/A')}")
        else:
            print(f"❌ Account info failed: HTTP {response.status_code}")

        # Test positions endpoint
        response = requests.get(f"{base_url}/positions", timeout=10)
        if response.status_code == 200:
            positions_data = response.json()
            positions_count = len(positions_data.get('positions', []))
            print(f"✅ Positions retrieved: {positions_count} open positions")
        else:
            print(f"❌ Positions check failed: HTTP {response.status_code}")

        # Test symbol endpoint
        response = requests.get(f"{base_url}/symbol/EURUSD", timeout=10)
        if response.status_code == 200:
            symbol_data = response.json()
            print(f"✅ Symbol info retrieved: EURUSD @ {symbol_data.get('bid', 'N/A')}/{symbol_data.get('ask', 'N/A')}")
        else:
            print(f"❌ Symbol info failed: HTTP {response.status_code}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ MT5 Bridge test failed: {str(e)}")
        return False

def test_n8n_service():
    """Test n8n service"""
    print("\n🔍 Testing n8n Service...")

    try:
        response = requests.get("http://localhost:5678/healthz", timeout=10)
        if response.status_code == 200:
            print("✅ n8n health check passed")
            return True
        else:
            print(f"❌ n8n health check failed: HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ n8n test failed: {str(e)}")
        return False

def test_webhook_flow():
    """Test webhook flow end-to-end"""
    print("\n🔍 Testing Webhook Flow...")

    # Test payload
    test_payload = {
        "signal": "BUY",
        "symbol": "EURUSD",
        "lot_size": 0.01,
        "sl_percent": 1.0,
        "tp_percent": 2.0,
        "timestamp": datetime.now().isoformat()
    }

    try:
        # Send test webhook to n8n (this would normally come from TradingView)
        # Note: This test assumes the n8n workflow is set up and active
        response = requests.post(
            "http://localhost:5678/webhook/tradingview-webhook",
            json=test_payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook test successful: {result}")
            return True
        else:
            print(f"❌ Webhook test failed: HTTP {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook test failed: {str(e)}")
        print("   Note: Make sure n8n workflow is active and webhook URL is correct")
        return False

def test_docker_services():
    """Test Docker services status"""
    print("\n🔍 Testing Docker Services...")

    try:
        import subprocess
        result = subprocess.run(
            ["docker-compose", "ps"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Header + at least one service
                print("✅ Docker services are running")
                # Print service status
                for line in lines[1:]:
                    if line.strip():
                        print(f"   {line}")
                return True
            else:
                print("❌ No Docker services found")
                return False
        else:
            print(f"❌ Docker status check failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Docker test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 TradingView to MT5 System Test Suite")
    print("=" * 50)

    test_results = []

    # Test Docker services first
    test_results.append(("Docker Services", test_docker_services()))

    # Wait a bit for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(5)

    # Test individual services
    test_results.append(("n8n Service", test_n8n_service()))
    test_results.append(("MT5 Bridge", test_mt5_bridge()))
    test_results.append(("Webhook Flow", test_webhook_flow()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
