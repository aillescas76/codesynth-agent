# Step-by-Step Implementation Plan for ADK Requirement System

Based on the system plan and ADK reference documentation, this document outlines the tasks required to implement the multi-agent system for processing software requirements.

**Phase 1: Setup and Core Components**

1.  **Project Initialization:**
    *   Create a main project directory.
    *   Ensure Docker is installed and running on the development machine, as it will be used for sandboxing the test execution tool.
    *   Install the Google Agent Development Kit: `pip install google-adk`.
    *   Create a `.env` file in the project root to store API keys (e.g., `GOOGLE_API_KEY` for AI Studio or `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION` for Vertex AI) and configure `GOOGLE_GENAI_USE_VERTEXAI` accordingly (Ref: Quickstart/Installation).
    *   Establish a basic project structure, for example:
        ```
        project-root/
        ├── .venv/
        ├── .env
        ├── src/
        │   ├── __init__.py
        │   ├── custom_tools.py
        │   ├── agents/
        │   │   ├── __init__.py
        │   │   ├── requirement_analysis.py
        │   │   ├── code_exploration.py
        │   │   ├── implementation_planning.py
        │   │   ├── code_generation.py
        │   │   ├── testing.py
        │   │   ├── refactoring.py
        │   │   └── orchestrator.py
        │   └── main.py  # Entry point to run the system
        └── requirements.txt
        ```

**1.b. Docker Environment Setup:**
    *   Create a `Dockerfile` in the project root.
    *   **Base Image:** Use an official Python base image (e.g., `python:3.11-slim`).
    *   **Working Directory:** Set a working directory within the container (e.g., `/app`).
    *   **Dependencies:**
        *   Copy the `requirements.txt` file into the image.
        *   Install Python dependencies using `pip install --no-cache-dir -r requirements.txt`. Include `google-adk` and any other necessary libraries (like `python-dotenv`, `pytest` if used by `run_tests`).
        *   **Docker Client:** Install the Docker client CLI *inside* the container. This is necessary for the `run_tests` tool to launch separate, sandboxed test containers. Add commands to install the Docker CLI (e.g., using `apt-get update && apt-get install -y docker-ce-cli` on Debian-based images, or follow official Docker installation instructions).
    *   **Project Code:** Copy the project source code (e.g., the `src` directory) into the working directory.
    *   **Configuration:** The `.env` file containing secrets should *not* be copied directly into the image. It should be mounted as a volume or secrets should be passed via environment variables during container runtime (`docker run -e GOOGLE_API_KEY=$GOOGLE_API_KEY ...` or using Docker Compose).
    *   **Docker Socket Access:** When running the container, the Docker daemon socket from the host machine must be mounted as a volume (e.g., `-v /var/run/docker.sock:/var/run/docker.sock`). This allows the Docker client inside the container to communicate with the host's Docker daemon to manage the sandboxed test containers. **Note:** Granting access to the Docker socket has security implications, as it provides significant control over the host system. Ensure this is acceptable in your deployment environment.
    *   **Entrypoint/Command:** Define the default command to run the application (e.g., `CMD ["python", "src/main.py"]`).
    *   **Debugging:** For debugging, the Docker image might include debug tools (like `debugpy`). The `Dockerfile` could expose a debug port (e.g., `EXPOSE 5678`), and the entrypoint could be modified to start the application with the debugger attached.

