# PyCSL Coordinator Agent

## Overview

The coordinator agent orchestrates a complete PyCSL testing workflow:

1. **Clean** — Remove all files from `tests/annotated/`
2. **Annotate** — Run `agent-annotate.py` on each file in `tests/to_annotate/` to produce annotated versions
3. **Prove** — Run `pycsl` on each annotated file to check proof validity
4. **Reconcile** — If proof fails, run `agent-reconcile.py` to generate recommendations
5. **Update** — Apply recommendations via `agent-script-update-mcp.py`

## Usage

### Quick Start

```bash
cd /path/to/rtos_spike/ai/PyCSL
./run.sh
```

### Manual Run

```bash
cd /path/to/rtos_spike/ai/PyCSL
python agents/coordinator.py
```

## Components

- **`coordinator.py`**: Main orchestration agent
  - Manages the workflow steps
  - Captures output from each step
  - Handles failures gracefully
  - Reports summary statistics

- **`run.sh`**: Launcher script
  - Activates the Python virtual environment
  - Sets up paths correctly
  - Runs the coordinator with proper context

## Workflow Details

### Step 1: Clean Annotated Directory
Removes all `.py` files from `tests/annotated/` to ensure a fresh start.

### Step 2: Annotation
For each `.py` file in `tests/to_annotate/`:
- Calls `agent-annotate.py`
- Outputs annotated version to `tests/annotated/`
- Stops on first error

### Step 3: PyCSL Proof
For each annotated file:
- Runs `pycsl` to verify the formal proof
- Collects success/failure for each file
- Continues through all files even if some fail

### Step 4: Reconciliation (on Failure)
For each failed file:
- Runs `agent-reconcile.py`
- Generates a JSON recommendation with `target` and `recommendation` fields
- Target can be: `update-pycsl-scripts`, `error-in-annotations`, or `unknown`

### Step 5: Update (on Recommendation)
- Applies recommendations via the MCP server
- Modifies relevant `Module*.py` or agent files
- Re-runs pycsl on updated files (future enhancement)

## Output

The coordinator logs all actions with timestamps and status. Exit code:
- `0`: All files passed proof
- `1`: One or more files failed proof (and reconciliation was attempted)

## Configuration

The coordinator expects:
- Virtual environment at `.venv/bin/activate`
- PyCSL binary at `pycsl`
- Test files in `tests/to_annotate/*.py`
- Agents at `agents/agent-annotate.py`, `agents/agent-reconcile.py`
- MCP server at `agents/agent-script-update-mcp.py`

## Future Enhancements

- Integrate MCP server calls for applying recommendations
- Add retry logic after applying recommendations
- Parallel annotation and proof checking
- Generate detailed reports in JSON format
- Support for custom test sets
