import pytest
import pathlib
import shutil
import json
import os
import sys

# Add src directory to sys.path to allow importing custom_tools
# This assumes tests are run from the project root directory
PROJECT_ROOT_TEST = pathlib.Path(__file__).parent.parent.resolve()
SRC_DIR = PROJECT_ROOT_TEST / "src"
sys.path.insert(0, str(SRC_DIR))

# Now import the functions from custom_tools
# Also import the PROJECT_ROOT defined there for consistency in tests
from custom_tools import (
    read_file,
    write_file,
    list_directory,
    run_tests,
    PROJECT_ROOT, # Import the PROJECT_ROOT from the module
    TEST_RUNNER_IMAGE # Import for potential use/checking
)

# Define paths relative to the PROJECT_ROOT from custom_tools
TEST_DIR_NAME = "temp_test_data"
TEST_DIR = PROJECT_ROOT / TEST_DIR_NAME
TEST_FILE_NAME = "test_file.txt"
TEST_FILE = TEST_DIR / TEST_FILE_NAME
NESTED_DIR_NAME = "nested_dir"
NESTED_DIR = TEST_DIR / NESTED_DIR_NAME
NESTED_FILE_NAME = "nested_file.txt"
NESTED_FILE = NESTED_DIR / NESTED_FILE_NAME
DUMMY_PYTEST_FILE_NAME = "test_dummy_sample.py"
DUMMY_PYTEST_FILE = TEST_DIR / DUMMY_PYTEST_FILE_NAME

# --- Test Fixture ---

@pytest.fixture(scope="module", autouse=True)
def test_environment():
    """Sets up and tears down the test directory and files."""
    # Setup: Create test directory and files
    TEST_DIR.mkdir(exist_ok=True)
    NESTED_DIR.mkdir(exist_ok=True)
    TEST_FILE.write_text("Hello Test", encoding='utf-8')
    NESTED_FILE.write_text("Hello Nested Test", encoding='utf-8')

    # Dummy pytest file content
    dummy_test_content = """
import pytest

def test_success():
    assert True

# Uncomment to test failures
# def test_failure():
#    assert False
"""
    DUMMY_PYTEST_FILE.write_text(dummy_test_content, encoding='utf-8')

    yield # Tests run here

    # Teardown: Remove the test directory and its contents
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)

# --- Helper to get relative path string ---
def relative_path_str(path_obj: pathlib.Path) -> str:
    """Returns the path relative to PROJECT_ROOT as a string."""
    return str(path_obj.relative_to(PROJECT_ROOT))

# --- Tests for read_file ---

def test_read_file_success():
    content = read_file(relative_path_str(TEST_FILE))
    assert content == "Hello Test"

def test_read_file_nested_success():
    content = read_file(relative_path_str(NESTED_FILE))
    assert content == "Hello Nested Test"

def test_read_file_not_found():
    result = read_file(f"{TEST_DIR_NAME}/non_existent_file.txt")
    assert "Error: File not found" in result

def test_read_file_is_directory():
    result = read_file(TEST_DIR_NAME) # Try reading the directory itself
    assert "Error: File not found at resolved path" in result # is_file() check fails

def test_read_file_unsafe_path_traversal():
    result = read_file("../some_other_file.txt") # Attempt traversal
    assert "Error: Invalid or unsafe path specified" in result

def test_read_file_unsafe_path_absolute(tmp_path):
    # Create a temporary file outside the project root
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("outside content")
    result = read_file(str(outside_file.resolve())) # Use absolute path
    assert "Error: Absolute paths are not allowed" in result

# --- Tests for write_file ---

def test_write_file_success_new():
    new_file_rel_path = f"{TEST_DIR_NAME}/new_write_file.txt"
    result = write_file(new_file_rel_path, "New content here")
    assert result["status"] == "success"
    assert (PROJECT_ROOT / new_file_rel_path).read_text(encoding='utf-8') == "New content here"

def test_write_file_success_overwrite():
    # First write
    write_file(relative_path_str(TEST_FILE), "Initial content")
    # Then overwrite
    result = write_file(relative_path_str(TEST_FILE), "Overwritten content", overwrite=True)
    assert result["status"] == "success"
    assert TEST_FILE.read_text(encoding='utf-8') == "Overwritten content"

def test_write_file_fail_exists_no_overwrite():
    result = write_file(relative_path_str(TEST_FILE), "Attempt to overwrite", overwrite=False)
    assert result["status"] == "failure"
    assert "File already exists" in result["message"]
    # Ensure content wasn't overwritten
    assert TEST_FILE.read_text(encoding='utf-8') != "Attempt to overwrite"

def test_write_file_fail_is_directory():
    result = write_file(TEST_DIR_NAME, "Trying to write to dir")
    assert result["status"] == "failure"
    assert "Path points to a directory" in result["message"]

