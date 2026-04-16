# Complete Azure OpenAI .env Configuration Example

# This file shows exactly how to configure your environment for Azure OpenAI

# ============================================================================

# AZURE OPENAI CONFIGURATION

# ============================================================================

# Your Azure OpenAI API Key

# Found in: Azure Portal → Your OpenAI Resource → Keys and Endpoint → "Key 1" or "Key 2"

# Format: copy the full key as-is

AZURE_OPENAI_API_KEY=12345abcde67890xyz1234567890abcdef

# Your Azure OpenAI Endpoint (Resource URL)

# Found in: Azure Portal → Your OpenAI Resource → Keys and Endpoint → "Endpoint"

# IMPORTANT: Must end with trailing slash /

# Format: https://[resource-name].openai.azure.com/

AZURE_OPENAI_ENDPOINT=https://my-company-openai.openai.azure.com/

# API Version (Stay with 2024-02-15-preview for latest features)

# Options: 2024-02-15-preview, 2024-02-01-preview, 2023-12-01-preview, etc.

# Recommended: Use the latest stable version

AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Deployment Name

# This is the name you gave to your GPT-4o deployment in Azure

# Found in: Azure Portal → OpenAI Resource → Deployments → [Your Deployment Name]

# Example names: "gpt-4o", "gpt-4o-prod", "contract-analyzer", etc.

AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# ============================================================================

# SERVER CONFIGURATION (Optional - defaults work for local development)

# ============================================================================

# Server host (0.0.0.0 = accessible from any network interface)

SERVER_HOST=0.0.0.0

# Server port (default: 8000)

SERVER_PORT=8000

# ============================================================================

# STEP-BY-STEP: How to fill in these values

# ============================================================================

# 1. Get API Key:

# - Open Azure Portal (portal.azure.com)

# - Find your OpenAI resource (search: "openai")

# - Click on your resource

# - Go to "Keys and Endpoint" in left sidebar

# - Copy "Key 1" or "Key 2" → paste as AZURE_OPENAI_API_KEY

# 2. Get Endpoint:

# - In the same "Keys and Endpoint" page

# - Copy "Endpoint" URL

# - Make sure it ends with / → paste as AZURE_OPENAI_ENDPOINT

# 3. Get API Version:

# - Use: 2024-02-15-preview

# - This is the latest stable version with good feature support

# 4. Get Deployment Name:

# - Still in Azure Portal

# - Go to "Deployments" in left sidebar

# - Look for your GPT-4o deployment

# - Copy the deployment name → paste as AZURE_OPENAI_DEPLOYMENT_NAME

# ============================================================================

# EXAMPLE VALUES

# ============================================================================

# If you see values like these, you're in the right place:

#

# AZURE_OPENAI_API_KEY=f8d9e2c4a1b6c3e5f7a2b4d6c8e9f1a3

# AZURE_OPENAI_ENDPOINT=https://mycompany-openai.openai.azure.com/

# AZURE_OPENAI_API_VERSION=2024-02-15-preview

# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-deployment

# ============================================================================

# IMPORTANT NOTES

# ============================================================================

# ⚠️ Never commit this file to git! Keep it private.

# ⚠️ Endpoint MUST have trailing slash (/)

# ⚠️ API Key should start with 32+ alphanumeric characters

# ⚠️ Use Key 1 or Key 2 from Azure Portal, not any other key

# ✅ Deployment name is case-sensitive

# ✅ Always verify each value has been copied correctly

# ============================================================================

# Quick Verification

# ============================================================================

# To verify your configuration is correct:

# cd backend

# python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'OK' if os.getenv('AZURE_OPENAI_API_KEY') else 'MISSING'); print('Endpoint:', 'OK' if os.getenv('AZURE_OPENAI_ENDPOINT') else 'MISSING'); print('Deployment:', 'OK' if os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME') else 'MISSING')"

# ============================================================================
