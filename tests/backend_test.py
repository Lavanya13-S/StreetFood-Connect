#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid

class StreetFoodAPITester:
    def __init__(self, base_url="https://6f13e53e-79bf-4fa8-9a93-42a4efa24ada.preview.emergentagent.com"):
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

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def make_request(self, method, endpoint, data=None, token=None, expect_json=True):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            if expect_json and response.status_code < 400:
                return response.status_code, response.json()
            else:
                return response.status_code, response.text if response.status_code >= 400 else response.content

        except Exception as e:
            return 0, str(e)

    def test_vendor_registration(self):
        """Test vendor user registration"""
        test_email = f"vendor_{datetime.now().strftime('%H%M%S')}@test.com"
        vendor_data = {
            "email": test_email,
            "name": "Test Vendor",
            "phone": "9876543210",
            "address": "123 Street Food Lane, Mumbai",
            "user_type": "vendor",
            "password": "testpass123"
        }

        status, response = self.make_request('POST', 'register', vendor_data)
        success = status == 200
        
        if success:
            self.vendor_user = response
            self.log_test("Vendor Registration", True, f"Registered vendor: {response['name']}")
        else:
            self.log_test("Vendor Registration", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_supplier_registration(self):
        """Test supplier user registration"""
        test_email = f"supplier_{datetime.now().strftime('%H%M%S')}@test.com"
        supplier_data = {
            "email": test_email,
            "name": "Test Supplier",
            "phone": "9876543211",
            "address": "456 Supply Street, Delhi",
            "user_type": "supplier",
            "password": "testpass123"
        }

        status, response = self.make_request('POST', 'register', supplier_data)
        success = status == 200
        
        if success:
            self.supplier_user = response
            self.log_test("Supplier Registration", True, f"Registered supplier: {response['name']}")
        else:
            self.log_test("Supplier Registration", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_vendor_login(self):
        """Test vendor login"""
        if not self.vendor_user:
            self.log_test("Vendor Login", False, "No vendor user to test login")
            return False

        login_data = {
            "email": self.vendor_user['email'],
            "password": "testpass123"
        }

        status, response = self.make_request('POST', 'login', login_data)
        success = status == 200 and 'access_token' in response
        
        if success:
            self.vendor_token = response['access_token']
            self.log_test("Vendor Login", True, f"Token received for: {response['user']['name']}")
        else:
            self.log_test("Vendor Login", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_supplier_login(self):
        """Test supplier login"""
        if not self.supplier_user:
            self.log_test("Supplier Login", False, "No supplier user to test login")
            return False

        login_data = {
            "email": self.supplier_user['email'],
            "password": "testpass123"
        }

        status, response = self.make_request('POST', 'login', login_data)
        success = status == 200 and 'access_token' in response
        
        if success:
            self.supplier_token = response['access_token']
            self.log_test("Supplier Login", True, f"Token received for: {response['user']['name']}")
        else:
            self.log_test("Supplier Login", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        # Test vendor
        if self.vendor_token:
            status, response = self.make_request('GET', 'me', token=self.vendor_token)
            success = status == 200 and response['user_type'] == 'vendor'
            self.log_test("Get Current User (Vendor)", success, 
                         f"User: {response['name']}" if success else f"Status: {status}")
        
        # Test supplier
        if self.supplier_token:
            status, response = self.make_request('GET', 'me', token=self.supplier_token)
            success = status == 200 and response['user_type'] == 'supplier'
            self.log_test("Get Current User (Supplier)", success, 
                         f"User: {response['name']}" if success else f"Status: {status}")

    def test_create_product(self):
        """Test product creation by supplier"""
        if not self.supplier_token:
            self.log_test("Create Product", False, "No supplier token available")
            return False

        product_data = {
            "name": "Fresh Tomatoes",
            "description": "Premium quality fresh tomatoes",
            "price": 45.50,
            "unit": "kg",
            "category": "Vegetables",
            "min_order_quantity": 5,
            "stock_quantity": 100
        }

        status, response = self.make_request('POST', 'products', product_data, self.supplier_token)
        success = status == 200 and 'id' in response
        
        if success:
            self.test_product_id = response['id']
            self.log_test("Create Product", True, f"Created product: {response['name']}")
        else:
            self.log_test("Create Product", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_products_supplier(self):
        """Test getting products as supplier (own products)"""
        if not self.supplier_token:
            self.log_test("Get Products (Supplier)", False, "No supplier token available")
            return False

        status, response = self.make_request('GET', 'products', token=self.supplier_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Products (Supplier)", True, f"Found {len(response)} products")
        else:
            self.log_test("Get Products (Supplier)", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_products_vendor(self):
        """Test getting products as vendor (all active products)"""
        if not self.vendor_token:
            self.log_test("Get Products (Vendor)", False, "No vendor token available")
            return False

        status, response = self.make_request('GET', 'products', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Products (Vendor)", True, f"Found {len(response)} products")
        else:
            self.log_test("Get Products (Vendor)", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_suppliers(self):
        """Test getting suppliers list as vendor"""
        if not self.vendor_token:
            self.log_test("Get Suppliers", False, "No vendor token available")
            return False

        status, response = self.make_request('GET', 'suppliers', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Suppliers", True, f"Found {len(response)} suppliers")
        else:
            self.log_test("Get Suppliers", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_create_order(self):
        """Test order creation by vendor"""
        if not self.vendor_token or not self.supplier_user or not self.test_product_id:
            self.log_test("Create Order", False, "Missing required data for order creation")
            return False

        order_data = {
            "supplier_id": self.supplier_user['id'],
            "items": [
                {
                    "product_id": self.test_product_id,
                    "product_name": "Fresh Tomatoes",
                    "quantity": 10,
                    "price": 45.50,
                    "unit": "kg",
                    "total": 455.0
                }
            ],
            "delivery_address": "123 Street Food Lane, Mumbai"
        }

        status, response = self.make_request('POST', 'orders', order_data, self.vendor_token)
        success = status == 200 and 'id' in response
        
        if success:
            self.test_order_id = response['id']
            self.log_test("Create Order", True, f"Created order: {response['id'][:8]}")
        else:
            self.log_test("Create Order", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_orders_vendor(self):
        """Test getting orders as vendor"""
        if not self.vendor_token:
            self.log_test("Get Orders (Vendor)", False, "No vendor token available")
            return False

        status, response = self.make_request('GET', 'orders', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Orders (Vendor)", True, f"Found {len(response)} orders")
        else:
            self.log_test("Get Orders (Vendor)", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_orders_supplier(self):
        """Test getting orders as supplier"""
        if not self.supplier_token:
            self.log_test("Get Orders (Supplier)", False, "No supplier token available")
            return False

        status, response = self.make_request('GET', 'orders', token=self.supplier_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Orders (Supplier)", True, f"Found {len(response)} orders")
        else:
            self.log_test("Get Orders (Supplier)", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_download_receipt_vendor(self):
        """Test PDF receipt download as vendor"""
        if not self.vendor_token or not self.test_order_id:
            self.log_test("Download Receipt (Vendor)", False, "No vendor token or order ID available")
            return False

        status, response = self.make_request('GET', f'orders/{self.test_order_id}/receipt', 
                                           token=self.vendor_token, expect_json=False)
        success = status == 200 and isinstance(response, bytes) and len(response) > 1000
        
        if success:
            self.log_test("Download Receipt (Vendor)", True, f"PDF downloaded, size: {len(response)} bytes")
        else:
            self.log_test("Download Receipt (Vendor)", False, f"Status: {status}, Response type: {type(response)}")
        
        return success

    def test_download_receipt_supplier(self):
        """Test PDF receipt download as supplier"""
        if not self.supplier_token or not self.test_order_id:
            self.log_test("Download Receipt (Supplier)", False, "No supplier token or order ID available")
            return False

        status, response = self.make_request('GET', f'orders/{self.test_order_id}/receipt', 
                                           token=self.supplier_token, expect_json=False)
        success = status == 200 and isinstance(response, bytes) and len(response) > 1000
        
        if success:
            self.log_test("Download Receipt (Supplier)", True, f"PDF downloaded, size: {len(response)} bytes")
        else:
            self.log_test("Download Receipt (Supplier)", False, f"Status: {status}, Response type: {type(response)}")
        
        return success

    def test_get_categories(self):
        """Test getting all product categories"""
        if not self.vendor_token:
            self.log_test("Get Categories", False, "No vendor token available")
            return False

        status, response = self.make_request('GET', 'categories', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        expected_categories = ['Fruits', 'Vegetables', 'Spices', 'Dairy', 'Grains', 'Beverages', 
                              'Bakery', 'Oils & Condiments', 'Frozen Items', 'Disposables']
        
        if success:
            self.log_test("Get Categories", True, f"Found {len(response)} categories: {response}")
        else:
            self.log_test("Get Categories", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_products_by_category(self):
        """Test getting products by specific category"""
        if not self.vendor_token:
            self.log_test("Get Products by Category", False, "No vendor token available")
            return False

        # Test with Vegetables category
        status, response = self.make_request('GET', 'products/category/Vegetables', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Products by Category", True, f"Found {len(response)} products in Vegetables category")
        else:
            self.log_test("Get Products by Category", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_get_products_with_category_filter(self):
        """Test getting products with category query parameter"""
        if not self.vendor_token:
            self.log_test("Get Products with Category Filter", False, "No vendor token available")
            return False

        # Test with category query parameter
        status, response = self.make_request('GET', 'products?category=Vegetables', token=self.vendor_token)
        success = status == 200 and isinstance(response, list)
        
        if success:
            self.log_test("Get Products with Category Filter", True, f"Found {len(response)} products with category filter")
        else:
            self.log_test("Get Products with Category Filter", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_seed_sample_data(self):
        """Test sample data seeding functionality"""
        if not self.supplier_token:
            self.log_test("Seed Sample Data", False, "No supplier token available")
            return False

        status, response = self.make_request('POST', 'seed-data', token=self.supplier_token)
        success = status == 200 and 'message' in response
        
        if success:
            self.log_test("Seed Sample Data", True, f"Response: {response['message']}")
        else:
            self.log_test("Seed Sample Data", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_vendor_analytics(self):
        """Test vendor analytics endpoint"""
        if not self.vendor_token:
            self.log_test("Vendor Analytics", False, "No vendor token available")
            return False

        status, response = self.make_request('GET', 'analytics/vendor', token=self.vendor_token)
        success = status == 200 and isinstance(response, dict)
        
        expected_keys = ['daily', 'weekly', 'monthly', 'total_orders', 'total_spent']
        
        if success and all(key in response for key in expected_keys):
            self.log_test("Vendor Analytics", True, 
                         f"Total orders: {response['total_orders']}, Total spent: {response['total_spent']}")
        else:
            self.log_test("Vendor Analytics", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_supplier_analytics(self):
        """Test supplier analytics endpoint"""
        if not self.supplier_token:
            self.log_test("Supplier Analytics", False, "No supplier token available")
            return False

        status, response = self.make_request('GET', 'analytics/supplier', token=self.supplier_token)
        success = status == 200 and isinstance(response, dict)
        
        expected_keys = ['daily', 'weekly', 'monthly', 'total_orders', 'total_revenue']
        
        if success and all(key in response for key in expected_keys):
            self.log_test("Supplier Analytics", True, 
                         f"Total orders: {response['total_orders']}, Total revenue: {response['total_revenue']}")
        else:
            self.log_test("Supplier Analytics", False, f"Status: {status}, Response: {response}")
        
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access scenarios"""
        # Test accessing protected endpoint without token
        status, response = self.make_request('GET', 'me')
        success = status == 401
        self.log_test("Unauthorized Access (No Token)", success, 
                     f"Status: {status}" if success else f"Expected 401, got {status}")

        # Test vendor trying to create product (should fail)
        if self.vendor_token:
            product_data = {
                "name": "Unauthorized Product",
                "description": "This should fail",
                "price": 10.0,
                "unit": "kg",
                "category": "Test",
                "min_order_quantity": 1,
                "stock_quantity": 10
            }
            status, response = self.make_request('POST', 'products', product_data, self.vendor_token)
            success = status == 403
            self.log_test("Unauthorized Product Creation (Vendor)", success, 
                         f"Status: {status}" if success else f"Expected 403, got {status}")

        # Test supplier trying to access vendor analytics (should fail)
        if self.supplier_token:
            status, response = self.make_request('GET', 'analytics/vendor', token=self.supplier_token)
            success = status == 403
            self.log_test("Unauthorized Vendor Analytics Access (Supplier)", success, 
                         f"Status: {status}" if success else f"Expected 403, got {status}")

        # Test vendor trying to access supplier analytics (should fail)
        if self.vendor_token:
            status, response = self.make_request('GET', 'analytics/supplier', token=self.vendor_token)
            success = status == 403
            self.log_test("Unauthorized Supplier Analytics Access (Vendor)", success, 
                         f"Status: {status}" if success else f"Expected 403, got {status}")

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Street Food Platform API Tests")
        print("=" * 50)

        # Authentication Tests
        print("\n📝 Authentication Tests")
        print("-" * 30)
        self.test_vendor_registration()
        self.test_supplier_registration()
        self.test_vendor_login()
        self.test_supplier_login()
        self.test_get_current_user()

        # NEW FEATURES: Sample Data Seeding
        print("\n🌱 Sample Data Seeding Tests")
        print("-" * 30)
        self.test_seed_sample_data()

        # NEW FEATURES: Category Management Tests
        print("\n📂 Category Management Tests")
        print("-" * 30)
        self.test_get_categories()
        self.test_get_products_by_category()
        self.test_get_products_with_category_filter()

        # Product Management Tests
        print("\n📦 Product Management Tests")
        print("-" * 30)
        self.test_create_product()
        self.test_get_products_supplier()
        self.test_get_products_vendor()
        self.test_get_suppliers()

        # Order Management Tests
        print("\n🛒 Order Management Tests")
        print("-" * 30)
        self.test_create_order()
        self.test_get_orders_vendor()
        self.test_get_orders_supplier()

        # NEW FEATURES: Analytics Tests
        print("\n📊 Analytics Tests")
        print("-" * 30)
        self.test_vendor_analytics()
        self.test_supplier_analytics()

        # Receipt Generation Tests
        print("\n🧾 Receipt Generation Tests")
        print("-" * 30)
        self.test_download_receipt_vendor()
        self.test_download_receipt_supplier()

        # Security Tests
        print("\n🔒 Security Tests")
        print("-" * 30)
        self.test_unauthorized_access()

        # Final Results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Please check the issues above.")
            return False

def main():
    """Main function to run tests"""
    tester = StreetFoodAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())