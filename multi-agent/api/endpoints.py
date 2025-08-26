"""API endpoint handlers."""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from google.genai import types
from google.adk.runners import Runner

from models.api_models import QueryRequest, ErrorResponse, StandardResponse
from config.settings import APP_NAME, session_service, memory_service
from agents.pipeline import code_pipeline_agent
from .helpers import get_or_create_session, stream_agent_responses

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/ask_stream",
    tags=["streaming", "code-generation"],
    summary="Stream Multi-Agent Code Generation",
    description="""
    **Real-time streaming endpoint** that processes your code generation request through the multi-agent pipeline.
    
    ### How it works:
    1. **CodeWriterAgent** generates initial code
    2. **CodeReviewerAgent** reviews and provides feedback  
    3. **CodeRefactorerAgent** refactors based on feedback
    
    ### Response Format:
    Returns streaming JSON chunks, each containing:
    - `agent`: Name of the agent producing the response
    - `content`: The agent's output (code, review, or refactored code)
    - `is_final`: Boolean indicating if this is the agent's final response
    - `session_id`: Session identifier for conversation continuity
    
    ### Use Cases:
    - Interactive web applications requiring live updates
    - Real-time monitoring of agent progress
    - Applications where user engagement during processing is important
    """,
    responses={
        200: {
            "description": "Streaming JSON chunks from each agent",
            "content": {
                "application/json": {
                    "example": {
                        "agent": "CodeWriterAgent",
                        "content": "```python\\ndef fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)\\n```",
                        "is_final": True,
                        "session_id": "550e8400-e29b-41d4-a716-446655440000"
                    }
                }
            }
        },
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def ask_agent_stream(req: QueryRequest):
    """Stream real-time responses from the multi-agent code generation pipeline."""
    logger.info(f"Stream request - User: {req.user_id}, Session: {req.session_id}, Query: {req.query[:50]}...")
    return StreamingResponse(
        stream_agent_responses(req.user_id, req.session_id, req.query),
        media_type="application/json",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post(
    "/ask",
    tags=["code-generation"],
    summary="Complete Multi-Agent Code Generation",
    description="""
    **Standard endpoint** that processes your code generation request through the complete multi-agent pipeline and returns all results at once.
    
    ### How it works:
    1. **CodeWriterAgent** generates initial Python code from your specification
    2. **CodeReviewerAgent** reviews the code and provides constructive feedback
    3. **CodeRefactorerAgent** applies improvements based on the review
    
    ### Response:
    Returns a complete response containing:
    - `responses`: Array of final responses from each agent
    - `session_id`: Session identifier for conversation continuity
    
    ### Use Cases:
    - API integrations requiring complete responses
    - Batch processing scenarios
    - Applications where you need all results at once
    - Integration with other services or pipelines
    
    ### Example Request:
    ```json
    {
        "query": "Create a function to validate email addresses with regex",
        "user_id": "developer123",
        "session_id": "optional-existing-session-id"
    }
    ```
    """,
    response_model=StandardResponse,
    responses={
        200: {
            "model": StandardResponse,
            "description": "Successfully processed request through all agents"
        },
        422: {"model": ErrorResponse, "description": "Invalid request format"},
        500: {"model": ErrorResponse, "description": "Internal processing error"}
    }
)
async def ask_agent(req: QueryRequest):
    """Process code generation request through the complete multi-agent pipeline."""
    logger.info(f"Non-stream request - User: {req.user_id}, Session: {req.session_id}, Query: {req.query[:50]}...")
    try:
        # Get or create session
        session = await get_or_create_session(req.user_id, req.session_id)
        actual_session_id = session.id
        
        # Create runner
        runner = Runner(
            agent=code_pipeline_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service
        )
        
        content = types.Content(role="user", parts=[types.Part(text=req.query)])
        events = runner.run(user_id=req.user_id, session_id=actual_session_id, new_message=content)

        responses = []
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                responses.append(event.content.parts[0].text)

        # Save session to memory after each turn
        final_session = await session_service.get_session(app_name=APP_NAME, user_id=req.user_id, session_id=actual_session_id)
        memory_service.add_session_to_memory(final_session)

        return StandardResponse(
            responses=responses or ["No response received."],
            session_id=actual_session_id
        )
    except Exception as e:
        logger.error(f"Ask error: {e}")
        return ErrorResponse(error=str(e))


@router.get(
    "/",
    tags=["health"],
    summary="API Health Check",
    description="Simple health check endpoint to verify the API is running.",
    responses={
        200: {
            "description": "API is healthy and running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "message": "Multi-Agent Code Generation Pipeline API",
                        "version": "1.0.0"
                    }
                }
            }
        }
    }
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Multi-Agent Code Generation Pipeline API",
        "version": "1.0.0"
    }


@router.get(
    "/health",
    tags=["health"],
    summary="Detailed Health Status",
    description="Detailed health check with service status information.",
    responses={
        200: {
            "description": "Detailed health status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "agents": {
                            "CodeWriterAgent": "active",
                            "CodeReviewerAgent": "active", 
                            "CodeRefactorerAgent": "active"
                        },
                        "services": {
                            "session_service": "active",
                            "memory_service": "active"
                        },
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            }
        }
    }
)
async def detailed_health():
    """Detailed health check with service status."""
    return {
        "status": "healthy",
        "agents": {
            "CodeWriterAgent": "active",
            "CodeReviewerAgent": "active",
            "CodeRefactorerAgent": "active"
        },
        "services": {
            "session_service": "active",
            "memory_service": "active"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }