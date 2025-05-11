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
# Corrected imports to target r2g_app
try:
    from r2g_app import main # Import the main module from r2g_app
    from r2g_app.main import text_to_graph, process_text, revise_recipe # Import specific functions
    # upload_to_gcs is part of aux_funs, but called via main._get_gcs_bucket and main.upload_to_gcs
    # For patching, we'll target where it's used or defined: 'r2g_app.main.upload_to_gcs' or 'r2g_app.aux_funs.upload_to_gcs'
except ImportError as e:
    raise ImportError(f"Could not import from 'r2g_app.main'. Original error: {e}\nEnsure r2g_app is in PYTHONPATH: {project_root}") from e


# --- Test Class for upload_to_gcs function (from aux_funs, but test setup uses main.upload_to_gcs) ---
# This class seems to test 'upload_to_gcs' which is now in 'aux_funs.py'.
# The patch target 'main.storage.Client' implies it's testing the GCS interaction part,
# assuming 'main.upload_to_gcs' was a wrapper or the function itself.
# Given 'upload_to_gcs' is now in aux_funs, the patch target for storage.Client inside it would be 'r2g_app.aux_funs.storage.Client'
# However, the test calls main.upload_to_gcs. This needs to be reconciled.
# For now, I will assume 'main.upload_to_gcs' is what's intended to be tested,
# which means 'upload_to_gcs' must be imported into main's namespace or be a helper in main.
# From previous steps, 'upload_to_gcs' is in 'aux_funs' and imported into 'main'.
# So, patching 'r2g_app.main.upload_to_gcs' would mock the imported function in main's context if not careful.
# The current patches like '@patch('main.storage.Client')' are for when 'upload_to_gcs' was IN main.py.
# These will need to be '@patch('r2g_app.aux_funs.storage.Client')' if we are testing the aux_funs.upload_to_gcs directly.
# Or, if main.py has its own GCS client for _get_gcs_bucket, that would be 'r2g_app.main.storage.Client'.

# Let's assume TestGcsUpload is testing the aux_funs.upload_to_gcs via an import in main for now.
# The test calls `main.upload_to_gcs` which is fine if `upload_to_gcs` is imported into `main`.
# The patch target for `storage.Client` should be where `storage.Client()` is called.
# If `upload_to_gcs` is in `aux_funs.py`, then it should be `r2g_app.aux_funs.storage.Client`.

class TestGcsUpload(unittest.TestCase): # This class is stated to be kept as is. I will adjust its patches later if direct testing of aux_funs.upload_to_gcs is needed.
                                        # For now, focusing on TextToGraph. The current patches in TestGcsUpload might be incorrect due to refactoring.

    DUMMY_BUCKET = "test-bucket"
    DUMMY_LOCAL_FILE = "local_test_file.txt"
    DUMMY_BLOB_NAME = "remote_test_file.txt"

    def setUp(self):
        """Create a dummy local file before each test."""
        # Create dummy file in the test directory
        self.test_dir = Path(__file__).parent
        self.dummy_local_file_path = self.test_dir / self.DUMMY_LOCAL_FILE
        with open(self.dummy_local_file_path, "w") as f:
            f.write("Test content")

    def tearDown(self):
        """Remove the dummy local file after each test."""
        if os.path.exists(self.dummy_local_file_path):
            os.remove(self.dummy_local_file_path)

    # Assuming upload_to_gcs is now in aux_funs and imported by main.
    # If main.upload_to_gcs is just a direct import, we test aux_funs.upload_to_gcs.
    # The GCS client is instantiated within upload_to_gcs in aux_funs.py.
    @patch('r2g_app.aux_funs.storage.Client') # Corrected patch target
    def test_upload_to_gcs_success(self, mock_storage_client):
        """Tests successful upload path for upload_to_gcs."""
        # Configure mocks
        mock_client_instance = mock_storage_client.return_value
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_client_instance.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # Call the function (main.upload_to_gcs is from r2g_app.aux_funs)
        main.upload_to_gcs(self.DUMMY_BUCKET, str(self.dummy_local_file_path), self.DUMMY_BLOB_NAME)

        # Assertions
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)
        mock_bucket.blob.assert_called_once_with(self.DUMMY_BLOB_NAME)
        mock_blob.upload_from_filename.assert_called_once_with(str(self.dummy_local_file_path))

    @patch('r2g_app.aux_funs.storage.Client') # Corrected patch target
    def test_upload_to_gcs_failure_bucket_not_found(self, mock_storage_client):
        """Tests upload_to_gcs failure when the bucket is not found."""
        # Configure mocks to raise NotFound
        mock_client_instance = mock_storage_client.return_value
        mock_client_instance.bucket.side_effect = gcs_exceptions.NotFound("Bucket not found")

        # Assertions
        with self.assertRaises(gcs_exceptions.NotFound):
            main.upload_to_gcs(self.DUMMY_BUCKET, str(self.dummy_local_file_path), self.DUMMY_BLOB_NAME)

        # Verify mocks were called as expected before the exception
        mock_storage_client.assert_called_once()
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)

    @patch('r2g_app.aux_funs.storage.Client') # Corrected patch target
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
            main.upload_to_gcs(self.DUMMY_BUCKET, str(self.dummy_local_file_path), self.DUMMY_BLOB_NAME)

        # Verify mocks
        mock_client_instance.bucket.assert_called_once_with(self.DUMMY_BUCKET)
        mock_bucket.blob.assert_called_once_with(self.DUMMY_BLOB_NAME)
        mock_blob.upload_from_filename.assert_called_once_with(str(self.dummy_local_file_path))

    def test_upload_to_gcs_failure_local_file_not_found(self):
        """Tests upload_to_gcs failure when the local file doesn't exist."""
        # No need to mock GCS client here, as it should fail before that.
        # Delete the dummy file created in setUp
        os.remove(self.dummy_local_file_path)

        with self.assertRaises(FileNotFoundError):
            main.upload_to_gcs(self.DUMMY_BUCKET, str(self.dummy_local_file_path), self.DUMMY_BLOB_NAME)


