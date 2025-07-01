# Project Manager Dashboard with Multi-Agent System

A 3-agent system that helps project managers track project status, identify blockers, and plan next actions.

## Features

- **Research Agent**: Gathers and structures project information from various sources
- **Blocker Detection Agent**: Identifies potential risks and blockers in the project
- **Action Planner Agent**: Recommends prioritized next steps based on project status
- **Interactive Dashboard**: Streamlit-based UI for easy interaction
- **Mock Data Generation**: Built-in mock data for demonstration purposes

## Prerequisites

- Python 3.8+
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pm_dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   ```bash
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   ```

## Usage

1. Start the Streamlit application:
   ```bash
   streamlit run main.py
   ```

2. Open your web browser and navigate to `http://localhost:8501`

3. Select a project from the sidebar and click "Analyze Project" to see the dashboard in action

## Project Structure

```
pm_dashboard/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Base class for all agents
│   ├── research_agent.py   # Research Agent implementation
│   ├── blocker_detection_agent.py  # Blocker Detection Agent
│   └── action_planner_agent.py     # Action Planner Agent
├── static/                 # Static files (CSS, images, etc.)
├── templates/              # HTML templates (if needed)
├── .env.example           # Example environment variables
├── config.py              # Application configuration
├── main.py                # Main application and UI
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

## How It Works

1. **Research Agent**: 
   - Gathers project information from various sources (documents, chat logs, etc.)
   - Extracts and structures key project details (milestones, tasks, team members)

2. **Blocker Detection Agent**:
   - Analyzes the structured project data
   - Identifies current blockers and potential risks
   - Provides severity assessment and recommended actions

3. **Action Planner Agent**:
   - Takes project data and blockers as input
   - Generates a prioritized action plan
   - Suggests schedule adjustments and resource allocations

## Customization

- Edit `config.py` to modify agent configurations, project settings, and mock data
- Add new project templates in the `MOCK_PROJECTS` list in `config.py`
- Extend the agent classes in the `agents/` directory to add new functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
