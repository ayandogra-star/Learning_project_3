"""
Compliance Analysis Service

Evaluates contract compliance requirements using RAG and LLM generation.
Extracts compliance findings for key security/operational areas.
"""

import json
import os
from typing import List, Dict, Any
from openai import AzureOpenAI


class ComplianceAnalyzer:
    """Analyzes contract compliance using retrieved chunks and LLM."""

    # Compliance questions to evaluate
    COMPLIANCE_QUESTIONS = [
        "Network Authentication & Authorization Protocols",
        "Multi-Factor Authentication (MFA) Enforcement",
        "Logging and Monitoring Requirements",
        "Incident Response and Breach Notification",
        "Data Encryption and Key Management",
    ]

    @staticmethod
    def generate_compliance_analysis(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate compliance analysis from retrieved contract chunks.

        Args:
            retrieved_chunks: List of chunk dicts with 'content', 'metadata', etc.

        Returns:
            List of compliance findings with state, confidence, quotes, reasoning.

        Raises:
            ValueError: If chunks are empty or LLM fails.
        """
        if not retrieved_chunks:
            return ComplianceAnalyzer._empty_compliance_response()

        # Format chunks as context
        context = ComplianceAnalyzer._format_chunks_as_context(retrieved_chunks)

        # Build system and user prompts
        system_prompt = """You are a Contract Compliance Analysis AI.

Evaluate the contract using ONLY the provided context.
Do NOT hallucinate or invent information.

For each compliance question, return ONLY valid JSON with:
- compliance_question: exact question from list
- compliance_state: "Fully Compliant" | "Partially Compliant" | "Non-Compliant"
- confidence: 0-100 (lower if uncertain or no evidence)
- relevant_quotes: list of exact verbatim quotes with section references
- rationale: brief reasoning based on extracted quotes

If no evidence found: state="Non-Compliant", confidence <= 40, quotes=[]

Return ONLY valid JSON array. Do NOT include markdown, explanations, or wrapping text."""

        user_prompt = f"""Analyze the following contract for compliance with these requirements:

1. Network Authentication & Authorization Protocols
2. Multi-Factor Authentication (MFA) Enforcement
3. Logging and Monitoring Requirements
4. Incident Response and Breach Notification
5. Data Encryption and Key Management

For each requirement, provide:
- Compliance state (Fully Compliant / Partially Compliant / Non-Compliant)
- Confidence score (0-100)
- Exact supporting quotes from the contract
- Reasoning

Contract Context:
{context}

Return ONLY the JSON array. Start with [ and end with ]."""

        try:
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            )

            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                max_tokens=2000,
            )

            response_text = response.choices[0].message.content.strip()

            # Extract JSON from markdown wrapping if present
            if "```" in response_text:
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                if start != -1 and end > start:
                    response_text = response_text[start:end]

            # Parse JSON response
            compliance_data = json.loads(response_text)

            # Validate and normalize response
            compliance_data = ComplianceAnalyzer._validate_compliance_response(compliance_data)

            return compliance_data

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            return ComplianceAnalyzer._empty_compliance_response()

        except Exception as e:
            print(f"Error generating compliance analysis: {e}")
            return ComplianceAnalyzer._empty_compliance_response()

    @staticmethod
    def _format_chunks_as_context(chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks from vector store as context for LLM compliance analysis.
        
        Args:
            chunks: List of chunk dictionaries from FAISS vector store.
                   Each chunk contains: 'content', 'metadata' (with section_title, page_number), 
                   'chunk_id', 'similarity_score', etc.
        
        Returns:
            Formatted context string with full chunk content for LLM analysis.
        """
        if not chunks:
            return ""
        
        context_parts = []

        for idx, chunk in enumerate(chunks[:7], 1):  # Limit to top 7 chunks
            # Extract content - use full content from vector store
            content = chunk.get("content", "")
            
            # Fallback to content_preview if full content not available
            if not content:
                content = chunk.get("content_preview", "")
            
            if not content or not isinstance(content, str):
                continue
            
            # Extract metadata from chunk
            metadata = chunk.get("metadata", {})
            section = metadata.get("section_title", "Unknown Section")
            page = metadata.get("page_number", "?")
            chunk_id = chunk.get("chunk_id", "")

            # Add section divider and chunk info
            context_parts.append(f"\n--- Chunk {idx} | Section: {section} (Page {page}) | ID: {chunk_id} ---")
            context_parts.append(content.strip())  # Use full content for accurate compliance analysis

        return "\n".join(context_parts)

    @staticmethod
    def _validate_compliance_response(data: Any) -> List[Dict[str, Any]]:
        """Validate and normalize compliance response structure."""
        if not isinstance(data, list):
            return ComplianceAnalyzer._empty_compliance_response()

        validated = []

        for item in data:
            if not isinstance(item, dict):
                continue

            validated_item = {
                "compliance_question": item.get("compliance_question", "Unknown"),
                "compliance_state": ComplianceAnalyzer._normalize_state(
                    item.get("compliance_state", "Non-Compliant")
                ),
                "confidence": ComplianceAnalyzer._normalize_confidence(
                    item.get("confidence", 0)
                ),
                "relevant_quotes": ComplianceAnalyzer._normalize_quotes(
                    item.get("relevant_quotes", [])
                ),
                "rationale": str(item.get("rationale", "No rationale provided"))[:500],
            }

            validated.append(validated_item)

        return validated if validated else ComplianceAnalyzer._empty_compliance_response()

    @staticmethod
    def _normalize_state(state: str) -> str:
        """Normalize compliance state to allowed values."""
        state_lower = str(state).lower().strip()

        if "fully" in state_lower or "complete" in state_lower:
            return "Fully Compliant"
        elif "partial" in state_lower or "partially" in state_lower:
            return "Partially Compliant"
        else:
            return "Non-Compliant"

    @staticmethod
    def _normalize_confidence(confidence: Any) -> int:
        """Normalize confidence to 0-100 range."""
        try:
            conf = int(confidence)
            return max(0, min(100, conf))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def _normalize_quotes(quotes: Any) -> List[str]:
        """Normalize quotes to list of strings."""
        if not isinstance(quotes, list):
            return []

        normalized = []
        for quote in quotes:
            if isinstance(quote, str) and quote.strip():
                normalized.append(quote.strip())

        return normalized

    @staticmethod
    def _empty_compliance_response() -> List[Dict[str, Any]]:
        """Return empty/non-compliant response for all questions."""
        return [
            {
                "compliance_question": question,
                "compliance_state": "Non-Compliant",
                "confidence": 0,
                "relevant_quotes": [],
                "rationale": "No evidence found in contract context.",
            }
            for question in ComplianceAnalyzer.COMPLIANCE_QUESTIONS
        ]
