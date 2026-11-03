# Agentic Tool Call Evaluator

[![Tests](https://img.shields.io/badge/pytest-passing-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![Author](https://img.shields.io/badge/author-Jacob%20Andrew%20Astorga-orange.svg)](https://github.com/jacobastorga)

A production-grade evaluation harness and benchmarking framework for assessing autonomous coding agents and Large Language Models (LLMs) on **multi-step tool calling, JSON schema compliance, parameter hallucination detection, and causal dependency ordering**.

Built for AI model trainers, RLHF annotators, and benchmark task authors to objectively grade agentic trajectories beyond simple textual matching.

---

## 🚀 Key Architectural Capabilities

1. **Deterministic JSON Schema Validator (`src/schema_validator.py`)**:
   - Validates function call arguments against OpenAI / Anthropic format tool definitions.
   - Detects **parameter hallucinations** (keys passed by the model that do not exist in the schema).
   - Enforces strict type compliance (`string`, `integer`, `number`, `boolean`, `array`, `object`).
   - Flags missing mandatory parameters without throwing unhandled runtime exceptions.

2. **Stateful Execution Sandbox (`src/execution_sandbox.py`)**:
   - Executes invoked tool calls in a deterministic, isolated mock environment (filesystem, databases, calculator, REST endpoints).
   - Tracks environment state mutations (file creations, database inserts) to verify agent side-effects.
   - Measures tool execution latency and captures unhandled exceptions (e.g., division by zero, missing file paths).

3. **Causal Dependency DAG Analyzer (`src/dag_analyzer.py`)**:
   - Audits multi-turn tool trajectories for causal order violations.
   - Catches anti-patterns: attempting to read or execute a file before creating/staging it, or committing before staging.

4. **Scoring & Diagnostic Reporting (`src/evaluator.py`)**:
   - Computes weighted trajectory compliance scores ($0.0 - 1.0$) based on:
     - 40% Schema Validity (types, required args, no hallucinations)
     - 40% Execution Success (runtime handling, valid outputs)
     - 20% Causal Dependency Adherence (proper DAG sequence)
   - Outputs comprehensive diagnostic logs for RLHF reward modeling and SFT dataset filtering.

---

## 📂 Repository Architecture

```text
agentic-tool-call-evaluator/
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── schema_validator.py       # JSON schema & hallucination validation
│   ├── execution_sandbox.py      # Stateful mock execution environment
│   ├── dag_analyzer.py           # Multi-step causal dependency tracking
│   └── evaluator.py              # Composite scoring & diagnostic engine
└── tests/
    ├── __init__.py
    ├── test_schema_validator.py  # Schema enforcement unit tests
    ├── test_execution_sandbox.py # Sandboxed execution unit tests
    ├── test_dag_analyzer.py      # Dependency ordering unit tests
    └── test_evaluator.py         # End-to-end trajectory evaluation tests
```

---

## 🛠️ Installation & Testing

```bash
# Clone the repository
git clone https://github.com/jacobastorga/agentic-tool-call-evaluator.git
cd agentic-tool-call-evaluator

# Install dependencies
pip install -r requirements.txt

# Execute all test suites
pytest tests/ -v
```

---

## 💻 Python API Usage

```python
from src import AgenticToolEvaluator

schemas = [
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

evaluator = AgenticToolEvaluator(schemas)

trajectory = [
    {"tool": "write_file", "args": {"path": "/workspace/main.py", "content": "print('hello')"}},
    {"tool": "read_file", "args": {"path": "/workspace/main.py"}}
]

report = evaluator.evaluate_trajectory(trajectory)
print(f"Overall Score: {report.overall_score} (Compliant: {report.is_fully_compliant})")
# Output: Overall Score: 1.0 (Compliant: True)
```

---

## 👨‍💻 Author
**Jacob Andrew Astorga**  
*AI Evaluation Specialist & Software Developer*  
* GitHub: [@jacobastorga](https://github.com/jacobastorga)  
* LinkedIn: [linkedin.com/in/jacob-astorga-895405416](https://www.linkedin.com/in/jacob-astorga-895405416/)
