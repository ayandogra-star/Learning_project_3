# GPT-4o Contract Analysis Integration

This document describes the integration of Azure OpenAI's GPT-4o for automated contract KPI extraction.

## Overview

The contract analysis system extracts 18 specific KPIs from uploaded PDF contracts using Azure OpenAI GPT-4o. All KPIs are grounded in the actual PDF content—if a KPI is not found, it's marked as "Not Present."

## Architecture

### Services

#### 1. **ContractAnalyzer** (`app/services/contract_analyzer.py`)

- Integrates with Azure OpenAI GPT-4o API
- Loads system prompt from `app/prompts/kpi_prompt.txt`
- Extracts KPIs from parsed PDF text
- Returns strictly formatted JSON with camelCase keys

#### 2. **PDFParser** (`app/services/pdf_parser.py`)

- Extracts text from PDF files using PyPDF
- Handles multi-page PDFs
- Returns raw text for LLM analysis

#### 3. **FileService** (`app/services/file_service.py`)

- Handles file upload and storage
- Orchestrates PDF parsing and contract analysis
- Caches KPIs with file metadata
- Provides dashboard metrics

### Models

**FileMetadata** - Now includes:

- `id`: Unique file identifier
- `filename`: Original filename
- `file_size`: Size in bytes
- `upload_time`: ISO timestamp
- `processing_time`: Time to analyze (seconds)
- `status`: "completed" or error state
- `kpis`: Extracted KPIs as dictionary

### API Endpoints

#### POST `/api/upload`

Upload a contract and automatically analyze it.

**Response:**

```json
{
  "id": 1,
  "filename": "vendor_agreement.pdf",
  "file_size": 45678,
  "message": "File uploaded and analyzed successfully",
  "upload_time": "2026-04-15T10:30:00",
  "processing_time": 2.5
}
```

#### GET `/api/contracts/{file_id}/analysis`

Get extracted KPIs for a specific contract.

**Response:**

```json
{
  "filename": "vendor_agreement.pdf",
  "kpis": {
    "totalContractsProcessed": "1",
    "contractType": "Vendor Agreement",
    "contractStatus": "Active",
    "complianceScore": "92%",
    ...
  },
  "analysis_timestamp": "2026-04-15T10:30:00",
  "message": "Contract analyzed successfully"
}
```

#### GET `/api/dashboard/metrics`

Get aggregated metrics and the latest contract's KPIs.

#### GET `/api/files`

List all uploaded contracts with their metadata.

## KPIs Extracted

1. **totalContractsProcessed** - Count of contracts analyzed
2. **contractType** - Type/category of contract
3. **contractStatus** - Current status (Active, Expired, etc.)
4. **complianceScore** - Compliance percentage
5. **controlCoveragePercentage** - Security controls coverage
6. **incidentReadinessScore** - Incident response score
7. **highRiskIssuesCount** - Number of high-risk findings
8. **openRisksCount** - Number of open risks
9. **averageTimeToRemediate** - Time to fix issues
10. **totalContractValue** - Contract monetary value
11. **revenueAtRisk** - Potential revenue impact
12. **totalObligationsExtracted** - Number of extracted obligations
13. **obligationsCompletionRate** - Completion percentage
14. **upcomingExpirations** - Expiration dates
15. **averageProcessingTime** - Processing duration
16. **clauseExtractionAccuracy** - Accuracy percentage
17. **dataResidencyCompliance** - Data location compliance
18. **encryptionCompliance** - Encryption status
19. **mfaCoverage** - MFA implementation percentage

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend/` directory:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

Get your credentials from: Azure Portal → OpenAI Resource → Keys and Endpoint

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## How It Works

1. **User Uploads Contract**: POST to `/api/upload` with PDF file
2. **PDF Parsing**: PDFParser extracts text from all pages
3. **AI Analysis**: ContractAnalyzer sends text + system prompt to Azure OpenAI GPT-4o
4. **KPI Extraction**: GPT-4o identifies and extracts KPIs based on contract content
5. **Response**: KPIs stored and returned in strict JSON format

## System Prompt

The system prompt (`app/prompts/kpi_prompt.txt`) instructs GPT-4o to:

- Extract ONLY specified KPIs
- Return "Not Present" for missing values
- Never fabricate or infer information
- Return strict JSON with camelCase field names
- Ground all values in actual PDF text

## Error Handling

- Invalid file types are rejected at upload
- PDF parsing errors result in default "Not Present" values
- API errors are logged but don't fail the response
- All errors return graceful HTTP error responses

## Frontend Integration

The Dashboard component displays KPIs organized by category:

- Contract Overview
- Compliance & Risk
- Risk & Obligations
- Security & Obligations
- Processing & Accuracy

KPIs marked "Not Present" are visually distinguished in gray.

## Example Contract Analysis

For a vendor agreement containing:

```
This Vendor Agreement between Company A and Vendor B is effective from
January 1, 2024 through December 31, 2026. The total contract value is
$500,000. Encryption required: AES-256. MFA required for all access.
```

Extracted KPIs would include:

```json
{
  "contractType": "Vendor Agreement",
  "contractStatus": "Active",
  "totalContractValue": "$500,000",
  "encryptionCompliance": "AES-256 encryption required",
  "mfaCoverage": "MFA required for all access",
  ...
}
```

## Development Notes

- All KPI fields must be present in responses (use "Not Present" for missing values)
- Temperature is set to 0 for deterministic responses
- PDF text extraction may have OCR errors—GPT-4o uses best-effort matching
- Consider implementing caching for frequently analyzed contracts
- Monitor API usage costs due to per-request GPT-4o calls

## Troubleshooting

**"Invalid API Key" Error:**

- Verify AZURE_OPENAI_API_KEY in .env file
- Check key permissions in Azure Portal
- Ensure billing is enabled on Azure account

**"Invalid endpoint" Error:**

- Verify AZURE_OPENAI_ENDPOINT in .env includes trailing slash
- Check endpoint format: `https://your-resource.openai.azure.com/`
- Verify resource exists in correct region

**"Invalid deployment" Error:**

- Verify AZURE_OPENAI_DEPLOYMENT_NAME matches your deployment in Azure
- Check GPT-4o is deployed in your resource

**"PDF parsing failed":**

- Some PDFs may have encoding issues
- Try converting PDF to text externally first
- Check file isn't corrupted

**"Timeout analyzing contract":**

- Large PDFs may exceed timeout
- Consider chunking very large documents
- Monitor network connectivity to Azure OpenAI endpoint

## Future Enhancements

- Batch processing multiple contracts
- Contract comparison and differencing
- Risk-based prioritization
- Integration with contract management systems
- Custom KPI definitions per organization
- Historical trend analysis
