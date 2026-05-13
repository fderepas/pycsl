Act as an expert Python developer. Write a Python script named `agent-annotate.py` that annotates a Python program with PyCSL contracts and returns the annotated source code as plain Python text.

In `agent-annotate.py`, define a global variable named `AGENT_NAME` with the value `"agent-annotate"`.

## 1. Input

The script must accept these command-line options:

* `--in`: path to the Python program to annotate.
* `--out`: path to the output file that will contain the annotated program.

The script must read `agents-config.json` from the same directory as `agent-annotate.py`. The config must provide:

* `model`
* `project-directory`
* `skill-annotate`

The `skill-annotate` path is resolved relative to the script directory unless it is already absolute.

## 2. Skill prompt

The prompt must include the contents of `<skill-annotate>` followed by the input Python program.

The skill file ends with:

```python
...

# TASK

Analyze the following Python code and output the fully annotated PyCSL version. Output ONLY the valid Python code.
```

The model must be instructed to output only the annotated Python code in markdown code fences:

```
Just output the python code between "```python" and "```".
```

## 3. Output file

The script must create missing output directories automatically and write the generated annotated code to `<out>`.

## 4. Library to use

The script must import:

```python
from llm_client import llm_generate, log
```

It should use `log(...)` for errors and call `llm_generate(agent_id=model, prompt=prompt)` to generate the annotated code.

