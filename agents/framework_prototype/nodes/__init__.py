"""
Node types for the agent framework
"""

import sys
from pathlib import Path

# Handle imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import basic nodes (we'll create these if missing)
try:
    from .basic_nodes import BASIC_NODE_TYPES
except ImportError:
    BASIC_NODE_TYPES = {}

# Import advanced nodes
try:
    from .advanced_nodes import ADVANCED_NODE_TYPES
except ImportError:
    ADVANCED_NODE_TYPES = {}

# Import external nodes
try:
    from .external_nodes import EXTERNAL_NODE_TYPES
except ImportError:
    EXTERNAL_NODE_TYPES = {}

# Combined registry
ALL_NODE_TYPES = {
    **BASIC_NODE_TYPES,
    **ADVANCED_NODE_TYPES,
    **EXTERNAL_NODE_TYPES
}

__all__ = ["ALL_NODE_TYPES", "BASIC_NODE_TYPES", "ADVANCED_NODE_TYPES"]
