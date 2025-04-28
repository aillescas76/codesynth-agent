import asyncio
import argparse
import os
import json
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
        help="The natural language software requirement to implement."
    )
    parser.add_argument(
        "--codebase-path",
        type=str,
        default=None,
        help="Optional. The relative path to the existing codebase directory within the project."
    )
    args = parser.parse_args()

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
    initial_state = {"user_requirement": args.requirement}
    if args.codebase_path:
        # Basic validation: check if it's not an absolute path and seems plausible
        # More robust validation could be added here or rely on custom_tools validation
        if os.path.isabs(args.codebase_path):
             print(f"Warning: Provided codebase path '{args.codebase_path}' seems absolute. Only relative paths are recommended.")
             # Decide whether to proceed or exit based on policy
        initial_state["codebase_path"] = args.codebase_path # Use the key expected by the orchestrator
        print(f"Initial state includes codebase path: {args.codebase_path}")
    else:
        print("Initial state does not include a codebase path.")

    # --- Session Creation ---
    print("Creating new session...")
    session = await session_service.create_session(initial_state=initial_state)
    print(f"Session created with ID: {session.session_id}")
    print(f"Initial Session State: {initial_state}")

    # --- Agent Execution ---
    print("\n>>> Starting Agent Execution <<<")
    try:
        async for event in runner.run_async(session_id=session.session_id, query=args.requirement):
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
