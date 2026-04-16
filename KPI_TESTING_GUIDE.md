# KPI Extraction Testing Guide

## Quick Commands

### Enable Debugging

```bash
cd backend
# Edit .env and set DEBUG=true
# or just for one run:
DEBUG=true python example_usage.py
```

### Test 1: Basic KPI Extraction (No PDF needed)

```bash
cd backend
python example_usage.py
```

Expected output:

```
0. Checking Environment Variables
✓ All environment variables are configured!

1. Testing System Prompt...
[System prompt content...]

2. Testing Direct Contract Analysis...
✓ Analysis successful!
✓ Extracted 14 out of 18 KPIs

3. Verifying All KPI Fields...
✓ All expected fields present!

4. To test PDF parsing, run:
   python example_usage.py /path/to/contract.pdf
```

### Test 2: PDF-based KPI Extraction

```bash
cd backend
python example_usage.py /path/to/contract.pdf
```

Expected output:

```
0. Checking Environment Variables
✓ All environment variables are configured!

4. Testing PDF Parser with Contract Analysis
[DEBUG] Parsing PDF: /path/to/contract.pdf
[DEBUG] PDF has 5 pages
[DEBUG] Total extracted text: 12456 characters
[DEBUG] Starting KPI extraction...
[DEBUG] Sending request to Azure OpenAI...
✓ Analysis complete!

Extracted KPIs:
{
  "totalContractsProcessed": "1",
  "contractType": "Service Agreement",
  ...
  "mfaCoverage": "100%"
}
```

### Test 3: Full Server with API

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Upload contract via API
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"

# Get analytics
curl http://localhost:8000/api/dashboard/metrics
```

## Debug Mode Options

### Production (No Debug Logs)

```env
DEBUG=false
```

Output: Clean, minimal logging
Best for: Production servers

### Development (With Debug Logs)

```env
DEBUG=true
```

Output: Verbose step-by-step logs
Shows: File sizes, character counts, API calls, JSON parsing
Best for: Testing and troubleshooting

## What Gets Logged When DEBUG=true

### PDF Parsing Logs

- File path and size
- Number of pages
- Characters extracted per page
- Total text length

### Azure OpenAI Logs

- Endpoint and API version
- Client initialization status
- Request being sent
- Response received
- Response length and preview
- JSON parsing status

### Error Logs (Always Shown)

- File not found errors
- API authentication errors
- Invalid JSON responses
- System prompt not found errors
- PDF parsing failures

## Troubleshooting with Debug Mode

1. **Enable debugging:**

```bash
DEBUG=true python example_usage.py /path/to/contract.pdf
```

2. **Look for these markers:**
   - `✓` = Success, continue
   - `✗` = Failed, stop here
   - `[ERROR]` = Problem that needs fixing
   - `[WARNING]` = Non-fatal issue
   - `[DEBUG]` = Detailed info (only when DEBUG=true)

3. **Common issue paths:**

**Issue: Environment check fails**

- Check .env file exists in backend/
- Verify all Azure credentials are set
- API key should be 32+ characters

**Issue: PDF parsing shows 0 characters**

- PDF might be image-based
- PDF might be corrupted
- Try different PDF file

**Issue: JSON parsing fails**

- Azure OpenAI returned an error
- Check deployment exists in Azure
- Verify API key is valid
- Wait if rate-limited

4. **Save the debug output:**

```bash
DEBUG=true python example_usage.py /path/to/contract.pdf > debug_output.txt 2>&1
```

Then review `debug_output.txt` for all details.

## Performance Expectations

| Operation         | Time  | Notes                   |
| ----------------- | ----- | ----------------------- |
| Sample analysis   | < 1s  | No network, local JSON  |
| PDF parsing       | 1-5s  | Depends on PDF size     |
| Azure OpenAI call | 2-10s | Depends on text length  |
| Total end-to-end  | 3-15s | Typical with small PDFs |

If analysis takes > 30 seconds:

- Check internet connection
- Verify Azure service is responsive
- Check system isn't throttled

## File Requirements

For PDF testing, file should:

- Be in PDF format (.pdf)
- Be text-based (not scanned images)
- Contain contract text
- Be under 50MB (Azure limit)

Example PDF content that works:

```
SERVICE AGREEMENT

This agreement dated January 1, 2024...
- Contract Value: $500,000
- Duration: 24 months
- MFA Required: Yes
- Encryption: AES-256
```

## Next Steps

1. **Test locally first:**

   ```bash
   python example_usage.py  # With debug output
   ```

   View extracted KPIs to verify system works

2. **Test with your PDF:**

   ```bash
   python example_usage.py /path/to/your/contract.pdf
   ```

   Verify KPIs are correctly extracted from your contract

3. **Start server for production:**

   ```bash
   # Set DEBUG=false for production
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Upload via API:**
   ```bash
   curl -X POST http://localhost:8000/api/upload \
     -F "file=@contract.pdf"
   ```

## Support

If you're still seeing issues:

1. Run with `DEBUG=true`
2. Save full output to file
3. Check these files exist:
   - `backend/.env` (with credentials)
   - `backend/app/prompts/kpi_prompt.txt` (system prompt)
   - `backend/app/services/contract_analyzer.py`
   - `backend/app/services/pdf_parser.py`

4. Verify Azure resources:
   - OpenAI resource exists
   - gpt-4o deployment is running
   - API key hasn't expired
   - Quota isn't exceeded
