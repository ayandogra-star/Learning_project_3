"""Contract analyzer service using Azure OpenAI GPT-4o for KPI extraction."""
import json
import os
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
        try:
            system_prompt = ContractAnalyzer.load_system_prompt()
            client = get_azure_client()
            
            # Send to Azure OpenAI with temperature=0 for deterministic extraction
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": parsed_pdf_text}
                ],
                temperature=0
            )
            
            # Extract JSON response
            response_text = response.choices[0].message.content
            
            # Parse and validate JSON
            kpi_data = json.loads(response_text)
            
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
            
            return ordered_kpis
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from Azure OpenAI: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error analyzing contract: {str(e)}")
