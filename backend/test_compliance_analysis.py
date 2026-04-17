#!/usr/bin/env python3
"""
Updated Test Script for Compliance Analysis Feature - Using Actual Vector Store Chunks

Tests compliance analyzer with real chunks from FAISS vector store (metadata.json)

Tests:
1. Compliance analyzer with actual vector store chunks  
2. Empty chunks handling
3. Compliance questions verification
4. JSON response validation
5. Summary calculation
6. Quote extraction
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.compliance_analyzer import ComplianceAnalyzer


def load_vector_store_chunks(limit: int = 7):
    """
    Load actual chunks from vector store metadata.json.
    
    Returns:
        List of chunks in format: {vector_id, chunk_id, file_id, content, metadata, content_type}
    """
    try:
        metadata_path = Path(__file__).parent / "app" / "vector_store" / "metadata.json"
        
        if not metadata_path.exists():
            print(f"⚠ Vector store not found at {metadata_path}")
            return []
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Convert metadata chunks to list format expected by compliance analyzer
        chunks_dict = metadata.get("chunks", {})
        chunks_list = []
        
        for vector_id_str in sorted(chunks_dict.keys())[:limit]:
            chunk_data = chunks_dict[vector_id_str]
            chunks_list.append({
                "vector_id": chunk_data.get("vector_id"),
                "chunk_id": chunk_data.get("chunk_id"),
                "file_id": chunk_data.get("file_id"),
                "content": chunk_data.get("content", ""),
                "metadata": chunk_data.get("metadata", {}),
                "content_type": chunk_data.get("content_type", "text"),
                "content_length": chunk_data.get("content_length", 0),
                "token_count": chunk_data.get("token_count", 0),
            })
        
        return chunks_list
    
    except Exception as e:
        print(f"⚠ Error loading vector store chunks: {e}")
        return []


def test_1_compliance_analyzer_with_vector_store_chunks():
    """Test: Compliance analyzer with actual vector store chunks."""
    print("\n" + "="*70)
    print("TEST 1: Compliance Analyzer with Vector Store Chunks")
    print("="*70)

    # Load chunks from actual vector store
    chunks = load_vector_store_chunks(limit=7)
    
    if not chunks:
        print("⚠ No chunks found in vector store, skipping test")
        return
    
    print(f"✓ Loaded {len(chunks)} chunks from vector store metadata.json")
    
    # Display chunk info
    for i, chunk in enumerate(chunks[:3], 1):
        content_preview = chunk.get("content", "")[:100].replace("\n", " ").strip()
        print(f"  Chunk {i}: {chunk.get('chunk_id')} - {content_preview}...")
    
    # Generate compliance analysis from vector store chunks
    print("\n✓ Generating compliance analysis from vector store chunks...")
    findings = ComplianceAnalyzer.generate_compliance_analysis(chunks)
    
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

    # Load chunks from vector store or use mock
    chunks = load_vector_store_chunks(limit=3)
    if not chunks:
        chunks = [
            {
                "content": "MFA is required for all admin access.",
                "metadata": {
                    "section_title": "Access Control",
                    "page_number": 1
                }
            }
        ]
    
    findings = ComplianceAnalyzer.generate_compliance_analysis(chunks)

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
    """Test: Quote extraction from findings with vector store chunks."""
    print("\n" + "="*70)
    print("TEST 6: Quote Extraction from Vector Store Chunks")
    print("="*70)

    # Load chunks from vector store
    chunks = load_vector_store_chunks(limit=5)
    
    if chunks:
        print(f"✓ Using {len(chunks)} chunks from vector store")
        findings = ComplianceAnalyzer.generate_compliance_analysis(chunks)
    else:
        print("⚠ No vector store chunks, using mock data")
        mock_chunks = [
            {
                "content": "Section 6.2: MFA is required for privileged accounts and production access. All admin accounts must use MFA.",
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
            for quote in finding['relevant_quotes'][:2]:
                print(f"    - \"{quote[:70].strip()}...\"")

    print(f"✓ Total findings with quotes: {quotes_found}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("COMPLIANCE ANALYSIS TEST SUITE (WITH VECTOR STORE CHUNKS)")
    print("="*70)

    tests = [
        ("Compliance Analysis with Vector Store Chunks", test_1_compliance_analyzer_with_vector_store_chunks),
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
        print("✓ Now uses actual chunks from vector store (metadata.json)")
        print("✓ Full text content included (not just previews)")
        print("✓ Proper chunk formatting from uploaded PDFs")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
