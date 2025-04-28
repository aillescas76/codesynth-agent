# ADK Requirement Implementation Agent System

This project implements a multi-agent system using the Google Agent Development Kit (ADK) designed to take a natural language software requirement, interact with an optional existing codebase, and attempt to produce a planned, implemented, tested, and refactored code solution.

## Architecture

The system follows a multi-agent approach as outlined in `docs/ADK-Agent-System-Plan-for-Requirement-Implementation.md`:

1.  **Requirement Analysis Agent:** Understands and structures the initial requirement.
2.  **Code Exploration Agent (Optional):** Analyzes an existing codebase if a path is provided.
3.  **Implementation Planning Agent:** Creates a step-by-step plan.
4.  **Code Generation Agent:** Writes the code based on the plan.
5.  **Testing Agent:** Generates and runs unit tests (using pytest via Docker).
6.  **Refactoring Agent:** Attempts to fix failing tests or improve code quality.
7.  **Orchestrator Agent (`CustomAgent`):** Manages the workflow, including conditional execution and a test/refactor loop.

## Prerequisites

*   **Docker:** Docker must be installed and running on your system. The system relies on Docker for sandboxing the test execution environment.
*   **Docker Client in Image:** The primary Docker image used to run the application needs the Docker *client* CLI installed within it to manage the test sandbox containers. (See Dockerfile instructions below).
*   **Python:** Python (3.9+) is needed to run the ADK framework *within* the Docker container.
*   **Google Cloud / AI Studio Credentials:** You need API keys or credentials set up for the Google AI models (e.g., Gemini) used by the agents.

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Configure Environment Variables:**
    *   Create a file named `.env` in the project root directory.
    *   Add your Google API credentials. Choose **one** of the following methods:

        *   **For Google AI Studio (Gemini API Key):**
            ```dotenv
            # .env
            GOOGLE_API_KEY=YOUR_API_KEY_HERE
            GOOGLE_GENAI_USE_VERTEXAI=FALSE
            ```

        *   **For Google Cloud Vertex AI:**
            ```dotenv
            # .env
            GOOGLE_CLOUD_PROJECT=your-gcp-project-id
            GOOGLE_CLOUD_LOCATION=your-gcp-region # e.g., us-central1
            GOOGLE_GENAI_USE_VERTEXAI=TRUE
            # Ensure you have authenticated via gcloud CLI: gcloud auth application-default login
            ```
    *   **Optional Configuration:**
        ```dotenv
        # Specify the Gemini model to use (e.g., gemini-1.5-flash, gemini-1.5-pro)
        # This model will be used by default if not overridden in specific agent definitions.
        ADK_LLM_MODEL=gemini-1.5-flash
        ```
        ```dotenv
        # Maximum attempts for the refactoring loop (default is 2)
        MAX_REFACTOR_ATTEMPTS=3
        ```

3.  **Create Dockerfile:**
    *   Create a `Dockerfile` in the project root. Here is a basic example (adapt as needed, especially for Docker CLI installation):

        ```dockerfile
        # Dockerfile
        FROM python:3.11-slim

        WORKDIR /app

        # Install necessary system packages (including Docker CLI)
        # Example for Debian/Ubuntu based images:
        RUN apt-get update && \
            apt-get install -y --no-install-recommends \
            ca-certificates curl gnupg lsb-release && \
            mkdir -p /etc/apt/keyrings && \
            curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
              $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
            apt-get update && \
            apt-get install -y --no-install-recommends docker-ce-cli && \
            apt-get clean && \
            rm -rf /var/lib/apt/lists/*

        # Install Python dependencies
        COPY requirements.txt .
        # Ensure requirements.txt includes: google-adk python-dotenv docker
        RUN pip install --no-cache-dir -r requirements.txt

        # Copy project source code
        COPY src/ src/

        # Define the default command
        CMD ["python", "src/main.py"]
        ```
    *   Create a `requirements.txt` file listing dependencies:
        ```txt
        # requirements.txt
        google-adk
        python-dotenv
        docker
        pytest # Needed if running tests from inside this container
        ```

