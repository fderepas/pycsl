# Session report — 2026-06-16

A working session on the PyCSL `os` formal-verification effort that turned into
three things: (1) catching and fixing a soundness regression that had gone silently
red on `main`, (2) taking an authoritative measurement of where `os` actually
stands, and (3) building a two-level **Squeeze Loop (SL)** framework and running it
to extend the os formal tests. Every "done" below was re-confirmed from a disjoint
base — no self-reported result was trusted on its face.

---

## 1. The sys_write "content-postcondition drift" — diagnosed and fixed (PR #17)

**The complaint:** `sys_write` showed 2 "Unknown content postconditions" that the
M6 work had reported as `0 unproven`.

**What it actually was.** Not environmental, not a prover regression: `sys_write`'s
emitted `.mlw` was **byte-identical** to the M6 commit and the prover versions were
unchanged (why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3). The "2 Unknown" double-counted
*one* failing goal across both provers. The real cause was a **latent over-claim**:
the gap-17 `fd_block`-range ensures

```
(\result == \length(data) and \old(fd_offset[fd]) == 0 and \length(data) <= 512)
    ==> 6 <= fd_block[fd] < 256
```

is **false for the empty write** — `\length(data) == 0` hits `if n == 0: return 0`
and returns *before* `fd_block` is set, yet `\result == 0 == \length(data)` makes the
antecedent true. The sibling content ensures (`block_content_eq`) survived only
because it is vacuously true over an empty buffer. The M6 "0 unproven" had been
reported from a **stale/intermediate measurement** that never exercised `len == 0`,
which had left the os `__init__` gate **silently RED (1128/2) on `main`** since the
M6 merge.

**Fix:** a `\result >= 1` guard on the antecedent, in both
`UnixInodeFileSystem.py` (the method) and `__init__.py` (the wrapper — which must
mirror or the trusted `val` over-claims). Verified: `sys_write` 399/1 → **400/0**;
`__init__` gate 1128/2 → **1129/0 green**; `formal_os_content` still 48/0.
**Merged as PR #17.**

> Lesson recorded: re-run the gate on the *committed* artifact; never re-report an
> intermediate count. This is the "self-declared-done" collapse.

---

## 2. Authoritative body-gate measurement

The dated figure (2026-06-13: 1573/1670, 94%) was replaced with a fresh full run:
**1986 Valid / 8 residual (99.6%)** — total goals had grown to 1994 and the old
dominant byte-range-invariant residual class was essentially gone. Each residual was
re-checked in `--fun` isolation to separate genuine gaps from aggregate noise:

| Residual | Verdict |
|---|---|
| `sys_rename` ×2 | genuine — SMT-infeasible no-trust closure (e-matching divergence) |
| `sys_write` ×3 | aggregate E-matching noise (proves 400/0 in `--fun` isolation) |
| `_now` ×1 | byte-range class-invariant noise (trivial goal OOMs under the full axiom set) |
| `_unpack_direntry` ×2 | genuine, small, fixable codec-leaf precondition |

---

## 3. `_unpack_direntry` dig-in — root-caused, fix found, reverted to protect a gate

`_unpack_direntry` calls `_unpack_uint16_be(data, 0)`, whose contract requires
`0 <= data[0..1] <= 255`, but `_unpack_direntry`'s only precondition is
`\valid(data, 32)` (length) — so it can't discharge the callee's byte-range. The fix
(a `for i in range(0,32): requires 0 <= data[i] <= 255`, mirroring `_unpack_inode`,
plus removing the dead `_read_directory` whose only verified caller it was) **worked
at the body-gate level** (leaf 35/0; body gate 8→4). But the byte-range clauses land
in the os `__init__` gate's axiom-rich context and **stalled it (>25 min, didn't
finish vs ~15 min)**; `#@ no_inline` did not turn the leaf into a contract-only `val`
there. To keep the load-bearing gate green *and practical*, the change was
**reverted** and documented as a fresh-machine follow-up (try a minimal 2-clause
precondition). Filed as a candidate bug (`bugs-to-report/`, STATUS: UNCONFIRMED).

---

## 4. The Squeeze Loop (SL) framework — built

Read the four `sl-*` skills (the SL strategy, builder, auditor, monitor-of-monitor)
and recognized that **PyCSL verification is itself a squeeze**: `U` = the `#@`
contracts (soft), `L` = Why3 + Alt-Ergo/Z3 (hard, executable). The session's own
work was an episode of *collapse-and-repair* (the stale-measurement self-declared-done,
the empty-write coherent-and-wrong). Then built two loops with `sl-builder`:

- **`formal-test-sl.md`** — the **base loop**: author and *fully prove* one PyCSL
  formal test per `(module, public API, English property)`. `U` = the API contracts
  + the English property + the consequence / calls-the-API rules; `L` = PyCSL
  discharge (SUCCESS, 0 non-Valid, 0 `\trusted`) + a non-vacuity seed. Its load-bearing
  barrier (the driver author sees API+spec only, never internals → cannot simulate)
  came straight from existing methodology memory.
