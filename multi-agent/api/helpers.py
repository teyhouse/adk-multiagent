"""Helper functions for API operations."""

import uuid
import json
import asyncio
import logging
from typing import Optional

from google.genai import types
from google.adk.runners import Runner

from config.settings import APP_NAME, session_service, memory_service
from agents.pipeline import code_pipeline_agent

logger = logging.getLogger(__name__)


async def get_or_create_session(user_id: str, session_id: Optional[str] = None):
    """Get existing session or create a new one"""
    if session_id:
        # Try to get existing session
        try:
            return await session_service.get_session(
                app_name=APP_NAME, 
                user_id=user_id, 
                session_id=session_id
            )
        except:
            # Session doesn't exist, create it
            pass
    
    # Create new session with generated ID if none provided
    new_session_id = session_id or str(uuid.uuid4())
    await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=new_session_id
    )
    return await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id, 
        session_id=new_session_id
    )


async def stream_agent_responses(user_id: str, session_id: Optional[str], query: str):
    """Simple generator that yields JSON chunks for each agent response"""
    try:
        # Get or create session for this user
        session = await get_or_create_session(user_id, session_id)
        actual_session_id = session.id
        logger.info(f"Processing stream for User: {user_id}, Session: {actual_session_id}")
        
        # Create runner for this session
        runner = Runner(
            agent=code_pipeline_agent,
            app_name=APP_NAME,
            session_service=session_service,
            memory_service=memory_service
        )
        
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events_async = runner.run_async(
            user_id=user_id, 
            session_id=actual_session_id, 
            new_message=content
        )
        
        async for event in events_async:
            if event.content and event.content.parts and event.content.parts[0].text:
                chunk = {
                    'agent': event.author,
                    'content': event.content.parts[0].text,
                    'is_final': event.is_final_response(),
                    'session_id': actual_session_id  # Include session ID for client
                }
                yield json.dumps(chunk) + "\n"
                await asyncio.sleep(0.05)  # Small delay for smooth streaming
        
        # Save session to memory
        final_session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=user_id, 
            session_id=actual_session_id
        )
        memory_service.add_session_to_memory(final_session)
        
    except Exception as e:
        logger.error(f"Stream error: {e}")
        error_chunk = {'error': str(e)}
        yield json.dumps(error_chunk) + "\n"