"""Application settings and configuration."""

from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv()

# Model configuration for Gemini
MODEL = "gemini-2.5-flash"

MODEL_CONFIG = LiteLlm(
    "openai/llama3.2:1b",
    api_base="http://192.168.237.77:11434/v1",
    api_key="placeholder"
)

# Application constants
APP_NAME = "code_pipeline_app"

# Initialize services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()