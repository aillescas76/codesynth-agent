import os
from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.sessions import InvocationContext
from google.adk.events import Event

# Import sub-agent instances
# Ensure these files exist and the agent instances are correctly defined within them.
 from .requirement_analysis import requirement_analyzer_agent
 from .code_exploration import code_explorer_agent
 from .implementation_planning import implementation_planner_agent
 from .code_generation import code_generator_agent
 from .testing import tester_agent
 from .refactoring import refactorer_agent

# Placeholder agents until the real ones are created
from google.adk.agents import LlmAgent # Use LlmAgent as a placeholder type


# Configuration for the refactor loop
MAX_REFACTOR_ATTEMPTS = int(os.environ.get("MAX_REFACTOR_ATTEMPTS", 2)) # Default to 2 attempts

class RequirementImplementationOrchestrator(BaseAgent):
    """
    Orchestrates the end-to-end workflow for implementing a software requirement
    using specialized sub-agents.
    """
    def __init__(self):
        """Initializes the orchestrator with all necessary sub-agents."""
        # Store sub-agents as attributes for clarity
        self.req_analysis_agent = requirement_analyzer_agent
        self.code_explore_agent = code_explorer_agent
        self.plan_agent = implementation_planner_agent
        self.code_gen_agent = code_generator_agent
        self.test_agent = tester_agent
        self.refactor_agent = refactorer_agent

        # Register sub-agents with the framework for proper event handling etc.
        super().__init__(sub_agents=[
            self.req_analysis_agent,
            self.code_explore_agent,
            self.plan_agent,
            self.code_gen_agent,
            self.test_agent,
            self.refactor_agent
        ], name="requirement_implementation_orchestrator") # Give the orchestrator a name

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Implements the custom logic for the requirement implementation workflow.
        """
        print("\n--- Starting Requirement Analysis ---")
        async for event in self.req_analysis_agent.run_async(ctx):
            yield event
        print("--- Requirement Analysis Done ---")
        print(f"State['requirement_details']: {ctx.session.state.get('requirement_details')}")

        # Check if codebase exploration is needed
        # Use a placeholder key for now, adjust as needed based on initial input
        if ctx.session.state.get("initial_codebase_path"):
            print("\n--- Starting Code Exploration ---")
            # Pass the path to the explorer agent, potentially via state or context modification if needed
            # ctx.session.state["codebase_path"] = ctx.session.state.get("initial_codebase_path") # Example
            async for event in self.code_explore_agent.run_async(ctx):
                yield event
            print("--- Code Exploration Done ---")
            print(f"State['code_context']: {ctx.session.state.get('code_context')}")
        else:
            print("\n--- Skipping Code Exploration (no initial_codebase_path provided in session state) ---")
            # Set a default context if exploration is skipped
            ctx.session.state["code_context"] = "No existing codebase provided or explored."

        print("\n--- Starting Implementation Planning ---")
        async for event in self.plan_agent.run_async(ctx):
            yield event
        print("--- Implementation Planning Done ---")
        print(f"State['implementation_plan']: {ctx.session.state.get('implementation_plan')}")

        print("\n--- Starting Code Generation ---")
        async for event in self.code_gen_agent.run_async(ctx):
            yield event
        print("--- Code Generation Done ---")
        print(f"State['generated_code_paths']: {ctx.session.state.get('generated_code_paths')}")

        # Ensure generated_code_paths exists before testing
        if not ctx.session.state.get("generated_code_paths"):
             print("\n--- Skipping Testing and Refactoring: No generated code paths found. ---")
             print("\n--- Workflow Complete (Ended Early) ---")
             return # Exit the workflow if no code was generated

        print("\n--- Starting Testing ---")
        async for event in self.test_agent.run_async(ctx):
            yield event
        test_results = ctx.session.state.get("test_results", {})
        print("--- Testing Done ---")
        print(f"State['test_results']: {test_results}")

        # --- Iterative Refactor/Test Loop ---
        attempt = 0
        # Check if 'status' key exists and if it's not 'PASS'
        # Handle potential case differences and ensure status exists
        while test_results.get("status", "UNKNOWN").upper() != "PASS" and attempt < MAX_REFACTOR_ATTEMPTS:
            attempt += 1
            print(f"\n--- Tests Failed/Errored/Unknown. Starting Refactoring Attempt {attempt}/{MAX_REFACTOR_ATTEMPTS} ---")
            async for event in self.refactor_agent.run_async(ctx):
                yield event
            print(f"--- Refactoring Attempt {attempt} Done ---")
            # Assuming refactor agent updates files in place or updates 'generated_code_paths'
            print(f"State['generated_code_paths' after refactor]: {ctx.session.state.get('generated_code_paths')}")

            print(f"\n--- Re-running Tests after Refactoring Attempt {attempt} ---")
            async for event in self.test_agent.run_async(ctx): # Re-run tests
                yield event
            test_results = ctx.session.state.get("test_results", {}) # Update results
            print(f"--- Re-Testing Done (Attempt {attempt}) ---")
            print(f"State['test_results']: {test_results}")

        # Final status check after the loop
        if test_results.get("status", "UNKNOWN").upper() != "PASS":
            print(f"\n--- Warning: Tests did not pass after {attempt} refactoring attempts. Final Status: {test_results.get('status', 'UNKNOWN')} ---")
        else:
            print("\n--- Tests Passed! ---")

        print("\n--- Workflow Complete ---")

# Instantiate the orchestrator agent.
# This instance will be imported by the main execution script or runner setup.
main_orchestrator = RequirementImplementationOrchestrator()
