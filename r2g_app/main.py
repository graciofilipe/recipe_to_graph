import os
import re # Add import for regular expressions
# Removed argparse import
from .genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
# Import constants from genai_funs
from .genai_funs import (
    PROJECT_ID, DEFAULT_VERTEX_LOCATION,
    PROCESS_TEXT_MODEL_NAME, TEXT_TO_GRAPH_MODEL_NAME,
    RECIPE_DRAFT_TEMP, RECIPE_REWRITE_TEMP, RECIPE_REVISE_TEMP,
    GRAPH_GEN_TEMP, GRAPH_IMPROVE_TEMP
)
from datetime import date # Import date from datetime
# Updated import from aux_funs
from .aux_funs import create_python_file_from_string, upload_to_gcs, parse_html_css_js_output
# Import the new prompt along with existing ones
from .aux_vars import (
    GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT,
    RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT, REVISE_RECIPE_SYS_PROMPT
)
from pathlib import Path
# Removed sys import

# Import the Google Cloud Storage library
from google.cloud import storage
# Import Blob and Bucket for uploading string data and bucket operations
from google.cloud.storage import Blob, Bucket


# DEFAULT_GRAPH_SCRIPT_FILENAME = "create_graph.py" # Removed, generated dynamically
# STANDARDISED_RECIPE_FILENAME = "standardised_recipe.txt" # Removed, generated dynamically
# INITIAL_GRAPHVIZ_SOURCE = "initial_recipe_flow" # Removed, generated dynamically
# FINAL_GRAPHVIZ_SOURCE = "recipe_flow" # Removed, generated dynamically


# --- New Function: process_text ---
def process_text(recipe_draft_text: str, project_id: str) -> str:
    """
    Processes raw recipe draft text into a standardized format using AI.

    Args:
        recipe_draft_text: The raw text of the recipe draft.
        project_id: Google Cloud Project ID for Vertex AI calls.

    Returns:
        The standardized recipe text as a string.

    Raises:
        ValueError: If input text is empty.
        RuntimeError: If AI processing fails.
    """
    # --- Input Validation ---
    if not recipe_draft_text:
        raise ValueError("Recipe draft text cannot be empty.")

    standardised_recipe = None
    print("Processing recipe text...") # Keep print for server logs

    # --- AI Processing: Draft -> Structured -> Standardized ---
    try:
        print("Converting draft to structured recipe...") # Keep print for server logs
        # Use imported constants
        recipe = draft_to_recipe(
            recipe_draft=recipe_draft_text,
            system_instruction=DRAFT_TO_RECIPE_SYS_PROMPT,
            project_id=project_id,  # Pass explicitly
            location=DEFAULT_VERTEX_LOCATION, # Use imported constant
            model_name=PROCESS_TEXT_MODEL_NAME, # Use imported constant
            temperature=RECIPE_DRAFT_TEMP # Use imported constant
        )

        print("Standardizing structured recipe...") # Keep print for server logs
        # Use imported constants
        standardised_recipe = re_write_recipe(
            recipe_input=recipe,
            input_type="txt",
            system_instruction=RE_WRITE_SYS_PROMPT,
            project_id=project_id,  # Pass explicitly
            location=DEFAULT_VERTEX_LOCATION, # Use imported constant
            model_name=PROCESS_TEXT_MODEL_NAME, # Use imported constant
            temperature=RECIPE_REWRITE_TEMP # Use imported constant
        )

    except Exception as e:
        # Catch errors during AI calls (draft_to_recipe, re_write_recipe)
        raise RuntimeError(f"AI processing failed during recipe standardization: {e}") from e

    # --- Validation ---
    if not standardised_recipe:
        # This condition should ideally be caught by the exception handler above,
        # but kept as a safeguard.
        raise RuntimeError("Standardized recipe could not be generated (empty result).")

    print("Recipe text processing finished.")
    return standardised_recipe
