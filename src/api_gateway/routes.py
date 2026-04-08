"""
API Routes

Defines all API routes for SiliconSoul.
"""

from typing import Dict, Any, Optional
import re
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

    def _normalize_aggregated_payload(raw: Any) -> Dict[str, Any]:
        if not isinstance(raw, dict):
            return {"results": raw}
        payload = dict(raw)
        payload["request_id"] = raw.get("request_id")
        payload["result"] = raw.get("final_result")
        payload["expert_results"] = raw.get("expert_results", [])
        payload["results"] = raw
        return payload

    # Health Check
    @gateway.route("/api/health", methods=["GET"])
    async def health_check(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Health check endpoint"""
        monitor = getattr(orchestrator, "monitor", None)
        monitor_status = monitor.get_status() if monitor is not None and hasattr(monitor, "get_status") else {}
        version = "1.0.0"
        if hasattr(orchestrator, "config_manager"):
            version = str(orchestrator.config_manager.get("system.version", version))
        return {
            "status": "healthy",
            "version": version,
            "uptime": monitor_status.get("uptime", "0d 0h"),
            "request_count": int(monitor_status.get("total_requests", getattr(orchestrator, "request_count", 0))),
        }

    @gateway.route("/api/me", methods=["GET"])
    async def me(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = body or {}
        return {
            "user_id": params.get("user_id", "anonymous"),
            "auth_enabled": bool(orchestrator.config_manager.get("auth.enabled", False)) if hasattr(orchestrator, "config_manager") else False,
        }

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
        user_id = body.get("user_id", "api_user")
        extra_params = body.get("extra_params")
        expert_names = body.get("expert_names")
        if expert_names is not None and not isinstance(expert_names, list):
            raise ValueError("expert_names must be a list")

        results = await orchestrator.process(
            text,
            task_type,
            context,
            user_id=user_id,
            extra_params=extra_params,
            expert_names=expert_names,
        )

        return _normalize_aggregated_payload(results)

    # Batch Process
    @gateway.route("/api/batch", methods=["POST"])
    async def batch_process(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process batch requests"""
        if not body or "requests" not in body:
            raise ValueError("Requests list required")

        requests = body["requests"]
        user_id = body.get("user_id", "api_user")

        if hasattr(orchestrator, "batch_process"):
            results = await orchestrator.batch_process(requests, user_id=user_id)
        else:
            results = []
            for req in requests:
                results.append(
                    await orchestrator.process(
                        req.get("text", ""),
                        req.get("task_type"),
                        req.get("context", {}),
                        user_id=req.get("user_id", user_id),
                        extra_params=req.get("extra_params"),
                    )
                )

        normalized = [_normalize_aggregated_payload(r) for r in results]
        return {"batch_id": f"batch_{orchestrator.request_count}", "results": results, "items": normalized}

    # Monitor - Metrics
    @gateway.route("/api/monitor/metrics", methods=["GET"])
    async def get_metrics(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system metrics"""
        monitor = getattr(orchestrator, "monitor", None)
        if monitor is None or not hasattr(monitor, "get_metrics"):
            return {}
        out = monitor.get_metrics()
        if isinstance(out, dict):
            metrics = out.get("metrics")
            if isinstance(metrics, dict):
                return metrics
        return {}

    # Monitor - Status
    @gateway.route("/api/monitor/status", methods=["GET"])
    async def get_monitor_status(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system status"""
        monitor = getattr(orchestrator, "monitor", None)
        if monitor is None or not hasattr(monitor, "get_status"):
            return {}
        return monitor.get_status()

    # Monitor - Stats
    @gateway.route("/api/monitor/stats", methods=["GET"])
    async def get_stats(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get system statistics"""
        monitor = getattr(orchestrator, "monitor", None)
        if monitor is None or not hasattr(monitor, "get_metrics"):
            return {"status": {}, "metrics": {}}
        return monitor.get_metrics()

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

    @gateway.route("/api/history/<user_id>", methods=["GET"])
    async def list_history(body: Optional[Dict[str, Any]] = None, user_id: str = "") -> Dict[str, Any]:
        params = body or {}
        q = params.get("q")
        expert_name = params.get("expert_name")
        task_type = params.get("task_type")
        consensus_level = params.get("consensus_level")
        since = params.get("since")
        until = params.get("until")
        only_errors_raw = params.get("only_errors", False)
        only_errors = False
        if isinstance(only_errors_raw, bool):
            only_errors = only_errors_raw
        elif isinstance(only_errors_raw, str):
            only_errors = only_errors_raw.lower() in {"1", "true", "yes"}
        limit = int(params.get("limit", 50))
        offset = int(params.get("offset", 0))
        sm = getattr(orchestrator, "storage_manager", None)
        if sm is None:
            raise ValueError("storage_manager not available")
        return {"items": sm.list_requests(user_id=user_id, q=q, expert_name=expert_name, task_type=task_type, consensus_level=consensus_level, only_errors=only_errors, since=since, until=until, limit=limit, offset=offset)}

    @gateway.route("/api/history/<user_id>/<request_id>", methods=["GET"])
    async def get_history_detail(
        body: Optional[Dict[str, Any]] = None, user_id: str = "", request_id: str = ""
    ) -> Dict[str, Any]:
        sm = getattr(orchestrator, "storage_manager", None)
        if sm is None:
            raise ValueError("storage_manager not available")
        record = sm.get_request(request_id)
        if record is None or record.user_id != user_id:
            raise ValueError("record not found")
        results = sm.get_results(request_id)
        aggregated = None
        normalized = []
        expert_results = []
        for r in results:
            name = r.expert_name if hasattr(r, "expert_name") else r.get("expert_name")
            row = r.to_dict() if hasattr(r, "to_dict") else r
            if name == "__aggregated__":
                aggregated = row
            normalized.append(row)
            if name == "__aggregated__":
                continue
            ts = row.get("timestamp")
            duration_ms = float(row.get("duration_ms") or 0.0)
            expert_results.append(
                {
                    "expert_name": name,
                    "result": row.get("result"),
                    "confidence": row.get("confidence", 0.5),
                    "metadata": {"result_id": row.get("result_id"), "request_id": row.get("request_id")},
                    "timestamp_start": ts,
                    "timestamp_end": ts,
                    "duration_ms": duration_ms,
                    "error": row.get("error"),
                }
            )
        aggregated_result = aggregated.get("result") if isinstance(aggregated, dict) else None
        return {
            "request": record.to_dict(),
            "results": normalized,
            "aggregated": aggregated,
            "expert_results": expert_results,
            "result": aggregated_result,
        }

    @gateway.route("/api/history/<user_id>/<request_id>/replay", methods=["POST"])
    async def replay_history(
        body: Optional[Dict[str, Any]] = None, user_id: str = "", request_id: str = ""
    ) -> Dict[str, Any]:
        sm = getattr(orchestrator, "storage_manager", None)
        if sm is None:
            raise ValueError("storage_manager not available")
        record = sm.get_request(request_id)
        if record is None or record.user_id != user_id:
            raise ValueError("record not found")

        if not hasattr(orchestrator, "process"):
            raise ValueError("orchestrator.process not available")

        params = body or {}
        task_type = params.get("task_type")
        expert_names = params.get("expert_names")
        if expert_names is not None and not isinstance(expert_names, list):
            raise ValueError("expert_names must be a list")
        if isinstance(expert_names, list):
            expert_names = [str(x) for x in expert_names if str(x)]
            expert_names = expert_names or None

        replayed = await orchestrator.process(
            record.text,
            task_type,
            record.context or {},
            user_id=user_id,
            extra_params={"replay_of": request_id},
            expert_names=expert_names,
        )
        return _normalize_aggregated_payload(replayed)

    @gateway.route("/api/portfolio/<user_id>", methods=["GET"])
    async def get_portfolio(body: Optional[Dict[str, Any]] = None, user_id: str = "") -> Dict[str, Any]:
        pm = getattr(orchestrator, "portfolio_manager", None)
        if pm is None:
            raise ValueError("portfolio_manager not available")
        return pm.get_portfolio(user_id)

    @gateway.route("/api/portfolio/<user_id>/positions", methods=["POST"])
    async def update_position(body: Optional[Dict[str, Any]] = None, user_id: str = "") -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        pm = getattr(orchestrator, "portfolio_manager", None)
        if pm is None:
            raise ValueError("portfolio_manager not available")
        symbol = body.get("symbol", "")
        quantity = body.get("quantity", 0)
        if isinstance(quantity, str) and quantity.isdigit():
            quantity = int(quantity)
        if not isinstance(quantity, int):
            raise ValueError("quantity must be int")
        return pm.update_position(user_id, symbol, quantity)

    @gateway.route("/api/portfolio/<user_id>/stats", methods=["GET"])
    async def get_portfolio_stats(body: Optional[Dict[str, Any]] = None, user_id: str = "") -> Dict[str, Any]:
        pm = getattr(orchestrator, "portfolio_manager", None)
        if pm is None:
            raise ValueError("portfolio_manager not available")
        return pm.get_stats(user_id)

    @gateway.route("/api/stocks/popular", methods=["GET"])
    async def get_popular_stocks(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        symbols = ["600000.SH", "000001.SZ", "AAPL", "MSFT", "TSLA"]
        return {"symbols": symbols}

    @gateway.route("/api/stocks/<symbol>", methods=["GET"])
    async def get_stock_info(
        body: Optional[Dict[str, Any]] = None, symbol: str = ""
    ) -> Dict[str, Any]:
        expert = orchestrator.experts.get("StockAnalysisExpert")
        name = symbol
        if expert is not None and hasattr(expert, "_get_stock_name"):
            try:
                name = expert._get_stock_name(symbol)
            except Exception:
                name = symbol
        market = "CN" if re.match(r"^\d{6}\.(SH|SZ)$", symbol, flags=re.IGNORECASE) else "US"
        return {"symbol": symbol, "name": name, "market": market}

    @gateway.route("/api/stocks/<symbol>/history", methods=["GET"])
    async def get_stock_history(
        body: Optional[Dict[str, Any]] = None, symbol: str = ""
    ) -> Dict[str, Any]:
        params = body or {}
        days = int(params.get("days", 60))
        expert = orchestrator.experts.get("StockAnalysisExpert")
        if expert is None or not hasattr(expert, "_load_price_data"):
            raise ValueError("StockAnalysisExpert not available")
        data = await expert._load_price_data(symbol, days)
        return {"symbol": symbol, "days": days, "data": data}

    @gateway.route("/api/analysis/analyze", methods=["POST"])
    async def analyze_stock(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        symbol = body.get("symbol", "")
        indicators = body.get("indicators", ["MA", "RSI", "MACD"])
        period_days = int(body.get("period_days", 60))
        user_id = body.get("user_id", "api_user")

        return await orchestrator.process(
            f"Analyze {symbol}",
            "stock_analysis",
            {},
            user_id=user_id,
            extra_params={"symbol": symbol, "indicators": indicators, "period_days": period_days},
        )

    @gateway.route("/api/ml/predict-price", methods=["POST"])
    async def ml_predict_price(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        prices = body.get("prices", [])
        user_id = body.get("user_id", "api_user")
        return await orchestrator.process(
            "price_prediction",
            "price_prediction",
            {},
            user_id=user_id,
            extra_params={"task": "price_prediction", "prices": prices},
        )

    @gateway.route("/api/ml/detect-anomalies", methods=["POST"])
    async def ml_detect_anomalies(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        prices = body.get("prices", [])
        user_id = body.get("user_id", "api_user")
        return await orchestrator.process(
            "anomaly_detection",
            "anomaly_detection",
            {},
            user_id=user_id,
            extra_params={"task": "anomaly_detection", "prices": prices},
        )

    @gateway.route("/api/ml/calculate-risk", methods=["POST"])
    async def ml_calculate_risk(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        prices = body.get("prices", [])
        user_id = body.get("user_id", "api_user")
        return await orchestrator.process(
            "risk_scoring",
            "risk_scoring",
            {},
            user_id=user_id,
            extra_params={"task": "risk_scoring", "prices": prices},
        )

    @gateway.route("/api/ml/analyze-sentiment", methods=["POST"])
    async def ml_analyze_sentiment(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not body:
            raise ValueError("Request body required")
        prices = body.get("prices", [])
        user_id = body.get("user_id", "api_user")
        return await orchestrator.process(
            "sentiment_analysis",
            "sentiment_analysis",
            {},
            user_id=user_id,
            extra_params={"task": "sentiment_analysis", "prices": prices},
        )

    @gateway.route("/api/knowledge/search", methods=["GET"])
    async def knowledge_search(body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = body or {}
        query = params.get("q", "")
        user_id = params.get("user_id", "api_user")
        return await orchestrator.process(
            query,
            "knowledge_query",
            {},
            user_id=user_id,
            extra_params={"query": query},
        )

    logger.info("All routes created successfully")
