from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pathlib import Path

# Create uploads directory
Path("uploads").mkdir(exist_ok=True)

# Create a test contract PDF
pdf_path = Path("uploads/test_contract.pdf")
c = canvas.Canvas(str(pdf_path), pagesize=letter)

# Add contract text
text = """SERVICE AGREEMENT

Contract Type: Software License Agreement
Contract Status: Active
Total Contract Value: $500,000

This agreement is entered into between Party A and Party B for the provision of cloud services.

Compliance Requirements:
- Data Residency Compliance: US Data Centers Required
- Encryption Compliance: AES-256 Encryption Required
- MFA Coverage: 100% for Admin Accounts

Risk Management:
- High Risk Issues Count: 2
- Open Risks Count: 1
- Average Time to Remediate: 5 days

Obligations:
- Total Obligations Extracted: 12
- Obligations Completion Rate: 85%

Performance Metrics:
- Clause Extraction Accuracy: 95%
- Average Processing Time: 2 seconds
- Total Contracts Processed: 10

Financial Risk:
- Revenue at Risk: $50,000
- Compliance Score: 92%
- Control Coverage Percentage: 88%
- Incident Readiness Score: 87%

Upcoming Expirations: 2026-12-31"""

y = 750
for line in text.split('\n'):
    if line.strip():
        c.drawString(40, y, line[:80])
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

c.save()
print(f"Created test PDF: {pdf_path}")
