import os
from google.adk.agents import LlmAgent
from src.custom_tools import read_file, write_file, run_tests

# Define the Refactoring Agent
refactorer_agent = LlmAgent(
    name="refactorer",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your task is to review, potentially fix, and refactor the generated code based on test results and best practices.\n"
        "1. Read the list of generated code paths from session state key 'generated_code_paths'.\n"
        "2. Read the test results dictionary from session state key 'test_results'.\n"
        "3. Analyze the 'test_results':\n"
        "   a. If the 'status' is 'FAIL' or 'ERROR', identify the failing tests or errors from the 'output'. Use 'read_file' to examine the relevant code from 'generated_code_paths' and the corresponding test files (infer test file paths based on convention, e.g., 'test_*.py'). Determine the cause of the failures.\n"
        "   b. Modify the code in the relevant files using 'read_file' to get the current content and 'write_file' (with overwrite=True) to save the corrected code. Focus *only* on fixing the issues causing test failures.\n"
        "   c. If the 'status' is 'PASS', proceed to step 4 (refactoring).\n"
        "4. If the tests passed initially OR after you applied fixes in step 3b, review the code in 'generated_code_paths' for potential improvements.\n"
        "   a. Use 'read_file' to examine the code.\n"
        "   b. Apply refactoring to improve code quality, readability, maintainability, and performance, adhering to standard Python best practices (e.g., PEP 8). Consider aspects like variable naming, function length, complexity, comments, and potential optimizations.\n"
        "   c. Use 'write_file' (with overwrite=True) to save the refactored code.\n"
        "5. **Optional Verification:** After making fixes or refactoring changes, you *may* use the 'run_tests' tool again on the relevant test file paths to verify that your changes did not break functionality and that fixes were successful. Be mindful that running tests again adds processing time and cost.\n"
        "6. Output a list of the relative paths of all files you modified during the fixing or refactoring process."

    ),
    tools=[
        read_file,
        write_file,
        run_tests # Tool is available, but instruction guides optional use
    ],
    # Similar to code generation, we rely on the agent's final text output
    # for the list of modified paths, but set output_key as a fallback.
    output_key="refactored_code_paths"
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
