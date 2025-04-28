## **Plan: ADK Agent System for Requirement Implementation**

**1\. Goal:**

To develop a system using the Google Agent Development Kit (ADK) that takes a natural language software requirement, potentially interacts with an existing codebase, and produces a planned, implemented, tested, and refactored code solution.

**2\. Architecture:**

A **Multi-Agent System** is recommended. This involves several specialized agents coordinated by an orchestrator agent. This promotes modularity and allows each agent to focus on a specific task.

* **Orchestrator:** A SequentialAgent or CustomAgent will manage the overall workflow, invoking sub-agents in a defined order or with custom logic. A SequentialAgent is simpler for a linear process, while a CustomAgent offers more flexibility (e.g., conditional execution, loops).  
* **Sub-Agents:** Dedicated LlmAgent instances for each stage of the process.  
* **Data Flow:** Information (requirements, plans, code snippets, test results) will be passed between agents primarily using **Session State** (ctx.session.state accessed via InvocationContext or ToolContext, and populated using output\_key on LlmAgents).

**3\. Defined Agents (Sub-Agents):**

Each agent below will likely be an instance of LlmAgent, configured with specific instructions, tools, and potentially input/output schemas (though output\_schema disables tools/delegation, so careful use is needed).

* **A. Requirement Analysis Agent:**  
  * **Purpose:** Understand, clarify, and decompose the initial user requirement into actionable steps or specifications.  
  * **Instructions:** Focus on understanding intent, identifying ambiguities, breaking down complex requests, and outputting a structured format (e.g., list of features, user stories).  
  * **Tools:** (Optional) Could include a FunctionTool to ask clarifying questions if interacting with a user interface.  
  * **Output:** Structured requirement details (saved to session state, e.g., output\_key="requirement\_details").  
* **B. Code Exploration Agent:**  
  * **Purpose:** (If applicable) Analyze an existing codebase to understand structure, identify relevant files/functions for modification or integration, and provide context for planning.  
  * **Instructions:** Given requirement\_details and a codebase path (from session state or initial config), locate relevant code sections, identify dependencies, and summarize findings.  
  * **Tools:**  
    * read\_file(path: str) \-\> str: Custom FunctionTool to read file contents.  
    * list\_directory(path: str, recursive: bool \= False) \-\> list\[str\]: Custom FunctionTool to explore the file system.  
    * (Advanced) Potentially tools integrating with static analysis libraries.  
  * **Input:** requirement\_details (from state).  
  * **Output:** Code context summary (saved to state, e.g., output\_key="code\_context").  
* **C. Implementation Planning Agent:**  
  * **Purpose:** Create a detailed, step-by-step plan for implementing the requirement, considering the code context.  
  * **Instructions:** Based on requirement\_details and code\_context, generate a plan outlining new functions/classes, modifications to existing code, file structures, and logic flow.  
  * **Tools:** None strictly required (relies on LLM planning). Could use a tool to format the plan into a specific structure (e.g., JSON, Markdown).  
  * **Input:** requirement\_details, code\_context (from state).  
  * **Output:** Detailed implementation plan (saved to state, e.g., output\_key="implementation\_plan").  
* **D. Code Generation Agent:**  
  * **Purpose:** Write the actual code based on the implementation\_plan.  
  * **Instructions:** Follow the implementation\_plan precisely, generate Python code (or other target language), adhere to best practices, and include necessary comments.  
  * **Tools:**  
    * write\_file(path: str, content: str, overwrite: bool \= False) \-\> bool: Custom FunctionTool to save generated code. Ensure path safety.  
    * read\_file (from Agent B): To read existing files for modification.  
    * (Optional) built\_in\_code\_execution (if using compatible Gemini model) or a custom, **securely sandboxed** FunctionTool for executing snippets for validation during generation.  
  * **Input:** implementation\_plan, code\_context (from state).  
  * **Output:** Path(s) to generated/modified files (saved to state, e.g., output\_key="generated\_code\_paths").  
