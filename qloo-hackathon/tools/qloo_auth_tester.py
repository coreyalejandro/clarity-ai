#!/usr/bin/env python3
"""
QLOO Authentication Tester

Test different authentication methods to see what actually works.
"""

import requests
import json


def test_qloo_auth_methods():
    """Test different ways to authenticate with QLOO API."""
    
    base_url = "https://hackathon.api.qloo.com"
    api_key = "QJSMyzrcQV4-pa_Dxglm4XRp_oWS8z_c_4YhGd4vKbw"
    
    # Different authentication methods to try
    auth_methods = [
        {
            "name": "Bearer Token in Authorization Header",
            "headers": {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        },
        {
            "name": "API Key in Authorization Header",
            "headers": {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
        },
        {
            "name": "X-API-Key Header",
            "headers": {"X-API-Key": api_key, "Content-Type": "application/json"}
        },
        {
            "name": "API Key in Query Parameter",
            "headers": {"Content-Type": "application/json"},
            "params": {"api_key": api_key}
        },
        {
            "name": "API Key in Request Body",
            "headers": {"Content-Type": "application/json"},
            "body_key": api_key
        }
    ]
    
    # Test endpoints to try
    endpoints = [
        "/",
        "/v1/recommendations", 
        "/v2/recommendations",
        "/recommendations",
        "/health",
        "/status"
    ]
    
    results = []
    
    for auth_method in auth_methods:
        print(f"\n🔑 Testing: {auth_method['name']}")
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                headers = auth_method["headers"]
                params = auth_method.get("params", {})
                
                # Prepare request body
                if "body_key" in auth_method:
                    data = {"api_key": auth_method["body_key"], "input": "test"}
                else:
                    data = {"input": "test"}
                
                response = requests.post(url, headers=headers, params=params, json=data, timeout=5)
                
                result = {
                    "auth_method": auth_method["name"],
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "success": response.status_code not in [401, 403]
                }
                
                if response.status_code == 200:
                    try:
                        result["response_data"] = response.json()
                    except:
                        result["response_text"] = response.text[:200]
                elif response.status_code in [401, 403]:
                    result["auth_error"] = response.text[:200]
                else:
                    result["other_response"] = response.text[:200]
                
                results.append(result)
                
                if response.status_code == 200:
                    print(f"   ✅ {endpoint}: SUCCESS!")
                elif response.status_code in [401, 403]:
                    print(f"   ❌ {endpoint}: Auth failed")
                else:
                    print(f"   ⚠️  {endpoint}: Status {response.status_code}")
                
            except Exception as e:
                results.append({
                    "auth_method": auth_method["name"],
                    "endpoint": endpoint,
                    "error": str(e),
                    "success": False
                })
                print(f"   💥 {endpoint}: {str(e)[:50]}")
    
    return results


def test_qloo_documentation():
    """Test if their documentation endpoint works."""
    try:
        response = requests.get("https://docs.qloo.com/", timeout=10)
        return {
            "docs_accessible": response.status_code == 200,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except Exception as e:
        return {"docs_accessible": False, "error": str(e)}


def main():
    """Run authentication tests."""
    print("🔍 TESTING QLOO API AUTHENTICATION METHODS")
    print("="*50)
    
    # Test authentication methods
    auth_results = test_qloo_auth_methods()
    
    # Test documentation
    docs_result = test_qloo_documentation()
    
    # Analyze results
    successful_auths = [r for r in auth_results if r.get("success", False)]
    
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   Total tests: {len(auth_results)}")
    print(f"   Successful: {len(successful_auths)}")
    print(f"   Documentation accessible: {docs_result.get('docs_accessible', False)}")
    
    if successful_auths:
        print(f"\n✅ WORKING AUTHENTICATION METHODS:")
        for result in successful_auths:
            print(f"   • {result['auth_method']} on {result['endpoint']}")
    else:
        print(f"\n❌ NO WORKING AUTHENTICATION METHODS FOUND")
        print("   This suggests QLOO has a major API accessibility problem!")
    
    # Save results
    full_report = {
        "auth_test_results": auth_results,
        "docs_accessibility": docs_result,
        "summary": {
            "total_tests": len(auth_results),
            "successful_tests": len(successful_auths),
            "success_rate": len(successful_auths) / len(auth_results) if auth_results else 0
        }
    }
    
    with open("qloo-hackathon/docs/qloo_auth_investigation.json", "w") as f:
        json.dump(full_report, f, indent=2)
    
    return full_report


if __name__ == "__main__":
    main()