import pytest
import sys, os

# Ensure src in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.schema_validator import ToolSchemaValidator

@pytest.fixture
def sample_schemas():
    return [
        {
            "name": "calculator",
            "description": "Performs basic arithmetic.",
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
            "description": "Writes text to a file path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    ]

def test_valid_call(sample_schemas):
    validator = ToolSchemaValidator(sample_schemas)
    res = validator.validate_call("calculator", {"operation": "add", "a": 10.5, "b": 20})
    assert res.is_valid is True
    assert len(res.missing_required) == 0
    assert len(res.hallucinated_params) == 0

def test_missing_required_parameter(sample_schemas):
    validator = ToolSchemaValidator(sample_schemas)
    res = validator.validate_call("calculator", {"operation": "add", "a": 5})
    assert res.is_valid is False
    assert "b" in res.missing_required

def test_hallucinated_parameter(sample_schemas):
    validator = ToolSchemaValidator(sample_schemas)
    res = validator.validate_call("write_file", {
        "path": "/workspace/test.txt",
        "content": "sample",
        "unauthorized_flag": True  # Hallucinated param
    })
    assert res.is_valid is False
    assert "unauthorized_flag" in res.hallucinated_params

def test_type_mismatch_error(sample_schemas):
    validator = ToolSchemaValidator(sample_schemas)
    res = validator.validate_call("calculator", {
        "operation": "add",
        "a": "not_a_number",  # Wrong type
        "b": 10
    })
    assert res.is_valid is False
    assert len(res.type_errors) > 0

def test_unregistered_tool(sample_schemas):
    validator = ToolSchemaValidator(sample_schemas)
    res = validator.validate_call("deploy_cluster", {"region": "us-west-1"})
    assert res.is_valid is False
    assert "Unknown tool" in res.error_message