- **`test-supervise-sl.md`** — the **monitor loop** (`sl-monitoring-sl`): decompose a
  mission, launch one `formal-test-sl` per target **as a sub-agent** (only soft
  outputs return → the barrier is physical, the supervisor's context stays bounded),
  squeeze each run. Ground truth `L` = the base-loop verdict; `U` = the mission
  guidance. It is the **bearer of the EXTREME-RIGOR doctrine**: reduce the TCB (zero
  `\trusted`; any axiom cross-validated Rocq+Lean; TCB only shrinks), and when
  Why3/SMT fails, route the goal to a proof assistant — never weaken or trust away.
- **`config/skills/pycsl-monitoring/SKILL.md`** — the Gate-S-audited knowledge store
  the monitor accumulates (proven patterns, the coherent-and-wrong catalog, per-module
  coverage ledgers), plus output dirs `getting-better/` and `bugs-to-report/`
  (`YYYYMMDD-hhmm-name.md`). Committed on branch **`docs/sl-loops`** (`3998840`).

---

## 5. Ran `test-supervise-sl` on the os module — and independently verified it

**Mission:** "annotate all `pure_lib/os` syscalls and write corresponding formal test
drivers in `pure_lib_test`." Launched as a background sub-agent.

**What it produced:** scoped 40 public `os.*` symbols, ran three `formal-test-sl`
instances as disjoint sub-agents (one self-corrected its own diagnosis — caught
*because* its base was disjoint), and left:

- **New, zero-trust, non-vacuous tests:** `formal_os_close.py`
  (open→close→fstat==EBADF), `formal_os_lseek.py` (lseek==pos).
- **Repaired 5 stale tests** (`query`, `meta`, `dir`, `fd`, `rwsize`) that had gone
  red after a model upgrade.
- **Leaf-first contract extensions** (sys_close / sys_fstat-EBADF / sys_lseek +
  wrappers), zero new trust.
- `bugs-to-report/…-import-stub-missing-use-array.md` (CONFIRMED emitter bug),
  `getting-better/…-formal-test-context-pollution.md`, and Gate-S-passed
  `pycsl-monitoring` updates.

**Independent verification (the monitoring discipline — did not trust the report):**

| Claim | Independent re-check | Result |
|---|---|---|
| 7 changed/new tests prove | re-ran each, `PYTHONHASHSEED=0` | all SUCCESS, 0 non-Valid ✅ |
| 0 new `\trusted` | grep gate diffs + test files | none ✅ (the "trusted" hits are comments) |
| `__init__` gate stays green | full re-run | **1159 / 0** (↑ from 1129; the +30 wrapper ensures discharge) ✅ |
| body gate not regressed | full re-run | **2016 / 8** — the *same* 8 residuals; +30 Valid from the new method ensures ✅ |

**Honest residuals flagged for the human (cannot self-certify):**
- `chmod` / `truncate`: **PARTIAL** — return-code-only; no mode/size accessor at the
  `os.*` layer to state the deeper consequence (logged as a gap, not a false green).
- **reopen-by-name** content/size round-trip still open (the **on-fd** round-trip *is*
  proven via `formal_os_content`).
- `formal_os_io.py` reaches internals (`UnixInodeFileSystem`, not public `os.*`) — a
  **pre-existing** barrier irregularity, not from this mission; flagged, untouched.
- Scope faithfulness (the 40-symbol set as "all syscalls") — a human judgment call.

---

## 6. Current repository state

**Merged to `main` this session:**
- PR #16 — 3 test-harness emitter bug fixes + `pure_lib_test/` naming unification.
- PR #17 — the `sys_write` fd_block empty-write soundness fix (restored the red gate).

**On branch `docs/sl-loops` (committed `3998840`, not pushed/merged):**
- `formal-test-sl.md`, `test-supervise-sl.md`, `config/skills/pycsl-monitoring/`,
  `getting-better/`, `bugs-to-report/`.

**Uncommitted in the working tree (the supervised-mission output, verified):**
- New: `pure_lib_test/formal_os_close.py`, `formal_os_lseek.py`
- Repaired: `pure_lib_test/formal_os_{query,meta,dir,fd,rwsize}.py`
- Zero-trust leaf extensions: `pure_lib/os/UnixInodeFileSystem.py`, `pure_lib/os/__init__.py`
- `config/skills/pycsl-monitoring/SKILL.md` update; new `bugs-to-report/` and
  `getting-better/` entries.

**Not mine to commit:** the `sl-*` foundation skills (`config/skills/sl-*`) are the
user's own additions — left for a separate `fabrice:`-prefixed commit.

**Gate status now:** os `__init__` gate **1159/0 green**; body gate **2016 Valid / 8
residual** (the same 8 long-standing residuals — `sys_rename` ×2 genuine-hard,
`sys_write` ×3 aggregate noise, `_now` ×1 invariant noise, `_unpack_direntry` ×2
genuine-small).

---

## 7. Open items

- Commit decision pending on the supervised-mission os formal-test work.
- `_unpack_direntry` precondition: retry with the minimal 2-clause form on an
  unloaded machine; confirm the `no_inline`-across-import behavior (`bugs-to-report/`).
- `chmod`/`truncate` deeper consequences and the reopen-by-name round-trip remain the
  functional-correctness frontier.
- `sys_rename` no-trust closure remains genuinely SMT-infeasible (needs a different
  prover or the ready trusted swap).
