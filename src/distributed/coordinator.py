"""
Coordinator

Coordinates distributed execution of tasks.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from src.distributed.node_manager import NodeManager, NodeInfo
from src.logging.logger import get_logger

logger = get_logger("coordinator")


class Coordinator:
    """Coordinates distributed task execution"""

    def __init__(self, node_manager: NodeManager):
        """
        Initialize coordinator.

        Args:
            node_manager: Node manager instance
        """
        self.node_manager = node_manager
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: Dict[str, Dict[str, Any]] = {}

    async def distribute_task(
        self, task_id: str, task: Dict[str, Any], expert_name: str = None
    ) -> Dict[str, Any]:
        """
        Distribute task to available nodes.

        Args:
            task_id: Task ID
            task: Task data
            expert_name: Preferred expert name

        Returns:
            Task result
        """
        # Get available nodes
        available_nodes = self.node_manager.get_available_nodes()

        if not available_nodes:
            return {
                "status": "error",
                "message": "No available nodes",
                "task_id": task_id,
            }

        # Select node based on capability
        if expert_name:
            suitable_nodes = self.node_manager.get_nodes_by_capability(
                expert_name
            )
            if suitable_nodes:
                selected_node = suitable_nodes[0]
            else:
                selected_node = available_nodes[0]
        else:
            selected_node = available_nodes[0]

        logger.info(
            f"Distributing task {task_id} to node {selected_node.node_id}"
        )

        # Update node status
        self.node_manager.update_node_status(selected_node.node_id, "busy")

        try:
            # Execute task on node
            result = await self._execute_on_node(selected_node, task)
            self.node_manager.record_request(selected_node.node_id, True)
            logger.info(f"Task {task_id} completed on node {selected_node.node_id}")

        except Exception as e:
            self.node_manager.record_request(selected_node.node_id, False)
            logger.error(f"Task {task_id} failed: {str(e)}")
            result = {"status": "error", "message": str(e)}

        finally:
            # Update node status back to online
            self.node_manager.update_node_status(selected_node.node_id, "online")

        # Store result
        self.completed_tasks[task_id] = result
        return result

    async def _execute_on_node(
        self, node: NodeInfo, task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute task on specific node.

        Args:
            node: Target node
            task: Task to execute

        Returns:
            Task result
        """
        # In a real distributed system, this would send to remote node
        # For now, simulate execution
        await asyncio.sleep(0.1)

        return {
            "status": "success",
            "node_id": node.node_id,
            "result": task.get("data", {}),
        }

    async def distribute_parallel(
        self, tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Distribute multiple tasks in parallel.

        Args:
            tasks: List of tasks

        Returns:
            List of results
        """
        coroutines = [
            self.distribute_task(f"task_{i}", task)
            for i, task in enumerate(tasks)
        ]

        results = await asyncio.gather(*coroutines)
        return results

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get result of completed task.

        Args:
            task_id: Task ID

        Returns:
            Task result or None
        """
        return self.completed_tasks.get(task_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        return {
            "total_tasks": len(self.task_queue) + len(self.completed_tasks),
            "pending_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "nodes_stats": self.node_manager.get_stats(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of all nodes.

        Returns:
            Health status
        """
        nodes = self.node_manager.nodes.values()
        unhealthy = []

        for node in nodes:
            if not node.is_alive():
                unhealthy.append(node.node_id)

        return {
            "status": "healthy" if not unhealthy else "degraded",
            "unhealthy_nodes": unhealthy,
            "available_nodes": len(self.node_manager.get_available_nodes()),
        }

    async def balance_load(self) -> Dict[str, Any]:
        """
        Perform load balancing.

        Returns:
            Load balancing result
        """
        nodes = self.node_manager.get_available_nodes()

        if not nodes:
            return {"status": "error", "message": "No available nodes"}

        # Calculate average load
        total_requests = sum(node.request_count for node in nodes)
        avg_load = total_requests / len(nodes) if nodes else 0

        logger.info(f"Average load: {avg_load}, Nodes: {len(nodes)}")

        return {
            "status": "balanced",
            "average_load": avg_load,
            "nodes": len(nodes),
        }
