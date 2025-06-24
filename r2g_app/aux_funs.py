import logging
import re # Import regular expressions module
from pathlib import Path
from typing import Optional
import os

# Import the Google Cloud Storage library
from google.cloud import storage

# Configure logger for this module
logger = logging.getLogger(__name__)
# Ensure logging is configured at the application entry point or here if standalone
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def upload_to_gcs(bucket_name: str, destination_blob_name: str, source_file_name: Optional[str] = None, source_content_string: Optional[str] = None, content_type: str = 'application/octet-stream'):
    """Uploads a file or content string to the specified Google Cloud Storage bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        destination_blob_name: The desired name of the file in the GCS bucket.
        source_file_name: The path to the local file to upload.
        source_content_string: The string content to upload.
        content_type: The content type of the string to upload. Defaults to 'application/octet-stream'.

    Raises:
        ValueError: If both source_file_name and source_content_string are provided, or if neither is provided.
        google.cloud.exceptions.NotFound: If the bucket does not exist.
        google.cloud.exceptions.Forbidden: If permission is denied to access the bucket or upload the file.
        FileNotFoundError: If the source_file_name is provided but the file does not exist locally.
        Exception: For other potential errors during the upload process.
    """
    if source_file_name and source_content_string:
        logger.error("ValueError: Provide either source_file_name or source_content_string, not both.")
        raise ValueError("Provide either source_file_name or source_content_string, not both.")
    if not source_file_name and not source_content_string:
        logger.error("ValueError: Either source_file_name or source_content_string must be provided.")
        raise ValueError("Either source_file_name or source_content_string must be provided.")

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        if source_file_name:
            logger.info(f"Uploading {source_file_name} to gs://{bucket_name}/{destination_blob_name}...")
            blob.upload_from_filename(source_file_name)
            logger.info(f"Successfully uploaded {source_file_name} to gs://{bucket_name}/{destination_blob_name}.")
        elif source_content_string:
            logger.info(f"Uploading content string to gs://{bucket_name}/{destination_blob_name}...")
            blob.upload_from_string(source_content_string, content_type=content_type)
            logger.info(f"Successfully uploaded content string to gs://{bucket_name}/{destination_blob_name}.")

    except FileNotFoundError:
        logger.error(f"Local file not found: {source_file_name}")
        raise
    except storage.exceptions.NotFound:
        logger.error(f"GCS Bucket '{bucket_name}' not found or access denied.")
        raise
    except storage.exceptions.Forbidden:
        logger.error(f"Permission denied to upload to gs://{bucket_name}/{destination_blob_name}.")
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred during GCS upload to gs://{bucket_name}/{destination_blob_name}: {e}")
        raise


# --- Updated Function: parse_code_string ---
def parse_code_string(code_string: str) -> dict:
    """
    Parses a string of code to extract HTML, CSS, and JavaScript content.
    The regex patterns are made more flexible to handle variations in AI output.
    """
    logger.debug(f"Raw AI output for parsing:\n---\n{code_string}\n---")

    # Flexible regex:
    # - Allows optional spaces around "=" and within quotes.
    # - Allows single or double quotes for filenames.
    # - Still captures content within the fenced code blocks.
    # - Handles variations in language specifier (e.g., "html", "HTML", "Html")
    html_regex = re.compile(r"```(?:html|HTML|Html)\s*filename\s*=\s*['\"]index\.html['\"]\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    css_regex = re.compile(r"```(?:css|CSS|Css)\s*filename\s*=\s*['\"]style\.css['\"]\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    js_regex = re.compile(r"```(?:javascript|JAVASCRIPT|Javascript|js|JS|Js)\s*filename\s*=\s*['\"]script\.js['\"]\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)

    html_match = html_regex.search(code_string)
    css_match = css_regex.search(code_string)
    js_match = js_regex.search(code_string)

    html_content = html_match.group(1).strip() if html_match else ""
    css_content = css_match.group(1).strip() if css_match else ""
    js_content = js_match.group(1).strip() if js_match else ""

    if not html_content:
        logger.warning("HTML content not found or could not be parsed from AI output.")
    else:
        logger.info("Successfully parsed HTML content.")
        logger.debug(f"Parsed HTML content (first 100 chars):\n{html_content[:100]}...")

    if not css_content:
        logger.warning("CSS content not found or could not be parsed from AI output.")
    else:
        logger.info("Successfully parsed CSS content.")
        logger.debug(f"Parsed CSS content (first 100 chars):\n{css_content[:100]}...")

    if not js_content:
        logger.warning("JavaScript content not found or could not be parsed from AI output.")
    else:
        logger.info("Successfully parsed JavaScript content.")
        logger.debug(f"Parsed JS content (first 100 chars):\n{js_content[:100]}...")

    # Fallback: if specific filename blocks are not found, try to find generic code blocks
    if not html_content and not css_content and not js_content:
        logger.warning("Initial parsing failed to find any specifically named code blocks. Attempting generic block parsing.")
        # Generic HTML (look for ```html then ```)
        generic_html_match = re.search(r"```html\s*\n(.*?)\n```", code_string, re.DOTALL | re.IGNORECASE)
        if generic_html_match:
            html_content = generic_html_match.group(1).strip()
            logger.info("Found generic HTML block.")

        # Generic CSS (look for ```css then ```)
        generic_css_match = re.search(r"```css\s*\n(.*?)\n```", code_string, re.DOTALL | re.IGNORECASE)
        if generic_css_match:
            css_content = generic_css_match.group(1).strip()
            logger.info("Found generic CSS block.")

        # Generic JS (look for ```javascript or ```js then ```)
        generic_js_match = re.search(r"```(?:javascript|js)\s*\n(.*?)\n```", code_string, re.DOTALL | re.IGNORECASE)
        if generic_js_match:
            js_content = generic_js_match.group(1).strip()
            logger.info("Found generic JavaScript block.")

    parsed_data = {
        "index.html": html_content,
        "style.css": css_content,
        "script.js": js_content,
    }

    if not any(parsed_data.values()):
        logger.error("Failed to parse any code content from the AI output. All fields are empty.")
    elif not all(parsed_data.values()):
        logger.warning(f"Partial parsing success: HTML {'found' if html_content else 'NOT found'}, CSS {'found' if css_content else 'NOT found'}, JS {'found' if js_content else 'NOT found'}.")

    return parsed_data


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