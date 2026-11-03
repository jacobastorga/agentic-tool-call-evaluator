import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dag_analyzer import ToolDAGAnalyzer

def test_valid_dag_order():
    analyzer = ToolDAGAnalyzer()
    trajectory = [
        {"tool": "write_file", "args": {"path": "script.py", "content": "x=1"}},
        {"tool": "read_file", "args": {"path": "script.py"}},
        {"tool": "execute_script", "args": {"path": "script.py"}}
    ]
    violations = analyzer.analyze_sequence(trajectory)
    assert len(violations) == 0

def test_out_of_order_violation():
    analyzer = ToolDAGAnalyzer()
    # Attempting to execute script before writing or staging it
    trajectory = [
        {"tool": "execute_script", "args": {"path": "script.py"}}
    ]
    violations = analyzer.analyze_sequence(trajectory)
    assert len(violations) == 1
    assert violations[0].tool_name == "execute_script"
