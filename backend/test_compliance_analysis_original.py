#!/usr/bin/env python3
"""
Test script for Compliance Analysis feature.

Tests:
1. Compliance analyzer with mock data
2. Compliance endpoint integration
3. JSON response validation
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.compliance_analyzer import ComplianceAnalyzer


def test_1_compliance_analyzer_with_mock_data():
    """Test: Compliance analyzer generates valid JSON response."""
    print("\n" + "="*70)
    print("TEST 1: Compliance Analyzer with Mock Data")
    print("="*70)

    # Mock retrieved chunks
    mock_chunks = [
        {
            "content": """
            6.2 MFA. Vendor will enforce multi-factor authentication (MFA) for 
            (a) privileged accounts, (b) remote access, and (c) all access to 
            production environments. All admin access requires MFA.""",
            "metadata": {
                "section_title": "Identity and Access Management",
                "page_number": 4
            }
        },
        {
            "content": """
            7.1 Encryption. Vendor will encrypt Company Data in transit and at rest.
            7.2 Data in Transit Requirements (TLS). Vendor will enforce encryption 
            in transit for all external and internal transmissions using TLS 1.2 
            or higher (TLS 1.3 where feasible).""",
            "metadata": {
                "section_title": "Encryption and Key Management",
                "page_number": 5
            }
        },
        {
            "content": """
            12.1 Logging. Vendor will collect and retain security-relevant logs for 
            systems processing Company Data, including authentication, authorization, 
            privileged actions, and access to production data where feasible.""",
            "metadata": {
                "section_title": "Logging, Monitoring, Records Management",
                "page_number": 7
            }
        },
        {
            "content": """
            15. Incident Response and Breach Notification
            Vendor will maintain and test an incident response plan annually and will 
            notify Company within 72 hours after becoming aware of a Security Incident, 
            provide ongoing updates, and deliver a written incident report within 10 
            business days after containment.""",
            "metadata": {
                "section_title": "Incident Response",
                "page_number": 9
            }
        },
    ]

    print("✓ Generated mock chunks")
    print(f"✓ Chunk count: {len(mock_chunks)}")

    # Generate compliance analysis
    print("\n✓ Generating compliance analysis...")
    findings = ComplianceAnalyzer.generate_compliance_analysis(mock_chunks)

    print(f"✓ Generated {len(findings)} compliance findings")

    # Validate response structure
    print("\n✓ Validating response structure...")
    for idx, finding in enumerate(findings, 1):
        assert "compliance_question" in finding, f"Finding {idx}: Missing 'compliance_question'"
        assert "compliance_state" in finding, f"Finding {idx}: Missing 'compliance_state'"
        assert finding["compliance_state"] in [
            "Fully Compliant",
            "Partially Compliant",
            "Non-Compliant"
        ], f"Finding {idx}: Invalid compliance_state: {finding['compliance_state']}"
        assert "confidence" in finding, f"Finding {idx}: Missing 'confidence'"
        assert isinstance(finding["confidence"], int), f"Finding {idx}: confidence is not int"
        assert 0 <= finding["confidence"] <= 100, f"Finding {idx}: confidence out of range"
        assert "relevant_quotes" in finding, f"Finding {idx}: Missing 'relevant_quotes'"
        assert isinstance(finding["relevant_quotes"], list), f"Finding {idx}: quotes is not list"
        assert "rationale" in finding, f"Finding {idx}: Missing 'rationale'"

        print(f"  Finding {idx}: {finding['compliance_question'][:40]}...")
        print(f"    State: {finding['compliance_state']}")
        print(f"    Confidence: {finding['confidence']}%")
        print(f"    Quotes: {len(finding['relevant_quotes'])}")


def test_2_empty_chunks_handling():
    """Test: Compliance analyzer handles empty chunks gracefully."""
    print("\n" + "="*70)
    print("TEST 2: Empty Chunks Handling")
    print("="*70)

    print("✓ Testing with empty chunks list...")
    findings = ComplianceAnalyzer.generate_compliance_analysis([])

    print(f"✓ Returned {len(findings)} findings")
    assert len(findings) == 5, "Should return all 5 compliance questions"

    # All should be non-compliant
    for finding in findings:
        assert finding["compliance_state"] == "Non-Compliant", "Expected all non-compliant"
        assert finding["confidence"] == 0, "Expected confidence 0"
        assert finding["relevant_quotes"] == [], "Expected no quotes"

    print("✓ All findings marked as Non-Compliant (as expected)")


def test_3_compliance_questions():
    """Test: Verify all required compliance questions are present."""
    print("\n" + "="*70)
    print("TEST 3: Compliance Questions Verification")
    print("="*70)

    expected_questions = [
        "Network Authentication & Authorization Protocols",
        "Multi-Factor Authentication (MFA) Enforcement",
        "Logging and Monitoring Requirements",
        "Incident Response and Breach Notification",
        "Data Encryption and Key Management",
    ]

    findings = ComplianceAnalyzer.generate_compliance_analysis([])
    actual_questions = [f["compliance_question"] for f in findings]

    print(f"✓ Expected questions: {len(expected_questions)}")
    print(f"✓ Actual questions: {len(actual_questions)}")

    for expected in expected_questions:
        assert expected in actual_questions, f"Missing question: {expected}"
        print(f"  ✓ {expected}")


def test_4_json_serialization():
    """Test: Compliance findings can be JSON serialized."""
    print("\n" + "="*70)
    print("TEST 4: JSON Serialization")
    print("="*70)

    mock_chunks = [
        {
            "content": "MFA is required for all admin access.",
            "metadata": {
                "section_title": "Access Control",
                "page_number": 1
            }
        }
    ]

    findings = ComplianceAnalyzer.generate_compliance_analysis(mock_chunks)

    print("✓ Serializing to JSON...")
    json_str = json.dumps(findings, indent=2)

    print(f"✓ JSON length: {len(json_str)} characters")
    print(f"✓ JSON valid: Yes")

    # Deserialize to verify
    parsed = json.loads(json_str)
    print(f"✓ Deserialization successful")
    print(f"✓ Findings count: {len(parsed)}")


def test_5_compliance_summary_calculation():
    """Test: Compliance summary statistics calculation."""
    print("\n" + "="*70)
    print("TEST 5: Compliance Summary Calculation")
    print("="*70)

    from app.routes.files import _calculate_compliance_summary

    mock_findings = [
        {
            "compliance_question": "Q1",
            "compliance_state": "Fully Compliant",
            "confidence": 95,
        },
        {
            "compliance_question": "Q2",
            "compliance_state": "Partially Compliant",
            "confidence": 70,
        },
        {
            "compliance_question": "Q3",
            "compliance_state": "Non-Compliant",
            "confidence": 30,
        },
        {
            "compliance_question": "Q4",
            "compliance_state": "Fully Compliant",
            "confidence": 90,
        },
        {
            "compliance_question": "Q5",
            "compliance_state": "Fully Compliant",
            "confidence": 85,
        },
    ]

    summary = _calculate_compliance_summary(mock_findings)

    print("✓ Summary statistics:")
    print(f"  Total requirements: {summary['total_requirements']}")
    print(f"  Fully compliant: {summary['fully_compliant']}")
    print(f"  Partially compliant: {summary['partially_compliant']}")
    print(f"  Non-compliant: {summary['non_compliant']}")
    print(f"  Average confidence: {summary['average_confidence']}%")
    print(f"  Compliance percentage: {summary['compliance_percentage']}%")

    assert summary['total_requirements'] == 5
    assert summary['fully_compliant'] == 3
    assert summary['partially_compliant'] == 1
    assert summary['non_compliant'] == 1
    assert summary['compliance_percentage'] == 60.0


def test_6_quote_extraction():
    """Test: Quote extraction from findings."""
    print("\n" + "="*70)
    print("TEST 6: Quote Extraction")
    print("="*70)

    mock_chunks = [
        {
            "content": "Section 6.2: MFA is required for privileged accounts and production access.",
            "metadata": {
                "section_title": "Access Control",
                "page_number": 4
            }
        }
    ]

    findings = ComplianceAnalyzer.generate_compliance_analysis(mock_chunks)

    print("✓ Checking for quotes in findings...")
    quotes_found = 0
    for finding in findings:
        if finding["relevant_quotes"]:
            quotes_found += 1
            print(f"  Question: {finding['compliance_question']}")
            print(f"  Quotes: {len(finding['relevant_quotes'])}")
            for quote in finding['relevant_quotes'][:1]:
                print(f"    - \"{quote[:60]}...\"")

    print(f"✓ Total findings with quotes: {quotes_found}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("COMPLIANCE ANALYSIS TEST SUITE")
    print("="*70)

    tests = [
        ("Compliance Analysis Generation", test_1_compliance_analyzer_with_mock_data),
        ("Empty Chunks Handling", test_2_empty_chunks_handling),
        ("Compliance Questions", test_3_compliance_questions),
        ("JSON Serialization", test_4_json_serialization),
        ("Summary Calculation", test_5_compliance_summary_calculation),
        ("Quote Extraction", test_6_quote_extraction),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"\n✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    print("="*70)

    if failed == 0:
        print("\n✅ ALL TESTS PASSED - COMPLIANCE ANALYSIS READY!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
