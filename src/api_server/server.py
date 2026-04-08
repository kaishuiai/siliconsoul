import os
import uuid
import json
from pathlib import Path
from typing import Any, Dict, Optional

from aiohttp import web

from src.api_gateway.gateway import APIGateway
from src.api_gateway.routes import create_routes
from src.api_server.facade import OrchestratorFacade
from src.auth.token_auth import parse_bearer_token, resolve_user_id


def _cors_headers() -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

def _resolve_auth_user_id(request: web.Request, orchestrator: OrchestratorFacade) -> Optional[str]:
    cfg = orchestrator.config_manager
    auth_enabled = bool(cfg.get("auth.enabled", False))
    exempt_paths = cfg.get("auth.exempt_paths", ["/api/health", "/api/me"]) or []
    tokens_map = cfg.get("auth.tokens", {}) or {}

    if not auth_enabled:
        return None

    token = parse_bearer_token(request.headers.get("Authorization"))
    user_id = resolve_user_id(token, tokens_map) if token else None
    if request.path in exempt_paths:
        return user_id
    return user_id


async def _handle_upload(request: web.Request) -> web.Response:
    orchestrator: OrchestratorFacade = request.app["orchestrator"]
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=_cors_headers())

    auth_user_id = _resolve_auth_user_id(request, orchestrator)
    auth_enabled = bool(orchestrator.config_manager.get("auth.enabled", False))
    if auth_enabled and not auth_user_id:
        return web.json_response(
            {"status": "error", "code": 401, "message": "Unauthorized"},
            status=401,
            headers=_cors_headers(),
        )
    user_id = auth_user_id or "api_user"

    if not request.content_type or "multipart" not in request.content_type.lower():
        return web.json_response(
            {"status": "error", "code": 400, "message": "Content-Type must be multipart/form-data"},
            status=400,
            headers=_cors_headers(),
        )

    reader = await request.multipart()
    uploaded: list[dict[str, Any]] = []

    base_dir = os.getenv("SILICONSOUL_UPLOAD_DIR", "data/uploads")
    upload_root = Path(base_dir) / user_id
    upload_root.mkdir(parents=True, exist_ok=True)

    while True:
        part = await reader.next()
        if part is None:
            break
        if part.filename is None:
            await part.read(decode=False)
            continue

        filename = os.path.basename(part.filename)
        ext = os.path.splitext(filename)[1].lower()
        allowed = {".pdf", ".xlsx", ".xls", ".pptx", ".docx", ".ppt", ".doc"}
        if ext not in allowed:
            await part.read(decode=False)
            continue

        file_id = str(uuid.uuid4())
        stored_path = upload_root / f"{file_id}_{filename}"
        with open(stored_path, "wb") as f:
            while True:
                chunk = await part.read_chunk()
                if not chunk:
                    break
                f.write(chunk)

        orchestrator.storage_manager.add_upload(
            user_id=user_id,
            original_name=filename,
            stored_path=str(stored_path),
            content_type=part.headers.get("Content-Type", ""),
            file_id=file_id,
        )

        uploaded.append(
            {
                "file_id": file_id,
                "original_name": filename,
            }
        )

    return web.json_response({"status": "success", "data": {"files": uploaded}}, status=200, headers=_cors_headers())


def _extract_stream_text(payload: Dict[str, Any]) -> str:
    fr = payload.get("final_result") if isinstance(payload, dict) else None
    if not isinstance(fr, dict):
        return json.dumps(payload, ensure_ascii=False)
    for key in ["answer", "response", "reply", "message", "summary", "recommendation", "analysis"]:
        v = fr.get(key)
        if isinstance(v, str) and v.strip():
            return v
    if payload.get("expert_results") and isinstance(payload["expert_results"], list):
        for x in payload["expert_results"]:
            if isinstance(x, dict) and not x.get("error"):
                rv = x.get("result")
                if isinstance(rv, str) and rv.strip():
                    return rv
                if isinstance(rv, dict):
                    return json.dumps(rv, ensure_ascii=False)
    return json.dumps(fr, ensure_ascii=False)


