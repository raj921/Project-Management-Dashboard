from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os
import openai
from dotenv import load_dotenv
import json

load_dotenv()

class BaseAgent(ABC):
    """Base class for all agents in the PM Dashboard system."""
    
    def __init__(self, agent_type: str, config: Dict[str, Any]):
        """Initialize the base agent with configuration.
        
        Args:
            agent_type: Type of the agent (e.g., 'research', 'blocker_detection', 'action_planner')
            config: Configuration dictionary containing model settings
        """
        self.agent_type = agent_type
        self.config = config
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)
    
    @abstractmethod
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process the input data and return the agent's output.
        
        Args:
            input_data: Input data for the agent to process
            
        Returns:
            Dict containing the agent's output
        """
        pass
    
    async def _call_llm(self, prompt: str, system_message: str = "") -> str:
        """Make a call to the OpenAI API.
        
        Args:
            prompt: The user's prompt
            system_message: Optional system message to guide the model's behavior
            
        Returns:
            The model's response as a string
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse a JSON response from the LLM.
        
        Args:
            response: The raw response string from the LLM
            
        Returns:
            Parsed JSON as a dictionary
        """
        try:
            # Try to find JSON in the response (in case there's extra text)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            json_str = response[start_idx:end_idx]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response was: {response}")
            return {"error": f"Failed to parse response: {str(e)}"}
