**Act as an expert Python developer.** Write a Python script named `agent-meta-reviewer.py` that acts as the human interface and trend analyzer for a self-healing agentic pipeline.

In `agent-meta-reviewer.py`, define a global variable named `AGENT_NAME` with the value `"agent-meta-reviewer"`.

## 1. Input

The script must accept these command-line options using `argparse`:

* `--monitor-json`: path to the JSON metrics file produced by `agent-meta-monitor.py`.
* `--eval-json`: path to the JSON evaluation file produced by `agent-meta-evaluator.py`.
* `--reconcile-json`: path to the original recommendation JSON produced by `agent-reconcile.py`.
* `--out-json`: path to the output JSON file for the structured review data.
* `--out-md`: path to the output Markdown file for the human-readable Pull Request description.

## 2. Prompt to generate

The script must read the contents of the three input JSON files. It must construct a prompt for an LLM that includes:

* The operational health metrics (from `<monitor-json>`).
* The efficacy evaluation (from `<eval-json>`).
* The original fix recommendation and target (from `<reconcile-json>`).

The prompt should ask the LLM to act as a Staff Software Engineer reviewing an automated fix. It must synthesize the data and generate two things:

1. A clear, concise Pull Request title and body explaining the problem, the agent's fix, the blast radius, and the test results.
2. A macro-level recommendation on whether the base prompts or system config need adjustments based on the health metrics and test outcomes.

The prompt must instruct the LLM to return raw JSON only, wrapped in a strict code block:

```
Just output the JSON between "```json" and "```".

```

Required JSON fields:

* `pr_title` (string)
* `pr_body` (string, formatted as Markdown)
* `system_recommendation` (string)
* `requires_human_intervention` (boolean: `true` if the evaluation status was "Regression" or if the monitor reported a "warning" health status, `false` otherwise)

## 3. Output files

The script must call the LLM, parse the returned JSON (handling optional fenced blocks), and validate the required keys.

* It must write the entire parsed JSON payload to `<out-json>`.
* It must extract the `pr_body` field and write it directly to `<out-md>` so it can be easily consumed by CI/CD pipelines (like GitHub Actions).

The script must create missing output directories automatically before writing the files.

## 4. Libraries and Conventions

The script must import:

```python
from llm_client import llm_generate, log

```

It must use standard Python libraries (`argparse`, `json`, `pathlib`).
It should use `log(...)` for error reporting and call `llm_generate(...)` to obtain the reviewer JSON. If any input files are missing, it should log a warning and gracefully exit or pass placeholder data to the LLM.