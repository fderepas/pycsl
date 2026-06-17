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

## BINDING: the extreme-rigor path is the ONLY path

`test-supervise-sl` is the bearer of the extreme-rigor doctrine (full text in
`test-supervise-sl.md` §Doctrine). The operative rule, restated here because every
run reads this store: **a residual is NEVER closed by adding trust.** A raw
`\trusted`, a reviewer-trusted helper, or a "ready trusted swap" (e.g.
`_rename_swap`) is **struck from the option set** — it is a Gate-B/Gate-C REJECT, not
a choice. The only sanctioned closure routes are (a) Rocq+Lean cross-validated +
cited `#@ proof`, (b) a restructured / re-folded proof, (c) a different prover /
tactic. **If none discharges the goal, the target is a LOGGED GAP routed to the
human — never a trusted "done", and never offered as "accept the trusted swap".**
Adopting even a cross-validated axiom (kernel-PROVED, not bare `\trusted`) is a
human-gated TCB decision, not the loop's. Recorded GAPs under this rule (e.g.
`sys_rename`, see §C) stay open until a rigorous route lands.

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
7. **Keep array-heavy reopen/read/write consequence theorems in their OWN file.**
   A light fd-chain / namespace theorem that PROVES in isolation can flip to
   `Unknown` purely by being co-located with a heavy `open→write→close→reopen→read`
   theorem in the same module (shared E-matching context starves the light goal's
   step budget). Byte-identical body + import set, different verdict — the only
   variable is the sibling theorems. Diagnose by re-proving the goal alone; do NOT
   blame a missing contract. *(Carve-out: split `content_round_trip*` out of
   `formal_os_fd`/`formal_os_rwsize` this session; see
   `getting-better/20260616-2050-formal-test-context-pollution.md`.)*
8. **Co-import an array-trigger op (`mkdir`+`access`) with a return-code-only
   filesystem stub.** Importing `chmod`/`truncate` alone yields
   `unbound type symbol 'array'` at L3-tc — the emitter omits `use array.Array`
   when no imported contract carries an explicit array term, even though the
   pulled-in helper `val`s reference `array int`. Co-importing+calling `mkdir`
   (whose `dir_lookup` ensures is an array term) emits the `use`. *(CONFIRMED
   emitter bug: `bugs-to-report/20260616-2050-import-stub-missing-use-array.md`.)*

## B. Coherent-and-wrong catalog for formal tests (what the monitor hunts)

| Shape | Tell | How the monitor catches it |
|---|---|---|
| **Self-return assertion** | `#@ ensures \result == 0 or 1` — holds even if the op fails | Gate C non-vacuity seed: break the op, the test must FAIL |
| **Simulation** | the driver mutates the data structure / inlines internals instead of calling the API | API-only audit; the physical barrier prevents it at source |
| **Adjacent-weaker** | proves the byte-COUNT round-trip while claiming the byte-VALUE round-trip (`formal_0008` `back == c` int-vs-array) | clause map: the `ensures` must be the *intended* property, not a weaker cousin |
| **Plane blend** | a `--no-proof` (emission) green reported as "proven" | no-blend: emission ≠ proof |
| **Honorary green** | "the gate is green" from a stale/partial run | re-run on the committed file; scan EVERY status incl. `Out of memory` |
| **Aggregate noise mistaken for a residual** | a goal fails in the full-file gate but proves in `--fun` isolation | re-check residuals per-method before recording them as real |
| **Stale test after a model upgrade** | a committed `formal_*` file FAILS at L3-tc with `int`-vs-`string` type errors, or its header claims a consequence is "UNPROVABLE/Unknown" that now proves | the model gained str-typed path params / `dir_lookup` consequence ensures since the test was written; RUN it, fix the param types, and rewrite the stale header to the now-passing reality (don't trust the comment) |
| **Context pollution mis-blamed on a missing contract** | a theorem is `Unknown` in-module but the author "fixes" it by weakening or adding a contract | re-prove the goal ALONE; if it passes in isolation the contract is fine — split the file instead (pattern A.7) |

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
  `formal_os_*` family. As of 2026-06-16 (test-supervise-sl os mission) ALL 19
  `formal_os_*.py` files prove SUCCESS / 0 non-Valid / 0 `\trusted`, each
  re-confirmed non-vacuous from the supervisor's disjoint base (seeded
  falsification flips to FAILED). Every public `os.*` symbol in `__init__.py` has
  a proven consequence (not return-code-only) EXCEPT `walk` (yields, geometry
  only) and the pure stubs (chflags/confstr/copy_file_range/getxattr/listxattr/
  kill/islink — total constants by spec) and chmod/truncate (return-code only;
  no mode/size accessor — model gap, below).
- **Leaf-first extensions this session (zero new trust, body-faithful):**
  `sys_close` gained `\result==0 ⇒ fd_open[fd]==0` (close post-state); `sys_fstat`
  gained the EBADF twin `fd_open[fd]==0 ⇒ \result==-1`; `sys_lseek` gained the
  SEEK_SET consequence `whence==0 ∧ offset≥0 ∧ open ⇒ \result==offset ∧
  fd_offset[fd]==offset`. Propagated to the public `close`/`fstat`/`lseek`
  wrappers. New tests: `formal_os_close` (close→fstat==EBADF) and `formal_os_lseek`
  (lseek SET returns pos). Body gate failing-goal set UNCHANGED by these edits
  (same step-count fingerprints: 320459/337358/4621194) → no regression.
- **Open frontiers (logged gaps, not failures):** reopen-by-name content/size
  round-trip (write count is `<=` not `==`; reopened size unpinned through
  reopen-by-name) — the on-FD round-trip IS proven (`formal_os_content`);
  open(absent,O_RDONLY)==-1 with absence NOT pre-established (a never-created
  name's `dir_lookup` is havoc'd — provable only WITH an established absence, as
  in `formal_os_enoent` after mkdir→rmdir); chmod mode-reflected / truncate
  size==length (return-code-only contracts, no accessor); multi-block content;
  `sys_rename` no-trust closure — **a LOGGED GAP, not a trust candidate**: the only
  doctrine-compliant routes are a different prover / a restructured proof / composing
  its already-cross-validated lemmas in-context; the ready reviewer-trusted
  `_rename_swap` is OFF THE MENU (see the BINDING rule above).

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
