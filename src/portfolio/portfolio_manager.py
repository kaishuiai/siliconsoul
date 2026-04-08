import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class PortfolioManager:
    def __init__(self, storage_type: str = "memory", connection_string: str = ""):
        self.storage_type = storage_type
        self.connection_string = connection_string
        self._memory: Dict[str, Dict[str, Dict[str, Any]]] = {}

        if self.storage_type == "json":
            self.file_path = Path(connection_string or "data/portfolio.json")
            self._load_json()
        elif self.storage_type == "sqlite":
            self.db_path = connection_string or "data/siliconsoul.db"
            self._init_sqlite()
        elif self.storage_type != "memory":
            raise ValueError(f"Unsupported storage type: {storage_type}")

    def get_portfolio(self, user_id: str) -> Dict[str, Any]:
        positions = self._get_positions(user_id)
        return {
            "user_id": user_id,
            "positions": [
                {
                    "symbol": symbol,
                    "quantity": pos.get("quantity", 0),
                    "updated_at": pos.get("updated_at"),
                }
                for symbol, pos in sorted(positions.items(), key=lambda x: x[0])
            ],
        }

    def update_position(self, user_id: str, symbol: str, quantity: int) -> Dict[str, Any]:
        symbol = (symbol or "").strip()
        if not symbol:
            raise ValueError("symbol required")
        if not isinstance(quantity, int):
            raise ValueError("quantity must be int")

        now = datetime.now().isoformat()
        if self.storage_type == "memory":
            self._memory.setdefault(user_id, {})
            if quantity <= 0:
                self._memory[user_id].pop(symbol, None)
            else:
                self._memory[user_id][symbol] = {"quantity": quantity, "updated_at": now}
            return {"symbol": symbol, "quantity": quantity, "updated_at": now}

        if self.storage_type == "json":
            self._memory.setdefault(user_id, {})
            if quantity <= 0:
                self._memory[user_id].pop(symbol, None)
            else:
                self._memory[user_id][symbol] = {"quantity": quantity, "updated_at": now}
            self._save_json()
            return {"symbol": symbol, "quantity": quantity, "updated_at": now}

        if self.storage_type == "sqlite":
            self._sqlite_upsert_position(user_id, symbol, quantity, now)
            return {"symbol": symbol, "quantity": quantity, "updated_at": now}

        raise ValueError(f"Unsupported storage type: {self.storage_type}")

    def get_stats(self, user_id: str) -> Dict[str, Any]:
        positions = self._get_positions(user_id)
        total_quantity = sum(int(v.get("quantity", 0)) for v in positions.values())
        return {
            "user_id": user_id,
            "positions_count": len(positions),
            "total_quantity": total_quantity,
            "symbols": sorted(list(positions.keys())),
        }

    def _get_positions(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        if self.storage_type in {"memory", "json"}:
            return self._memory.get(user_id, {})
        if self.storage_type == "sqlite":
            return self._sqlite_get_positions(user_id)
        return {}

    def _load_json(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._memory = data
            except Exception:
                self._memory = {}
        else:
            self._memory = {}

    def _save_json(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(self._memory, f, indent=2, ensure_ascii=False)

    def _init_sqlite(self) -> None:
        Path(os.path.dirname(self.db_path) or ".").mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_positions (
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, symbol)
            )
            """
        )
        conn.commit()
        conn.close()

    def _sqlite_upsert_position(self, user_id: str, symbol: str, quantity: int, updated_at: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if quantity <= 0:
            cursor.execute(
                "DELETE FROM portfolio_positions WHERE user_id = ? AND symbol = ?",
                (user_id, symbol),
            )
        else:
            cursor.execute(
                """
                INSERT INTO portfolio_positions (user_id, symbol, quantity, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, symbol) DO UPDATE SET
                    quantity=excluded.quantity,
                    updated_at=excluded.updated_at
                """,
                (user_id, symbol, int(quantity), updated_at),
            )
        conn.commit()
        conn.close()

    def _sqlite_get_positions(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT symbol, quantity, updated_at FROM portfolio_positions WHERE user_id = ?",
            (user_id,),
        )
        rows = cursor.fetchall()
        conn.close()
        positions: Dict[str, Dict[str, Any]] = {}
        for symbol, quantity, updated_at in rows:
            positions[symbol] = {"quantity": int(quantity), "updated_at": updated_at}
        return positions
