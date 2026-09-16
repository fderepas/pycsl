# ROUTE #143 — an IMPORTED function's `raises` condition is folded against the IMPORTING module's constants

**Status: REPAIR DRAFTED by gen #29 (worktree, drafts 1-4); battery pending — see "Gen #29" at the end.**
Severity 1. Both directions measured. Generator: carrier-rerun, on gen #27's own #140/#141 repairs.

## The exploit (measured, both directions)

`test-suite/corpus/pycsl-reference/multi_file_lib/r141_raiselib.py` (created by gen #27, committed):

```python
LIM = -1

#@ raises ValueError when LIM < 0
#@ assigns \nothing
def f(k: int) -> int:
    if LIM < 0:
        raise ValueError
    return k
```

and the importer:

```python
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f

LIM = 5

#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)
```

**PyCSL: `Verification SUCCESS`. CPython: `caller(3)` raises `ValueError`.**

The emitted WhyML says it in one line — the callee's own `val` contract already carries the
importer's value:

```
  val f (k: int) : int
    raises { ValueError -> ((5) < 0) }

  let function caller (k: int) : int
  =
    begin assert { not (((5) < 0)) }; try (f k) with ValueError -> absurd end end
```

`LIM` is the **dependency's** constant (`-1`). It was rendered as the **importer's** `5`.

## The mechanism — and it is NOT the `_wrap_call_with_callee_raises_assert` substitution

Gen #27's routes #140 and #141 both live in `Module6_WhyMLTranspiler._render_callee_condition`.
This one does not: the condition is already wrong in the injected `val` itself, before any
call-site wrap. The cause is in `src/pycsl/frontend/ir_resolve.py::_resolve_direct_imports`:

```python
dep_consts = (cache.get(os.path.abspath(resolved), {}) or {}).get("module_constants", {})
if dep_consts:
    own = ir_data.setdefault("module_constants", {})
    for local, orig in names:
        if orig in dep_consts and local not in own:
            own[local] = dep_consts[orig]
```

Two facts combine:

  1. the loop runs over `names` — the names the importer **explicitly imported** (here just `f`).
     `LIM` is never even considered, so the dependency's `LIM = -1` is not propagated; and
  2. the injected function's contract IR is lowered **in the importer's namespace**, where the
     constant folder finds the importer's `LIM = 5`.

The comment on that block — *"Local definitions win on a name clash (only fill names the importer
does not already define)"* — is the right rule for the importer's own code and the wrong rule for
a contract that crossed the boundary. **A name free in a contract that travelled across a module
boundary does not denote what the importing module's binding denotes.**

## The fence that DOES hold, and why the hazard is exactly the shadowing case

Delete `LIM = 5` from the importer and the same program is REFUSED:

```
  val f (k: int) : int
    raises { ValueError -> (lIM < 0) }
    begin assert { not ((lIM < 0)) }; ...
```

`lIM` lowers to an unconstrained `val constant`, the assert is unprovable, and the proof fails.
So the route needs the importing module to **bind the same name**; without the clash the model is
already fail-closed by accident.

## The scoped repair (NOT landed)

In `_resolve_direct_imports`, after `_inject_functions`, for each injected function compute the
free names of its contract clauses (the file already has `_contract_referenced_names`) minus that
function's own `formal_params`. If any such name is bound by the IMPORTING module — as a module
constant, a module global, or a def/class — **refuse** with a PyCSLSemanticError naming the
function, the name, and both values. Fail-closed and precise: the non-clashing case already
lowers to an unconstrained constant and needs no change.

## Why gen #27 did not land it

The population was not censused. `#@ raises ... when <non-parameter>` exists in the tree
(`FileNotFoundError when dir_lookup(_filesystem.dir, 5, filepath) < 0` and
`OSError when (fd >= 64 or _filesystem.fd_open[fd] == 0)` in `src/pycsl_lib`), and those
conditions reference a module GLOBAL that is carried across the boundary by a *different*
propagation block (`11-1039-spec-10`). Whether any corpus program imports such a function AND
binds a clashing name was not measured, and a refusal that fires on the `pycsl_lib` os stubs
would be a suite regression rather than a finding. **Census that population first, predict the
refusal set, then land it.** A half-gated import-boundary change is worse than an honest open
route.

## Reproduction

  - helper: `test-suite/corpus/pycsl-reference/multi_file_lib/r141_raiselib.py` (committed)
  - exploit and control: `scratchpad/g27/j1.py` (PROVES, CPython raises) and
    `scratchpad/g27/j2.py` (the same file without `LIM = 5` — correctly refused)
  - probe-ledger rows: `g27-cross-module-raises-condition-folded-in-the-importers-scope`


## Gen #29 — re-measure, wider shapes, and the repair

**Re-measured at `260bb92a`.** j1 still PROVES. NOTE: gen #27's `j1.py`/`j2.py` must be run with the
corpus on the import path; from `scratchpad/g27` the import prints `external module ... skipping`
and j2 then PROVES for an unrelated reason (nothing is imported).

**The route is wider than `raises` and wider than a from-import.** All PROVED at HEAD with CPython
contradicting: a MODULE import (`lib.f(k)`, witness 1465), a WILDCARD import rebound afterwards
(1466), an imported CLASS's method (1467), a name the importer imports FROM ANOTHER module (1468),
and an ENSURES clause (`\result == BASE`, 1475). FAIL-CLOSED at HEAD (the proof or Why3 refuses),
refused now: a binding in a module-level `if` (1469), a name reaching the importer only through
another module's wildcard (1470) or a two-hop wildcard (1474), a condition CALLING a helper the
importer redefines (1471). FAIL-CLOSED and untouched: a caller LOCAL or PARAMETER named like the
dependency's constant — the call-site assert binds it, but the `with ValueError -> absurd` arm is
judged against the `val`'s own global, and stays unprovable.

**The repair (inside `resolve_imports`, no new `def`s).** `_process_dependency` tags every
dependency function with its file; at the end of `resolve_imports` every tagged function that
reached the importer is checked and the tag POPPED (the resolved IR — the frozen goldens — never
carries it). REFUSE when a name is (a) read by the injected contract — a `Var`, a string `Call`
callee or an `Attribute` root, every clause; (b) bound at module level by the function's own file,
its wildcard sources followed transitively; (c) not a formal parameter or `self`; and (d) bound at
module level by the importer by anything other than an import of THAT name from THAT file, or —
when the importer does not bind it explicitly — exported by a wildcard import of another file.
Positive control 1472: `from lib import g2, LIM` is allowed and `requires k >= LIM` discharges.

**Carrier found against the repair itself:** draft 2 built the dependency-bound set from explicit
bindings only, and a callee module that obtains `LIM` through its OWN `from consts import *`
PROVED again (witness 1473). Draft 3 follows wildcard sources on both sides.

**Two gates the placement had to respect, both measured on the draft.** Helper `def`s in
`ir_resolve.py` broke the mirror-coverage ratchet (556 > 549); parking them in an unmirrored file
would game it, so the check is inlined into two functions the mirror already carries as
`\trusted` stubs. And a new `raise` in `resolve_imports` broke the trusted-raises ratchet (63 > 62);
the mirror stub now DECLARES `#@ raises PyCSLSemanticError when True` (route #59's precedent),
14 declared / 62 silent.
