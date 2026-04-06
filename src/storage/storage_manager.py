"""
Storage Manager

Provides abstraction for different storage backends.
Supports: memory, file-based (JSON), SQLite
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.storage.models import RequestRecord, ResultRecord


class StorageManager:
    """
    Unified storage interface supporting multiple backends.
    
    Features:
    - Memory storage (in-process)
    - JSON file storage (local)
    - SQLite storage (embedded)
    - Query and filtering
    - Automatic cleanup
    """
    
    def __init__(self, storage_type: str = "memory", connection_string: str = ""):
        """
        Initialize storage manager.
        
        Args:
            storage_type: "memory", "json", or "sqlite"
            connection_string: Connection details (file path or DB URI)
        """
        self.storage_type = storage_type
        self.connection_string = connection_string
        
        # Initialize storage
        if storage_type == "memory":
            self.requests: List[RequestRecord] = []
            self.results: List[ResultRecord] = []
        elif storage_type == "json":
            self.file_path = Path(connection_string or "siliconsoul.json")
            self._load_json()
        elif storage_type == "sqlite":
            self.db_path = connection_string or ":memory:"
            self._init_sqlite()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        # Statistics
        self.request_count = 0
        self.result_count = 0
    
    # ==================== Memory Storage ====================
    
    def add_request(self, user_id: str, text: str, context: Optional[Dict] = None) -> str:
        """
        Add request record.
        
        Args:
            user_id: User ID
            text: Request text
            context: Optional context
        
        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        
        if self.storage_type == "memory":
            record = RequestRecord(
                request_id=request_id,
                user_id=user_id,
                text=text,
                timestamp=datetime.now(),
                context=context
            )
            self.requests.append(record)
        elif self.storage_type == "json":
            record = RequestRecord(
                request_id=request_id,
                user_id=user_id,
                text=text,
                timestamp=datetime.now(),
                context=context
            )
            self.requests.append(record)
            self._save_json()
        elif self.storage_type == "sqlite":
            self._sqlite_add_request(request_id, user_id, text, context)
        
        self.request_count += 1
        return request_id
    
    def add_result(self,
                   request_id: str,
                   expert_name: str,
                   result: Dict,
                   confidence: float,
                   duration_ms: float,
                   error: Optional[str] = None) -> str:
        """
        Add result record.
        
        Args:
            request_id: Associated request ID
            expert_name: Name of Expert
            result: Result data
            confidence: Confidence score
            duration_ms: Execution duration
            error: Optional error message
        
        Returns:
            Result ID
        """
        result_id = str(uuid.uuid4())
        
        if self.storage_type == "memory":
            record = ResultRecord(
                result_id=result_id,
                request_id=request_id,
                expert_name=expert_name,
                result=result,
                confidence=confidence,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                error=error
            )
            self.results.append(record)
        elif self.storage_type == "json":
            record = ResultRecord(
                result_id=result_id,
                request_id=request_id,
                expert_name=expert_name,
                result=result,
                confidence=confidence,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                error=error
            )
            self.results.append(record)
            self._save_json()
        elif self.storage_type == "sqlite":
            self._sqlite_add_result(result_id, request_id, expert_name, result, confidence, duration_ms, error)
        
        self.result_count += 1
        return result_id
    
    def get_request(self, request_id: str) -> Optional[RequestRecord]:
        """Get request by ID"""
        if self.storage_type == "memory" or self.storage_type == "json":
            for req in self.requests:
                if req.request_id == request_id:
                    return req
        elif self.storage_type == "sqlite":
            return self._sqlite_get_request(request_id)
        return None
    
    def get_results(self, request_id: str) -> List[ResultRecord]:
        """Get all results for a request"""
        if self.storage_type == "memory" or self.storage_type == "json":
            return [r for r in self.results if r.request_id == request_id]
        elif self.storage_type == "sqlite":
            return self._sqlite_get_results(request_id)
        return []
    
    def get_expert_stats(self) -> Dict[str, Any]:
        """Get statistics by Expert"""
        stats = {}
        
        results_list = self.results if self.storage_type in ["memory", "json"] else self._sqlite_get_all_results()
        
        for result in results_list:
            expert_name = result.expert_name
            if expert_name not in stats:
                stats[expert_name] = {
                    "count": 0,
                    "avg_confidence": 0,
                    "avg_duration": 0,
                    "errors": 0
                }
            
            stats[expert_name]["count"] += 1
            stats[expert_name]["avg_confidence"] = (
                (stats[expert_name]["avg_confidence"] * (stats[expert_name]["count"] - 1) + result.confidence) /
                stats[expert_name]["count"]
            )
            stats[expert_name]["avg_duration"] = (
                (stats[expert_name]["avg_duration"] * (stats[expert_name]["count"] - 1) + result.duration_ms) /
                stats[expert_name]["count"]
            )
            if result.error:
                stats[expert_name]["errors"] += 1
        
        return stats
    
    # ==================== JSON Storage ====================
    
    def _load_json(self):
        """Load data from JSON file"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.requests = data.get("requests", [])
                    self.results = data.get("results", [])
            except Exception as e:
                print(f"Warning: Failed to load JSON storage: {e}")
                self.requests = []
                self.results = []
        else:
            self.requests = []
            self.results = []
    
    def _save_json(self):
        """Save data to JSON file"""
        try:
            data = {
                "requests": [r.to_dict() if isinstance(r, RequestRecord) else r for r in self.requests],
                "results": [r.to_dict() if isinstance(r, ResultRecord) else r for r in self.results]
            }
            
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save JSON storage: {e}")
    
    # ==================== SQLite Storage ====================
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                request_id TEXT PRIMARY KEY,
                user_id TEXT,
                text TEXT,
                timestamp DATETIME,
                context TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id TEXT PRIMARY KEY,
                request_id TEXT,
                expert_name TEXT,
                result TEXT,
                confidence REAL,
                duration_ms REAL,
                timestamp DATETIME,
                error TEXT,
                FOREIGN KEY (request_id) REFERENCES requests(request_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _sqlite_add_request(self, request_id: str, user_id: str, text: str, context: Optional[Dict]):
        """Add request to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        context_json = json.dumps(context) if context else None
        
        cursor.execute("""
            INSERT INTO requests (request_id, user_id, text, timestamp, context)
            VALUES (?, ?, ?, ?, ?)
        """, (request_id, user_id, text, datetime.now().isoformat(), context_json))
        
        conn.commit()
        conn.close()
    
    def _sqlite_add_result(self,
                           result_id: str,
                           request_id: str,
                           expert_name: str,
                           result: Dict,
                           confidence: float,
                           duration_ms: float,
                           error: Optional[str]):
        """Add result to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        result_json = json.dumps(result)
        
        cursor.execute("""
            INSERT INTO results (result_id, request_id, expert_name, result, confidence, duration_ms, timestamp, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (result_id, request_id, expert_name, result_json, confidence, duration_ms, datetime.now().isoformat(), error))
        
        conn.commit()
        conn.close()
    
    def _sqlite_get_request(self, request_id: str) -> Optional[RequestRecord]:
        """Get request from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM requests WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return RequestRecord(
            request_id=row[0],
            user_id=row[1],
            text=row[2],
            timestamp=datetime.fromisoformat(row[3]),
            context=json.loads(row[4]) if row[4] else None
        )
    
    def _sqlite_get_results(self, request_id: str) -> List[ResultRecord]:
        """Get results from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM results WHERE request_id = ?", (request_id,))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append(ResultRecord(
                result_id=row[0],
                request_id=row[1],
                expert_name=row[2],
                result=json.loads(row[3]),
                confidence=row[4],
                duration_ms=row[5],
                timestamp=datetime.fromisoformat(row[6]),
                error=row[7]
            ))
        
        return results
    
    def _sqlite_get_all_results(self) -> List[ResultRecord]:
        """Get all results from SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM results")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append(ResultRecord(
                result_id=row[0],
                request_id=row[1],
                expert_name=row[2],
                result=json.loads(row[3]),
                confidence=row[4],
                duration_ms=row[5],
                timestamp=datetime.fromisoformat(row[6]),
                error=row[7]
            ))
        
        return results
    
    # ==================== Utilities ====================
    
    def clear(self) -> None:
        """Clear all storage"""
        if self.storage_type == "memory":
            self.requests.clear()
            self.results.clear()
        elif self.storage_type == "json":
            self.requests.clear()
            self.results.clear()
            self._save_json()
        elif self.storage_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM results")
            cursor.execute("DELETE FROM requests")
            conn.commit()
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            "storage_type": self.storage_type,
            "request_count": self.request_count,
            "result_count": self.result_count,
            "requests_stored": len(self.requests) if self.storage_type in ["memory", "json"] else "N/A",
            "results_stored": len(self.results) if self.storage_type in ["memory", "json"] else "N/A"
        }
