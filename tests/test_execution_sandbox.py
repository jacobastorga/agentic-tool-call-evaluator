import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.execution_sandbox import MockToolSandbox

def test_calculator_execution():
    sandbox = MockToolSandbox()
    res = sandbox.execute("calculator", {"operation": "multiply", "a": 6, "b": 7})
    assert res.success is True
    assert res.output == 42.0

def test_division_by_zero():
    sandbox = MockToolSandbox()
    res = sandbox.execute("calculator", {"operation": "divide", "a": 10, "b": 0})
    assert res.success is False
    assert "Division by zero" in res.error

def test_stateful_file_operations():
    sandbox = MockToolSandbox()
    # Write file
    w_res = sandbox.execute("write_file", {"path": "/workspace/config.json", "content": "{\"mode\": \"prod\"}"})
    assert w_res.success is True
    assert w_res.state_mutated is True

    # Read back file
    r_res = sandbox.execute("read_file", {"path": "/workspace/config.json"})
    assert r_res.success is True
    assert "prod" in r_res.output

def test_read_nonexistent_file():
    sandbox = MockToolSandbox()
    res = sandbox.execute("read_file", {"path": "/workspace/ghost.txt"})
    assert res.success is False
    assert "does not exist" in res.error
