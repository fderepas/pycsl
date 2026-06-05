# §0 — Alias audit of pycsl's own source

**Status:** Finding (by-hand audit, 2026-06-05) · **Decides:** whether A2b-2 (the alias checker) is on
the critical path (`no-more-int-7.md` §0). **Result: pycsl is alias-clean in the problematic sense →
A2b-2 is NOT triggered by self-hosting; it becomes a contingent future item.**

## The question
Does pycsl's own source mutate a mutable object **through aliases** — i.e. are there two
simultaneously-live references to one mutable object, both *written*, where the interleaving matters?
That pattern is the one the value-semantics boundary excludes; everything else (local accumulation,
stack-scoped borrowing, read-only sharing) is within the discipline.

## Method (cheap, by hand)
Scanned `src/pycsl/*.py` + `module6_whyml/*.py` + `module5/*.py` (~18.5k LOC) for the red flags:
1. **Mutable default arguments** (`def f(x, acc=[]/{})`) — the classic shared-alias bug.
2. **Field aliasing** — `self.X = <name>` where `<name>` is later mutated (so `self.X` mutates too).
3. **Container aliasing** — a mutable stored in a dict/list while the original is kept and both mutated.
4. **Out-parameters** — a mutable passed to a callee that mutates it in place.

This is a *targeted pattern scan*, not a sound static alias analysis — it gives strong evidence, not
proof. A sound check is A2b-2 itself (only built if this audit had found aliasing).

## Findings

| Pattern | Found | Verdict |
|---|---|---|
| Mutable default args | **0** | clean — disciplined code |
| `self.X = <name>` then mutate | 1 (`Module5:1434 self.tree = tree`) | **clean** — `tree` is the parsed AST, only *read* by `emitter.visit(self.tree)`; never mutated. Store-and-read. |
| Container stores a name | a few (`types.py [target] = elem_map`, rename maps) | **clean** — each stored value is *freshly constructed* (dict comprehension / fresh literal) and never mutated after storage. |
| Out-parameters (`_emit_*(…, out, …)` append in place) | yes (common) | **within the discipline** — stack-scoped *borrows*: the callee appends to the caller's accumulator and returns; the callee's reference dies at return; no two simultaneously-live writers. |

**No shared mutable aliasing was found.** pycsl's mutation is exclusively:
- **Local accumulation** — build a `lines`/`out` list (or dict/set) and return it (value semantics);
- **Stack-scoped borrowing** — out-parameters the callee mutates and the caller resumes after
  (a mutable borrow, the Creusot/Dafny-acceptable case A2b-1 explicitly allows);
- **Store-and-read** / **fresh-value-into-container** — no write through a second live name.

## Consequence for the plan
- **A2b-2 (the ~3–4 wk alias-check frontend) is NOT on the self-hosting critical path.** pycsl already
  lives inside the value-semantics boundary. A2b-2 drops to *"build only if a third-party-code use
  case ever demands it."*
- **Honest status of the no-more-int program: essentially complete**, with A2b-2 a contingent future
  item rather than "the one substantial track remaining."
- **A2b-1 (specify the discipline) is still worth doing** — it formalizes *why* pycsl is within the
  boundary (out-params = stack-scoped borrows; values entering containers are snapshots), documents it
  for users, and unblocks A1-residual's seq-model. But it documents an *already-satisfied* discipline
  rather than gating a build.
- **The next milestone is the self-hosting push itself**, not a verification feature — exactly the
  shift `rq.md` predicted if the audit came back clean.

## Caveat
By-hand pattern scan, not a soundness proof. If self-hosting later surfaces a missed aliasing site,
that site becomes a concrete driver for A2b-1 to classify (and, only then, possibly A2b-2 to enforce).
