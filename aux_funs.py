def create_python_file_from_string(code_string, filename="create_graph.py"):
    """
    Creates an executable Python file from a string containing Python code.

    Args:
        code_string: A string containing the Python code, potentially including
                     triple backticks (```) to denote a code block.
        filename: The name of the Python file to be created (defaults to "output.py").
    """

    if not code_string:
        raise ValueError("The code string cannot be empty.")

    # Remove leading/trailing whitespace and code block markers
    code_string = code_string.strip()
    if code_string.startswith("```python"):
        code_string = code_string[9:]  # Remove "```python"
    elif code_string.startswith("```"):  # Handle cases without "python" after backticks
        code_string = code_string[3:]
    if code_string.endswith("```"):
        code_string = code_string[:-3]

    code_string = code_string.strip() # Remove any leading/trailing newlines *after* removing backticks

    with open(filename, "w") as f:
        f.write(code_string)
    print(f"Successfully created Python file: {filename}")