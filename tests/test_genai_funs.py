import unittest
import os
import sys
from genai_funs import re_write_recipe, generate_graph, improve_graph

PROJECT_ID = os.getenv("PROJECT_ID")

# Get the directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory of the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

class TestGenAIFuns(unittest.TestCase):
    
    def test_re_write_recipe(self):
        # Call the function with a dummy recipe
        recipe = "This is a test recipe"
        # Call the function
        result = re_write_recipe(project_id=PROJECT_ID, recipe=recipe, input_type="txt", si_text="test_prompt")
        # Check if the result is a non empty string
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")
        
    def test_generate_graph(self):
        # Call the function with a dummy recipe
        recipe = "This is a test recipe"
        # Call the function
        result = generate_graph(project_id=PROJECT_ID, recipe=recipe, si_text="test_prompt")
        # Check if the result is a non empty string
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_improve_graph(self):
        # Call the function with a dummy recipe
        recipe = "This is a test recipe"
        graph_code = "graph code"
        # Call the function
        result = improve_graph(project_id=PROJECT_ID, recipe=recipe, graph_code=graph_code, si_text="test_prompt")
        # Check if the result is a non empty string
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")
