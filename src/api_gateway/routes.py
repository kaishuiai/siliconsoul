"""
API Routes

Defines all API routes for SiliconSoul.
"""

from typing import Dict, Any, Optional
from src.api_gateway.gateway import APIGateway
from src.logging.logger import get_logger

logger = get_logger("routes")


def create_routes(gateway: APIGateway, orchestrator: Any) -> None:
    """
    Create API routes.

    Args:
        gateway: API gateway instance
        orchestrator: MOE orchestrator instance
    """

    # Health Check
    @gateway.route("/api/health", methods=["GET"])
    async def health_check(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Health check endpoint"""
        return {"status": "healthy", "version": "1.0.0"}

    # List Experts
    @gateway.route("/api/experts", methods=["GET"])
    async def list_experts(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List all experts"""
        experts = []
        for name, expert in orchestrator.experts.items():
            experts.append({
                "name": name,
                "version": getattr(expert, "version", "1.0"),
                "supported_tasks": getattr(expert, "supported_tasks", []),
            })
        return {"experts": experts}

    # Get Expert
    @gateway.route("/api/experts/<name>", methods=["GET"])
    async def get_expert(body: Optional[Dict[str, Any]] = None, name: str = "") -> Dict[str, Any]:
        """Get specific expert"""
        if name not in orchestrator.experts:
            raise ValueError(f"Expert {name} not found")

        expert = orchestrator.experts[name]
        return {
            "name": name,
            "version": getattr(expert, "version", "1.0"),
            "supported_tasks": getattr(expert, "supported_tasks", []),
        }

    # Process Request
    @gateway.route("/api/process", methods=["POST"])
    async def process_request(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process a request through MOE"""
        if not body:
            raise ValueError("Request body required")

        text = body.get("text", "")
        task_type = body.get("task_type")
        context = body.get("context", {})

        request_id = f"req_{orchestrator.request_count + 1}"

        results = await orchestrator.process(text, task_type, context)

        return {
            "request_id": request_id,
            "results": results,
        }

    # Batch Process
    @gateway.route("/api/batch", methods=["POST"])
    async def batch_process(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process batch requests"""
        if not body or "requests" not in body:
            raise ValueError("Requests list required")

        requests = body["requests"]
        results = []

        for req in requests:
            result = await orchestrator.process(
                req.get("text", ""),
                req.get("task_type"),
                req.get("context", {}),
            )
            results.append(result)

        return {"batch_id": f"batch_{orchestrator.request_count}", "results": results}

    # Monitor - Metrics
    @gateway.route("/api/monitor/metrics", methods=["GET"])
    async def get_metrics(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system metrics"""
        return orchestrator.monitor.get_status()

    # Monitor - Stats
    @gateway.route("/api/monitor/stats", methods=["GET"])
    async def get_stats(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system statistics"""
        return orchestrator.monitor.get_metrics()

    # Config - Get
    @gateway.route("/api/config", methods=["GET"])
    async def get_config(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get configuration"""
        return orchestrator.config_manager.get_all()

    # Config - Set
    @gateway.route("/api/config", methods=["POST"])
    async def set_config(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Set configuration"""
        if not body or "key" not in body:
            raise ValueError("Key required")

        key = body["key"]
        value = body["value"]
        orchestrator.config_manager.set(key, value)

        return {"message": f"Config {key} updated"}

    # Logs
    @gateway.route("/api/logs", methods=["GET"])
    async def get_logs(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system logs"""
        # This would integrate with actual logging system
        return {"logs": [], "message": "Logs endpoint"}

    logger.info("All routes created successfully")
