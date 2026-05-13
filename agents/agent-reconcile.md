Act as an expert Python developer. Write a Python script named `agent-reconcile.py` that generates a reconciliation prompt for a failing PyCSL run and stores the LLM response as JSON.

In `agent-reconcile.py`, define a global variable named `AGENT_NAME` with the value `"agent-reconcile"`.

## 1. Input

The script must accept these command-line options:

* `--script`: path to the Python source file under analysis.
* `--out`: path to the output JSON file.
* `--stdout`: path to the captured standard output file.
* `--stderr`: path to the captured standard error file.
* `--ret-code`: the captured return code.

The script must read `agents-config.json` from the same directory as `agent-reconcile.py`. The config must provide:

* `model`
* `project-directory`
* `skill-annotate`
* `skill-agents`
* `skill-module5`
* `skill-module6`

The skill file paths are resolved relative to the script directory unless already absolute.

## 2. Prompt to generate

The generated prompt must include the contents of:

* `<skill-annotate>`
* `<skill-agents>`
* `<skill-module5>`
* `<skill-module6>`

It must also include:

* `<script>`
* `<stdout>`
* `<stderr>`
* `<ret-code>`

If a WhyML file exists next to `<script>`, it must also be included. Its path is obtained by replacing the `.py` suffix with `.mlw`.

The prompt should ask the LLM to return raw JSON only with a strict instruction:

```
Just output the JSON between "```json" and "```".
```

Required JSON fields:

* `language`
* `author`
* `recommendation`
* `target`

`target` should be one of:

* `update-pycsl-scripts`
* `error-in-annotations`
* `unknown`

## 3. Output file

The script must create missing output directories automatically and write the resulting JSON to `<out>`.

The response must be parsed as JSON, with optional handling for fenced or embedded JSON text, and validated to contain the required keys before writing.

## 4. Library to use

The script must import:

```python
from llm_client import llm_generate, log
```

It should use `log(...)` for error reporting and call `llm_generate(...)` to obtain the reconciliation JSON.

