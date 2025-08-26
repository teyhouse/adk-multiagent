"""Code Writer Agent - Generates initial Python code from specifications."""

from google.adk.agents.llm_agent import LlmAgent
from config.settings import MODEL_CONFIG


code_writer_agent = LlmAgent(
    name="CodeWriterAgent",
    model=MODEL_CONFIG,
    instruction="""You are a Python Code Generator.
    Based *only* on the user's request, write Python code that fulfills the requirement.
    Output *only* the complete Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.
    """,
    description="Writes initial Python code based on a specification.",
    output_key="generated_code"  # Stores output in state['generated_code']
)