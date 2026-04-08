import time
from typing import Any, Dict, Optional, List

from src.config.config_manager import ConfigManager
from src.core.moe_orchestrator import MOEOrchestrator
from src.core.input_validator import InputValidator
from src.experts.demo_expert_1 import DemoExpert1
from src.experts.demo_expert_2 import DemoExpert2
from src.experts.demo_expert_3 import DemoExpert3
from src.experts.stock_analysis_expert import StockAnalysisExpert
from src.experts.cfo_expert import CFOExpert
from src.experts.knowledge_expert import KnowledgeExpert
from src.experts.dialog_expert import DialogExpert
from src.experts.decision_expert import DecisionExpert
from src.experts.reflection_expert import ReflectionExpert
from src.experts.execution_expert import ExecutionExpert
from src.experts.ml_expert import MLExpert
from src.monitoring.monitor import SystemMonitor
from src.models.request_response import ExpertRequest
from src.portfolio.portfolio_manager import PortfolioManager
from src.storage.storage_manager import StorageManager


class OrchestratorFacade:
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigManager(config_path=config_path)
        timeout_sec = float(self.config_manager.get("moe.timeout_sec", 5.0))
        self.moe = MOEOrchestrator(default_timeout_sec=timeout_sec)
        self.monitor = SystemMonitor()
        self.request_count = 0

        storage_type = str(self.config_manager.get("storage.type", "memory"))
        storage_conn = str(self.config_manager.get("storage.connection_string", ""))
        if storage_type == "sqlite" and not storage_conn:
            storage_conn = "data/siliconsoul.db"
        if storage_type == "json" and not storage_conn:
            storage_conn = "data/siliconsoul.json"
        self.storage_manager = StorageManager(storage_type=storage_type, connection_string=storage_conn)

        portfolio_storage_type = str(self.config_manager.get("portfolio.type", self.config_manager.get("storage.type", "memory")))
        portfolio_conn = str(self.config_manager.get("portfolio.connection_string", self.config_manager.get("portfolio.file", "")))
        if portfolio_storage_type == "sqlite" and not portfolio_conn:
            portfolio_conn = "data/siliconsoul.db"
        if portfolio_storage_type == "json" and not portfolio_conn:
            portfolio_conn = "data/portfolio.json"
        self.portfolio_manager = PortfolioManager(storage_type=portfolio_storage_type, connection_string=portfolio_conn)

        for expert in [
            DemoExpert1(),
            DemoExpert2(),
            DemoExpert3(),
            StockAnalysisExpert(),
            CFOExpert(self.config_manager),
            KnowledgeExpert(),
            DialogExpert(),
            DecisionExpert(),
            ReflectionExpert(),
            ExecutionExpert(),
            MLExpert(),
        ]:
            self.moe.register_expert(expert)

    @property
    def experts(self):
        return self.moe.experts

    async def process(
        self,
        text: str,
        task_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        *,
        user_id: str = "api_user",
        extra_params: Optional[Dict[str, Any]] = None,
        expert_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        self.request_count += 1

        ok, err, sanitized, validated_user_id = InputValidator.validate_and_sanitize(text, user_id)
        if not ok:
            raise ValueError(err)

        merged_context: Dict[str, Any] = {}
        if isinstance(context, dict):
            merged_context.update(context)
        merged_context["_meta"] = {
            "task_type": task_type,
            "extra_params": extra_params if isinstance(extra_params, dict) else {},
        }

        resolved_extra_params: Optional[Dict[str, Any]] = extra_params if isinstance(extra_params, dict) else None
        if isinstance(resolved_extra_params, dict):
            file_ids = resolved_extra_params.get("file_ids")
            if isinstance(file_ids, list) and file_ids:
                file_ids_norm = [str(x) for x in file_ids]
                paths = self.storage_manager.resolve_upload_paths(user_id=validated_user_id, file_ids=file_ids_norm)
                if paths:
                    resolved_extra_params = dict(resolved_extra_params)
                    resolved_extra_params["file_paths"] = paths
                    if len(paths) == 1:
                        resolved_extra_params["file_path"] = paths[0]
                    file_tags = resolved_extra_params.get("file_tags")
                    if isinstance(file_tags, dict):
                        file_id_to_path = {}
                        resolved_records = self.storage_manager.resolve_upload_records(user_id=validated_user_id, file_ids=file_ids_norm)
                        for r in resolved_records:
                            fid = r.get("file_id")
                            p = r.get("stored_path")
                            if fid and p:
                                file_id_to_path[str(fid)] = str(p)
                        by_path: Dict[str, Any] = {}
                        for fid, tag in file_tags.items():
                            p = file_id_to_path.get(str(fid))
                            if not p:
                                continue
                            by_path[p] = tag
                        if by_path:
                            resolved_extra_params["file_tags_by_path"] = by_path

        request_id = self.storage_manager.add_request(validated_user_id, sanitized, context=merged_context)
        request = ExpertRequest(
            text=sanitized,
            user_id=validated_user_id,
            context=merged_context,
            task_type=task_type,
            extra_params=resolved_extra_params,
        )

        selected_expert_names = expert_names
        if selected_expert_names is not None:
            selected_expert_names = [n for n in selected_expert_names if n in self.moe.experts]
            selected_expert_names = selected_expert_names or None
        elif task_type:
            names = []
            for name, expert in self.moe.experts.items():
                supported = getattr(expert, "supported_tasks", [])
                if task_type in supported:
                    names.append(name)
            selected_expert_names = names or None

        t0 = time.time()
        aggregated = await self.moe.process_request(
            request,
            expert_names=selected_expert_names,
            timeout_sec=float(self.config_manager.get("moe.timeout_sec", 5.0)),
        )
        duration_ms = (time.time() - t0) * 1000
        self.monitor.record_request(duration_ms, success=(aggregated.final_result.get("error") is None))
        for r in aggregated.expert_results:
            self.storage_manager.add_result(
                request_id=request_id,
                expert_name=r.expert_name,
                result=r.result,
                confidence=r.confidence,
                duration_ms=r.duration_ms,
                error=r.error,
            )
        self.storage_manager.add_aggregated(
            request_id=request_id,
            aggregated={
                "final_result": aggregated.final_result,
                "overall_confidence": aggregated.overall_confidence,
                "consensus_level": aggregated.consensus_level,
                "num_experts": aggregated.num_experts,
            },
            confidence=aggregated.overall_confidence,
            duration_ms=aggregated.duration_ms,
        )

        payload = aggregated.model_dump()
        payload["request_id"] = request_id
        return payload

    async def batch_process(
        self,
        requests: List[Dict[str, Any]],
        *,
        user_id: str = "api_user",
    ) -> Dict[str, Any]:
        items: List[Dict[str, Any]] = []
        success = 0
        failed = 0
        duration_total_ms = 0.0
        for idx, req in enumerate(requests):
            started = time.time()
            try:
                payload = await self.process(
                    req.get("text", ""),
                    req.get("task_type"),
                    req.get("context", {}),
                    user_id=req.get("user_id", user_id),
                    extra_params=req.get("extra_params"),
                    expert_names=req.get("expert_names"),
                )
                took_ms = (time.time() - started) * 1000
                duration_total_ms += took_ms
                success += 1
                items.append(
                    {
                        "index": idx,
                        "status": "success",
                        "success": True,
                        "request": req,
                        "duration_ms": round(took_ms, 2),
                        "data": payload,
                    }
                )
            except Exception as e:
                took_ms = (time.time() - started) * 1000
                duration_total_ms += took_ms
                failed += 1
                items.append(
                    {
                        "index": idx,
                        "status": "error",
                        "success": False,
                        "request": req,
                        "duration_ms": round(took_ms, 2),
                        "error": {"message": str(e)},
                    }
                )
        total = len(requests)
        avg_ms = duration_total_ms / total if total > 0 else 0.0
        return {
            "items": items,
            "summary": {
                "total": total,
                "success": success,
                "failed": failed,
                "avg_duration_ms": round(avg_ms, 2),
            },
        }
