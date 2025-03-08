import unittest
import os

def run_all_tests():
    """
    Discover and run all tests in the tests directory.
    """
    test_dir = os.path.dirname(__file__)
    test_suite = unittest.defaultTestLoader.discoverTestsFromDirectory(test_dir)
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)

if __name__ == "__main__":
    run_all_tests()
