# Stdlib annotation — Extreme Rigor (ER)

> **Load when:** starting a standard-library annotation pass (Python
> `os`, Go `bytes`, C `string.h`, …) or when a baseline stdlib stub
> needs to be promoted to a real model.

## TL;DR

The default Phase 9 stdlib pass writes `\trusted reviewer:
<lang>-stdlib` stubs derived from official API docs and ships. That
is the **baseline**. **Extreme rigor** is the **goal state**:
body-verify what you can, axiom-anchor what you cannot, and pair
every remaining `\trusted` with a named gap in a tracked feature
plan. `\trusted` stays a tool — it stops being the default.

## Why the bar moves for stdlib

Real programs call stdlib continuously. If the stdlib annotations
are `\trusted` stubs:

- Every contract that depends on stdlib semantics becomes Tier-2
  trust — large surface, silent erosion.
- The verifier's own annotations end up indirectly trusted via
  their stdlib dependencies (self-annotation passes vacuously over
  stdlib-stub edges).
- Real-program proofs become "we verified the logic, trusting that
  `os.read` does what we said it does" — the gap doc never says.

ER for stdlib closes that loop. Each stdlib function carries a
*model* of its semantics that the prover can reason about, not a
prose hand-wave.

## The canonical example: `unix-filesystem/UnixInodeFileSystem.py`

666 lines. A Unix-like inode filesystem (32 inodes, 256 blocks,
1024-byte blocks, 10 direct blocks per inode) with 20 sys_*
system-call entry points and the four internal helpers
`_read_inode`/`_write_inode`/`_read_directory`/`_write_directory`.
Annotated to demonstrate the ER bar.

Where the file lands today:

| Method | State | Why |
|---|---|---|
| `_get_bitmap` | **body-verified** + Coq axiom | `(x >> y) & 1 ∈ {0, 1}` blew up Z3 at ~3.4B steps; the Coq theorem `UnixFs.Bitmap.bit_and_one_in_zero_one` (`Z.land_ones` + `Z.mod_pos_bound`) is imported as a Why3 axiom and Z3 dispatches in zero steps |
| `_set_bitmap` | body-verified | straight bitwise update, SMT handles |
| `_alloc_inode`, `_alloc_block` | body-verified | range-loop with explicit invariants + variants |
| `_format_disk` | body-verified | sequential bitmap setup, no surprises |
| `_read_directory` | **body-verified** + round-trip axiom | uses `struct.unpack('>H30s', ...)`; cites `UnixFs.Struct.i1a1.round_trip` |
| `_read_inode`, `_write_inode`, `_write_directory` | `\trusted + axiom` | each `cite:_note:` names the IR-feature gap (dict-literal returns, `*list` spread in call args, array-slice-assign with non-int RHS, `bytes.encode`/`.ljust`/`.split`) tracked in `missing-pycsl-ir-features.md` |
| `sys_*` (20 methods) | `\trusted reviewer:` at the syscall boundary | API surface — model lives at the internals layer |

What the file demonstrates:

1. **Body-first.** Every method that *could* be body-verified, is.
2. **Coq lemma for SMT timeouts.** The `_get_bitmap`
   `#@ proof rocq UnixFs.Bitmap.bit_and_one_in_zero_one` pattern.
   Companion proof in
   `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v`.
3. **Round-trip axioms for inverse operations.** Three formats
   (`i1a1`, `i2`, `i18`) each have a Coq witness module under
   `UnixFs.Struct.Fmt_<id>` that proves `unpack(pack(...)) = ...`
   by `reflexivity` on a concrete list-of-Z model — and a matching
   entry in `src/pycsl/module6_whyml/preamble.py:_AXIOM_REGISTRY`.
4. **Trust at the right layer.** The 20 `sys_*` calls are
   `\trusted` at the POSIX-boundary; internals are body-verified.
   Trust placement is intentional, not accidental.
5. **`\trusted` with a path forward.** The three internal methods
   that stay `\trusted+axiom` each cite a specific IR feature gap
   in `missing-pycsl-ir-features.md` — the file isn't a dead end,
   it's a forcing function for the next IR work.

Read the file end-to-end before annotating any other stdlib module.

## Acceptance criteria for an ER-grade stdlib module

A module annotated to the ER bar passes ALL of these:

```
- `pycsl <path/to/module.py>` exits 0
- `bin/cmmi-audit.sh --quick` reports `[STRUCT]` (or equivalent
  audit step for the module's domain) with at least N
  body-verified entries
- Every loop in the body has BOTH a `#@ loop invariant` and a
  `#@ loop variant` annotation
- Every `\trusted reviewer:` carries a `cite:_note:` that:
    * Names the IR-feature gap blocking promotion (not "Module 6
      limitation"; the precise gap)
    * Points to a feature plan tracking that gap
- `Print Assumptions` on the companion Coq proofs returns ∅ (no
  Admitted, no Axiom beyond explicit kernel axioms)
- `coqc -q <path>/.proofs/rocq/*.v` exits 0
- The module's audit step shows zero entries in `unknown` category
  (every method's trust state is classified, no dark matter)
```

These are the lines that belong in a `**Acceptance:**` block under
`bin/agent-feature-supervisor` (see `feature-supervisor-extreme-rigor.md`
for the supervisor side). Once supervisor enforcement lands, the
checks above are machine-enforced per phase.

## The escalation ladder

When body verification fails, the **prescribed** sequence:

1. **Strengthen the invariants.** Most "stuck" body proofs are
   missing one invariant. Try the trivial ones first
   (`0 <= idx <= N` and the for-range bound `N - idx`). Then the
   list-length bounds (`len(X) <= idx` for append-targets — works
   only if PyCSL knows X is an append-target; see
   `_handle_len_call` in `module6_whyml/expressions.py`).
2. **Import a Coq lemma.** If the obligation is mathematically
   provable but the SMT solver hangs, write a Coq theorem in the
   companion `.proofs/rocq/` module and import via
   `#@ proof rocq <qualname>`. Add the matching
   `_AXIOM_REGISTRY` entry. The Coq must be `Qed`, no `Axiom`, no
   `Admitted`.
3. **Carve a feature-plan gap and `\trusted` with a pointer.**
   When the obligation requires an IR feature PyCSL doesn't have
   yet (dict-literal return, list spread, bytes methods, etc.):
   add the gap to the relevant `missing-*-feature.md`, set
   `\trusted reviewer:`, and write a `cite:_note:` quoting the gap
   identifier from the plan.
4. **Drop scope.** If steps 1–3 fail and the gap is genuinely
   out-of-scope for this annotation pass, drop the method from
   the pass with a note saying so. Better to admit the limit than
   to ship a `\trusted` with no path.

**Never** (the anti-pattern this ladder replaces):

5. Silently `\trusted` and move on. The audit step will count it
   as `trusted-only` and the work will be invisible.

## What ER work always produces

An ER stdlib pass is supposed to expose IR-feature gaps. The
UnixInodeFileSystem pass exposed six (catalogued in
`missing-pycsl-ir-features.md`):

1. Dict-literal in return value (blocks `_read_inode`)
2. Tuple-subscript on struct_unpack returns (blocks `_read_inode`)
3. `*list` spread in call args (blocks `_write_inode`)
4. Array-slice-assign with non-int RHS (blocks `_write_inode`,
   `_write_directory`)
5. `bytes.encode` / `.ljust` / `.split` methods (blocks
   `_write_directory`)
6. Append-target auto-invariant in for-range loops (partially
   landed during Phase 4 gap closure)

Treat the output of an ER pass as having **two** deliverables: the
annotated module *and* the missing-feature plan it surfaced.
Skipping the second deliverable means the next pass repeats the
same blockers.

## Pointers

- **Supervisor enforcement of ER:**
  [`feature-supervisor-extreme-rigor.md`](../../../../feature-supervisor-extreme-rigor.md)
- **The example IR-gap catalogue:**
  [`missing-pycsl-ir-features.md`](../../../../missing-pycsl-ir-features.md)
- **The case-study Coq proofs:**
  [`unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v`](../../../../unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v)
- **The Coq axiom-import pattern (Phase 6 trust-anchoring):**
  [`phase-formal-semantics.md`](phase-formal-semantics.md)
- **The baseline Phase-9 stdlib pass that ER builds on:**
  [`phases-trust-discipline.md`](phases-trust-discipline.md)
