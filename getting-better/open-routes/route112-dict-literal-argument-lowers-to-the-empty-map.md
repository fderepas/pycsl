# ROUTE #112 — a NON-EMPTY dict literal outside a map-returning function lowers to the
# EVERYWHERE-EMPTY MAP, and route #86's repair lets it through by PREFIX

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED (gen #22, 2026-09-14).**
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
