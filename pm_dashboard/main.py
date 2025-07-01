import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import streamlit as st
import pandas as pd
import openai
from dotenv import load_dotenv

from config import AGENT_CONFIG, MOCK_PROJECTS, STATUS_OPTIONS, PRIORITY_LEVELS
from agents.research_agent import ResearchAgent
from agents.blocker_detection_agent import BlockerDetectionAgent
from agents.action_planner_agent import ActionPlannerAgent

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="PM Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'project_data' not in st.session_state:
    st.session_state.project_data = {}
if 'blockers_data' not in st.session_state:
    st.session_state.blockers_data = {}
if 'action_plan' not in st.session_state:
    st.session_state.action_plan = {}
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Initialize agents
research_agent = ResearchAgent(AGENT_CONFIG["research"])
blocker_detection_agent = BlockerDetectionAgent(AGENT_CONFIG["blocker_detection"])
action_planner_agent = ActionPlannerAgent(AGENT_CONFIG["action_planner"])

# Mock data generator
def generate_mock_project_data(project_name: str) -> Dict[str, Any]:
    """Generate mock project data for demonstration."""
    team_members = [
        {"name": "Alex Johnson", "role": "Project Manager", "email": "alex.j@example.com"},
        {"name": "Sam Lee", "role": "Lead Developer", "email": "sam.lee@example.com"},
        {"name": "Jordan Taylor", "role": "UX Designer", "email": "jordan.t@example.com"},
        {"name": "Casey Smith", "role": "QA Engineer", "email": "casey.s@example.com"},
    ]
    
    # Generate some random dates
    today = datetime.now()
    start_date = today - timedelta(days=random.randint(10, 30))
    
    milestones = [
        {
            "name": "Project Kickoff",
            "due_date": (start_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "status": random.choice(["Completed", "In Progress"]),
            "description": "Official project kickoff meeting with all stakeholders"
        },
        {
            "name": "Requirements Finalized",
            "due_date": (start_date + timedelta(days=15)).strftime("%Y-%m-%d"),
            "status": random.choice(["Completed", "In Progress", "Not Started"]),
            "description": "All project requirements documented and approved"
        },
        {
            "name": "First Prototype",
            "due_date": (start_date + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": random.choice(["In Progress", "Not Started"]),
            "description": "Initial working prototype ready for review"
        },
        {
            "name": "Beta Release",
            "due_date": (start_date + timedelta(days=60)).strftime("%Y-%m-%d"),
            "status": "Not Started",
            "description": "Beta version released to test users"
        },
        {
            "name": "Final Release",
            "due_date": (start_date + timedelta(days=90)).strftime("%Y-%m-%d"),
            "status": "Not Started",
            "description": "Final version released to production"
        }
    ]
    
    tasks = [
        {
            "id": f"TASK-{i+1}",
            "title": f"{task_type} {component}",
            "assignee": random.choice([m["name"] for m in team_members]),
            "status": random.choice(STATUS_OPTIONS),
            "priority": random.choice(PRIORITY_LEVELS),
            "due_date": (today + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
            "description": f"{task_type} for {component} component"
        }
        for i, (task_type, component) in enumerate([
            ("Design", "user authentication"),
            ("Implement", "database schema"),
            ("Test", "API endpoints"),
            ("Review", "UI components"),
            ("Document", "API documentation"),
            ("Deploy", "staging environment"),
            ("Optimize", "database queries"),
            ("Fix", "login issues"),
        ])
    ]
    
    recent_updates = [
        {
            "date": (today - timedelta(days=days_ago)).strftime("%Y-%m-%d"),
            "author": random.choice([m["name"] for m in team_members]),
            "update": update
        }
        for days_ago, update in [
            (1, "Completed initial project setup and repository configuration"),
            (2, "Held kickoff meeting with all stakeholders"),
            (3, "Created initial project timeline and milestones"),
            (5, "Drafted technical requirements document"),
            (7, "Completed competitive analysis")
        ]
    ]
    
    return {
        "project_name": project_name,
        "description": f"A project focused on {project_name.lower()}",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "team_members": team_members,
        "milestones": milestones,
        "tasks": tasks,
        "recent_updates": recent_updates
    }

def generate_mock_chat_logs() -> List[Dict[str, str]]:
    """Generate mock chat logs for the project."""
    team_members = ["Alex Johnson", "Sam Lee", "Jordan Taylor", "Casey Smith"]
    
    messages = [
        {"sender": "Alex Johnson", "timestamp": "2023-11-01 09:15:00", "message": "Good morning team! Let's have a quick standup."},
        {"sender": "Sam Lee", "timestamp": "2023-11-01 09:16:00", "message": "Morning! I'm working on the authentication service today."},
        {"sender": "Jordan Taylor", "timestamp": "2023-11-01 09:16:30", "message": "I'll be finalizing the UI mockups for the dashboard."},
        {"sender": "Casey Smith", "timestamp": "2023-11-01 09:17:00", "message": "I've found a few edge cases we should test for in the login flow."},
        {"sender": "Alex Johnson", "timestamp": "2023-11-01 09:17:30", "message": "Great, let's schedule a review for those test cases later today."},
        {"sender": "Sam Lee", "timestamp": "2023-11-01 14:30:00", "message": "Blocked on the OAuth integration - waiting for API credentials from the provider."},
        {"sender": "Alex Johnson", "timestamp": "2023-11-01 14:32:00", "message": "I'll follow up with them right away."},
    ]
    
    return messages

async def process_project(project_name: str):
    """Process the project using all three agents."""
    try:
        st.session_state.processing = True
        
        # Generate mock data
        with st.spinner("Generating mock project data..."):
            project_data = generate_mock_project_data(project_name)
            chat_logs = generate_mock_chat_logs()
            
            # Combine all data for the research agent
            research_input = {
                "documents": [
                    {
                        "title": "Project Overview",
                        "content": f"Project: {project_name}\n"
                                  f"Description: {project_data['description']}\n"
                                  f"Team: {', '.join([m['name'] for m in project_data['team_members']])}"
                    }
                ],
                "chats": chat_logs,
                "text_content": [
                    f"Project Milestones:\n" + 
                    "\n".join([f"- {m['name']}: {m['status']} (Due: {m['due_date']})" 
                             for m in project_data['milestones']]),
                    "\nRecent Tasks:\n" +
                    "\n".join([f"- {t['title']} ({t['status']}, Priority: {t['priority']})" 
                              for t in project_data['tasks'][:3]])
                ]
            }
        
        # Step 1: Research Agent
        with st.spinner("Researching project details..."):
            research_results = await research_agent.process(research_input)
            st.session_state.project_data = research_results
        
        # Step 2: Blocker Detection Agent
        with st.spinner("Analyzing for blockers and risks..."):
            blockers_data = await blocker_detection_agent.process(research_results)
            st.session_state.blockers_data = blockers_data
        
        # Step 3: Action Planner Agent
        with st.spinner("Generating action plan..."):
            action_plan = await action_planner_agent.process(research_results, blockers_data)
            st.session_state.action_plan = action_plan
        
        st.session_state.processing = False
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.processing = False

def display_project_summary():
    """Display the project summary section."""
    if not st.session_state.project_data:
        return
        
    data = st.session_state.project_data
    
    st.header("📋 Project Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Project", data.get("project_name", "N/A"))
        st.metric("Status", data.get("status", "Active"))
    
    with col2:
        if "team_members" in data and data["team_members"]:
            st.metric("Team Size", len(data["team_members"]))
        if "start_date" in data:
            st.metric("Start Date", data.get("start_date", "N/A"))
    
    with col3:
        if "milestones" in data and data["milestones"]:
            completed = sum(1 for m in data["milestones"] if m.get("status") == "Completed")
            total = len(data["milestones"])
            st.metric("Milestones", f"{completed} / {total} Completed")
    
    # Project description
    if "description" in data:
        st.subheader("Description")
        st.write(data["description"])
    
    # Recent updates
    if "recent_updates" in data and data["recent_updates"]:
        st.subheader("Recent Updates")
        for update in data["recent_updates"][:5]:  # Show only the 5 most recent
            with st.expander(f"{update.get('date', '')} - {update.get('author', '')}"):
                st.write(update.get("update", ""))

def display_blockers():
    """Display the blockers and risks section."""
    if not st.session_state.blockers_data:
        return
        
    data = st.session_state.blockers_data
    
    st.header("⚠️ Blockers & Risks")
    
    # Display blockers
    if "blockers" in data and data["blockers"]:
        st.subheader("Current Blockers")
        for i, blocker in enumerate(data["blockers"][:5], 1):  # Show only top 5
            with st.expander(f"Blocker {i}: {blocker.get('description', '')}"):
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    st.metric("Area", blocker.get("area", "N/A"))
                with cols[1]:
                    st.metric("Severity", blocker.get("severity", "N/A"))
                with cols[2]:
                    st.metric("Status", "Active")
                
                st.write("**Recommended Actions:**")
                for action in blocker.get("recommended_actions", ["No specific actions recommended."]):
                    st.write(f"- {action}")
    
    # Display risks
    if "risks" in data and data["risks"]:
        st.subheader("Potential Risks")
        for i, risk in enumerate(data["risks"][:3], 1):  # Show only top 3
            with st.expander(f"Risk {i}: {risk.get('description', '')}"):
                cols = st.columns(2)
                with cols[0]:
                    st.metric("Impact", risk.get("potential_impact", "N/A"))
                with cols[1]:
                    st.metric("Likelihood", risk.get("likelihood", "N/A"))
                
                st.write("**Mitigation Strategies:**")
                for strategy in risk.get("mitigation_strategies", ["No specific strategies defined."]):
                    st.write(f"- {strategy}")
    
    # Display summary if available
    if "summary" in data and data["summary"]:
        with st.expander("Analysis Summary"):
            st.write(data["summary"])

def display_action_plan():
    """Display the action plan section."""
    if not st.session_state.action_plan:
        return
        
    data = st.session_state.action_plan
    
    st.header("📅 Action Plan")
    
    # Display priority tasks
    if "priority_tasks" in data and data["priority_tasks"]:
        st.subheader("Priority Tasks")
        for i, task in enumerate(data["priority_tasks"], 1):
            st.write(f"{i}. {task}")
    
    # Display detailed actions
    if "actions" in data and data["actions"]:
        st.subheader("Detailed Actions")
        
        # Convert to DataFrame for better display
        actions_df = pd.DataFrame(data["actions"])
        
        # Ensure all required columns exist
        for col in ["task", "owner", "due_date", "priority", "status"]:
            if col not in actions_df.columns:
                actions_df[col] = "N/A"
        
        # Display the table
        st.dataframe(
            actions_df[["task", "owner", "due_date", "priority", "status"]],
            column_config={
                "task": "Task",
                "owner": "Owner",
                "due_date": "Due Date",
                "priority": "Priority",
                "status": "Status"
            },
            hide_index=True,
            use_container_width=True
        )
    
    # Display schedule recommendations
    if "schedule_recommendations" in data and data["schedule_recommendations"]:
        st.subheader("Schedule Recommendations")
        for rec in data["schedule_recommendations"]:
            st.write(f"- {rec}")
    
    # Display resource recommendations
    if "resource_recommendations" in data and data["resource_recommendations"]:
        st.subheader("Resource Recommendations")
        for rec in data["resource_recommendations"]:
            st.write(f"- {rec}")
    
    # Display summary if available
    if "summary" in data and data["summary"]:
        with st.expander("Plan Summary"):
            st.write(data["summary"])

def main():
    """Main application function."""
    st.title("🚀 Project Manager Dashboard")
    
    # Sidebar for project selection
    with st.sidebar:
        st.header("Project Selection")
        
        # Project selector
        selected_project = st.selectbox(
            "Select a project",
            options=MOCK_PROJECTS,
            index=0
        )
        
        # Process button
        if st.button("Analyze Project", disabled=st.session_state.processing):
            asyncio.run(process_project(selected_project))
        
        # Display status
        if st.session_state.processing:
            st.info("Processing project data... Please wait.")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "This is a 3-Agent PM Dashboard that helps project managers "
            "track project status, identify blockers, and plan next actions."
        )
        st.markdown("\n**Agents:**")
        st.markdown("- Research: Gathers project context")
        st.markdown("- Blocker Detection: Identifies risks and blockers")
        st.markdown("- Action Planner: Recommends next steps")
    
    # Main content area
    if st.session_state.project_data:
        display_project_summary()
        st.markdown("---")
        display_blockers()
        st.markdown("---")
        display_action_plan()
    else:
        st.info("👈 Select a project and click 'Analyze Project' to get started.")

if __name__ == "__main__":
    # Set OpenAI API key from environment variable
    if "OPENAI_API_KEY" not in os.environ:
        st.error("Error: OPENAI_API_KEY environment variable is not set.")
    else:
        openai.api_key = os.environ["OPENAI_API_KEY"]
        main()