from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """Agent responsible for gathering and structuring project information."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Research Agent."""
        super().__init__("research", config)
        
    async def process(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process project data and extract structured information.
        
        Args:
            project_data: Raw project data including documents, chat logs, etc.
            
        Returns:
            Dict containing structured project information
        """
        print("Research Agent: Processing project data...")
        
        # Extract text from various sources
        text_sources = self._extract_text_sources(project_data)
        
        # Analyze the text to extract structured information
        structured_data = await self._analyze_text_sources(text_sources)
        
        return structured_data
    
    def _extract_text_sources(self, project_data: Dict[str, Any]) -> List[str]:
        """Extract text from various sources in the project data.
        
        Args:
            project_data: Raw project data
            
        Returns:
            List of text strings from different sources
        """
        text_sources = []
        
        # Extract from documents
        if "documents" in project_data:
            for doc in project_data["documents"]:
                if "content" in doc:
                    text_sources.append(f"Document: {doc.get('title', 'Untitled')}\n{doc['content']}")
        
        # Extract from chat logs
        if "chats" in project_data:
            chat_texts = []
            for chat in project_data["chats"]:
                chat_text = f"{chat.get('sender', 'User')} ({chat.get('timestamp', '')}): {chat.get('message', '')}"
                chat_texts.append(chat_text)
            if chat_texts:
                text_sources.append("Chat Logs:\n" + "\n".join(chat_texts))
        
        # Add any direct text content
        if "text_content" in project_data:
            if isinstance(project_data["text_content"], list):
                text_sources.extend(project_data["text_content"])
            else:
                text_sources.append(str(project_data["text_content"]))
        
        return text_sources
    
    async def _analyze_text_sources(self, text_sources: List[str]) -> Dict[str, Any]:
        """Analyze text sources to extract structured project information.
        
        Args:
            text_sources: List of text strings from different sources
            
        Returns:
            Dict containing structured project information
        """
        if not text_sources:
            return {}
            
        combined_text = "\n---\n".join(text_sources)
        
        system_prompt = """You are a research assistant that extracts and structures project information. 
        Analyze the provided project data and extract the following information in JSON format:
        - project_name: Name of the project
        - description: Brief project description
        - milestones: List of key milestones with their due dates and status
        - team_members: List of team members and their roles
        - current_tasks: List of current tasks with their status and priority
        - recent_updates: List of recent updates with timestamps
        """
        
        user_prompt = f"""Analyze the following project information and extract the requested details:
        
        {combined_text}
        
        Return the information in a valid JSON format with the structure specified above.
        """
        
        response = await self._call_llm(user_prompt, system_prompt)
        
        try:
            # Try to parse the response as JSON
            structured_data = self._parse_json_response(response)
            return structured_data
        except json.JSONDecodeError:
            # If parsing fails, try to fix common JSON issues
            fixed_response = response.replace("\n", " ").replace("  ", " ")
            try:
                structured_data = json.loads(fixed_response)
                return structured_data
            except json.JSONDecodeError:
                print("Failed to parse JSON response from Research Agent")
                return {
                    "error": "Failed to parse research data",
                    "raw_response": response
                }
