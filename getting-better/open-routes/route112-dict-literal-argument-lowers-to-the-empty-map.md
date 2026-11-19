# ROUTE #112 — a NON-EMPTY dict literal outside a map-returning function lowers to the
# EVERYWHERE-EMPTY MAP, and route #86's repair lets it through by PREFIX

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Found by gen #22 (2026-09-14); original finding preserved below.
**Severity: SEV-1. First-order. NO ADVERSARIAL NAMING** — `g({1: 5})` is ordinary Python.

## PROVENANCE

Generator `carrier-rerun`. Carrier: route #111's "second fact" (a dict literal assigned to a
field in a non-`__init__` method is modelled empty). Gen #22 instrumented both erasure sites
and found that the literal is erased BEFORE #111's guard ever sees it — the erasure lives in
`DictLitExpr`'s own lowering, which makes every expression position a candidate, not just
the field store. Re-running the carrier on the argument position was LIVE.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/expressions.py`, the end of the `DictLitExpr` arm of `_expr_to_whyml`:
the relaunch-#16 faithful `map_update_some` chain is GATED on the enclosing function's
`_func_return_type` being a `map <K> (option <V>)`. Every other non-empty literal falls
through to

    return "(const (None: option int))"

— a DEFINITE value (the empty map), not an unknown one. Route #86's map-param coercion then
KEEPS it, because its fence is a text prefix list that includes `"(const (None: option int)"`.
#86 replaced its OWN witness with `any_map` and waved an already-erased literal through.

## BOTH DIRECTIONS MEASURED at HEAD `a990ad50`

`p_arg.py`:

```python
#@ ensures (1 in d) ==> \result == 1
#@ ensures (not (1 in d)) ==> \result == 0
def g(d: Dict[int, int]) -> int:
    if 1 in d:
        return 1
    return 0

#@ ensures \result == 0
def f() -> int:
    return g({1: 5})
```

FALSE claim `\result == 0` — `[+] Verification SUCCESS` (rc=0). CPython returns **1** (run).
TRUE twin `\result == 1` — rc=1, `postcondition of goal f'vc` Unknown (read).
Emitted: `(g (const (None: option int)))`.

## CONTROLS / FENCES (all logged in probes.tsv, gen 22)

| shape | verdict | fence |
|---|---|---|
| `d: Dict[int,int] = {1: 5}` local, `1 in d` | FAIL-CLOSED | statement path builds its own faithful chain |
| `x = {1: 5}; g(x)` | FAIL-CLOSED | same chain; `!x` is alnum so #86 keeps it |
| `1 in {1: 5}` inline | FAIL-CLOSED (type error) | `contains_check` takes int |
| `g(dict({1: 5}))`, `g(dict([(1, 5)]))` | FAIL-CLOSED | the dict-call arm emits #86's `any_map` |
| `set([1,2])` / `{1,2}` annotated local | FAIL-CLOSED (type error) | int-erased local, typing rejects |

## POPULATION (instrumented census, all four trees, gen #22)

The fallback FIRES 37 times for a NON-EMPTY literal (26 corpus, 10 mirror, 1 pycsl_lib), but
most are LOWER-AND-DISCARD calls from the local-assignment path, whose emission is the faithful
chain (read: 1112, 0751, 1143, pyref 0049/0139/0150). The byte effect of a repair is therefore
decided by the emission diff, not by this count.

## REPAIR

Non-empty literal that the faithful chain cannot build -> the POLYMORPHIC UNCONSTRAINED
`(any_map ())` (routes #85/#86/#89's value, already spiked), never the empty map. Landed
together with route #111 (same erasure family; #111's own guard must not re-erase an
`any_map` RHS back to the empty map).

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** `expressions.py` `DictLitExpr` arm: a NON-EMPTY literal the gated faithful
chain cannot build lowers to `(any_map ())`, never `(const (None: option int))`. An empty `{}`
is unchanged. **The co-landing fix that the battery found:** `_emit_first_assign` folded a local
literal's keys onto the LOWERED LITERAL as its base, which was only the empty map BECAUSE the
literal lowered to the empty map; the first sweep moved 17 corpus + 2 python-reference files to
`map_update_some (any_map ()) ...` (a completeness regression). The base is now named
explicitly. LESSON: a value that was a lie in one consumer (an argument) was load-bearing in
another (a fold's base) — read the hunks, not the MOVED count.

**Witnesses.** `p_arg` false claim refused; corpus 1308 (XFAIL). The only corpus effect is one
unused `val any_map` declaration in 20 pycsl-reference + 3 python-reference files (declared by a
lower-and-discard call).
