#!/usr/bin/env python3
"""Create a test PDF with actual contract content."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path

Path("app/uploads").mkdir(exist_ok=True)

pdf_path = Path("app/uploads/test_real_contract.pdf")
c = canvas.Canvas(str(pdf_path), pagesize=letter)

# Add real contract content
text = """SERVICE LEVEL AGREEMENT

PARTIES:
This Service Level Agreement ("Agreement") is entered into between Acme Corporation ("Client") and CloudTech Solutions Inc. ("Provider"), effective as of April 1, 2026.

CONTRACT DETAILS:
Contract Type: Software License and Support Agreement
Contract Status: Active
Contract Duration: 36 months
Total Contract Value: $2,500,000

COMPLIANCE AND SECURITY REQUIREMENTS:
Compliance Score: 95%
Control Coverage Percentage: 92%
Data Residency Compliance: All data shall be stored in US East Region data centers compliant with HIPAA regulations
Encryption Compliance: All data must be encrypted using AES-256 encryption at rest and TLS 1.3 in transit
MFA Coverage: Two-factor authentication required for all administrative accounts (100% coverage)

INCIDENT AND RISK MANAGEMENT:
Incident Readiness Score: 88%
High Risk Issues Count: 3 critical vulnerabilities identified
Open Risks Count: 2 open risks under active remediation
Average Time to Remediate: 14 days

SERVICE OBLIGATIONS:
Total Obligations Extracted: 24 obligations
Obligations Completion Rate: 96%
Average Processing Time: 0.5 seconds per transaction
Clause Extraction Accuracy: 97%

FINANCIAL TERMS:
Revenue at Risk: $250,000 if SLA breaches >10%

RENEWAL DATES:
Upcoming Expirations: March 31, 2029

PERFORMANCE METRICS:
Total Contracts Processed: 145 contracts under this framework

Key Terms: Software licensing, support services, SLA, compliance, security
"""

y = 750
lines = text.split('\n')
for line in lines:
    if line.strip():
        # Wrap long lines
        if len(line) > 80:
            c.drawString(40, y, line[:80])
            y -= 12
            c.drawString(40, y, line[80:])
            y -= 12
        else:
            c.drawString(40, y, line)
            y -= 12
        if y < 50:
            c.showPage()
            y = 750

c.save()
print(f"✓ Created test contract: {pdf_path}")
print(f"  This PDF contains all 18 KPI fields for testing")
