**Act as an expert Python developer.
** Write a Python script named `agent-meta-monitor.py` that acts as an operational watchdog for a self-healing agentic pipeline.

In `agent-meta-monitor.py`, define a global variable named `AGENT_NAME` with the value `"agent-meta-monitor"`.

## 1. Input

The script must accept these command-line options using `argparse`:

* `--reconcile-log`: path to the log file or captured stdout/stderr of `agent-reconcile.py`.
* `--update-log`: path to the MCP execution log of `agent-script-update.py`.
* `--out`: path to the output JSON metrics file.

## 2. Core Responsibilities

The script must parse the provided text logs to extract and compute operational health metrics. It needs to perform regex or string-based analysis to track the following:

* **JSON Validation Rate:** Scan the `--reconcile-log` to determine if `agent-reconcile.py` failed to produce valid JSON or missed the required keys (`language`, `author`, `recommendation`, `target`). Count the number of malformed outputs.
* **MCP Constraint Tracking:** Scan the `--update-log` to count how many times `agent-script-update.py` attempted to write to forbidden paths (specifically looking for rejection errors or attempts to write to `tests/annotated/`).
* **Execution Telemetry:** If timestamps or token counts are present in the logs, parse them to calculate total execution time and token consumption.

## 3. Output file

The script must aggregate these metrics into a single dictionary and write the resulting JSON to `<out>`.

Required JSON output fields:

* `json_validation_failures` (integer)
* `mcp_rejection_count` (integer)
* `total_execution_time_seconds` (float, or `null` if not found)
* `health_status` (string: `"healthy"` if failures/rejections are 0, `"warning"` if > 0)

The script must create missing output directories automatically before writing the `<out>` file.

## 4. Libraries and Conventions

The script must use standard Python libraries (`argparse`, `json`, `pathlib`, `re`).
If available in the environment, it should import `log` from `llm_client` for its own internal error reporting (e.g., `from llm_client import log`).

It must gracefully handle missing log files or unparseable lines. If a log file does not exist, it should record `0` for the relevant metrics rather than crashing, and log a warning.
