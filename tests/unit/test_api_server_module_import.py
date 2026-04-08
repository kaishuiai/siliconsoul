from src.api_server import server


def test_server_module_import_and_cors_headers():
    headers = server._cors_headers()
    assert "Access-Control-Allow-Origin" in headers


def test_create_app_builds_gateway():
    app = server.create_app(config_path=None)
    assert "gateway" in app
    assert "orchestrator" in app


def test_extract_stream_text_prefers_final_result_fields():
    payload = {
        "final_result": {"answer": "hello"},
        "expert_results": [{"result": {"x": 1}}],
    }
    assert server._extract_stream_text(payload) == "hello"
