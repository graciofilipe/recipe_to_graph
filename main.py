from genai_funs import generate
from aux_funs import create_python_file_from_string
import os

# get project ID from environment variable
PROJECT_ID = os.getenv("PROJECT_ID")



if __name__ == "__main__":

    #import text from test_recipe.txt file
    with open("test_recipe.txt", "r") as f:
        recipe = f.read()

    python_code = generate(project_id=PROJECT_ID, recipe_text=recipe)
    create_python_file_from_string(python_code)

    #execute the python script create_graph.py
    os.system("python create_graph.py")
    