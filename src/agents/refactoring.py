import os
from google.adk.agents import LlmAgent
# Import necessary tools
from src.custom_tools import read_file, write_file, run_tests # Ensure these imports are present

# Define the Refactoring Agent
refactorer_agent = LlmAgent(
    name="refactorer",
    model=os.getenv("ADK_LLM_MODEL", "gemini-1.5-flash"), # Use env var or default
    instruction=(
        # Instruction should already be updated from previous step to mention base_path_str
        "Your task is to review, potentially fix, and refactor the generated code based on test results and code review feedback.\n"
        "1. Read the list of generated code paths from session state key 'generated_code_paths'. These paths are relative to the project path.\n"
        "2. Read the test results dictionary from session state key 'test_results'.\n"
        "3. Read the code review summary from session state key 'code_review_summary' (if available).\n"
        "4. Read the target project directory path from session state under the key 'project_path'. This is the root directory for all file operations.\n"
        "5. Analyze the 'test_results':\n"
        "   a. If the 'status' is 'FAIL' or 'ERROR', identify the failing tests or errors from the 'output'.\n"
        "   b. Analyze the 'code_review_summary' for suggested improvements.\n"
        "6. Modify the code in the relevant files to address the failures, errors, or review comments. Use 'read_file' to get the current content and 'write_file' (with overwrite=True) to save changes. When calling these tools, you MUST provide the 'base_path_str' argument with the value from 'project_path', and the 'path' argument must be the relative path within that base path.\n"
        "7. Aim to fix bugs, improve clarity, and adhere to the original plan and requirements.\n"
        "8. After making modifications, output a summary of the changes made."
    ),
    tools=[
        read_file,
        write_file,
        run_tests # Add the imported tools here
    ],
    output_key="refactored_code_paths" # Or potentially a summary key
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