async def _handle_process_stream(request: web.Request) -> web.StreamResponse:
    orchestrator: OrchestratorFacade = request.app["orchestrator"]
    if request.method == "OPTIONS":
        return web.Response(status=200, headers=_cors_headers())

    auth_user_id = _resolve_auth_user_id(request, orchestrator)
    auth_enabled = bool(orchestrator.config_manager.get("auth.enabled", False))
    if auth_enabled and not auth_user_id:
        return web.json_response(
            {"status": "error", "code": 401, "message": "Unauthorized"},
            status=401,
            headers=_cors_headers(),
        )

    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}

    text = str(body.get("text", "") or "").strip()
    if not text:
        return web.json_response(
            {"status": "error", "code": 400, "message": "text required"},
            status=400,
            headers=_cors_headers(),
        )

    task_type = body.get("task_type")
    context = body.get("context") if isinstance(body.get("context"), dict) else {}
    user_id = auth_user_id or str(body.get("user_id", "api_user"))
    extra_params = body.get("extra_params") if isinstance(body.get("extra_params"), dict) else None
    expert_names = body.get("expert_names") if isinstance(body.get("expert_names"), list) else None

    resp = web.StreamResponse(
        status=200,
        headers={
            **_cors_headers(),
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
    await resp.prepare(request)
    await resp.write(b"event: start\ndata: {}\n\n")
    try:
        result = await orchestrator.process(
            text,
            task_type,
            context,
            user_id=user_id,
            extra_params=extra_params,
            expert_names=expert_names,
        )
        output = _extract_stream_text(result if isinstance(result, dict) else {})
        step = max(1, min(32, max(1, len(output) // 80)))
        for i in range(0, len(output), step):
            chunk = output[i : i + step]
            await resp.write(f"event: delta\ndata: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n".encode("utf-8"))
        done_data = {"request_id": (result or {}).get("request_id"), "done": True}
        await resp.write(f"event: done\ndata: {json.dumps(done_data, ensure_ascii=False)}\n\n".encode("utf-8"))
    except Exception as e:
        await resp.write(f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n".encode("utf-8"))
    await resp.write_eof()
    return resp


async def _handle(request: web.Request) -> web.Response:
    gateway: APIGateway = request.app["gateway"]
    orchestrator: OrchestratorFacade = request.app["orchestrator"]
    body: Optional[Dict[str, Any]] = None

    if request.method == "OPTIONS":
        return web.Response(status=200, headers=_cors_headers())

    if request.method == "GET":
        body = dict(request.query)

    if request.can_read_body and request.method in {"POST", "PUT", "PATCH"}:
        try:
            body = await request.json()
        except Exception:
            body = None

    cfg = orchestrator.config_manager
    auth_enabled = bool(cfg.get("auth.enabled", False))

    auth_user_id = _resolve_auth_user_id(request, orchestrator)
    if auth_enabled and request.path not in (cfg.get("auth.exempt_paths", ["/api/health", "/api/me"]) or []) and not auth_user_id:
        return web.json_response(
            {"status": "error", "code": 401, "message": "Unauthorized"},
            status=401,
            headers=_cors_headers(),
        )

    if body is None:
        body = {}

    if auth_user_id:
        if request.path.startswith("/api/portfolio/"):
            parts = [p for p in request.path.split("/") if p]
            if len(parts) >= 3:
                path_user_id = parts[2]
                if path_user_id != auth_user_id:
                    return web.json_response(
                        {"status": "error", "code": 403, "message": "Forbidden"},
                        status=403,
                        headers=_cors_headers(),
                    )
        if request.path.startswith("/api/history/"):
            parts = [p for p in request.path.split("/") if p]
            if len(parts) >= 3:
                path_user_id = parts[2]
                if path_user_id != auth_user_id:
                    return web.json_response(
                        {"status": "error", "code": 403, "message": "Forbidden"},
                        status=403,
                        headers=_cors_headers(),
                    )
        body["user_id"] = auth_user_id

    result = await gateway.handle_request(request.method, request.path, body)

    status = 200
    if isinstance(result, dict) and result.get("status") == "error":
        code = result.get("code")
        if isinstance(code, int):
            status = code
        else:
            status = 500

    return web.json_response(result, status=status, headers=_cors_headers())


def create_app(config_path: Optional[str] = None) -> web.Application:
    app = web.Application()
    gateway = APIGateway()
    orchestrator = OrchestratorFacade(config_path=config_path)
    create_routes(gateway, orchestrator)
    app["gateway"] = gateway
    app["orchestrator"] = orchestrator

    app.router.add_route("*", "/api/uploads", _handle_upload)
    app.router.add_route("*", "/api/process/stream", _handle_process_stream)

    app.router.add_route("*", "/{tail:.*}", _handle)
    return app


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    config_path = os.getenv("CONFIG_FILE")
    web.run_app(create_app(config_path=config_path), host=host, port=port)


if __name__ == "__main__":
    main()
