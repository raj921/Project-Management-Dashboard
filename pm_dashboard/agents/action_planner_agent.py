from typing import Dict, Any, List
import json
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class ActionPlannerAgent(BaseAgent):
    """Agent responsible for planning next steps and actions for a project."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Action Planner Agent."""
        super().__init__("action_planner", config)
        
    async def process(self, project_data: Dict[str, Any], blockers_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an action plan based on project data and blockers.
        
        Args:
            project_data: Structured project information from the Research Agent
            blockers_data: Blockers and risks from the Blocker Detection Agent
            
        Returns:
            Dict containing the action plan
        """
        print("Action Planner Agent: Generating action plan...")
        
        if not project_data:
            return {
                "actions": [],
                "priority_tasks": [],
                "schedule_recommendations": [],
                "summary": "No project data available to generate action plan"
            }
            
        # Prepare data for the LLM
        project_info = json.dumps(project_data, indent=2)
        blockers_info = json.dumps(blockers_data, indent=2)
        
        # Generate the action plan
        action_plan = await self._generate_action_plan(project_info, blockers_info)
        
        return action_plan
    
    async def _generate_action_plan(self, project_info: str, blockers_info: str) -> Dict[str, Any]:
        """Generate an action plan using the LLM.
        
        Args:
            project_info: String representation of project information
            blockers_info: String representation of blockers and risks
            
        Returns:
            Dict containing the action plan
        """
        system_prompt = """You are an experienced project manager responsible for creating clear, 
        actionable plans. Based on the project information and identified blockers/risks, create 
        a prioritized action plan with specific, time-bound tasks.
        
        Your plan should include:
        1. Immediate actions to unblock critical path items
        2. High-priority tasks that will drive the most value
        3. Resource allocation recommendations
        4. Timeline adjustments if needed
        5. Dependencies between tasks
        
        Be specific, realistic, and focus on outcomes.
        """
        
        user_prompt = f"""Project Information:
        {project_info}
        
        Identified Blockers and Risks:
        {blockers_info}
        
        Based on this information, please generate a comprehensive action plan with the following structure:
        
        {{
            "actions": [
                {{
                    "task": "Specific action to take",
                    "owner": "Who should be responsible",
                    "due_date": "When it should be completed (YYYY-MM-DD)",
                    "priority": "High/Medium/Low",
                    "status": "Not Started/In Progress/Blocked/Completed",
                    "dependencies": ["Task ID or description this depends on"],
                    "success_metrics": "How to know this is done correctly"
                }}
            ],
            "priority_tasks": [
                "The 3-5 most critical tasks that need immediate attention"
            ],
            "schedule_recommendations": [
                "Any suggested changes to the project timeline or milestones"
            ],
            "resource_recommendations": [
                "Any suggestions for reallocating or adding resources"
            ],
            "summary": "A brief overview of the recommended approach"
        }}
        """
        
        response = await self._call_llm(user_prompt, system_prompt)
        
        try:
            # Try to parse the response as JSON
            action_plan = self._parse_json_response(response)
            
            # Ensure the response has the expected structure
            if not isinstance(action_plan, dict):
                raise ValueError("Invalid response format: expected a dictionary")
                
            # Ensure required fields exist
            if "actions" not in action_plan:
                action_plan["actions"] = []
            if "priority_tasks" not in action_plan:
                action_plan["priority_tasks"] = []
            if "schedule_recommendations" not in action_plan:
                action_plan["schedule_recommendations"] = []
            if "resource_recommendations" not in action_plan:
                action_plan["resource_recommendations"] = []
            if "summary" not in action_plan:
                action_plan["summary"] = "Action plan generated. Review the recommended tasks and priorities."
                
            # Add timestamps
            action_plan["generated_at"] = datetime.now().isoformat()
            action_plan["time_horizon"] = self._calculate_time_horizon(action_plan)
                
            return action_plan
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing action plan: {e}")
            return {
                "actions": [],
                "priority_tasks": [],
                "schedule_recommendations": [],
                "resource_recommendations": [],
                "summary": "Error generating action plan",
                "error": str(e),
                "raw_response": response
            }
    
    def _calculate_time_horizon(self, action_plan: Dict[str, Any]) -> str:
        """Calculate the time horizon for the action plan.
        
        Args:
            action_plan: The generated action plan
            
        Returns:
            String describing the time horizon (e.g., "2 weeks", "1 month")
        """
        if not action_plan.get("actions"):
            return "No time horizon - no actions defined"
            
        # Look for due dates in the actions
        due_dates = []
        today = datetime.now().date()
        
        for action in action_plan["actions"]:
            if "due_date" in action and action["due_date"]:
                try:
                    # Try different date formats
                    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
                        try:
                            due_date = datetime.strptime(str(action["due_date"]), fmt).date()
                            due_dates.append(due_date)
                            break
                        except ValueError:
                            continue
                except (ValueError, TypeError):
                    continue
        
        if not due_dates:
            return "Time horizon not specified in actions"
            
        # Find the latest due date
        latest_date = max(due_dates)
        delta = latest_date - today
        
        # Convert to weeks or months
        if delta.days <= 14:
            return f"{delta.days} days"
        elif delta.days <= 60:
            weeks = delta.days // 7
            return f"{weeks} weeks"
        else:
            months = delta.days // 30
            return f"{months} months"
