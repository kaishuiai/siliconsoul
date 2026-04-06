"""
Unit tests for distributed system
"""

import pytest
from src.distributed.node_manager import NodeManager, NodeInfo
from src.distributed.coordinator import Coordinator
from datetime import datetime


class TestNodeManager:
    """Tests for node manager"""

    def test_register_node(self):
        """Test registering a node"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000, ["expert1"])

        assert node_id in manager.nodes
        assert manager.nodes[node_id].host == "localhost"
        assert manager.nodes[node_id].port == 9000

    def test_set_local_node(self):
        """Test setting local node"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000)
        manager.set_local_node(node_id)

        assert manager.local_node is not None
        assert manager.local_node.node_id == node_id

    def test_heartbeat(self):
        """Test heartbeat recording"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000)

        initial_time = manager.nodes[node_id].last_heartbeat
        assert manager.heartbeat(node_id)
        assert manager.nodes[node_id].last_heartbeat > initial_time

    def test_get_alive_nodes(self):
        """Test getting alive nodes"""
        manager = NodeManager()
        node_id1 = manager.register_node("localhost", 9000)
        node_id2 = manager.register_node("localhost", 9001)

        manager.heartbeat(node_id1)

        alive = manager.get_alive_nodes()
        assert len(alive) == 2

    def test_get_nodes_by_capability(self):
        """Test getting nodes by capability"""
        manager = NodeManager()
        node_id = manager.register_node(
            "localhost", 9000, capabilities=["stock_analysis"]
        )
        manager.heartbeat(node_id)

        nodes = manager.get_nodes_by_capability("stock_analysis")
        assert len(nodes) == 1
        assert nodes[0].node_id == node_id

    def test_update_node_status(self):
        """Test updating node status"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000)

        assert manager.update_node_status(node_id, "busy")
        assert manager.nodes[node_id].status == "busy"

    def test_record_request(self):
        """Test recording request"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000)

        manager.record_request(node_id, success=True)
        assert manager.nodes[node_id].request_count == 1

        manager.record_request(node_id, success=False)
        assert manager.nodes[node_id].error_count == 1

    def test_get_stats(self):
        """Test getting statistics"""
        manager = NodeManager()
        node_id = manager.register_node("localhost", 9000)
        manager.heartbeat(node_id)

        stats = manager.get_stats()
        assert stats["total_nodes"] == 1
        assert stats["alive_nodes"] == 1


class TestCoordinator:
    """Tests for coordinator"""

    def test_coordinator_creation(self):
        """Test creating coordinator"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        assert coordinator.node_manager is manager
        assert len(coordinator.task_queue) == 0

    @pytest.mark.asyncio
    async def test_distribute_task_no_nodes(self):
        """Test distributing task with no nodes"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        result = await coordinator.distribute_task(
            "task_1", {"data": "test"}
        )

        assert result["status"] == "error"
        assert "No available nodes" in result["message"]

    @pytest.mark.asyncio
    async def test_distribute_task_with_node(self):
        """Test distributing task with available node"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        node_id = manager.register_node("localhost", 9000)
        manager.heartbeat(node_id)

        result = await coordinator.distribute_task(
            "task_1", {"data": "test"}
        )

        assert result["status"] == "success"

    def test_get_task_result(self):
        """Test getting task result"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        coordinator.completed_tasks["task_1"] = {"result": "test"}
        result = coordinator.get_task_result("task_1")

        assert result is not None
        assert result["result"] == "test"

    def test_coordinator_stats(self):
        """Test coordinator statistics"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        stats = coordinator.get_stats()
        assert stats["total_tasks"] == 0
        assert stats["pending_tasks"] == 0
        assert stats["completed_tasks"] == 0

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        node_id = manager.register_node("localhost", 9000)
        manager.heartbeat(node_id)

        health = await coordinator.health_check()
        assert health["status"] in ["healthy", "degraded"]

    @pytest.mark.asyncio
    async def test_balance_load_no_nodes(self):
        """Test load balancing with no nodes"""
        manager = NodeManager()
        coordinator = Coordinator(manager)

        result = await coordinator.balance_load()
        assert result["status"] == "error"
