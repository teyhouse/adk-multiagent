"""Pydantic models for API request/response validation and documentation."""

from pydantic import BaseModel, Field
from typing import Optional, List


class QueryRequest(BaseModel):
    """Request model for querying the multi-agent pipeline."""
    query: str = Field(
        ..., 
        description="The code generation request or specification",
        example="Create a function to calculate fibonacci numbers with memoization"
    )
    user_id: str = Field(
        default="default_user",
        description="Unique identifier for the user making the request",
        example="user123"
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Optional session ID to continue a previous conversation. If not provided, a new session will be created.",
        example="550e8400-e29b-41d4-a716-446655440000"
    )


class AgentStep(BaseModel):
    """Individual agent step in the pipeline."""
    agent: str = Field(..., description="Name of the agent", example="CodeWriterAgent")
    content: str = Field(..., description="Content produced by the agent")
    is_final: bool = Field(..., description="Whether this is the final response from the agent")


class StreamChunk(BaseModel):
    """Individual streaming response chunk."""
    agent: str = Field(..., description="Name of the agent producing this chunk")
    content: str = Field(..., description="Content from the agent")
    is_final: bool = Field(..., description="Whether this is the final response from the agent")
    session_id: str = Field(..., description="Session identifier")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message", example="Invalid request format")


class StandardResponse(BaseModel):
    """Standard non-streaming response model."""
    responses: List[str] = Field(
        ...,
        description="List of responses from all agents in the pipeline",
        example=["```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"]
    )
    session_id: str = Field(
        ...,
        description="Session identifier for this conversation",
        example="550e8400-e29b-41d4-a716-446655440000"
    )