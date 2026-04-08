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
            self.uploads: List[Dict[str, Any]] = []
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

    def add_aggregated(self, request_id: str, aggregated: Dict[str, Any], confidence: float, duration_ms: float) -> str:
        return self.add_result(
            request_id=request_id,
            expert_name="__aggregated__",
            result=aggregated,
            confidence=confidence,
            duration_ms=duration_ms,
            error=aggregated.get("error") if isinstance(aggregated, dict) else None,
        )
    
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

    def list_requests(
        self,
        user_id: Optional[str] = None,
        *,
        q: Optional[str] = None,
        expert_name: Optional[str] = None,
        task_type: Optional[str] = None,
        consensus_level: Optional[str] = None,
        only_errors: bool = False,
        since: Optional[str] = None,
        until: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 200))
        offset = max(0, int(offset))

        if self.storage_type in ["memory", "json"]:
            items = self.requests
            if user_id:
                filtered = []
                for r in items:
                    rid = r.user_id if hasattr(r, "user_id") else r.get("user_id")
                    if rid == user_id:
                        filtered.append(r)
                items = filtered
            if q:
                q_lower = str(q).lower()
                filtered = []
                for r in items:
                    text = r.text if hasattr(r, "text") else r.get("text", "")
                    if q_lower in (text or "").lower():
                        filtered.append(r)
                items = filtered

            if task_type:
                want = str(task_type)
                filtered = []
                for r in items:
                    ctx = r.context if hasattr(r, "context") else r.get("context")
                    t = None
                    if isinstance(ctx, dict):
                        meta = ctx.get("_meta")
                        if isinstance(meta, dict):
                            t = meta.get("task_type")
                    if t == want:
                        filtered.append(r)
                items = filtered

            results_list = self.results
            if expert_name:
                request_ids = set()
                for res in results_list:
                    ename = res.expert_name if hasattr(res, "expert_name") else res.get("expert_name")
                    req_id = res.request_id if hasattr(res, "request_id") else res.get("request_id")
                    if ename == expert_name and req_id:
                        request_ids.add(req_id)
                items = [r for r in items if (r.request_id if hasattr(r, "request_id") else r.get("request_id")) in request_ids]

            aggregated_map: Dict[str, Dict[str, Any]] = {}
            errors_set = set()
            for res in results_list:
                ename = res.expert_name if hasattr(res, "expert_name") else res.get("expert_name")
                if (res.error if hasattr(res, "error") else res.get("error")):
                    req_id = res.request_id if hasattr(res, "request_id") else res.get("request_id")
                    if req_id:
                        errors_set.add(req_id)
                if ename != "__aggregated__":
                    continue
                req_id = res.request_id if hasattr(res, "request_id") else res.get("request_id")
                payload = res.result if hasattr(res, "result") else res.get("result", {})
                if req_id:
                    aggregated_map[req_id] = payload or {}

            def _ts(v: Any) -> Any:
                if hasattr(v, "timestamp"):
                    return v.timestamp
                if isinstance(v, dict):
                    return v.get("timestamp")
                return None

            def _dt(v: Any) -> Optional[datetime]:
                if v is None:
                    return None
                if isinstance(v, datetime):
                    return v
                if isinstance(v, str):
                    try:
                        return datetime.fromisoformat(v)
                    except Exception:
                        return None
                return None

            since_dt = _dt(since)
            until_dt = _dt(until)
            if since_dt or until_dt:
                filtered = []
                for r in items:
                    rt = r.timestamp if hasattr(r, "timestamp") else r.get("timestamp")
                    rt_dt = _dt(rt)
                    if rt_dt is None:
                        continue
                    if since_dt and rt_dt < since_dt:
                        continue
                    if until_dt and rt_dt > until_dt:
                        continue
                    filtered.append(r)
                items = filtered

            if consensus_level:
                want = str(consensus_level)
                filtered = []
                for r in items:
                    rid = r.request_id if hasattr(r, "request_id") else r.get("request_id")
                    agg = aggregated_map.get(rid) if rid else None
                    if agg and agg.get("consensus_level") == want:
                        filtered.append(r)
                items = filtered

            if only_errors:
                items = [
                    r for r in items
                    if (r.request_id if hasattr(r, "request_id") else r.get("request_id")) in errors_set
                ]

            items = sorted(items, key=_ts, reverse=True)
            sliced = items[offset : offset + limit]
            output: List[Dict[str, Any]] = []
            for r in sliced:
                request_id = r.request_id if hasattr(r, "request_id") else r.get("request_id")
                uid = r.user_id if hasattr(r, "user_id") else r.get("user_id")
                text = r.text if hasattr(r, "text") else r.get("text")
                ts = r.timestamp.isoformat() if hasattr(r, "timestamp") else r.get("timestamp")
                task = None
                ctx = r.context if hasattr(r, "context") else r.get("context")
                if isinstance(ctx, dict):
                    meta = ctx.get("_meta")
                    if isinstance(meta, dict):
                        task = meta.get("task_type")
                row: Dict[str, Any] = {"request_id": request_id, "user_id": uid, "text": text, "timestamp": ts, "task_type": task}
                agg = aggregated_map.get(request_id)
                if agg:
                    row["consensus_level"] = agg.get("consensus_level")
                    row["overall_confidence"] = agg.get("overall_confidence")
                output.append(row)
            return output

        if self.storage_type == "sqlite":
            return self._sqlite_list_requests(
                user_id=user_id,
                q=q,
                expert_name=expert_name,
                task_type=task_type,
                consensus_level=consensus_level,
                only_errors=only_errors,
                since=since,
                until=until,
                limit=limit,
                offset=offset,
            )

        return []

    def add_upload(
        self,
        *,
        user_id: str,
        original_name: str,
        stored_path: str,
        content_type: str = "",
        file_tags: Optional[Dict[str, Any]] = None,
        file_id: Optional[str] = None,
    ) -> str:
        file_id = str(file_id or uuid.uuid4())
        row = {
            "file_id": file_id,
            "user_id": user_id,
            "original_name": original_name,
            "stored_path": stored_path,
            "content_type": content_type,
            "file_tags": file_tags or {},
            "created_at": datetime.now().isoformat(),
        }
        if self.storage_type == "memory":
            self.uploads.append(row)
            return file_id
        if self.storage_type == "json":
            self.uploads.append(row)
            self._save_json()
            return file_id
        if self.storage_type == "sqlite":
            self._sqlite_add_upload(row)
            return file_id
        return file_id

    def resolve_upload_paths(self, *, user_id: str, file_ids: List[str]) -> List[str]:
        ids = [fid for fid in (file_ids or []) if isinstance(fid, str) and fid.strip()]
        if not ids:
            return []

        if self.storage_type in ["memory", "json"]:
            path_map: Dict[str, str] = {}
            for u in self.uploads:
                if not isinstance(u, dict):
                    continue
                if u.get("user_id") != user_id:
                    continue
                fid = u.get("file_id")
                p = u.get("stored_path")
                if fid and p:
                    path_map[str(fid)] = str(p)
            return [path_map[fid] for fid in ids if fid in path_map]

        if self.storage_type == "sqlite":
            return self._sqlite_get_upload_paths(user_id=user_id, file_ids=ids)

        return []

    def resolve_upload_records(self, *, user_id: str, file_ids: List[str]) -> List[Dict[str, Any]]:
        ids = [fid for fid in (file_ids or []) if isinstance(fid, str) and fid.strip()]
        if not ids:
            return []

        if self.storage_type in ["memory", "json"]:
            out: List[Dict[str, Any]] = []
            for u in self.uploads:
                if not isinstance(u, dict):
                    continue
                if u.get("user_id") != user_id:
                    continue
                fid = u.get("file_id")
                if fid in ids:
                    out.append(u)
            out.sort(key=lambda x: ids.index(x.get("file_id")) if x.get("file_id") in ids else 0)
            return out

        if self.storage_type == "sqlite":
            return self._sqlite_get_upload_records(user_id=user_id, file_ids=ids)

        return []
    
    # ==================== JSON Storage ====================
    
    def _load_json(self):
        """Load data from JSON file"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.requests = data.get("requests", [])
                    self.results = data.get("results", [])
                    self.uploads = data.get("uploads", [])
            except Exception as e:
                print(f"Warning: Failed to load JSON storage: {e}")
                self.requests = []
                self.results = []
                self.uploads = []
        else:
            self.requests = []
            self.results = []
            self.uploads = []
    
    def _save_json(self):
        """Save data to JSON file"""
        try:
            data = {
                "requests": [r.to_dict() if isinstance(r, RequestRecord) else r for r in self.requests],
                "results": [r.to_dict() if isinstance(r, ResultRecord) else r for r in self.results],
                "uploads": [u for u in self.uploads if isinstance(u, dict)],
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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                file_id TEXT PRIMARY KEY,
                user_id TEXT,
                original_name TEXT,
                stored_path TEXT,
                content_type TEXT,
                file_tags TEXT,
                created_at DATETIME
            )
            """
        )
        
        conn.commit()
        conn.close()

    def _sqlite_add_upload(self, row: Dict[str, Any]) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO uploads (file_id, user_id, original_name, stored_path, content_type, file_tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row.get("file_id"),
                row.get("user_id"),
                row.get("original_name"),
                row.get("stored_path"),
                row.get("content_type"),
                json.dumps(row.get("file_tags") or {}, ensure_ascii=False),
                row.get("created_at"),
            ),
        )
        conn.commit()
        conn.close()

    def _sqlite_get_upload_paths(self, *, user_id: str, file_ids: List[str]) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(file_ids))
        cursor.execute(
            f"SELECT file_id, stored_path FROM uploads WHERE user_id = ? AND file_id IN ({placeholders})",
            (user_id, *file_ids),
        )
        rows = cursor.fetchall()
        conn.close()
        path_map = {r[0]: r[1] for r in rows if r and r[0] and r[1]}
        return [path_map[fid] for fid in file_ids if fid in path_map]

    def _sqlite_get_upload_records(self, *, user_id: str, file_ids: List[str]) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(file_ids))
        cursor.execute(
            f"SELECT file_id, original_name, stored_path, content_type, file_tags, created_at FROM uploads WHERE user_id = ? AND file_id IN ({placeholders})",
            (user_id, *file_ids),
        )
        rows = cursor.fetchall()
        conn.close()
        items: List[Dict[str, Any]] = []
        for r in rows:
            tags = {}
            if r[4]:
                try:
                    tags = json.loads(r[4])
                except Exception:
                    tags = {}
            items.append(
                {
                    "file_id": r[0],
                    "user_id": user_id,
                    "original_name": r[1],
                    "stored_path": r[2],
                    "content_type": r[3],
                    "file_tags": tags,
                    "created_at": r[5],
                }
            )
        items.sort(key=lambda x: file_ids.index(x.get("file_id")) if x.get("file_id") in file_ids else 0)
        return items
    
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

    def _sqlite_list_requests(
        self,
        user_id: Optional[str],
        q: Optional[str],
        expert_name: Optional[str],
        task_type: Optional[str],
        consensus_level: Optional[str],
        only_errors: bool,
        since: Optional[str],
        until: Optional[str],
        limit: int,
        offset: int,
    ) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        clauses = []
        args: List[Any] = []
        if user_id:
            clauses.append("req.user_id = ?")
            args.append(user_id)
        if q:
            clauses.append("req.text LIKE ?")
            args.append(f"%{q}%")
        if expert_name:
            clauses.append(
                "EXISTS (SELECT 1 FROM results r2 WHERE r2.request_id = req.request_id AND r2.expert_name = ?)"
            )
            args.append(expert_name)
        if task_type:
            clauses.append("req.context LIKE ?")
            args.append(f"%\"task_type\"%{task_type}%")
        if consensus_level:
            clauses.append("agg.result LIKE ?")
            args.append(f"%\"consensus_level\"%{consensus_level}%")
        if only_errors:
            clauses.append(
                "EXISTS (SELECT 1 FROM results r3 WHERE r3.request_id = req.request_id AND r3.error IS NOT NULL AND r3.error != '')"
            )
        if since:
            clauses.append("req.timestamp >= ?")
            args.append(since)
        if until:
            clauses.append("req.timestamp <= ?")
            args.append(until)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        cursor.execute(
            f"""
            SELECT
              req.request_id,
              req.user_id,
              req.text,
              req.timestamp,
              agg.result,
              req.context
            FROM requests req
            LEFT JOIN results agg
              ON agg.request_id = req.request_id AND agg.expert_name = '__aggregated__'
            {where}
            ORDER BY req.timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (*args, limit, offset),
        )
        rows = cursor.fetchall()
        conn.close()

        output: List[Dict[str, Any]] = []
        for r in rows:
            row = {"request_id": r[0], "user_id": r[1], "text": r[2], "timestamp": r[3], "task_type": None}
            if r[4]:
                try:
                    agg = json.loads(r[4])
                    row["consensus_level"] = agg.get("consensus_level")
                    row["overall_confidence"] = agg.get("overall_confidence")
                except Exception:
                    pass
            if r[5]:
                try:
                    ctx = json.loads(r[5])
                    meta = ctx.get("_meta") if isinstance(ctx, dict) else None
                    if isinstance(meta, dict):
                        row["task_type"] = meta.get("task_type")
                except Exception:
                    pass
            output.append(row)
        return output
    
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
