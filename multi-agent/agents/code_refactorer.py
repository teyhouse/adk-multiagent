"""Code Refactorer Agent - Refactors code based on review comments."""

from google.adk.agents.llm_agent import LlmAgent
from config.settings import MODEL_CONFIG


code_refactorer_agent = LlmAgent(
    name="CodeRefactorerAgent",
    model=MODEL_CONFIG,
    instruction="""You are a Python Code Refactoring AI.
    Your goal is to improve the given Python code based on the provided review comments.

    **Original Code:**
    ```python
    {generated_code}
    ```

    **Review Comments:**
    {review_comments}

    **Task:**
    Carefully apply the suggestions from the review comments to refactor the original code.
    If the review comments state "No major issues found," return the original code unchanged.
    Ensure the final code is complete, functional, and includes necessary imports and docstrings.

    **Output:**
    Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.
    """,
    description="Refactors code based on review comments.",
    output_key="refactored_code",  # Stores output in state['refactored_code']
)