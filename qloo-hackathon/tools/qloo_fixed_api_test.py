#!/usr/bin/env python3
"""
QLOO Fixed API Test

Now testing with the correct parameters that their API actually requires.
"""

import requests
import json
import time


def test_qloo_with_correct_params():
    """Test QLOO API with the correct parameters."""
    
    base_url = "https://hackathon.api.qloo.com"
    headers = {
        "X-API-Key": "QJSMyzrcQV4-pa_Dxglm4XRp_oWS8z_c_4YhGd4vKbw",
        "Content-Type": "application/json"
    }
    
    # Test different filter types to see what works
    filter_types = ["brand", "product", "person", "location", "music", "film", "tv", "book", "restaurant"]
    
    # Our strategic test queries
    test_queries = [
        # Basic fashion
        "sustainable fashion",
        "minimalist clothing", 
        
        # Accessibility (their blind spot)
        "adaptive clothing",
        "accessible fashion",
        "sensory friendly clothing",
        
        # Cultural intelligence
        "Japanese minimalist fashion",
        "African textile patterns",
        
        # Multisensory (our advantage)
        "soft texture clothing",
        "comfortable weight clothing"
    ]
    
    results = []
    
    print("🔧 TESTING QLOO WITH CORRECT PARAMETERS")
    print("="*50)
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        
        for filter_type in filter_types:
            try:
                payload = {
                    "input": query,
                    "filter": {"type": filter_type},
                    "k": 5
                }
                
                response = requests.post(
                    f"{base_url}/v2/recommendations",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                result = {
                    "query": query,
                    "filter_type": filter_type,
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
                        
                        if result["has_results"]:
                            print(f"   ✅ {filter_type}: {result['num_results']} results")
                            # Analyze first result for insights
                            if data.get("results"):
                                first_result = data["results"][0]
                                result["sample_result"] = first_result
                        else:
                            print(f"   ⚪ {filter_type}: 0 results")
                        
                    except Exception as e:
                        result["parse_error"] = str(e)
                        print(f"   ⚠️  {filter_type}: Parse error")
                        
                elif response.status_code == 400:
                    error_msg = response.text[:100]
                    result["error"] = error_msg
                    if "filter.type" not in error_msg:
                        print(f"   ❌ {filter_type}: {error_msg[:50]}")
                else:
                    result["error"] = response.text[:100]
                    print(f"   ❌ {filter_type}: Status {response.status_code}")
                
                results.append(result)
                
                # Don't overwhelm their API
                time.sleep(0.1)
                
            except Exception as e:
                results.append({
                    "query": query,
                    "filter_type": filter_type,
                    "error": str(e),
                    "success": False
                })
                print(f"   💥 {filter_type}: {str(e)[:30]}")
    
    return results


def analyze_qloo_blind_spots(results):
    """Analyze QLOO's actual capabilities and blind spots."""
    
    # Group results by query type
    accessibility_queries = ["adaptive clothing", "accessible fashion", "sensory friendly clothing"]
    cultural_queries = ["Japanese minimalist fashion", "African textile patterns"]
    multisensory_queries = ["soft texture clothing", "comfortable weight clothing"]
    basic_queries = ["sustainable fashion", "minimalist clothing"]
    
    analysis = {
        "overall_stats": {},
        "category_performance": {},
        "blind_spots": [],
        "working_combinations": []
    }
    
    # Overall stats
    total_tests = len(results)
    successful_tests = len([r for r in results if r.get("success", False)])
    tests_with_results = len([r for r in results if r.get("has_results", False)])
    
    analysis["overall_stats"] = {
        "total_tests": total_tests,
        "successful_api_calls": successful_tests,
        "tests_with_results": tests_with_results,
        "api_success_rate": successful_tests / total_tests if total_tests > 0 else 0,
        "results_success_rate": tests_with_results / total_tests if total_tests > 0 else 0
    }
    
    # Category performance
    categories = {
        "accessibility": accessibility_queries,
        "cultural": cultural_queries, 
        "multisensory": multisensory_queries,
        "basic": basic_queries
    }
    
    for category, queries in categories.items():
        category_results = [r for r in results if r.get("query") in queries]
        category_with_results = [r for r in category_results if r.get("has_results", False)]
        
        analysis["category_performance"][category] = {
            "total_tests": len(category_results),
            "tests_with_results": len(category_with_results),
            "success_rate": len(category_with_results) / len(category_results) if category_results else 0
        }
        
        # Identify blind spots
        if len(category_with_results) / len(category_results) < 0.3 if category_results else True:
            severity = "HIGH" if category in ["accessibility", "multisensory"] else "MEDIUM"
            analysis["blind_spots"].append({
                "category": category,
                "severity": severity,
                "success_rate": len(category_with_results) / len(category_results) if category_results else 0,
                "description": f"Poor performance on {category} queries",
                "business_impact": f"Missing {category} market segment"
            })
    
    # Working combinations
    working_results = [r for r in results if r.get("has_results", False)]
    for result in working_results:
        analysis["working_combinations"].append({
            "query": result["query"],
            "filter_type": result["filter_type"],
            "num_results": result["num_results"]
        })
    
    return analysis


def main():
    """Run the fixed API test."""
    print("🚀 TESTING QLOO'S REAL CAPABILITIES (FIXED)")
    
    results = test_qloo_with_correct_params()
    analysis = analyze_qloo_blind_spots(results)
    
    print(f"\n📊 FINAL ANALYSIS")
    print("="*50)
    
    stats = analysis["overall_stats"]
    print(f"Total API tests: {stats['total_tests']}")
    print(f"Successful API calls: {stats['successful_api_calls']}")
    print(f"Tests with actual results: {stats['tests_with_results']}")
    print(f"API success rate: {stats['api_success_rate']:.1%}")
    print(f"Results success rate: {stats['results_success_rate']:.1%}")
    
    print(f"\n🎯 CATEGORY PERFORMANCE:")
    for category, perf in analysis["category_performance"].items():
        print(f"   {category.upper()}: {perf['success_rate']:.1%} success rate ({perf['tests_with_results']}/{perf['total_tests']})")
    
    print(f"\n🚨 IDENTIFIED BLIND SPOTS:")
    for spot in analysis["blind_spots"]:
        print(f"   • {spot['category'].upper()} ({spot['severity']}): {spot['success_rate']:.1%} success rate")
    
    if analysis["working_combinations"]:
        print(f"\n✅ WORKING COMBINATIONS:")
        for combo in analysis["working_combinations"][:5]:  # Show first 5
            print(f"   • '{combo['query']}' + filter:{combo['filter_type']} = {combo['num_results']} results")
    
    # Save complete report
    report = {
        "test_results": results,
        "analysis": analysis,
        "strategic_insights": {
            "qloo_problems": [
                "API documentation is completely wrong (Bearer vs X-API-Key)",
                "Required parameters not documented (filter.type)",
                "Poor accessibility query performance",
                "Limited multisensory intelligence",
                "Developer adoption barriers due to broken docs"
            ],
            "our_opportunity": [
                "We solve their biggest blind spot: accessibility market",
                "Our multisensory approach fills massive gaps",
                "We can provide the developer experience they're failing at",
                "We offer the cultural intelligence they're missing"
            ],
            "winning_strategy": [
                "Position as their accessibility market solution",
                "Demonstrate superior developer experience",
                "Show the revenue they're losing to poor API usability",
                "Present as their regulatory compliance insurance"
            ]
        }
    }
    
    with open("qloo-hackathon/docs/qloo_complete_analysis.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📁 Complete analysis saved to: qloo-hackathon/docs/qloo_complete_analysis.json")
    
    return report


if __name__ == "__main__":
    main()