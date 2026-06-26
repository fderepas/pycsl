# more-toolfix-spec.md — Path to typing-global-impl.md readiness

**Status:** Planning
**Goal:** Close all preconditions so `typing-global-impl.md` can run from a clean baseline
**Precondition (from typing-global-impl.md):** P-series settled, HAPPY landed with `--soundness-report`, PEP 695 `pure_ast` productions landed before TY3

---

## Current blockers

| Blocker | Status | Why it blocks typing |
|---|---|---|
| This branch has uncommitted changes | ❌ Working tree dirty (statements.py toolfix + skill edits) | Typing work needs a committed baseline; the vacuity-gate fix is part of that baseline |
| PEP 695 parser landed | ⚠️ Partially — `pure_ast.py` stubs node classes but rejects with `unsupported()` on parse (§3 below) | TY3 requires PEP 695; even TY0/TY1 need a stable front-end that won't change mid-engagement |
| os proof baseline green | ✅ 23 formal tests PASS, `__init__.py` SUCCESS | Standing gate for typing — already satisfied |
| IR platform settled at 1.2 | ✅ Stable, additive bump policy documented | Ready |
| `--soundness-report` machinery present | ✅ In `pycsl.py`, wired to CLI flag | Ready |
| `--check-vacuity` / false-twin available | ✅ Both present; vacuity-gate fix (68d56ec7) addresses prior false positives | Ready but needs merge |

---

## 1. Close this branch cleanly

The working tree on `fix-vacuity-gate-false-positive` has uncommitted changes that are dependencies of the typing engagement:

### 1A. Land the vacuity-gate toolfix
- **What:** The per-element VC assert in `_handle_array_slice_set_stmt` (statements.py +24 lines, see `toolfix-spec.md`) is correct and gate-satisfied but not committed
- **Why it matters:** It is a soundness improvement that typing's standing gate assumes. Commit it as part of this branch
- **Scope:** Working-tree diff in `src/pycsl/module6_whyml/statements.py` only

### 1B. Land pending skill edits
- **What:** Multiple `config/skills/*.md` files have working-tree modifications
- **Why it matters:** Typing agents will load skills; they must reflect current platform capabilities (non-vacuity gate, soundness report, prover dispatch)
- **Scope:** Editorial — ensure skills document the now-shipped features: `--check-vacuity`, `--soundness-report`, `false-twin.py`

### 1C. Merge branch to main
- **What:** `fix-vacuity-gate-false-positive` → main (1 commit + toolfix)
- **Why it matters:** Typing engagement expects a single baseline; the spec says "P-series settled" which means merged, not in-flight

---

## 2. Land PEP 695 parser productions

**Current state:** `pure_ast.py` defines the node types (`TypeVar`, `ParamSpec`, `TypeVarTuple`, `type_params` field on `FunctionDef`/`ClassDef`) but rejects them at parse time with `self.unsupported("PEP 695 ...")`. Three locations (lines 726, 1373, 1392) need to produce the nodes instead of rejecting.

**Why it blocks typing:** TY3 *requires* these productions. But the typing spec says TY0 runs first — and if we don't land PEP 695 before starting TY0, there is a risk that TY3 back-propagates parser changes into the middle of TY1/TY2 work. Typing-global-impl.md §5 explicitly states: "the PEP 695 `pure_ast` parser productions [must] land before TY3." Landing them **before starting the engagement** avoids mid-stream front-end churn.

**Scope:** Parse support for three syntax forms in `pure_ast.py`:
1. `type X = ...` type alias statement (one location, line 726)
2. `def f[T]` / `async def f[T]` function type params (two locations, lines 1373, 1392)
3. `class C[T]` class type params (same locations — shared code path)

These are parser-only. The IR lowering for TY3 is separate work.

---

## 3. Verify standing gate is green on main after merge

After step 1, confirm the full gate from typing-global-impl.md §3.2:
- Corpus tests: all green (both suites)
- os formal tests: 23/23 PASS, `__init__.py` SUCCESS
- Byte-diff: no regression on unaffected drivers
- Doc-coherency: `bin/doc-coherency.py --check` passes
- Non-vacuity: `--check-vacuity` does not over-report (the fix in 68d56ec7 already verified this)

This is a checkpoint, not implementation. A one-command verification pass.

---

## What is NOT in scope (typing itself)

The following are **typing-global-impl.md's** job, not this plan's:
- TY0–TY3 construct specifications, two-plane specs, S5 subsets
- Agent definitions (spec-agent, core-agent, conformance-agent, probe-agent)
- The per-construct pipeline with Gates A/C/D
- Monomorphization machinery for TY3 generics
- TypedDict / Protocol / overload lowering

This plan only closes the preconditions. Once it is done, `typing-global-impl.md` runs on a clean, merged baseline with all infrastructure in place.

---

## Estimated effort

| Step | Effort | Risk |
|---|---|---|
| 1A–1C: Commit and merge this branch | Low — toolfix already implemented and gates verified | Very low; the vacuity-gate work is proven complete |
| 2: Land PEP 695 parser | Medium — 4 locations in `pure_ast.py`, test-driven | Low; AST node table is already defined, only parsing is stubbed |
| 3: Standup verification | Trivial — one command pass, 5 minutes | None if merge and parser work are correct |

**Total:** This is toolfix + verification, not feature development. Estimated 2–4 hours of agent time.
