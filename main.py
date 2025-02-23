from genai_funs import generate
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
        input_type = "txt"
        #import text from test_recipe.txt file
        with open(args.recipe_file, "r") as f:
            recipe = f.read()

    elif youtube_url:
        input_type = "youtube"
        recipe = youtube_url

    
    python_code = generate(project_id=PROJECT_ID, recipe=recipe, input_type=input_type)
    create_python_file_from_string(python_code)

    #execute the python script create_graph.py
    os.system("python create_graph.py")
    