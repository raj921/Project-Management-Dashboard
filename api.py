from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
import pandas as pd
import os
import tempfile
import hashlib
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Import Redis utilities
from pm_dashboard.utils import redis_manager, cache_result

app = FastAPI(title="Project Management Dashboard API",
             description="API for the Project Management Dashboard with Redis Caching",
             version="1.0.0")

# Allow CORS for local React dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
@app.get("/healthz")  # Render's default health check path
async def health_check() -> Dict[str, str]:
    """Health check endpoint to verify API and Redis connectivity."""
    redis_status = "enabled" if redis_manager.is_connected() else "disabled"
    return {
        "status": "healthy",
        "redis": redis_status,
        "version": "1.0.0"
    }

# Cache control model
class CacheControl(BaseModel):
    no_cache: bool = False

# Cache key generator
def generate_cache_key(file_content: bytes) -> str:
    """Generate a cache key based on file content."""
    return f"dashboard:{hashlib.sha256(file_content).hexdigest()}"

@app.post("/dashboard")
async def dashboard(
    file: UploadFile = File(...),
    cache_control: CacheControl = Depends()
) -> Dict[str, Any]:
    """
    Process project dashboard data with optional caching.
    
    Args:
        file: Excel file containing project data
        cache_control: Cache control parameters
        
    Returns:
        Processed dashboard data with summary, tasks, blockers, and actions
    """
    # Read file content
    file_content = await file.read()
    
    # Generate cache key
    cache_key = generate_cache_key(file_content)
    
    # Check cache if not explicitly bypassed
    if not cache_control.no_cache and redis_manager.is_connected():
        cached_data = redis_manager.get(cache_key)
        if cached_data:
            return {
                **cached_data,
                "cached": True,
                "cache_key": cache_key
            }
    
    # Save uploaded file to a temp location
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Process the file
        from main import run_agents  # Lazy import to avoid circular imports
        context, blockers, actions = run_agents(tmp_path)
        
        # Prepare response
        response_data = {
            "summary": context.get('summary', ''),
            "milestones": context.get('milestones', []),
            "updates": context.get('updates', []),
            "tasks": context.get('tasks', []),
            "blockers": blockers.get('blockers', []),
            "actions": actions.get('actions', []),
            "cached": False
        }
        
        # Cache the result if Redis is available
        if redis_manager.is_connected():
            redis_manager.set(cache_key, response_data)
        
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Clean up temp file
        try:
            os.remove(tmp_path)
        except:
            pass

# Cache management endpoints
@app.post("/cache/clear")
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching a pattern."""
    if not redis_manager.is_connected():
        return {"status": "error", "message": "Redis is not available"}
    
    count = redis_manager.clear_cache(f"dashboard:{pattern}")
    return {"status": "success", "message": f"Cleared {count} cache entries"}

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    if not redis_manager.is_connected():
        return {"status": "error", "message": "Redis is not available"}
    
    client = redis_manager.client
    if not client:
        return {"status": "error", "message": "Redis client not available"}
    
    try:
        # Get basic Redis info
        info = client.info()
        
        # Count dashboard cache keys
        cache_keys = client.keys("dashboard:*")
        
        return {
            "status": "success",
            "redis_version": info.get("redis_version"),
            "uptime_seconds": info.get("uptime_in_seconds"),
            "used_memory_human": info.get("used_memory_human"),
            "total_connections_received": info.get("total_connections_received"),
            "total_commands_processed": info.get("total_commands_processed"),
            "cache_entries": len(cache_keys),
            "cache_keys": cache_keys[:10]  # Return first 10 keys as sample
        }
    except Exception as e:
        return {"status": "error", "message": f"Error getting cache stats: {str(e)}"} 