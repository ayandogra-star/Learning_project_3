# Diagnostic Guide: KPI Extraction Troubleshooting

## Quick Start: Test KPI Extraction

### Test 1: With Sample Contract (No PDF Required)

```bash
cd backend
python example_usage.py
```

This runs 3 tests:

1. **Environment Check**: Validates Azure OpenAI credentials
2. **System Prompt Check**: Ensures KPI prompt is loaded
3. **Sample Analysis**: Tests with built-in sample contract
4. **KPI Field Validation**: Verifies all 18 KPI fields

### Test 2: With Real PDF

```bash
cd backend
python example_usage.py /path/to/contract.pdf
```

This adds: 4. **PDF Parsing**: Extracts text from your PDF 5. **Full Analysis**: Sends extracted text to GPT-4o 6. **KPI Extraction**: Views actual KPIs from your contract

## Debug Output Explained

When `DEBUG=true` in `.env`, you'll see detailed logs:

### PDF Parser Debug Output

```
[DEBUG] Parsing PDF: /path/to/contract.pdf
[DEBUG] File size: 45678 bytes
[DEBUG] PDF has 5 pages
[DEBUG] Extracted 2345 characters from page 1
[DEBUG] Extracted 1890 characters from page 2
...
[DEBUG] Total extracted text: 12456 characters
```

### Contract Analyzer Debug Output

```
[DEBUG] Starting KPI extraction...
[DEBUG] Text length: 12456 characters
[DEBUG] System prompt loaded (2847 characters)
[DEBUG] Azure client initialized
[DEBUG] Using deployment: gpt-4o
[DEBUG] Sending request to Azure OpenAI...
[DEBUG] Response received from Azure OpenAI
[DEBUG] Response text length: 1203 characters
[DEBUG] Response preview: {"totalContractsProcessed": "1", ...
[DEBUG] Parsing JSON response...
[DEBUG] JSON parsed successfully (18 KPI fields)
```

## Troubleshooting Common Issues

### Issue 1: Environment Variables Not Set

**Error Message:**

```
✗ Azure OpenAI API Key               NOT SET
✗ Azure OpenAI Endpoint URL          NOT SET
```

**Solution:**

- Check `.env` file exists in `backend/` directory
- Verify all Azure credentials are present
- Endpoint must end with `/`: `https://resource.openai.azure.com/`
- Restart example_usage.py after updating .env

### Issue 2: PDF File Not Found

**Error Message:**

```
[ERROR] File not found: PDF file not found: /path/to/contract.pdf
```

**Solution:**

- Check file path is correct
- Use absolute path: `/Users/ayandogra/Documents/contract.pdf`
- Ensure PDF file exists before running test

### Issue 3: PDF Text Extraction Returns Empty

**Error Message:**

```
[WARNING] No text extracted from PDF - file may be image-only
```

**Causes:**

- PDF is image-based (scanned document)
- PDF is encrypted or corrupted
- PDF uses unsupported encoding

**Solution:**

- Try converting PDF to text using Adobe or online tools
- Ensure PDF is text-based, not scanned images
- Check PDF file isn't corrupted

### Issue 4: Invalid JSON Response from GPT-4o

**Error Message:**

```
[ERROR] Invalid JSON response: Expecting value: line 1 column 1 (char 0)
[ERROR] Raw response: Error message from API...
```

**Causes:**

- GPT-4o returned an error instead of JSON
- API rate limit exceeded
- Deployment not found
- Insufficient quota

**Solution:**

- Check Azure Portal → OpenAI → Deployments
- Verify `gpt-4o` deployment exists
- Check API key is valid
- Wait before retrying if rate limited

### Issue 5: Azure Authentication Failed

**Error Message:**

```
[ERROR] Exception during analysis: AuthenticationError: ...
```

**Causes:**

- Invalid API key
- API key expired
- Wrong endpoint URL

**Solution:**

- Get fresh API key from Azure Portal
- Verify endpoint: `https://your-resource.openai.azure.com/`
- Check no typos in .env file

## Environment Variables Reference

Create `.env` in `backend/` with these variables:

```env
# Required for Azure OpenAI
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Enable verbose debugging (optional)
DEBUG=true

# Server settings (optional, defaults shown)
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## How to Get Azure Credentials

1. **Go to Azure Portal**: https://portal.azure.com
2. **Find OpenAI Resource**: Search for "OpenAI" or go to your resource group
3. **Click on resource** → "Keys and Endpoint" in left sidebar
4. **Copy values:**
   - **Key 1 or Key 2** → `AZURE_OPENAI_API_KEY`
   - **Endpoint** → `AZURE_OPENAI_ENDPOINT`
5. **Get Deployment Name**: From "Deployments" menu (usually "gpt-4o")
6. **API Version**: Use `2024-12-01-preview` or latest stable

## Expected Output: Successful Analysis

When everything works, you'll see:

```
✓ All environment variables are configured!

[DEBUG] Parsing PDF: /path/to/contract.pdf
[DEBUG] Total extracted text: 5234 characters

[DEBUG] Starting KPI extraction...
[DEBUG] Sending request to Azure OpenAI...
[DEBUG] Response received from Azure OpenAI
[DEBUG] JSON parsed successfully (18 KPI fields)

✓ Analysis successful!
✓ Extracted 14 out of 18 KPIs

Extracted KPIs:
{
  "totalContractsProcessed": "1",
  "contractType": "Service Agreement",
  "contractStatus": "Active",
  ...
  "mfaCoverage": "100%"
}
```

## Performance Notes

- **Sample analysis**: < 1 second
- **PDF parsing**: 1-5 seconds (depends on PDF size)
- **GPT-4o analysis**: 2-10 seconds (depends on text length)
- **Total end-to-end**: 3-15 seconds typically

If analysis takes much longer:

- Check network connection
- Verify Azure service isn't throttled
- Check system resources

## Disabling Debug Output

In production (when not debugging), set `DEBUG=false` in `.env`:

```env
DEBUG=false
```

This removes verbose logs and keeps output clean for your application.

## Still Not Working?

1. Run with `DEBUG=true`
2. Copy the full error message
3. Check logs mention file paths and sizes
4. Verify Azure OpenAI deployment exists
5. Test with sample contract first (no PDF)
6. Then test with simple PDF file

Common: Authentication fails → Check API key

Unlikely: System prompt not found → File structure issue

## File Structure Expected

```
backend/
├── .env                    ← Your credentials here
├── example_usage.py        ← Run this to test
├── app/
│   ├── services/
│   │   ├── contract_analyzer.py
│   │   └── pdf_parser.py
│   └── prompts/
│       └── kpi_prompt.txt   ← System prompt
└── requirements.txt
```

If any file is missing, example_usage.py will report `FileNotFoundError`.
