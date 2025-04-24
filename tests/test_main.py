import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
from pathlib import Path
from datetime import date # Add date import

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
# Remove patches for constants that no longer exist in main.py
@patch('main.PROJECT_ID', 'test-project')
@patch('main.DEFAULT_VERTEX_LOCATION', 'test-location')
@patch('main.DEFAULT_MODEL_NAME', 'test-model')
# @patch('main.STANDARDISED_RECIPE_FILENAME', 'test_standardised_recipe.txt') # Removed
# @patch('main.DEFAULT_GRAPH_SCRIPT_FILENAME', 'test_create_graph.py') # Removed
# @patch('main.INITIAL_GRAPHVIZ_SOURCE', 'test_initial_recipe_flow') # Removed
# @patch('main.FINAL_GRAPHVIZ_SOURCE', 'test_recipe_flow') # Removed
@patch('main.draft_to_recipe', return_value="Mocked structured recipe")
@patch('main.re_write_recipe', return_value="Mocked standardised recipe")
# Provide mock return values that include the placeholders the main code expects to replace
@patch('main.generate_graph', return_value="graph = Digraph('initial_recipe_flow')\n# Other graph code")
@patch('main.improve_graph', return_value="graph = Digraph('recipe_flow')\n# Improved graph code")
@patch('main.os.system', return_value=0) # Mock os.system to avoid actual execution
@patch('main.Path.is_file', return_value=True) # Assume draft file exists
class TestMainFunctionality(unittest.TestCase): # Renamed class for clarity

    # Mocks passed by class decorator are now fewer
    def test_user_approves_recipe(self, mock_is_file, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing continues when user inputs 'yes'."""
        # Mock file operations and system calls locally for this test
        with patch('builtins.input', return_value='yes'), \
             patch('sys.exit') as mock_exit, \
             patch('main.create_python_file_from_string') as mock_create_py_file, \
             patch('main.Path.unlink') as mock_unlink, \
             patch('main.os.remove') as mock_os_remove, \
             patch('builtins.open', unittest.mock.mock_open(read_data="mock recipe draft")): # Mock open for reading draft

            # Call the function under test (using default recipe name "recipe")
            process_recipe("dummy_recipe.txt", "recipe") # Pass recipe_name

            # Assertions
            mock_exit.assert_not_called() # Exit should not be called
            mock_generate_graph.assert_called_once() # Graph generation should be called
            mock_improve_graph.assert_called_once() # Graph improvement should be called
            self.assertTrue(mock_create_py_file.called) # Check if script creation was attempted
            self.assertTrue(mock_os_system.called) # Check if os.system was called

    # Mocks passed by class decorator
    def test_user_rejects_recipe(self, mock_is_file, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing stops when user inputs anything other than 'yes'."""
        with patch('builtins.input', return_value='no'), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.open', unittest.mock.mock_open(read_data="mock recipe draft")): # Mock open for reading draft

            # Call the function under test
            process_recipe("dummy_recipe.txt", "recipe") # Pass recipe_name

            # Assertions
            mock_exit.assert_called_once_with(0) # sys.exit(0) should be called
            mock_generate_graph.assert_not_called() # Graph generation should NOT be called
            mock_improve_graph.assert_not_called() # Graph improvement should NOT be called

    # Mocks passed by class decorator
    def test_dynamic_filenames(self, mock_is_file, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that filenames are generated dynamically based on recipe_name and date."""
        test_recipe_name = "my_dynamic_recipe"
        today_str = date.today().strftime("%Y_%m_%d")

        # Expected filenames
        expected_recipe_file = f"{test_recipe_name}_{today_str}.txt"
        expected_initial_base = f"{test_recipe_name}_initial_{today_str}"
        expected_final_base = f"{test_recipe_name}_final_{today_str}"
        expected_initial_script = f"{test_recipe_name}_initial_graph_script_{today_str}.py"
        expected_final_script = f"{test_recipe_name}_final_graph_script_{today_str}.py"
        expected_initial_gv = f"{expected_initial_base}.gv"
        expected_final_gv = f"{expected_final_base}.gv"

        # Use MagicMock to wrap mock_open to check calls
        mock_file_open = unittest.mock.mock_open(read_data="mock recipe draft")
        mock_open_wrapper = MagicMock(wraps=mock_file_open)

        with patch('builtins.input', return_value='yes'), \
             patch('sys.exit') as mock_exit, \
             patch('main.create_python_file_from_string') as mock_create_py_file, \
             patch('main.Path') as mock_path_class, \
             patch('builtins.open', mock_open_wrapper): # Use wrapped mock_open

            # Configure mock Path object behavior
            # We need Path(filename).unlink() and Path(filename).exists()
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True # Assume files exist for cleanup
            mock_path_instance.unlink.return_value = None
            # Make Path(filename) return our configured instance
            mock_path_class.side_effect = lambda p: mock_path_instance if p in [expected_initial_script, expected_final_script, expected_initial_gv, expected_final_gv, expected_recipe_file] else unittest.mock.DEFAULT


            # Call the function under test
            process_recipe("dummy_recipe.txt", test_recipe_name)

            # --- Assertions ---
            mock_exit.assert_not_called()

            # 1. Check standardized recipe file write
            # Find the call to open for writing the recipe file
            write_call = None
            for call_args in mock_open_wrapper.call_args_list:
                 # Check if called with write mode ('w') and expected filename
                 if len(call_args[0]) > 1 and call_args[0][1] == 'w' and Path(call_args[0][0]).name == expected_recipe_file:
                     write_call = call_args
                     break
            self.assertIsNotNone(write_call, f"Expected 'open' call for writing '{expected_recipe_file}' not found.")
            # Check content was written (optional, basic check)
            handle = mock_open_wrapper() # Get the mock file handle
            handle.write.assert_called_once_with(mock_rewrite.return_value)


            # 2. Check create_python_file_from_string calls
            self.assertEqual(mock_create_py_file.call_count, 2, "Expected create_python_file_from_string to be called twice")
            # Check initial script call
            call_args_initial = mock_create_py_file.call_args_list[0]
            self.assertIn(expected_initial_base, call_args_initial[0][0], "Initial graph code string doesn't contain expected base name")
            self.assertNotIn("'initial_recipe_flow'", call_args_initial[0][0], "Initial graph code string still contains default base name")
            self.assertEqual(call_args_initial[1]['filename'], expected_initial_script, "Initial script filename is incorrect")
            # Check final script call
            call_args_final = mock_create_py_file.call_args_list[1]
            self.assertIn(expected_final_base, call_args_final[0][0], "Final graph code string doesn't contain expected base name")
            self.assertNotIn("'recipe_flow'", call_args_final[0][0], "Final graph code string still contains default base name")
            self.assertEqual(call_args_final[1]['filename'], expected_final_script, "Final script filename is incorrect")


            # 3. Check os.system calls
            self.assertEqual(mock_os_system.call_count, 2, "Expected os.system to be called twice")
            mock_os_system.assert_has_calls([
                call(f"python {expected_initial_script}"),
                call(f"python {expected_final_script}")
            ], any_order=False) # Ensure they are called in the right order

            # 4. Check cleanup calls (Path.unlink)
            # Get all paths passed to Path() constructor
            paths_constructed = [c[0][0] for c in mock_path_class.call_args_list]
            # Check that unlink was called on the path instance for each expected file
            self.assertEqual(mock_path_instance.unlink.call_count, 4, "Expected unlink to be called 4 times")

            # Verify the specific files were targeted for unlinking by checking Path constructor calls
            self.assertIn(expected_initial_gv, paths_constructed, f"Path({expected_initial_gv}) was not constructed for cleanup")
            self.assertIn(expected_initial_script, paths_constructed, f"Path({expected_initial_script}) was not constructed for cleanup")
            self.assertIn(expected_final_gv, paths_constructed, f"Path({expected_final_gv}) was not constructed for cleanup")
            self.assertIn(expected_final_script, paths_constructed, f"Path({expected_final_script}) was not constructed for cleanup")


if __name__ == '__main__':
    unittest.main()
