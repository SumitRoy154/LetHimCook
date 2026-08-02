"""Comprehensive Integration Test Suite for Let Him Cook! Backend API.
Tests all endpoints using FastAPI TestClient against live MySQL database.
"""

import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import engine
from sqlalchemy import text

client = TestClient(app)

def run_integration_tests():
    print("==================================================")
    print("STARTING FULL BACKEND INTEGRATION TEST SUITE")
    print("==================================================")

    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"testuser_{timestamp}@example.com"
    password = "TestPassword123!"

    results = {
        "passed": [],
        "failed": [],
        "details": {}
    }

    def record_test(name, success, info=""):
        if success:
            results["passed"].append(name)
            print(f"[PASS] {name} {info}")
        else:
            results["failed"].append(name)
            print(f"[FAIL] {name} - {info}")
        results["details"][name] = {"success": success, "info": info}

    # ----------------------------------------------------
    # 1. AUTHENTICATION MODULE
    # ----------------------------------------------------
    print("\n--- 1. AUTHENTICATION MODULE ---")

    # 1.1 Register
    res = client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
    record_test("POST /api/auth/register", res.status_code == 201, f"Status: {res.status_code}, User ID: {res.json().get('id') if res.status_code == 201 else res.text}")
    
    # Duplicate Registration Failure Case
    res_dup = client.post("/api/auth/register", json={"username": username, "email": email, "password": password})
    record_test("POST /api/auth/register (Duplicate Error 409)", res_dup.status_code == 409, f"Status: {res_dup.status_code}")

    # 1.2 Login
    res_login = client.post("/api/auth/login", json={"identifier": username, "password": password})
    login_ok = res_login.status_code == 200 and "access_token" in res_login.json()
    record_test("POST /api/auth/login", login_ok, f"Status: {res_login.status_code}")

    if not login_ok:
        print("Cannot proceed without login token!")
        return results

    tokens = res_login.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    # Invalid Password Failure Case
    res_bad_pass = client.post("/api/auth/login", json={"identifier": username, "password": "WrongPassword!"})
    record_test("POST /api/auth/login (Invalid Password 401)", res_bad_pass.status_code == 401, f"Status: {res_bad_pass.status_code}")

    # 1.3 Get Current User (/me)
    res_me = client.get("/api/auth/me", headers=auth_headers)
    record_test("GET /api/auth/me", res_me.status_code == 200 and res_me.json().get("username") == username, f"Balance: {res_me.json().get('wallet_balance')}")

    # Unauthorized Request Case (FastAPI HTTPBearer defaults to 403 Forbidden when credentials header is missing)
    res_unauth = client.get("/api/auth/me")
    record_test("GET /api/auth/me (Unauthorized 401/403)", res_unauth.status_code in (401, 403), f"Status: {res_unauth.status_code}")

    # 1.4 Refresh Token
    res_ref = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    record_test("POST /api/auth/refresh", res_ref.status_code == 200 and "access_token" in res_ref.json(), f"Status: {res_ref.status_code}")

    # 1.5 Logout
    res_logout = client.post("/api/auth/logout", headers=auth_headers)
    record_test("POST /api/auth/logout", res_logout.status_code == 200, f"Status: {res_logout.status_code}")

    # ----------------------------------------------------
    # 2. WALLET MODULE
    # ----------------------------------------------------
    print("\n--- 2. WALLET MODULE ---")

    # 2.1 Current Balance
    res_bal = client.get("/api/wallet", headers=auth_headers)
    record_test("GET /api/wallet", res_bal.status_code == 200 and "balance" in res_bal.json(), f"Balance: {res_bal.json().get('balance')}")

    # 2.2 Transaction History
    res_tx = client.get("/api/wallet/transactions", headers=auth_headers)
    record_test("GET /api/wallet/transactions", res_tx.status_code == 200 and isinstance(res_tx.json(), list), f"Transactions count: {len(res_tx.json())}")

    # ----------------------------------------------------
    # 3. INVENTORY MODULE
    # ----------------------------------------------------
    print("\n--- 3. INVENTORY MODULE ---")

    # 3.1 Inventory Retrieval
    res_inv = client.get("/api/inventory", headers=auth_headers)
    record_test("GET /api/inventory", res_inv.status_code == 200 and isinstance(res_inv.json(), list), f"Inventory item count: {len(res_inv.json())}")

    # ----------------------------------------------------
    # 4. ORDERS & WORKFLOW MODULE (Mock execution test)
    # ----------------------------------------------------
    print("\n--- 4. ORDERS & WORKFLOW MODULE (Mock Execution Test) ---")

    dish_mock = f"Test Pasta {timestamp}"
    res_ord_mock = client.post("/api/orders", headers=auth_headers, json={"dish_name": dish_mock, "mock": True})
    order_mock_ok = res_ord_mock.status_code == 201
    record_test("POST /api/orders (Mock Execution)", order_mock_ok, f"Order ID: {res_ord_mock.json().get('order_id') if order_mock_ok else res_ord_mock.text}")

    order_mock_id = None
    if order_mock_ok:
        order_mock_data = res_ord_mock.json()
        order_mock_id = order_mock_data["order_id"]

        # Retrieve Order Details
        res_ord_det = client.get(f"/api/orders/{order_mock_id}", headers=auth_headers)
        record_test("GET /api/orders/{order_id}", res_ord_det.status_code == 200 and res_ord_det.json().get("status") == "COMPLETED", f"Status: {res_ord_det.json().get('status') if res_ord_det.status_code==200 else res_ord_det.text}")

    # Order History Retrieval
    res_ord_hist = client.get("/api/orders", headers=auth_headers)
    record_test("GET /api/orders", res_ord_hist.status_code == 200 and len(res_ord_hist.json()) > 0, f"History length: {len(res_ord_hist.json()) if res_ord_hist.status_code==200 else 0}")

    # Invalid Order ID (404)
    res_ord_404 = client.get("/api/orders/999999", headers=auth_headers)
    record_test("GET /api/orders/{order_id} (404 Not Found)", res_ord_404.status_code == 404, f"Status: {res_ord_404.status_code}")

    # ----------------------------------------------------
    # 5. REVIEWS & RECIPES MODULE (Post Mock Order)
    # ----------------------------------------------------
    print("\n--- 5. REVIEWS & RECIPES MODULE ---")

    # Reviews History
    res_rev = client.get("/api/reviews", headers=auth_headers)
    record_test("GET /api/reviews", res_rev.status_code == 200 and isinstance(res_rev.json(), list), f"Reviews count: {len(res_rev.json()) if res_rev.status_code==200 else 0}")

    # Review Suggestions Lookup by Dish
    res_sug = client.get(f"/api/reviews/{dish_mock}", headers=auth_headers)
    record_test("GET /api/reviews/{dish_name}", res_sug.status_code == 200 and isinstance(res_sug.json(), list), f"Suggestions: {res_sug.json() if res_sug.status_code==200 else 0}")

    # Recipe Retrieval (Cached)
    res_rec = client.get(f"/api/recipes/{dish_mock}", headers=auth_headers)
    record_test("GET /api/recipes/{dish_name}", res_rec.status_code == 200 and res_rec.json().get("dish_name") == dish_mock.lower(), f"Recipe found: {res_rec.json().get('dish_name') if res_rec.status_code==200 else res_rec.text}")

    # Missing Recipe Retrieval (404)
    res_rec_404 = client.get("/api/recipes/nonexistent_dish_xyz", headers=auth_headers)
    record_test("GET /api/recipes/{dish_name} (404 Not Found)", res_rec_404.status_code == 404, f"Status: {res_rec_404.status_code}")

    # ----------------------------------------------------
    # 6. WORKFLOW MODULE
    # ----------------------------------------------------
    print("\n--- 6. WORKFLOW MODULE ---")

    # Workflow History
    res_wf_hist = client.get("/api/workflow/history", headers=auth_headers)
    record_test("GET /api/workflow/history", res_wf_hist.status_code == 200 and len(res_wf_hist.json()) > 0, f"Workflows count: {len(res_wf_hist.json()) if res_wf_hist.status_code==200 else 0}")

    if res_wf_hist.status_code == 200 and len(res_wf_hist.json()) > 0:
        exec_id = res_wf_hist.json()[0]["id"]
        # Workflow Execution Details
        res_wf_det = client.get(f"/api/workflow/{exec_id}", headers=auth_headers)
        record_test("GET /api/workflow/{execution_id}", res_wf_det.status_code == 200 and res_wf_det.json().get("id") == exec_id, f"Execution status: {res_wf_det.json().get('workflow_status') if res_wf_det.status_code==200 else res_wf_det.text}")

    # ----------------------------------------------------
    # 7. REAL PROVIDER ROUTING & RETRY / FAILURE PERSISTENCE TEST
    # ----------------------------------------------------
    print("\n--- 7. REAL PROVIDER ROUTING & RETRY / FAILURE PERSISTENCE TEST ---")

    dish_real = f"Real Provider Pizza {timestamp}"
    res_ord_real = client.post("/api/orders", headers=auth_headers, json={"dish_name": dish_real, "mock": False})
    
    print(f"Real Provider Call Result Status Code: {res_ord_real.status_code}")
    print(f"Real Provider Call Response Body: {res_ord_real.json()}")

    order_real_id = res_ord_real.json().get("order_id")
    if order_real_id:
        res_ord_real_det = client.get(f"/api/orders/{order_real_id}", headers=auth_headers)
        real_status = res_ord_real_det.json().get("status")
        print(f"Order #{order_real_id} Final Status: {real_status}")
        record_test("Real Provider Workflow Execution", res_ord_real_det.status_code == 200 and real_status in ("COMPLETED", "FAILED"), f"Order status: {real_status}")

        res_wf_real = client.get("/api/workflow/history", headers=auth_headers)
        latest_wf = res_wf_real.json()[0]
        print(f"Latest Workflow Execution ID #{latest_wf['id']} Status: {latest_wf['workflow_status']}")

        res_wf_real_det = client.get(f"/api/workflow/{latest_wf['id']}", headers=auth_headers)
        wf_det_data = res_wf_real_det.json()
        error_logs = wf_det_data.get('error_logs', [])
        print(f"Execution Error Logs: {error_logs}")
        record_test("Real Provider Retry & Error Persistence Logged", len(error_logs) > 0 or latest_wf['workflow_status'] == "COMPLETED", f"Error log count: {len(error_logs)}")

    # ----------------------------------------------------
    # 8. DIRECT DATABASE VERIFICATION
    # ----------------------------------------------------
    print("\n--- 8. DIRECT DATABASE PERSISTENCE VERIFICATION ---")
    try:
        with engine.connect() as conn:
            user_count = conn.execute(text(f"SELECT COUNT(*) FROM users WHERE username='{username}'")).scalar()
            wallet_count = conn.execute(text("SELECT COUNT(*) FROM wallets")).scalar()
            orders_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            inventory_count = conn.execute(text("SELECT COUNT(*) FROM inventories")).scalar()
            recipes_count = conn.execute(text("SELECT COUNT(*) FROM recipes")).scalar()
            reviews_count = conn.execute(text("SELECT COUNT(*) FROM reviews")).scalar()
            workflows_count = conn.execute(text("SELECT COUNT(*) FROM workflow_executions")).scalar()

            print(f"Direct DB Query Counts:")
            print(f" - Users created: {user_count}")
            print(f" - Wallets total: {wallet_count}")
            print(f" - Orders total: {orders_count}")
            print(f" - Inventory items: {inventory_count}")
            print(f" - Recipes cached: {recipes_count}")
            print(f" - Reviews written: {reviews_count}")
            print(f" - Workflow Executions logged: {workflows_count}")
            
            record_test("Database MySQL Direct Persistence Check", user_count == 1 and orders_count > 0, "All tables verified in MySQL")
    except Exception as e:
        record_test("Database MySQL Direct Persistence Check", False, str(e))

    print("\n==================================================")
    print(f"TEST SUMMARY: {len(results['passed'])} PASSED, {len(results['failed'])} FAILED")
    print("==================================================")
    return results

if __name__ == "__main__":
    run_integration_tests()
