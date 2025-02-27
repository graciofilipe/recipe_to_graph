from genai_funs import generate_graph, re_write_recipe, improve_graph
from aux_funs import create_python_file_from_string
import os
import argparse

# get project ID from environment variable
PROJECT_ID = os.getenv("PROJECT_ID")



if __name__ == "__main__":

    # take the recipe.txt file from args
    args = parser = argparse.ArgumentParser()
    parser.add_argument("--recipe_file", required=False)
    parser.add_argument("--youtube_url", required=False)
    args = parser.parse_args()

    recipe_file = args.recipe_file
    youtube_url = args.youtube_url

    if recipe_file:
        #import text from test_recipe.txt file
        with open(args.recipe_file, "r") as f:
            pre_recipe = f.read()
        recipe = re_write_recipe(project_id=PROJECT_ID, recipe=pre_recipe, input_type="txt")


    elif youtube_url:
        recipe = youtube_url
        recipe = re_write_recipe(project_id=PROJECT_ID, recipe=youtube_url, input_type="youtube")

    first_pass_graph = generate_graph(project_id=PROJECT_ID, recipe=recipe)
    create_python_file_from_string(first_pass_graph)
    os.system("python create_graph.py")
    os.system("rm create_graph.py")

    improved_graph = improve_graph(project_id=PROJECT_ID, recipe=recipe, graph_code=first_pass_graph)
    create_python_file_from_string(improved_graph)
    os.system("python create_graph.py")


    