4.  **Build the Docker Image (Optional but Recommended):**
    *   You can build the image explicitly for faster startup later.
    ```bash
    docker build -t adk-req-impl .
    ```
    *   If you skip this, `docker run` might build it implicitly if using tools like Docker Compose, or you'll need to ensure the image specified in `docker run` exists.

5.  **Configure Test Runner Image:**
    *   The `run_tests` tool in `src/custom_tools.py` uses a Docker image specified by the `TEST_RUNNER_IMAGE` variable (default: `python:3.11-slim`).
    *   **Important:** This test runner image **must have `pytest` installed**. You can either:
        *   Use a pre-built image that includes Python and pytest.
        *   Build your own simple test runner image (e.g., `FROM python:3.11-slim\nRUN pip install pytest`) and update `TEST_RUNNER_IMAGE` in `src/custom_tools.py` to use your custom image name.

## Running the System

Execute the main application script using Docker. You need to:

*   Mount the Docker socket (`/var/run/docker.sock`) to allow the application container to run the test sandbox containers.
*   Pass the `.env` file for credentials.
*   Mount the project directory (or at least the parts needed for file I/O by the agents) if the agents need to read/write files relative to the host project structure. The current `custom_tools.py` assumes file operations happen relative to the project root *as seen by the container*. Mounting the whole project ensures consistency.
*   Pass the requirement and optional codebase path as command-line arguments.

```bash
# Example using the pre-built image name 'adk-req-impl'
# Mount current directory (.) into /app inside the container
# Mount Docker socket
# Pass .env file
# Run main.py with arguments

docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --env-file .env \
  -v "$(pwd)":/app \
  adk-req-impl \
  python src/main.py \
    --requirement "Create a Python function in a file named 'calculator.py' that takes two numbers and returns their sum."

# Example with an existing codebase (assuming 'my_code' is a subdir in your project)
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --env-file .env \
  -v "$(pwd)":/app \
  adk-req-impl \
  python src/main.py \
    --requirement "Add a subtraction feature to the Calculator class in my_code/calculator.py" \
    --codebase-path "my_code"
```

The application will print the events generated by the ADK runner, showing the progress through the different agents and tool calls. The final session state will be printed at the end. Generated code and test files will appear in your project directory (as mounted into the container).

## Project Structure

```
.
├── Dockerfile          # Defines the main application container
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (API keys, config) - !! GITIGNORE !!
├── docs/               # Documentation (plans, etc.)
│   ├── ADK-Agent-System-Plan-for-Requirement-Implementation.md
│   └── ADK-Implementation-Steps.md
├── src/                # Source code
│   ├── __init__.py
│   ├── agents/         # ADK Agent definitions
│   │   ├── __init__.py
│   │   ├── code_exploration.py
│   │   ├── code_generation.py
│   │   ├── implementation_planning.py
│   │   ├── orchestrator.py     # Main workflow logic
│   │   ├── refactoring.py
│   │   ├── requirement_analysis.py
│   │   └── testing.py
│   ├── custom_tools.py # Implementations of file I/O and test execution tools
│   └── main.py         # Main script to run the agent system
└── tests/              # Unit/Integration tests
    └── test_custom_tools.py # Tests for the custom tools
```

## Custom Tools

The `src/custom_tools.py` file implements functions used by the agents:

*   `read_file`: Reads files relative to the project root.
*   `write_file`: Writes files relative to the project root.
*   `list_directory`: Lists directory contents relative to the project root.
*   `run_tests`: Executes `pytest` within a sandboxed Docker container.

**Security:** These tools enforce path safety, preventing access outside the defined `PROJECT_ROOT`. Absolute paths and path traversal (`../`) are disallowed. The `run_tests` tool uses Docker for sandboxing with network access disabled.

## Testing

Unit tests for the custom tools are located in the `tests/` directory. To run them:

1.  Ensure Docker is running.
2.  Ensure the `TEST_RUNNER_IMAGE` (with pytest installed) is available locally or can be pulled.
3.  Run pytest using the application Docker container:

    ```bash
    # Example using the pre-built image name 'adk-req-impl'
    docker run --rm -it \
      -v /var/run/docker.sock:/var/run/docker.sock \
      --env-file .env \
      -v "$(pwd)":/app \
      adk-req-impl \
      pytest tests/
    ```

This command runs the tests defined in `tests/test_custom_tools.py`.
