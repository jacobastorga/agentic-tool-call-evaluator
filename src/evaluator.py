"""
Agentic Tool Evaluator Core
Combines schema validation, execution sandboxing, and sequence DAG analysis
to produce an objective benchmark score (0.0 - 1.0) and detailed diagnostic report for LLMs.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .schema_validator import ToolSchemaValidator, ValidationResult
from .execution_sandbox import MockToolSandbox, ExecutionResult
from .dag_analyzer import ToolDAGAnalyzer, DependencyViolation

@dataclass
class EvaluationReport:
    total_calls: int
    valid_schema_count: int
    successful_execution_count: int
    dependency_violations_count: int
    overall_score: float
    is_fully_compliant: bool
    diagnostics: List[str] = field(default_factory=list)

class AgenticToolEvaluator:
    def __init__(self, tool_schemas: List[Dict[str, Any]]):
        self.validator = ToolSchemaValidator(tool_schemas)
        self.sandbox = MockToolSandbox()
        self.dag_analyzer = ToolDAGAnalyzer()

    def evaluate_trajectory(self, trajectory: List[Dict[str, Any]]) -> EvaluationReport:
        """
        Evaluates a complete agent reasoning & tool execution trajectory.
        Trajectory format:
        [
            {"tool": "calculator", "args": {"operation": "add", "a": 5, "b": 10}},
            {"tool": "write_file", "args": {"path": "/workspace/log.txt", "content": "res=15"}}
        ]
        """
        total = len(trajectory)
        if total == 0:
            return EvaluationReport(
                total_calls=0,
                valid_schema_count=0,
                successful_execution_count=0,
                dependency_violations_count=0,
                overall_score=0.0,
                is_fully_compliant=False,
                diagnostics=["Trajectory is empty."]
            )

        valid_schema = 0
        successful_exec = 0
        diagnostics = []

        for idx, call in enumerate(trajectory):
            name = call.get("tool") or call.get("name", "unknown")
            args = call.get("args") or call.get("arguments", {})

            # 1. Schema check
            schema_res = self.validator.validate_call(name, args)
            if schema_res.is_valid:
                valid_schema += 1
            else:
                diagnostics.append(f"Step {idx} [{name}] Schema Error: {schema_res.error_message}")

            # 2. Execution check
            exec_res = self.sandbox.execute(name, args)
            if exec_res.success:
                successful_exec += 1
            else:
                diagnostics.append(f"Step {idx} [{name}] Execution Error: {exec_res.error}")

        # 3. DAG order check
        dag_violations = self.dag_analyzer.analyze_sequence(trajectory)
        for v in dag_violations:
            diagnostics.append(v.description)

        # Scoring weights: 40% schema accuracy, 40% execution success, 20% causality
        schema_pct = valid_schema / total
        exec_pct = successful_exec / total
        dag_pct = max(0.0, (total - len(dag_violations)) / total)

        score = round((0.40 * schema_pct) + (0.40 * exec_pct) + (0.20 * dag_pct), 3)
        compliant = (score == 1.0) and len(diagnostics) == 0

        return EvaluationReport(
            total_calls=total,
            valid_schema_count=valid_schema,
            successful_execution_count=successful_exec,
            dependency_violations_count=len(dag_violations),
            overall_score=score,
            is_fully_compliant=compliant,
            diagnostics=diagnostics
        )
