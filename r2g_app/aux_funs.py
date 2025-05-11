import logging
import re # Import regular expressions module
from pathlib import Path
from typing import Optional
import os

# Import the Google Cloud Storage library
from google.cloud import storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#DEFAULT_FILENAME = "create_graph.py"

# def create_python_file_from_string(
#     code_string: Optional[str],
#     filename: str = DEFAULT_FILENAME
# ) -> None:
#     """
#     Creates an executable Python file from a string containing Python code.

#     Removes optional leading/trailing triple backticks (```) and the
#     'python' language identifier if present.

#     Args:
#         code_string: A string containing the Python code. Can be None or empty.
#         filename: The name of the Python file to be created.
#                   Defaults to "create_graph.py".

#     Raises:
#         ValueError: If code_string is None or effectively empty after stripping
#                     whitespace and potential formatting markers.
#         IOError: If there's an issue writing to the specified file.
#     """
#     if not code_string:
#         # Handles None and empty string cases initially
#         raise ValueError("Input code string cannot be None or empty.")

#     # Start processing by removing leading/trailing whitespace
#     processed_code = code_string.strip()

#     # Remove potential ```python ... ``` or ``` ... ``` code blocks
#     if processed_code.startswith("```python"):
#         # Remove ```python and strip potential whitespace around the core code
#         processed_code = processed_code[9:].strip()
#     elif processed_code.startswith("```"):
#         # Remove ``` and strip potential whitespace around the core code
#         processed_code = processed_code[3:].strip()

#     # Remove potential trailing ``` after stripping the start
#     if processed_code.endswith("```"):
#         # Remove trailing ``` and strip potential whitespace before it
#         processed_code = processed_code[:-3].strip()

#     # Final check to ensure there's code left after removing formatting
#     if not processed_code:
#         raise ValueError("Code string is empty after removing formatting markers.")

#     try:
#         # Use pathlib for safer path handling
#         file_path = Path(filename)
#         # Use 'w' mode and specify encoding
#         with file_path.open("w", encoding="utf-8") as f:
#             f.write(processed_code)
#         logging.info(f"Successfully created Python file: {file_path}")
#     except IOError as e:
#         logging.error(f"Failed to write to file {filename}: {e}")
#         raise


def upload_to_gcs(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Uploads a file to the specified Google Cloud Storage bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        source_file_name: The path to the local file to upload.
        destination_blob_name: The desired name of the file in the GCS bucket.

    Raises:
        google.cloud.exceptions.NotFound: If the bucket does not exist.
        google.cloud.exceptions.Forbidden: If permission is denied to access the bucket or upload the file.
        FileNotFoundError: If the source file does not exist locally.
        Exception: For other potential errors during the upload process.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        print(f"Uploading {source_file_name} to gs://{bucket_name}/{destination_blob_name}...")
        blob.upload_from_filename(source_file_name)
        print(f"Successfully uploaded {source_file_name} to gs://{bucket_name}/{destination_blob_name}.")

    except FileNotFoundError:
        print(f"Error: Local file not found: {source_file_name}")
        # Re-raise the exception to potentially handle it further up the call stack
        raise
    except storage.blob.exceptions.NotFound:
        print(f"Error: Bucket '{bucket_name}' not found or you don't have access.")
        raise
    except storage.blob.exceptions.Forbidden:
        print(f"Error: Permission denied to upload to gs://{bucket_name}/{destination_blob_name}.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during GCS upload: {e}")
        raise


# --- New Function: parse_html_css_js_output ---
def parse_code_string(code_string: str):
    """
    Parses a string of code to extract HTML, CSS, and JavaScript content.
    """
    html_regex = re.compile(r'```html filename="index\.html"(.*?)```', re.DOTALL)
    css_regex = re.compile(r'```css filename="style\.css"(.*?)```', re.DOTALL)
    js_regex = re.compile(r'```javascript filename="script\.js"(.*?)```', re.DOTALL)

    html_match = html_regex.search(code_string)
    css_match = css_regex.search(code_string)
    js_match = js_regex.search(code_string)

    html_content = html_match.group(1).strip() if html_match else ""
    css_content = css_match.group(1).strip() if css_match else ""
    js_content = js_match.group(1).strip() if js_match else ""

    return {
    "index.html": html_content,
    "style.css": css_content,
    "script.js": js_content,
    }


def save_files(parsed_content: dict, output_directory: str = "."):
    """
    Saves the parsed code content into files.
    """
    import os
    os.makedirs(output_directory, exist_ok=True)
    for filename, content in parsed_content.items():
    filepath = os.path.join(output_directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saving {filename} to {filepath}")