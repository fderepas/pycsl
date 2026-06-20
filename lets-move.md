# lets-move.md — Promote `pure_lib` to the PyCSL standard library

**Status: PLAN for review. Nothing executed yet.**

## 0. Goal

Make the formally-verified `pure_lib/` the *canonical* PyCSL standard library by
relocating it to `src/pycsl_lib/`, retiring the old un-/under-verified stub set,
and moving the formal tests alongside it.

| # | From | To | What it is |
|---|------|----|-----------|
| 1 | `src/pycsl_lib/` (310 files) | `attic/pycsl_lib/` | OLD stdlib stub set (real names: `array.py`, `ast.py`, `argparse.py`, demos, `MANIFEST.toml`). Retired. |
| 2 | `pure_lib/` (108 files, 94 modules) | `src/pycsl_lib/` | The verified models (de-clashed names: `csys`, `strmod`, `mth`, `arr`, …). New standard library. |
| 3 | `pure_lib_test/` (121 files) | `src/pycsl_lib_test/` | Formal consequence tests. |

`attic/pycsl_lib` does **not** currently exist → move #1 is collision-free.

---

## 1. How resolution works today (so we change the right things)

The tool resolves imports in **two independent mechanisms** — both must keep working:

### (A) Package-qualified imports — `from pure_lib.os import mkdir`
Resolved by `src/pycsl/frontend/ir_resolve.py :: _resolve_module_path` (line 69).
For an absolute import it tries, in order, the bases:
```
[ dir(main_file), os.getcwd(), <src/pycsl>/Lib ]   # Lib/ does not exist → no-op
```
mapping `pure_lib.os` → `<base>/pure_lib/os/__init__.py`. In practice it resolves
because **cwd = repo root** when you run `pycsl pure_lib_test/formal_*.py`.
→ Used by **all 107 `from pure_lib.…` lines** in `pure_lib_test/`, plus 2 intra-lib
importers (`pure_lib/frac`, `pure_lib/world`).

### (B) Bare imports — `import os` (the "trusted stub" set)
Resolved via `stub_dir`, set at `src/pycsl/pycsl.py:420`:
```python
stub_dir=_project_root / "src" / "pycsl_lib",
```
`import_classifier._stub_set(stub_dir)` builds the set of "known stdlib module
names" from the *directory contents*. **This constant already points at
`src/pycsl_lib/`** — the future location — so after move #2 it needs **no edit**;
its contents simply become the verified models.

**Consequence to decide (D1 below):** mechanism (B)'s known-name set changes from
`{array, ast, argparse, os, re, …}` (old real names) to `{arr, astmod, argp, os,
re, csys, …}` (de-clashed). Bare `import array` will no longer classify as a known
stub.

---

## 2. Reference inventory (what references break)

Counts are tracked files containing the literal term.

### Load-bearing — MUST change for correctness
| Class | Files / locus | Action |
|---|---|---|
| **Package resolver** | `src/pycsl/frontend/ir_resolve.py` `_resolve_module_path` | Add `src/` to the base list so `pycsl_lib.X` → `src/pycsl_lib/X` resolves regardless of cwd. (1-line list addition.) |
| **Test imports** | `pure_lib_test/*.py` — 107 `from pure_lib.…` lines | Rewrite `from pure_lib.` → `from pycsl_lib.`. |
| **Intra-lib imports** | `pure_lib/frac/__init__.py`, `pure_lib/world/__init__.py` | Rewrite `pure_lib.` → `pycsl_lib.` (move with the tree). |
| **stub_dir constant** | `src/pycsl/pycsl.py:420` | **No change** (already `src/pycsl_lib`); verify post-move. |

### Tooling pointed at the OLD stub set — needs a decision (D2)
| File | Current target |
|---|---|
| `src/pycsl/agents/agent-stdlib-annotate.py` | `_STUB_DIR = src/pycsl_lib`, `_TEST_DIR = test-suite/corpus/python-reference/stdlib` |
| `bin/stdlib-coverage.py`, `bin/stdlib-coverage-report.py` | walk `src/pycsl_lib` annotation depth |
| `bin/generate_lib_stubs.py`, `bin/check-no-trusted-stubs.py` | the old stub set |
| `bin/run-reference-tests.sh`, `bin/phase-c-bulk-runner.sh` | reference paths |

These measured the OLD stubs' annotation coverage. `pure_lib` is already fully
annotated/verified, so the coverage campaign they serve is largely complete.

