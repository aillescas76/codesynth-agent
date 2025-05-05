import asyncio
import asyncio
import argparse
import os
import json
import pathlib # Added import
from dotenv import load_dotenv

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Import the main orchestrator agent instance
# Assumes the instance 'main_orchestrator' is defined in src/agents/orchestrator.py
# and src/agents/__init__.py might expose it or orchestrator.py is directly imported.
# Adjust the import path if necessary based on your project structure.
try:
    # Assuming src is in PYTHONPATH or running from root
    from agents.orchestrator import main_orchestrator
except ImportError as e:
    print(f"Error: Could not import main_orchestrator from agents.orchestrator: {e}")
    print("Ensure the file exists and the instance is correctly defined.")
    print("Also check your PYTHONPATH or how you are running the script.")
    exit(1)


async def main():
    """
    Main execution function to run the requirement implementation workflow.
    Parses command-line arguments, sets up the ADK runner, executes the
    orchestrator agent, and prints events and final state.
    """
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run the ADK Requirement Implementation Agent System.")
    parser.add_argument(
        "--requirement",
        type=str,
        required=True,
        # Update help text to indicate it's a file path
        help="The path to a file containing the natural language software requirement."
    )
    # Keep the --project-path argument as is (Note: This replaces --codebase-path)
    parser.add_argument(
        "--project-path",
        type=str,
        required=True, # Make project path required
        help="The relative path to the target project directory for code exploration, generation, and review."
    )
    args = parser.parse_args()

    # --- Read Requirement from File ---
    requirement_file_path = args.requirement
    try:
        # Ensure the path is treated as a file path
        req_path = pathlib.Path(requirement_file_path)
        if not req_path.is_file():
             print(f"Error: Requirement file not found or is not a file: {requirement_file_path}")
             exit(1)
        user_requirement_text = req_path.read_text(encoding='utf-8')
        print(f"Successfully read requirement from: {requirement_file_path}")
    except FileNotFoundError:
        print(f"Error: Requirement file not found: {requirement_file_path}")
        exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading requirement file: {requirement_file_path}")
        exit(1)
    except Exception as e:
        print(f"Error reading requirement file '{requirement_file_path}': {e}")
        exit(1)

    # --- Environment Setup ---
    # Load environment variables from .env file (especially API keys)
    if load_dotenv():
        print("Loaded environment variables from .env")
    else:
        print("Warning: .env file not found or empty.")
        # Check for essential env vars if needed (e.g., API keys)
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_CLOUD_PROJECT"):
             print("Warning: GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT not found in environment. LLM calls may fail.")


    # --- ADK Setup ---
    print("Setting up ADK Runner and Session Service...")
    # Use InMemorySessionService for simplicity; replace for persistence
    session_service = InMemorySessionService()
    runner = Runner(agent=main_orchestrator, session_service=session_service)
    print("ADK Runner configured.")

    # --- Initial State ---
    # Use the text read from the file
    initial_state = {"user_requirement": user_requirement_text}

    # Add the project_path logic (using the new required argument)
    if os.path.isabs(args.project_path):
         print(f"Warning: Provided project path '{args.project_path}' seems absolute. Only relative paths within the agent's execution context are recommended for security.")
         # Consider adding an exit(1) here if absolute paths are strictly forbidden
    initial_state["project_path"] = args.project_path # Use the key expected by agents needing the base path
    print(f"Initial state includes project path: {args.project_path}")

    # --- Session Creation ---
    print("Creating new session...")
    session = await session_service.create_session(initial_state=initial_state)
    print(f"Session created with ID: {session.session_id}")
    print(f"Initial Session State: {initial_state}")

    # --- Agent Execution ---
    print("\n>>> Starting Agent Execution <<<")
    try:
        # Pass the requirement text itself in the query, not the path
        async for event in runner.run_async(session_id=session.session_id, query=user_requirement_text):
            # Print events for observation during execution
            # You might want to filter or format specific event types
            print(f"\n--- Event Received ---")
            print(f"Type: {type(event).__name__}")
            # Pretty print the event dictionary if it has one
            # Use model_dump_json for Pydantic v2+
            if hasattr(event, 'model_dump_json'):
                 print(event.model_dump_json(indent=2))
            elif hasattr(event, 'dict'): # Fallback for older Pydantic or other dict-like objects
                 print(json.dumps(event.dict(), indent=2, default=str))
            else:
                 print(event)
            print("----------------------")

    except Exception as e:
        print(f"\n!!! An error occurred during agent execution: {e} !!!")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
    finally:
        # --- Final State Retrieval ---
        print("\n>>> Agent Execution Finished <<<")
        try:
            final_session = await session_service.get_session(session.session_id)
            print("\n--- Final Session State ---")
            # Use default=str to handle non-serializable types like Path objects if they end up in state
            print(json.dumps(final_session.state, indent=2, default=str))
            print("-------------------------")
        except Exception as e:
            print(f"Error retrieving final session state: {e}")


if __name__ == "__main__":
    # Ensure the script runs within an asyncio event loop
    asyncio.run(main())
