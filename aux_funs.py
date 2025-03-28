import logging
from pathlib import Path # Use pathlib for path manipulation
from typing import Optional # Import Optional for type hints

# Consider setting up basic logging if needed elsewhere,
# otherwise print might be sufficient for this simple case.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define default filename as a constant
DEFAULT_FILENAME = "create_graph.py"

def create_python_file_from_string(
    code_string: Optional[str],
    filename: str = DEFAULT_FILENAME
) -> None:
    """
    Creates an executable Python file from a string containing Python code.

    Removes optional leading/trailing triple backticks (```) and the
    'python' language identifier if present.

    Args:
        code_string: A string containing the Python code. Can be None or empty.
        filename: The name of the Python file to be created.
                  Defaults to "create_graph.py".

    Raises:
        ValueError: If code_string is None or effectively empty after stripping
                    whitespace and potential formatting markers.
        IOError: If there's an issue writing to the specified file.
    """
    if not code_string:
        # Handles None and empty string cases initially
        raise ValueError("Input code string cannot be None or empty.")

    # Start processing by removing leading/trailing whitespace
    processed_code = code_string.strip()

    # Remove potential ```python ... ``` or ``` ... ``` code blocks
    if processed_code.startswith("```python"):
        # Remove ```python and strip potential whitespace around the core code
        processed_code = processed_code[9:].strip()
    elif processed_code.startswith("```"):
        # Remove ``` and strip potential whitespace around the core code
        processed_code = processed_code[3:].strip()

    # Remove potential trailing ``` after stripping the start
    if processed_code.endswith("```"):
        # Remove trailing ``` and strip potential whitespace before it
        processed_code = processed_code[:-3].strip()

    # Final check to ensure there's code left after removing formatting
    if not processed_code:
        raise ValueError("Code string is empty after removing formatting markers.")

    try:
        # Use pathlib for safer path handling
        file_path = Path(filename)
        # Use 'w' mode and specify encoding
        with file_path.open("w", encoding="utf-8") as f:
            f.write(processed_code)
        # Use logging instead of print for better practice
        logging.info(f"Successfully created Python file: {file_path}")
    except IOError as e:
        logging.error(f"Failed to write to file {filename}: {e}")
        # Re-raise the exception after logging it
        raise

# You could add example usage within a `if __name__ == "__main__":` block
# for testing purposes if desired.