# agent-english-writer

## Purpose

Step 1 of the 3-agent annotation pipeline. Reads a Python function and produces a structured plain-English description of its semantics. Has no knowledge of PyCSL or formal contracts.

## Interface

**Callable as**: Python module (`generate()` function), imported by `agent-writer.py`.

**Input**:
- `function_source` (str): Raw Python function source code
- `class_context` (str): Optional class header + `__init__` for methods
- `model` (str): LLM model name
- `project_directory` (str): Base directory for logging

**Output**: Structured English text with sections:
- `DESCRIPTION`: What the function computes
- `RETURN VALUE`: Type and mathematical properties
- `PRECONDITIONS`: What callers must guarantee
- `MUTATIONS`: What state is modified
- `LOOP PROPERTIES`: Per-loop analysis (changes, invariants, termination)

## Design

- Uses a small, focused prompt with no skill file dependency
- Output is consumed by `agent-contract-writer.py` to produce formal contracts
- Separation ensures the LLM reasons about semantics before syntax
