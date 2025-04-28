import os
from google.adk.agents import LlmAgent
from src.custom_tools import write_file, read_file

# Define the Code Generation Agent
code_generator_agent = LlmAgent(
    name="code_generator",
    model=os.getenv("ADK_LLM_MODEL", "gemini-2.5-flash"), # Use env var or default
    instruction=(
        "Your primary task is to generate code based on a provided implementation plan.\n"
        "1. Carefully review the implementation plan provided in session state under the key 'implementation_plan'.\n"
        "2. Access the code context summary (if available) in session state under the key 'code_context' for understanding existing structures.\n"
        "3. Follow the plan precisely. Generate high-quality, correct, and efficient Python code (unless another language is specified in the plan).\n"
        "4. Adhere to standard coding best practices, including clear variable names, appropriate comments, and logical structure.\n"
        "5. Use the 'write_file' tool to save newly generated code to the specified file paths (relative to the project root). Ensure you use the 'overwrite=True' argument if the plan indicates modifying an existing file.\n"
        "6. Use the 'read_file' tool ONLY if the plan explicitly requires reading an existing file to inform modifications.\n"
        "7. After generating and writing all necessary files according to the plan, output a list of the relative paths of all files you created or modified."
    ),
    tools=[
        write_file,
        read_file
    ],
    # The agent's final text output should be the list of generated/modified paths.
    # We'll rely on the agent's text output for this, but also set output_key
    # in case the LLM directly outputs the list in its final response.
    # A more robust approach might involve a custom agent or callback to
    # aggregate paths from write_file tool calls.
    output_key="generated_code_paths"
)

# Example usage/testing can be added below if needed
# if __name__ == '__main__':
#    # Add code here to test the agent directly
#    pass
