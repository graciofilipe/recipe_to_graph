import os
import argparse
from genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from datetime import date # Import date from datetime
from genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from aux_funs import create_python_file_from_string
from aux_vars import GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT, RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT
from pathlib import Path
import sys # Import sys for sys.exit

# Import the Google Cloud Storage library
from google.cloud import storage

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


def process_recipe(recipe_draft_path_str: str, recipe_name: str, gcs_bucket_name: str):
    """
    Processes a recipe draft: converts, standardizes, verifies with user,
    generates initial and improved graphs, uploads outputs to GCS, and cleans up intermediate files.

    Args:
        recipe_draft_path_str: Path to the recipe draft file.
        recipe_name: Base name for output files.

    Raises:
        FileNotFoundError: If the recipe draft file is not found.
        ValueError: If input or configuration is invalid.
        RuntimeError: If AI processing fails.
        Exception: For other unexpected errors.
    """
    standardised_recipe = None
    recipe_draft_text = None
    input_source_description = f"draft file '{recipe_draft_path_str}'"
    # Define date string early for use in all filenames
    today_str = date.today().strftime("%Y_%m_%d")


    print(f"Processing recipe from {input_source_description}...")
    draft_path = Path(recipe_draft_path_str)

    if not draft_path.is_file():
        raise FileNotFoundError(f"Recipe draft file not found: {draft_path}")

    with open(draft_path, "r", encoding="utf-8") as f:
        recipe_draft_text = f.read()

    print("Converting draft to structured recipe...")
    recipe = draft_to_recipe(
        recipe_draft=recipe_draft_text,
        system_instruction=DRAFT_TO_RECIPE_SYS_PROMPT,
        project_id=PROJECT_ID,
        location=DEFAULT_VERTEX_LOCATION,
        model_name=DEFAULT_MODEL_NAME
    )

    print("Standardizing structured recipe...")
    standardised_recipe = re_write_recipe(
        recipe_input=recipe,
        input_type="txt",
        system_instruction=RE_WRITE_SYS_PROMPT,
        project_id=PROJECT_ID,
        location=DEFAULT_VERTEX_LOCATION,
        model_name=DEFAULT_MODEL_NAME
    )

    # --- User Verification ---
    print("\n--- Standardized Recipe for Review ---")
    print(standardised_recipe)
    print("--------------------------------------\n")
    user_confirmation = input("Are you happy with the standardized recipe? (yes/no): ").lower()
    if user_confirmation != 'yes':
        print("Process aborted by user.")
        sys.exit(0)
    # --- End User Verification ---

    if standardised_recipe:
        # Generate standardized recipe filename with date
        output_recipe_filename = f"{recipe_name}_{today_str}.txt"
        try:
            output_recipe_path = Path(output_recipe_filename)
            with open(output_recipe_path, "w", encoding="utf-8") as f:
                f.write(standardised_recipe)
            print(f"Successfully wrote standardized recipe to '{output_recipe_filename}'")

            # --- Upload standardized recipe to GCS ---
            try:
                upload_to_gcs(gcs_bucket_name, str(output_recipe_path), output_recipe_filename)
                # Remove local file after successful upload
                try:
                    os.remove(output_recipe_path)
                    print(f"Removed local recipe file: {output_recipe_path}")
                except OSError as e:
                    print(f"Warning: Could not remove local file {output_recipe_path}: {e}")
            except Exception as e:
                print(f"Warning: Failed to upload {output_recipe_filename} to GCS bucket '{gcs_bucket_name}': {e}")
            # --- End GCS Upload ---

        except IOError as e:
            print(f"Warning: Could not write standardized recipe to file '{output_recipe_filename}': {e}")
            # Note: If writing fails, we don't attempt GCS upload

    else:
        print("\nError: Standardized recipe could not be generated.\n")
        sys.exit(1)


    print("Generating initial graph code...")
    first_pass_graph_code = generate_graph(
        standardised_recipe=standardised_recipe,
        system_instruction=GENERATE_GRAPH_SYS_PROMPT,
        project_id=PROJECT_ID,
        location=DEFAULT_VERTEX_LOCATION,
        model_name=DEFAULT_MODEL_NAME
    )
    print("Initial graph code generated.")

    # Define initial graph filenames and script name
    initial_graph_base_name = f"{recipe_name}_initial_{today_str}"
    initial_pdf_filename = f"{initial_graph_base_name}.pdf"
    initial_script_name = f"{recipe_name}_initial_graph_script_{today_str}.py"

    # Replace default filename in the generated initial code
    first_pass_graph_code = first_pass_graph_code.replace("'initial_recipe_flow'", f"'{initial_graph_base_name}'")
    first_pass_graph_code = first_pass_graph_code.replace('"initial_recipe_flow"', f'"{initial_graph_base_name}"')

    create_python_file_from_string(first_pass_graph_code, filename=initial_script_name)
    print(f"Executing initial graph script: {initial_script_name}")
    os.system(f"python {initial_script_name}")
    print(f"Initial graph script execution finished (check '{initial_pdf_filename}').") # Use dynamic filename

    try:
        # Clean up the dynamically named initial .gv file
        initial_dot_file_path = Path(f"{initial_graph_base_name}.gv") # Assuming .gv extension
        if initial_dot_file_path.exists():
            initial_dot_file_path.unlink()
            print(f"Cleaned up intermediate file: {initial_dot_file_path}")
    except OSError as e:
        print(f"Warning: Could not remove intermediate file {initial_dot_file_path}: {e}")

    try:
        # Clean up the dynamically named initial script file
        initial_script_path = Path(initial_script_name)
        if initial_script_path.exists():
            initial_script_path.unlink()
            print(f"Removed temporary script: {initial_script_path}")
    except OSError as e:
        print(f"Warning: Could not remove temporary script {initial_script_path}: {e}")


    print("Improving graph code...")
    improved_graph_code = improve_graph(
            standardised_recipe=standardised_recipe,
            graph_code=first_pass_graph_code,
            system_instruction=IMPROVE_GRAPH_SYS_PROMPT,
            project_id=PROJECT_ID,
            location=DEFAULT_VERTEX_LOCATION,
            model_name=DEFAULT_MODEL_NAME
    )
    print("Graph code improvement finished.")

    # Define final graph filenames using recipe_name and date
    # today_str should already be defined from standardised recipe step
    # Define final graph filenames and script name
    final_graph_base_name = f"{recipe_name}_final_{today_str}" # Added _final_ indicator
    final_pdf_filename = f"{final_graph_base_name}.pdf"
    final_script_name = f"{recipe_name}_final_graph_script_{today_str}.py"

    # Replace default filename ('recipe_flow') in the improved code
    improved_graph_code = improved_graph_code.replace("'recipe_flow'", f"'{final_graph_base_name}'")
    improved_graph_code = improved_graph_code.replace('"recipe_flow"', f'"{final_graph_base_name}"')


    create_python_file_from_string(improved_graph_code, filename=final_script_name) # Use dynamic script name
    print(f"Executing final graph script: {final_script_name}") # Use dynamic script name
    os.system(f"python {final_script_name}") # Use dynamic script name
    print(f"Final graph script execution finished (check '{final_pdf_filename}').") # Use dynamic filename

    # --- Upload final PDF to GCS ---
    try:
        # Ensure the local PDF file exists before attempting upload
        final_pdf_path = Path(final_pdf_filename)
        if final_pdf_path.is_file():
             upload_to_gcs(gcs_bucket_name, str(final_pdf_path), final_pdf_filename)
             # Remove local file after successful upload
             try:
                 os.remove(final_pdf_filename)
                 print(f"Removed local PDF file: {final_pdf_filename}")
             except OSError as e:
                 print(f"Warning: Could not remove local file {final_pdf_filename}: {e}")
        else:
            print(f"Warning: Final PDF file '{final_pdf_filename}' not found locally. Skipping GCS upload.")
    except Exception as e:
        print(f"Warning: Failed to upload {final_pdf_filename} to GCS bucket '{gcs_bucket_name}': {e}")
    # --- End GCS Upload ---

    try:
        # Clean up the dynamically named final .gv file
        final_dot_file_path = Path(f"{final_graph_base_name}.gv") # Assuming .gv extension
        if final_dot_file_path.exists():
            final_dot_file_path.unlink()
            print(f"Cleaned up intermediate file: {final_dot_file_path}")
    except OSError as e:
        print(f"Warning: Could not remove intermediate file {final_dot_file_path}: {e}")

    try:
        # Clean up the dynamically named final script file
        final_script_path = Path(final_script_name) # Use dynamic script name
        if final_script_path.exists():
            final_script_path.unlink()
            print(f"Cleaned up final temporary script: {final_script_path}")
    except OSError as e:
        print(f"Warning: Could not clean up final temporary script {final_script_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Graphviz diagram from a recipe draft.")
    parser.add_argument("--recipe_draft", required=True, help="Path to a file containing a recipe draft.")
    parser.add_argument("--recipe_name", default="recipe", help="Optional name for the recipe output files (defaults to 'recipe').")
    parser.add_argument('--gcs_bucket', required=True, help='Google Cloud Storage bucket name for uploading output files.')
    args = parser.parse_args()

    try:
        # Call the main processing function, passing the recipe name and GCS bucket
        process_recipe(args.recipe_draft, args.recipe_name, args.gcs_bucket)

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Input or configuration error - {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: AI processing failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)