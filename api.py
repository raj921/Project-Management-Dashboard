from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
from main import run_agents
import tempfile

app = FastAPI()

# Allow CORS for local React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/dashboard")
def dashboard(file: UploadFile = File(...)):
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        context, blockers, actions = run_agents(tmp_path)
        return JSONResponse({
            "summary": context.get('summary', ''),
            "milestones": context.get('milestones', []),
            "updates": context.get('updates', []),
            "tasks": context.get('tasks', []),
            "blockers": blockers.get('blockers', []),
            "actions": actions.get('actions', [])
        })
    finally:
        os.remove(tmp_path) 