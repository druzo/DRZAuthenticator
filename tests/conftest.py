"""pytest configuration and fixtures."""

import sys
import os
import tempfile

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
