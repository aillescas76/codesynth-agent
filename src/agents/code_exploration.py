import os
from google.adk.agents import LlmAgent
from src.custom_tools import read_file, list_directory

# Define the Code Exploration Agent
code_explorer_agent = LlmAgent(
    name="code_explorer",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your task is to explore an existing codebase to provide context for implementing "
        "a software requirement.\n"
        "1. Read the requirement details provided in the session state under the key 'requirement_details'.\n"
        "2. Read the base path of the codebase provided in the session state under the key 'codebase_path'.\n"
        "3. Use the 'list_directory' tool to understand the structure of the codebase, starting from the 'codebase_path'. You might need to use it recursively.\n"
        "4. Use the 'read_file' tool to examine the contents of potentially relevant files based on the requirement details and the directory structure.\n"
        "5. Identify key files, functions, classes, or modules that might need modification or integration.\n"
        "6. Identify potential dependencies or areas of impact within the codebase.\n"
        "7. Summarize your findings concisely, focusing on information that will be useful for planning the implementation. Highlight relevant file paths and code structures."
    ),
    tools=[
        read_file,
        list_directory
    ],
    output_key="code_context" # Save the summary to session state
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
