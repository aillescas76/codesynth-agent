import json
import os
import pathlib
import subprocess
import typing

import docker
from docker.errors import ContainerError, ImageNotFound, APIError
from docker.types import Mount

# --- Configuration ---

# Define the root directory for allowed file operations.
# Assumes custom_tools.py is in 'src/' and the project root is its parent.
# Adjust this path if your project structure is different.
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()

# Define the Docker image to use for running tests.
# This image should have Python and the necessary test runner (e.g., pytest) installed.
# You might want to build a custom image for this.
TEST_RUNNER_IMAGE = "python:3.11-slim" # Example: Replace with your actual test image

# Define the internal workspace path inside the test container
CONTAINER_WORKSPACE = "/workspace"

# --- Security Helper ---

def _is_path_safe(path_to_check: pathlib.Path) -> bool:
    """Checks if the resolved path is within the defined PROJECT_ROOT."""
    try:
        resolved_path = path_to_check.resolve(strict=True)
        # Check if the resolved path is within the project root directory
        return PROJECT_ROOT in resolved_path.parents or resolved_path == PROJECT_ROOT
    except (FileNotFoundError, RuntimeError):
        # RuntimeError can occur on Windows with long paths or specific junctions
        # FileNotFoundError if path doesn't exist (resolve strict=True)
        return False
    except Exception:
        # Catch any other potential exceptions during path resolution
        return False

def _resolve_safe_path(path_str: str) -> typing.Optional[pathlib.Path]:
    """Resolves a string path relative to PROJECT_ROOT and checks safety."""
    try:
        # Attempt to create the path object relative to project root
        # Forbid absolute paths by checking if path_str starts with '/' or drive letter
        if os.path.isabs(path_str):
             print(f"Error: Absolute paths are not allowed: {path_str}")
             return None

        # Join with project root and resolve
        full_path = (PROJECT_ROOT / path_str).resolve()

        # Check if the resolved path is still within the project root
        if PROJECT_ROOT in full_path.parents or full_path == PROJECT_ROOT:
            return full_path
        else:
            print(f"Error: Path traversal detected or path outside project root: {path_str}")
            return None
    except Exception as e:
        print(f"Error resolving path '{path_str}': {e}")
        return None


# --- Custom Tools ---

def read_file(path: str) -> str:
    """
    Reads the content of a file within the project directory.

    Args:
        path: The relative path to the file within the project directory.
              Do not use absolute paths or attempt to navigate outside
              the project structure (e.g., using '../').

    Returns:
        The content of the file as a string, or an error message if
        the file cannot be read or the path is invalid/unsafe.
    """
    safe_path = _resolve_safe_path(path)
    if not safe_path:
        return f"Error: Invalid or unsafe path specified: {path}"

    try:
        # Re-check existence after resolving potential symlinks etc.
        if not safe_path.is_file():
             return f"Error: File not found at resolved path: {safe_path}"

        with open(safe_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except PermissionError:
        return f"Error: Permission denied when reading file: {path}"
    except Exception as e:
        return f"Error: An unexpected error occurred while reading file '{path}': {e}"

def write_file(path: str, content: str, overwrite: bool = False) -> typing.Dict[str, typing.Any]:
    """
    Writes content to a file within the project directory.

    Args:
        path: The relative path to the file within the project directory.
              Do not use absolute paths or attempt to navigate outside
              the project structure (e.g., using '../').
        content: The string content to write to the file.
        overwrite: If True, overwrite the file if it exists.
                   If False, return an error if the file exists. Defaults to False.

    Returns:
        A dictionary indicating the status:
        {"status": "success", "message": "File written successfully."} or
        {"status": "failure", "message": "Error description."}
    """
    safe_path = _resolve_safe_path(path)
    if not safe_path:
        return {"status": "failure", "message": f"Invalid or unsafe path specified: {path}"}

    try:
        # Ensure the parent directory exists
        safe_path.parent.mkdir(parents=True, exist_ok=True)

        if safe_path.exists() and not overwrite:
            return {"status": "failure", "message": f"File already exists and overwrite is False: {path}"}
        if safe_path.is_dir():
             return {"status": "failure", "message": f"Path points to a directory, cannot write file: {path}"}

        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"File written successfully to {path}"}
    except PermissionError:
        return {"status": "failure", "message": f"Permission denied when writing to file: {path}"}
    except Exception as e:
        return {"status": "failure", "message": f"An unexpected error occurred while writing file '{path}': {e}"}

