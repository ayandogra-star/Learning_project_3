# RAG System - Quick Start Guide

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs the new RAG packages:

- `pdfplumber==0.10.4` - PDF extraction
- `numpy==1.24.3` - Numerical operations
- `faiss-cpu==1.7.4` - Vector search
- `tiktoken==0.5.2` - Token counting

### 2. Verify Installation

```bash
python -c "from app.services.rag_pipeline import RAGPipeline; print('RAG system ready!')"
```

### 3. Start Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend is ready when you see:

```
Uvicorn running on http://0.0.0.0:8000
```

## Basic Usage

### Upload a PDF

The system automatically processes RAG when you upload:

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

Response includes file_id needed for retrieval.

### Get All Chunks for a File

```bash
curl http://localhost:8000/api/rag/1
```

Shows total chunks, text chunks, table chunks, and embeddings added.

### Search for Chunks

```bash
curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "payment terms",
    "top_k": 5,
    "file_id": 1
  }'
```

Returns most relevant chunks sorted by similarity.

### Retrieve Chunks by Query

Alternative GET endpoint:

```bash
curl "http://localhost:8000/api/rag/retrieve?query=liability&top_k=3&file_id=1"
```

## What Gets Extracted

### Text Extraction

- Full text per page
- Page numbers tracked
- Sections identified by headings
- Paragraphs preserved

### Table Extraction

- Tables detected on page
- Row/column structure preserved
- Formatted as readable text for embeddings
- Tracked separately from text chunks

### Semantic Chunks

Each chunk includes:

```
chunk_id: "file_1_p3_chunk_5"
content: 500 tokens or less (semantic boundary preserved)
page_number: 3
section_title: "DEFINITIONS"
content_type: "text" or "table"
token_count: 445
```

### Vector Embeddings

- 1536-dimensional vectors (text-embedding-3-small)
- One embedding per chunk
- Stored in FAISS index
- Persisted to disk

## Example Flow

### 1. Upload PDF

```bash
$ curl -X POST http://localhost:8000/api/upload -F "file=@contract.pdf"

{
  "id": 1,
  "filename": "contract.pdf",
  "file_size": 206534,
  "message": "File uploaded and analyzed successfully",
  "upload_time": "2026-04-15T21:46:38",
  "processing_time": 2.5
}
```

### 2. Check RAG Status

```bash
$ curl http://localhost:8000/api/rag/1

{
  "file_id": 1,
  "total_chunks": 42,
  "chunks": [...],
  "rag_metadata": {
    "chunks_created": 42,
    "embeddings_added": 42,
    "processing_status": "completed",
    "details": {
      "text_chunks": 38,
      "table_chunks": 4,
      "total_pages": 12
    }
  }
}
```

### 3. Search Chunks

```bash
$ curl -X POST http://localhost:8000/api/rag/search \
  -H "Content-Type: application/json" \
  -d '{"query": "payment deadline", "top_k": 3}'

[
  {
    "vector_id": 8,
    "chunk_id": "file_1_p4_chunk_2",
    "file_id": 1,
    "similarity_score": 0.89,
    "metadata": {
      "page_number": 4,
      "section_title": "PAYMENT TERMS"
    }
  },
  ...
]
```

## Outputs Generated

### JSON Structures Returned

**Chunk Object:**

```json
{
  "chunk_id": "file_1_p2_chunk_3",
  "content": "Lorem ipsum dolor sit amet...",
  "page_number": 2,
  "section_title": "TERMS AND CONDITIONS",
  "content_type": "text",
  "token_count": 356,
  "metadata": {
    "chunk_id": "file_1_p2_chunk_3",
    "page_number": 2,
    "section_title": "TERMS AND CONDITIONS",
    "content_type": "text",
    "source_filename": "contract.pdf"
  }
}
```

**Retrieval Result:**

```json
{
  "vector_id": 12,
  "chunk_id": "file_1_p2_chunk_3",
  "file_id": 1,
  "similarity_score": 0.87,
  "metadata": {
    "page_number": 2,
    "section_title": "TERMS AND CONDITIONS",
    "content_type": "text",
    "source_filename": "contract.pdf"
  }
}
```

**File Metadata:**

```json
{
  "rag_metadata": {
    "chunks_created": 42,
    "embeddings_added": 42,
    "processing_status": "completed",
    "details": {
      "text_chunks": 38,
      "table_chunks": 4,
      "total_pages": 12
    }
  }
}
```

## Files and Storage

### New Files Created

```
backend/
├── app/
│   ├── services/
│   │   ├── rag_document_processor.py    # PDF extraction
│   │   ├── semantic_chunker.py          # Smart chunking
│   │   ├── embedding_service.py         # Embedding generation
│   │   ├── vector_store.py              # FAISS management
│   │   ├── rag_pipeline.py              # Orchestration
│   │   └── file_service.py              # UPDATED
│   ├── routes/
│   │   └── files.py                     # UPDATED with RAG endpoints
│   ├── models.py                        # UPDATED with RAG metadata
│   └── schemas.py                       # UPDATED with RAG schemas
│   └── vector_store/                    # NEW - Vector DB storage
│       ├── faiss.index
│       └── metadata.json
├── requirements.txt                     # UPDATED with RAG packages
└── RAG_INTEGRATION.md                   # This documentation
```

### Vector Store Persistence

```
backend/app/vector_store/
├── faiss.index          # FAISS index (binary)
└── metadata.json        # Chunk metadata
```

Automatically created and updated on first PDF upload.

## Monitoring

### Check Vector Store

```bash
ls -lh backend/app/vector_store/
```

Shows index size and creation time.

### Check Processing Status

```bash
curl http://localhost:8000/api/rag/1 | jq '.rag_metadata'
```

Shows processing status, chunks created, embeddings added.

## Constraints

- **Chunk size**: 300-800 tokens (semantic boundaries honored)
- **Tables**: Never split across chunks
- **Embeddings**: 1536 dimensions (text-embedding-3-small)
- **Vector search**: L2 distance metric
- **File upload**: PDF, TXT, DOC, DOCX
- **Chunking**: Per-page processing

## Important Notes

1. **First Upload is Slower**
   - FAISS index creation takes ~1 second
   - Subsequent uploads are faster

2. **Deterministic Outputs**
   - Same PDF always produces same chunks
   - Same chunks always produce same embeddings
   - Retrieval always returns same results for same query

3. **No External Dependencies**
   - FAISS runs locally (no cloud vector DB required)
   - Uses existing Azure OpenAI credentials
   - No additional API keys needed

4. **Graceful Degradation**
   - If RAG fails, file still uploads with KPIs
   - If embedding fails, query returns empty results
   - No cascade failures to main API

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pdfplumber'`

**Solution:**

```bash
pip install pdfplumber==0.10.4
```

### Issue: `FileNotFoundError: Cannot find vector_store`

**Solution:** Vector store created automatically on first upload

```bash
curl -X POST http://localhost:8000/api/upload -F "file=@test.pdf"
```

### Issue: Empty search results

**Solution:** Re-upload PDF to generate embeddings

```bash
curl http://localhost:8000/api/rag/1  # Check status
```

### Issue: Slow performance

**FAISS is optimized for speed** - expected behavior for large indexes

## Next Steps

1. ✅ RAG system installed and integrated
2. ✅ PDF parsing with text/table extraction
3. ✅ Semantic chunking with metadata
4. ✅ Embedding generation and storage
5. ✅ Vector similarity search
6. ✅ Chunk retrieval endpoints

Your system is ready for:

- Document analysis and question-answering
- Contract clause retrieval
- Context extraction for LLM prompts
- Similarity-based document discovery
