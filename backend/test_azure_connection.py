#!/usr/bin/env python3
"""Test Azure OpenAI connection directly."""
import sys
sys.path.insert(0, '/Users/ayandogra/Documents/GitHub/Learning_project/backend')

from app.services.contract_analyzer import ContractAnalyzer, get_azure_client
from dotenv import load_dotenv
import os

load_dotenv()

# Test 1: Check environment variables
print("=" * 50)
print("ENVIRONMENT VARIABLES CHECK")
print("=" * 50)
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(f"API Key present: {bool(api_key)}")
print(f"API Key (first 20 chars): {api_key[:20] if api_key else 'MISSING'}")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")

# Test 2: Test client creation
print("\n" + "=" * 50)
print("CLIENT CREATION TEST")
print("=" * 50)
try:
    client = get_azure_client()
    print("✓ Client created successfully")
except Exception as e:
    print(f"✗ Client creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Load system prompt
print("\n" + "=" * 50)
print("SYSTEM PROMPT TEST")
print("=" * 50)
try:
    prompt = ContractAnalyzer.load_system_prompt()
    print(f"✓ Prompt loaded successfully ({len(prompt)} chars)")
    print(f"Prompt preview: {prompt[:100]}...")
except Exception as e:
    print(f"✗ Prompt loading failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test KPI extraction
print("\n" + "=" * 50)
print("KPI EXTRACTION TEST")
print("=" * 50)
test_text = """
Service Agreement

Contract Type: Software License
Contract Status: Active
Total Contract Value: $500,000
Compliance Score: 92%
Control Coverage: 88%
Data Residency: US Data Centers
Encryption: AES-256
MFA Coverage: 100%
"""

try:
    kpis = ContractAnalyzer.extract_kpis(test_text)
    print("✓ KPI extraction successful")
    import json
    print(json.dumps(kpis, indent=2))
except Exception as e:
    print(f"✗ KPI extraction failed: {e}")
    import traceback
    traceback.print_exc()
