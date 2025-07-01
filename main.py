# main.py

import pandas as pd
import os
from crewai import Agent, Task, Crew
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Placeholder for CrewAI agent imports
# from crewai import ...

# Helper: Load Excel data
def load_project_data(filepath):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Excel file not found: {filepath}")
        
        df = pd.read_excel(filepath)
        if df.empty:
            raise ValueError("Excel file is empty")
        
        print(f"Loaded data with {len(df)} rows and columns: {list(df.columns)}")
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        # Return a minimal dataset for demo purposes
        return pd.DataFrame({
            'Goal Description': ['Sample Task'],
            'Status': ['In Progress'],
            'Team Member': ['Sample User'],
            'Month': ['2024-01'],
            'Goal Type': ['Sample Goal']
        })

# Agent 1: Research Agent (robust to missing columns)
def research_agent_task(data):
    summary = f"Project has {len(data)} goals/tasks."
    milestones = data['Month'].dropna().unique().tolist() if 'Month' in data else []
    updates = []  # No explicit updates column in this dataset
    tasks = []
    for _, row in data.iterrows():
        task = {
            'Task': row['Goal Description'] if 'Goal Description' in row else '',
            'Status': row['Status'] if 'Status' in row else '',
            'Owner': row['Team Member'] if 'Team Member' in row else '',
            'DueDate': row['Month'] if 'Month' in row else '',
            'Goal Type': row['Goal Type'] if 'Goal Type' in row else ''
        }
        tasks.append(task)
    return {
        'summary': summary,
        'milestones': milestones,
        'updates': updates,
        'tasks': tasks
    }

# Agent 2: Blocker Detection Agent
def blocker_detection_agent_task(context):
    blockers = []
    # Define which statuses count as blockers
    blocker_statuses = ['blocked', 'delayed', 'overdue', 'not started', 'pending']
    for task in context.get('tasks', []):
        status = str(task.get('Status', '')).strip().lower()
        if status in blocker_statuses:
            blockers.append({
                'task': task.get('Task', ''),
                'reason': task.get('Status', ''),
                'owner': task.get('Owner', ''),
                'due': str(task.get('DueDate', ''))
            })
    # Use OpenAI LLM for blocker analysis if API key is present
    if OPENAI_API_KEY and blockers:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"Given these blockers: {blockers}, categorize them by type or priority for a PM dashboard."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a project risk analyst."},
                      {"role": "user", "content": prompt}]
        )
        blockers.append({'llm_analysis': response.choices[0].message.content.strip()})
    return {'blockers': blockers}

# Agent 3: Action Planner Agent
def action_planner_agent_task(context, blockers):
    actions = []
    for blocker in blockers.get('blockers', []):
        if isinstance(blocker, dict) and 'task' in blocker:
            actions.append(f"Follow up with {blocker['owner']} on '{blocker['task']}' (Reason: {blocker['reason']}, Due: {blocker['due']})")
    if not actions:
        actions.append("No immediate actions required. Monitor project progress.")
    # Use OpenAI LLM for action planning if API key is present
    if OPENAI_API_KEY:
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = f"Given the project context: {context} and blockers: {blockers}, suggest a concise, prioritized action plan for the PM."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a project action planner."},
                      {"role": "user", "content": prompt}]
        )
        actions.append(response.choices[0].message.content.strip())
    return {'actions': actions}

# Custom agent wrappers for project processing
class ResearchAgent:
    def __init__(self, name, role, goal, backstory):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
    
    def process(self, data):
        return research_agent_task(data)

class BlockerDetectionAgent:
    def __init__(self, name, role, goal, backstory):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
    
    def process(self, context):
        return blocker_detection_agent_task(context)

class ActionPlannerAgent:
    def __init__(self, name, role, goal, backstory):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
    
    def process(self, context, blockers):
        return action_planner_agent_task(context, blockers)

# Orchestration function
def run_agents(filepath):
    data = load_project_data(filepath)
    research_agent = ResearchAgent(
        name="Research Agent",
        role="Extracts project context",
        goal="Summarize project data and extract key milestones, updates, and tasks.",
        backstory="You are an expert project analyst, skilled at extracting structured context from project documents."
    )
    context = research_agent.process(data)
    blocker_agent = BlockerDetectionAgent(
        name="Blocker Detection Agent",
        role="Finds blockers",
        goal="Identify risks, delays, and dependencies in the project.",
        backstory="You are a risk analyst specializing in project management bottlenecks."
    )
    blockers = blocker_agent.process(context)
    planner_agent = ActionPlannerAgent(
        name="Action Planner Agent",
        role="Plans next steps",
        goal="Recommend next steps and actions for the project manager.",
        backstory="You are a project management assistant focused on actionable planning."
    )
    actions = planner_agent.process(context, blockers)
    return context, blockers, actions

if __name__ == "__main__":
    context, blockers, actions = run_agents('PM Dashboard sample dataset.xlsx')
    print('Context:', context)
    print('Blockers:', blockers)
    print('Actions:', actions) 