2.  **Implement Custom Tools (`src/custom_tools.py`):**
    *   **`read_file(path: str) -> str`:**
        *   Implement file reading logic.
        *   **Crucially:** Add a clear docstring explaining its function, arguments (especially the path), and return value for the LLM.
        *   Implement robust error handling (e.g., `FileNotFoundError`, `PermissionError`).
        *   **Security:** Implement strict path validation and sanitization to prevent directory traversal. Ensure it only reads files within the intended project scope.
    *   **`write_file(path: str, content: str, overwrite: bool = False) -> bool`:**
        *   Implement file writing logic, respecting the `overwrite` flag.
        *   Add a clear docstring.
        *   Implement error handling.
        *   **Security:** Implement strict path validation and sanitization. Ensure it only writes files within the intended project scope.
        *   Return a status (e.g., `True` on success, `False` on failure, or a dict `{"status": "success/failure", "message": "..."}`).
    *   **`list_directory(path: str, recursive: bool = False) -> list[str]`:**
        *   Implement directory listing logic.
        *   Add a clear docstring.
        *   Implement error handling.
        *   **Security:** Implement strict path validation and sanitization.
    *   **`run_tests(test_paths: list[str]) -> dict`:**
        *   Implement logic to execute a test runner (like `pytest`) using `subprocess` or a similar mechanism on the specified `test_paths`.
        *   Add a clear docstring explaining it runs tests and returns results.
        *   **Security (Critical):** Execute the test runner within a **securely sandboxed environment using Docker**. This container must have no network access and restricted file system access to prevent malicious code execution. ADK's `built_in_code_execution` or Vertex AI Code Interpreter are safer alternatives if applicable and sufficient, but we will proceed with a custom Docker-based sandbox for this tool.
        *   Parse the output of the test runner to extract pass/fail counts, error details, etc., and return them in a structured dictionary (e.g., `{"status": "PASS/FAIL", "passed": 5, "failed": 1, "errors": [...]}`).
    *   *(Consider if `run_tests` needs `LongRunningFunctionTool` if tests are expected to be slow, otherwise standard `FunctionTool` wrapping via ADK should suffice).*

**Phase 2: Implement Sub-Agents**

3.  **Implement Requirement Analysis Agent (`src/agents/requirement_analysis.py`):**
    *   Import `LlmAgent` from `google.adk.agents`.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"requirement_analyzer"`
        *   `model`: Specify your chosen LLM (e.g., `"gemini-1.5-flash"`).
        *   `instruction`: Provide detailed instructions based on the plan: "Understand, clarify, decompose the user requirement. Identify ambiguities. Output a structured format (list of features/user stories)." Mention it should read `user_requirement` from initial state if applicable.
        *   `tools`: Likely `[]` unless adding interactive clarification.
        *   `output_key`: `"requirement_details"` (to save the structured output to session state).

4.  **Implement Code Exploration Agent (`src/agents/code_exploration.py`):**
    *   Import `LlmAgent` and the `read_file`, `list_directory` tools from `src.custom_tools`.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"code_explorer"`
        *   `model`: Specify LLM.
        *   `instruction`: "Analyze the codebase at `codebase_path` (from session state) based on `requirement_details` (from session state). Locate relevant code sections, identify dependencies, and summarize findings relevant to the requirement."
        *   `tools`: `[read_file, list_directory]`
        *   `output_key`: `"code_context"`

5.  **Implement Implementation Planning Agent (`src/agents/implementation_planning.py`):**
    *   Import `LlmAgent`.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"implementation_planner"`
        *   `model`: Specify LLM.
        *   `instruction`: "Based on `requirement_details` and `code_context` (from session state), create a detailed, step-by-step implementation plan. Outline new functions/classes, modifications, file structures, and logic flow. Output the plan."
        *   `tools`: `[]` (unless adding a formatting tool).
        *   `output_key`: `"implementation_plan"`

6.  **Implement Code Generation Agent (`src/agents/code_generation.py`):**
    *   Import `LlmAgent` and the `write_file`, `read_file` tools.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"code_generator"`
        *   `model`: Specify LLM.
        *   `instruction`: "Follow the `implementation_plan` (from session state) precisely. Generate Python code (or target language). Adhere to best practices. Include comments. Use `write_file` to save new/modified code and `read_file` to read existing code if needed for modification. Consider the `code_context`."
        *   `tools`: `[write_file, read_file]`
        *   `output_key`: `"generated_code_paths"` (Save a list or dict of paths written).

