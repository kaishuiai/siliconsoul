import os
import uuid
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

    app.router.add_route("*", "/{tail:.*}", _handle)
    return app


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    config_path = os.getenv("CONFIG_FILE")
    web.run_app(create_app(config_path=config_path), host=host, port=port)


if __name__ == "__main__":
    main()
