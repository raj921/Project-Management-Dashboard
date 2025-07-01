from typing import Dict, Any, List
import json
from .base_agent import BaseAgent

class BlockerDetectionAgent(BaseAgent):
    """Agent responsible for identifying potential blockers and risks in a project."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Blocker Detection Agent."""
        super().__init__("blocker_detection", config)
        
    async def process(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project data to identify blockers and risks.
        
        Args:
            project_data: Structured project information from the Research Agent
            
        Returns:
            Dict containing identified blockers and risks
        """
        print("Blocker Detection Agent: Analyzing project for blockers and risks...")
        
        if not project_data:
            return {"blockers": [], "risks": [], "summary": "No project data provided for analysis"}
            
        # Convert project data to a string representation for the LLM
        project_info = json.dumps(project_data, indent=2)
        
        # Analyze the project data for blockers and risks
        analysis = await self._analyze_for_blockers(project_info)
        
        return analysis
    
    async def _analyze_for_blockers(self, project_info: str) -> Dict[str, Any]:
        """Use LLM to analyze project information for blockers and risks.
        
        Args:
            project_info: String representation of project information
            
        Returns:
            Dict containing blockers and risks analysis
        """
        system_prompt = """You are an experienced project manager who excels at identifying potential 
        blockers and risks in software projects. Analyze the provided project information and identify:
        
        1. Blockers: Issues that are currently preventing progress (e.g., missing dependencies, 
           team member unavailability, technical challenges)
        2. Risks: Potential issues that could become blockers if not addressed
        
        For each item, provide:
        - A clear description
        - The area/component it affects
        - Severity (Low, Medium, High, Critical)
        - Recommended actions to resolve or mitigate
        
        Return the information in a structured JSON format.
        """
        
        user_prompt = f"""Analyze the following project information and identify blockers and risks:
        
        {project_info}
        
        Return the analysis in a valid JSON format with the following structure:
        {{
            "blockers": [
                {{
                    "description": "Description of the blocker",
                    "area": "Area/component affected",
                    "severity": "High/Medium/Low/Critical",
                    "recommended_actions": ["Action 1", "Action 2"]
                }}
            ],
            "risks": [
                {{
                    "description": "Description of the risk",
                    "potential_impact": "What could happen if not addressed",
                    "likelihood": "High/Medium/Low",
                    "mitigation_strategies": ["Strategy 1", "Strategy 2"]
                }}
            ],
            "summary": "Brief summary of the key findings"
        }}
        """
        
        response = await self._call_llm(user_prompt, system_prompt)
        
        try:
            # Try to parse the response as JSON
            analysis = self._parse_json_response(response)
            
            # Ensure the response has the expected structure
            if not isinstance(analysis, dict):
                raise ValueError("Invalid response format: expected a dictionary")
                
            # Ensure required fields exist
            if "blockers" not in analysis:
                analysis["blockers"] = []
            if "risks" not in analysis:
                analysis["risks"] = []
            if "summary" not in analysis:
                analysis["summary"] = "Analysis completed. Review the blockers and risks for details."
                
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing blocker detection results: {e}")
            return {
                "blockers": [],
                "risks": [],
                "summary": "Error analyzing project for blockers and risks",
                "error": str(e),
                "raw_response": response
            }
