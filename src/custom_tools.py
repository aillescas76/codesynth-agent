import json
import os
import pathlib
import subprocess
import shutil # Needed for checking git executable
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


# --- Git Tools ---

def _run_git_command(base_dir: pathlib.Path, command: list[str]) -> dict:
    """Helper function to run a Git command in the specified directory."""
    if not shutil.which("git"):
        return {"status": "failure", "message": "Error: 'git' command not found in PATH."}
    try:
        # Ensure the base directory exists before running git commands
        if not base_dir.is_dir():
             return {"status": "failure", "message": f"Error: Base directory does not exist: {base_dir}"}

        # Run the git command with cwd set to the base directory
        result = subprocess.run(
            ["git"] + command,
            cwd=base_dir,
            capture_output=True,
            text=True,
            check=False, # Don't raise exception on non-zero exit, handle it below
            encoding='utf-8'
        )
        if result.returncode == 0:
            return {"status": "success", "message": f"Git command '{' '.join(command)}' executed successfully.", "stdout": result.stdout, "stderr": result.stderr}
        else:
            error_message = f"Git command '{' '.join(command)}' failed with exit code {result.returncode}."
            # Combine stderr and stdout for more context on failure
            error_details = f"Stderr: {result.stderr.strip()}\nStdout: {result.stdout.strip()}"
            return {"status": "failure", "message": error_message, "details": error_details.strip()}
    except FileNotFoundError:
        # This might happen if base_dir is invalid despite the check, though unlikely
         return {"status": "failure", "message": f"Error: Base directory not found during git execution: {base_dir}"}
    except PermissionError:
        return {"status": "failure", "message": f"Error: Permission denied executing git command in {base_dir}."}
    except Exception as e:
        return {"status": "failure", "message": f"An unexpected error occurred running git command in {base_dir}: {e}"}


def git_init(base_path_str: str) -> dict:
    """
    Initializes a Git repository in the specified base project directory if one doesn't exist.

    Args:
        base_path_str: The relative or absolute path to the base project directory.
                       Relative paths are resolved from the agent's execution directory.

    Returns:
        A dictionary indicating the status (success/failure) and a message.
    """
    try:
        # Resolve the base path first
        base_dir = pathlib.Path(base_path_str).resolve(strict=True)
    except FileNotFoundError:
        return {"status": "failure", "message": f"Base path directory not found: {base_path_str}"}
    except Exception as e:
        return {"status": "failure", "message": f"Error resolving base path '{base_path_str}': {e}"}

    # Check if .git directory already exists
    git_dir = base_dir / ".git"
    if git_dir.exists():
        return {"status": "success", "message": f"Git repository already exists in {base_path_str}."}

    # Run git init
    return _run_git_command(base_dir, ["init"])


def git_add(base_path_str: str, paths_to_add: list[str]) -> dict:
    """
    Stages specified files or directories within the Git repository located at base_path_str.

    Args:
        base_path_str: The relative or absolute path to the base project directory (which should be a Git repo).
        paths_to_add: A list of relative paths (strings) *within* the base_path_str
                      to stage (e.g., ["src/main.py", "docs/"]). Use "." to add all changes.

    Returns:
        A dictionary indicating the status (success/failure) and a message.
    """
    try:
        # Resolve the base path first
        base_dir = pathlib.Path(base_path_str).resolve(strict=True)
    except FileNotFoundError:
        return {"status": "failure", "message": f"Base path directory not found: {base_path_str}"}
    except Exception as e:
        return {"status": "failure", "message": f"Error resolving base path '{base_path_str}': {e}"}

    if not paths_to_add:
        return {"status": "failure", "message": "No paths provided to stage."}

    # Basic validation: ensure provided paths are relative and don't try to escape.
    # _resolve_safe_path isn't directly applicable here as we just need to pass the relative strings to git add.
    # We rely on git itself operating within the CWD set by _run_git_command.
    for p in paths_to_add:
        if os.path.isabs(p) or ".." in p:
             return {"status": "failure", "message": f"Invalid or potentially unsafe relative path provided for git add: {p}"}

    # Run git add command
    return _run_git_command(base_dir, ["add"] + paths_to_add)


def git_commit(base_path_str: str, commit_message: str) -> dict:
    """
    Creates a commit with the staged changes in the Git repository at base_path_str.

    Args:
        base_path_str: The relative or absolute path to the base project directory (which should be a Git repo).
        commit_message: The commit message string.

    Returns:
        A dictionary indicating the status (success/failure) and a message.
    """
    try:
        # Resolve the base path first
        base_dir = pathlib.Path(base_path_str).resolve(strict=True)
    except FileNotFoundError:
        return {"status": "failure", "message": f"Base path directory not found: {base_path_str}"}
    except Exception as e:
        return {"status": "failure", "message": f"Error resolving base path '{base_path_str}': {e}"}

    if not commit_message:
        return {"status": "failure", "message": "Commit message cannot be empty."}

    # Run git commit command
    # Use -m flag for the message
    return _run_git_command(base_dir, ["commit", "-m", commit_message])


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
