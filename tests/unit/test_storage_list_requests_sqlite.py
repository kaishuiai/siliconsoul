import sqlite3

import pytest

from src.storage.storage_manager import StorageManager


def test_sqlite_list_requests_filters_and_includes_aggregated_fields(tmp_path):
    db_path = tmp_path / "test.db"
    sm = StorageManager(storage_type="sqlite", connection_string=str(db_path))

    r1 = sm.add_request("u1", "first request", {"_meta": {"task_type": "cfo_chat", "conversation_id": "conv-1"}})
    r2 = sm.add_request("u1", "second request", {"_meta": {"task_type": "stock_analysis", "conversation_id": "conv-2"}})

    sm.add_result(r1, "DemoExpert", {"ok": True}, 0.5, 1.0, error="boom")
    sm.add_aggregated(r1, {"consensus_level": "high", "overall_confidence": 0.9, "final_result": {}}, 0.9, 1.0)

    sm.add_result(r2, "DemoExpert", {"ok": True}, 0.5, 1.0, error=None)
    sm.add_aggregated(r2, {"consensus_level": "low", "overall_confidence": 0.1, "final_result": {}}, 0.1, 1.0)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("UPDATE requests SET timestamp = ? WHERE request_id = ?", ("2020-01-01T00:00:00", r1))
    cursor.execute("UPDATE requests SET timestamp = ? WHERE request_id = ?", ("2024-01-01T00:00:00", r2))
    conn.commit()
    conn.close()

    items = sm.list_requests(user_id="u1", limit=10, offset=0)
    assert len(items) == 2
    assert "consensus_level" in items[0]
    assert "overall_confidence" in items[0]

    items = sm.list_requests(user_id="u1", consensus_level="high", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r1

    items = sm.list_requests(user_id="u1", only_errors=True, limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r1

    items = sm.list_requests(user_id="u1", expert_name="DemoExpert", limit=10, offset=0)
    assert len(items) == 2

    items = sm.list_requests(user_id="u1", since="2023-01-01T00:00:00", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r2

    items = sm.list_requests(user_id="u1", task_type="cfo_chat", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r1
    assert items[0]["conversation_id"] == "conv-1"

    items = sm.list_requests(user_id="u1", conversation_id="conv-2", limit=10, offset=0)
    assert len(items) == 1
    assert items[0]["request_id"] == r2
