# Route #219 (CLOSED, gen #31) — every check, VC and UB detector was switched off by the method's NAME

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

## A SECURITY POLICY is accepted and silently unenforced — the third carrier

`#@ happy NAME: targets M postcond P` is the trust-boundary surface: a NAMED property
attached to a target method and discharged as an ordinary contract. Module 3 attaches it by
walking the AST, **where dunders are present**, so the "a missing target is a hard error"
refusal (`Module3_Weaver.py:781`, the loop with fifteen raises in it) does NOT fire. Then
Module 5 drops the method and nothing is checked:

```python
#@ happy no_decrease:
#@     targets __enter__
#@     postcond self.v >= \old(self.v)
class C:
    def __init__(self) -> None: self.v: int = 5
    #@ assigns self.v
    def __enter__(self) -> int:
        self.v = 0              # 5 -> 0 plainly violates the policy
        return 0
```

    [+] Verification SUCCESS! All contracts formally proven.

Rename `__enter__` to `bump` and the identical file FAILS. This carrier matters more than
the other two because the `happy` family is the surface a reader would point at to say
"this property is enforced across the module" — and the enforcement is decided by the
target's NAME. It is also the shape routes #206/#208/#210/#211 kept finding from the other
side (a policy stamped into a body that is never lowered); this is the same defect reached
through the TARGET rather than through the body.

## OTHER METHOD KINDS ARE CLEAN — measured, so the scope is not guessed

The same `#@ no_exception ll` over `10 // 0` was run as a plain method, a `@staticmethod`,
a `@classmethod`, a `@property`, a nested function and a module-level function. Every one of
them FAILS or is REFUSED. **Only the dunder spelling evades**, which is what makes the
repair exactly "stop dropping dunders" and nothing wider.

## Carriers

* `route219-carrier-no-exception-inside-a-dunder.py`  — expects SUCCESS (the false certificate)
* `route219-control-no-exception-non-dunder.py`       — expects FAILED  (one identifier apart)
* `route219-carrier-ub71-inside-a-dunder.py`          — expects SUCCESS (a UB refusal evaded)
* `route219-control-ub71-plain-function.py`           — expects REFUSED (the detector working)

All four registered in `bin/check-open-route-carriers.py`, so the day one of them changes,
somebody notices.


---

## CLOSED — 2026-09-23, gen #31, by EMITTING the dunders

The repair is the one this record priced: `Module5_IREmitter._should_skip_method` now skips
only the CONSTRUCTOR HOOKS — `__init__`, `__new__`, `__post_init__` — and every other dunder
is emitted as an ordinary method, so it enters `ir_data["functions"]` and every check that
iterates that list sees it.

**All three carriers close, and their one-identifier-apart controls are unchanged:**

    1828  `#@ no_exception \all` over `10 // 0` in `__enter__`   SUCCESS -> FAILED
    1829  the same body in `enter`                              FAILED  -> FAILED
    1830  UB-7.1's loop in `__enter__`                          SUCCESS -> REFUSED
    1831  `#@ happy ... postcond` targeting `__enter__`         SUCCESS -> FAILED
    1832  the same policy targeting `bump`                      FAILED  -> FAILED
    1827  a dunder override that REFINES, under
          `--check-behavioral-subtyping`                        REFUSED -> SUCCESS

The last line is the one worth reading twice. Route #216's refusal stopped the LIE but also
meant a CORRECT dunder override could only be DECLINED, never certified. With the methods
emitted, `goal sub____len___refines_base` is BUILT: 1805 (a weakened override) still fails
and now fails ON THAT GOAL rather than on the refusal, and 1827 discharges. The difference
is between "we refuse to look" and "we looked and it holds".

**THE TWO SKIPPED HOOKS KEEP THE REFUSAL**, because for them the original hazard is
unchanged. `__new__` is not a method and becomes a Why3 type error when emitted with a
return annotation (review oracle O9); `__post_init__` is owned by route #150's dedicated
mechanism, and emitting it closes nothing while costing a failing frame goal on every honest
dataclass (spiked before deciding).

**WHAT IT COST, and every number was measured rather than estimated:** the `\trusted` count
goes 459 -> 461. Both new markers are CORRECTIONS: `errors.py::PyCSLError.__str__` and
`Module2_Parser.py::_Tok.__repr__` were counted among the 887 VERBATIM UN-TRUSTED TWINS —
the population this project calls verified — while never being emitted or proved, because
`check-untrusted-emitted` allow-listed `__repr__`/`__str__`/`__enter__`/`__exit__` as
EXPECTED-ABSENT on the stated grounds that "dunders are modelled structurally", which was not
what the emitter did with them. That allow-list now names only the skipped hooks.
