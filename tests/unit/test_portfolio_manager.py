import os

import pytest

from src.portfolio.portfolio_manager import PortfolioManager


def test_portfolio_manager_memory_crud():
    pm = PortfolioManager(storage_type="memory")

    assert pm.get_portfolio("u1")["positions"] == []

    pm.update_position("u1", "600000.SH", 100)
    portfolio = pm.get_portfolio("u1")
    assert portfolio["user_id"] == "u1"
    assert portfolio["positions"][0]["symbol"] == "600000.SH"
    assert portfolio["positions"][0]["quantity"] == 100

    stats = pm.get_stats("u1")
    assert stats["positions_count"] == 1
    assert stats["total_quantity"] == 100

    pm.update_position("u1", "600000.SH", 0)
    assert pm.get_stats("u1")["positions_count"] == 0


def test_portfolio_manager_json_persistence(tmp_path):
    file_path = tmp_path / "portfolio.json"
    pm = PortfolioManager(storage_type="json", connection_string=str(file_path))

    pm.update_position("u1", "AAPL", 3)
    assert file_path.exists()

    pm2 = PortfolioManager(storage_type="json", connection_string=str(file_path))
    portfolio = pm2.get_portfolio("u1")
    assert len(portfolio["positions"]) == 1
    assert portfolio["positions"][0]["symbol"] == "AAPL"
    assert portfolio["positions"][0]["quantity"] == 3


def test_portfolio_manager_sqlite_persistence(tmp_path):
    db_path = tmp_path / "test.db"
    pm = PortfolioManager(storage_type="sqlite", connection_string=str(db_path))
    pm.update_position("u1", "MSFT", 5)

    pm2 = PortfolioManager(storage_type="sqlite", connection_string=str(db_path))
    portfolio = pm2.get_portfolio("u1")
    assert len(portfolio["positions"]) == 1
    assert portfolio["positions"][0]["symbol"] == "MSFT"
    assert portfolio["positions"][0]["quantity"] == 5


@pytest.mark.parametrize(
    "symbol,quantity",
    [
        ("", 1),
        ("   ", 1),
    ],
)
def test_portfolio_manager_validation(symbol, quantity):
    pm = PortfolioManager(storage_type="memory")
    with pytest.raises(ValueError):
        pm.update_position("u1", symbol, quantity)


def test_portfolio_manager_rejects_unknown_storage():
    with pytest.raises(ValueError):
        PortfolioManager(storage_type="unknown")


def test_portfolio_manager_sqlite_delete(tmp_path):
    db_path = tmp_path / "test.db"
    pm = PortfolioManager(storage_type="sqlite", connection_string=str(db_path))
    pm.update_position("u1", "TSLA", 1)
    assert pm.get_stats("u1")["positions_count"] == 1
    pm.update_position("u1", "TSLA", 0)
    assert pm.get_stats("u1")["positions_count"] == 0

