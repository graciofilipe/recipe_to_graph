import os
import argparse
# Assuming genai_funs and aux_funs are using the signatures from the provided context
from genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from aux_funs import create_python_file_from_string
from aux_vars import GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT, RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT
from pathlib import Path # Import Path


# --- Configuration (Consider moving to a config file or constants module) ---
# get project ID from environment variable
PROJECT_ID = os.getenv("PROJECT_ID")
DEFAULT_VERTEX_LOCATION = "us-central1"
# Using the model name from the context
DEFAULT_MODEL_NAME = "gemini-2.0-pro-exp-02-05"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 8048

# Define the name for the temporary script and output recipe file
DEFAULT_GRAPH_SCRIPT_FILENAME = "create_graph.py"
STANDARDISED_RECIPE_FILENAME = "standardised_recipe.txt" # Filename for output
# Define names for the intermediate Graphviz source files (without extension)
INITIAL_GRAPHVIZ_SOURCE = "initial_recipe_flow"
FINAL_GRAPHVIZ_SOURCE = "recipe_flow"


if __name__ == "__main__":

    # --- Argument Parsing ---
    # Basic argparse setup from context
    parser = argparse.ArgumentParser(description="Generate a Graphviz diagram from a recipe draft.")
    # Only recipe_draft is active based on context
    parser.add_argument("--recipe_draft", required=True, help="Path to a file containing a recipe draft.")
    # parser.add_argument("--recipe_file", required=False)
    # parser.add_argument("--youtube_url", required=False)
    args = parser.parse_args()

    # --- Variable Initialization ---
    standardised_recipe = None
    recipe_draft_text = None
    input_source_description = ""

    # --- Main Logic ---
    # Basic error handling added for file operations and checking results
    try:
        if args.recipe_draft:
            input_source_description = f"draft file '{args.recipe_draft}'"
            print(f"Processing recipe from {input_source_description}...")
            draft_path = Path(args.recipe_draft) # Use Path for file check

            if not draft_path.is_file():
                 raise FileNotFoundError(f"Recipe draft file not found: {draft_path}")

            # Read the draft file
            with open(args.recipe_draft, "r", encoding="utf-8") as f:
                recipe_draft_text = f.read()

            # Convert draft to structured recipe
            print("Converting draft to structured recipe...")
            recipe = draft_to_recipe(
                recipe_draft=recipe_draft_text,
                system_instruction=DRAFT_TO_RECIPE_SYS_PROMPT,
                project_id=PROJECT_ID,
                location=DEFAULT_VERTEX_LOCATION,
                model_name=DEFAULT_MODEL_NAME
            )

            # Standardize the structured recipe
            print("Standardizing structured recipe...")
            standardised_recipe = re_write_recipe(
                recipe_input=recipe,
                input_type="txt",
                system_instruction=RE_WRITE_SYS_PROMPT,
                project_id=PROJECT_ID,
                location=DEFAULT_VERTEX_LOCATION,
                model_name=DEFAULT_MODEL_NAME
            )

            # --- Process standardized recipe ---
            if standardised_recipe: # Check if it was successfully created
                # --- REMOVED: Print standardized recipe to screen ---

                # --- Write standardized recipe to file ---
                try:
                    output_recipe_path = Path(STANDARDISED_RECIPE_FILENAME)
                    with open(output_recipe_path, "w", encoding="utf-8") as f:
                        f.write(standardised_recipe)
                    print(f"Successfully wrote standardized recipe to '{STANDARDISED_RECIPE_FILENAME}'")
                except IOError as e:
                    # Log a warning but continue execution
                    print(f"Warning: Could not write standardized recipe to file '{STANDARDISED_RECIPE_FILENAME}': {e}")
                # --- END Write section ---

            else:
                # Handle case where standardization failed
                print("\nError: Standardized recipe could not be generated.\n")
                exit(1) # Exit if standardization failed

        else:
             # This part shouldn't be reached if --recipe_draft is required
             print("Error: No recipe input provided.")
             exit(1)


        # --- Generate Initial Graph ---
        print("Generating initial graph code...")
        first_pass_graph_code = generate_graph(
            standardised_recipe=standardised_recipe,
            system_instruction=GENERATE_GRAPH_SYS_PROMPT,
            project_id=PROJECT_ID,
            location=DEFAULT_VERTEX_LOCATION,
            model_name=DEFAULT_MODEL_NAME
        )
        print("Initial graph code generated.")

        # --- Create and Execute Initial Graph Script ---
        temp_script_name = DEFAULT_GRAPH_SCRIPT_FILENAME
        create_python_file_from_string(first_pass_graph_code, filename=temp_script_name)
        print(f"Executing initial graph script: {temp_script_name}")
        # WARNING: os.system is generally discouraged. Consider subprocess.
        # The prompt for Agent-2 asks it to include rendering to 'initial_recipe_flow.pdf'
        os.system(f"python {temp_script_name}")
        print("Initial graph script execution finished (check 'initial_recipe_flow.pdf').")

        # --- Clean up initial intermediate dot file ---
        try:
            initial_dot_file_path = Path(INITIAL_GRAPHVIZ_SOURCE)
            if initial_dot_file_path.exists():
                initial_dot_file_path.unlink() # Use unlink for Path objects
                print(f"Cleaned up intermediate file: {initial_dot_file_path}")
        except OSError as e:
            print(f"Warning: Could not remove intermediate file {initial_dot_file_path}: {e}")
        # --- END Clean up ---

        # --- Remove Initial Script ---
        # This was in the original context, kept here but be aware it removes the script
        # before the improve step uses the *code string* (first_pass_graph_code)
        try:
            os.remove(temp_script_name)
            print(f"Removed temporary script: {temp_script_name}")
        except OSError as e:
            print(f"Warning: Could not remove temporary script {temp_script_name}: {e}")


        # --- Improve Graph ---
        print("Improving graph code...")
        improved_graph_code = improve_graph(
             standardised_recipe=standardised_recipe,
             graph_code=first_pass_graph_code, # Pass the code string
             system_instruction=IMPROVE_GRAPH_SYS_PROMPT,
             project_id=PROJECT_ID,
             location=DEFAULT_VERTEX_LOCATION,
             model_name=DEFAULT_MODEL_NAME
        )
        print("Graph code improvement finished.")

        # --- Create and Execute Final Graph Script ---
        create_python_file_from_string(improved_graph_code, filename=temp_script_name) # Overwrite/create script
        print(f"Executing final graph script: {temp_script_name}")
        # The prompt for Agent-3 asks it to include rendering to 'recipe_flow.pdf'
        os.system(f"python {temp_script_name}")
        print("Final graph script execution finished (check 'recipe_flow.pdf').")

        # --- Clean up final intermediate dot file ---
        try:
            final_dot_file_path = Path(FINAL_GRAPHVIZ_SOURCE)
            if final_dot_file_path.exists():
                final_dot_file_path.unlink() # Use unlink for Path objects
                print(f"Cleaned up intermediate file: {final_dot_file_path}")
        except OSError as e:
            print(f"Warning: Could not remove intermediate file {final_dot_file_path}: {e}")
        # --- END Clean up ---


        #--- Final Cleanup (Python Script) ---
        # Clean up the temporary python script itself
        try:
            temp_script_path = Path(temp_script_name)
            if temp_script_path.exists():
                temp_script_path.unlink()
                print(f"Cleaned up final temporary script: {temp_script_path}")
        except OSError as e:
            print(f"Warning: Could not clean up final temporary script {temp_script_path}: {e}")

    except FileNotFoundError as e:
        print(f"Error: Input file not found - {e}")
        exit(1)
    except ValueError as e: # Catch errors from genai_funs/aux_funs
        print(f"Error: Input or configuration error - {e}")
        exit(1)
    except RuntimeError as e: # Catch errors from genai_funs API calls
        print(f"Error: AI processing failed - {e}")
        exit(1)
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        # Consider logging the traceback here for debugging
        # import traceback
        # traceback.print_exc()
        exit(1)

    print("\nProcess completed.")
