"""
Node Manager

Manages distributed nodes and their states.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
from src.logging.logger import get_logger

logger = get_logger("node_manager")


@dataclass
class NodeInfo:
    """Information about a node"""
    node_id: str
    host: str
    port: int
    status: str = "online"  # online, offline, busy
    last_heartbeat: datetime = field(default_factory=datetime.now)
    request_count: int = 0
    error_count: int = 0
    capabilities: List[str] = field(default_factory=list)

    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """Check if node is alive"""
        elapsed = (datetime.now() - self.last_heartbeat).total_seconds()
        return elapsed < timeout_seconds

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "capabilities": self.capabilities,
        }


class NodeManager:
    """Manages distributed nodes"""

    def __init__(self):
        """Initialize node manager"""
        self.nodes: Dict[str, NodeInfo] = {}
        self.local_node: Optional[NodeInfo] = None

    def register_node(
        self, host: str, port: int, capabilities: List[str] = None
    ) -> str:
        """
        Register a new node.

        Args:
            host: Node host
            port: Node port
            capabilities: Node capabilities

        Returns:
            Node ID
        """
        node_id = str(uuid.uuid4())[:8]
        node = NodeInfo(
            node_id=node_id,
            host=host,
            port=port,
            capabilities=capabilities or [],
        )

        self.nodes[node_id] = node
        logger.info(f"Node {node_id} registered at {host}:{port}")

        return node_id

    def set_local_node(self, node_id: str) -> None:
        """
        Set local node.

        Args:
            node_id: Node ID
        """
        if node_id in self.nodes:
            self.local_node = self.nodes[node_id]
            logger.info(f"Local node set to {node_id}")

    def heartbeat(self, node_id: str) -> bool:
        """
        Record heartbeat from node.

        Args:
            node_id: Node ID

        Returns:
            True if successful
        """
        if node_id not in self.nodes:
            return False

        self.nodes[node_id].last_heartbeat = datetime.now()
        return True

    def get_node(self, node_id: str) -> Optional[NodeInfo]:
        """
        Get node information.

        Args:
            node_id: Node ID

        Returns:
            Node info or None
        """
        return self.nodes.get(node_id)

    def get_alive_nodes(self, timeout_seconds: int = 30) -> List[NodeInfo]:
        """
        Get all alive nodes.

        Args:
            timeout_seconds: Heartbeat timeout

        Returns:
            List of alive nodes
        """
        return [
            node
            for node in self.nodes.values()
            if node.is_alive(timeout_seconds)
        ]

    def get_available_nodes(self) -> List[NodeInfo]:
        """
        Get available nodes (online and not busy).

        Returns:
            List of available nodes
        """
        return [
            node
            for node in self.get_alive_nodes()
            if node.status in ["online"]
        ]

    def get_nodes_by_capability(self, capability: str) -> List[NodeInfo]:
        """
        Get nodes with specific capability.

        Args:
            capability: Capability name

        Returns:
            List of nodes with capability
        """
        return [
            node
            for node in self.get_alive_nodes()
            if capability in node.capabilities
        ]

    def update_node_status(self, node_id: str, status: str) -> bool:
        """
        Update node status.

        Args:
            node_id: Node ID
            status: New status

        Returns:
            True if successful
        """
        if node_id not in self.nodes:
            return False

        self.nodes[node_id].status = status
        logger.info(f"Node {node_id} status updated to {status}")

        return True

    def record_request(self, node_id: str, success: bool = True) -> None:
        """
        Record request on node.

        Args:
            node_id: Node ID
            success: Whether request was successful
        """
        if node_id in self.nodes:
            self.nodes[node_id].request_count += 1
            if not success:
                self.nodes[node_id].error_count += 1

    def get_stats(self) -> Dict:
        """Get node manager statistics"""
        alive_nodes = self.get_alive_nodes()
        available_nodes = self.get_available_nodes()

        return {
            "total_nodes": len(self.nodes),
            "alive_nodes": len(alive_nodes),
            "available_nodes": len(available_nodes),
            "nodes": [node.to_dict() for node in self.nodes.values()],
        }
