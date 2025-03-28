import os
import argparse
from genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from aux_funs import create_python_file_from_string
from aux_vars import GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT, RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT



# get project ID from environment variable
PROJECT_ID = os.getenv("PROJECT_ID")
DEFAULT_VERTEX_LOCATION = "us-central1"
DEFAULT_MODEL_NAME = "gemini-2.0-pro-exp-02-05" # Verify this is the intended model
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 1.0
DEFAULT_MAX_TOKENS = 8048

if __name__ == "__main__":

    # take the recipe.txt file from args
    args = parser = argparse.ArgumentParser()
    parser.add_argument("--recipe_draft", required=False)
    #parser.add_argument("--recipe_file", required=False)
    #parser.add_argument("--youtube_url", required=False)
    args = parser.parse_args()


    recipe_draft = args.recipe_draft
    #recipe_file = args.recipe_file
    #youtube_url = args.youtube_url

    if recipe_draft:
        # import text from test_recipe.txt file
        with open(args.recipe_draft, "r") as f:
            recipe_draft = f.read()
            recipe = draft_to_recipe(recipe_draft=recipe_draft, system_instruction=DRAFT_TO_RECIPE_SYS_PROMPT, project_id=PROJECT_ID, location=DEFAULT_VERTEX_LOCATION, model_name=DEFAULT_MODEL_NAME)
            standardised_recipe = re_write_recipe(recipe_input=recipe, input_type="txt", system_instruction=RE_WRITE_SYS_PROMPT, project_id=PROJECT_ID, location=DEFAULT_VERTEX_LOCATION, model_name=DEFAULT_MODEL_NAME)


    first_pass_graph = generate_graph(standardised_recipe=standardised_recipe, system_instruction=GENERATE_GRAPH_SYS_PROMPT, project_id=PROJECT_ID, location=DEFAULT_VERTEX_LOCATION, model_name=DEFAULT_MODEL_NAME)

    create_python_file_from_string(first_pass_graph)
    os.system("python create_graph.py")
    os.system("rm create_graph.py")

    improved_graph = improve_graph(
         standardised_recipe=standardised_recipe, graph_code=first_pass_graph, system_instruction=IMPROVE_GRAPH_SYS_PROMPT, project_id=PROJECT_ID, location=DEFAULT_VERTEX_LOCATION, model_name=DEFAULT_MODEL_NAME
    )
    create_python_file_from_string(improved_graph)
    os.system("python create_graph.py")
