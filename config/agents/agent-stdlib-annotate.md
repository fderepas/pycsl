Act as an expert Python verification engineer building deductive
contracts for Python stdlib stubs in PyCSL. Write a Python script
named `agent-stdlib-annotate.py` that autonomously promotes
stubs from L2 (trusted, no semantic content) to L4 / L5 (full
contract + reference tests) **without interactive supervision**.

In `agent-stdlib-annotate.py`, define a global variable named
`AGENT_NAME` with the value `"agent-stdlib-annotate"`.

## 1. Input

The script must accept these command-line options:

* `--module <name>` — annotate a single stdlib module (e.g.
  `math`, `json`, `os.path`). Mutually exclusive with `--all`.
* `--all` — iterate every stdlib module under
  `src/pycsl_lib/` not in the exclusion set (see §6).
* `--dry-run` — generate the contracts in memory and print the
  diff to stdout; do NOT write to disk.
* `--max-fns <N>` — cap per-module function count (smoke-test
  knob; default unlimited).
* `--log-dir <path>` — base path for per-module logs (default
  `logs/stdlib-annotator/<UTC-timestamp>/`).
* `--config <path>` — override `agents-config.json` location
  (default `config/agents-config.json`).

The script must read `agents-config.json` from the
`--config`-specified path (or the default). The config must
provide:

* `model` — LLM model tag (passed to `llm_generate`).
* `project-directory` — repo root.
* `skill-stdlib-annotate` — path to the global-plan synthesis
  (defaults to `docs/stdlib-global-plan.md`, which embeds the
  per-function conventions from `docs/stdlib-annotation-conventions.md`
  AND the multi-quarter strategy framing).
* `writer-timeout` — optional, defaults to existing
  config value.

## 2. Per-module workflow

For each stdlib module in scope:

1. **Snapshot baseline**: invoke
   `bin/stdlib-coverage-report.py --module <name> --json` and
   record the per-level counts. This is the
   monotonic-ratchet anchor.
2. **Identify promotion targets**: parse
   `src/pycsl_lib/<name>.py` with `libcst`. Collect every
   top-level function and class method NOT already classified
   as L4 or L5 by the coverage scanner's rules.
3. **Extract docstrings**: for each target, find the same
   function in `cpython/Lib/<name>.py` (or its package nested
   form, e.g. `cpython/Lib/os/path.py`). Pull the function's
   docstring and signature. **No web access** — the cpython
   submodule is the offline truth source.
4. **Generate contract block** per function via `llm_generate`:
   feed the conventions skill + extracted docstring + signature;
   expect the LLM to output the canonical block:
   ```
   #@ \trusted reviewer: python-stdlib
   # cite: <cpython/Lib/<name>.py:<line>>
   #@ requires <bool>
   #@ ensures <bool>
   #@ ensures <bool>   // multiple ensures allowed
   ```
5. **Splice into stub**: use `libcst` to replace the existing
   leading comments + decorator block above the FunctionDef
   with the LLM-generated block. Preserve everything else
   (docstring, body, surrounding functions) verbatim.
6. **Generate reference tests**: for each promoted function,
   write TWO files under
   `test-suite/corpus/python-reference/stdlib/<name>/`:
   * `<fnname>_<scenario>_proves.py` — positive test where a
     caller establishes the precondition and exploits the
     postcondition.
   * `<fnname>_<scenario>_fails.py` — negative test where the
     caller cannot discharge the precondition (or
     over-claims a stronger postcondition). Header carries
     `# pycsl-flags: --no-proof` for the corpus runner.
7. **Validate gate**: run sequentially:
   - `.venv/bin/python -m pycsl.pycsl --no-proof src/pycsl_lib/<name>.py` (exit 0).
   - `bin/stdlib-coverage-report.py --module <name>` (parse output; L4+ count must NOT decrease).
   - `bash bin/run-self-annotation-suite.sh` (must still report `26/26 proved`).

   If any gate fails:
   - `git checkout -- src/pycsl_lib/<name>.py` (rollback stub).
   - `rm -rf test-suite/corpus/python-reference/stdlib/<name>/` for any test files newly added by this run (track them in the per-module log).
   - Record the failure in the log.
   - Move on to the next module (continue past failures).

