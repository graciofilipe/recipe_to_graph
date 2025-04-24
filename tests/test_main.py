import unittest
from unittest.mock import patch, MagicMock, call, mock_open, ANY
import sys
import os
from pathlib import Path
from datetime import date
from google.cloud import storage # Import GCS library
from google.cloud import exceptions as gcs_exceptions # Import GCS exceptions

# Add project root to sys.path to allow importing main
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import functions and classes AFTER potentially modifying sys.path
try:
    import main # Import the whole module to access upload_to_gcs
    from main import process_recipe
except ImportError as e:
    raise ImportError(f"Could not import from 'main'. Original error: {e}\nMake sure main.py is in the project root: {project_root}") from e

# --- Test Class for upload_to_gcs function ---
class TestGcsUpload(unittest.TestCase):

    DUMMY_BUCKET = "test-bucket"
    DUMMY_LOCAL_FILE = "local_test_file.txt"
    DUMMY_BLOB_NAME = "remote_test_file.txt"

    def setUp(self):
        """Create a dummy local file before each test."""
        with open(self.DUMMY_LOCAL_FILE, "w") as f:
            f.write("Test content")

    def tearDown(self):
        """Remove the dummy local file after each test."""
        if os.path.exists(self.DUMMY_LOCAL_FILE):
            os.remove(self.DUMMY_LOCAL_FILE)

    @patch('main.storage.Client')
    def test_upload_to_gcs_success(self, mock_storage_client):
        """Tests successful upload path for upload_to_gcs."""
        # Configure mocks
        mock_client_instance = mock_storage_client.return_value
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Call the function
        main.upload_to_gcs(self.DUMMY_BUCKET, self.DUMMY_LOCAL_FILE, self.DUMMY_BLOB_NAME)

        # Assertions
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)
        mock_bucket.blob.assert_called_once_with(self.DUMMY_BLOB_NAME)
        mock_blob.upload_from_filename.assert_called_once_with(self.DUMMY_LOCAL_FILE)

    @patch('main.storage.Client')
    def test_upload_to_gcs_failure_bucket_not_found(self, mock_storage_client):
        """Tests upload_to_gcs failure when the bucket is not found."""
        # Configure mocks to raise NotFound
        mock_client_instance = mock_storage_client.return_value
        mock_client_instance.bucket.side_effect = gcs_exceptions.NotFound("Bucket not found")

        # Assertions
        with self.assertRaises(gcs_exceptions.NotFound):
            main.upload_to_gcs(self.DUMMY_BUCKET, self.DUMMY_LOCAL_FILE, self.DUMMY_BLOB_NAME)

        # Verify mocks were called as expected before the exception
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)

    @patch('main.storage.Client')
    def test_upload_to_gcs_failure_permission_denied(self, mock_storage_client):
        """Tests upload_to_gcs failure due to permissions."""
        # Configure mocks
        mock_client_instance = mock_storage_client.return_value
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_filename.side_effect = gcs_exceptions.Forbidden("Permission denied")

        # Assertions
        with self.assertRaises(gcs_exceptions.Forbidden):
            main.upload_to_gcs(self.DUMMY_BUCKET, self.DUMMY_LOCAL_FILE, self.DUMMY_BLOB_NAME)

        # Verify mocks
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)
        mock_bucket.blob.assert_called_once_with(self.DUMMY_BLOB_NAME)
        mock_blob.upload_from_filename.assert_called_once_with(self.DUMMY_LOCAL_FILE)

    def test_upload_to_gcs_failure_local_file_not_found(self):
        """Tests upload_to_gcs failure when the local file doesn't exist."""
        # No need to mock GCS client here, as it should fail before that.
        # Delete the dummy file created in setUp
        os.remove(self.DUMMY_LOCAL_FILE)

        with self.assertRaises(FileNotFoundError):
            main.upload_to_gcs(self.DUMMY_BUCKET, self.DUMMY_LOCAL_FILE, self.DUMMY_BLOB_NAME)