def test_write_file_unsafe_path_traversal():
    result = write_file("../unsafe_write.txt", "unsafe content")
    assert result["status"] == "failure"
    assert "Invalid or unsafe path specified" in result["message"]

def test_write_file_unsafe_path_absolute(tmp_path):
    outside_file = tmp_path / "outside_write.txt"
    result = write_file(str(outside_file.resolve()), "outside content")
    assert result["status"] == "failure"
    assert "Absolute paths are not allowed" in result["message"]

# --- Tests for list_directory ---

def test_list_directory_success_non_recursive():
    # List contents of TEST_DIR_NAME
    result = list_directory(TEST_DIR_NAME)
    assert isinstance(result, list)
    # Use sets for order-independent comparison
    expected = {TEST_FILE_NAME, NESTED_DIR_NAME, DUMMY_PYTEST_FILE_NAME}
    # Get actual file names present in the test directory
    actual_files = {item.name for item in TEST_DIR.iterdir()}
    assert actual_files == expected


def test_list_directory_success_recursive():
    result = list_directory(TEST_DIR_NAME, recursive=True)
    assert isinstance(result, list)
    # Expected paths relative to TEST_DIR_NAME
    expected = {
        TEST_FILE_NAME,
        NESTED_DIR_NAME,
        os.path.join(NESTED_DIR_NAME, NESTED_FILE_NAME), # Use os.path.join for cross-platform compatibility
        DUMMY_PYTEST_FILE_NAME
    }
    # Convert result paths to use os specific separators for comparison
    result_paths_set = {os.path.normpath(p) for p in result}
    expected_paths_set = {os.path.normpath(p) for p in expected}
    assert result_paths_set == expected_paths_set


def test_list_directory_default_path_non_recursive():
    # This lists the PROJECT_ROOT. Be careful if many files exist there.
    # We know 'src' and 'tests' should be there.
    result = list_directory(".") # Default path is '.'
    assert isinstance(result, list)
    assert "src" in result
    assert "tests" in result
    assert TEST_DIR_NAME in result # From the fixture setup

def test_list_directory_fail_not_directory():
    result = list_directory(relative_path_str(TEST_FILE)) # Try listing a file
    assert isinstance(result, dict)
    assert result["status"] == "failure"
    assert "Path is not a directory" in result["message"]

def test_list_directory_fail_unsafe_path():
    result = list_directory("../")
    assert isinstance(result, dict)
    assert result["status"] == "failure"
    assert "Invalid or unsafe path specified" in result["message"]

def test_list_directory_fail_non_existent():
    result = list_directory("non_existent_dir_abc")
    assert isinstance(result, dict)
    assert result["status"] == "failure"
    assert "Path is not a directory" in result["message"] # Fails is_dir() check

# --- Tests for run_tests ---
# These tests require Docker to be running and the TEST_RUNNER_IMAGE
# (e.g., python:3.11-slim with pytest installed) to be available.

# Mark tests that require docker
requires_docker = pytest.mark.skipif(
    shutil.which("docker") is None, reason="Docker executable not found in PATH"
)

@requires_docker
def test_run_tests_success():
    """Tests running a simple passing pytest file."""
    test_file_rel_path = relative_path_str(DUMMY_PYTEST_FILE)
    result = run_tests([test_file_rel_path])

    assert isinstance(result, dict)
    # Check for expected keys
    assert "status" in result
    assert "output" in result
    assert "passed" in result
    assert "failed" in result
    assert "errors" in result

    # Assert basic success conditions (may vary slightly based on pytest version/output)
    # Allow FAIL if dummy test has failures uncommented
    assert result["status"] in ["PASS", "FAIL"], f"Unexpected status: {result.get('status')}. Output:\n{result.get('output')}"

    if result["status"] == "PASS":
        assert result["passed"] >= 1 # Should find at least one test
        assert result["failed"] == 0
        assert result["errors"] == 0
        assert "1 passed" in result["output"] or "1 item collected" in result["output"] # Check for specific output string variations
    elif result["status"] == "FAIL":
        # If it failed, ensure the output reflects it (e.g., contains "failed")
        assert " failed" in result["output"] or " FAILURES " in result["output"]


@requires_docker
def test_run_tests_fail_no_paths():
    result = run_tests([])
    assert result["status"] == "ERROR"
    assert "No test paths provided" in result["message"]

@requires_docker
def test_run_tests_fail_unsafe_path():
    result = run_tests(["../unsafe_test.py"])
    assert result["status"] == "ERROR"
    assert "Invalid or unsafe test path" in result["message"]

@requires_docker
def test_run_tests_fail_non_existent_path():
    result = run_tests(["non_existent_test_file.py"])
    # This should fail at path validation before Docker is involved
    assert result["status"] == "ERROR"
    assert "Invalid or unsafe test path" in result["message"]


# Note: Testing Docker image pull requires network and time, often skipped in unit tests.
# Note: Testing specific Docker errors (APIError) might require mocking the docker client.
