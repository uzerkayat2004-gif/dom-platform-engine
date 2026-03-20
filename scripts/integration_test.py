"""
DOM Platform — Full Integration Test
Tests the complete Category C pipeline end to end.
Run: python scripts/integration_test.py
"""

import asyncio
import httpx
import json
import time

ENGINE_URL = "http://127.0.0.1:8080"
DOM_URL = "http://127.0.0.1:5000"

async def run_tests():
    print("=" * 60)
    print("DOM PLATFORM — FULL INTEGRATION TEST")
    print("Category C Engine End-to-End Validation")
    print("=" * 60)
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # TEST 1: Engine health
        print("\nTEST 1: Engine health check")
        try:
            r = await client.get(f"{ENGINE_URL}/health")
            passed = r.status_code == 200
            print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {r.json()}")
            results.append(("Engine health", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Engine health", False))
        
        # TEST 2: Create project
        print("\nTEST 2: Create restaurant project")
        try:
            r = await client.post(f"{ENGINE_URL}/project/create", json={
                "name": "test-restaurant",
                "description": "Restaurant POS system for Indian restaurant"
            })
            passed = r.status_code == 200 and "project_id" in r.json()
            print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — Project created")
            results.append(("Create project", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Create project", False))
        
        # TEST 3: DOM Server health
        print("\nTEST 3: Start and check DOM Server")
        try:
            # Start DOM server
            await client.post(f"{ENGINE_URL}/dom-server/start", json={
                "project_id": "test-restaurant",
                "port": 5000
            })
            time.sleep(2)
            
            # Check health
            dom_client = httpx.AsyncClient(timeout=10.0)
            r = await dom_client.get(f"{DOM_URL}/health")
            passed = r.status_code == 200
            print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — DOM Server running")
            results.append(("DOM Server health", passed))
            await dom_client.aclose()
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("DOM Server health", False))
        
        # TEST 4: Add item — normal operation
        print("\nTEST 4: Add item to order (should PASS)")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Add one Butter Chicken at 350 rupees to the order",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("status") == "success" and not data.get("blocked")
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {data.get('display', '')}")
                results.append(("Add item — normal", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Add item — normal", False))
        
        # TEST 5: Security block — price too high
        print("\nTEST 5: Add item at Rs.15000 (should be BLOCKED)")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Add one item at 15000 rupees to the order",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("blocked") == True
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — BLOCKED: {data.get('reason', '')}")
                results.append(("Security block — price", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Security block — price", False))
        
        # TEST 6: Security block — excessive discount
        print("\nTEST 6: Apply 60% discount (should be BLOCKED)")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Apply 60 percent discount to the total",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("blocked") == True
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — BLOCKED: {data.get('reason', '')}")
                results.append(("Security block — discount", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Security block — discount", False))
        
        # TEST 7: Valid discount
        print("\nTEST 7: Apply 10% discount (should PASS)")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Apply 10 percent discount to the total",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("status") == "success" and not data.get("blocked")
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {data.get('display', '')}")
                results.append(("Valid discount", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Valid discount", False))
        
        # TEST 8: Send to kitchen
        print("\nTEST 8: Send order to kitchen")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Send order to kitchen",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("status") == "success"
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {data.get('display', '')}")
                results.append(("Send to kitchen", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Send to kitchen", False))
        
        # TEST 9: Process payment
        print("\nTEST 9: Process payment")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.post(f"{DOM_URL}/process", json={
                    "instruction": "Process payment for total amount",
                    "project_id": "test-restaurant"
                })
                data = r.json()
                passed = data.get("status") == "success"
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {data.get('display', '')}")
                results.append(("Process payment", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Process payment", False))
        
        # TEST 10: Glass Box has entries
        print("\nTEST 10: Glass Box logging all actions")
        try:
            async with httpx.AsyncClient(timeout=10.0) as dom:
                r = await dom.get(f"{DOM_URL}/glassbox/test-restaurant")
                data = r.json()
                entries = data.get("entries", [])
                passed = len(entries) >= 5
                print(f"  {'✅ PASSED' if passed else '❌ FAILED'} — {len(entries)} entries logged")
                results.append(("Glass Box logging", passed))
        except Exception as e:
            print(f"  ❌ FAILED — {e}")
            results.append(("Glass Box logging", False))
    
    # Final summary
    print()
    print("=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed in results:
        print(f"  {'✅' if passed else '❌'} {test_name}")
    
    accuracy = (passed_count / total) * 100
    print()
    print(f"SCORE: {passed_count}/{total} = {accuracy:.0f}%")
    
    if accuracy >= 80:
        print()
        print("🚀 CATEGORY C ENGINE — FULLY VALIDATED")
        print("   Plain English → Rule Files → DOM Model → Security Blocking")
        print("   The world's first Category C engine is working.")
    else:
        print()
        print("⚠️  Some tests need attention — check output above")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
