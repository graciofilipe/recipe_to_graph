import unittest
import os
import sys

# Get the directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory of the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

class TestMain(unittest.TestCase):
    
    def test_main_with_recipe_file(self):
        #create a test file
        with open("test_recipe.txt", "w") as f:
            f.write("This is a test recipe")

        # Call the function
        sys.argv = ["--recipe_file", "test_recipe.txt"]
        import main
        try:
            main.main()
        except SystemExit:
            pass
        os.remove("test_recipe.txt")

    def test_main_with_youtube_url(self):
        # Call the function
        sys.argv = ["--youtube_url", "https://www.youtube.com/watch?v=test"]
        import main
        try:
            main.main()
        except SystemExit:
            pass
