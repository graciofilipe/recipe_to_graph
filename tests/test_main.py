import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add project root to sys.path to allow importing main
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the function to test AFTER potentially modifying sys.path
try:
    from main import process_recipe
except ImportError as e:
    # Provide a more informative error if main cannot be imported
    raise ImportError(f"Could not import 'process_recipe' from 'main'. Original error: {e}\nMake sure main.py is in the project root: {project_root}") from e

# Mock constants and functions from external modules used in process_recipe
# We mock them globally here so they don't interfere with the specific tests unless needed
@patch('main.PROJECT_ID', 'test-project')
@patch('main.DEFAULT_VERTEX_LOCATION', 'test-location')
@patch('main.DEFAULT_MODEL_NAME', 'test-model')
@patch('main.STANDARDISED_RECIPE_FILENAME', 'test_standardised_recipe.txt')
@patch('main.DEFAULT_GRAPH_SCRIPT_FILENAME', 'test_create_graph.py')
@patch('main.INITIAL_GRAPHVIZ_SOURCE', 'test_initial_recipe_flow')
@patch('main.FINAL_GRAPHVIZ_SOURCE', 'test_recipe_flow')
@patch('main.draft_to_recipe', return_value="Mocked structured recipe")
@patch('main.re_write_recipe', return_value="Mocked standardised recipe")
@patch('main.generate_graph', return_value="mock graph code")
@patch('main.create_python_file_from_string', return_value=None)
@patch('main.os.system', return_value=0) # Mock os.system to avoid actual execution
@patch('main.improve_graph', return_value="mock improved graph code")
@patch('main.Path.unlink', return_value=None) # Mock unlink to avoid file errors
@patch('main.os.remove', return_value=None) # Mock os.remove
@patch('main.Path.is_file', return_value=True) # Assume file exists
@patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="mock recipe draft")
class TestMainVerification(unittest.TestCase):

    # These mocks are passed by the class decorator to each test method
    def test_user_approves_recipe(self, mock_open, mock_is_file, mock_os_remove, mock_unlink, mock_improve_graph, mock_os_system, mock_create_py_file, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing continues when user inputs 'yes'."""
        with patch('builtins.input', return_value='yes'), \
             patch('sys.exit') as mock_exit: # Mock sys.exit specifically for this test

            # Create a dummy recipe draft file path (doesn't need to exist due to mocks)
            dummy_draft_path = "dummy_recipe.txt"

            # Call the function under test
            process_recipe(dummy_draft_path)

            # Assertions
            mock_exit.assert_not_called() # Exit should not be called
            mock_generate_graph.assert_called_once() # Graph generation should be called
            mock_improve_graph.assert_called_once() # Graph improvement should be called

    # These mocks are passed by the class decorator to each test method
    def test_user_rejects_recipe(self, mock_open, mock_is_file, mock_os_remove, mock_unlink, mock_improve_graph, mock_os_system, mock_create_py_file, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing stops when user inputs anything other than 'yes'."""
        with patch('builtins.input', return_value='no'), \
             patch('sys.exit') as mock_exit: # Mock sys.exit specifically for this test

            # Create a dummy recipe draft file path
            dummy_draft_path = "dummy_recipe.txt"

            # Call the function under test
            process_recipe(dummy_draft_path)

            # Assertions
            mock_exit.assert_called_once_with(0) # sys.exit(0) should be called
            mock_generate_graph.assert_not_called() # Graph generation should NOT be called
            mock_improve_graph.assert_not_called() # Graph improvement should NOT be called


if __name__ == '__main__':
    unittest.main()
