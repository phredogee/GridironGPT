"""Cortex Understand faculty.

Resolves entities and interprets incoming information.
"""

from gridiron_cortex.understand.entity_resolver import EntityResolver
from gridiron_cortex.understand.signal_processor import SignalProcessor

__all__ = ["EntityResolver", "SignalProcessor"]
