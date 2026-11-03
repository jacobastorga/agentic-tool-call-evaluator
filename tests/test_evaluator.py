import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluator import AgenticToolEvaluator

@pytest.fixture
def evaluator():
    schemas = [
        {
            "name": "calculator",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        },
        {
            "name": "write_file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "read_file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    ]
    return AgenticToolEvaluator(schemas)

def test_flawless_trajectory(evaluator):
    trajectory = [
        {"tool": "write_file", "args": {"path": "/workspace/res.txt", "content": "42"}},
        {"tool": "read_file", "args": {"path": "/workspace/res.txt"}},
        {"tool": "calculator", "args": {"operation": "add", "a": 10, "b": 32}}
    ]
    report = evaluator.evaluate_trajectory(trajectory)
    assert report.is_fully_compliant is True
    assert report.overall_score == 1.0
    assert len(report.diagnostics) == 0

def test_flawed_trajectory_with_hallucinations_and_failures(evaluator):
    trajectory = [
        # Missing required parameter and division by zero
        {"tool": "calculator", "args": {"operation": "divide", "a": 10}},
        # Unregistered tool
        {"tool": "send_email", "args": {"recipient": "admin@example.com"}}
    ]
    report = evaluator.evaluate_trajectory(trajectory)
    assert report.is_fully_compliant is False
    assert report.overall_score < 0.5
    assert len(report.diagnostics) > 0
