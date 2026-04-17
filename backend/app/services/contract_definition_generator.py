"""LLM generation service for RAG-based contract queries."""
import json
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ContractDefinitionGenerator:
    """
    Generate contract term definitions and explanations using LLM.
    
    Uses Azure OpenAI to generate JSON responses with:
    - Term definition
    - Key elements
    - Risk implications
    - Compliance requirements
    - Related sections
    """
    
    @staticmethod
    def get_azure_client():
        """Get Azure OpenAI client."""
        from openai import AzureOpenAI
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI credentials not configured")
        
        return AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
    
    @staticmethod
    def generate_definition(
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        file_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a detailed definition for a contract term based on retrieved chunks.
        
        Args:
            query: User query (term to define)
            retrieved_chunks: List of relevant chunks from RAG retrieval
            file_id: Optional file ID for context
            
        Returns:
            Dictionary with structured definition response
        """
        try:
            # Format retrieved chunks for context
            context_sections = ContractDefinitionGenerator._format_chunks_as_context(retrieved_chunks)
            
            if not context_sections:
                return {
                    "term": query,
                    "definition": "Not explicitly defined in the provided contract content",
                    "key_elements": [],
                    "risk_implications": "Unable to assess",
                    "compliance_requirements": [],
                    "related_sections": [],
                    "confidence": "low",
                    "message": "No relevant sections found in contract"
                }
            
            # Build system prompt
            system_prompt = """You are a contract analysis AI assistant specializing in extracting term definitions and explanations from legal documents.

Your task is to:
1. Analyze the provided contract sections
2. Extract and explain the requested term
3. Identify key elements, risks, and compliance requirements
4. Return ONLY valid JSON (no other text)

CRITICAL RULES:
- Use ONLY information from the provided context
- Do NOT hallucinate or infer beyond what's stated
- If the term is not found, set definition to "Not explicitly defined in provided context"
- Be concise but thorough
- Return valid JSON that matches the required schema

RESPONSE SCHEMA:
{
  "term": "<term requested>",
  "definition": "<clear definition from context, or 'Not explicitly defined' if not found>",
  "key_elements": ["<element1>", "<element2>", ...],
  "risk_implications": "<potential risks and implications>",
  "compliance_requirements": ["<requirement1>", "<requirement2>", ...],
  "related_sections": ["<section ref>", "<section ref>", ...],
  "confidence": "<high|medium|low>"
}"""
            
            user_prompt = f"""Extract and explain the following term from the provided contract sections:

TERM TO DEFINE: {query}

CONTRACT SECTIONS:
{context_sections}

Generate a comprehensive definition response in JSON format."""
            
            # Call Azure OpenAI
            client = ContractDefinitionGenerator.get_azure_client()
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Handle markdown-wrapped JSON
            if '```' in response_text:
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                else:
                    start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            # Parse response
            result = json.loads(response_text)
            
            # Add metadata
            result["file_id"] = file_id
            result["chunks_used"] = len(retrieved_chunks)
            result["source_chunks"] = [
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "page_number": chunk.get("metadata", {}).get("page_number"),
                    "preview": chunk.get("content_preview", "")[:100]
                }
                for chunk in retrieved_chunks[:3]
            ]
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {
                "term": query,
                "definition": "Error processing response",
                "error": str(e),
                "confidence": "low"
            }
        except Exception as e:
            logger.error(f"Error generating definition: {str(e)}")
            return {
                "term": query,
                "definition": f"Error: {str(e)}",
                "confidence": "low"
            }
    
    @staticmethod
    def generate_section_explanation(
        section_query: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate explanation for a contract section.
        
        Args:
            section_query: What to explain (e.g., "Section 3.2: Data Processing")
            retrieved_chunks: Relevant chunks
            
        Returns:
            Dictionary with explanation
        """
        try:
            context = ContractDefinitionGenerator._format_chunks_as_context(retrieved_chunks)
            
            system_prompt = """You are a contract analysis expert. Explain the provided section clearly and concisely.

Return ONLY valid JSON with this schema:
{
  "section": "<section identifier>",
  "summary": "<brief summary>",
  "obligations": ["<obligation1>", ...],
  "restrictions": ["<restriction1>", ...],
  "key_dates": ["<date1>", ...],
  "financial_terms": ["<term1>", ...],
  "risks": ["<risk1>", ...]
}"""
            
            user_prompt = f"""Analyze and explain this contract section:

SECTION TO EXPLAIN: {section_query}

CONTEXT:
{context}

Generate a detailed explanation in JSON format."""
            
            client = ContractDefinitionGenerator.get_azure_client()
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
            
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Handle markdown JSON
            if '```' in response_text:
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                else:
                    start = response_text.find('```') + 3
                end = response_text.find('```', start)
                response_text = response_text[start:end].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Error generating section explanation: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def _format_chunks_as_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks as readable context for the LLM.
        
        Args:
            chunks: Retrieved chunks from FAISS
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "[No relevant sections found]"
        
        formatted_parts = []
        
        for idx, chunk in enumerate(chunks, 1):
            section_title = chunk.get("metadata", {}).get("section_title", "Untitled")
            page_num = chunk.get("metadata", {}).get("page_number", "?")
            content_type = chunk.get("metadata", {}).get("content_type", "text")
            similarity = chunk.get("boosted_similarity_score", chunk.get("similarity_score", 0))
            content = chunk.get("content", "")[:1000]  # Limit to 1000 chars per chunk
            
            header = f"[Section {idx}] {section_title} (Page {page_num}, Type: {content_type}, Relevance: {similarity:.2f})"
            formatted_parts.append(f"{header}\n{content}\n")
        
        return "\n---\n".join(formatted_parts)
