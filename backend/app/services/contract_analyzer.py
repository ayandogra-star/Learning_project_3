"""Contract analyzer service using Azure OpenAI GPT-4o for KPI extraction."""
import json
import os
import logging
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global client (lazy-loaded)
_client = None


def get_azure_client():
    """Get or create the Azure OpenAI client (lazy loading)."""
    global _client
    if _client is None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")
        if not endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables")
        
        _client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
    return _client


DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")


class ContractAnalyzer:
    """
    Production KPI extraction engine for contract analysis.
    
    Integrates with Azure OpenAI GPT-4o to extract exactly 18 KPIs from contract text.
    Returns only clean JSON output for backend/frontend consumption.
    """
    
    @staticmethod
    def load_system_prompt() -> str:
        """
        Load the KPI extraction system prompt.
        
        Returns:
            System prompt instructing the model on KPI extraction rules
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_path = Path(__file__).parent.parent / "prompts" / "kpi_prompt.txt"
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt file not found at: {prompt_path}")
        
        with open(prompt_path, "r") as f:
            return f.read()
    
    @staticmethod
    def extract_kpis(parsed_pdf_text: str) -> dict:
        """
        Extract contract KPIs using Azure OpenAI GPT-4o.
        
        This method is called by the FastAPI backend after PDF text extraction.
        It returns ONLY the exact 18 KPIs in camelCase JSON format.
        
        Args:
            parsed_pdf_text: Contract text extracted from uploaded PDF
            
        Returns:
            Dictionary with exactly 18 KPI fields in camelCase.
            Missing KPIs are set to "Not Present"
            
        Raises:
            ValueError: If API call fails or JSON parsing fails
        """
        response_text = None
        try:
            system_prompt = ContractAnalyzer.load_system_prompt()
            client = get_azure_client()
            
            # Log API call for debugging
            logger.debug(f"Sending contract text to Azure OpenAI (length: {len(parsed_pdf_text)} chars)")
            logger.debug(f"Using deployment: {DEPLOYMENT_NAME}")
            
            # Send to Azure OpenAI with temperature=0 for deterministic extraction
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": parsed_pdf_text}
                ],
                temperature=0
            )
            
            # Extract JSON response - full response object details for debugging
            logger.debug(f"Response object: model={response.model}, usage={response.usage}")
            
            response_text = response.choices[0].message.content
            
            # Check if response is empty
            if not response_text or not response_text.strip():
                logger.error("Empty response from Azure OpenAI API")
                logger.error(f"Response object choices: {response.choices}")
                raise ValueError(
                    "Azure OpenAI returned an empty response. Possible causes:\n"
                    "1. API key or endpoint misconfiguration\n"
                    "2. Deployment name mismatch or deployment doesn't exist\n"
                    "3. API rate limit or quota exceeded\n"
                    "4. Temporary Azure service issues\n"
                    "5. Content filter triggered (try with different input)\n"
                    "Run: python test_azure_openai_diagnostic.py for more details"
                )
            
            logger.debug(f"Response from Azure OpenAI (first 500 chars): {response_text[:500]}")
            
            # Extract JSON from response (handle markdown code fences)
            # Sometimes the model wraps JSON in ```json ... ``` or just ```...```
            json_str = response_text
            if '```' in response_text:
                # Extract content between code fences
                try:
                    # Try to extract content between ```json and ```
                    if '```json' in response_text:
                        start = response_text.find('```json') + 7
                    else:
                        start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    json_str = response_text[start:end].strip()
                    logger.debug(f"Extracted JSON from markdown code fences: {json_str[:200]}")
                except Exception as e:
                    logger.warning(f"Could not extract JSON from markdown: {str(e)}")
            
            # Parse and validate JSON
            try:
                kpi_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error at position {e.pos}: {str(e)}")
                logger.error(f"Raw response that failed to parse: {response_text[:1000]}")
                raise ValueError(
                    f"Invalid JSON response from Azure OpenAI: {str(e)}\n"
                    f"Response preview: {response_text[:300]}\n"
                    f"This could mean: 1) Model didn't return JSON, 2) Response was truncated, "
                    f"3) Content filter intervention"
                )
            
            # Ensure all 18 KPI fields are present
            required_fields = [
                "totalContractsProcessed",
                "contractType",
                "contractStatus",
                "complianceScore",
                "controlCoveragePercentage",
                "incidentReadinessScore",
                "highRiskIssuesCount",
                "openRisksCount",
                "averageTimeToRemediate",
                "totalContractValue",
                "revenueAtRisk",
                "totalObligationsExtracted",
                "obligationsCompletionRate",
                "upcomingExpirations",
                "averageProcessingTime",
                "clauseExtractionAccuracy",
                "dataResidencyCompliance",
                "encryptionCompliance",
                "mfaCoverage"
            ]
            
            # Add missing fields with "Not Present"
            for field in required_fields:
                if field not in kpi_data:
                    kpi_data[field] = "Not Present"
            
            # Return only the required fields in correct order
            ordered_kpis = {field: kpi_data.get(field, "Not Present") for field in required_fields}
            
            logger.debug(f"Successfully extracted KPIs: {list(ordered_kpis.keys())}")
            return ordered_kpis
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise ValueError(
                f"Invalid JSON response from Azure OpenAI: {str(e)}\n"
                f"Response preview: {response_text[:300] if response_text else '[EMPTY]'}"
            )
        except ValueError as e:
            # Re-raise ValueError with better context
            logger.error(f"ValueError in extract_kpis: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Critical error in extract_kpis: {str(e)}", exc_info=True)
            raise ValueError(f"Error analyzing contract: {str(e)}")
