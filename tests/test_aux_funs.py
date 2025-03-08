import unittest
import os
import sys
import shutil
import tempfile

# Get the directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory of the parent directory
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the module search path
sys.path.append(parent_dir)

from aux_funs import create_python_file_from_string


class TestAuxFuns(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_python_file_from_string(self):
        # Create a dummy code string
        code_string = "print('Hello, world!')"
        # Call the function
        create_python_file_from_string(code_string, filename=os.path.join(self.test_dir,'test_file.py'))
        # Check if the file exists
        self.assertTrue(os.path.exists(os.path.join(self.test_dir,'test_file.py')))
        # Check if the file content is correct
        with open(os.path.join(self.test_dir,'test_file.py'), 'r') as f:
            self.assertEqual(f.read(), code_string)
        # Remove the file
        os.remove(os.path.join(self.test_dir,'test_file.py'))
        # Check if the file exists
        self.assertFalse(os.path.exists(os.path.join(self.test_dir,'test_file.py')))
        # check that ValueError is raised when code string is empty
        with self.assertRaises(ValueError):
            create_python_file_from_string("", filename=os.path.join(self.test_dir,'test_file.py'))
