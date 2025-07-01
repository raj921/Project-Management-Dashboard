
# Project Management Dashboard

A simple project management dashboard to track progress and identify blockers.

## Quick Start

1. **Install Dependencies**
   - Python 3.8+
   - Node.js 16+
   - npm or yarn

2. **Setup**
   ```bash
   # Clone and enter project
   git clone https://github.com/raj921/Project-Management-Dashboard.git
   cd Project-Management-Dashboard
   
   # Set up backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up frontend
   cd frontend
   npm install
   cd ..
   ```

3. **Configure**
   Create `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

4. **Run**
   ```bash
   # Start backend
   python api.py
   
   # In new terminal, start frontend
   cd frontend
   npm start
   ```

5. Open `http://localhost:3000` in your browser
