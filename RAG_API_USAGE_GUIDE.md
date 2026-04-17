# RAG API Usage Guide

## Overview

The RAG system provides three main API endpoints for semantic contract analysis. All endpoints require the contract to be previously uploaded and indexed.

## Required Environment Variables

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# OpenAI Embeddings
OPENAI_API_KEY=your_key  # For embeddings generation
```

## Base URL

```
http://localhost:8000/api/rag
```

---

## Endpoint 1: Define Contract Term

**Purpose:** Extract and explain the definition of a specific term or concept in a contract.

### Request

```http
POST /api/rag/define
Content-Type: application/json

{
  "term": "Personal Information",
  "file_id": 123,
  "context": "optional additional context about what aspect you want defined"
}
```

**Parameters:**

- `term` (string, required): The contract term to define
- `file_id` (integer, required): ID of the uploaded contract
- `context` (string, optional): Additional context for more specific definitions

### Response

```json
{
  "term": "Personal Information",
  "definition": "Any information relating to an identified or identifiable natural person, including but not limited to name, email address, phone number, address, and any other data that can directly or indirectly identify an individual.",
  "key_elements": [
    "Identified or identifiable natural person",
    "Direct identification: name, email, phone",
    "Indirect identification: correlated data",
    "Includes derived and inferred attributes"
  ],
  "risk_implications": "Unauthorized access to Personal Information could result in identity theft, fraud, privacy violations, and regulatory fines.",
  "compliance_requirements": [
    "GDPR: Lawful basis required for processing",
    "CCPA: Consumer rights must be honored",
    "HIPAA: Protected health information safeguards",
    "PIPEDA: Consent required for commercial use"
  ],
  "related_sections": [
    "Section 3.1: Data Protection Measures",
    "Section 3.2: Access Controls",
    "Section 5.4: Data Breach Notification"
  ],
  "confidence": 0.92,
  "file_id": 123,
  "chunks_used": 5,
  "source_chunks": [
    {
      "chunk_id": "doc_123_chunk_5",
      "section": "Definitions",
      "preview": "Personal Information: Any information relating...",
      "similarity_score": 0.89,
      "boosted_score": 1.34
    }
  ]
}
```

**Response Fields:**

- `term`: The defined term
- `definition`: Comprehensive definition extracted from contract
- `key_elements`: List of important components of the term
- `risk_implications`: Potential risks if this term is mishandled
- `compliance_requirements`: Relevant compliance obligations
- `related_sections`: Cross-references to related contract sections
- `confidence`: LLM confidence score (0.0-1.0)
- `file_id`: ID of the source contract
- `chunks_used`: Number of document chunks used for context
- `source_chunks`: Array of retrieved chunks with relevance scores

### Example: cURL

```bash
curl -X POST http://localhost:8000/api/rag/define \
  -H "Content-Type: application/json" \
  -d '{
    "term": "Service Level Agreement",
    "file_id": 123
  }'
```

### Example: Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag/define",
    json={
        "term": "Service Level Agreement",
        "file_id": 123,
        "context": "Performance and uptime guarantees"
    }
)

result = response.json()
print(f"Term: {result['term']}")
print(f"Definition: {result['definition']}")
print(f"Confidence: {result['confidence']}")
```

### Example: JavaScript

```javascript
const response = await fetch("http://localhost:8000/api/rag/define", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    term: "Indemnification",
    file_id: 123,
  }),
});

const result = await response.json();
console.log("Definition:", result.definition);
console.log("Compliance:", result.compliance_requirements);
```

---

## Endpoint 2: Generic RAG Query

**Purpose:** Query the contract with different query types (definition, section, compliance, risk).

### Request

```http
POST /api/rag/query
Content-Type: application/json

{
  "query": "What are the security requirements?",
  "file_id": 123,
  "query_type": "compliance",
  "top_k": 5
}
```

**Parameters:**

- `query` (string, required): Your question or search term
- `file_id` (integer, required): ID of the uploaded contract
- `query_type` (string, required): One of `definition`, `section`, `compliance`, `risk`
- `top_k` (integer, optional): Number of results (default: 5, max: 20)

**Query Types:**

- `definition`: Extract and explain a definition
- `section`: Find and explain a specific contract section
- `compliance`: Identify compliance requirements and obligations
- `risk`: Identify risks, liabilities, and penalty clauses

### Response