# --- Test Class for R2G App Main Functions ---
# Mocks for dependencies of text_to_graph, process_text, revise_recipe
# These are broad; specific tests might override or narrow them.
@patch('r2g_app.main.PROJECT_ID', 'test-r2g-project')
@patch('r2g_app.main.DEFAULT_VERTEX_LOCATION', 'test-r2g-location')
@patch('r2g_app.main.PROCESS_TEXT_MODEL_NAME', 'test-process-model')
@patch('r2g_app.main.TEXT_TO_GRAPH_MODEL_NAME', 'test-graph-model')
# Mocks for genai_funs used by the main functions
@patch('r2g_app.main.generate_graph')
@patch('r2g_app.main.improve_graph')
@patch('r2g_app.main.draft_to_recipe')
@patch('r2g_app.main.re_write_recipe')
# Mocks for aux_funs or other utilities used by main functions
@patch('r2g_app.main.upload_to_gcs') # Mock the GCS upload function used within text_to_graph
@patch('r2g_app.main._get_gcs_bucket') # Mock the helper that gets bucket object
@patch('r2g_app.main.Path') # Mock pathlib.Path for file operations
@patch('builtins.open', new_callable=mock_open) # Mock open for file writing
@patch('datetime.date') # Mock date to control today_str
class TestR2GAppMainFunctions(unittest.TestCase):

    def test_text_to_graph_html_css_js_output_and_upload(
        self, mock_date, mock_builtin_open, mock_path_class, mock_get_gcs_bucket,
        mock_upload_gcs_main, mock_re_write_recipe_main, mock_draft_to_recipe_main,
        mock_improve_graph_main, mock_generate_graph_main
    ):
        """Tests text_to_graph for HTML/CSS/JS output, local writing, GCS upload, and cleanup."""
        # --- Setup Test Data ---
        test_recipe_name = "my_html_recipe"
        test_gcs_bucket_name = "my-r2g-bucket"
        test_project_id = "test-r2g-project" # Matches class-level mock
        standardised_recipe_text = "This is a standardised recipe."
        fixed_date = date(2023, 10, 26)
        today_str = fixed_date.strftime("%Y_%m_%d")
        mock_date.today.return_value = fixed_date

        # Expected generated filenames
        expected_txt_filename = f"{test_recipe_name}_{today_str}.txt"
        expected_html_filename = f"{test_recipe_name}_{today_str}_index.html"
        expected_css_filename = f"{test_recipe_name}_{today_str}_style.css"
        expected_js_filename = f"{test_recipe_name}_{today_str}_script.js"

        # Expected GCS URIs
        expected_txt_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_txt_filename}"
        expected_html_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_html_filename}"
        expected_css_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_css_filename}"
        expected_js_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_js_filename}"

        # --- Configure Mocks ---
        mock_generate_graph_main.return_value = "Initial graphviz code" # Actual content doesn't matter much
        mock_improve_graph_main.return_value = f"""
        <!-- start_html -->
        <h1>Test HTML for {test_recipe_name}</h1>
        <!-- end_html -->
        /* start_css */
        body {{ color: green; }}
        /* end_css */
        // start_js
        console.log("Test JS for {test_recipe_name}");
        // end_js
        """
        # Configure _get_gcs_bucket mock
        mock_bucket_instance = MagicMock(spec=storage.Bucket)
        mock_get_gcs_bucket.return_value = mock_bucket_instance
        # Configure mock for GCS blob uploads via the bucket instance
        mock_blob_instance = MagicMock(spec=storage.Blob)
        mock_bucket_instance.blob.return_value = mock_blob_instance

        # Configure Path mock instances
        # map path strings to their mock objects to control exists, unlink etc.
        path_mocks = {}
        def path_side_effect(p):
            p_str = str(p)
            if p_str not in path_mocks:
                m = MagicMock(spec=Path)
                m.name = Path(p_str).name
                m.__str__ = lambda: p_str # Make str(mock) return the path string
                m.exists.return_value = True # Assume files exist after creation for upload
                m.unlink.return_value = None
                # When Path(p).open() is called, it should use the global mock_builtin_open
                m.open = mock_builtin_open
                path_mocks[p_str] = m
            return path_mocks[p_str]
        mock_path_class.side_effect = path_side_effect


        # --- Call the function under test ---
        result = text_to_graph(
            standardised_recipe=standardised_recipe_text,
            recipe_name=test_recipe_name,
            gcs_bucket_name=test_gcs_bucket_name,
            project_id=test_project_id
        )

        # --- Assertions ---
        # 1. AI function calls
        mock_generate_graph_main.assert_called_once_with(
            standardised_recipe=standardised_recipe_text,
            system_instruction=ANY, project_id=test_project_id, location=ANY, model_name=ANY, temperature=ANY
        )
        mock_improve_graph_main.assert_called_once_with(
            standardised_recipe=standardised_recipe_text,
            graph_code=mock_generate_graph_main.return_value,
            system_instruction=ANY, project_id=test_project_id, location=ANY, model_name=ANY, temperature=ANY
        )

        # 2. File writing assertions (using builtins.open mock)
        # Check HTML write
        mock_builtin_open.assert_any_call(path_mocks[expected_html_filename], "w", encoding="utf-8")
        # Check CSS write
        mock_builtin_open.assert_any_call(path_mocks[expected_css_filename], "w", encoding="utf-8")
        # Check JS write
        mock_builtin_open.assert_any_call(path_mocks[expected_js_filename], "w", encoding="utf-8")
        # Check content written - this is a bit tricky with mock_open;
        # usually, you'd check handle.write() calls on the result of mock_open()
        # For simplicity, we assume parse_html_css_js_output (tested elsewhere) works.

        # 3. GCS Upload Assertions
        # Standardized recipe text upload (via bucket.blob().upload_from_string)
        mock_bucket_instance.blob.assert_any_call(expected_txt_filename)
        # The actual call to upload_from_string happens on the blob object returned by mock_bucket_instance.blob()
        # We need to ensure the blob that "received" expected_txt_filename was used for upload_from_string
        # This requires a more sophisticated mock setup for bucket.blob if we want to track individual blob interactions.
        # For now, let's check if upload_from_string was called with the recipe text.
        mock_blob_instance.upload_from_string.assert_any_call(standardised_recipe_text, content_type='text/plain; charset=utf-8')

        # HTML, CSS, JS uploads (via main.upload_to_gcs)
        expected_gcs_calls = [
            call(test_gcs_bucket_name, str(path_mocks[expected_html_filename]), expected_html_filename),
            call(test_gcs_bucket_name, str(path_mocks[expected_css_filename]), expected_css_filename),
            call(test_gcs_bucket_name, str(path_mocks[expected_js_filename]), expected_js_filename),
        ]
        mock_upload_gcs_main.assert_has_calls(expected_gcs_calls, any_order=False) # Order should be HTML, CSS, JS

        # 4. Cleanup Assertions (Path.unlink)
        path_mocks[str(Path(expected_html_filename))].unlink.assert_called_once()
        path_mocks[str(Path(expected_css_filename))].unlink.assert_called_once()
        path_mocks[str(Path(expected_js_filename))].unlink.assert_called_once()


        # 5. Return Value Assertion
        expected_return = {
            "recipe_uri": expected_txt_gcs_uri,
            "html_uri": expected_html_gcs_uri,
            "css_uri": expected_css_gcs_uri,
            "js_uri": expected_js_gcs_uri,
        }
        self.assertEqual(result, expected_return)

    # TODO: Add tests for process_text and revise_recipe if they are part of this class's responsibility.
    # test_user_approves_recipe and test_user_rejects_recipe are removed as they tested 'process_recipe'
    # which had interactive elements not present in text_to_graph.

    def test_text_to_graph_no_css_no_js(
        self, mock_date, mock_builtin_open, mock_path_class, mock_get_gcs_bucket,
        mock_upload_gcs_main, mock_re_write_recipe_main, mock_draft_to_recipe_main,
        mock_improve_graph_main, mock_generate_graph_main
    ):
        """Tests text_to_graph when CSS and JS content are missing from improve_graph output."""
        # --- Setup Test Data ---
        test_recipe_name = "my_html_only_recipe"
        test_gcs_bucket_name = "my-r2g-bucket"
        test_project_id = "test-r2g-project"
        standardised_recipe_text = "This is a standardised recipe for HTML only."
        fixed_date = date(2023, 11, 15) # Different date for different test
        today_str = fixed_date.strftime("%Y_%m_%d")
        mock_date.today.return_value = fixed_date

        expected_txt_filename = f"{test_recipe_name}_{today_str}.txt"
        expected_html_filename = f"{test_recipe_name}_{today_str}_index.html"
        # CSS and JS filenames won't be created if content is missing
        # expected_css_filename = f"{test_recipe_name}_{today_str}_style.css"
        # expected_js_filename = f"{test_recipe_name}_{today_str}_script.js"


        expected_txt_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_txt_filename}"
        expected_html_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_html_filename}"

        # --- Configure Mocks ---
        mock_generate_graph_main.return_value = "Initial graphviz code for HTML only"
        mock_improve_graph_main.return_value = """
        <!-- start_html -->
        <h1>Test HTML Only</h1>
        <!-- end_html -->
        /* start_css */
        /* end_css */
        // start_js
        // end_js
        """ # CSS and JS sections are empty

        mock_bucket_instance = MagicMock(spec=storage.Bucket)
        mock_get_gcs_bucket.return_value = mock_bucket_instance
        mock_blob_instance = MagicMock(spec=storage.Blob)
        mock_bucket_instance.blob.return_value = mock_blob_instance

        path_mocks = {}
        def path_side_effect(p):
            p_str = str(p)
            if p_str not in path_mocks:
                m = MagicMock(spec=Path)
                m.name = Path(p_str).name
                m.__str__ = lambda: p_str
                m.exists.return_value = True # Assume HTML file exists after creation
                if expected_html_filename not in p_str: # CSS/JS files won't exist
                    m.exists.return_value = False
                m.unlink.return_value = None
                m.open = mock_builtin_open
                path_mocks[p_str] = m
            return path_mocks[p_str]
        mock_path_class.side_effect = path_side_effect
        
        # Ensure the HTML path mock has exists = True specifically
        html_path_mock = MagicMock(spec=Path)
        html_path_mock.name = Path(expected_html_filename).name
        html_path_mock.__str__ = lambda: expected_html_filename
        html_path_mock.exists.return_value = True
        html_path_mock.unlink.return_value = None
        html_path_mock.open = mock_builtin_open
        path_mocks[expected_html_filename] = html_path_mock


        # --- Call the function ---
        result = text_to_graph(
            standardised_recipe=standardised_recipe_text,
            recipe_name=test_recipe_name,
            gcs_bucket_name=test_gcs_bucket_name,
            project_id=test_project_id
        )

        # --- Assertions ---
        # File writing: Only HTML should be written
        mock_builtin_open.assert_any_call(path_mocks[expected_html_filename], "w", encoding="utf-8")
        # Check that open was not called for CSS/JS - this is implicit if only HTML call is present and no others match
        # A more explicit way is to check call_count if mock_builtin_open is reset for each test.
        # For now, this relies on assert_any_call for HTML and lack of it for others.

        # GCS Uploads: Only recipe text and HTML
        mock_bucket_instance.blob.assert_any_call(expected_txt_filename) # For recipe text
        mock_blob_instance.upload_from_string.assert_any_call(standardised_recipe_text, content_type='text/plain; charset=utf-8')

        mock_upload_gcs_main.assert_called_once_with(
            test_gcs_bucket_name, str(path_mocks[expected_html_filename]), expected_html_filename
        ) # Only HTML is uploaded via upload_to_gcs

        # Cleanup: Only HTML file should be unlinked (plus any other internal temp files if any)
        path_mocks[expected_html_filename].unlink.assert_called_once()
        # Ensure unlink was not called for CSS/JS paths if they were instantiated by Path() mock
        # This depends on how Path mock is set up. If path_mocks only contains HTML, this is fine.
        # If Path() was called for CSS/JS files, their unlink should not be called.
        if f"{test_recipe_name}_{today_str}_style.css" in path_mocks:
             path_mocks[f"{test_recipe_name}_{today_str}_style.css"].unlink.assert_not_called()
        if f"{test_recipe_name}_{today_str}_script.js" in path_mocks:
             path_mocks[f"{test_recipe_name}_{today_str}_script.js"].unlink.assert_not_called()


        # Return value
        expected_return = {
            "recipe_uri": expected_txt_gcs_uri,
            "html_uri": expected_html_gcs_uri,
            "css_uri": None,
            "js_uri": None,
        }
        self.assertEqual(result, expected_return)

if __name__ == '__main__':
    unittest.main()
