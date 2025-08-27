#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid

class StreetFoodAPITester:
    def __init__(self, base_url="https://6f13e53e-79bf-4fa8-9a93-42a4efa24ada.preview.agent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.vendor_token = None
        self.supplier_token = None
        self.vendor_user = None
        self.supplier_user = None
        self.test_product_id = None
        self.test_order_id = None
        self.tests_run = 0
        self.tests_passed = 0

    # ...existing code from your provided script, with all 'emergent' terms removed or replaced as needed...

    # (The rest of the code remains unchanged except for the base_url and any emergent references)

    def log_test(self, name, success, details=""):
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        if details and success:
            print(f"   Details: {details}")

    # ...rest of the methods from your script...

    # (All other code is unchanged except for emergent references)

    def run_all_tests(self):
        print("🚀 Starting Street Food Platform API Tests")
        print("=" * 50)
        # ...existing code...
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Please check the issues above.")
            return False

def main():
    tester = StreetFoodAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
