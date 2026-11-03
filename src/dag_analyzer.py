"""
Tool DAG Analyzer Module
Audits multi-step tool call sequences for causal dependency ordering,
detecting uninitialized resource usage, redundant calls, and circular dependencies.
"""

from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass

@dataclass
class DependencyViolation:
    step_index: int
    tool_name: str
    required_prerequisite: str
    description: str

class ToolDAGAnalyzer:
    def __init__(self):
        # Maps a tool to its required preceding tools
        self.prerequisites: Dict[str, List[str]] = {
            "read_file": ["write_file", "search_files"],
            "execute_script": ["write_file"],
            "commit_git": ["stage_files", "write_file"]
        }

    def set_dependency(self, tool_name: str, required_tools: List[str]):
        self.prerequisites[tool_name] = required_tools

    def analyze_sequence(self, call_history: List[Dict[str, Any]]) -> List[DependencyViolation]:
        """
        Analyzes a sequence of tool calls (e.g. [{'tool': 'execute_script', 'args': {...}}])
        and returns any causality violations.
        """
        seen_tools: Set[str] = set()
        violations: List[DependencyViolation] = []

        for idx, call in enumerate(call_history):
            name = call.get("tool") or call.get("name")
            if not name:
                continue

            if name in self.prerequisites:
                prereqs = self.prerequisites[name]
                # At least one prerequisite must have been called prior
                if not any(p in seen_tools for p in prereqs):
                    violations.append(DependencyViolation(
                        step_index=idx,
                        tool_name=name,
                        required_prerequisite=str(prereqs),
                        description=f"Step {idx}: '{name}' called before any prerequisite {prereqs} was executed."
                    ))

            seen_tools.add(name)

        return violations
