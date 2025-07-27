# memory_system.py
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

class AgentMemory:
    """Simple memory system for AI agents to store and retrieve information using SQLite"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._init_database()
        self.memory = {}  # In-memory cache
    
    def _init_database(self) -> None:
        """Initialize SQLite database for persistent storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_successes (
                    id INTEGER PRIMARY KEY,
                    task_type TEXT,
                    solution TEXT,
                    timestamp TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_fixes (
                    id INTEGER PRIMARY KEY,
                    error TEXT UNIQUE,
                    fix TEXT,
                    timestamp TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    task TEXT,
                    data TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning: Could not initialize database: {e}")
    
    def store(self, task: str, data: Dict[str, Any]) -> None:
        """Store task and associated data in SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO tasks (task, data, timestamp)
                VALUES (?, ?, ?)
            ''', (task, json.dumps(data, default=str), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            print(f"💾 Stored task in memory: {task[:50]}...")
        except Exception as e:
            print(f"Warning: Could not store task: {e}")
    
    def remember_success(self, task_type: str, solution: str) -> None:
        """Store successful patterns in SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO task_successes (task_type, solution, timestamp)
                VALUES (?, ?, ?)
            ''', (task_type, solution, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            print(f"💾 Remembered success for {task_type}")
        except Exception as e:
            print(f"Warning: Could not store success: {e}")
    
    def remember_error_fix(self, error: str, fix: str) -> None:
        """Store error fixes in SQLite with UPSERT logic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO error_fixes (error, fix, timestamp)
                VALUES (?, ?, ?)
            ''', (error, fix, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            print(f"💾 Remembered fix for error: {error[:50]}...")
        except Exception as e:
            print(f"Warning: Could not store error fix: {e}")
    
    def get_similar_solutions(self, task: str) -> List[Dict]:
        """Get similar solutions using SQLite text search"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple keyword matching
            task_words = task.lower().split()
            similar_solutions = []
            
            cursor.execute('SELECT task_type, solution, timestamp FROM task_successes')
            results = cursor.fetchall()
            
            for task_type, solution, timestamp in results:
                # Check if task words appear in stored task_type
                if any(word in task_type.lower() for word in task_words):
                    similar_solutions.append({
                        'task_type': task_type,
                        'solution': solution,
                        'timestamp': timestamp
                    })
            
            conn.close()
            return similar_solutions
        except Exception as e:
            print(f"Warning: Could not retrieve similar solutions: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about stored memory from SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM tasks')
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM task_successes')
            successful_patterns = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM error_fixes')
            error_fixes = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_tasks': total_tasks,
                'successful_patterns': successful_patterns,
                'error_fixes': error_fixes
            }
        except Exception as e:
            print(f"Warning: Could not get memory stats: {e}")
            return {'total_tasks': 0, 'successful_patterns': 0, 'error_fixes': 0}
    
    def clear_memory(self) -> None:
        """Clear all stored memory from SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM tasks')
            cursor.execute('DELETE FROM task_successes')
            cursor.execute('DELETE FROM error_fixes')
            
            conn.commit()
            conn.close()
            print("🧹 Memory cleared")
        except Exception as e:
            print(f"Warning: Could not clear memory: {e}")

if __name__ == "__main__":
    print("Testing AgentMemory...")
    memory = AgentMemory()
    
    # Test storing a task
    memory.store("Create a calculator", {
        "plan": "Build a simple calculator",
        "code": "def add(a, b): return a + b",
        "result": "Success"
    })
    
    # Test remembering success
    memory.remember_success("calculator", "Simple arithmetic functions work well")
    
    # Test error fix
    memory.remember_error_fix("ModuleNotFoundError: requests", "pip install requests")
    
    # Get stats
    stats = memory.get_memory_stats()
    print(f"Memory stats: {stats}")
    
    print("✅ AgentMemory test completed")
