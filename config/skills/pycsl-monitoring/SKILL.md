---
name: pycsl-monitoring
description: >-
  The accumulated, Gate-S-audited knowledge base of the `test-supervise-sl`
  squeeze loop (the monitor that drives `formal-test-sl`). Holds the proven
  patterns for getting PyCSL formal tests to fully prove, the coherent-and-wrong
  catalog for formal tests (the vacuous-test shapes), per-module coverage ledgers,
  and the discipline for adding knowledge (only via Gate S, traceable, carve-outs
  cite the upper bound). Consult and update this whenever supervising or monitoring
  a fleet of formal-test runs, deciding whether a learned heuristic is in-band,
  diagnosing why a formal test will not prove, or recording coverage. Trigger
  phrasings: "monitor the formal-test loop", "what patterns make a formal test
  prove", "is this formal test vacuous", "record formal-test coverage", "audit a
  consolidated formal-test skill", "Gate S on a PyCSL heuristic", "what's the os
  formal-test coverage".
---

# pycsl-monitoring — knowledge store for `test-supervise-sl`

This skill is the **persistent, disjoint knowledge base** that the supervising loop
`test-supervise-sl` (see `test-supervise-sl.md`) accumulates while monitoring the
base loop `formal-test-sl` (see `formal-test-sl.md`). It is written **only by the
disjoint skill-monitor**, never by the base loop about itself (that would be
self-judging). Everything here has passed **Gate S** (`sl-monitoring-sl`).

## Discipline for adding knowledge (non-negotiable)

- **Gate S first.** A heuristic enters this file only after the skill-monitor
  classified it (ignore-signal vs defer-to-oracle), ran the matching check (trigger
  / validity test against the PyCSL oracle), and returned PASS or CARVE-OUT. A
  REJECT is logged, not kept.
- **Grounded & traceable.** Each entry cites the upper-bound clause (spec /
  methodology rule) it serves, and the run/inputs that revealed it.
- **Carve, don't discard.** Narrow an over-general skill with a bound-deferring
  exception; keep the valid core.
- **Safe direction.** An entry may only make a formal test *stronger / more
  faithful*, never license a weaker or vacuous one.
- **Disjoint authorship.** Only the monitor writes here. The base loop may *propose*
  a skill (a returned soft output); it does not *enter* it.

---

## A. Proven patterns (what makes a PyCSL formal test fully prove)

*(Seeded from the os work; each is a PASS/CARVE under Gate S.)*

1. **Test the observable CONSEQUENCE, not the op's return code.** A formal test is
   setup → operate → observe (write→read-back; mkdir→stat-sees-it→rmdir→stat-gone).
   Asserting the op's own `\result` is vacuous. *(Serves: the consequence rule.)*
2. **Call the public API; never simulate.** The driver calls `os.*` / the module
   API; it never re-implements the op on the data structure or inlines internals.
   Enforced physically: the driver author's context has API + spec only, not the
   internals — so it *cannot* simulate. *(Serves: the calls-the-API rule.)*
3. **Leaf-first, compose-don't-re-derive.** When a clause won't discharge, the cause
   is usually a missing **leaf VALUE contract**; fix bottom-up (the codec leaves'
   value contracts compose into the inode round-trip; the syscall reuses proven
   contracts via `#@ no_inline`). Never weaken the test to land.
4. **Cross a `#@ no_inline` boundary with a FOLDED uninterpreted atom, never a bare
   `∀i`.** A `\forall i …` (and `\array_eq`, which lowers to the same `∀i`) does NOT
   propagate across a `no_inline` boundary (Alt-Ergo and Z3 both go Unknown). Fold
   the per-element fact into an uninterpreted predicate (e.g. `block_content_eq`)
   with definitional intro/elim; the atom crosses as one term. *(This is the gap-17
   content-round-trip mechanism.)*
5. **A non-vacuous range/value postcondition needs an early-return guard.** If an
   early path (`if n == 0: return 0`) returns before establishing the claimed field,
   guard the ensures antecedent (e.g. `\result >= 1`) — else the claim is false on
   that input. *(Carve-out from the fd_block empty-write bug this session.)*
6. **Re-run the gate on the COMMITTED artifact; never re-report an intermediate
   count.** A green taken from an intermediate run while the committed file is red is
   the self-declared-done collapse. Run `PYTHONHASHSEED=0` on the file as it stands.

## B. Coherent-and-wrong catalog for formal tests (what the monitor hunts)

| Shape | Tell | How the monitor catches it |
|---|---|---|
| **Self-return assertion** | `#@ ensures \result == 0 or 1` — holds even if the op fails | Gate C non-vacuity seed: break the op, the test must FAIL |
| **Simulation** | the driver mutates the data structure / inlines internals instead of calling the API | API-only audit; the physical barrier prevents it at source |
| **Adjacent-weaker** | proves the byte-COUNT round-trip while claiming the byte-VALUE round-trip (`formal_0008` `back == c` int-vs-array) | clause map: the `ensures` must be the *intended* property, not a weaker cousin |
| **Plane blend** | a `--no-proof` (emission) green reported as "proven" | no-blend: emission ≠ proof |
| **Honorary green** | "the gate is green" from a stale/partial run | re-run on the committed file; scan EVERY status incl. `Out of memory` |
| **Aggregate noise mistaken for a residual** | a goal fails in the full-file gate but proves in `--fun` isolation | re-check residuals per-method before recording them as real |

## C. Per-module coverage ledger

### os (`pure_lib/os/`) — as of 2026-06-16
- **Body gate (authoritative, full file):** 1986 Valid / 8 residual (99.6%).
  Residuals classified: `sys_rename` ×2 (genuine, SMT-infeasible no-trust),
  `sys_write` ×3 (aggregate E-matching noise — 400/0 in `--fun` isolation),
  `_now` ×1 (byte-range class-invariant noise), `_unpack_direntry` ×2 (genuine
  leaf precondition — fix found but perturbs the `__init__` gate; deferred).
- **`__init__` gate:** 1129/0 green (restored this session — was silently red
  1128/2 from the fd_block empty-write over-claim).
- **Proven formal tests:** `formal_os_roundtrip` (18/18, totality), `formal_os_content`
  (48/0, on-fd write→pread==data content round-trip), plus the topical
  `formal_os_*` family.
- **Open frontiers (logged gaps, not failures):** reopen-by-name content round-trip
  (create→write→close→reopen→read==data); multi-block content (Phase 2 loop `∀i`
  divergence); `sys_rename` no-trust closure.

*(Other modules: `re` 16/16 stub-level; `warnings` 18/18 body + 3/3 formal;
`json` 6/6 thin-API. Add ledgers here as missions cover them.)*

---

## D. Outputs the loop files elsewhere

- **`getting-better/`** — ergonomic feature ideas (PyCSL/tooling improvements that
  would make formal tests easier). One concern per `YYYYMMDD-hhmm-name.md`.
- **`bugs-to-report/`** — candidate PyCSL bugs with minimal repro and
  `STATUS: CONFIRMED|UNCONFIRMED`. One per `YYYYMMDD-hhmm-name.md`.

These are *proposals*, not knowledge — they live outside this skill until acted on.
When a bug is fixed or a feature lands, fold the resulting durable lesson back here
(under A/B) via Gate S.