# --- End process_text ---


# Function to get GCS bucket (moved outside process_recipe for clarity)
def _get_gcs_bucket(bucket_name: str) -> Bucket:
    """Gets the GCS bucket object."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
             # Basic check, more robust checks might be needed (e.g., permissions)
            raise ValueError(f"GCS Bucket '{bucket_name}' not found or accessible.")
        return bucket
    except Exception as e:
        raise RuntimeError(f"Failed to access GCS bucket '{bucket_name}': {e}")


# --- New Function: text_to_graph ---
def text_to_graph(standardised_recipe: str, recipe_name: str, gcs_bucket_name: str, project_id: str) -> dict:
    """
    Generates a graph from standardized recipe text, uploads recipe text and graph PDF to GCS,
    and cleans up intermediate files.

    Args:
        standardised_recipe: The standardized recipe text.
        recipe_name: Base name for output files.
        gcs_bucket_name: Name of the GCS bucket to upload results.
        project_id: Google Cloud Project ID for Vertex AI calls.

    Returns:
        A dictionary containing the GCS URIs of the generated recipe text and graph PDF.

    Raises:
        ValueError: If input or configuration is invalid (empty text, name, bucket).
        RuntimeError: If GCS operations, AI graph generation, or graph script execution fail.
        Exception: For other unexpected errors.
    """
    # --- Input Validation ---
    if not standardised_recipe:
        raise ValueError("Standardized recipe text cannot be empty.")
    if not recipe_name:
        raise ValueError("Recipe name cannot be empty.")
    if not gcs_bucket_name:
        raise ValueError("GCS bucket name cannot be empty.")

    # Define date string early for use in all filenames
    today_str = date.today().strftime("%Y_%m_%d")
    print("Processing standardized recipe for graph generation and GCS upload...")

    # --- Get GCS Bucket ---
    try:
        bucket = _get_gcs_bucket(gcs_bucket_name)
    except (ValueError, RuntimeError) as e:
        # Re-raise exceptions from _get_gcs_bucket
        raise e

    # --- Upload Standardized Recipe Text to GCS (Moved to the beginning) ---
    output_recipe_filename = f"{recipe_name}_{today_str}.txt"
    standardized_recipe_gcs_uri = None
    try:
        print(f"Uploading standardized recipe to GCS: gs://{gcs_bucket_name}/{output_recipe_filename}") # Keep print
        blob = bucket.blob(output_recipe_filename)
        # Upload directly from string
        blob.upload_from_string(standardised_recipe, content_type='text/plain; charset=utf-8') # Specify encoding
        standardized_recipe_gcs_uri = f"gs://{gcs_bucket_name}/{output_recipe_filename}"
        print(f"Successfully uploaded standardized recipe to {standardized_recipe_gcs_uri}") # Keep print

    except Exception as e:
         # Use raise instead of print/sys.exit; includes GCS errors
        raise RuntimeError(f"Failed to upload standardized recipe to GCS bucket '{gcs_bucket_name}': {e}") from e
    # --- End Upload Standardized Recipe Text to GCS ---


    # --- AI Processing: Graph Generation & Improvement ---
    first_pass_graph_code = None
    improved_graph_code = None
    try:
        print("Generating initial graph code...") # Keep print
        # Use imported constants
        first_pass_graph_code = generate_graph(
            standardised_recipe=standardised_recipe,
            system_instruction=GENERATE_GRAPH_SYS_PROMPT,
            project_id=project_id,  # Pass explicitly
            location=DEFAULT_VERTEX_LOCATION, # Use imported constant
            model_name=TEXT_TO_GRAPH_MODEL_NAME, # Use imported constant
            temperature=GRAPH_GEN_TEMP # Use imported constant
        )
        print("Initial graph code generated.") # Keep print

        # Validate that first pass code was generated before improving
        if not first_pass_graph_code:
             raise RuntimeError("Initial graph code generation returned empty result.")

        print("Improving graph code...") # Keep print
        # Use imported constants
        improved_graph_code = improve_graph(
                standardised_recipe=standardised_recipe,
                graph_code=first_pass_graph_code,
                system_instruction=IMPROVE_GRAPH_SYS_PROMPT,
                project_id=project_id,  # Pass explicitly
                location=DEFAULT_VERTEX_LOCATION, # Use imported constant
                model_name=TEXT_TO_GRAPH_MODEL_NAME, # Use imported constant
                temperature=GRAPH_IMPROVE_TEMP # Use imported constant
        )
        print("Graph code improvement finished.") # Keep print

        # Validate that improved code was generated
        if not improved_graph_code:
             raise RuntimeError("Graph code improvement returned empty result.")

    except Exception as e:
        # Catch errors during graph generation AI calls
        raise RuntimeError(f"AI processing failed during graph generation/improvement: {e}") from e
    # --- End AI Processing: Graph ---


    # --- Process Improved Graph Code ---
    # Call the imported function
    parsed_content = parse_html_css_js_output(improved_graph_code)
    html_content = parsed_content.get("html", "")
    css_content = parsed_content.get("css", "")
    js_content = parsed_content.get("js", "")

    if not html_content:
        # Or handle this more gracefully depending on requirements
        raise RuntimeError("HTML content could not be parsed from improved_graph_code.")

    # --- Define Local Filenames ---
    base_filename = f"{recipe_name}_{today_str}"
    html_filename = f"{base_filename}_index.html"
    css_filename = f"{base_filename}_style.css"
    js_filename = f"{base_filename}_script.js"

    html_file_path = Path(html_filename)
    css_file_path = Path(css_filename)
    js_file_path = Path(js_filename)

    # --- Write Content to Local Files ---
    try:
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Successfully wrote HTML to {html_file_path}")

        if css_content: # Only write if CSS content exists
            with open(css_file_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            print(f"Successfully wrote CSS to {css_file_path}")
        else:
            print(f"No CSS content to write for {css_filename}")


        if js_content: # Only write if JS content exists
            with open(js_file_path, "w", encoding="utf-8") as f:
                f.write(js_content)
            print(f"Successfully wrote JavaScript to {js_file_path}")
        else:
            print(f"No JavaScript content to write for {js_filename}")

    except IOError as e:
        raise RuntimeError(f"Failed to write graph content to local files: {e}") from e

    # --- TODO: Upload HTML, CSS, JS to GCS (or handle as needed) ---
    # This will be handled in a subsequent step.
    # For now, the files are written locally.

    # --- Cleanup Logic (Marked for Update) ---
    # Add new files to cleanup list
    # The old cleanup logic for .py, .pdf, .gv files is no longer directly applicable.
    # This section needs to be revised based on what files (if any) are
    # created and need cleanup in the new workflow.

    files_to_remove_later = [html_file_path, css_file_path, js_file_path]
    # The actual removal will happen in the finally block, which needs to be added/updated.

    # --- Return Values (Needs Update) ---
    # The return signature needs to be updated to reflect the new outputs.
    # 'graph_uri' might now point to an HTML file in GCS, or be removed if content is returned directly.
    # 'pdf_content' is no longer relevant as we are not generating a PDF in this function.

    if not standardized_recipe_gcs_uri:
         raise RuntimeError("Standardized recipe GCS URI not found.")

    # For now, we will return the local paths and content.
    # The GCS upload and URI generation will be handled in the next steps.
    # The 'pdf_content' key is replaced by 'html_content' for the main displayable output.
    # 'graph_uri' will temporarily hold the local HTML file path.
    # This will be updated once GCS upload for HTML file is implemented.

    # Read HTML content as bytes for consistency with previous 'pdf_content' if needed by caller
    # This is a temporary measure. Ideally, the caller adapts to string HTML content.
    html_content_bytes = None
    try:
        if html_file_path.exists():
            html_content_bytes = html_file_path.read_bytes()
    except IOError as e:
        print(f"Warning: Could not read back HTML file for byte content: {e}")


    # --- Return GCS URIs and Local File Info ---
    # Ensure standardized_recipe_gcs_uri is set (from earlier in the function)
    if not standardized_recipe_gcs_uri:
         raise RuntimeError("Processing completed, but failed to obtain GCS URI for recipe text.")

    # The following return structure is temporary and will be finalized
    # once GCS upload for HTML/CSS/JS is implemented.
    # 'graph_uri' will eventually be the GCS URI of the main HTML file.
    # 'pdf_content' is being phased out, using 'html_content_bytes' as a temporary substitute.
    return {
        "recipe_uri": standardized_recipe_gcs_uri,
        "graph_uri": str(html_file_path), # Placeholder: local path, to be GCS URI
        "pdf_content": html_content_bytes, # Placeholder: local HTML bytes, to be actual HTML content or URI
        "html_content": html_content,
        "css_content": css_content,
        "js_content": js_content,
        "local_html_path": str(html_file_path),
        "local_css_path": str(css_file_path) if css_content else None,
        "local_js_path": str(js_file_path) if js_content else None,
    }
# --- End text_to_graph ---

# --- Helper function _parse_improved_graph_output removed ---
# It has been moved to r2g_app/aux_funs.py and renamed to parse_html_css_js_output

# --- Duplicated text_to_graph function (and its content) also removed ---

# --- New Function: revise_recipe ---
def revise_recipe(original_draft: str, current_standardised_recipe: str, user_feedback: str, project_id: str) -> str:
    '''
    Revises a standardized recipe based on user feedback using an AI model.

    Args:
        original_draft: The initial recipe draft (for context).
        current_standardised_recipe: The recipe version the user reviewed.
        user_feedback: The changes requested by the user.
        project_id: Google Cloud Project ID.

    Returns:
        The revised standardized recipe text.

    Raises:
        RuntimeError: If AI revision fails.
    '''
    print("Revising recipe based on user feedback...") # Keep print for server logs

    # Construct input text for the AI model
    # Consider if original_draft is needed contextually. If prompts handle revision well without it, it can be omitted.
    # Let's include it for now for better context.
    input_text = f"""
