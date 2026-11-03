"""
Schema Validator Module
Validates LLM-generated function call payloads against defined JSON schemas,
detecting type mismatches, missing required arguments, and hallucinated parameters.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    is_valid: bool
    function_name: str
    missing_required: List[str] = field(default_factory=list)
    hallucinated_params: List[str] = field(default_factory=list)
    type_errors: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

class ToolSchemaValidator:
    def __init__(self, tool_schemas: List[Dict[str, Any]]):
        """
        Initialize with a list of OpenAI / Anthropic format tool definitions.
        """
        self.schemas: Dict[str, Dict[str, Any]] = {}
        for tool in tool_schemas:
            name = tool.get("name") or tool.get("function", {}).get("name")
            spec = tool.get("parameters") or tool.get("function", {}).get("parameters", {})
            if name:
                self.schemas[name] = spec

    def validate_call(self, function_name: str, arguments: Dict[str, Any]) -> ValidationResult:
        if function_name not in self.schemas:
            return ValidationResult(
                is_valid=False,
                function_name=function_name,
                error_message=f"Unknown tool '{function_name}'. Not found in registered tool specifications."
            )

        spec = self.schemas[function_name]
        expected_props = spec.get("properties", {})
        required_fields = spec.get("required", [])

        missing_required = [f for f in required_fields if f not in arguments]
        hallucinated_params = [k for k in arguments.keys() if k not in expected_props]

        type_errors = []
        for key, val in arguments.items():
            if key in expected_props:
                prop_type = expected_props[key].get("type")
                if prop_type and not self._check_type(val, prop_type):
                    type_errors.append(
                        f"Field '{key}' expected type '{prop_type}', got '{type(val).__name__}' with value: {val!r}"
                    )

        is_valid = len(missing_required) == 0 and len(hallucinated_params) == 0 and len(type_errors) == 0

        err_parts = []
        if missing_required:
            err_parts.append(f"Missing required arguments: {missing_required}")
        if hallucinated_params:
            err_parts.append(f"Hallucinated unexpected parameters: {hallucinated_params}")
        if type_errors:
            err_parts.append("; ".join(type_errors))

        return ValidationResult(
            is_valid=is_valid,
            function_name=function_name,
            missing_required=missing_required,
            hallucinated_params=hallucinated_params,
            type_errors=type_errors,
            error_message=" | ".join(err_parts) if err_parts else None
        )

    def _check_type(self, val: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(val, str)
        elif expected_type == "integer":
            return isinstance(val, int) and not isinstance(val, bool)
        elif expected_type == "number":
            return isinstance(val, (int, float)) and not isinstance(val, bool)
        elif expected_type == "boolean":
            return isinstance(val, bool)
        elif expected_type == "array":
            return isinstance(val, list)
        elif expected_type == "object":
            return isinstance(val, dict)
        return True
