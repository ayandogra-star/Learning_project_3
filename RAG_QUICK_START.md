# RAG System Quick Start

Get the RAG semantic search and LLM analysis features running in 5 minutes.

## Prerequisites

- Python 3.9+
- Azure OpenAI API credentials
- OpenAI API key for embeddings (or use mock mode)

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Key packages:

- `faiss-cpu==1.7.4` - Vector similarity search
- `tiktoken==0.5.2` - Token counting
- `openai==1.43.0` - Embeddings
- `azure-openai==1.3.0` - Azure OpenAI LLM

### 2. Configure Environment

Create `.env` file in `backend/` directory:

```bash
# Azure OpenAI (for LLM generation)
AZURE_OPENAI_API_KEY=your_azure_key_here
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_key_here
```

### 3. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Server runs at: `http://localhost:8000`

---

## Core Workflow

### Step 1: Upload Contract

```bash
# Upload a contract PDF
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

Response:

```json
{
  "file_id": 123,
  "filename": "contract.pdf",
  "status": "processed",
  "kpi_extracted": 15
}
```

**Save the `file_id`** for subsequent RAG queries.

### Step 2: Define Contract Terms

```bash
# Define a specific term
curl -X POST http://localhost:8000/api/rag/define \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Personal Information",
    "file_id": 123
  }'
```

Response includes:

- `definition` - Complete definition from contract
- `key_elements` - Important components
- `compliance_requirements` - Relevant regulations
- `related_sections` - Cross-references
- `confidence` - LLM confidence score

### Step 3: Query Compliance & Risk

```bash
# Ask about compliance requirements
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What compliance requirements apply?",
    "file_id": 123,
    "query_type": "compliance"
  }'
```

Query types:

- `definition` - Extract term definition
- `section` - Find specific contract section
- `compliance` - Identify compliance obligations
- `risk` - Identify risks and liabilities

### Step 4: Raw Retrieval (Optional)

```bash
# Get raw chunks without LLM processing
curl "http://localhost:8000/api/rag/retrieve?file_id=123&query=security&top_k=5"
```

---

## System Architecture

```
┌─────────────────┐
│  Upload PDF     │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│  PDFParser (Extract Text)    │
└────────┬─────────────────────┘
         │
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
    ┌────────────────┐                 ┌──────────────────┐
    │  KPI Extraction│                 │ RAG Processing   │
    │  (Existing)    │                 │ (New)            │
    └────────────────┘                 └────────┬─────────┘
                                                 │
                                    ┌────────────┴────────────┐
                                    │                         │
                            ┌───────▼─────────┐    ┌─────────▼──────┐
                            │ PDFPlumber Tables│    │ Semantic Chunker│
                            │ + Merging        │    │ + Boosting      │
                            └────────┬─────────┘    └────────┬────────┘
                                     │                       │
                                     └───────────┬───────────┘
                                                 │
                                        ┌────────▼────────┐
                                        │ Embeddings API  │
                                        │ (OpenAI)        │
                                        └────────┬────────┘
                                                 │
                          ┌──────────────────────▼──────────────────────┐
                          │  FAISS Vector Store (Similarity Search)     │
                          │  - 1536-dimensional embeddings              │
                          │  - L2 distance metric                       │
                          │  - Relevance boosting (1.0-2.0x)           │
                          └──────────────────────┬──────────────────────┘
                                                 │
                          ┌──────────────────────▼──────────────────────┐
                          │  Azure OpenAI GPT-4o (LLM)                  │
                          │  - Definition generation                    │
                          │  - Section explanation                      │
                          │  - Compliance analysis                      │
                          │  - Risk assessment                          │
                          └──────────────────────────────────────────────┘
```

---

## Test the System

### Run Integration Tests

```bash
cd backend
python test_rag_integration.py
```

Expected output:

```
✅ Document Extraction: PASSED
✅ Semantic Chunking: PASSED
✅ Table Formatting: PASSED
✅ Vector Store Operations: PASSED
✅ RAG Pipeline: PASSED
✅ Retrieval Ranking: PASSED
✅ Error Handling: PASSED

✅ ALL TESTS PASSED - RAG SYSTEM IS READY!
```

### Test Endpoints

```bash
# 1. Upload a test contract
RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload \
  -F "file=@backend/create_test_pdf.py")
FILE_ID=$(echo $RESPONSE | jq '.file_id')

# 2. Define a term
curl -X POST http://localhost:8000/api/rag/define \
  -H "Content-Type: application/json" \
  -d "{\"term\": \"Service\", \"file_id\": $FILE_ID}"

