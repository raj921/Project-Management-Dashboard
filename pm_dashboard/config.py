import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Project directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Agent Configuration
AGENT_CONFIG = {
    "research": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 2000,
    },
    "blocker_detection": {
        "model": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 1500,
    },
    "action_planner": {
        "model": "gpt-4",
        "temperature": 0.2,
        "max_tokens": 2000,
    }
}

# Mock Data Configuration
MOCK_PROJECTS = [
    "E-commerce Platform Redesign",
    "Mobile App Development",
    "Data Migration Project",
    "Marketing Website Revamp",
    "Internal Tool Development"
]

# Status Options
STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Blocked",
    "In Review",
    "Completed"
]

# Priority Levels
PRIORITY_LEVELS = [
    "Low",
    "Medium",
    "High",
    "Critical"
]