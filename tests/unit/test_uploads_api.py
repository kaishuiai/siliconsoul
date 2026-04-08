import os

import pytest
from aiohttp import FormData
from aiohttp.test_utils import TestClient, TestServer

from src.api_server.server import create_app
from src.storage.storage_manager import StorageManager


@pytest.mark.asyncio
async def test_uploads_endpoint_saves_file_and_registers_file_id(tmp_path, monkeypatch):
    monkeypatch.setenv("SILICONSOUL_UPLOAD_DIR", str(tmp_path / "uploads"))

    app = create_app(config_path=None)
    app["orchestrator"].storage_manager = StorageManager(storage_type="memory")

    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        form = FormData()
        form.add_field("file", b"hello", filename="a.docx", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        resp = await client.post("/api/uploads", data=form)
        assert resp.status == 200
        payload = await resp.json()
        assert payload["status"] == "success"
        files = payload["data"]["files"]
        assert isinstance(files, list)
        assert len(files) == 1
        fid = files[0]["file_id"]
        assert isinstance(fid, str) and fid

        paths = app["orchestrator"].storage_manager.resolve_upload_paths(user_id="api_user", file_ids=[fid])
        assert len(paths) == 1
        assert os.path.exists(paths[0])
    finally:
        await client.close()
