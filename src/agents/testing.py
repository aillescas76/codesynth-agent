import os
from google.adk.agents import LlmAgent
from src.custom_tools import write_file, read_file, run_tests

# Define the Testing Agent
tester_agent = LlmAgent(
    name="tester",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your task is to generate and execute unit tests for the provided code based on the requirements and implementation plan.\n"
        "1. Review the requirement details from session state key 'requirement_details'.\n"
        "2. Review the implementation plan from session state key 'implementation_plan'.\n"
        "3. Identify the paths of the generated code from session state key 'generated_code_paths'. This should be a list of relative file paths.\n"
        "4. For each relevant code file in 'generated_code_paths':\n"
        "    a. Use the 'read_file' tool to examine the code content.\n"
        "    b. Generate comprehensive unit tests using the pytest framework and conventions.\n"
        "    c. Ensure tests cover the main functionality described in the requirements/plan, including edge cases and potential error conditions.\n"
        "    d. Determine an appropriate relative path for the test file. A good convention is to place it in the same directory as the code file, prefixing the filename with 'test_' (e.g., if code is 'src/module/widget.py', the test file could be 'src/module/test_widget.py').\n"
        "    e. Use the 'write_file' tool to save the generated pytest code to the determined test file path. Use overwrite=True if necessary.\n"
        "5. After generating and writing all test files, gather the list of relative paths for *all the test files you created*.\n"
        "6. Use the 'run_tests' tool, providing it with the list of relative paths to the test files you just created.\n"
        "7. The final output of your execution should be the result dictionary returned by the 'run_tests' tool."
    ),
    tools=[
        write_file,
        read_file,
        run_tests
    ],
    # The run_tests tool returns a dictionary which will be captured.
    output_key="test_results"
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
