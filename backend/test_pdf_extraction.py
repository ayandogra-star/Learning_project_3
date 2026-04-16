#!/usr/bin/env python3
"""Test PDF extraction directly."""
import sys
sys.path.insert(0, '/Users/ayandogra/Documents/GitHub/Learning_project/backend')

from app.services.pdf_parser import PDFParser
from app.services.contract_analyzer import ContractAnalyzer
from pathlib import Path

pdf_path = Path("/Users/ayandogra/Documents/GitHub/Learning_project/backend/app/uploads/Contract_Analyzer_Assignment_new.pdf")

print("=" * 60)
print("PDF EXTRACTION DIAGNOSTICS")
print("=" * 60)

# Check if file exists
if not pdf_path.exists():
    print(f"✗ File not found: {pdf_path}")
    sys.exit(1)

print(f"✓ File found: {pdf_path.name} ({pdf_path.stat().st_size} bytes)")

# Try to extract text
print("\n" + "=" * 60)
print("EXTRACTING TEXT FROM PDF")
print("=" * 60)

try:
    text = PDFParser.extract_text(pdf_path)
    print(f"✓ Text extracted successfully ({len(text)} characters)")
    print(f"\nFirst 300 characters:\n{text[:300]}")
    print(f"\n... (truncated) ...\n")
except Exception as e:
    print(f"✗ Error extracting text: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try to extract KPIs
print("\n" + "=" * 60)
print("EXTRACTING KPIs FROM TEXT")
print("=" * 60)

try:
    kpis = ContractAnalyzer.extract_kpis(text)
    import json
    print("✓ KPIs extracted successfully")
    print(json.dumps(kpis, indent=2))
except Exception as e:
    print(f"✗ Error extracting KPIs: {e}")
    import traceback
    traceback.print_exc()