# --- Test Class for process_recipe, including GCS integration ---
# Mock constants and functions from external modules used in process_recipe
@patch('main.PROJECT_ID', 'test-project')
@patch('main.DEFAULT_VERTEX_LOCATION', 'test-location')
@patch('main.DEFAULT_MODEL_NAME', 'test-model')
@patch('main.draft_to_recipe', return_value="Mocked structured recipe")
@patch('main.re_write_recipe', return_value="Mocked standardised recipe")
@patch('main.generate_graph', return_value="graph = Digraph('initial_recipe_flow')\n# Other graph code")
@patch('main.improve_graph', return_value="graph = Digraph('recipe_flow')\n# Improved graph code")
@patch('main.os.system', return_value=0) # Mock os.system to avoid actual execution
@patch('main.Path.is_file', return_value=True) # Assume draft file exists
@patch('main.upload_to_gcs') # Mock the GCS upload function directly for integration test
@patch('main.os.remove') # Mock os.remove used for cleanup
class TestMainFunctionality(unittest.TestCase):

    # Mocks passed by class decorator are now fewer
    def test_user_approves_recipe(self, mock_os_remove, mock_upload_gcs, mock_is_file, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing continues when user inputs 'yes'."""
        with patch('builtins.input', return_value='yes'), \
             patch('sys.exit') as mock_exit, \
             patch('main.create_python_file_from_string') as mock_create_py_file, \
             patch('main.Path.unlink') as mock_unlink, \
             patch('builtins.open', mock_open(read_data="mock recipe draft")): # Mock open for reading draft

            # Call the function under test (using default recipe name "recipe")
            process_recipe("dummy_recipe.txt", "recipe", "test-gcs-bucket") # Pass recipe_name and bucket

            # Assertions
            mock_exit.assert_not_called() # Exit should not be called
            mock_generate_graph.assert_called_once() # Graph generation should be called
            mock_improve_graph.assert_called_once() # Graph improvement should be called
            self.assertTrue(mock_create_py_file.called) # Check if script creation was attempted
            self.assertTrue(mock_os_system.called) # Check if os.system was called
            self.assertGreaterEqual(mock_upload_gcs.call_count, 2) # Check GCS upload called at least for txt and pdf

    # Mocks passed by class decorator
    def test_user_rejects_recipe(self, mock_os_remove, mock_upload_gcs, mock_is_file, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests that processing stops when user inputs anything other than 'yes'."""
        with patch('builtins.input', return_value='no'), \
             patch('sys.exit') as mock_exit, \
             patch('builtins.open', mock_open(read_data="mock recipe draft")): # Mock open for reading draft

            # Call the function under test
            process_recipe("dummy_recipe.txt", "recipe", "test-gcs-bucket") # Pass recipe_name and bucket

            # Assertions
            mock_exit.assert_called_once_with(0) # sys.exit(0) should be called
            mock_generate_graph.assert_not_called() # Graph generation should NOT be called
            mock_improve_graph.assert_not_called() # Graph improvement should NOT be called
            mock_upload_gcs.assert_not_called() # GCS Upload should NOT be called

    # Mocks passed by class decorator
    @patch('main.Path') # Mock Path specifically for this test to control is_file for outputs
    def test_dynamic_filenames_and_gcs_upload(self, mock_path_class_local, mock_os_remove, mock_upload_gcs, mock_is_file_draft, mock_os_system, mock_improve_graph, mock_generate_graph, mock_rewrite, mock_draft_to_recipe, *args):
        """Tests dynamic filenames and verifies GCS upload calls."""
        test_recipe_name = "my_gcs_recipe"
        test_bucket_name = "my-test-bucket"
        today_str = date.today().strftime("%Y_%m_%d")

        # Expected filenames
        expected_recipe_file = f"{test_recipe_name}_{today_str}.txt"
        expected_initial_base = f"{test_recipe_name}_initial_{today_str}"
        expected_final_base = f"{test_recipe_name}_final_{today_str}"
        expected_initial_script = f"{test_recipe_name}_initial_graph_script_{today_str}.py"
        expected_final_script = f"{test_recipe_name}_final_graph_script_{today_str}.py"
        expected_initial_gv = f"{expected_initial_base}.gv"
        expected_final_gv = f"{expected_final_base}.gv"
        expected_final_pdf = f"{expected_final_base}.pdf"

        # Use MagicMock to wrap mock_open to check calls
        mock_file_open_instance = mock_open(read_data="mock recipe draft")
        mock_open_wrapper = MagicMock(wraps=mock_file_open_instance)

        # Configure mock Path object behavior
        # Need Path(filename).unlink(), Path(filename).exists(), Path(filename).is_file()
        mock_path_instance_map = {}

        def mock_path_side_effect(p):
            p_str = str(p)
            if p_str not in mock_path_instance_map:
                instance = MagicMock(spec=Path)
                instance.name = Path(p_str).name # Set the name attribute
                instance.__str__.return_value = p_str
                # Default behavior: exists=True, is_file=True (can be overridden)
                instance.exists.return_value = True
                instance.is_file.return_value = True
                instance.unlink.return_value = None
                mock_path_instance_map[p_str] = instance
            return mock_path_instance_map[p_str]

        mock_path_class_local.side_effect = mock_path_side_effect
        # Ensure draft file check uses the class-level mock_is_file_draft
        mock_path_instance_map["dummy_recipe.txt"] = MagicMock(is_file=mock_is_file_draft)


        with patch('builtins.input', return_value='yes'), \
             patch('sys.exit') as mock_exit, \
             patch('main.create_python_file_from_string') as mock_create_py_file, \
             patch('builtins.open', mock_open_wrapper): # Use wrapped mock_open

            # Call the function under test
            process_recipe("dummy_recipe.txt", test_recipe_name, test_bucket_name)

            # --- Assertions ---
            mock_exit.assert_not_called()

            # 1. Check standardized recipe file write and upload
            recipe_path_written = None
            for call_args in mock_open_wrapper.call_args_list:
                 if len(call_args[0]) > 1 and call_args[0][1] == 'w' and Path(call_args[0][0]).name == expected_recipe_file:
                     recipe_path_written = str(call_args[0][0])
                     break
            self.assertIsNotNone(recipe_path_written, f"Expected 'open' call for writing '{expected_recipe_file}' not found.")
            handle = mock_open_wrapper()
            handle.write.assert_called_once_with(mock_rewrite.return_value)

            # 2. Check create_python_file_from_string calls (as before)
            self.assertEqual(mock_create_py_file.call_count, 2)
            # Check initial script call
            call_args_initial = mock_create_py_file.call_args_list[0]
            self.assertIn(expected_initial_base, call_args_initial[0][0])
            self.assertEqual(call_args_initial[1]['filename'], expected_initial_script)
            # Check final script call
            call_args_final = mock_create_py_file.call_args_list[1]
            self.assertIn(expected_final_base, call_args_final[0][0])
            self.assertEqual(call_args_final[1]['filename'], expected_final_script)

            # 3. Check os.system calls (as before)
            self.assertEqual(mock_os_system.call_count, 2)
            mock_os_system.assert_has_calls([
                call(f"python {expected_initial_script}"),
                call(f"python {expected_final_script}")
            ], any_order=False)

            # 4. Check GCS Upload Calls
            self.assertGreaterEqual(mock_upload_gcs.call_count, 2)
            # Use ANY for the exact local path, as it might be absolute depending on test runner
            expected_calls = [
                 call(test_bucket_name, ANY, expected_recipe_file), # Check bucket and blob name for txt
                 call(test_bucket_name, ANY, expected_final_pdf)   # Check bucket and blob name for pdf
            ]
            mock_upload_gcs.assert_has_calls(expected_calls, any_order=False) # Order matters here

            # Verify the local paths passed to upload_to_gcs match the expected files
            first_upload_call_args = mock_upload_gcs.call_args_list[0][0]
            second_upload_call_args = mock_upload_gcs.call_args_list[1][0]
            self.assertTrue(first_upload_call_args[1].endswith(expected_recipe_file))
            self.assertTrue(second_upload_call_args[1].endswith(expected_final_pdf))


            # 5. Check os.remove calls for uploaded files
            remove_calls_expected = [
                call(mock_path_instance_map[recipe_path_written]), # Path obj for recipe
                call(expected_final_pdf) # String path for pdf
            ]
            # We need to check if the calls were made. Allow any order.
            mock_os_remove.assert_has_calls(remove_calls_expected, any_order=True)
            self.assertGreaterEqual(mock_os_remove.call_count, 2) # Should be called at least for txt and pdf

            # 6. Check cleanup calls (Path.unlink) for intermediate files
            unlink_call_count = 0
            for path_str, instance in mock_path_instance_map.items():
                 if path_str in [expected_initial_gv, expected_initial_script, expected_final_gv, expected_final_script]:
                      unlink_call_count += instance.unlink.call_count
            self.assertEqual(unlink_call_count, 4, "Expected unlink to be called 4 times for intermediate files")


if __name__ == '__main__':
    unittest.main()
