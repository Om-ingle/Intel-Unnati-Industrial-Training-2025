"""
SQLite Backend - Store execution logs and state
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import sqlite3
from contextlib import contextmanager

# Handle imports
try:
    from ..core import FlowExecution
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core import FlowExecution


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

CREATE_TABLES_SQL = """
-- Executions table
CREATE TABLE IF NOT EXISTS executions (
    execution_id TEXT PRIMARY KEY,
    flow_id TEXT NOT NULL,
    flow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_data TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    duration_seconds REAL,
    error TEXT,
    node_count INTEGER,
    successful_nodes INTEGER,
    failed_nodes INTEGER,
    created_at TEXT NOT NULL
);

-- Node results table
CREATE TABLE IF NOT EXISTS node_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    status TEXT NOT NULL,
    output TEXT,
    error TEXT,
    metadata TEXT,
    executed_at TEXT NOT NULL,
    FOREIGN KEY (execution_id) REFERENCES executions (execution_id)
);

-- State snapshots table
CREATE TABLE IF NOT EXISTS state_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    node_id TEXT,
    state_data TEXT NOT NULL,
    snapshot_at TEXT NOT NULL,
    FOREIGN KEY (execution_id) REFERENCES executions (execution_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_executions_flow_id ON executions(flow_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_node_results_execution ON node_results(execution_id);
"""


# ============================================================================
# SQLITE STORAGE
# ============================================================================

class SQLiteStorage:
    """
    SQLite-based storage for execution logs and state.
    
    Example:
        storage = SQLiteStorage("agent_framework.db")
        storage.save_execution(execution)
        logs = storage.get_execution("exec-123")
    """
    
    def __init__(self, db_path: str = "agent_framework.db"):
        """
        Initialize storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Create tables if they don't exist"""
        with self._get_connection() as conn:
            conn.executescript(CREATE_TABLES_SQL)
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def save_execution(self, execution: FlowExecution) -> bool:
        """
        Save or update an execution.
        
        Args:
            execution: FlowExecution to save
        
        Returns:
            True if successful
        """
        try:
            with self._get_connection() as conn:
                # Save execution
                conn.execute("""
                    INSERT OR REPLACE INTO executions (
                        execution_id, flow_id, flow_name, status,
                        input_data, started_at, completed_at,
                        duration_seconds, error, node_count,
                        successful_nodes, failed_nodes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    execution.flow_id,
                    execution.flow_name,
                    execution.status,
                    json.dumps(execution.input_data),
                    execution.started_at.isoformat() if execution.started_at else None,
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    execution.get_duration(),
                    execution.error,
                    len(execution.node_results),
                    sum(1 for r in execution.node_results.values() if r.is_success()),
                    sum(1 for r in execution.node_results.values() if r.is_failed()),
                    datetime.now().isoformat()
                ))
                
                # Save node results
                for node_id, result in execution.node_results.items():
                    conn.execute("""
                        INSERT INTO node_results (
                            execution_id, node_id, node_type, status,
                            output, error, metadata, executed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        execution.execution_id,
                        node_id,
                        result.metadata.get("node_type", "unknown"),
                        result.status.value,
                        json.dumps(result.output) if result.output else None,
                        result.error,
                        json.dumps(result.metadata),
                        result.timestamp.isoformat()
                    ))
                
                # Save state snapshot
                conn.execute("""
                    INSERT INTO state_snapshots (
                        execution_id, node_id, state_data, snapshot_at
                    ) VALUES (?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    None,  # Final state
                    json.dumps(execution.state.get_all()),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ Error saving execution: {e}")
            return False
    
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution by ID.
        
        Args:
            execution_id: Execution ID
        
        Returns:
            Execution data or None
        """
        try:
            with self._get_connection() as conn:
                # Get execution
                row = conn.execute(
                    "SELECT * FROM executions WHERE execution_id = ?",
                    (execution_id,)
                ).fetchone()
                
                if not row:
                    return None
                
                # Convert to dict
                execution = dict(row)
                execution["input_data"] = json.loads(execution["input_data"])
                
                # Get node results
                node_rows = conn.execute(
                    "SELECT * FROM node_results WHERE execution_id = ? ORDER BY id",
                    (execution_id,)
                ).fetchall()
                
                execution["node_results"] = [dict(row) for row in node_rows]
                
                return execution
                
        except Exception as e:
            print(f"❌ Error getting execution: {e}")
            return None
    
    def list_executions(
        self,
        flow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List executions with optional filters.
        
        Args:
            flow_id: Filter by flow ID
            status: Filter by status
            limit: Maximum number of results
        
        Returns:
            List of executions
        """
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM executions WHERE 1=1"
                params = []
                
                if flow_id:
                    query += " AND flow_id = ?"
                    params.append(flow_id)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(query, params).fetchall()
                
                executions = []
                for row in rows:
                    exec_dict = dict(row)
                    exec_dict["input_data"] = json.loads(exec_dict["input_data"])
                    executions.append(exec_dict)
                
                return executions
                
        except Exception as e:
            print(f"❌ Error listing executions: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            with self._get_connection() as conn:
                total = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
                completed = conn.execute(
                    "SELECT COUNT(*) FROM executions WHERE status = 'completed'"
                ).fetchone()[0]
                failed = conn.execute(
                    "SELECT COUNT(*) FROM executions WHERE status = 'failed'"
                ).fetchone()[0]
                
                return {
                    "total_executions": total,
                    "completed": completed,
                    "failed": failed,
                    "success_rate": (completed / total * 100) if total > 0 else 0
                }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing SQLite Storage...\n")
    
    # Create test database
    import tempfile
    import os
    
    temp_db = os.path.join(tempfile.gettempdir(), "test_agent_framework.db")
    if os.path.exists(temp_db):
        os.remove(temp_db)
    
    storage = SQLiteStorage(temp_db)
    print(f"✅ Database created: {temp_db}")
    
    # Create mock execution
    from core import State, NodeResult, NodeStatus
    
    execution = FlowExecution("flow-1", "Test Flow", {"input": "test"})
    execution.start()
    
    # Add mock results
    execution.node_results["node1"] = NodeResult(
        status=NodeStatus.SUCCESS,
        output="Result 1",
        metadata={"node_type": "llm_call"}
    )
    execution.node_results["node2"] = NodeResult(
        status=NodeStatus.SUCCESS,
        output="Result 2",
        metadata={"node_type": "transform"}
    )
    
    execution.complete()
    
    # Test save
    print("\n[1/4] Testing save execution...")
    success = storage.save_execution(execution)
    print(f"✅ Saved: {success}")
    
    # Test get
    print("\n[2/4] Testing get execution...")
    retrieved = storage.get_execution(execution.execution_id)
    print(f"✅ Retrieved: {retrieved['flow_name']}")
    print(f"   Status: {retrieved['status']}")
    print(f"   Nodes: {retrieved['node_count']}")
    
    # Test list
    print("\n[3/4] Testing list executions...")
    executions = storage.list_executions()
    print(f"✅ Found {len(executions)} executions")
    
    # Test statistics
    print("\n[4/4] Testing statistics...")
    stats = storage.get_statistics()
    print(f"✅ Total: {stats['total_executions']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print("\n✅ SQLite Storage is working correctly!")
    print(f"   Database file: {temp_db}")