# agent-contract-writer

## Purpose

Step 2 of the 3-agent annotation pipeline. Receives a Python function + plain-English description (from `agent-english-writer`) and writes function-level PyCSL contracts: `#@ requires`, `#@ ensures`, `#@ assigns`.

Does NOT write loop invariants or loop variants — that is step 3.

## Interface

**Callable as**: Python module (`generate()` function), imported by `agent-writer.py`.

**Input**:
- `function_source` (str): Raw Python function source code
- `english_description` (str): Structured English from step 1
- `class_context` (str): Optional class header + `__init__`
- `memory_model` (str): One of `hoare`, `typed`, `store`
- `model` (str): LLM model name
- `project_directory` (str): Base directory for logging

**Output**: Contract lines only (each starting with `#@`), newline-separated.

## Design

- Prompt includes a focused PyCSL syntax reference (allowed/forbidden operators, memory model notes)
- The English description anchors the LLM on function semantics, preventing lazy `True` contracts
- Output is post-processed to extract only `#@` lines and ensure all three required contracts are present
- Falls back to `#@ requires True` / `#@ ensures True` / `#@ assigns \nothing` only for missing contracts
