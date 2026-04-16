"""
Example usage of the Contract Analyzer - Test Script

This script demonstrates how to use the contract analysis services directly.
Run this to test the GPT-4o integration without starting the FastAPI server.

Usage:
    python example_usage.py
    python example_usage.py /path/to/contract.pdf
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services.pdf_parser import PDFParser
from app.services.contract_analyzer import ContractAnalyzer

# Example contract text (for testing without PDF)
SAMPLE_CONTRACT_TEXT = """
VENDOR SERVICE AGREEMENT

This Vendor Service Agreement ("Agreement") is entered into as of January 1, 2024
between Company ABC Corp ("Client") and XYZ Vendor Services LLC ("Vendor").

1. CONTRACT DETAILS
   - Contract Type: Enterprise Software License
   - Contract Status: Active
   - Total Contract Value: $250,000 USD
   - Term: January 1, 2024 - December 31, 2026

2. COMPLIANCE AND SECURITY
   - Encryption: All data must use AES-256 encryption
   - Data Residency: EU data centers only
   - MFA Coverage: Required for all administrative access (100% coverage)
   - Compliance Score: 94%

3. RISK MANAGEMENT
   - Control Coverage: 92% of critical controls
   - High-Risk Issues: 1 identified
   - Open Risks: 3 items
   - Average Time to Remediate: 10 days
   - Revenue at Risk: $25,000

4. OBLIGATIONS AND PERFORMANCE
   - Total Obligations: 15 identified
   - Obligations Completion Rate: 93%
   - Processing Time Requirement: 2-3 business days
   - Clause Extraction Accuracy: 98%

5. EXPIRATION DATES
   - Contract Expiration: December 31, 2026
   - Renewal Option Expiration: June 30, 2026
   - Service Level Agreement: 99.9% uptime

6. INCIDENT READINESS
   - Incident Readiness Score: 87%
   - Support Hours: 24/7
   - Response Time: 2 hours for critical issues
"""


def check_environment():
    """Check if Azure OpenAI environment variables are configured."""
    print("=" * 60)
    print("Checking Azure OpenAI Configuration")
    print("=" * 60)
    print()
    
    required_vars = {
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API Key",
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI Endpoint URL",
        "AZURE_OPENAI_API_VERSION": "Azure OpenAI API Version",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "Azure OpenAI Deployment Name",
    }
    
    all_set = True
    for var_name, var_description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # Mask sensitive values
            if "KEY" in var_name:
                display_value = value[:10] + "..." + value[-5:] if len(value) > 20 else "***"
            else:
                display_value = value
            print(f"✓ {var_description:40} {display_value}")
        else:
            print(f"✗ {var_description:40} NOT SET")
            all_set = False
    
    print()
    if all_set:
        print("✓ All environment variables are configured!")
    else:
        print("✗ Some environment variables are missing!")
        print("\nPlease create a .env file in the backend/ directory with:")
        print("  AZURE_OPENAI_API_KEY=your-api-key")
        print("  AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("  AZURE_OPENAI_API_VERSION=2024-02-15-preview")
        print("  AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o")
    
    print()
    return all_set


def test_direct_analyzer():
    """Test the analyzer with sample text directly."""
    print("=" * 60)
    print("Testing Contract Analyzer with Sample Text")
    print("=" * 60)
    print()
    
    try:
        print("Analyzing contract text...")
        kpis = ContractAnalyzer.extract_kpis(SAMPLE_CONTRACT_TEXT)
        
        print("\n✓ Analysis successful!")
        print("\nExtracted KPIs:")
        print("-" * 60)
        print(json.dumps(kpis, indent=2))
        print("-" * 60)
        
        # Count non-"Not Present" values
        extracted_count = sum(1 for v in kpis.values() if v != "Not Present")
        total_count = len(kpis)
        print(f"\n✓ Extracted {extracted_count} out of {total_count} KPIs")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_pdf_parser(pdf_path: str):
    """Test the PDF parser with an actual PDF file."""
    print("=" * 60)
    print("Testing PDF Parser")
    print("=" * 60)
    print()
    
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"✗ File not found: {pdf_path}")
        return
    
    try:
        print(f"Parsing PDF: {pdf_path}")
        text = PDFParser.extract_text(pdf_file)
        
        print(f"\n✓ PDF parsed successfully!")
        print(f"Extracted {len(text)} characters")
        print("\nFirst 500 characters of extracted text:")
        print("-" * 60)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 60)
        
        # Now analyze the extracted text
        print("\nAnalyzing extracted text...")
        kpis = ContractAnalyzer.extract_kpis(text)
        
        print("\n✓ Analysis complete!")
        print("\nExtracted KPIs:")
        print("-" * 60)
        print(json.dumps(kpis, indent=2))
        print("-" * 60)
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


def show_prompt():
    """Display the system prompt used for analysis."""
    print("=" * 60)
    print("System Prompt for Contract Analysis")
    print("=" * 60)
    print()
    
    try:
        prompt = ContractAnalyzer.load_system_prompt()
        print(prompt)
        print("\n" + "=" * 60)
    except Exception as e:
        print(f"✗ Error loading prompt: {str(e)}")


def test_all_kpi_fields():
    """Verify all KPI fields are present in the response."""
    print("=" * 60)
    print("Testing All KPI Fields")
    print("=" * 60)
    print()
    
    expected_fields = [
        "totalContractsProcessed",
        "contractType",
        "contractStatus",
        "complianceScore",
        "controlCoveragePercentage",
        "incidentReadinessScore",
        "highRiskIssuesCount",
        "openRisksCount",
        "averageTimeToRemediate",
        "totalContractValue",
        "revenueAtRisk",
        "totalObligationsExtracted",
        "obligationsCompletionRate",
        "upcomingExpirations",
        "averageProcessingTime",
        "clauseExtractionAccuracy",
        "dataResidencyCompliance",
        "encryptionCompliance",
        "mfaCoverage"
    ]
    
    print(f"Expected KPI fields: {len(expected_fields)}\n")
    
    for i, field in enumerate(expected_fields, 1):
        print(f"{i:2d}. {field}")
    
    print("\n" + "=" * 60)
    
    # Test with sample text
    try:
        kpis = ContractAnalyzer.extract_kpis(SAMPLE_CONTRACT_TEXT)
        
        print("\nValidating response structure...")
        missing_fields = []
        
        for field in expected_fields:
            if field not in kpis:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"✗ Missing fields: {missing_fields}")
        else:
            print("✓ All expected fields present!")
        
        print(f"\n✓ Response contains {len(kpis)} fields")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " CONTRACT ANALYSIS EXAMPLE USAGE ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Check environment first
    print("0. Checking Environment Variables...")
    env_ok = check_environment()
    if not env_ok:
        print("[ERROR] Azure OpenAI not configured. Exiting.")
        sys.exit(1)
    print()
    
    # Run tests
    print("1. Testing System Prompt...")
    show_prompt()
    print("\n")
    
    print("2. Testing Direct Contract Analysis...")
    test_direct_analyzer()
    print("\n")
    
    print("3. Verifying All KPI Fields...")
    test_all_kpi_fields()
    print("\n")
    
    # Test PDF parsing if a PDF is provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print("4. Testing PDF Parser with Contract Analysis...")
        test_pdf_parser(pdf_path)
        print("\n")
    else:
        print("4. To test PDF parsing, run:")
        print("   python example_usage.py /path/to/contract.pdf")
        print()
    
    print("=" * 60)
    print("Example usage script completed!")
    print("=" * 60)
