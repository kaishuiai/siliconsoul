from datetime import datetime

from src.storage.storage_manager import StorageManager


def test_list_requests_filters_by_user_and_query():
    sm = StorageManager(storage_type="memory")
    r1 = sm.add_request("u1", "hello apple", None)
    r2 = sm.add_request("u2", "hello banana", None)
    _ = (r1, r2)

    items = sm.list_requests(user_id="u1", q="apple", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["user_id"] == "u1"
    assert "apple" in items[0]["text"]

    items = sm.list_requests(user_id="u1", q="banana", limit=10, offset=0)
    assert len(items) == 0


def test_list_requests_filters_by_consensus_and_errors():
    sm = StorageManager(storage_type="memory")
    r1 = sm.add_request("u1", "a", None)
    r2 = sm.add_request("u1", "b", None)

    sm.add_result(r1, "DemoExpert", {"ok": True}, 0.5, 1.0, error="boom")
    sm.add_aggregated(r1, {"consensus_level": "high", "overall_confidence": 0.9, "final_result": {}}, 0.9, 1.0)
    sm.add_result(r2, "DemoExpert", {"ok": True}, 0.5, 1.0, error=None)
    sm.add_aggregated(r2, {"consensus_level": "low", "overall_confidence": 0.1, "final_result": {}}, 0.1, 1.0)

    items = sm.list_requests(user_id="u1", consensus_level="high", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r1

    items = sm.list_requests(user_id="u1", only_errors=True, limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r1


def test_list_requests_filters_by_time_range_memory():
    sm = StorageManager(storage_type="memory")
    r1 = sm.add_request("u1", "old", None)
    r2 = sm.add_request("u1", "new", None)

    for r in sm.requests:
        if r.request_id == r1:
            r.timestamp = datetime.fromisoformat("2020-01-01T00:00:00")
        if r.request_id == r2:
            r.timestamp = datetime.fromisoformat("2024-01-01T00:00:00")

    items = sm.list_requests(user_id="u1", since="2023-01-01T00:00:00", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r2


def test_list_requests_filters_by_task_type_memory():
    sm = StorageManager(storage_type="memory")
    r1 = sm.add_request("u1", "a", {"_meta": {"task_type": "cfo_chat"}})
    r2 = sm.add_request("u1", "b", {"_meta": {"task_type": "stock_analysis"}})
    _ = (r1, r2)

    items = sm.list_requests(user_id="u1", task_type="cfo_chat", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["task_type"] == "cfo_chat"
