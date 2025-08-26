"""
Multi-Agent Code Generation Pipeline

A FastAPI application that orchestrates a sequential multi-agent system 
for Python code generation, review, and refactoring.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.endpoints import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup - services are initialized via imports
    logger.info("Multi-Agent Code Generation Pipeline starting up...")
    yield
    # Shutdown (if needed)
    logger.info("Multi-Agent Code Generation Pipeline shutting down...")


# FastAPI application with comprehensive OpenAPI metadata
app = FastAPI(
    title="Multi-Agent Code Generation Pipeline",
    description="""
    A sequential multi-agent system for Python code generation, review, and refactoring.
    
    ## Pipeline Overview
    
    The system consists of three specialized agents working in sequence:
    
    1. **CodeWriterAgent** - Generates initial Python code from natural language specifications
    2. **CodeReviewerAgent** - Reviews the generated code and provides constructive feedback
    3. **CodeRefactorerAgent** - Refactors the code based on review comments
    
    ## Usage
    
    - Use `/ask_stream` for real-time streaming responses (recommended for UI applications)
    - Use `/ask` for complete responses (recommended for API integrations)
    
    ## Session Management
    
    Sessions are automatically managed to maintain conversation context. You can:
    - Let the system create a new session automatically
    - Provide a specific `session_id` to continue a previous conversation
    
    ## Model Configuration
    
    Currently configured to use:
    - **Primary**: Local Ollama Llama 3.2:1b model
    - **Alternative**: Google Gemini 2.5 Flash (configurable)
    """,
    version="1.0.0",
    contact={
        "name": "Multi-Agent Code Pipeline",
        "url": "https://github.com/your-repo/multi-agent",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    tags_metadata=[
        {
            "name": "code-generation",
            "description": "Endpoints for generating, reviewing, and refactoring Python code",
        },
        {
            "name": "streaming",
            "description": "Real-time streaming endpoints for live agent updates",
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints",
        },
    ],
)

# Include API routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port to avoid conflicts