7.  **Implement Testing Agent (`src/agents/testing.py`):**
    *   Import `LlmAgent` and the `write_file`, `read_file`, `run_tests` tools.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"tester"`
        *   `model`: Specify LLM.
        *   `instruction`: "Based on `requirement_details` and `implementation_plan` (from session state), generate unit tests (e.g., pytest format) for the code located at `generated_code_paths` (from session state). Cover main functionality and edge cases. Use `write_file` to save test files. Use `read_file` to examine the code being tested. Finally, use `run_tests` to execute the generated tests."
        *   `tools`: `[write_file, read_file, run_tests]`
        *   `output_key`: `"test_results"` (Save the structured dictionary returned by `run_tests`).

8.  **Implement Refactoring Agent (`src/agents/refactoring.py`):**
    *   Import `LlmAgent` and the `read_file`, `write_file`, `run_tests` tools.
    *   Instantiate `LlmAgent`:
        *   `name`: e.g., `"refactorer"`
        *   `model`: Specify LLM.
        *   `instruction`: "Review the code at `generated_code_paths` (from session state) and the `test_results` (from session state). If tests failed, attempt to fix the code. Apply refactoring for quality, readability, performance based on best practices. Use `read_file` and `write_file` to modify code. Optionally, use `run_tests` again to verify fixes/refactoring."
        *   `tools`: `[read_file, write_file, run_tests]` (Note: Re-running tests here adds complexity/cost).
        *   `output_key`: `"refactored_code_paths"` (or update `generated_code_paths` if modifying in place).

**Phase 3: Orchestration and Execution**

9.  **Implement the Orchestrator Agent (`src/agents/orchestrator.py`):**
    *   **Choose Option B (Custom Agent) for full plan logic.**
    *   Import `BaseAgent`, `InvocationContext`, `Event`, `AsyncGenerator` from ADK.
    *   Import all sub-agent instances.
    *   Define a class inheriting from `BaseAgent`:
        ```python
        # Example Structure (Place actual implementation in the .py file)
        from google.adk.agents import BaseAgent
        from google.adk.sessions import InvocationContext
        from google.adk.events import Event
        from typing import AsyncGenerator

        # Import sub-agent instances
        from .requirement_analysis import requirement_analyzer_agent
        from .code_exploration import code_explorer_agent
        from .implementation_planning import implementation_planner_agent
        from .code_generation import code_generator_agent
        from .testing import tester_agent
        from .refactoring import refactorer_agent

        class RequirementImplementationOrchestrator(BaseAgent):
            def __init__(self):
                # Store sub-agents as attributes
                self.req_analysis_agent = requirement_analyzer_agent
                self.code_explore_agent = code_explorer_agent
                self.plan_agent = implementation_planner_agent
                self.code_gen_agent = code_generator_agent
                self.test_agent = tester_agent
                self.refactor_agent = refactorer_agent
                # Register sub-agents with the framework
                super().__init__(sub_agents=[
                    self.req_analysis_agent, self.code_explore_agent, self.plan_agent,
                    self.code_gen_agent, self.test_agent, self.refactor_agent
                ], name="requirement_implementation_orchestrator") # Give the orchestrator a name

            async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
                print("Starting Requirement Analysis...")
                yield from self.req_analysis_agent.run_async(ctx)
                print("Requirement Analysis Done. State:", ctx.session.state.get("requirement_details"))

                if ctx.session.state.get("codebase_path"):
                    print("Starting Code Exploration...")
                    yield from self.code_explore_agent.run_async(ctx)
                    print("Code Exploration Done. State:", ctx.session.state.get("code_context"))
                else:
                    print("Skipping Code Exploration (no codebase path).")
                    ctx.session.state["code_context"] = "No existing codebase provided." # Set default context

                print("Starting Implementation Planning...")
                yield from self.plan_agent.run_async(ctx)
                print("Planning Done. State:", ctx.session.state.get("implementation_plan"))

                print("Starting Code Generation...")
                yield from self.code_gen_agent.run_async(ctx)
                print("Code Generation Done. State:", ctx.session.state.get("generated_code_paths"))

                print("Starting Testing...")
                yield from self.test_agent.run_async(ctx)
                test_results = ctx.session.state.get("test_results", {})
                print("Testing Done. State:", test_results)

                # Optional: Iterative Refactor/Test Loop
                max_refactor_attempts = 2 # Example limit
                attempt = 0
                while test_results.get("status") != "PASS" and attempt < max_refactor_attempts:
                    attempt += 1
                    print(f"Tests failed/did not pass. Starting Refactoring Attempt {attempt}...")
                    yield from self.refactor_agent.run_async(ctx)
                    print("Refactoring Attempt Done. State:", ctx.session.state.get("refactored_code_paths")) # Or updated generated_code_paths

                    print(f"Re-running Tests after Refactoring Attempt {attempt}...")
                    yield from self.test_agent.run_async(ctx) # Re-run tests
                    test_results = ctx.session.state.get("test_results", {})
                    print("Re-Testing Done. State:", test_results)

                if test_results.get("status") != "PASS":
                    print("Warning: Tests did not pass after maximum refactoring attempts.")
                else:
                    print("Tests passed!")

                print("Workflow Complete.")

        # Instantiate the orchestrator (e.g., in agents/__init__.py or main.py)
        # main_orchestrator = RequirementImplementationOrchestrator()
        ```

10. **Configure Runner and Session Service (`src/main.py`):**
    *   Import the orchestrator agent instance (e.g., `main_orchestrator` from `src.agents`).
    *   Import `Runner` from `google.adk.runners` and `InMemorySessionService` from `google.adk.sessions` (or a persistent one like `DatabaseSessionService` if needed later).
    *   Instantiate the session service: `session_service = InMemorySessionService()`.
    *   Instantiate the runner: `runner = Runner(agent=main_orchestrator, session_service=session_service)`.

11. **Implement Execution Logic (`src/main.py`):**
    *   Create an entry point (e.g., an `async main()` function) that:
        *   Takes the user's requirement (string) and optionally the codebase path (string) as input (e.g., using `argparse`).
        *   Loads environment variables from `.env` (e.g., using `python-dotenv`).
        *   Creates an initial state dictionary: `initial_state = {"user_requirement": requirement}`. Add `"codebase_path": codebase_path` if provided.
        *   Creates a new session using the session service: `session = await session_service.create_session(initial_state=initial_state)`.
        *   Invokes the runner: `async for event in runner.run_async(session_id=session.session_id, query=requirement):`.
        *   Process or print events yielded by the runner for observation (e.g., `print(event)`).
        *   Optionally, retrieve and display the final session state after execution completes: `final_session = await session_service.get_session(session.session_id); print("Final State:", final_session.state)`.
    *   Use `asyncio.run(main())` to run the main function.

**Phase 4: Refinement and Evaluation**

12. **(Optional) Add Callbacks:**
    *   Define callback functions as needed (e.g., for logging tool calls, adding safety checks before `write_file` or `run_tests`).
    *   Register these callbacks in the `LlmAgent` constructors where appropriate (e.g., `after_tool_callback=log_tool_call`).

13. **(Optional) Set Up Evaluation:**
    *   Create `.evalset.json` files containing sample requirements (`query`), expected tool usage (`expected_tool_use`), and potentially key aspects of the final code or test results (`reference`).
    *   Use `adk eval src/agents/__init__.py path/to/your.evalset.json` (assuming the orchestrator is exposed in `src/agents/__init__.py`) or integrate `AgentEvaluator` into a `pytest` suite to run evaluations against the main orchestrator.

14. **Testing, Debugging, and Iteration:**
    *   Run the `main.py` script with various requirements and codebase scenarios.
    *   Monitor the printed events and final state.
    *   Debug issues by examining agent instructions, tool logic, and state transitions.
    *   Refine agent `instruction` prompts for better performance and reliability.
    *   Improve the robustness and security of custom tools.
    *   Adjust the orchestration logic in the `CustomAgent` as needed.