* **E. Testing Agent:**  
  * **Purpose:** Generate and potentially execute unit tests for the code produced by the Code Generation Agent.  
  * **Instructions:** Based on requirement\_details and implementation\_plan, create relevant unit tests (e.g., using unittest or pytest conventions). Cover main functionality and edge cases.  
  * **Tools:**  
    * write\_file (from Agent D): To save test files.  
    * read\_file (from Agent B): To read the code being tested.  
    * (Optional) run\_tests(test\_paths: list\[str\]) \-\> dict: Custom FunctionTool wrapping a test runner (e.g., pytest) in a **secure sandbox**. Returns test results (pass/fail counts, errors).  
  * **Input:** implementation\_plan, generated\_code\_paths (from state).  
  * **Output:** Path(s) to test files, test results (saved to state, e.g., output\_key="test\_results").  
* **F. Refactoring Agent:**  
  * **Purpose:** Analyze the generated code and test results to suggest and apply improvements for quality, readability, performance, or adherence to standards.  
  * **Instructions:** Review the code at generated\_code\_paths, consider test\_results, and apply refactoring based on best practices or specific guidelines (which could be part of the initial requirement or agent config). If tests failed, attempt to fix the code.  
  * **Tools:**  
    * read\_file (from Agent B).  
    * write\_file (from Agent D).  
    * (Optional) run\_tests (from Agent E): To verify refactoring didn't break functionality.  
    * (Optional) Tools for linting/static analysis.  
  * **Input:** generated\_code\_paths, test\_results (from state).  
  * **Output:** Path(s) to refactored files (updated in state or new key, e.g., output\_key="refactored\_code\_paths").

**4\. Custom Tools Implementation:**

The custom FunctionTools (read\_file, write\_file, list\_directory, run\_tests) need careful implementation:

* **Docstrings:** Must be clear and detailed for the LLM agents to use them correctly.  
* **Error Handling:** Implement robust error handling (e.g., file not found, permissions issues).  
* **Security:**  
  * **Path Validation:** Sanitize and validate all file paths to prevent directory traversal attacks. Restrict access to intended project directories.  
  * **Sandboxing:** Any tool executing code (run\_tests, potentially code generation validation) MUST run in a strictly isolated, sandboxed environment with no network access and limited resources to prevent security risks. ADK's built\_in\_code\_execution or Vertex AI Code Interpreter Extension are safer alternatives if applicable.

**5\. Orchestration Logic:**

* **SequentialAgent:** Define the sub\_agents list in the order A \-\> B \-\> C \-\> D \-\> E \-\> F. Session state automatically carries data forward.  
* **CustomAgent (\_run\_async\_impl):** Provides more control.  
  \# Pseudocode within CustomAgent.\_run\_async\_impl(self, ctx)  
  yield from self.req\_analysis\_agent.run\_async(ctx)  
  \# Check state if codebase path exists  
  if ctx.session.state.get("codebase\_path"):  
      yield from self.code\_explore\_agent.run\_async(ctx)  
  yield from self.plan\_agent.run\_async(ctx)  
  yield from self.code\_gen\_agent.run\_async(ctx)  
  yield from self.test\_agent.run\_async(ctx)  
  \# Loop or conditional refactoring based on test\_results  
  if ctx.session.state.get("test\_results", {}).get("status") \!= "PASS":  
       yield from self.refactor\_agent.run\_async(ctx)  
       \# Optionally re-run tests  
       yield from self.test\_agent.run\_async(ctx) \# Update test\_results

**6\. Callbacks:**

Consider using callbacks for:

* **Logging:** before\_agent\_callback, after\_tool\_callback to log progress and tool usage.  
* **Guardrails:** before\_tool\_callback on write\_file or run\_tests for extra safety checks. before\_model\_callback on Code Generation/Refactoring agents to enforce coding standards or block certain patterns.

**7\. Evaluation:**

* Use ADK's evaluation framework (google.adk.evaluation).  
* Create .evalset.json files containing sample requirements (as query), expected code structures or key functions (reference or custom checks), and potentially expected tool usage (expected\_tool\_use).  
* Run evaluations using adk eval or pytest integration to systematically test the end-to-end system performance.

**8\. Iteration:**

The process, especially Testing and Refactoring, might need to be iterative. A CustomAgent orchestrator is better suited for implementing loops (e.g., Code \-\> Test \-\> Refactor \-\> Test until tests pass or max attempts reached).

This plan provides a solid foundation for building your requirement implementation agent system using ADK's modular components and features. Remember to prioritize security, especially when dealing with file system access and code execution.