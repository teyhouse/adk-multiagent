"""Code Reviewer Agent - Reviews generated code and provides feedback."""

from google.adk.agents.llm_agent import LlmAgent
from config.settings import MODEL_CONFIG


code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model=MODEL_CONFIG,
    instruction="""You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

    **Review Criteria:**
    1.  **Correctness:** Does the code work as intended? Are there logic errors?
    2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
    3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
    4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
    5.  **Best Practices:** Does the code follow common Python best practices?

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
    If the code is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues" statement.
    """,
    description="Reviews code and provides feedback.",
    output_key="review_comments",  # Stores output in state['review_comments']
)