def list_directory(path: str = ".", recursive: bool = False) -> typing.Union[list[str], typing.Dict[str, str]]:
    """
    Lists the contents (files and directories) of a specified directory
    within the project structure.

    Args:
        path: The relative path to the directory within the project.
              Defaults to the project root ('.'). Do not use absolute paths
              or attempt to navigate outside the project structure.
        recursive: If True, list contents recursively. Defaults to False.

    Returns:
        A list of relative paths (strings) of files and directories within
        the specified path, relative to that path.
        Returns a dictionary with an error message if the path is invalid,
        unsafe, or not a directory.
    """
    safe_path = _resolve_safe_path(path)
    if not safe_path:
        return {"status": "failure", "message": f"Invalid or unsafe path specified: {path}"}

    if not safe_path.is_dir():
        return {"status": "failure", "message": f"Path is not a directory: {path}"}

    results = []
    try:
        if recursive:
            for item in safe_path.rglob('*'):
                # Calculate path relative to the original 'path' argument for consistency
                relative_item_path = item.relative_to(safe_path)
                results.append(str(relative_item_path))
        else:
            for item in safe_path.iterdir():
                results.append(item.name)
        return results
    except PermissionError:
         return {"status": "failure", "message": f"Permission denied when listing directory: {path}"}
    except Exception as e:
        return {"status": "failure", "message": f"An unexpected error occurred listing directory '{path}': {e}"}


def run_tests(test_paths: list[str]) -> dict:
    """
    Runs tests (e.g., pytest) within a specified list of paths using a secure,
    isolated Docker container. The project's root directory is mounted into
    the container. Assumes tests are relative to the project root.

    Args:
        test_paths: A list of relative paths (strings) to the test files or
                    directories within the project root.

    Returns:
        A dictionary containing the test results, including 'status' ('PASS',
        'FAIL', or 'ERROR'), 'output' (captured stdout/stderr), and potentially
        parsed counts ('passed', 'failed', 'errors').
        Example: {"status": "PASS", "passed": 5, "failed": 0, "errors": 0, "output": "..."}
                 {"status": "ERROR", "message": "Docker error details", "output": ""}
    """
    if not test_paths:
        return {"status": "ERROR", "message": "No test paths provided.", "output": ""}

    # Validate all paths before proceeding
    validated_container_paths = []
    for p in test_paths:
        safe_host_path = _resolve_safe_path(p)
        if not safe_host_path:
             return {"status": "ERROR", "message": f"Invalid or unsafe test path: {p}", "output": ""}
        # Convert host path to the expected path inside the container
        relative_path = safe_host_path.relative_to(PROJECT_ROOT)
        validated_container_paths.append(f"{CONTAINER_WORKSPACE}/{relative_path}")

    try:
        client = docker.from_env()
        # Ensure the test runner image exists locally
        try:
            client.images.get(TEST_RUNNER_IMAGE)
        except ImageNotFound:
             print(f"Test runner image '{TEST_RUNNER_IMAGE}' not found. Pulling...")
             client.images.pull(TEST_RUNNER_IMAGE)

    except Exception as e:
        return {"status": "ERROR", "message": f"Docker client initialization failed: {e}", "output": ""}

    # Mount the entire project root read-only into the container's workspace
    # Adjust if specific subdirs are needed or write access is required for coverage etc.
    mounts = [
        Mount(target=CONTAINER_WORKSPACE, source=str(PROJECT_ROOT), type='bind', read_only=True)
    ]

    # Construct the command to run inside the container (e.g., using pytest)
    # This assumes pytest is installed in the TEST_RUNNER_IMAGE
    # Add flags like '-v' for verbose, '--json-report' if parsing JSON output
    test_command = ["pytest"] + validated_container_paths

    print(f"Running tests in Docker. Image: {TEST_RUNNER_IMAGE}, Command: {' '.join(test_command)}")

    try:
        container = client.containers.run(
            image=TEST_RUNNER_IMAGE,
            command=test_command,
            mounts=mounts,
            working_dir=CONTAINER_WORKSPACE,
            network_disabled=True, # Disable network access
            remove=True,           # Automatically remove container when done
            stdout=True,
            stderr=True,
            detach=False,          # Run in foreground and wait for completion
            # Consider adding resource limits (mem_limit, cpu_quota) for production
        )
        # Output is bytes, decode it
        output = container.decode('utf-8')
        status = "PASS" # Assume pass unless ContainerError occurred (non-zero exit)
        print(f"Test execution finished. Status: {status}\nOutput:\n{output}")

    except ContainerError as e:
        # Container exited with a non-zero status code (tests likely failed)
        output = e.stderr.decode('utf-8') if e.stderr else ""
        status = "FAIL"
        print(f"Test execution failed (non-zero exit code). Status: {status}\nOutput:\n{output}")

    except ImageNotFound:
        return {"status": "ERROR", "message": f"Docker image not found: {TEST_RUNNER_IMAGE}", "output": ""}
    except APIError as e:
        return {"status": "ERROR", "message": f"Docker API error: {e}", "output": ""}
    except Exception as e:
        # Catch other potential errors during container run
        return {"status": "ERROR", "message": f"An unexpected error occurred running tests in Docker: {e}", "output": ""}

    # --- Basic Output Parsing (Example for pytest) ---
    # This is a simple example; robust parsing might require specific pytest plugins
    # (e.g., pytest-json-report) or more complex regex.
    passed_count = output.count(" passed") # Very basic
    failed_count = output.count(" failed") # Very basic
    error_count = output.count(" error")   # Very basic

    # Refine status based on counts if possible
    if status == "PASS" and (failed_count > 0 or error_count > 0):
        status = "FAIL" # Mark as FAIL if tests ran but some failed/errored

    return {
        "status": status,
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "output": output
    }