```json
{
  "query": "What are the security requirements?",
  "query_type": "compliance",
  "results": {
    "answer": "The contract requires the Service Provider to implement AES-256 encryption at rest, TLS 1.2+ encryption in transit, role-based access controls, and multi-factor authentication for all administrative access. Security audits must be conducted quarterly by independent third parties.",
    "related_sections": ["Section 3.1", "Section 3.2", "Section 4.5"],
    "confidence": 0.88
  },
  "retrieved_chunks": 4,
  "metadata": {
    "processing_time_ms": 245,
    "chunks_analyzed": 4,
    "boost_multipliers_applied": {
      "definitions": 1,
      "tables": 0,
      "keywords": 2
    }
  }
}
```

**Response Fields:**

- `query`: The original query
- `query_type`: The query type used
- `results`: Object with answer, related_sections, and confidence
- `retrieved_chunks`: Number of document chunks retrieved
- `metadata`: Processing statistics and boost multipliers used

### Example: cURL

```bash
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the termination clauses?",
    "file_id": 123,
    "query_type": "section",
    "top_k": 5
  }'
```

### Example: Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag/query",
    json={
        "query": "What liabilities apply to data breaches?",
        "file_id": 123,
        "query_type": "risk",
        "top_k": 8
    }
)

result = response.json()
print("Answer:", result["results"]["answer"])
print("Confidence:", result["results"]["confidence"])
```

### Example: JavaScript

```javascript
const response = await fetch("http://localhost:8000/api/rag/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "What data protection measures are required?",
    file_id: 123,
    query_type: "compliance",
    top_k: 5,
  }),
});

const result = await response.json();
console.log("Answer:", result.results.answer);
console.log("Chunks retrieved:", result.retrieved_chunks);
```

---

## Endpoint 3: Raw Vector Retrieval

**Purpose:** Retrieve raw chunks without LLM processing (useful for debugging or custom processing).

### Request

```http
GET /api/rag/retrieve?file_id=123&query=security&top_k=5
```

**Parameters (Query String):**

- `file_id` (integer, required): ID of the uploaded contract
- `query` (string, required): Search term
- `top_k` (integer, optional): Number of results (default: 5)

### Response

```json
{
  "query": "security",
  "file_id": 123,
  "chunks": [
    {
      "chunk_id": "doc_123_chunk_8",
      "content": "The Service Provider shall implement industry-standard security measures including AES-256 encryption...",
      "page_number": 3,
      "section_title": "Security",
      "similarity_score": 0.876,
      "boosted_score": 1.139,
      "boost_multiplier": 1.3,
      "source_type": "table"
    }
  ],
  "count": 1
}
```

### Example: cURL

```bash
curl "http://localhost:8000/api/rag/retrieve?file_id=123&query=audit&top_k=3"
```

---

## Complete Workflow Example

### Step 1: Upload Contract

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@contract.pdf"
```

Response includes `file_id`: `123`

### Step 2: Define Key Terms

```javascript
// Define "Confidential Information"
const termResponse = await fetch("http://localhost:8000/api/rag/define", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    term: "Confidential Information",
    file_id: 123,
  }),
});
const termDef = await termResponse.json();
console.log("Definition:", termDef.definition);

// Define "Indemnification"
const indemnifyResponse = await fetch("http://localhost:8000/api/rag/define", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    term: "Indemnification",
    file_id: 123,
  }),
});
const indemnifyDef = await indemnifyResponse.json();
console.log("Definition:", indemnifyDef.definition);
```

### Step 3: Query Compliance Requirements

```javascript
const complianceResponse = await fetch("http://localhost:8000/api/rag/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "What GDPR compliance requirements apply?",
    file_id: 123,
    query_type: "compliance",
  }),
});
const compliance = await complianceResponse.json();
console.log("Compliance Answer:", compliance.results.answer);
```

### Step 4: Identify Risks

```javascript
const riskResponse = await fetch("http://localhost:8000/api/rag/query", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "What are the liability limitations?",
    file_id: 123,
    query_type: "risk",
  }),
});
const risks = await riskResponse.json();
console.log("Risk Analysis:", risks.results.answer);
```

---

## Error Handling

All endpoints return appropriate HTTP status codes:

### 200 OK

Successful query with results

### 400 Bad Request

Missing or invalid parameters

```json
{
  "message": "Missing required field: term or file_id",
  "details": "Error details here"
}
```

### 404 Not Found

File not found or not indexed

```json
{
  "message": "Contract file_id 123 not found in vector store",
  "details": "Please upload and process the contract first"
}
```

### 500 Internal Server Error

Azure OpenAI failure, embedding failure, or other processing error

