# Route #219 (OPEN) — every check, VC and UB detector is switched off by the method's NAME

**Found:** 2026-09-23, gen #31, by applying lesson (t3) to the one collection the campaign
had just spent a morning learning about: `ir_data["functions"]`.

## The decisive pair, ONE IDENTIFIER APART

```python
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ no_exception \all
    def __enter__(self) -> int:        # rename to `enter` and the file FAILS
        d: int = 0
        return 10 // d
```

    [+] Verification SUCCESS! All contracts formally proven.

The same file with `__enter__` renamed to `enter`:

    [-] Verification FAILED or INCOMPLETE.

CPython raises `ZeroDivisionError`. The contract `#@ no_exception \all` is FALSE of the
method, the checker that catches it EXISTS AND WORKS, and it is switched off by the
method's name.

## A UB REFUSAL is evaded by the same mechanism

UB-7.1 (mutation during iteration) is not a proof obligation, it is a HARD REFUSAL the UB
catalog documents. In a plain function:

    [!] PIPELINE ERROR: ... (function 'go', for-loop near line 8): UB-7.1 — the loop body
    mutates the iterated collection 'xs'. This is undefined behaviour in CPython ...

The identical loop inside `__enter__`:

    [+] Verification SUCCESS! All contracts formally proven.

So the perimeter this project advertises — "PyCSL detects these Python undefined
behaviours" — has a hole the width of a method name.

## The mechanism, and why it is a FAMILY rather than one defect

`Module5_IREmitter._should_skip_method` drops every dunder before any IR is built. The
method is therefore absent from `ir_data["functions"]`, and **every check that iterates
that list is blind to it**. An AST census of `for` loops containing a `raise PyCSL*Error`
across the shipping compiler finds 116 such loops over 94 distinct collections; five of
them iterate `ir_data["functions"]` directly in `pycsl.py` alone:

| site | what it enforces |
|---|---|
| `pycsl.py:523`  | **UB-7.1** mutation-during-iteration (a hard refusal) |
| `pycsl.py:796`  | route #204 — an `#@ interface assigns` NARROWER than the definition |
| `pycsl.py:980`  | routes #200/#202 — actual/formal agreement at a call |
| `pycsl.py:1454` | route #37 — a jumping `try ... else` whose lowering drops a `raise` |
| `pycsl.py:1503` | (the fifth of the same shape) |

and the whole of `core_ir_semantic` consumes the same IR. The pattern is lesson (t3)'s
question answered on the largest collection in the system: **what stops an x from reaching
`ir_data["functions"]` at all? A dunder name does.**

## What it is NOT

It is not "dunders are unsupported". A reader is told the opposite by the summary line: the
tool prints **All contracts formally proven** over a module in which one contract was never
considered. That is route #216's standard — the same sentence over a module whose whole
body is `type sub = { }` — and it is why this is recorded as a route rather than a gap.

## The repair, and it is already priced

Emit non-`__init__` dunders as ordinary methods. MEASURED, spike-gated, in
`getting-better/emit-dunders-wall.md`:

* Both carriers above close: the `no_exception` pair becomes FAILED/FAILED and the UB-7.1
  carrier becomes REFUSED.
* Whole-corpus blast radius is **15 moved emissions of 1310** in `pycsl-reference` and
  **5 of 2199** in `python-reference`, **0 GONE, 0 APPEARED**, and exactly ONE verdict
  changes (`0402.py`, whose `__del__` writes `self._n` under an absent `#@ assigns` — a
  defect the skip was hiding, repaired by one honest annotation line).
* Mirror cost: 18 of 53 emissions move and owe a re-proof; of the ten mirror dunders
  EIGHT ALREADY CARRY `#@ \trusted`, so the marker count moves by at most two
  (`errors.py::PyCSLError.__str__`, `frontend/Module2_Parser.py::_Tok.__repr__`) — and
  those two are currently counted among the UN-trusted mirror functions while never being
  emitted, so marking them is a CORRECTION of the headline number, not a regression.

## Carriers

* `route219-carrier-no-exception-inside-a-dunder.py`  — expects SUCCESS (the false certificate)
* `route219-control-no-exception-non-dunder.py`       — expects FAILED  (one identifier apart)
* `route219-carrier-ub71-inside-a-dunder.py`          — expects SUCCESS (a UB refusal evaded)
* `route219-control-ub71-plain-function.py`           — expects REFUSED (the detector working)

All four registered in `bin/check-open-route-carriers.py`, so the day one of them changes,
somebody notices.
