"""
Execution Sandbox Module
Simulates safe, deterministic execution of model-invoked tool calls in a stateful mock environment.
Supports mock database queries, HTTP endpoints, file operations, and calculation tools.
"""

from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
import time

@dataclass
class ExecutionResult:
    success: bool
    output: Any
    execution_time_ms: float
    error: Optional[str] = None
    state_mutated: bool = False

class MockToolSandbox:
    def __init__(self):
        self.tool_handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self.state: Dict[str, Any] = {
            "filesystem": {"/workspace/main.py": "print('hello world')"},
            "database": {"users": [{"id": 1, "username": "admin", "role": "superuser"}]},
            "environment": {"API_KEY": "sandbox-secret-123"}
        }
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool("calculator", self._tool_calculator)
        self.register_tool("read_file", self._tool_read_file)
        self.register_tool("write_file", self._tool_write_file)
        self.register_tool("query_db", self._tool_query_db)

    def register_tool(self, name: str, handler: Callable[[Dict[str, Any]], Any]):
        self.tool_handlers[name] = handler

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> ExecutionResult:
        if tool_name not in self.tool_handlers:
            return ExecutionResult(
                success=False,
                output=None,
                execution_time_ms=0.0,
                error=f"Tool '{tool_name}' handler not implemented in sandbox."
            )

        start = time.perf_counter()
        initial_fs_len = len(self.state["filesystem"])
        try:
            handler = self.tool_handlers[tool_name]
            out = handler(arguments)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            mutated = len(self.state["filesystem"]) != initial_fs_len or tool_name == "write_file"
            return ExecutionResult(
                success=True,
                output=out,
                execution_time_ms=elapsed_ms,
                state_mutated=mutated
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return ExecutionResult(
                success=False,
                output=None,
                execution_time_ms=elapsed_ms,
                error=str(e)
            )

    def _tool_calculator(self, args: Dict[str, Any]) -> float:
        op = args.get("operation")
        a = float(args.get("a", 0))
        b = float(args.get("b", 0))
        if op == "add":
            return a + b
        elif op == "subtract":
            return a - b
        elif op == "multiply":
            return a * b
        elif op == "divide":
            if b == 0:
                raise ZeroDivisionError("Division by zero in calculator tool.")
            return a / b
        raise ValueError(f"Unsupported operation '{op}'")

    def _tool_read_file(self, args: Dict[str, Any]) -> str:
        path = args.get("path")
        if path not in self.state["filesystem"]:
            raise FileNotFoundError(f"File '{path}' does not exist.")
        return self.state["filesystem"][path]

    def _tool_write_file(self, args: Dict[str, Any]) -> str:
        path = args.get("path")
        content = args.get("content", "")
        self.state["filesystem"][path] = content
        return f"Successfully wrote {len(content)} bytes to {path}."

    def _tool_query_db(self, args: Dict[str, Any]) -> list:
        table = args.get("table")
        if table not in self.state["database"]:
            raise KeyError(f"Table '{table}' not found in database.")
        return self.state["database"][table]
