"""
Distributed Module

Provides distributed processing and coordination.
"""

from src.distributed.node_manager import NodeManager
from src.distributed.coordinator import Coordinator

__all__ = ["NodeManager", "Coordinator"]
