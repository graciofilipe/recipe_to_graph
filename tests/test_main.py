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
@patch('r2g_app.main.os.remove') # Mock os.remove for cleanup
class TestR2GAppMainFunctions(unittest.TestCase):

    def test_text_to_graph_html_css_js_output_and_upload(
        self, mock_os_remove_main, mock_date, mock_builtin_open, mock_path_class, mock_get_gcs_bucket,
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

        # Expected local filenames (passed to Path)
        expected_html_local_filename = f"{test_recipe_name}_{today_str}_index.html"
        expected_css_local_filename = f"{test_recipe_name}_{today_str}_style.css"
        expected_js_local_filename = f"{test_recipe_name}_{today_str}_script.js"

        # Expected GCS details
        expected_txt_gcs_filename = f"{test_recipe_name}_{today_str}.txt" # Recipe text GCS name
        gcs_folder_path = f"{test_recipe_name}/{today_str}" # GCS sub-directory

        expected_html_gcs_blob_name = f"{gcs_folder_path}/{expected_html_local_filename}"
        expected_css_gcs_blob_name = f"{gcs_folder_path}/{expected_css_local_filename}"
        expected_js_gcs_blob_name = f"{gcs_folder_path}/{expected_js_local_filename}"

        expected_txt_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_txt_gcs_filename}"
        expected_html_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_html_gcs_blob_name}"
        expected_css_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_css_gcs_blob_name}"
        expected_js_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_js_gcs_blob_name}"

        html_content_val = f"<h1>Test HTML for {test_recipe_name}</h1>"
        css_content_val = "body { color: green; }"
        js_content_val = f'console.log("Test JS for {test_recipe_name}");'

        # --- Configure Mocks ---
        mock_generate_graph_main.return_value = "Initial graphviz code"
        mock_improve_graph_main.return_value = f"""```html filename="index.html"
{html_content_val}
```
```css filename="style.css"
{css_content_val}
```
```javascript filename="script.js"
{js_content_val}
```"""
        mock_bucket_instance = MagicMock(spec=storage.Bucket)
        mock_get_gcs_bucket.return_value = mock_bucket_instance
        mock_blob_instance_for_text = MagicMock(spec=storage.Blob)
        def blob_side_effect(blob_name): # For recipe text upload
            if blob_name == expected_txt_gcs_filename:
                return mock_blob_instance_for_text
            return MagicMock(spec=storage.Blob) # Default for other calls if any
        mock_bucket_instance.blob.side_effect = blob_side_effect

        path_mocks = {}
        def path_side_effect(p_str_arg): # Argument to Path()
            # Ensure p_str_arg is a string, as it might be a mock if Path is called with another mock
            p_str = str(p_str_arg)
            if p_str not in path_mocks:
                m = MagicMock(spec=Path)
                m.name = Path(p_str).name # Set the .name attribute
                m.__str__ = lambda s=p_str: s # str(mock) returns the path string
                m.exists.return_value = True # Assume files exist after writing for upload/cleanup
                m.open = mock_builtin_open # For Path(...).open(...) calls
                path_mocks[p_str] = m
            return path_mocks[p_str]
        mock_path_class.side_effect = path_side_effect
        
        # Create specific path mocks to use in assertions and ensure __str__ returns the simple filename
        path_html = path_side_effect(expected_html_local_filename)
        path_css = path_side_effect(expected_css_local_filename)
        path_js = path_side_effect(expected_js_local_filename)

        # --- Call the function under test ---
        result = text_to_graph(
            standardised_recipe=standardised_recipe_text,
            recipe_name=test_recipe_name,
            gcs_bucket_name=test_gcs_bucket_name,
            project_id=test_project_id
        )

        # --- Assertions ---
        mock_generate_graph_main.assert_called_once_with(
            standardised_recipe=standardised_recipe_text, system_instruction=ANY,
            project_id=test_project_id, location=ANY, model_name=ANY, temperature=ANY
        )
        mock_improve_graph_main.assert_called_once_with(
            standardised_recipe=standardised_recipe_text, graph_code=mock_generate_graph_main.return_value,
            system_instruction=ANY, project_id=test_project_id, location=ANY, model_name=ANY, temperature=ANY
        )

        path_html.open.assert_called_once_with("w", encoding="utf-8")
        path_css.open.assert_called_once_with("w", encoding="utf-8")
        path_js.open.assert_called_once_with("w", encoding="utf-8")

        mock_bucket_instance.blob.assert_any_call(expected_txt_gcs_filename) # Recipe text upload
        mock_blob_instance_for_text.upload_from_string.assert_called_once_with(standardised_recipe_text, content_type='text/plain; charset=utf-8')

        # Assert calls to main.upload_to_gcs
        expected_gcs_calls = [
            call(test_gcs_bucket_name, str(path_html), expected_html_gcs_blob_name),
            call(test_gcs_bucket_name, str(path_css), expected_css_gcs_blob_name),
            call(test_gcs_bucket_name, str(path_js), expected_js_gcs_blob_name),
        ]
        mock_upload_gcs_main.assert_has_calls(expected_gcs_calls, any_order=False)

        # Assert os.remove calls using the mocked Path objects
        mock_os_remove_main.assert_any_call(path_html)
        mock_os_remove_main.assert_any_call(path_css)
        mock_os_remove_main.assert_any_call(path_js)

        expected_return = {
            "recipe_uri": expected_txt_gcs_uri,
            "html_gcs_uri": expected_html_gcs_uri,
            "css_gcs_uri": expected_css_gcs_uri,
            "js_gcs_uri": expected_js_gcs_uri,
            "html_content": html_content_val,
            "css_content": css_content_val,
            "js_content": js_content_val,
        }
        self.assertDictEqual(result, expected_return)


    def test_text_to_graph_no_css_no_js(
        self, mock_os_remove_main, mock_date, mock_builtin_open, mock_path_class, mock_get_gcs_bucket,
        mock_upload_gcs_main, mock_re_write_recipe_main, mock_draft_to_recipe_main,
        mock_improve_graph_main, mock_generate_graph_main
    ):
        """Tests text_to_graph when CSS and JS content are missing from improve_graph output."""
        test_recipe_name = "my_html_only_recipe"
        test_gcs_bucket_name = "my-r2g-bucket"
        test_project_id = "test-r2g-project"
        standardised_recipe_text = "This is a standardised recipe for HTML only."
        fixed_date = date(2023, 11, 15)
        today_str = fixed_date.strftime("%Y_%m_%d")
        mock_date.today.return_value = fixed_date

        expected_html_local_filename = f"{test_recipe_name}_{today_str}_index.html"
        expected_css_local_filename = f"{test_recipe_name}_{today_str}_style.css" # Will be empty
        expected_js_local_filename = f"{test_recipe_name}_{today_str}_script.js"   # Will be empty

        expected_txt_gcs_filename = f"{test_recipe_name}_{today_str}.txt"
        gcs_folder_path = f"{test_recipe_name}/{today_str}"
        expected_html_gcs_blob_name = f"{gcs_folder_path}/{expected_html_local_filename}"

        expected_txt_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_txt_gcs_filename}"
        expected_html_gcs_uri = f"gs://{test_gcs_bucket_name}/{expected_html_gcs_blob_name}"
        
        html_content_val = "<h1>Test HTML Only</h1>"

        mock_generate_graph_main.return_value = "Initial graphviz code for HTML only"
        mock_improve_graph_main.return_value = f"""```html filename="index.html"
{html_content_val}
```
```css filename="style.css"
```
```javascript filename="script.js"
```"""
        mock_bucket_instance = MagicMock(spec=storage.Bucket)
        mock_get_gcs_bucket.return_value = mock_bucket_instance
        mock_blob_instance_for_text = MagicMock(spec=storage.Blob)
        mock_bucket_instance.blob.return_value = mock_blob_instance_for_text # For recipe text

        path_mocks = {}
        def path_side_effect(p_str_arg):
            p_str = str(p_str_arg)
            if p_str not in path_mocks:
                m = MagicMock(spec=Path)
                m.name = Path(p_str).name
                m.__str__ = lambda s=p_str: s
                # All local files (html, css, js) are written, even if empty for css/js.
                # So, they all "exist" before cleanup attempts.
                m.exists.return_value = True
                m.open = mock_builtin_open
                path_mocks[p_str] = m
            return path_mocks[p_str]
        mock_path_class.side_effect = path_side_effect

        path_html = path_side_effect(expected_html_local_filename)
        path_css = path_side_effect(expected_css_local_filename) # Mock for empty style.css
        path_js = path_side_effect(expected_js_local_filename)   # Mock for empty script.js

        result = text_to_graph(
            standardised_recipe=standardised_recipe_text,
            recipe_name=test_recipe_name,
            gcs_bucket_name=test_gcs_bucket_name,
            project_id=test_project_id
        )

        path_html.open.assert_called_once_with("w", encoding="utf-8")
        path_css.open.assert_called_once_with("w", encoding="utf-8") # Empty file is written
        path_js.open.assert_called_once_with("w", encoding="utf-8")   # Empty file is written

        mock_bucket_instance.blob.assert_any_call(expected_txt_gcs_filename)
        mock_blob_instance_for_text.upload_from_string.assert_called_once_with(standardised_recipe_text, content_type='text/plain; charset=utf-8')

        # upload_to_gcs is only called for HTML because css_content and js_content are empty
        mock_upload_gcs_main.assert_called_once_with(
            test_gcs_bucket_name, str(path_html), expected_html_gcs_blob_name
        )

        # os.remove is called for all path objects passed to it if they exist.
        # Path(...).exists() is mocked to True for all of them.
        mock_os_remove_main.assert_any_call(path_html)
        mock_os_remove_main.assert_any_call(path_css)
        mock_os_remove_main.assert_any_call(path_js)

        expected_return = {
            "recipe_uri": expected_txt_gcs_uri,
            "html_gcs_uri": expected_html_gcs_uri,
            "css_gcs_uri": None, # None because css_content was empty
            "js_gcs_uri": None,  # None because js_content was empty
            "html_content": html_content_val,
            "css_content": "", # Empty as per mock_improve_graph
            "js_content": "",  # Empty as per mock_improve_graph
        }
        self.assertDictEqual(result, expected_return)

if __name__ == '__main__':
    unittest.main()
