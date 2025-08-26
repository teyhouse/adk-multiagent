"""Pipeline Agent - Orchestrates the sequential execution of code generation agents."""

from google.adk.agents.sequential_agent import SequentialAgent
from .code_writer import code_writer_agent
from .code_reviewer import code_reviewer_agent  
from .code_refactorer import code_refactorer_agent


# This agent orchestrates the pipeline by running the sub_agents in order.
code_pipeline_agent = SequentialAgent(
    name="CodePipelineAgent",
    sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent],
    description="Executes a sequence of code writing, reviewing, and refactoring.",
    # The agents will run in the order provided: Writer -> Reviewer -> Refactorer
)