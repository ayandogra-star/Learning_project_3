# Azure OpenAI Migration Guide

## Overview

The contract analysis system has been updated to use Azure OpenAI services instead of direct OpenAI API access.

## What Changed

### Environment Variables

**Old (OpenAI):**

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

**New (Azure OpenAI):**

```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### Code Changes

- Import changed: `from openai import OpenAI` → `from openai import AzureOpenAI`
- Client initialization now includes `api_version` and `azure_endpoint`
- Model parameter replaced with `deployment_name` parameter
- Error messages updated to reference Azure OpenAI

### Files Modified

- `.env.example` - Updated environment template
- `app/services/contract_analyzer.py` - Azure OpenAI client integration
- Documentation files updated with Azure-specific instructions

## Migration Steps

### 1. Update Environment File

```bash
cd backend
# Delete or backup old .env
rm .env
# Copy new template
cp .env.example .env
```

### 2. Get Azure Credentials

1. Go to Azure Portal
2. Find your OpenAI resource
3. Click "Keys and Endpoint"
4. Copy:
   - Key (API_KEY)
   - Endpoint URL
5. Note your GPT-4o deployment name

### 3. Configure .env

Edit `backend/.env`:

```env
AZURE_OPENAI_API_KEY=paste-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 4. Verify Installation

Dependencies remain the same - the `openai` package supports both APIs:

```bash
pip install -r requirements.txt
```

### 5. Test Connection

```bash
cd backend
python example_usage.py
```

## Benefits of Azure OpenAI

✅ Enterprise-grade security and compliance
✅ Private endpoint support
✅ Integrated with Azure ecosystem
✅ Granular access control
✅ Audit logging and compliance tools
✅ Same Python SDK compatibility
✅ Optional GPU acceleration options

## API Compatibility

The Python code now uses:

- `AzureOpenAI` client instead of `OpenAI`
- Deployment names instead of model names
- Azure-specific error handling
- Same chat completion interface

All existing functionality remains the same - only the underlying API endpoint changes.

## Troubleshooting

### "Invalid endpoint" error

- Ensure URL ends with `/`: `https://resource.openai.azure.com/`
- Check resource exists in Azure Portal
- Verify correct region

### "Invalid deployment" error

- Check deployment name in Azure Portal matches exactly
- Ensure GPT-4o is deployed in your resource
- Verify deployment is in the same region as endpoint

### "Authentication failed" error

- Verify API key is correct in Azure Portal
- Check key hasn't expired
- Try regenerating key in Azure Portal

### "Model not available" error

- Ensure GPT-4o is deployed
- Check deployment status in Azure Portal
- Verify quota isn't exceeded

## Reverting to Standard OpenAI (if needed)

To revert back to standard OpenAI:

1. Update `.env`:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
```

2. Restore `contract_analyzer.py` to use `OpenAI` client:

```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# In extract_kpis:
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL"),
    ...
)
```

3. Reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Documentation Updates

All documentation has been updated to reflect Azure OpenAI:

- `SETUP_GPT4o_CONTRACT_ANALYSIS.md` - Setup guide
- `backend/CONTRACT_ANALYSIS_INTEGRATION.md` - Technical documentation
- `VERIFICATION_CHECKLIST.md` - Implementation checklist

## Support

For Azure OpenAI issues: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/
For deployment help: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource
