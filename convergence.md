# The Convergence Principle

A section for `config/skills/pycsl-stdlib-coverage`.

## Why

Covering the Python standard library with formal proofs serves **two purposes at once**:

1. **Annotate the stdlib formally** — re-express each module as a faithful pure-Python model and prove
   it by Hoare logic, exactly as `docs/formal-filesystem.md` does for `os`.
2. **Debug the PyCSL tool** — the verifier is new, so pushing a real module through it to a faithful
   proof is the best stress test there is. Where the model is correct but the tool cannot express or
   discharge it, the proof attempt has found a **tool bug**.

These two goals are not separate tasks done in sequence — they **converge**. Every stdlib module proved
faithfully exposes tool gaps; fixing those gaps improves the tool; a better tool lets more of the stdlib
be proved. The fixed point is a faithfully-proved module *and* a tool with no remaining gaps for it.

## The loop

A **coordination agent** orchestrates a ping-pong between two worker agents, mediated by a **gap
document**:

```
                         ┌─────────────────────────┐
                         │   coordination agent     │
                         │  (orchestrate + approve;  │
                         │   never edits code)       │
                         └───────────┬──────────────┘
              spawn on a module       │        approve gap → spawn
              (formal-filesystem.md)  ▼                      ▼
                    ┌────────────────────┐        ┌────────────────────┐
                    │    stdlib-agent     │        │     tool-agent      │
                    │ prove pure_lib/<m>  │        │ read the gap doc;   │
                    │ faithfully; on a    │  gap   │ fix the verifier;   │
                    │ tool limitation,    │ ─────► │ gate (byte-diff +   │
                    │ write a GAP DOC     │  doc   │ proof + conformance)│
                    └─────────┬──────────┘        └──────────┬─────────┘
                              │                              │
                              └──────────◄───────────────────┘
                               respawn stdlib-agent to continue
                                  (now unblocked)
```

1. The coordination agent **spawns a `stdlib-agent`** on a target `pure_lib/<module>`, instructing it to
   apply the `docs/formal-filesystem.md` strategy: English spec → faithful pure-`str`/real-typed model →
   contracts → SMT proof → a loop-closing formal driver. Faithfulness is non-negotiable (the no-more-int
   doctrine: real WhyML type classes, never an int stand-in; never a false postcondition).
2. When the `stdlib-agent` hits something the model needs but the **tool cannot do** (a missing lowering,
   an ill-typed emission, an unsound default), it stops at that point and **writes a gap document** —
   each gap with: symptom, minimal reproducer, root cause (`file:line`), the workaround it used (if any)
   so its own proof stays clean, and a proposed fix. It finishes everything it *can* prove faithfully,
   then hands the gap document back.
3. The coordination agent **reviews and approves** the gap document (tool changes are higher-risk than
   model work, so they pass an explicit gate), then **spawns a `tool-agent`** with it.
4. The `tool-agent` reads the gap document, implements the verifier fix, and **gates it** — byte-identical
   `.mlw` everywhere else, the affected module/drivers prove, both conformance corpora pass, doc-coherency
   green. It touches *only* the tool, never the stdlib model.
5. The coordination agent **respawns a `stdlib-agent`** to continue from where the previous one stopped,
   now unblocked by the fix.

The loop repeats until a pass produces **no new gaps** — at which point the module is faithfully proved
and the tool has no remaining gaps for it.

## Roles (kept strictly separate)

- **coordination agent** — orchestrates the loop, holds the approval gate, sequences the spawns. It never
  edits code; its job is decide-and-dispatch.
- **stdlib-agent** — proves one `pure_lib/<module>` faithfully via `docs/formal-filesystem.md`. Edits only
  the model + its formal driver. Its output is *a proved module and/or a gap document*.
- **tool-agent** — fixes the verifier for one approved gap document. Edits only `src/pycsl/`. Its output is
  *a gated tool fix*. It never weakens the model to dodge a real gap.

## Artifacts

- **The gap document** is the contract between the two workers — the only thing that crosses from the
  stdlib side to the tool side. (Example from the strmod run: `10-1732-gap.md`.)
- **The proved module** (`pure_lib/<module>/` + its `pure_lib_test/formal_<module>.py` loop-closer).
- **The gated tool fixes** (one commit per gap).

## Invocation

Saying **"apply the convergence principle to `<module>`"** spawns the coordination agent on
`pure_lib/<module>` and runs the loop above to its fixed point. For example, **"apply the convergence
principle to strmod"** targets `pure_lib/strmod/`.

## Worked precedent

The strmod pass already ran this loop once, by hand: a stdlib-agent rebuilt `pure_lib/strmod/` on real
`str` and proved it (commit `a50bc61`), surfacing three tool gaps it worked around and recorded in the gap
document `10-1732-gap.md` (the hardcoded `exception Return int`; `len()` over a string-returning call;
the int-`0` default fill for a non-`int` param). The next turn of the loop is a tool-agent fixing those
gaps — after which a fresh stdlib-agent can prove strmod's functions with their *natural* control flow
(early returns, omitted defaults) instead of the workarounds. That is convergence: the module pushed the
tool, the tool fix lets the module be pushed further.
