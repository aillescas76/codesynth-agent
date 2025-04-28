import os
from google.adk.agents import LlmAgent

# Define the Implementation Planning Agent
implementation_planner_agent = LlmAgent(
    name="implementation_planner",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your task is to create a detailed, step-by-step implementation plan based on the "
        "software requirement analysis and the existing code context.\n"
        "1. Review the structured requirement details provided in session state under the key 'requirement_details'.\n"
        "2. Review the code context summary provided in session state under the key 'code_context'. If no context was provided, assume a new implementation.\n"
        "3. Generate a clear, actionable plan outlining:\n"
        "    - New files to be created (with paths relative to the project root).\n"
        "    - New functions or classes to be implemented (with signatures and brief descriptions).\n"
        "    - Existing files/functions/classes to be modified (specify changes needed).\n"
        "    - Core logic flow for the implementation.\n"
        "    - Any necessary data structures or interfaces.\n"
        "4. The plan should be detailed enough for another agent (Code Generation Agent) to directly implement the code.\n"
        "5. Format the output plan clearly, for example using Markdown lists or numbered steps."
    ),
    tools=[], # No tools needed for planning
    output_key="implementation_plan" # Save the plan to session state
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
