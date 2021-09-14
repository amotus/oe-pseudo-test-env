import os
import sys

# NOTE: This is required for pytest to find the location of our sources.
# Required because we do not work with a proper python package with
# development mode.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
