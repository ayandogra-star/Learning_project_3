# RAG System - Frequently Asked Questions & Troubleshooting

## Overview

The RAG (Retrieval-Augmented Generation) system is now fully integrated into your FastAPI backend. It automatically processes uploaded documents (TXT, PDF, DOC, DOCX) and makes them searchable via semantic vector similarity.

## How the RAG System Works

### 1. Document Upload → Processing Pipeline

When you upload a file via `POST /api/upload`:

1. File is saved to disk
2. KPI extraction runs (contract analysis)
3. **RAG Pipeline automatically triggers** for PDF/TXT/DOCX files
4. Document chunks are created and embeddings generated
5. Chunks stored in local FAISS vector database

### 2. Semantic Chunking

Documents are split into chunks (300-800 tokens each):

- Preserves logical sections (headings, paragraphs)
- Keeps content together when possible
- Tracks page numbers and section titles
- Stores tables as separate chunks

### 3. Vector Database

Uses local FAISS (no external dependencies):

- Stores at: `backend/app/vector_store/`
- Contains: `faiss.index` (vectors) + `metadata.json` (chunk data)
- Persists across backend restarts
- Can query across one or all files

## API Endpoints

### Get Chunks for a File

```bash
GET /api/rag/{file_id}
```

Returns all chunks with content for a specific file.

**Response:**

```json
{
  "file_id": 1,
  "filename": "contract.txt",
  "total_chunks": 5,
  "chunks": [
    {
      "vector_id": 0,
      "chunk_id": "file_1_p1_0",
      "content": "Full chunk text here...",
      "content_type": "text",
      "metadata": { "page_number": 1, "section_title": "PAYMENT TERMS" },
      "content_length": 847,
      "token_count": 213
    }
  ],
  "rag_metadata": {
    "chunks_created": 5,
    "embeddings_added": 5,
    "processing_status": "completed",
    "details": { "text_chunks": 5, "table_chunks": 0, "total_pages": 1 }
  }
}
```

### Search Across Chunks

```bash
POST /api/rag/search
Content-Type: application/json

{
  "query": "payment terms",
  "file_id": 1,
  "top_k": 5
}
```

**Response:**

```json
[
  {
    "vector_id": 0,
    "chunk_id": "file_1_p1_0",
    "file_id": 1,
    "similarity_score": 0.95,
    "metadata": { "page_number": 1, "section_title": "PAYMENT TERMS" }
  }
]
```

### Retrieve Chunks

```bash
GET /api/rag/retrieve?query=payment&file_id=1&top_k=5
```

Alternative to POST /api/rag/search using query parameters.

## File Upload Status

When you upload a file, check the RAG metadata:

```bash
curl http://localhost:8000/api/rag/{file_id}
```

Fields to watch:

- `processing_status`: "pending" → "processing" → "completed" or "failed"
- `chunks_created`: Number of semantic chunks extracted
- `embeddings_added`: Number of embeddings stored (should equal/near chunks_created)
- `details.text_chunks`: Text vs table chunks
- `details.total_pages`: Multi-page documents tracked

## Embeddings: Real vs Mock

### Current Status

The system uses **mock embeddings** for testing because:

- Azure OpenAI doesn't have `text-embedding-3-small` deployment
- Standard OpenAI API key (`sk-...`) not configured

### To Enable Real Embeddings

Add to `.env`:

```
OPENAI_API_KEY=sk-your-real-openai-key-here
```

The system will automatically:

1. Detect the key
2. Use real OpenAI text-embedding-3-small embeddings
3. Fall back to mock if API fails

**Note:** Mock embeddings work for testing. They're deterministic (same query = same embedding) but not semantically meaningful. Real embeddings provide actual semantic similarity.

## Testing the RAG System

### 1. Upload a document

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.txt"
```

### 2. Check processing status

```bash
curl http://localhost:8000/api/rag/1
```

Look for `"processing_status": "completed"` and `"embeddings_added" > 0`

### 3. Search the document

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "payment", "file_id": 1, "top_k": 5}'
```

### 4. Verify KPIs still extract

```bash
curl http://localhost:8000/api/files/1
```

Both KPIs and RAG metadata should be present.

## Troubleshooting

### "embeddings_added": 0

**Cause:** Chunks were created but embeddings failed silently.
**Fix:** Check backend logs for embedding errors. If using Azure, make sure OPENAI_API_KEY is set.

### "total_chunks": 0

**Cause:** Document processing failed or produced no chunks.
**Fix:** Check document format (TXT/PDF/DOCX). Verify file isn't corrupt.

### Search returns empty results

**Cause:**

- File_id doesn't exist
- Query embedding failed
- No chunks for that file

**Fix:**

1. Verify file_id exists: `GET /api/rag/{file_id}`
2. Confirm chunks_created > 0
3. Try simpler query terms

### Vector store too large

**Cause:** Many documents uploaded, vector_store/ folder growing large.
**Fix:**

1. Delete old vector_store: `rm -rf backend/app/vector_store/`
2. Re-upload needed documents
3. Or: Implement vector store cleanup (see Architecture docs)

## Performance Notes

- **Chunking:** ~1-2 seconds per document
- **Embedding:** ~100-200ms per chunk (mock), ~200-500ms (real OpenAI)
- **Search:** <50ms using FAISS
- **Memory:** FAISS index held in memory (~1536 _ num_chunks _ 4 bytes)

For large deployments (1000s of chunks), consider:

1. FAISS index persistence (already implemented)
2. Batch processing
3. External vector DB (Pinecone, Weaviate)

## Architecture

The RAG system integrates 5 services:

| Service              | Purpose               | Status                |
| -------------------- | --------------------- | --------------------- |
| RAGDocumentProcessor | PDF/text extraction   | ✓ Working             |
| SemanticChunker      | Intelligent splitting | ✓ Working             |
| EmbeddingService     | Vector generation     | ✓ Mock/Real available |
| VectorStore          | FAISS management      | ✓ Working             |
| RAGPipeline          | Orchestration         | ✓ Working             |

Files:

- `app/services/rag_*.py` - 5 service modules
- `app/routes/files.py` - API endpoints
- `app/vector_store/` - Persistent storage

## Next Steps

1. ✅ RAG system fully working with text documents
2. ⏳ Add real OpenAI embeddings (set OPENAI_API_KEY)
3. ⏳ Test with PDF documents (pdfplumber ready)
4. ⏳ Implement LLM-based Q&A on chunks (use GPT-4o)
5. ⏳ Add document management UI

## Support

For issues:

1. Check backend logs: `tail -f /tmp/backend.log`
2. Verify .env configuration
3. Test with simple documents first
4. Check vector_store size: `du -sh backend/app/vector_store/`