```json
{
  "message": "Failed to generate definition from LLM",
  "details": "Azure OpenAI API returned error: ...",
  "status": "error"
}
```

### Example Error Handling (Python)

```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/rag/define",
        json={
            "term": "Personal Information",
            "file_id": 123
        }
    )
    response.raise_for_status()
    result = response.json()

except requests.exceptions.HTTPError as e:
    if response.status_code == 404:
        print("Contract not found. Upload it first.")
    elif response.status_code == 400:
        print("Invalid request:", response.json()["message"])
    else:
        print("Server error:", response.json()["details"])

except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")
```

---

## Performance Characteristics

- **Definition Query:** ~1-2 seconds (includes embedding + retrieval + LLM generation)
- **Generic Query:** ~800ms - 1.5s (depends on LLM response complexity)
- **Vector Retrieval:** ~50-100ms (FAISS indexed search only)

- **Maximum Query Length:** 2000 characters
- **Maximum Response Tokens:** 1000 tokens
- **Vector Dimension:** 1536
- **Maximum Top-K Results:** 20

---

## Advanced Usage

### Batch Definition Extraction

```python
import asyncio
import requests

async def extract_definitions(file_id, terms):
    """Extract multiple term definitions in parallel."""
    async def get_definition(term):
        response = requests.post(
            "http://localhost:8000/api/rag/define",
            json={"term": term, "file_id": file_id}
        )
        return response.json()

    # Could use asyncio for true parallelism
    definitions = []
    for term in terms:
        result = get_definition(term)
        definitions.append(result)

    return definitions

# Usage
file_id = 123
terms = ["Confidential Information", "Indemnification", "Force Majeure"]
definitions = asyncio.run(extract_definitions(file_id, terms))
```

### Building a Contract Analyzer Dashboard

```python
class ContractAnalyzer:
    def __init__(self, file_id, base_url="http://localhost:8000"):
        self.file_id = file_id
        self.base_url = base_url

    def define_term(self, term):
        """Get term definition."""
        response = requests.post(
            f"{self.base_url}/api/rag/define",
            json={"term": term, "file_id": self.file_id}
        )
        return response.json()

    def analyze_compliance(self):
        """Analyze all compliance requirements."""
        response = requests.post(
            f"{self.base_url}/api/rag/query",
            json={
                "query": "List all compliance and regulatory requirements",
                "file_id": self.file_id,
                "query_type": "compliance",
                "top_k": 10
            }
        )
        return response.json()

    def identify_risks(self):
        """Identify all risks and liabilities."""
        response = requests.post(
            f"{self.base_url}/api/rag/query",
            json={
                "query": "List all liability limitations, exclusions, and penalties",
                "file_id": self.file_id,
                "query_type": "risk",
                "top_k": 10
            }
        )
        return response.json()

    def get_full_analysis(self):
        """Get comprehensive contract analysis."""
        return {
            "compliance": self.analyze_compliance(),
            "risks": self.identify_risks(),
            "key_terms": [
                self.define_term(term)
                for term in ["Confidential Information", "Indemnification", "Liability Cap"]
            ]
        }

# Usage
analyzer = ContractAnalyzer(file_id=123)
analysis = analyzer.get_full_analysis()
print("Compliance:", analysis["compliance"]["results"]["answer"])
print("Risks:", analysis["risks"]["results"]["answer"])
```

---

## Troubleshooting

### "Vector store not initialized for file_id"

**Cause:** Contract not yet processed through RAG pipeline
**Solution:** Wait for contract upload to complete, then try again

### "Empty response from Azure OpenAI"

**Cause:** API key issues or connection problem
**Solution:**

- Verify `AZURE_OPENAI_API_KEY` is set and valid
- Check `AZURE_OPENAI_ENDPOINT` format
- Ensure deployment name matches configuration

### "No relevant chunks found"

**Cause:** Query doesn't match contract content
**Solution:**

- Try more general search terms
- Break query into simpler components
- Check that contract was uploaded successfully

### Slow Response Times

**Cause:** FAISS index is large or network latency
**Solution:**

- Reduce `top_k` parameter
- Optimize query terms
- Consider using `/api/rag/retrieve` for just embedding distances

---

## Next Steps

1. **Integrate with Frontend:** Build React components to call these endpoints
2. **Add Caching:** Cache common term definitions to reduce latency
3. **Implement Batch Processing:** Process multiple contracts in parallel
4. **Set up Monitoring:** Track API performance and error rates
5. **Create Analytics Dashboard:** Monitor most-queried terms and patterns
