# `bin/` utilities + Configuration

Load when invoking a `bin/` script, configuring agent runs, or
setting up the local development environment.

## Utilities in `bin/`

| Script | Purpose |
|--------|---------|
| `run.sh` | **Main entry point.** Runs the full coordinator pipeline: annotate → prove → reconcile → update. Accepts `--start-at N` to skip files before number N. |
| `annotate.sh` | Annotate a single file without proof or reconciliation. |
| `run-annotated.sh` | Run `pycsl` on all files in `tests/annotated/` (manual validation). |
| `check-annotation-quality.py` | Analyze annotation quality: reports trivial contracts, missing assigns, etc. |
| `get-meta-info.sh` | Query meta-agent outputs (evaluator, monitor, reviewer) for a given file stem. |
| `update-rag.sh` | Rebuild the RAG index from all skills in `config/skills/`. **Must be run after any skill update.** |
| `run-reference-tests.sh` | Run all tests in `test-suite/corpus/pycsl-reference/`. Supports `# pycsl-flags:` and `# pycsl-expected: FAIL` directives in test files (per-test flags like `--no-proof`, `--memory-model typed`). **Runs tests in parallel** via `xargs -P`, default `--jobs = get_cpu_count()/2` (half the cores; portable Linux `nproc`/`getconf` + macOS `sysctl` count). `--jobs K` / `PYCSL_JOBS` override; `--jobs 1` = serial (old behaviour). Suite/range flags: `--pycsl`/`--python`, `--start-at N`/`--stop-at N`. Pre-gates (stdlib-coverage, doc-coherency) run once up front. ~5 min full corpus (was ~30+ min serial). |

## Configuration

### `config/agents-config.json`
Contains model name, project directory path, and allowed tools for agent execution.

### `config/schemas/`
JSON schemas validating agent input/output formats (reconciliation recommendations, meta-agent reports).

### Environment
- Python virtual environment expected at `.venv/`
- `pycsl` binary must be on PATH
- Ollama must be running locally for RAG embedding generation
