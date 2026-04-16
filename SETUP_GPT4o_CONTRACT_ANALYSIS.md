# Quick Setup Guide - Contract Analysis with Azure OpenAI GPT-4o

## Prerequisites

- Python 3.8+
- Azure OpenAI account with GPT-4o deployment
- Azure OpenAI API key, endpoint, and deployment name

## Step 1: Set Up Backend Environment

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Azure OpenAI

Create `.env` file in `backend/` directory:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Azure OpenAI credentials
```

Edit `.env` with your Azure OpenAI details:

```env
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

**Where to find these values:**

1. Go to Azure Portal → OpenAI resource
2. Click "Keys and Endpoint" in left sidebar
3. Copy API Key (key 1 or key 2)
4. Copy Endpoint URL
5. Deployment name is what you named your GPT-4o deployment

## Step 3: Start the Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:

```
Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start the Frontend (In Another Terminal)

```bash
cd frontend
npm install  # If not already done
npm run dev
```

The frontend should open at `http://localhost:5173`

## Step 5: Test Contract Analysis

1. Click "Analyze Contract" button
2. Upload a PDF contract file
3. Wait for analysis to complete (2-3 seconds)
4. View extracted KPIs on the dashboard

## File Structure Added

```
backend/
├── .env.example              # Template for environment variables
├── CONTRACT_ANALYSIS_INTEGRATION.md  # Full documentation
├── requirements.txt          # Updated with openai and pypdf
├── app/
│   ├── prompts/
│   │   └── kpi_prompt.txt   # System prompt for GPT-4o
│   ├── services/
│   │   ├── contract_analyzer.py  # NEW: OpenAI integration
│   │   └── pdf_parser.py         # NEW: PDF text extraction
│   ├── schemas.py            # Updated: camelCase KPI fields
│   ├── models.py             # Updated: KPI storage in FileMetadata
│   └── routes/
│       └── files.py          # Updated: new analysis endpoint
```

## API Endpoints

### Upload and Analyze Contract

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

### Get KPIs for a Contract

```bash
curl http://localhost:8000/api/contracts/1/analysis
```

### Get Dashboard Metrics

```bash
curl http://localhost:8000/api/dashboard/metrics
```

### List All Uploaded Contracts

```bash
curl http://localhost:8000/api/files
```

## Response Format

All KPI values are returned in strict JSON:

```json
{
  "totalContractsProcessed": "1",
  "contractType": "Vendor Agreement",
  "contractStatus": "Active",
  "complianceScore": "92%",
  "controlCoveragePercentage": "88%",
  "incidentReadinessScore": "85%",
  "highRiskIssuesCount": "2",
  "openRisksCount": "5",
  "averageTimeToRemediate": "14 days",
  "totalContractValue": "$500,000",
  "revenueAtRisk": "$50,000",
  "totalObligationsExtracted": "12",
  "obligationsCompletionRate": "91%",
  "upcomingExpirations": "2026-12-31",
  "averageProcessingTime": "2.5s",
  "clauseExtractionAccuracy": "96%",
  "dataResidencyCompliance": "EU compliant",
  "encryptionCompliance": "AES-256 required",
  "mfaCoverage": "100%"
}
```

## Troubleshooting

### "OPENAI_API_KEY not found"

- Ensure all Azure OpenAI environment variables are set in `.env`
- Variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME
- Don't use quotes around values
- Ensure `.env` is in the `backend/` directory

### "Invalid API Key" Error

- Verify AZURE_OPENAI_API_KEY in .env file
- Check credentials in Azure Portal → Keys and Endpoint
- Ensure access isn't restricted by IP/firewall
- Try regenerating the key in Azure Portal

### "Invalid endpoint" Error

- Endpoint must end with trailing slash: `https://your-resource.openai.azure.com/`
- Verify deployment name matches your Azure deployment exactly
- Check region is correct in endpoint URL

### "Invalid deployment" Error

- Verify AZURE_OPENAI_DEPLOYMENT_NAME in .env matches exactly
- Check deployment name in Azure Portal
- Ensure GPT-4o is deployed in your resource

### "Invalid file type"

- Ensure you're uploading PDF, TXT, DOC, or DOCX files
- Check file extension is correct

### "Empty KPI values"

- The contract may not contain specific KPI information
- "Not Present" is the correct response for missing KPIs
- This is expected behavior—don't fabricate values

### Frontend can't reach backend

- Ensure backend is running on port 8000
- Check CORS is enabled (it is by default)
- Verify no firewall blocking localhost:8000

## Next Steps

1. Upload sample contracts to test the system
2. Review extracted KPIs for accuracy
3. Consider implementing caching for large contracts
4. Monitor Azure OpenAI API usage costs
5. Set up production deployment

## Documentation

Full technical documentation: [CONTRACT_ANALYSIS_INTEGRATION.md](./CONTRACT_ANALYSIS_INTEGRATION.md)

## Support

For Azure OpenAI issues: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/
For PyPDF issues: https://github.com/py-pdf/pypdf