User Feedback:
---
{user_feedback}
---

Current Standardized Recipe:
---
{current_standardised_recipe}
---

Original Recipe Draft (for context):
---
{original_draft}
---

Based *only* on the User Feedback provided above, please revise the Current Standardized Recipe. Maintain the exact same structure and formatting rules as the Current Standardized Recipe. Output *only* the full, revised standardized recipe text.
"""

    try:
        # Assuming DEFAULT_VERTEX_LOCATION and DEFAULT_MODEL_NAME are accessible
        # If not, ensure they are imported or passed correctly.
        # Check if these constants exist in the scope of main.py, if not import from aux_vars
        revised_text = re_write_recipe(
            recipe_input=input_text,
            input_type="txt",
            system_instruction=REVISE_RECIPE_SYS_PROMPT, # Use the new prompt
            project_id=project_id, # Pass explicitly
            location=DEFAULT_VERTEX_LOCATION, # Use imported constant
            model_name=PROCESS_TEXT_MODEL_NAME, # Use imported constant
            temperature=RECIPE_REVISE_TEMP # Use imported constant
        )
        if not revised_text:
            raise RuntimeError("AI revision returned an empty result.")

        print("Recipe revision finished.") # Keep print for server logs
        return revised_text

    except Exception as e:
        print(f"Error during recipe revision: {e}") # Keep print for server logs
        # Re-raise the exception to be caught by the Streamlit app
        raise RuntimeError(f"AI processing failed during recipe revision: {e}") from e
# --- End revise_recipe ---


# --- Removed Command Line Interface ---