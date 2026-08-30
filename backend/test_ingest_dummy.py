"""
DUMMY INGEST TEST — Kartike ye chalao server start hone ke baad.
Poora output (script ka print + terminal ka server-log dono) paste karna,
sirf "PASS/FAIL" summary nahi — agar kuch fail ho, uska poora traceback
zaroori hai debug ke liye.

Run: python3 test_ingest_dummy.py
Requires: pip install requests --break-system-packages
"""

import requests
import json
import sys
import time
import uuid

BASE_URL = "http://localhost:8000"  # badlo agar tumhara port/host alag hai


def check(label, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status} — {label}" + (f" ({detail})" if detail else ""))
    return condition


def run_test(complaint_payload, test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    print("Sending payload:")
    print(json.dumps(complaint_payload, indent=2))

    try:
        resp = requests.post(
            f"{BASE_URL}/api/complaints/ingest",
            json=complaint_payload,
            timeout=15
        )
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION FAILED — server not reachable at {BASE_URL}")
        print(f"   Error: {e}")
        print("   -> Confirm server is actually running before re-testing.")
        return False

    print(f"\nHTTP Status: {resp.status_code}")
    try:
        data = resp.json()
        print("Response body:")
        print(json.dumps(data, indent=2))
    except Exception:
        print("Response body (not JSON):")
        print(resp.text[:2000])
        return False

    if resp.status_code != 200:
        print(f"\n❌ Non-200 response — check server logs for the actual exception.")
        return False

    print("\n--- Automated checks ---")
    all_pass = True

    all_pass &= check(
        "Response has alert_level",
        "alert_level" in data,
        data.get("alert_level")
    )
    all_pass &= check(
        "Response has predicted_atm_id",
        data.get("predicted_atm_id") is not None,
        data.get("predicted_atm_id")
    )
    all_pass &= check(
        "tracking_number generated",
        bool(data.get("tracking_number"))
    )

    return all_pass


if __name__ == "__main__":
    print("Checking server is up first...")
    try:
        health = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Server responded: {health.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server not reachable at {BASE_URL} at all — start it before running this test.")
        sys.exit(1)

    # ── Test 1: normal case, full-name bank (tests normalize_bank fix) ──
    test1 = {
        "complaint_id": f"TEST-{uuid.uuid4().hex[:8]}",
        "complaint_text": "Someone transferred money from my account via UPI fraud",
        "victim_district": "Delhi",
        "victim_state": "Delhi",
        "victim_lat": 28.6,
        "victim_lon": 77.2,
        "victim_account_type": "Savings",
        "mobile_number": "9999999999",
        "beneficiary_account": "TESTACC001",
        "beneficiary_bank": "HDFC Bank",  # full-name, tests normalize_bank
        "beneficiary_account_type": "Savings",
        "beneficiary_lat": 28.6,
        "beneficiary_lon": 77.2,
        "transaction_amount": 50000.0,
        "amount_lost": 50000.0,
        "number_of_hops": 3,
        "upi_id": "test@upi",
        "fraud_type": "UPI Fraud",
        "transaction_timestamp": None
    }
    result1 = run_test(test1, "Full-name bank ('HDFC Bank') — normalize_bank fix check")

    # ── Test 2: missing/empty bank (tests the None-crash risk) ──
    test2 = dict(test1)
    test2["complaint_id"] = f"TEST-{uuid.uuid4().hex[:8]}"
    test2["beneficiary_bank"] = None  # explicit null — this is the crash-risk case
    result2 = run_test(test2, "NULL beneficiary_bank — crash-risk check")

    # ── Test 3: high amount / high hops, should trigger HIGH alert + blockchain ──
    test3 = dict(test1)
    test3["complaint_id"] = f"TEST-{uuid.uuid4().hex[:8]}"
    test3["amount_lost"] = 500000.0
    test3["number_of_hops"] = 6
    result3 = run_test(test3, "High amount/hops — should trigger HIGH alert + blockchain flag attempt")

    print(f"\n{'='*60}")
    print("SUMMARY (do not trust this alone — read full output above)")
    print(f"{'='*60}")
    print(f"Test 1 (full-name bank):  {'PASS' if result1 else 'FAIL'}")
    print(f"Test 2 (null bank):       {'PASS' if result2 else 'FAIL — this is the known crash-risk from normalize_bank'}")
    print(f"Test 3 (HIGH alert):      {'PASS' if result3 else 'FAIL'}")
    print("\nFor Test 3, also check server console/logs for:")
    print("  - '[call_predict]' or blockchain-related print statements")
    print("  - Confirm mule_registry table got a new row (query DB manually)")
    print("  - Confirm dispatch_log table got 4 new rows (I4C/CyberCell/Bank/PoliceSHO)")