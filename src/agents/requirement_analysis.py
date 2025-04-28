import os
from google.adk.agents import LlmAgent

# Define the Requirement Analysis Agent
requirement_analyzer_agent = LlmAgent(
    name="requirement_analyzer",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your task is to analyze the user's software requirement provided in the initial "
        "session state under the key 'user_requirement'.\n"
        "1. Understand the core goal of the requirement.\n"
        "2. Identify any ambiguities, missing information, or potential conflicts.\n"
        "3. Decompose the requirement into a clear, structured list of specific features, "
        "user stories, or actionable steps.\n"
        "4. If ambiguities are found, list them clearly.\n"
        "5. Output the analysis in a structured format (e.g., Markdown list or JSON). "
        "Focus on clarity and actionability for the next steps in development planning."
    ),
    tools=[], # No tools needed for this agent at this stage
    output_key="requirement_details" # Save the structured analysis to session state
)

# You can add example usage or testing code below this line if needed,
# typically within an `if __name__ == '__main__':` block for direct testing.
