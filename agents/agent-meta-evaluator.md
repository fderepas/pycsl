**Act as an expert Python developer.** Write a Python script named `agent-meta-evaluator.py` that acts as the automated QA judge for a self-healing agentic pipeline.

In `agent-meta-evaluator.py`, define a global variable named `AGENT_NAME` with the value `"agent-meta-evaluator"`.

## 1. Input

The script must accept these command-line options using `argparse`:

* `--annotated-file`: path to the annotated `.py` file to re-verify with pycsl. The evaluator reconstructs the pycsl command internally (`python pycsl --keep-mlw <annotated-file>`).
* `--modified-file`: path to the file that was modified by the update agent (e.g., `agents/agent-annotate.py` or `agents/skill-annotate.md`).
* `--out`: path to the output JSON evaluation file.

## 2. Core Responsibilities

The script must evaluate the efficacy and safety of the applied fix by performing the following steps:

* **Syntax Verification:** If the `--modified-file` is a Python script (`.py` extension), run a syntax check using `python -m py_compile` (or invoke `ruff`/`flake8` if available) via the `subprocess` module. Capture whether the syntax is valid.
* **Pipeline Verification:** Re-run pycsl on `--annotated-file` by constructing the command internally as `python pycsl --keep-mlw <annotated-file>`. Capture the new return code, standard output, and standard error.
* **Status Evaluation:** Determine the outcome category:
* `Success`: The syntax is valid AND the pipeline return code is `0`.
* `Partial Fix`: The syntax is valid, but the pipeline return code is still non-zero.
* `Regression`: The syntax check failed (the update agent introduced broken Python code or invalid Markdown).



## 3. Output file

The script must aggregate the evaluation results into a single dictionary and write the resulting JSON to `<out>`.

Required JSON output fields:

* `resolution_status` (string: `"Success"`, `"Partial Fix"`, or `"Regression"`)
* `new_ret_code` (integer)
* `syntax_valid` (boolean)
* `stdout` (string, the captured test output)
* `stderr` (string, the captured test error)

The script must create missing output directories automatically before writing the `<out>` file.

## 4. Libraries and Conventions

The script must use standard Python libraries (`argparse`, `json`, `pathlib`, `subprocess`).
If available in the environment, it should import `log` from `llm_client` for its own internal error reporting (e.g., `from llm_client import log`).

It must gracefully handle subprocess execution failures (like timeouts or missing commands) by catching `subprocess.SubprocessError` and reflecting the failure in the `stderr` and `new_ret_code` fields of the output JSON.