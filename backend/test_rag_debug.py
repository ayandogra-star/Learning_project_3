#!/usr/bin/env python
"""Debug script to test RAG pipeline."""
import sys
sys.path.insert(0, '/Users/ayandogra/Documents/GitHub/Learning_project/backend')

from app.services.semantic_chunker import SemanticChunker, RAGChunk
from app.services.embedding_service import EmbeddingService

# Test text
test_text = """SERVICE AGREEMENT

1. PAYMENT TERMS

This agreement is subject to monthly payments of $5,000, due on the 15th of each month.

2. LIABILITY

Neither party shall be liable for indirect or consequential damages.

3. TERMINATION

Either party may terminate this agreement with 30 days notice in writing."""

print("=" * 50)
print("Testing RAG Pipeline Components")
print("=" * 50)

# Test 1: Create chunks
print("\n1. Testing Semantic Chunking...")
chunks = SemanticChunker.chunk_text_content(
    text=test_text,
    page_number=1,
    source_filename="test.txt",
    chunk_id_prefix="file_1_p1"
)
print(f"   ✓ Created {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"     Chunk {i+1}: {len(chunk.content)} chars, {chunk.token_count} tokens")

# Test 2: Generate embeddings
print("\n2. Testing Embedding Generation...")
try:
    embeddings_data = EmbeddingService.generate_embeddings(chunks)
    print(f"   ✓ Generated {len(embeddings_data)} embeddings")
    
    if embeddings_data:
        print(f"     First embedding keys: {embeddings_data[0].keys()}")
        print(f"     Content in embedding: {'content' in embeddings_data[0]}")
        if 'embedding' in embeddings_data[0]:
            print(f"     Embedding dimension: {len(embeddings_data[0]['embedding'])}")
        if 'content' in embeddings_data[0]:
            print(f"     Content length: {len(embeddings_data[0].get('content', ''))}")
    else:
        print("   ✗ No embeddings returned!")
        
except Exception as e:
    print(f"   ✗ Error generating embeddings: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
