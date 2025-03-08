import os
import sys

# Get the directory of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))

# Add the directory to the module search path
sys.path.append(dir_path)

# Import the module from the directory
from tests import *
