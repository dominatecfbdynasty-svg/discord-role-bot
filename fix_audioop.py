import sys
from unittest.mock import MagicMock

# Create a fake audioop module before discord imports it
sys.modules['audioop'] = MagicMock()
