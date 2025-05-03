import os
import argparse
from .genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from datetime import date # Import date from datetime
from .aux_funs import create_python_file_from_string, upload_to_gcs
from .aux_vars import GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT, RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT
from pathlib import Path
import sys # Import sys for sys.exit

# Import the Google Cloud Storage library
from google.cloud import storage
# Import Blob and Bucket for uploading string data and bucket operations
from google.cloud.storage import Blob, Bucket

PROJECT_ID = os.getenv("PROJECT_ID")
DEFAULT_VERTEX_LOCATION = "us-central1"
DEFAULT_MODEL_NAME = "gemini-2.5-pro-exp-03-25"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 8048

# DEFAULT_GRAPH_SCRIPT_FILENAME = "create_graph.py" # Removed, generated dynamically
# STANDARDISED_RECIPE_FILENAME = "standardised_recipe.txt" # Removed, generated dynamically
# INITIAL_GRAPHVIZ_SOURCE = "initial_recipe_flow" # Removed, generated dynamically
# FINAL_GRAPHVIZ_SOURCE = "recipe_flow" # Removed, generated dynamically


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


def process_recipe(recipe_draft_text: str, recipe_name: str, gcs_bucket_name: str, project_id: str):
    """
    Processes a recipe draft text: converts, standardizes,
    generates initial and improved graphs, uploads outputs to GCS, and cleans up intermediate files.

    Args:
        recipe_draft_text: The raw text of the recipe draft.
        recipe_name: Base name for output files.
        gcs_bucket_name: Name of the GCS bucket to upload results.
        project_id: Google Cloud Project ID for Vertex AI calls.

    Returns:
        A dictionary containing the GCS URIs of the generated recipe text and graph PDF.

    Raises:
        ValueError: If input or configuration is invalid (empty text, name, bucket).
        RuntimeError: If AI processing, GCS operations, or graph script execution fail.
        Exception: For other unexpected errors.
    """
    # --- Input Validation ---
    if not recipe_draft_text:
        raise ValueError("Recipe draft text cannot be empty.")
    if not recipe_name:
        raise ValueError("Recipe name cannot be empty.")
    if not gcs_bucket_name:
        raise ValueError("GCS bucket name cannot be empty.")

    standardised_recipe = None
    input_source_description = "input text area" # Updated description
    # Define date string early for use in all filenames
    today_str = date.today().strftime("%Y_%m_%d")

    print(f"Processing recipe from {input_source_description}...") # Keep print for server logs

    # --- Get GCS Bucket ---
    # Moved bucket retrieval here to fail fast if bucket is invalid
    try:
        bucket = _get_gcs_bucket(gcs_bucket_name)
    except (ValueError, RuntimeError) as e:
        # Re-raise exceptions from _get_gcs_bucket to be caught by Streamlit app
        raise e

    # --- AI Processing: Draft -> Structured -> Standardized ---
    try:
        print("Converting draft to structured recipe...") # Keep print for server logs
        recipe = draft_to_recipe(
            recipe_draft=recipe_draft_text,
            system_instruction=DRAFT_TO_RECIPE_SYS_PROMPT,
            project_id=project_id,  # Use function argument
            location=DEFAULT_VERTEX_LOCATION,
            model_name=DEFAULT_MODEL_NAME
        )

        print("Standardizing structured recipe...") # Keep print for server logs
        standardised_recipe = re_write_recipe(
            recipe_input=recipe,
            input_type="txt",
            system_instruction=RE_WRITE_SYS_PROMPT,
            project_id=project_id,  # Use function argument
            location=DEFAULT_VERTEX_LOCATION,
            model_name=DEFAULT_MODEL_NAME
        )

    except Exception as e:
        # Catch errors during AI calls (draft_to_recipe, re_write_recipe)
        raise RuntimeError(f"AI processing failed during recipe standardization: {e}") from e
    # --- End AI Processing ---


    # --- Validation & Upload Standardized Recipe Text to GCS ---
    if not standardised_recipe:
        # This condition should ideally be caught by the exception handler above,
        # but kept as a safeguard.
        raise RuntimeError("Standardized recipe could not be generated (empty result).")

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
    # --- End GCS Upload ---


    # --- AI Processing: Graph Generation & Improvement ---
    first_pass_graph_code = None
    improved_graph_code = None
    try:
        print("Generating initial graph code...") # Keep print
        first_pass_graph_code = generate_graph(
            standardised_recipe=standardised_recipe,
            system_instruction=GENERATE_GRAPH_SYS_PROMPT,
            project_id=project_id,  # Use function argument
            location=DEFAULT_VERTEX_LOCATION,
            model_name=DEFAULT_MODEL_NAME
        )
        print("Initial graph code generated.") # Keep print

        # Validate that first pass code was generated before improving
        if not first_pass_graph_code:
             raise RuntimeError("Initial graph code generation returned empty result.")

        print("Improving graph code...") # Keep print
        improved_graph_code = improve_graph(
                standardised_recipe=standardised_recipe,
                graph_code=first_pass_graph_code,
                system_instruction=IMPROVE_GRAPH_SYS_PROMPT,
                project_id=project_id,  # Use function argument
                location=DEFAULT_VERTEX_LOCATION,
                model_name=DEFAULT_MODEL_NAME
        )
        print("Graph code improvement finished.") # Keep print

        # Validate that improved code was generated
        if not improved_graph_code:
             raise RuntimeError("Graph code improvement returned empty result.")

    except Exception as e:
        # Catch errors during graph generation AI calls
        raise RuntimeError(f"AI processing failed during graph generation/improvement: {e}") from e
    # --- End AI Processing: Graph ---


    # --- Execute Graph Code, Upload PDF, and Cleanup ---
    # Define dynamically generated filenames
    final_graph_base_name = f"{recipe_name}_final_{today_str}"
    final_pdf_filename = f"{final_graph_base_name}.pdf"
    final_script_name = f"{recipe_name}_final_graph_script_{today_str}.py"
    final_dot_filename = f"{final_graph_base_name}.gv" # Define .gv filename for cleanup
    final_pdf_gcs_uri = None

    # Paths for local files
    final_script_path = Path(final_script_name)
    final_pdf_path = Path(final_pdf_filename)
    final_dot_path = Path(final_dot_filename)

    try:
        # Replace default filename ('recipe_flow') in the improved code
        # Ensure the replacement uses the final base name
        improved_graph_code_final = improved_graph_code.replace("'recipe_flow'", f"'{final_graph_base_name}'")
        improved_graph_code_final = improved_graph_code_final.replace('"recipe_flow"', f'"{final_graph_base_name}"') # Handle double quotes too

        # Write the final python script locally
        create_python_file_from_string(improved_graph_code_final, filename=str(final_script_path))
        print(f"Executing final graph script: {final_script_path}") # Keep print

        # Execute the script to generate the PDF and .gv file
        # TODO: Add better error checking for os.system if possible (e.g., check return code)
        # For now, we rely on the PDF existence check below.
        exit_code = os.system(f"python {final_script_path}")
        if exit_code != 0:
             raise RuntimeError(f"Final graph script '{final_script_path}' execution failed with exit code {exit_code}.")
        print(f"Final graph script execution finished (check '{final_pdf_path}').") # Keep print

        # --- Upload final PDF to GCS ---
        if final_pdf_path.is_file():
            print(f"Uploading final PDF to GCS: gs://{gcs_bucket_name}/{final_pdf_filename}") # Keep print
            # Use the existing aux_fun for uploading files
            upload_to_gcs(gcs_bucket_name, str(final_pdf_path), final_pdf_filename)
            final_pdf_gcs_uri = f"gs://{gcs_bucket_name}/{final_pdf_filename}"
            print(f"Successfully uploaded final PDF to {final_pdf_gcs_uri}") # Keep print
        else:
            # Raise an error if PDF wasn't created by the script
            raise RuntimeError(f"Final PDF file '{final_pdf_path}' was not generated by the script.")

    except (IOError, OSError, RuntimeError, Exception) as e:
        # Catch errors during script writing, execution, or GCS upload
        raise RuntimeError(f"Failed during final graph script execution or PDF upload: {e}") from e

    finally:
        # --- Cleanup Local Files ---
        # Ensure cleanup happens even if errors occurred above
        files_to_remove = [final_script_path, final_pdf_path, final_dot_path]
        for file_path in files_to_remove:
            try:
                if file_path.exists():
                    file_path.unlink()
                    print(f"Cleaned up local file: {file_path}") # Keep print for server logs
            except OSError as e:
                 # Log cleanup warnings but don't raise fatal errors
                print(f"Warning: Could not remove local file {file_path}: {e}")
        # --- End Cleanup ---

    # --- Return GCS URIs ---
    # Ensure both URIs are set before returning
    if not standardized_recipe_gcs_uri or not final_pdf_gcs_uri:
         # This indicates an issue potentially missed by earlier checks
         raise RuntimeError("Processing completed, but failed to obtain GCS URIs for recipe or graph.")

    return {
        "recipe_uri": standardized_recipe_gcs_uri,
        "graph_uri": final_pdf_gcs_uri
    }
    # --- End Execute Graph Code, Upload PDF, and Cleanup ---


