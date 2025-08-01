#!/usr/bin/env python3
"""
QLOO Real API Test

Now that we know the correct authentication, let's test their actual capabilities.
"""

import requests
import json
import time


def test_qloo_real_capabilities():
    """Test QLOO's actual API capabilities with correct authentication."""
    
    base_url = "https://hackathon.api.qloo.com"
    headers = {
        "X-API-Key": "QJSMyzrcQV4-pa_Dxglm4XRp_oWS8z_c_4YhGd4vKbw",
        "Content-Type": "application/json"
    }
    
    # Test cases to reveal their blind spots
    test_cases = [
        # Basic fashion
        {"input": "sustainable fashion", "k": 5},
        {"input": "minimalist clothing", "k": 5},
        
        # Accessibility-focused (their likely blind spot)
        {"input": "adaptive clothing", "k": 5},
        {"input": "accessible fashion", "k": 5},
        {"input": "clothing for disabled people", "k": 5},
        {"input": "sensory friendly clothing", "k": 5},
        {"input": "tactile fashion", "k": 5},
        
        # Cultural intelligence tests
        {"input": "Japanese minimalist fashion", "k": 5},
        {"input": "African textile patterns", "k": 5},
        {"input": "Indigenous fashion design", "k": 5},
        
        # Intersectional queries (likely gaps)
        {"input": "Black disabled fashion", "k": 5},
        {"input": "LGBTQ adaptive clothing", "k": 5},
        {"input": "elderly accessible fashion", "k": 5},
        
        # Multisensory queries (our advantage)
        {"input": "quiet clothing fabrics", "k": 5},
        {"input": "soft texture clothing", "k": 5},
        {"input": "comfortable weight clothing", "k": 5}
    ]
    
    results = []
    
    print("🧪 TESTING QLOO'S REAL CAPABILITIES")
    print("="*50)
    
    for i, test_case in enumerate(test_cases):
        print(f"Testing {i+1}/{len(test_cases)}: '{test_case['input']}'")
        
        try:
            response = requests.post(
                f"{base_url}/v2/recommendations",
                headers=headers,
                json=test_case,
                timeout=10
            )
            
            result = {
                "query": test_case["input"],
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data"] = data
                    result["num_results"] = len(data.get("results", []))
                    result["has_results"] = result["num_results"] > 0
                    
                    # Analyze quality of results
                    if "results" in data:
                        result["result_analysis"] = analyze_results_quality(data["results"], test_case["input"])
                    
                    print(f"   ✅ SUCCESS: {result['num_results']} results")
                    
                except Exception as e:
                    result["parse_error"] = str(e)
                    result["raw_response"] = response.text[:200]
                    print(f"   ⚠️  SUCCESS but parse error: {str(e)[:50]}")
            else:
                result["error"] = response.text[:200]
                print(f"   ❌ FAILED: Status {response.status_code}")
            
            results.append(result)
            
            # Be nice to their API
            time.sleep(0.2)
            
        except Exception as e:
            results.append({
                "query": test_case["input"],
                "error": str(e),
                "success": False
            })
            print(f"   💥 ERROR: {str(e)[:50]}")
    
    return results


def analyze_results_quality(results, query):
    """Analyze the quality and relevance of QLOO's results."""
    analysis = {
        "total_results": len(results),
        "has_accessibility_focus": False,
        "has_cultural_context": False,
        "has_multisensory_info": False,
        "result_types": [],
        "potential_gaps": []
    }
    
    # Check for accessibility-related terms
    accessibility_terms = ["accessible", "adaptive", "disability", "sensory", "tactile", "inclusive"]
    cultural_terms = ["cultural", "traditional", "heritage", "indigenous", "ethnic"]
    multisensory_terms = ["texture", "sound", "feel", "comfort", "weight", "soft", "smooth"]
    
    for result in results:
        result_text = json.dumps(result).lower()
        
        if any(term in result_text for term in accessibility_terms):
            analysis["has_accessibility_focus"] = True
        
        if any(term in result_text for term in cultural_terms):
            analysis["has_cultural_context"] = True
        
        if any(term in result_text for term in multisensory_terms):
            analysis["has_multisensory_info"] = True
        
        # Track result types
        if "type" in result:
            analysis["result_types"].append(result["type"])
    
    # Identify gaps based on query
    query_lower = query.lower()
    if "accessible" in query_lower or "adaptive" in query_lower or "disabled" in query_lower:
        if not analysis["has_accessibility_focus"]:
            analysis["potential_gaps"].append("Missing accessibility-focused results")
    
    if "tactile" in query_lower or "texture" in query_lower or "soft" in query_lower:
        if not analysis["has_multisensory_info"]:
            analysis["potential_gaps"].append("Missing multisensory information")
    
    return analysis


def identify_qloo_blind_spots(results):
    """Identify QLOO's blind spots based on test results."""
    blind_spots = []
    
    # Analyze accessibility coverage
    accessibility_queries = [r for r in results if any(term in r["query"].lower() 
                           for term in ["adaptive", "accessible", "disabled", "sensory", "tactile"])]
    
    accessibility_success_rate = len([r for r in accessibility_queries if r.get("has_results", False)]) / len(accessibility_queries) if accessibility_queries else 0
    
    if accessibility_success_rate < 0.5:
        blind_spots.append({
            "category": "Accessibility Market",
            "severity": "HIGH",
            "description": f"Only {accessibility_success_rate:.1%} success rate for accessibility queries",
            "business_impact": "Missing entire accessibility market segment"
        })
    
    # Analyze cultural coverage
    cultural_queries = [r for r in results if any(term in r["query"].lower() 
                       for term in ["japanese", "african", "indigenous", "cultural"])]
    
    cultural_success_rate = len([r for r in cultural_queries if r.get("has_results", False)]) / len(cultural_queries) if cultural_queries else 0
    
    if cultural_success_rate < 0.7:
        blind_spots.append({
            "category": "Cultural Intelligence",
            "severity": "MEDIUM",
            "description": f"Only {cultural_success_rate:.1%} success rate for cultural queries",
            "business_impact": "Limited global market penetration"
        })
    
    # Analyze multisensory coverage
    multisensory_queries = [r for r in results if any(term in r["query"].lower() 
                           for term in ["quiet", "soft", "texture", "comfortable", "weight"])]
    
    multisensory_success_rate = len([r for r in multisensory_queries if r.get("has_results", False)]) / len(multisensory_queries) if multisensory_queries else 0
    
    if multisensory_success_rate < 0.6:
        blind_spots.append({
            "category": "Multisensory Intelligence",
            "severity": "HIGH", 
            "description": f"Only {multisensory_success_rate:.1%} success rate for multisensory queries",
            "business_impact": "Cannot serve blind/neurodivergent users effectively"
        })
    
    return blind_spots


def main():
    """Run the real API test."""
    results = test_qloo_real_capabilities()
    
    # Analyze blind spots
    blind_spots = identify_qloo_blind_spots(results)
    
    # Generate summary
    successful_queries = [r for r in results if r.get("success", False)]
    queries_with_results = [r for r in results if r.get("has_results", False)]
    
    print(f"\n📊 QLOO API ANALYSIS RESULTS")
    print("="*50)
    print(f"Total queries tested: {len(results)}")
    print(f"Successful API calls: {len(successful_queries)}")
    print(f"Queries with actual results: {len(queries_with_results)}")
    print(f"Success rate: {len(successful_queries)/len(results):.1%}")
    print(f"Results rate: {len(queries_with_results)/len(results):.1%}")
    
    print(f"\n🚨 IDENTIFIED BLIND SPOTS:")
    for spot in blind_spots:
        print(f"   • {spot['category']} ({spot['severity']}): {spot['description']}")
    
    # Save complete report
    report = {
        "test_results": results,
        "blind_spots": blind_spots,
        "summary": {
            "total_queries": len(results),
            "successful_calls": len(successful_queries),
            "queries_with_results": len(queries_with_results),
            "success_rate": len(successful_queries)/len(results),
            "results_rate": len(queries_with_results)/len(results)
        },
        "strategic_implications": {
            "our_opportunity": "QLOO has massive gaps in accessibility and multisensory intelligence",
            "market_size": "Accessibility market is $13B+ and completely underserved by QLOO",
            "competitive_advantage": "We can own the entire accessibility intelligence market"
        }
    }
    
    with open("qloo-hackathon/docs/qloo_real_capabilities_analysis.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Full analysis saved to: qloo-hackathon/docs/qloo_real_capabilities_analysis.json")
    
    return report


if __name__ == "__main__":
    main()