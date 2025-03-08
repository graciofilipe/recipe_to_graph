import os
import argparse
from genai_funs import generate_graph, re_write_recipe, improve_graph, draft_to_recipe
from aux_funs import create_python_file_from_string
from aux_vars import GENERATE_GRAPH_SYS_PROMPT, IMPROVE_GRAPH_SYS_PROMPT, RE_WRITE_SYS_PROMPT, DRAFT_TO_RECIPE_SYS_PROMPT



# get project ID from environment variable
PROJECT_ID = os.getenv("PROJECT_ID")


if __name__ == "__main__":

    # take the recipe.txt file from args
    args = parser = argparse.ArgumentParser()
    parser.add_argument("--recipe_draft", required=False)
    parser.add_argument("--recipe_file", required=False)
    parser.add_argument("--youtube_url", required=False)
    args = parser.parse_args()


    recipe_draft = args.recipe_draft
    recipe_file = args.recipe_file
    youtube_url = args.youtube_url

    if recipe_draft:
        # import text from test_recipe.txt file
        with open(args.recipe_draft, "r") as f:
            recipe_draft = f.read()
            recipe = draft_to_recipe(project_id=PROJECT_ID, recipe=recipe_draft, si_text=DRAFT_TO_RECIPE_SYS_PROMPT)
            standardised_recipe = re_write_recipe(project_id=PROJECT_ID, recipe=recipe, input_type="txt", si_text=RE_WRITE_SYS_PROMPT
        )

    if recipe_file:
        # import text from test_recipe.txt file
        with open(args.recipe_file, "r") as f:
            pre_recipe = f.read()
        standardised_recipe = re_write_recipe(
            project_id=PROJECT_ID, recipe=pre_recipe, input_type="txt", si_text=RE_WRITE_SYS_PROMPT
        )

    elif youtube_url:
        recipe = youtube_url
        standardised_recipe = re_write_recipe(
            project_id=PROJECT_ID, recipe=youtube_url, input_type="youtube", si_text=RE_WRITE_SYS_PROMPT
        )

    ## With the standardised-recipe
    first_pass_graph = generate_graph(project_id=PROJECT_ID, recipe=standardised_recipe, si_text=GENERATE_GRAPH_SYS_PROMPT
    )
    create_python_file_from_string(first_pass_graph)
    os.system("python create_graph.py")
    os.system("rm create_graph.py")

    improved_graph = improve_graph(
        project_id=PROJECT_ID, recipe=standardised_recipe, graph_code=first_pass_graph, si_text=IMPROVE_GRAPH_SYS_PROMPT
    )
    create_python_file_from_string(improved_graph)
    os.system("python create_graph.py")