# 3. Query compliance
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What services are provided?\", \"file_id\": $FILE_ID, \"query_type\": \"section\"}"
```

---

## Key Features

### 1. Multi-Page Table Handling

- Automatically detects and merges tables spanning multiple pages
- Preserves table structure in embeddings
- Formats as readable text for LLM context

### 2. Semantic Chunking

- Section-based splitting (not naive token counting)
- Paragraph-aware boundaries
- Maintains document hierarchy
- Target chunk size: 300-800 tokens

### 3. Relevance Boosting

Automatically increases ranking priority for:

- **Definition Sections** (1.5x) - Sections 2-3 with "means" or "defined as"
- **Tables** (1.3x) - Structured data with high information density
- **Security Keywords** (1.2x) - compliance, security, encryption, audit, etc.

### 4. LLM Generation

Azure OpenAI GPT-4o powers:

- Contextual term definitions
- Compliance requirement extraction
- Risk assessment
- Section explanations

All generated content is grounded in retrieved document chunks—no hallucination.

---

## Configuration

### Vector Store Settings

File: `backend/app/services/vector_store.py`

```python
# Settings (adjust as needed)
EMBEDDING_DIMENSION = 1536      # Match OpenAI text-embedding-3-small
FAISS_INDEX_TYPE = "HNSW"       # Hierarchical NSW for faster search
L2_DISTANCE_METRIC = True       # Euclidean distance
SIMILARITY_THRESHOLD = 0.3      # Minimum similarity to include
TOP_K_RETRIEVAL = 5             # Default chunks retrieved
```

### Semantic Chunking Settings

File: `backend/app/services/semantic_chunker.py`

```python
# Settings
TARGET_TOKEN_COUNT = 500        # Target tokens per chunk
MIN_TOKEN_COUNT = 100           # Minimum chunk size
MAX_TOKEN_COUNT = 1000          # Maximum chunk size
OVERLAP_TOKENS = 50             # Prevent semantic gaps
```

### LLM Settings

File: `backend/app/services/contract_definition_generator.py`

```python
# Settings
TEMPERATURE = 0                 # Deterministic responses
MAX_TOKENS = 1000              # Maximum response length
SYSTEM_PROMPT_WARNING = True   # Enforce "use only provided context"
```

---

## Troubleshooting

### Issue: "Vector store not initialized"

```
Solution: Contract is still processing. Wait 10-30 seconds and retry.
```

### Issue: "Empty response from Azure OpenAI"

```
Solution:
1. Check AZURE_OPENAI_API_KEY is set: echo $AZURE_OPENAI_API_KEY
2. Verify endpoint format includes trailing slash
3. Confirm deployment name matches Azure console
```

### Issue: "No relevant chunks found"

```
Solution:
1. Try more specific search terms
2. Check contract was uploaded: GET /api/status
3. Verify file_id is correct
4. Test with broader queries
```

### Issue: Slow Response Times

```
Solution:
1. Reduce top_k parameter (fewer chunks to process)
2. Use raw retrieval endpoint (/api/rag/retrieve) instead of LLM
3. Check network latency to Azure OpenAI
```

---

## Performance Metrics

| Operation            | Time         | Notes                              |
| -------------------- | ------------ | ---------------------------------- |
| PDF Upload           | 2-5s         | Depends on file size               |
| Text Extraction      | 1-3s         | PDFPlumber parsing                 |
| Table Merging        | 500ms        | Two-pass algorithm                 |
| Semantic Chunking    | 1-2s         | Tiktoken counting + NLTK splitting |
| Embedding Generation | 2-5s         | OpenAI API batched                 |
| Vector Indexing      | 500ms        | FAISS index build                  |
| Definition Query     | 1-2s         | Retrieval + LLM generation         |
| Compliance Query     | 800ms - 1.5s | Depends on LLM response            |
| Raw Retrieval        | 50-100ms     | FAISS search only                  |

---

## Production Checklist

Before deploying to production:

- [ ] **Environment Variables**: All Azure/OpenAI keys set and tested
- [ ] **FAISS Index Backup**: Regular backups of vector_store/ folder
- [ ] **Monitoring**: Track API response times and error rates
- [ ] **Rate Limiting**: Implement if serving high-volume traffic
- [ ] **Caching**: Cache common definitions to reduce LLM calls
- [ ] **Error Handling**: Test graceful degradation on API failures
- [ ] **Security**: Store API keys in secure vault, not .env files
- [ ] **Testing**: Run integration tests against production data
- [ ] **Documentation**: Document custom configuration changes
- [ ] **Feedback Loop**: Monitor LLM responses for quality

---

## Next Steps

1. **Start Backend**: `python -m uvicorn app.main:app --reload`
2. **Upload Test Contract**: Use Postman or cURL
3. **Run Integration Tests**: `python test_rag_integration.py`
4. **Define Terms**: Start with `/api/rag/define` endpoint
5. **Query Compliance**: Use `/api/rag/query` with compliance type
6. **Integrate Frontend**: Build React components calling endpoints
7. **Monitor Performance**: Track response times and accuracy
8. **Optimize**: Fine-tune boosting multipliers based on results

---

## Additional Resources

- [RAG System Documentation](RAG_SYSTEM_DOCUMENTATION.md)
- [RAG API Usage Guide](RAG_API_USAGE_GUIDE.md)
- [Backend Readme](backend/README.md)
- [Azure OpenAI Setup](AZURE_ENV_EXAMPLE.md)

---

## Support

For issues or questions:

1. Check logs: `backend/app/logs/` (if logging configured)
2. Run diagnostics: `python backend/test_rag_integration.py`
3. Review error handling in [RAG_SYSTEM_DOCUMENTATION.md](RAG_SYSTEM_DOCUMENTATION.md#error-handling)
4. Check Azure OpenAI connection with diagnostic script:
   ```bash
   python backend/test_azure_connection.py
   ```
