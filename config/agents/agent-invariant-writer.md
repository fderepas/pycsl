# agent-invariant-writer

## Purpose

Step 3 of the 3-agent annotation pipeline. Receives a Python function + function-level contracts (from `agent-contract-writer`) + callee contracts (from the splitter) and produces the fully annotated function ready for PyCSL verification.

## Interface

**Callable as**: Python module (`generate()` function), imported by `agent-writer.py`.

**Input**:
- `function_source` (str): Raw Python function source code
- `contracts` (str): Contract lines from step 2 (each starting with `#@`)
- `callee_contracts` (str): Already-verified callee contracts for tighter invariants
- `class_context` (str): Optional class header + `__init__`
- `memory_model` (str): One of `hoare`, `typed`, `store`
- `skill_content` (str): Full PyCSL skill content (transpiler limits, solver heuristics)
- `model` (str): LLM model name
- `project_directory` (str): Base directory for logging

**Output**: Complete annotated function source code with:
- Function contracts inserted before `def`
- `#@ loop invariant` and `#@ loop variant` on every loop
- `for` → `while` rewrites where needed
- PEP 484 type hints on all parameters and return type

## Design

- Receives the full PyCSL skill so it can handle transpiler limits and solver-specific patterns
- Contracts are pre-decided (from step 2), so the LLM focuses on loop analysis only
- Conservation invariants (e.g., `a + b + c == i`) are guided by the postcondition
- Output is extracted from markdown code fences