## 3. No commits

The script **never** invokes `git commit`, `git add`, or
`git push`. All changes accumulate in the working tree; the
human reviewer commits selectively. This matches the
"stage all, no commits" policy from the strategy plan.

## 4. Skill prompt

The system prompt to `llm_generate` must include the full
contents of `<skill-stdlib-annotate>` (i.e.
`docs/stdlib-global-plan.md`) verbatim. The user
prompt per function must include:

* Function signature (from the stub).
* CPython docstring (from `cpython/Lib/<name>.py`).
* The function's current annotation block (L1/L2/L3 — what's
  there already, so the LLM can refine rather than rebuild).
* Instructions: "Output the canonical contract block as
  defined in the conventions doc; nothing else. The block
  must end before the `def <name>(...)` line."

The model must output ONLY the directive block in markdown
code fences:

```
Just output the block between "```contracts" and "```".
```

## 5. Library to use

The script must import:

```python
from llm_client import llm_generate, log
```

It should use `log(...)` for errors and call
`llm_generate(agent_id=AGENT_NAME, prompt=prompt,
system=system_prompt, model=model)` per function.

## 6. Module exclusion set

The agent must skip modules that the coverage scanner
classifies as non-stdlib (Module1_Ingestor.py, Module2_Parser.py,
… , __future__.py, jsonschema, lark, libcst, mcp, numpy).
Read this set from `bin/stdlib-coverage-report.py`'s
`_NON_STDLIB` constant (import it). Also skip modules with
zero L1+L2+L3 functions remaining (all already at L4+).

## 7. Logging

Per-module log under `<log-dir>/<module>.log`:

```
[<UTC-timestamp>] Module: math
  Baseline: L1=0 L2=58 L3=0 L4=0 L5=4   (6.5% L4+)
  Targets:  58 functions to promote
  ── Promoting: ceil ──
    docstring: "Return the ceiling of x..."
    LLM call: ok (412 ms)
    Splice: src/pycsl_lib/math.py:21-22 → :21-26
    Tests:  test-suite/corpus/python-reference/stdlib/math/ceil_above_x_proves.py
            test-suite/corpus/python-reference/stdlib/math/ceil_overclaim_fails.py
  ... [per function]
  ── Gate: pycsl --no-proof math.py ──  PASS
  ── Gate: stdlib-coverage --module math ──
    Final:   L1=0 L2=10 L3=4 L4=44 L5=4   (77.4% L4+, +70.9%)
  ── Gate: self-annotate-verify ──  26/26 PROVED
  Outcome: COMMIT-READY
```

## 8. Exit codes

* 0 — all in-scope modules processed (some may have rolled
  back; check logs).
* 2 — argument error.
* 3 — LLM backend unreachable.

The agent does NOT fail on a per-module gate failure — that's
the rollback path. Only structural errors (config missing,
unrecognized flag, cpython submodule absent) produce non-zero
exit.

## 9. Memory model context

Pulled from `agents-config.json` like other agents; the
stdlib stubs are memory-model-agnostic (most are pure
functions; side-effect-heavy modules cap at L3 per the
conventions doc). The model field is informational only —
contract content does not vary by memory model.

## 10. Cross-references

* Global plan (skill content the agent reads):
  `docs/stdlib-global-plan.md` (strategy + conventions
  synthesis). Standalone conventions:
  `docs/stdlib-annotation-conventions.md`.
* Strategy plan (multi-quarter context):
  `.claude/plans/parsed-booping-ember.md`.
* Coverage classifier (mechanical gate):
  `bin/stdlib-coverage-report.py`.
* Existing agent pattern (analogous architecture):
  `src/pycsl/agents/agent-annotate.py`.