# --- Command Line Interface (Keep for potential direct use/testing) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a recipe draft text, generate files, and upload to GCS.")
    # Allow providing draft via text or file
    parser.add_argument("--recipe_draft_text", help="Text of the recipe draft.")
    parser.add_argument("--recipe_draft_file", help="Path to a file containing the recipe draft.")
    parser.add_argument("--recipe_name", default="recipe", help="Base name for output files (defaults to 'recipe').")
    parser.add_argument('--gcs_bucket', required=True, help='GCS bucket name for uploading outputs.')
    args = parser.parse_args()

    # --- Handle input source (text or file) for CLI ---
    recipe_input_text = None
    if args.recipe_draft_text:
        recipe_input_text = args.recipe_draft_text
    elif args.recipe_draft_file:
        try:
            draft_path = Path(args.recipe_draft_file)
            if not draft_path.is_file():
                 # Use sys.exit here as it's the CLI entry point
                 print(f"Error: Recipe draft file not found: {draft_path}")
                 sys.exit(1)
            with open(draft_path, "r", encoding="utf-8") as f:
                recipe_input_text = f.read()
        except IOError as e:
             print(f"Error reading file {args.recipe_draft_file}: {e}")
             sys.exit(1)
    else:
        # Require one of the inputs for CLI use
        print("Error: Please provide either --recipe_draft_text or --recipe_draft_file for CLI execution.")
        sys.exit(1)
    # --- End Handle input source ---


    try:
        # Call the main processing function, passing PROJECT_ID
        PROJECT_ID = os.getenv("PROJECT_ID")
        results = process_recipe(recipe_input_text, args.recipe_name, args.gcs_bucket, PROJECT_ID)
        # Print results for CLI execution
        print("\n--- Processing Successful ---")
        print(f"Standardized Recipe GCS URI: {results.get('recipe_uri')}")
        print(f"Final Graph PDF GCS URI: {results.get('graph_uri')}")
        print("-----------------------------")

    except (ValueError, RuntimeError, Exception) as e:
        # Catch errors raised by process_recipe or argument parsing for CLI
        print(f"\n--- Processing Failed ---")
        print(f"Error: {e}")
        print("-------------------------")
        sys.exit(1) # Exit with error code for CLI
# --- End Command Line Interface ---