### Cosmetic — docs/comments (correctness-neutral, hygiene)
| Class | Count | Action |
|---|---|---|
| `config/skills/**` | 19 files | Update path strings `pure_lib` / `pure_lib_test` / old-`pycsl_lib` → new layout. |
| `docs/`, `README.md`, `Makefile`, `TODO` | ~10 | Update path references. |
| `src/pycsl/module6_whyml/preamble.py:1205–1242` | comments | `pure_lib/strmod` → `src/pycsl_lib/strmod`. |

### Out of scope — frozen historical record (DO NOT rewrite)
- `getting-better/` (33 refs) — campaign writeups; rewriting falsifies history.
- Root `*.md` specs/handoffs, `projects/` (280 stale-generated refs), `logs/` (40).
- These are candidates for the *separate* directory-tidy, not this move.

---

## 3. Decisions for your review (block execution until resolved)

- **D1 — Canonical names.** Confirm the de-clashed `pure_lib` names (`arr`,
  `csys`, `strmod`, …) become the canonical PyCSL stdlib names, and that any
  consumer importing the old *real* names (`array`, `colorsys`, …) is either
  retired with the old stub set or out of scope. (My read of intent: yes.)
- **D2 — Coverage tooling fate.** For `agent-stdlib-annotate` + the `bin/stdlib-*`
  tools, choose: **(a) repoint** to the new `src/pycsl_lib`, **(b) repoint to the
  attic** (freeze against the retired set), or **(c) retire** them (pure_lib is
  already fully annotated). Recommend (c) or (a).
- **D3 — Import spelling.** Rewrite tests to `from pycsl_lib.X import …` (needs the
  resolver base edit, §2). Alternative: keep `pure_lib` as a thin alias package —
  not recommended (defeats the rename).
- **D4 — Doc-rewrite scope.** All 19 config + docs now, or only the load-bearing
  set now and docs in a follow-up? (Recommend: load-bearing + README/Makefile now;
  bulk skills docs in a follow-up commit.)

---

## 4. Execution sequence (once D1–D4 are settled)

Pre-flight: working tree clean & committed (the git-clean hazard — untracked
plans like this file must be committed first); create branch `promote-pure-lib`.

1. `git mv src/pycsl_lib attic/pycsl_lib`           # retire old stubs (history preserved)
2. `git mv pure_lib src/pycsl_lib`                  # promote verified lib (carries its __init__.py)
3. `git mv pure_lib_test src/pycsl_lib_test`        # move formal tests
4. Edit `ir_resolve.py`: add repo-`src/` to `_resolve_module_path` bases.
5. Rewrite imports (verify diff before commit):
   `git grep -l 'pure_lib' -- src/pycsl_lib_test src/pycsl_lib | xargs sed -i 's/\bpure_lib\./pycsl_lib./g'`
   (then hand-audit: comments `# … pure_lib/X` are fine to leave or fix.)
6. Apply D2 (repoint/retire coverage tooling).
7. Update README/Makefile/preamble comments (+ config/docs per D4).
8. Run the verification gates (§5).
9. Commit → PR → review → merge.

---

## 5. Verification gates (must all pass before merge)

1. **os zero-trust preserved:** `grep -rc '#@ \trusted' src/pycsl_lib/os/` → 0.
2. **Package resolution works:** `pycsl src/pycsl_lib_test/formal_os_enoent.py`
   and `…/formal_os_fdchain.py` → `Verification SUCCESS` (these exercise the moved
   `from pycsl_lib.os import …`).
3. **Bare-import / stub set works:** `pycsl src/pycsl_lib/os/__init__.py` → SUCCESS;
   `import_classifier` stub set rebuilt from the new dir (sanity: a module that does
   `import os` still classifies `os` as a stub).
4. **Semantic no-op (byte-diff):** emitted `.mlw` for a sample module (e.g.
   `os/__init__.py`, `strmod/__init__.py`) byte-identical before vs after the move
   (modulo the path string in headers). Proves the move changed location, not logic.
5. **History preserved:** `git log --follow src/pycsl_lib/os/__init__.py` shows the
   pre-move history.
6. **No dangling refs in live code:** `git grep -n 'pure_lib' -- src/ bin/ Makefile
   README.md` returns only intentional/cosmetic leftovers (none load-bearing).

---

## 6. Rollback

All moves are `git mv` on a branch. Abort = `git checkout main && git branch -D
promote-pure-lib`. No history is lost (moves are tracked; the old stub set lives on
in `attic/pycsl_lib`).

---

## 7. Effort estimate

- Moves + resolver edit + import rewrite + gates: ~the load-bearing core, low risk,
  mechanical, fully verifiable.
- The long tail is **doc/comment** references (config skills, docs) — high count,
  zero correctness risk, batchable in a follow-up.
- Biggest real risk is **D1/D2** (semantics of the stub-name set + coverage tooling),
  not the file moves — which is why they're surfaced as decisions, not buried.
