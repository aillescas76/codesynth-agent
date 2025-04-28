# **Google Agent Development Kit (ADK): Technical Reference Sheet**

## **1\. Introduction to Google Agent Development Kit (ADK)**

### **Overview**

The Google Agent Development Kit (ADK) is an open-source framework implemented in Python, specifically engineered for the development, testing, and deployment of sophisticated AI agents. It provides a structured environment for building applications powered by Large Language Models (LLMs), with a notable emphasis on integration with Google's Artificial Intelligence (AI) ecosystem, including Gemini models and Vertex AI platform services.1

### **Core Philosophy**

The design of ADK is underpinned by several key philosophical tenets aimed at providing a robust and developer-friendly experience:

* **Modularity:** The framework is constructed from distinct, interchangeable components. Core elements such as Agents, Tools, Session Management services, and Runners are designed to be composable, allowing developers to assemble agentic applications by combining these building blocks as needed.1  
* **Flexibility:** ADK supports a wide array of agent architectures, ranging from simple single-agent setups to complex multi-agent systems. It accommodates various LLMs (not limited to Google's), diverse tool integrations (including custom functions, third-party libraries, and external APIs), and multiple deployment targets, from local development environments to scalable cloud platforms.1  
* **Google Ecosystem Integration:** A primary focus of ADK is to facilitate seamless integration with Google Cloud and AI services. This includes native support for Gemini models, deployment options via Vertex AI Agent Engine, Google Cloud Run, and Google Kubernetes Engine (GKE), and specialized tools for interacting with services like Vertex AI Search, Apigee API Hub, and Google Cloud Application Integration.1 This tight integration positions ADK as an effective layer for building agentic solutions specifically tailored to leverage Google's infrastructure and AI capabilities. The consistent highlighting of these integration points throughout the documentation suggests a strategic direction towards enabling developers within the Google Cloud ecosystem.1  
* **Developer Experience:** The framework prioritizes ease of use across different levels of complexity. Quickstart guides and tutorials enable rapid initial development, while advanced features like custom agents, callbacks, and detailed configuration options support the creation of sophisticated, production-grade applications.1

### **Documentation Structure Overview**

The official ADK documentation is logically organized to guide developers through the entire agent development lifecycle. Key sections include "Get Started" (installation, quickstart, tutorial), "Agents" (types and structures), "Tools" (extending capabilities), "Deploy" (running agents in production), "Sessions & Memory" (managing state), "Callbacks" (customizing execution), "Evaluate" (testing performance), and supplementary sections covering responsible AI, community resources, and a detailed API reference.1 This reference sheet synthesizes information primarily drawn from these sections.

## **2\. Getting Started with ADK**

This section details the initial steps required to set up the development environment and begin building agents with ADK.

### **Prerequisites**

Before installing ADK, ensure the following are available:

* A working Python installation. While specific version constraints might apply to certain components like Agent Engine (which requires Python 3.9-3.12 5), the core library generally relies on a modern Python 3 version.  
* The pip package installer, which typically comes bundled with Python installations.9  
* It is highly recommended to use a Python virtual environment manager like venv to isolate project dependencies and avoid conflicts with other Python projects.2

### **Installation**

The installation process involves setting up a virtual environment and installing the ADK package:

1. **Create Virtual Environment:** Open a terminal or command prompt and navigate to your desired project directory. Create a virtual environment (commonly named .venv) using:  
   Bash  
   python \-m venv.venv  
   9  
2. **Activate Virtual Environment:** Activate the newly created environment. The command varies by operating system and shell:  
   * macOS / Linux (bash/zsh): source.venv/bin/activate 2  
   * Windows CMD: .venv\\Scripts\\activate.bat 2  
   * Windows PowerShell: .venv\\Scripts\\Activate.ps1 2 Your terminal prompt should change to indicate the active environment.  
3. **Install ADK Package:** Install the google-adk package using pip:  
   Bash  
   pip install google-adk  
   2  
4. **Verify Installation (Optional):** Confirm the installation by checking the package details:  
   Bash  
   pip show google-adk  
   9

### **Quickstart Summary**

The ADK Quickstart guide provides a concise walkthrough for creating and running a basic agent.2

* **Goal:** Build a simple agent (weather\_time\_agent) capable of using two tools: one to get the weather and another to get the current time for a specific city (New York in the example).  
* **Project Structure:** The guide recommends a specific directory structure: a parent folder containing an agent module folder (e.g., multi\_tool\_agent/). This module folder must contain:  
  * \_\_init\_\_.py: Makes the directory importable as a Python package. Its content should typically be from. import agent to expose the agent definition.  
  * agent.py: Contains the core agent logic, including the agent definition and tool functions.  
  * .env: Stores environment variables, primarily API keys for LLM access.  
* **Agent Definition (agent.py):** An instance of the Agent class is created, specifying:  
  * name: A unique identifier (e.g., "weather\_time\_agent").  
  * model: The LLM to use (e.g., "gemini-2.0-flash").  
  * description: A brief summary of the agent's purpose.  
  * instruction: Natural language guidance for the LLM on how to behave and use tools.  
  * tools: A list containing the tool functions (get\_weather, get\_current\_time).  
* **Tool Definition:** The tools are implemented as standard Python functions with type hints (e.g., city: str) and descriptive docstrings. The docstrings are crucial as they inform the LLM about the tool's functionality.2  
* **Environment Setup (.env):** This file is critical for configuring access to external services. The Quickstart details two primary configurations:  
  * **Google AI Studio:** Requires setting GOOGLE\_GENAI\_USE\_VERTEXAI=FALSE and providing your GOOGLE\_API\_KEY.  
  * **Google Cloud Vertex AI:** Requires setting GOOGLE\_GENAI\_USE\_VERTEXAI=TRUE, GOOGLE\_CLOUD\_PROJECT (your project ID), and GOOGLE\_CLOUD\_LOCATION (the region). This path also requires having the gcloud CLI installed and authenticated, and the Vertex AI API enabled in the project. This reliance on environment variables for sensitive keys and cloud configuration underscores the framework's integration with external services and the importance of proper setup for functionality.2  
* **Running the Agent:** The Quickstart demonstrates three methods for interacting with the agent from the *parent directory*:  
  * adk web: Launches an interactive web-based Development UI (typically at http://localhost:8000). This UI allows selecting the agent module, chatting with the agent, and inspecting the underlying LLM calls, tool executions, and responses. This is often the most convenient method during development for testing and debugging.  
  * adk run \<agent\_module\_name\> (e.g., adk run multi\_tool\_agent): Runs the agent directly in the terminal, allowing for text-based interaction.  
  * adk api\_server: Starts a local FastAPI server hosting the agent's API endpoints. This allows testing interactions programmatically, for instance, using curl requests.  
* **Key Takeaway:** The Quickstart establishes the fundamental workflow: define the agent's core logic and tools in agent.py, configure necessary API keys and settings in .env, and use ADK's command-line tools (adk web, adk run, adk api\_server) to interact with and test the agent.2

### **Tutorial Deep Dive**

The ADK Tutorial provides a more comprehensive, step-by-step guide, progressively introducing advanced features and concepts by building an agent team.8

* **Goal:** Construct an intelligent agent team capable of handling greetings, farewells, and stateful weather lookups, incorporating multi-model support and safety guardrails.  
* **Step 0: Setup:** Installs necessary libraries (google-adk, litellm for multi-LLM support). Imports core ADK classes (Agent, LiteLlm, InMemorySessionService, Runner, types). Demonstrates setting API keys as environment variables for multiple providers (Google, OpenAI, Anthropic) and defining model name constants.  
* **Step 1: First Agent (Weather Lookup):**  
  * Defines a tool function (get\_weather) – again emphasizing the importance of the docstring for LLM understanding.  
  * Defines a basic Agent (weather\_agent\_v1) specifying its name, model, description, detailed instruction on behavior and tool use, and the get\_weather tool.  
  * Sets up an InMemorySessionService (for managing conversation history and state in memory) and a Runner (for orchestrating agent execution).  
  * Introduces an asynchronous helper function (call\_agent\_async) to send queries to the agent via the runner and print responses.  
  * Introduces core concepts: Tool, Agent, Instruction, SessionService, Runner, Events (representing steps in execution).  
* **Step 2: Multi-Model Flexibility (LiteLLM):**  
  * Demonstrates using the LiteLlm wrapper class to integrate models from different providers (OpenAI's GPT-4o, Anthropic's Claude Sonnet). The syntax model=LiteLlm(model="provider/model\_name") directs ADK to use the LiteLLM library for routing requests.  
  * Requires separate SessionService and Runner instances for each model-specific agent.  
* **Step 3: Building an Agent Team (Delegation):**  
  * Defines simple tools (say\_hello, say\_goodbye).  
  * Creates specialized sub-agents (greeting\_agent, farewell\_agent) with focused instructions, descriptions, and single tools.  
  * Updates the original weather agent to act as a root agent (weather\_agent\_v2) by adding the sub\_agents parameter (a list containing the greeting and farewell agents).  
  * Modifies the root agent's instruction to guide delegation to sub-agents based on user intent.  
  * Introduces concepts: Agent Team, Sub-Agent, Root Agent, Automatic Delegation (Auto Flow) – where the root agent's LLM uses sub-agent descriptions to decide when to transfer control.  
* **Step 4: Adding Memory and Personalization (Session State):**  
  * Creates a session with an initial state dictionary using InMemorySessionService (e.g., setting a preferred temperature unit).  
  * Defines a state-aware tool (get\_weather\_stateful) that accepts tool\_context: ToolContext as an argument. This context object provides access to the session state via tool\_context.state.  
  * Updates the root agent (weather\_agent\_v4\_stateful) to use the stateful tool.  
  * Introduces the output\_key parameter for the agent. Setting output\_key="last\_weather\_report" automatically saves the agent's final text response into the session state under that key, making it available for subsequent turns or tools.  
  * Introduces concepts: Session State (persistent dictionary per session), ToolContext (provides access to state within tools), output\_key (automatic state update).  
* **Step 5: Adding Safety (Input Guardrail via Callback):**  
  * Defines a before\_model\_callback function (block\_keyword\_guardrail). This function executes just before the agent calls the LLM. It inspects the user input (LlmRequest) and, if a specific keyword ("BLOCK") is found, it returns an LlmResponse object, effectively bypassing the LLM call and providing a predefined response.  
  * Updates the agent (weather\_agent\_v5\_model\_guardrail) by passing the callback function to the before\_model\_callback parameter.  
  * Introduces concepts: Callbacks (hooks into lifecycle), before\_model\_callback, LlmRequest (input to LLM), LlmResponse (output from LLM or callback override).  
* **Step 6: Adding Safety (Tool Argument Guardrail via Callback):**  
  * Defines a before\_tool\_callback function (block\_paris\_tool\_guardrail). This function executes just before a specific tool (get\_weather\_stateful) runs. It inspects the tool's arguments and, if the city is "Paris", it returns a custom dictionary, bypassing the actual tool execution and providing a predefined error message as the tool's result.  
  * Updates the agent (weather\_agent\_v6\_tool\_guardrail) to include both the model and tool callbacks.  
  * Introduces concepts: before\_tool\_callback, BaseTool (base class for tools).  
* **Key Takeaway:** The Tutorial serves as a practical demonstration of ADK's composability and power. It shows how to layer features – starting simple and adding multi-model support, delegation patterns (multi-agent systems), state management for personalization, and safety mechanisms using the callback system. This progression highlights that ADK is designed to support both elementary agent construction and the development of complex, feature-rich agentic applications.8 The contrast with the Quickstart emphasizes this scalability in functionality.2

## **3\. ADK Core Concepts**

The Agent Development Kit is built around several fundamental concepts that enable the creation and operation of AI agents 1:

* **Agents:** The central actors in the ADK framework. They are designed to perceive their environment (through user input or other triggers), reason about actions, and perform tasks to achieve specific goals. ADK supports different agent types (LLM, Workflow, Custom) to accommodate various levels of complexity and control.1  
* **Workflows:** Define the sequence or logic of execution within an agent or multi-agent system. Workflows can be dynamic and non-deterministic, driven by an LLM's reasoning (as in LlmAgent), or they can follow predefined, deterministic paths using specialized Workflow Agents (Sequential, Parallel, Loop).1  
* **Tools:** Mechanisms that extend an agent's capabilities beyond the inherent knowledge of its underlying LLM. Tools provide access to external information (e.g., web search, databases), allow interaction with other services (APIs), enable execution of code, or facilitate delegation to other agents.1  
* **Multi-Agent Systems:** A design pattern where complex problems are solved by coordinating multiple, specialized agents. Each agent focuses on a specific sub-task, and a root agent typically orchestrates the collaboration and delegation.1  
* **Sessions & Memory:** Essential for maintaining context and continuity in interactions. Sessions track the state of a single conversation, while memory mechanisms allow agents to retain and recall information across multiple turns or even sessions.1 (*Note: Detailed documentation on Session, State, and Memory 24 was inaccessible; insights are inferred from related components and examples.*)  
* **Callbacks:** Functions that allow developers to hook into specific points in the agent's execution lifecycle. They enable observation (logging), customization (modifying requests/responses), control (implementing guardrails, bypassing steps), and integration with external systems.1  
* **Deployment:** The process of making agents accessible and operational in various environments. ADK provides options for local execution, serverless deployment (Cloud Run), container orchestration (GKE), and a managed service (Vertex AI Agent Engine).1  
* **Evaluation:** The systematic assessment of agent performance. ADK includes tools and methodologies for evaluating aspects like response quality, tool usage accuracy, and adherence to expected behavior.1  
* **Responsible AI:** A guiding principle focused on building agents that are safe, secure, ethical, and trustworthy. ADK encourages implementing responsible AI patterns, including guardrails and safety checks, throughout the development process.1

## **4\. Understanding ADK Agents**

ADK offers several types of agents, each suited for different purposes and control paradigms.

### **LLM Agents (LlmAgent/Agent)**

The LlmAgent (often aliased simply as Agent) is the cornerstone for building agents that leverage the reasoning and natural language capabilities of Large Language Models.13

* **Purpose:** To act as the primary "thinking" component of an application. It uses an LLM to understand user input, make decisions, interact with tools, generate responses, and potentially delegate tasks to other agents.  
* **Functionality:** LlmAgent operates non-deterministically, meaning its behavior is dynamically determined by the LLM based on the provided instructions, the current conversation context, and the user's input. Key functions include:  
  * *Instruction Interpretation:* Following guidance provided in the instruction parameter regarding role, goals, constraints, and tool usage.  
  * *Reasoning and Decision Making:* Determining the best course of action, such as selecting a tool, formulating a direct response, or transferring control to a sub-agent.  
  * *Response Generation:* Creating natural language outputs.  
  * *Tool Interaction:* Utilizing available tools (functions, BaseTool instances, other agents) to gather information or perform actions.  
  * *Context Management:* Optionally incorporating conversation history (contents) to maintain coherent interactions (controlled by include\_contents).  
  * *Structured Data Handling:* Enforcing specific JSON input and output formats using Pydantic models defined in input\_schema and output\_schema. However, using output\_schema comes with a significant trade-off: it disables the agent's ability to use tools or delegate tasks.13 This limitation arises because enforcing a strict output schema prevents the LLM from generating the necessary function call structures or delegation commands, forcing developers to choose between guaranteed output format and the full spectrum of agentic capabilities.  
* **Technical Deep Dive:** The LlmAgent class is configured primarily through its constructor parameters.  
  **Table: LlmAgent Key Parameters**

| Parameter | Type | Description | Required/Optional | Key Use Case | Reference |
| :---- | :---- | :---- | :---- | :---- | :---- |
| model | str | Identifier for the underlying LLM (e.g., "gemini-2.0-flash"). | Required | Selecting the core language processing engine. | 13 |
| name | str | Unique identifier for the agent (cannot be "user"). | Required | Identifying the agent internally, especially in teams. | 13 |
| instruction | str \\ | Callable\[, str\] | **Critical:** Defines agent behavior, personality, constraints, tool usage guidance. | Optional | Controlling agent persona and task execution. |
| description | str | Concise summary of agent capabilities. **Crucial for delegation** in multi-agent systems (used by other LLM agents to decide routing). | Optional | Enabling automatic delegation (Auto Flow). | 13 |
| tools | List\] | List of tools (Python functions, BaseTool instances, AgentTool instances). | Optional | Extending agent capabilities. | 13 |
| generate\_content\_config | types.GenerateContentConfig | Fine-tune LLM generation parameters (temperature, max tokens, etc.). | Optional | Controlling LLM response characteristics. | 13 |
| input\_schema | Type | Pydantic model defining expected structured JSON input. | Optional | Enforcing structured input format. | 13 |
| output\_schema | Type | Pydantic model defining desired structured JSON output. **Disables tool use and delegation.** | Optional | Enforcing structured output format. | 13 |
| output\_key | str | Key under which the final text response is saved to session state (ctx.session.state). | Optional | Passing results to subsequent steps/agents. | 8 |
| include\_contents | Literal\['default', 'none'\] | Controls whether conversation history is sent to the LLM ('default' sends relevant history). | Optional | Managing context window and coherence. | 13 |
| planner | BasePlanner | Enables multi-step reasoning/planning before execution. | Optional | Implementing more complex reasoning patterns. | 13 |
| code\_executor | BaseCodeExecutor | Allows execution of code blocks (e.g., Python) found in LLM responses. | Optional | Enabling code execution capabilities. | 13 |
| callbacks | \`List\[Callable \\ | Callback\]\` | List of callback functions to hook into the agent lifecycle. | Optional | Implementing logging, guardrails, customization. |

The configuration of \`LlmAgent\` highlights the central role of natural language prompts. The \`instruction\` parameter dictates the agent's fundamental behavior and how it approaches tasks, while the \`description\` is essential for enabling effective delegation in multi-agent scenarios where one LLM agent needs to decide whether to pass control to another.\[13\] Crafting these prompts effectively is therefore a critical aspect of developing capable \`LlmAgent\` instances, particularly within teams.\[8, 13\]

### **Workflow Agents (Deterministic Control Flow)**

Workflow agents provide deterministic control over the execution flow of sub-agents, offering predictable patterns in contrast to the non-deterministic nature of LlmAgent.15 They orchestrate *how* and *when* sub-agents run based on predefined logic, although the sub-agents themselves can still be intelligent LlmAgent instances. This allows for the combination of structured process control with flexible, LLM-powered task execution.

* **Sequential Agents (SequentialAgent)** 14  
  * **Purpose:** Executes a list of sub-agents one after another in a predefined order. Ideal for tasks that naturally break down into sequential steps.  
  * **Functionality:** The SequentialAgent iterates through its sub\_agents list, invoking the run\_async() method of each sub-agent in turn. Crucially, it relies on the session state mechanism for passing data between steps. Sub-agents typically use the output\_key parameter (available in LlmAgent) to write their results to the session state (ctx.session.state), making this data available for subsequent sub-agents in the sequence to consume.  
  * **Technical Details:** The primary configuration involves providing the list of sub\_agents (instances of BaseAgent derivatives) in the desired execution order to the SequentialAgent constructor. An optional name can be provided for identification.  
  * **Usage Example:** A common use case is a pipeline, such as code generation: 1\) A code\_writer\_agent generates code and saves it to state via output\_key="generated\_code". 2\) A code\_reviewer\_agent reads "generated\_code" from state, performs a review, and saves feedback via output\_key="review\_comments". 3\) A code\_refactorer\_agent reads both "generated\_code" and "review\_comments" from state, refactors the code, and saves the result via output\_key="refactored\_code". This sequence is enforced by placing these agents in order within the SequentialAgent's sub\_agents list.  
* **Loop Agents (LoopAgent)** 16  
  * **Purpose:** Executes a list of sub-agents repeatedly until a specific termination condition is satisfied. Suitable for iterative processes like refinement or polling.  
  * **Functionality:** The LoopAgent executes its sub\_agents list sequentially within each iteration of the loop. A mechanism to terminate the loop is essential to prevent infinite execution.  
  * **Termination:** Termination can be controlled in two main ways:  
    1. **max\_iterations:** An optional integer parameter in the LoopAgent constructor sets a hard limit on the number of loop cycles.  
    2. **Sub-agent Signal:** One or more sub-agents within the loop can be designed to evaluate a condition and signal termination (e.g., by setting a specific flag in the session state, raising a custom event, or returning a specific value recognized by custom logic, although the exact signaling mechanism isn't fully detailed in the snippet).  
  * **Technical Details:** Configured with a name, the list of sub\_agents to execute in each iteration, and optionally max\_iterations. Like SequentialAgent, it often relies on session state for passing information between sub-agents within an iteration or across iterations.  
  * **Usage Example:** An iterative document improvement workflow: 1\) A WriterAgent writes or refines a document based on state (current\_document, criticism), saving the result via output\_key="current\_document". 2\) A CriticAgent reviews the current\_document from state and saves feedback via output\_key="criticism". The LoopAgent repeats this Writer-Critic sequence for a set number of max\_iterations or until a quality threshold (checked by a sub-agent) is met.  
* **Parallel Agents (ParallelAgent)** 17  
  * **Purpose:** Executes multiple sub-agents concurrently, aiming to reduce overall execution time for tasks that can run independently.  
  * **Functionality:** When invoked, the ParallelAgent initiates the execution of all agents in its sub\_agents list simultaneously. Each sub-agent runs in an isolated branch, meaning there is no automatic sharing of conversation history or session state between them during their parallel execution. The ParallelAgent collects the results from each branch upon completion; the order of completion may not be deterministic.  
  * **State Management:** Due to the independent execution branches, sharing information between parallel sub-agents requires explicit implementation. Strategies include using a shared InvocationContext object (requiring careful handling of concurrent access), leveraging external state management systems (like databases or message queues), or implementing logic to consolidate results after all parallel branches have finished.  
  * **Technical Details:** Configured with a name and the list of sub\_agents to run in parallel.  
  * **Usage Example:** Performing web research on multiple distinct topics simultaneously. Three separate LlmAgent instances, each tasked with researching a different topic and equipped with a search tool, can be placed in a ParallelAgent. The ParallelAgent triggers all three researchers concurrently, significantly speeding up the overall research process compared to running them sequentially.

The availability of these three workflow agents (SequentialAgent, LoopAgent, ParallelAgent) provides developers with fundamental control structures analogous to those found in traditional programming paradigms.14 They enable the construction of complex agent behaviors by composing simpler agents within predictable, deterministic flows. Effective utilization, particularly for SequentialAgent and LoopAgent, often hinges on managing the flow of information between steps using the session state (ctx.session.state) and the output\_key parameter within sub-agents.14 ParallelAgent, while offering performance benefits, introduces complexity regarding inter-agent communication due to its isolated execution model.17

### **Custom Agents (BaseAgent)**

For scenarios where the required orchestration logic does not fit the predefined patterns of sequential, loop, or parallel execution, ADK allows the creation of Custom Agents.18

* **Purpose:** To implement arbitrary, bespoke control flow and orchestration logic involving sub-agents and state management.  
* **Implementation:** Requires inheriting from the google.adk.agents.BaseAgent class and implementing the \_run\_async\_impl asynchronous generator method.  
  * **Signature:** async def \_run\_async\_impl(self, ctx: InvocationContext) \-\> AsyncGenerator\[Event, None\]:  
  * **Logic:** This method contains the custom workflow. Key operations within this method include:  
    * *Calling Sub-Agents:* Invoke the run\_async(ctx) method of sub-agent instances (typically stored as instance attributes like self.my\_sub\_agent). The events generated by the sub-agent must be yielded (yield event) to propagate them up the execution chain.  
    * *Managing State:* Read from and write to the session state dictionary via ctx.session.state. This is essential for passing data between custom steps or making decisions based on prior results.  
    * *Implementing Control Flow:* Utilize standard Python control structures (if/elif/else, for/while loops, try/except) to define conditional execution paths, iterations, and error handling involving sub-agents.  
* **Initialization (\_\_init\_\_)**: The custom agent's constructor should accept instances of the sub-agents it orchestrates and store them (e.g., self.story\_generator \= story\_generator\_instance). Importantly, the list of top-level sub-agents directly managed by the custom agent should be passed to the super().\_\_init\_\_(sub\_agents=...) call. This registration informs the ADK framework about the agent hierarchy.  
* **Usage Example:** The StoryFlowAgent example illustrates a complex content generation workflow:  
  1. Generate initial story (story\_generator sub-agent).  
  2. Run an iterative critique-revision cycle using a LoopAgent (which internally manages critic and reviser sub-agents).  
  3. Perform post-processing (grammar/tone check) using a SequentialAgent.  
  4. **Custom Logic:** Check the tone result stored in ctx.session.state. If the tone is negative, conditionally call the story\_generator *again* to regenerate the story. This conditional step based on intermediate results is logic that doesn't fit neatly into the standard workflow agents, necessitating a CustomAgent.  
* Custom Agents offer maximum flexibility but shift the responsibility of managing the detailed orchestration logic, sub-agent invocation, state transitions, and event propagation entirely to the developer. They represent the most powerful but also most complex way to define agent behavior in ADK, suitable for workflows with unique conditional or iterative patterns not covered by the standard Sequential, Loop, or Parallel agents.18

### **Multi-Agent Systems**

ADK supports the creation of multi-agent systems, where applications are built by composing multiple specialized agents that collaborate to achieve a larger goal.1 (*Note: Specific documentation 27 was inaccessible; details are based on related components and the Tutorial example.*)

* **Concept:** Instead of a single monolithic agent, tasks are broken down and assigned to agents with specific expertise or tools.  
* **Components:**  
  * **Root Agent:** Typically an LlmAgent that receives the initial user request and acts as the orchestrator, deciding which sub-agent is best suited for the current task or sub-task.8  
  * **Sub-Agents:** These are the specialized workers. They can be LlmAgent instances with specific instructions and tools, WorkflowAgent instances managing structured sub-processes, or even CustomAgent instances with unique logic.8  
* **Delegation (Auto Flow):** ADK facilitates delegation primarily through the "Auto Flow" mechanism when using an LlmAgent as the root agent.8 The root agent's LLM analyzes the user query and compares it against the description parameter provided for each sub-agent listed in its sub\_agents parameter.13 Based on this comparison and the root agent's own instruction (which should guide the delegation process), the LLM decides whether to handle the request itself or transfer control to the most appropriate sub-agent.  
* **Configuration:** Building a multi-agent system involves:  
  1. Defining the specialized sub-agents.  
  2. Defining the root agent (often an LlmAgent).  
  3. Passing the list of sub-agent instances to the root agent's sub\_agents parameter during initialization.8  
  4. Carefully crafting the instruction for the root agent to encourage appropriate delegation and the description for each sub-agent to accurately reflect its capabilities for the root agent's LLM to understand.8  
* The effectiveness of the Auto Flow delegation mechanism heavily depends on the LLM's ability to accurately interpret the sub-agents' description fields and follow the delegation logic outlined in the root agent's instruction.8 This places significant importance on prompt engineering for both the root agent's instructions and the sub-agents' descriptions to ensure reliable and accurate task routing within the multi-agent system.

**Table: Comparison of ADK Agent Types**

| Feature | LLM Agent (LlmAgent) | Sequential Agent (SequentialAgent) | Loop Agent (LoopAgent) | Parallel Agent (ParallelAgent) | Custom Agent (BaseAgent) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Core Class** | google.adk.agents.LlmAgent | google.adk.agents.SequentialAgent | google.adk.agents.LoopAgent | google.adk.agents.ParallelAgent | Subclass of google.adk.agents.BaseAgent |
| **Behavior** | Non-deterministic (LLM-driven) | Deterministic | Deterministic | Deterministic | Arbitrary (Developer-defined) |
| **Control Flow** | Dynamic (Reasoning, Tool Use, Delegation) | Fixed Sequence | Iteration until Condition/Max Iter | Concurrent Execution | Custom Logic via \_run\_async\_impl |
| **Primary Use Case** | Core reasoning, NLU, tool use, delegation | Multi-step ordered processes | Iterative refinement, polling | Speeding up independent tasks | Bespoke workflows, complex conditional logic |
| **Key Config** | model, instruction, description, tools, sub\_agents | sub\_agents (ordered list) | sub\_agents, max\_iterations | sub\_agents | Override \_run\_async\_impl, manage state/sub-agents |
| **References** | 8 | 14 | 15 | 15 | 18 |

## **5\. Leveraging ADK Tools**

Tools are essential components in ADK, extending the capabilities of agents beyond their core LLM knowledge. ADK provides multiple ways to define, integrate, and manage tools.1

### **Function Tools**

Function tools allow developers to integrate custom Python code as capabilities for agents.19

* **Standard (FunctionTool):**  
  * **Purpose:** The simplest way to wrap a synchronous Python function as a tool.  
  * **Creation:** Pass the Python function object directly into the tools list when initializing an Agent (e.g., Agent(tools=\[my\_custom\_function\])). ADK automatically wraps it.  
  * **Docstrings:** The function's docstring is critical. It serves as the description provided to the LLM, explaining the tool's purpose, parameters, and expected return values. Clear, comprehensive docstrings are vital for the LLM to understand when and how to use the tool correctly.  
  * **Parameters & Return:** Function parameters should use standard JSON-serializable types (str, int, float, bool, list, dict). Default parameter values should generally be avoided as the LLM may not interpret them correctly. The preferred return type is a Python dictionary, allowing structured output (e.g., including a "status": "success" key). If a non-dictionary type is returned, ADK wraps it automatically in {"result":...}.  
* **Long Running (LongRunningFunctionTool):**  
  * **Purpose:** Designed for tasks that may take considerable time to complete and should not block the agent's main execution thread. Allows for intermediate progress updates.  
  * **Creation:** The underlying Python function must be implemented as a *generator* function (using the yield keyword). This generator function is then wrapped using the LongRunningFunctionTool class: long\_tool \= LongRunningFunctionTool(func=my\_generator\_func). The resulting long\_tool instance is added to the agent's tools list.  
  * **Generator Logic:** The generator function should yield intermediate status updates (typically dictionaries containing keys like "status": "pending", "progress": 50, "message": "..."). Each yielded value is sent back to the LLM as a FunctionResponse event. When the task is complete, the generator uses return to provide the final result, which is also sent as the final FunctionResponse. The docstring of the generator function serves as the tool description.  
* **Agent-as-a-Tool (AgentTool):**  
  * **Purpose:** Enables one agent to invoke another agent as if it were a standard tool, facilitating delegation patterns.  
  * **Creation:** An existing Agent instance (the one to be called) is wrapped using the AgentTool class: agent\_tool \= AgentTool(agent=sub\_agent\_instance). This agent\_tool is then included in the calling agent's tools list.  
  * **Configuration:** The description attribute of the *wrapped agent* serves as the description for the AgentTool presented to the calling agent's LLM. An optional skip\_summarization: bool parameter in AgentTool can bypass LLM-based summarization of the sub-agent's response if it's already well-formatted.

This variety of function tool mechanisms (FunctionTool, LongRunningFunctionTool, AgentTool) provides developers with flexible options for integrating diverse computational logic and delegation patterns into their agents, accommodating simple synchronous tasks, long-running asynchronous operations, and inter-agent communication.19

### **Built-in Tools**

ADK offers several pre-built tools that provide common functionalities, often leveraging Google services. A key limitation currently is that only one built-in tool can be used per root agent or single agent; they cannot be added to sub-agents.3

* **Google Search (google\_search):**  
  * **Purpose:** Enables the agent to perform web searches using Google Search to retrieve up-to-date information from the internet.  
  * **Usage:** Import google\_search from google.adk.tools and add an instance to the agent's tools list.  
  * **Compatibility:** Requires Gemini 2 models.  
* **Code Execution (built\_in\_code\_execution):**  
  * **Purpose:** Allows the agent to execute code snippets (specifically Python when used with Gemini 2 models). Useful for calculations, data transformations, or running simple scripts.  
  * **Usage:** Import built\_in\_code\_execution from google.adk.tools and add an instance to the LlmAgent's tools list.  
  * **Compatibility:** Requires Gemini 2 models.  
* **Vertex AI Search (VertexAiSearchTool):**  
  * **Purpose:** Enables searching over private data stored and indexed within a configured Google Cloud Vertex AI Search data store (e.g., internal documents, knowledge bases).  
  * **Usage:** Import VertexAiSearchTool from google.adk.tools. Instantiate it, providing the specific data\_store\_id (in the format projects/\<PROJECT\_ID\>/locations/\<LOCATION\>/collections/default\_collection/dataStores/\<DATASTORE\_ID\>). Add the tool instance to the LlmAgent's tools list.  
  * **Compatibility:** Requires a Gemini model and a pre-configured Vertex AI Search data store.

These built-in tools provide convenient access to powerful capabilities, particularly those integrated with the Google ecosystem.3 However, the restriction of allowing only one per root agent necessitates careful architectural planning if an agent requires multiple of these core functionalities (e.g., both web search and code execution). In such cases, developers might need to implement equivalent functionality using Function Tools or explore other integration methods.

### **Third-Party Tool Integration**

ADK facilitates the integration of tools from other popular agent frameworks, promoting interoperability and code reuse.20

* **LangChain (LangchainTool):**  
  * **Purpose:** Allows using tools developed within the LangChain ecosystem.  
  * **Setup:** Requires installing relevant LangChain packages (e.g., langchain\_community, tavily-python for the Tavily search tool) and setting any required environment variables (e.g., TAVILY\_API\_KEY).  
  * **Wrapping:** Import LangchainTool from google.adk.tools.langchain\_tool and the specific LangChain tool class (e.g., TavilySearchResults). Instantiate the LangChain tool with its parameters. Wrap the instance using adk\_tool \= LangchainTool(tool=langchain\_tool\_instance). Add adk\_tool to the ADK agent's tools list. LangchainTool typically infers the name and description from the underlying LangChain tool object.  
* **CrewAI (CrewaiTool):**  
  * **Purpose:** Allows using tools developed within the CrewAI library.  
  * **Setup:** Requires installing relevant CrewAI packages (e.g., crewai-tools for SerperDevTool) and setting any required environment variables (e.g., SERPER\_API\_KEY).  
  * **Wrapping:** Import CrewaiTool from google.adk.tools.crewai\_tool and the specific CrewAI tool class (e.g., SerperDevTool). Instantiate the CrewAI tool. Wrap the instance using adk\_tool \= CrewaiTool(name="UniqueToolName", description="Tool description for LLM", tool=crewai\_tool\_instance). **Crucially, the name and description parameters must be explicitly provided to the CrewaiTool wrapper**, as ADK needs this information to present the tool effectively to its LLM. Add adk\_tool to the ADK agent's tools list.

The provision of dedicated wrappers (LangchainTool, CrewaiTool) demonstrates ADK's commitment to interoperability, enabling developers to leverage existing tool investments from other frameworks.20 The slight difference in wrapping CrewAI tools (requiring explicit name/description) compared to LangChain tools highlights the need for developers to be mindful of potential variations when integrating tools from different sources.

### **Google Cloud Tools**

ADK offers specialized toolsets designed to streamline integration with specific Google Cloud services, abstracting away much of the underlying connection and authentication complexity.4

* **Apigee API Hub (ApiHubToolset):**  
  * **Purpose:** Integrates with APIs documented and managed within an Apigee API Hub instance. Automatically creates tools based on the API's OpenAPI specification found in the Hub.  
  * **Usage:** Requires prerequisites like gcloud CLI, appropriate IAM permissions (roles/apihub.viewer), and an API Hub instance. Obtain an access token (gcloud auth print-access-token). Instantiate APIHubToolset, providing the API Hub resource name, access token, and optional authentication details for the target API (API Key, Bearer, Service Account, OIDC). Use toolset.get\_tools() to retrieve the generated tools and add them to the agent.  
* **Application Integration (ApplicationIntegrationToolset):**  
  * **Purpose:** Connects agents to enterprise applications via Google Cloud Application Integration, supporting both pre-built Integration Connectors (e.g., Salesforce, SAP) and custom integration workflows.  
  * **Usage (Connectors):** Requires an existing Integration Connector and provisioned Application Integration. Use the "Connection Tool" template in Application Integration to create and publish an integration named ExecuteConnection. Instantiate ApplicationIntegrationToolset in ADK, providing GCP project details, connection name/location, and supported operations. Add the resulting tool to the agent.  
  * **Usage (Workflows):** Requires an existing Application Integration workflow. Instantiate ApplicationIntegrationToolset, providing GCP project details, integration name/location, and the trigger ID. Add the resulting tool to the agent.  
* **Toolbox for Databases (ToolboxTool):**  
  * **Purpose:** Integrates with a deployed MCP Toolbox server, which provides an enterprise-grade layer for database interactions (handling connection pooling, authentication, etc.).  
  * **Usage:** Requires deploying and configuring the Toolbox server separately. Install the toolbox-langchain package. Instantiate ToolboxTool in ADK, providing the URL of the running Toolbox server and optionally specifying a toolset\_name or tool\_name to load specific tools defined in Toolbox. Add the loaded tool(s) to the agent.

These Google Cloud toolsets significantly simplify the process of connecting ADK agents to complex enterprise systems and Google Cloud services by providing higher-level abstractions compared to manual API integration.4

### **OpenAPI Tools (OpenAPIToolset)**

ADK provides a powerful mechanism to automatically generate tools directly from OpenAPI specifications (v3.x), drastically simplifying the integration of REST APIs.21

* **Purpose:** To eliminate the manual effort of creating individual function tools for each endpoint of a REST API by leveraging its standardized OpenAPI definition.  
* **How it Works:**  
  1. **Initialization:** The OpenAPIToolset class is initialized with the OpenAPI specification provided as a Python dictionary, a JSON string, or a YAML string.  
  2. **Parsing & Discovery:** The toolset parses the specification, resolves internal references ($ref), and identifies all valid HTTP operations (GET, POST, PUT, DELETE, etc.) defined within the paths section.  
  3. **Tool Generation (RestApiTool):** For each discovered operation, an instance of RestApiTool is automatically created.  
     * *Naming:* The tool's name is derived from the operationId in the spec (converted to snake\_case, max 60 chars) or generated from the method and path if operationId is absent.  
     * *Description:* The tool's description (used by the LLM) is taken from the operation's summary or description field in the spec.  
     * *Functionality:* Each RestApiTool encapsulates the necessary details (HTTP method, path, server URL, parameters, request body schema) from the spec. It dynamically generates a FunctionDeclaration to inform the LLM how to call it. When invoked by the agent, it constructs the HTTP request using arguments provided by the LLM, handles authentication (if configured globally on the toolset), executes the API call using the requests library, and returns the response.  
  4. **Authentication:** Global authentication schemes (e.g., API Key, OAuth Bearer token) can be configured when initializing OpenAPIToolset (using auth\_scheme and auth\_credential parameters) and are automatically applied to all generated RestApiTool instances.  
* **Usage Workflow:**  
  1. Obtain the OpenAPI specification document.  
  2. Instantiate OpenAPIToolset, passing the spec content and optional authentication details.  
  3. Retrieve the list of generated RestApiTool instances using toolset.get\_tools().  
  4. Add these tools to the tools list of an LlmAgent.  
  5. Update the agent's instruction to inform it about the newly available API capabilities (using the generated tool names).  
  6. Run the agent. The LLM will identify when to use an API and generate a function call targeting the appropriate RestApiTool.

The OpenAPIToolset significantly accelerates REST API integration by automating tool creation from a standard definition, reducing boilerplate code, ensuring consistency with the API contract, and simplifying the process for developers.21

### **Tool Authentication**

ADK incorporates a structured system for handling authentication required by tools interacting with protected resources.22

* **Core Concepts:**  
  * **AuthScheme:** Defines the authentication method required by the target API (e.g., APIKey, HTTPBearer, OAuth2, OpenIdConnectWithConfig), mirroring OpenAPI 3.0 standards.  
  * **AuthCredential:** Holds the initial information needed to *initiate* the authentication process (e.g., the API key itself, OAuth Client ID/Secret, Service Account JSON key). It also specifies the auth\_type.  
* **General Flow:**  
  1. **Configuration:** When defining a tool that requires authentication (e.g., RestApiTool, OpenAPIToolset, custom FunctionTool), the developer provides the necessary AuthScheme and initial AuthCredential.  
  2. **Automatic Exchange:** ADK attempts to automatically exchange the initial credential for a usable one (like an access token) when the tool needs to make an API call.  
  3. **Interactive Flow (OAuth/OIDC):** If user interaction is required (e.g., consent screen), ADK triggers a specific flow involving the **Agent Client** (the application interacting with the ADK agent, like a web backend or CLI).  
* **Handling Interactive Flows (Agent Client Responsibility):**  
  1. The Agent Client initiates the agent interaction (e.g., runner.run\_async).  
  2. It monitors events yielded by the runner.  
  3. If a tool requires user auth, ADK yields an event indicating a call to the special adk\_request\_credential function, containing an AuthConfig object with an auth\_uri (authorization URL) and an auth\_request\_event\_id.  
  4. The Agent Client **must** append its pre-registered redirect\_uri as a query parameter to the auth\_uri.  
  5. The client redirects the user to this combined URL for login and consent.  
  6. After authorization, the provider redirects the user back to the client's redirect\_uri with an authorization code.  
  7. The client captures the full callback URL.  
  8. The client sends a FunctionResponse back to the ADK runner via runner.run\_async. This response targets the adk\_request\_credential function (using the auth\_request\_event\_id), and its payload includes the captured callback URL and the client's redirect\_uri within an updated AuthConfig object.  
  9. ADK receives this response, automatically performs the backend token exchange with the provider using the authorization code, obtains the necessary tokens, and retries the original tool call, now with valid credentials.  
* **Building Custom Authenticated Tools (FunctionTool):**  
  1. The tool function must accept tool\_context: ToolContext as an argument.  
  2. **Logic:**  
     * Check for cached, valid credentials in tool\_context.state. If present, use them.  
     * If no valid cache, check if an auth response was just received from the client using tool\_context.get\_auth\_response(). If so, use the credentials from it.  
     * If neither cache nor response exists, initiate the flow: Define AuthScheme and AuthCredential, then call tool\_context.request\_credential() with an AuthConfig. This pauses execution and signals ADK to request user interaction via the Agent Client. The tool returns a pending status.  
     * Once credentials (tokens) are obtained (either from cache or via the flow handled by ADK/Client), **cache them** securely in tool\_context.state for reuse within the session.  
     * Make the authenticated API call using the obtained credentials. Handle potential 401/403 errors (e.g., expired tokens) by clearing the cache and potentially re-initiating auth.  
     * Return the tool's result.  
* **Security Considerations:** Storing sensitive, long-lived credentials like refresh tokens directly in session state (especially persistent state like databases) is discouraged without encryption. The recommended practice for production is to use dedicated secret management systems (e.g., Google Cloud Secret Manager, HashiCorp Vault). The session state might store short-lived access tokens or secure references, fetching secrets as needed.  
  ADK's authentication framework provides a robust separation of concerns, managing the complexities of various schemes while defining clear responsibilities for tool configuration (developer), interactive flows (agent client), and custom logic implementation (ToolContext for FunctionTool).22

**Table: Overview of ADK Tool Categories**

| Category | Key Class(es) | Purpose | Creation Method | Example Use Case | References |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Function** | FunctionTool, LongRunningFunctionTool, AgentTool | Integrate custom Python logic, handle long tasks, delegate | Pass function; Wrap generator with LongRunningFunctionTool; Wrap agent with AgentTool | Custom calculation; Async job; Task delegation | 19 |
| **Built-in** | google\_search, built\_in\_code\_execution, VertexAiSearchTool | Provide common capabilities (search, code exec) | Import and instantiate tool class | Web search; Run Python; Search private data | 3 |
| **Third-Party** | LangchainTool, CrewaiTool | Integrate tools from LangChain/CrewAI ecosystems | Wrap external tool instance with ADK wrapper class | Use Tavily search; Use SerperDevTool | 20 |
| **Google Cloud** | ApiHubToolset, ApplicationIntegrationToolset, ToolboxTool | Simplify integration with specific GCP services | Instantiate toolset/tool class with GCP resource details | Call Apigee API; Trigger App Integration; Query DB via Toolbox | 4 |
| **OpenAPI** | OpenAPIToolset, RestApiTool | Auto-generate tools from OpenAPI specifications | Instantiate OpenAPIToolset with OpenAPI spec | Integrate any REST API with OpenAPI spec | 21 |

## **6\. Managing Sessions, State, and Memory**

Maintaining context and information across interactions is crucial for effective agent behavior. ADK provides mechanisms for managing sessions, state, and potentially more complex forms of memory. 1

### **Session Management**

* **Purpose:** A session typically represents a single, stateful conversation or interaction sequence between a user and an agent or application.1 It serves as a container for the conversation history (events) and associated state data.  
* **Lifecycle:** Sessions are created at the start of an interaction, updated as the conversation progresses with new messages and state changes, retrieved for context, and potentially deleted when no longer needed. This lifecycle is managed by a Session Service.23  
* **Management (SessionService):** ADK defines a BaseSessionService interface for managing sessions. Concrete implementations handle the actual storage and retrieval:  
  * InMemorySessionService: Stores session data (history, state) in memory. This is simple for development and testing but is ephemeral – data is lost when the application restarts.8  
  * DatabaseSessionService: Implies persistence of session data to a database (details unspecified).23  
  * VertexAiSessionService: Likely leverages Vertex AI infrastructure for persistent and potentially managed session storage.23 The choice of SessionService determines how session data is persisted and scaled. The Runner component typically interacts with the configured SessionService to manage sessions during agent execution.8

### **State Handling**

Session state provides a mechanism for agents to store, retrieve, and share data within the context of a single session.

* **Purpose:** Enables agents to remember information across multiple turns in a conversation (e.g., user preferences) and allows different components (sub-agents in a workflow, tools) to pass data to each other.8  
* **Structure & Access:** Session state is represented as a simple Python dictionary (dict). It can be accessed in several ways:  
  * Within Custom Agents (\_run\_async\_impl): Via the InvocationContext object, specifically ctx.session.state.18  
  * Within Function Tools: Via the ToolContext object, specifically tool\_context.state.8  
* **Update:** State can be updated by directly modifying the state dictionary (e.g., ctx.session.state\["user\_preference"\] \= "Fahrenheit"). Additionally, LlmAgent provides the output\_key parameter as a convenient way to automatically save the agent's final text response to a specified key in the state dictionary upon completion.8  
* **Persistence:** The persistence of the state dictionary is determined by the configured SessionService. InMemorySessionService provides no persistence beyond the application's runtime, while database or Vertex AI-based services would offer persistent storage.8  
  Session state (ctx.session.state) emerges as the fundamental, built-in mechanism for short-term memory and data exchange within ADK workflows. Its use is demonstrated extensively in examples for personalization, passing results between sequential steps, managing iterative refinements in loops, and enabling conditional logic in custom agents.8

### **Agent Memory**

While session state handles immediate context, "memory" in agentic systems often refers to broader capabilities for information retention and retrieval.

* **Concept:** Likely encompasses mechanisms beyond the simple key-value session state dictionary. This could include summarizing past interactions, storing information long-term across sessions, or integrating external knowledge sources via techniques like Retrieval-Augmented Generation (RAG).1  
* **Distinction from State:** Session state appears focused on the immediate context and data passing within a single session or workflow execution.8 Memory likely involves more complex processing, longer-term storage, or integration with dedicated knowledge retrieval systems. The include\_contents parameter in LlmAgent, which controls sending conversation history to the LLM, represents a basic form of memory but is distinct from structured state or external retrieval.13  
* **Mechanisms:** The ADK API Reference lists BaseMemoryService, InMemoryMemoryService, and notably VertexAiRagMemoryService.23 The existence of a specific RAG memory service strongly suggests built-in support for retrieval-augmented generation, likely leveraging Vertex AI capabilities. This implies that more advanced memory functionalities beyond basic history and session state are available, potentially requiring configuration of these dedicated memory services.  
  While session state is the primary mechanism for intra-session context, ADK appears to offer more advanced memory capabilities, potentially including RAG, through dedicated MemoryService implementations.23 This suggests a layered approach where basic context is handled by state, while long-term retention and external knowledge integration require configuring specific memory components.

## **7\. Utilizing Callbacks for Control and Observation**

Callbacks are a powerful feature in ADK, providing hooks into the agent's execution lifecycle to enable observation, customization, and control without altering the core framework code.10

* **Purpose:** Callbacks serve multiple critical functions:  
  * **Observation & Debugging:** Log detailed information at key stages (e.g., before/after model calls, tool executions) for monitoring and troubleshooting.  
  * **Customization & Control:** Modify data in transit (e.g., LLM requests, tool arguments, responses). Bypass standard execution steps based on custom logic (e.g., return cached response, block disallowed action).  
  * **Guardrail Implementation:** Enforce safety rules, validate inputs/outputs, prevent harmful or unintended operations (a primary use case demonstrated in the Tutorial 8).  
  * **State Management:** Read or dynamically update the session state during execution.  
  * **Integration & Enhancement:** Trigger external actions (e.g., notifications, API calls) or add features like caching.  
* **Implementation:** Callbacks are implemented as standard Python functions. They are registered by passing the function object as an argument to the corresponding callback parameter in the Agent or LlmAgent constructor (e.g., LlmAgent(..., before\_model\_callback=my\_guardrail\_func, after\_tool\_callback=my\_logging\_func)). During execution, ADK automatically calls these registered functions at the appropriate lifecycle points, passing in relevant context objects (like CallbackContext or ToolContext) that provide access to information about the current execution state (e.g., LLM request, tool arguments, session state).  
* **Control Flow:** A callback function can influence the agent's execution flow based on its return value:  
  * Returning None (the default): Signals that the callback has completed its task (e.g., logging) and the agent should proceed with its normal execution path.  
  * Returning a specific object type (varies by callback): Overrides the default behavior. For example, returning an LlmResponse from before\_model\_callback skips the actual LLM call and uses the returned response instead. Returning a dict from before\_tool\_callback skips the tool execution and uses the dictionary as the tool's result.  
* **Callback Types & Use Cases:** ADK provides callbacks targeting key stages:  
  **Table: ADK Callback Hooks and Use Cases**

| Callback Name | Execution Point | Input Context Provides Access To... | Return Type to Override | Primary Use Cases | References |
| :---- | :---- | :---- | :---- | :---- | :---- |
| before\_agent\_callback | Before agent's main logic runs | Initial state, input message | types.Content | Handle simple requests directly, enforce access control, pre-process input | 10 |
| after\_agent\_callback | After agent's main logic completes | Agent's generated output, final state | types.Content | Post-process final response (add disclaimers, formatting), final validation | 10 |
| before\_model\_callback | Before sending request to LLM | LlmRequest (full prompt, history, config) | LlmResponse | Input guardrails, prompt validation/modification, LLM call caching, request logging | 8 |
| after\_model\_callback | After receiving response from LLM | LlmResponse (model's raw output) | LlmResponse | Output sanitization, add standard disclaimers, response modification/formatting | 10 |
| before\_tool\_callback | Before executing a tool/sub-agent | Tool object (BaseTool), arguments (dict) | dict | Tool argument validation, policy enforcement, tool call caching/mocking | 8 |
| after\_tool\_callback | After a tool/sub-agent finishes | Tool result (dict) | dict | Standardize tool output format, post-process tool results, result logging | 10 |

Callbacks represent ADK's primary mechanism for implementing cross-cutting concerns cleanly. By providing well-defined hooks at critical junctures, they allow developers to inject logic for security (guardrails), observability (logging), policy enforcement, and customization without cluttering the core agent or tool implementations, thus promoting a modular and maintainable architecture.\[8, 10\]

## **8\. Deploying ADK Agents**

ADK provides multiple deployment pathways, primarily targeting Google Cloud platforms, to transition agents from development to production environments.

### **Vertex AI Agent Engine**

Agent Engine offers a managed, scalable platform for deploying ADK agents within the Vertex AI ecosystem.5

* **Purpose:** Provides a simplified deployment and serving experience with integration into Vertex AI, including features like managed sessions.  
* **Setup:** Requires installing the Vertex AI SDK with specific extras: pip install google-cloud-aiplatform\[adk,agent\_engines\]. The SDK must be initialized with GCP project ID, location, and a GCS staging bucket: vertexai.init(...).  
* **Wrapping:** The ADK agent object needs to be wrapped using reasoning\_engines.AdkApp(agent=my\_root\_agent, enable\_tracing=True).  
* **Deployment:** The wrapped application is deployed using agent\_engines.create(agent\_engine=adk\_app\_wrapper, requirements=\[...\]). The requirements list should include necessary dependencies like "google-cloud-aiplatform\[adk,agent\_engines\]". Deployment can take several minutes.  
* **Permissions:** A crucial post-deployment step is granting the Agent Engine's service account (format: service-\<PROJECT\_NUMBER\>@gcp-sa-aiplatform-re.iam.gserviceaccount.com) the Vertex AI User (roles/aiplatform.user) IAM role. This permission is necessary for the deployed agent to utilize managed session capabilities.  
* **Interaction:** The deployment returns a remote\_app object representing the deployed agent. Interaction occurs through methods on this object: remote\_app.create\_session(), remote\_app.list\_sessions(), remote\_app.get\_session(), and remote\_app.stream\_query() to send messages and receive events.  
* **Cleanup:** Deployed agents should be deleted to avoid ongoing costs using remote\_app.delete(force=True).

### **Google Cloud Run**

Cloud Run offers a serverless container platform suitable for deploying ADK agents as web services. ADK provides two methods for Cloud Run deployment.6

* **Method 1: adk deploy cloud\_run (Recommended):**  
  * **Purpose:** A simplified command-line interface that automates the build and deployment process.  
  * **Prerequisites:** Authenticated gcloud CLI and necessary environment variables set (GOOGLE\_CLOUD\_PROJECT, GOOGLE\_CLOUD\_LOCATION, GOOGLE\_GENAI\_USE\_VERTEXAI).  
  * **Command:** adk deploy cloud\_run \--project=\<PROJECT\_ID\> \--region=\<REGION\> \<AGENT\_PATH\> \[options\]  
  * **Key Options:**  
    * \<AGENT\_PATH\>: Path to the agent module directory (containing \_\_init\_\_.py, agent.py).  
    * \--service\_name: Custom name for the Cloud Run service.  
    * \--app\_name: Application name for the ADK API server.  
    * \--with\_ui: Deploys the ADK development web UI alongside the API server (default is API only).  
    * \--port: Port the container listens on (default 8000).  
  * **Process:** The command handles building the container image, pushing it to Artifact Registry, and creating/updating the Cloud Run service. It prompts whether to allow unauthenticated invocations.  
* **Method 2: gcloud run deploy (Manual):**  
  * **Purpose:** Provides more control and flexibility, suitable for integrating ADK into custom FastAPI applications or complex build pipelines.  
  * **Requirements:** Requires manual setup of the project structure, including:  
    * agent\_dir/: Directory containing agent code (\_\_init\_\_.py, agent.py).  
    * main.py: FastAPI application entry point, typically using get\_fast\_api\_app() from google.adk.cli.fast\_api to initialize the app.  
    * requirements.txt: Lists Python dependencies (google\_adk, etc.).  
    * Dockerfile: Defines container build instructions (Python base image, copy files, install dependencies, run uvicorn).  
  * **Deployment Command:** gcloud run deploy \<SERVICE\_NAME\> \--source. \--region=\<REGION\> \--project=\<PROJECT\_ID\> \[--allow-unauthenticated\] \--set-env-vars="VAR1=val1,VAR2=val2"  
  * **Process:** gcloud builds the image from the local source (--source.), pushes it, and deploys the service based on the provided configuration and environment variables.

### **Google Kubernetes Engine (GKE)**

GKE provides a powerful container orchestration platform for deploying ADK agents with maximum control over the environment.7

* **Prerequisites:** gcloud CLI, kubectl CLI, an existing GKE cluster (Autopilot recommended, or Standard with Workload Identity enabled), and an Artifact Registry repository.  
* **Project Structure:** Similar to manual Cloud Run deployment, requiring agent\_dir/, main.py, requirements.txt, and Dockerfile. The main.py typically uses get\_fast\_api\_app() and uvicorn.  
* **Build Image:** Build the container image using Cloud Build and push it to Artifact Registry: gcloud builds submit \--tag \<ARTIFACT\_REGISTRY\_IMAGE\_PATH\>.  
* **Kubernetes Configuration (deployment.yaml):** Create a manifest file defining:  
  * **ServiceAccount:** A Kubernetes service account (e.g., adk-agent-sa). If using Vertex AI, configure Workload Identity by binding the necessary IAM role (e.g., roles/aiplatform.user) to this service account using gcloud projects add-iam-policy-binding.  
  * **Deployment:** Specifies the number of replicas, the container image path, resource requests/limits, the container port (e.g., 8080), and crucial environment variables (PORT=8080, GOOGLE\_CLOUD\_PROJECT, GOOGLE\_CLOUD\_LOCATION, GOOGLE\_GENAI\_USE\_VERTEXAI, etc.). Associates pods with the ServiceAccount.  
  * **Service:** Exposes the Deployment, typically using type: LoadBalancer to get an external IP address, mapping an external port (e.g., 80\) to the container's target port (e.g., 8080).  
* **Deploy:** Apply the manifest to the cluster: kubectl apply \-f deployment.yaml.  
* **Access:** Obtain the external IP address of the LoadBalancer service (kubectl get service adk-agent \-o=jsonpath='{.status.loadBalancer.ingress.ip}') and interact with the agent via the UI (if deployed) or API endpoints (e.g., using curl).  
  ADK's deployment options cater to a spectrum of operational requirements.5 The adk deploy cloud\_run command offers the simplest path for serverless deployment.6 Agent Engine provides a managed experience tightly integrated with Vertex AI.5 GKE offers the highest degree of control for teams managing their own Kubernetes infrastructure.7 Common threads across the container-based options (Cloud Run manual, GKE) include the need for containerization (Dockerfile), environment variable configuration for cloud settings, and the use of the get\_fast\_api\_app utility for serving the agent via FastAPI, indicating adherence to standard cloud-native practices.6

**Table: Comparison of ADK Deployment Options**

| Feature | Vertex AI Agent Engine | Cloud Run (adk deploy) | Cloud Run (Manual gcloud) | GKE (Manual kubectl) |
| :---- | :---- | :---- | :---- | :---- |
| **Platform** | Vertex AI (Managed Service) | Google Cloud Run (Serverless) | Google Cloud Run (Serverless) | Google Kubernetes Engine |
| **Ease of Use** | Moderate (SDK init, wrap, deploy) | High (Single CLI command) | Moderate (Requires Dockerfile, main.py) | Low (Requires K8s expertise, manifests) |
| **Scalability** | Managed Scaling | Automatic Scaling | Automatic Scaling | Configurable Scaling (HPA) |
| **Control** | Moderate (Vertex AI managed) | Low (Abstracted by CLI) | Moderate (Container config) | High (Full K8s control) |
| **Key Setup** | Install SDK, AdkApp wrap, create | gcloud auth, adk deploy cmd | Dockerfile, main.py, gcloud deploy | Dockerfile, main.py, K8s manifests, kubectl apply |
| **Primary Use** | Managed ADK deployment, Vertex AI integration | Quick serverless deployment | Custom serverless apps with ADK | Max control, existing K8s env |
| **References** | 5 | 6 | 6 | 7 |

## **9\. Evaluating Agent Performance**

Systematic evaluation is critical for ensuring the quality, reliability, and correctness of AI agents. ADK provides a dedicated framework for this purpose.11

### **Evaluation Approaches**

Two primary structures are used for defining evaluation cases:

* **Test Files (.test.json):**  
  * **Purpose:** Designed for unit testing during active development. Each file typically focuses on a single agent-model interaction (a simple session). Optimized for rapid feedback.  
  * **Structure:** A JSON list of test cases. Each test case object includes:  
    * query: The input message from the user.  
    * expected\_tool\_use: (Optional) A list of expected tool calls, each specifying tool\_name and tool\_input (arguments).  
    * expected\_intermediate\_agent\_responses: (Optional) A list of expected natural language responses from the agent during processing (useful for multi-agent or complex reasoning steps).  
    * reference: The expected final natural language response to the user.  
  * **Configuration:** Test files can be organized in folders. An optional test\_config.json file within a folder can specify custom evaluation criteria thresholds.  
* **Evalset Files (.evalset.json):**  
  * **Purpose:** Used for evaluating more complex, multi-turn conversations, akin to integration testing.  
  * **Structure:** A JSON file containing multiple "evals". Each "eval" represents a distinct session and has:  
    * A unique name.  
    * An optional initial\_session object defining starting state (state, app\_name, user\_id).  
    * One or more "turns", where each turn object has the same structure as a test case (query, expected\_tool\_use, etc.).  
  * **Creation:** Manually creating complex evalsets can be tedious; the documentation notes that UI tools are provided to capture interactive sessions and save them as evals.

### **Evaluation Tools**

ADK offers multiple tools to execute these evaluations:

* **adk web (Web UI):** Provides an interactive environment for running evaluations. Users can interact with an agent to create a session, navigate to the "Eval tab", save the session as an "eval" into a new or existing evalset file, and then run selected or all evals, viewing the pass/fail status directly in the UI.  
* **pytest (Programmatic):** Integrates agent evaluation into standard Python testing workflows using the pytest framework. Tests typically import AgentEvaluator from google.adk.evaluation and call the AgentEvaluator.evaluate method, passing the path to the agent module (agent\_module) and the path to the test file or evalset file (eval\_dataset). An optional initial\_session\_file can be provided to set a specific starting state for the test.  
* **adk eval (CLI):** Enables running evaluations on evalset files directly from the command line, suitable for automation and CI/CD pipelines.  
  * **Command:** adk eval \<AGENT\_MODULE\_FILE\_PATH\> \<EVAL\_SET\_FILE\_PATH\>\[--print\_detailed\_results\]  
  * \<AGENT\_MODULE\_FILE\_PATH\>: Path to the agent module's \_\_init\_\_.py.  
  * \<EVAL\_SET\_FILE\_PATH\>: Path to one or more .evalset.json files. Specific evals within a file can be targeted using the syntax file.json:eval\_name1,eval\_name2.  
  * Optional flags allow specifying a config file and printing detailed results.

### **Metrics & Configuration**

The evaluation framework uses specific metrics to compare the agent's actual behavior against the expected behavior defined in the test/evalset files:

* **tool\_trajectory\_avg\_score:** Measures the accuracy of the sequence of tool calls made by the agent compared to the expected\_tool\_use. It calculates the average match score across the steps (1 for a match at a step, 0 for a mismatch). The default success threshold is 1.0, requiring an exact match of the entire tool call sequence.  
* **response\_match\_score:** Compares the agent's final natural language response against the reference response using the ROUGE metric (measuring overlap/similarity). The default success threshold is 0.8, allowing for some variation in phrasing while still capturing the core meaning.

These default thresholds can be customized by creating a test\_config.json file in the evaluation directory and specifying the desired values for these metrics.

The provision of structured evaluation formats (test/evalset files), multiple execution methods (UI, CLI, programmatic), and specific, configurable metrics underscores the importance placed on rigorous testing and quality assurance within the ADK development lifecycle.11 This comprehensive approach enables developers to systematically verify agent behavior, including complex aspects like tool usage patterns and response quality.

## **10\. Building Responsible Agents**

Developing AI agents that operate safely, securely, and ethically is a critical concern. The ADK documentation provides guidance on building responsible agents by implementing a multi-layered safety approach.12

### **Core Principles & Practices**

Mitigating risks associated with agent autonomy requires careful consideration of identity, inputs/outputs, execution environments, and monitoring.

* **Identity and Authorization:** Controlling *who* the agent acts as and *what* it's allowed to do is fundamental.  
  * *Agent-Auth:* The agent interacts with external systems using its own dedicated identity (e.g., a service account). Access control is managed by granting this identity specific, limited permissions in the target systems. This is suitable when all users interacting with the agent should have the same level of access. Proper logging is crucial to attribute actions back to the initiating user.  
  * *User Auth:* The agent interacts with external systems using the end user's identity (typically via OAuth 2.0). This ensures the agent cannot perform actions the user isn't authorized for. However, developers must be cautious as delegated permissions (scopes) might still be broader than necessary for the agent's specific tasks, potentially requiring additional constraints.  
* **Guardrails (Input/Output Screening):** Implementing checks and balances at critical points in the agent's execution flow is essential.  
  * *In-Tool Guardrails:* Designing tools securely from the outset by exposing only necessary functionality and using developer-set context (tool\_context) to enforce policies dynamically (e.g., restricting database queries based on user role stored in state).  
  * *Built-in Gemini Safety Features:* Leveraging the safety filters integrated into Gemini models. These include non-configurable filters for highly sensitive content and configurable filters for categories like hate speech, harassment, and dangerous content. System instructions provided to the agent can also guide its behavior towards safety.  
  * *Model and Tool Callbacks:* This is a key mechanism for implementing custom guardrails in ADK.  
    * before\_tool\_callback: Can validate tool arguments against policies or state before execution, blocking disallowed calls.8  
    * before\_model\_callback / after\_model\_callback: Can inspect prompts sent to the LLM or responses received from it. This allows for implementing custom safety checks, potentially using a fast, inexpensive secondary model (like Gemini Flash Lite) as a screening layer to detect harmful content, misalignment, or brand safety risks before the main LLM is called or before the response is shown to the user.10  
* **Sandboxed Code Execution:** If agents generate and execute code, the execution environment must be strictly isolated to prevent security vulnerabilities. Options include using managed services like the Vertex Gemini Enterprise API code execution feature or the Vertex Code Interpreter Extension, or building custom hermetic environments with no network access and strict data cleanup.12  
* **Evaluation and Tracing:** Regularly evaluating agent output for quality, relevance, and safety is crucial. Tracing tools that provide visibility into the agent's decision-making process (tool choices, reasoning steps) are vital for understanding and debugging behavior.12 ADK's evaluation framework contributes to this.11  
* **Network Controls (VPC-SC):** Using network security perimeters like VPC Service Controls can provide coarse-grained control, limiting the agent's ability to communicate with unauthorized external services and preventing data exfiltration.12  
* **UI Security:** Always properly escape any content generated by the LLM before rendering it in a user interface. This prevents potential cross-site scripting (XSS) attacks if the model generates malicious HTML or JavaScript, which could occur through prompt injection techniques.12

### **Risk Assessment**

Before implementing specific safety measures, a thorough risk assessment tailored to the agent's capabilities, domain, and deployment context is recommended. Potential risks include ambiguous instructions leading to unintended actions, direct or indirect prompt injection attacks, generation of harmful content, and unsafe actions performed via tools.12

The emphasis on callbacks as a primary mechanism for implementing custom guardrails demonstrates how ADK integrates responsible AI principles directly into its architecture.8 By providing these hooks, the framework empowers developers to implement fine-grained safety logic at critical model and tool interaction points, complementing built-in model features and secure design practices.

## **11\. ADK API Reference Overview**

The API Reference section of the ADK documentation serves as the definitive technical guide to the framework's structure and components.23

* **Structure:** Organized hierarchically based on the Python modules and submodules within the google.adk package. This structure mirrors the modular design of the framework itself.  
* **Key Modules:** Provides detailed documentation for core modules, including:  
  * google.adk.agents: Defines agent classes (LlmAgent, SequentialAgent, LoopAgent, ParallelAgent, BaseAgent).  
  * google.adk.tools: Defines tool-related classes (FunctionTool, LongRunningFunctionTool, AgentTool, BaseTool, ToolContext, OpenAPIToolset, VertexAiSearchTool, etc.) and authentication components.  
  * google.adk.sessions: Defines session management classes (BaseSessionService, InMemorySessionService, DatabaseSessionService, Session, State).  
  * google.adk.memory: Defines memory service classes (BaseMemoryService, InMemoryMemoryService, VertexAiRagMemoryService).  
  * google.adk.callbacks: (Implicitly covered, as callbacks are parameters to Agent classes).  
  * google.adk.runners: Defines agent execution runners (Runner, InMemoryRunner).  
  * google.adk.evaluation: Defines evaluation components (AgentEvaluator).  
  * google.adk.models: Defines LLM integration classes (BaseLlm, Gemini, LiteLlm).  
  * Other supporting modules like artifacts, code\_executors, events, examples, planners.  
* **Content per Module:** For each class within a module, the reference typically provides:  
  * Class name and inheritance.  
  * Detailed descriptions of constructor parameters (\_\_init\_\_ arguments).  
  * Descriptions of public attributes and properties.  
  * Detailed descriptions of public methods, including signatures (parameters, types, defaults), return types, and explanations of functionality. For standalone functions, it provides signatures, return types, and descriptions.  
* **Purpose:** To provide developers with the low-level technical details needed to understand and effectively use each component of the ADK framework – how to instantiate classes, what parameters are available, what methods to call, and what behavior to expect.

The comprehensive and structured nature of the API reference directly reflects ADK's modular design, equipping developers with the necessary information to leverage its components for building complex agentic applications.1

## **12\. Conclusion**

The Google Agent Development Kit (ADK) presents a comprehensive and flexible Python framework for building, evaluating, and deploying AI agents, with a strong orientation towards the Google Cloud and AI ecosystem. Its modular design, based on composable Agents, Tools, Session/Memory services, and Runners, allows developers to construct applications ranging from simple tool-using agents to sophisticated multi-agent systems.1

Key strengths of ADK include its flexibility in supporting various agent architectures (LLM-driven, deterministic workflows, custom logic), multiple LLMs (via direct integration or wrappers like LiteLLM), and diverse tool integration patterns (custom functions, built-in tools, third-party libraries, Google Cloud services, OpenAPI specs).1 The framework places significant emphasis on developer experience, offering clear pathways for getting started, alongside powerful features for advanced development.1

Critical mechanisms enabling complex agent behavior include session state management (primarily via ctx.session.state and output\_key) for short-term memory and data passing, and the callback system, which provides essential hooks for implementing guardrails, observability, and customization at key lifecycle points.8 The framework's approach to responsible AI is deeply integrated, leveraging callbacks and secure design principles alongside built-in model safety features.12

ADK offers multiple deployment options targeting Google Cloud (Vertex AI Agent Engine, Cloud Run, GKE), catering to different operational needs from managed services to full container orchestration control.5 Furthermore, the dedicated evaluation framework underscores a commitment to rigorous testing and quality assurance for agentic systems.11

While ADK provides powerful abstractions, effective development often relies on careful prompt engineering (for LlmAgent instructions and descriptions driving behavior and delegation) and thoughtful management of state and authentication, particularly in complex multi-agent or tool-heavy scenarios.8 Overall, ADK equips developers with a robust toolkit for building sophisticated, integrated, and responsible AI agents, particularly within the context of Google's AI and cloud infrastructure.

#### **Obras citadas**

1. Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/](https://google.github.io/adk-docs/)  
2. Quickstart \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/get-started/quickstart/](https://google.github.io/adk-docs/get-started/quickstart/)  
3. Built-in tools \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/built-in-tools/](https://google.github.io/adk-docs/tools/built-in-tools/)  
4. Google Cloud tools \- Agent Development Kit, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/google-cloud-tools/](https://google.github.io/adk-docs/tools/google-cloud-tools/)  
5. Agent Engine \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/deploy/agent-engine/](https://google.github.io/adk-docs/deploy/agent-engine/)  
6. Cloud Run \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/deploy/cloud-run/](https://google.github.io/adk-docs/deploy/cloud-run/)  
7. GKE \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/deploy/gke/](https://google.github.io/adk-docs/deploy/gke/)  
8. Tutorial \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/get-started/tutorial/](https://google.github.io/adk-docs/get-started/tutorial/)  
9. Installation \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/get-started/installation/](https://google.github.io/adk-docs/get-started/installation/)  
10. Callbacks: Observe, Customize, and Control Agent Behavior \- Agent ..., fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/callbacks/](https://google.github.io/adk-docs/callbacks/)  
11. Why Evaluate Agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/evaluate/](https://google.github.io/adk-docs/evaluate/)  
12. Responsible Agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/guides/responsible-agents/](https://google.github.io/adk-docs/guides/responsible-agents/)  
13. LLM agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/llm-agents/](https://google.github.io/adk-docs/agents/llm-agents/)  
14. Sequential agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)  
15. Workflow Agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/workflow-agents/](https://google.github.io/adk-docs/agents/workflow-agents/)  
16. Loop agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)  
17. Parallel agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)  
18. Custom agents \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/agents/custom-agents/](https://google.github.io/adk-docs/agents/custom-agents/)  
19. Function tools \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/function-tools/](https://google.github.io/adk-docs/tools/function-tools/)  
20. Third party tools \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/third-party-tools/](https://google.github.io/adk-docs/tools/third-party-tools/)  
21. OpenAPI tools \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/openapi-tools/](https://google.github.io/adk-docs/tools/openapi-tools/)  
22. Authentication \- Agent Development Kit \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/tools/authentication/](https://google.github.io/adk-docs/tools/authentication/)  
23. Agent Development Kit documentation \- Google, fecha de acceso: abril 18, 2025, [https://google.github.io/adk-docs/api-reference/](https://google.github.io/adk-docs/api-reference/)  
24. fecha de acceso: enero 1, 1970, [https://google.github.io/adk-docs/sessions-memory/session/](https://google.github.io/adk-docs/sessions-memory/session/)  
25. fecha de acceso: enero 1, 1970, [https://google.github.io/adk-docs/sessions-memory/state/](https://google.github.io/adk-docs/sessions-memory/state/)  
26. fecha de acceso: enero 1, 1970, [https://google.github.io/adk-docs/sessions-memory/memory/](https://google.github.io/adk-docs/sessions-memory/memory/)  
27. fecha de acceso: enero 1, 1970, [https://google.github.io/adk-docs/agents/multi-agent-systems/](https://google.github.io/adk-docs/agents/multi-agent-systems/)