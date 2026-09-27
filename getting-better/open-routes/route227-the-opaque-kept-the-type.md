# OPEN ROUTE #227 — THE `pycsl_none` REPAIR MADE THE VALUE UNKNOWN AND LEFT THE TYPE TRUE

**Status: OPEN, reproduced at HEAD `1b2f676e`, repair scoped below. Severity 1.**
Generator: `oracle-audit` — the self-annotation suite, scheduled for the first time in gen #32.
**Order 2: the carrier IS the campaign's own repair** (routes #44 / #184 / #191).

## THE WITNESS — four lines, no container, no annotation

```python
#@ ensures \result == 3
#@ no_exception \all
def w4() -> int:
    v = None
    return v - v + 3
```

`[+] Verification SUCCESS! All contracts formally proven.` (Valid, 31 steps.)

CPython: `TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType'`.
The function has **no value at all**, and PyCSL proves both that it returns 3 and — via
`#@ no_exception \all` — that it raises nothing.

Emitted WhyML, verbatim (`--no-proof --keep-mlw`):

```
  val function pycsl_none : int
  let w4 () : int
    ensures  { (result = 3) }
  =
    v := pycsl_none;
    ((pycsl_none - pycsl_none) + 3)
```

## THE MECHANISM — AND WHY THE EXISTING REPAIR CANNOT REACH IT

Route #44 recorded a `None` binding in `_erased_truthy_locals` and made a READ of that name
the opaque `val function pycsl_none : int` "with NO defining axiom", replacing a definite
integer `0`. Routes #183 / #184 / #191 extended the same device to the FIELD, the LIST
ELEMENT, the DICT VALUE and the four STORE positions. Every one of those closures is real:
`v == 0` no longer proves, and that is what they were built to stop.

**But the opaque has no defining axiom and a perfectly good TYPE.** `pycsl_none : int`
inhabits `int`, so every law of integer arithmetic still applies to it. The falsehood did not
leave — it moved from the VALUE to the TYPE:

| expression | model | CPython |
|---|---|---|
| `v == 0`     | undecided — **#44's closure** | `False` |
| `v - v + 3`  | **proves `== 3`** | `TypeError` |
| `v < v`      | **proves `False`**, so `\result == 0` proves | `TypeError` |
| `v * 0 + 3`  | **proves `== 3`** | `TypeError` |
| `v - v` via a `Dict[int, Optional[int]]` read | **proves `== 3`** | `TypeError` |

And `#@ no_exception \all` — a claim about the TYPE alone — is certified in every row.

## THE GENERATOR THIS ROUTE IS THE FIRST INSTANCE OF

>>> **WHEN A REPAIR ANSWERS A WRONG VALUE WITH AN OPAQUE, IT HAS MOVED THE FALSEHOOD FROM
>>> THE VALUE TO THE TYPE.** Re-probe the repaired carrier with an expression whose result
>>> does NOT depend on the value — `x - x`, `x * 0`, `x < x`, `x // x` — and with the
>>> `no_exception` claim. `v == 0` is the probe the repair was built to defeat; `v - v` is
>>> the one nobody wrote.

The corpus proves this was a near miss rather than an oversight. Route #44's own negative
witness `1060_route44_none_arith.py` is *this shape*:

```python
#@ ensures \result == 5
def f() -> int:
    x = None
    return x + 5
```

It picked `x + 5` — value-DEPENDENT, so the opaque genuinely closed it — where `x - x` is
value-INVARIANT and was never tried. The witness file's own docstring says "an equality-only
fix would have been the same mistake one operator later"; the fix was arithmetic-aware and
still stopped one *algebraic identity* short.

## WHAT IS AND IS NOT REACHABLE — measured, not assumed

* **FAIL-CLOSED: the Optional PARAMETER.** `def w1(v: Optional[int]) -> int: return v - v + 3`
  is L3-tc REFUSED (`expected to have type int`) — a parameter is modelled as a union/option.
* **FAIL-CLOSED: the explicit-`None` MEMBERSHIP shape.** `d[k] = None` lowers to
  `map_update_some !d k pycsl_none`, *not* `map_update_none`, so `k in d` proves `== 1` (true
  of the program) and the false twin `== 0` FAILS. Absence and a stored `None` do not share a
  representation. Probed because they plausibly could have.
* **LIVE: the straight-line LOCAL**, and the dict/list value read into a local.

## THE REPAIR — use the record to REFUSE, which is what it is already used for elsewhere

Route #46's file states the distinction this repair turns on, in its own words:
**"route #50's facts are used to REFUSE; route #44's are used to DECIDE."** #44's `None`
fact is used only to decide (the truthiness arm answers `false`, the value arm answers the
opaque). Nothing consults it to refuse, and arithmetic on a `None` is the one place where a
refusal is unambiguously right, because *every* such program is a `TypeError` in CPython.

So: in `_handle_binop` (PROGRAM code only, `not self._in_spec`), REFUSE when an operand is
definitely `None` — a `Var` whose `_erased_truthy_locals` entry is `"None#empty"`, or a
literal `None` node — and the operator is arithmetic (`+ - * / // % ** << >> & | ^`) or a
STRICT ORDER (`< <= > >=`). `==` / `!=` are left DECIDED: `None == None` really is `True`,
and the shared (not per-name) opaque is what makes that faithful — corpus control 1063.

**Write it INLINE** (wall-lesson (a4)): `_handle_binop`'s mirror twin is `#@ \trusted`, and a
new private method in a mirrored file moves the `check-mirror-coverage` ratchet and adds an
unused abstract `val` to every importer's emission.

### THE FENCE'S PRECISION IS THE RECORD'S CERTAINTY, AND THAT IS WHY IT IS SAFE

`AMBIG` — a name bound to `None` on one path and to something else on another — must NOT be
refused, and does not need to be: `_erased_truthy_locals` only ever holds `"None#empty"` for
a name with **no nested rebinding** (`functions.py` pre-seeds `"AMBIG"` when a name has
assignments of two kinds and at least one at nested depth). That is exactly where the
legitimate guarded idioms live, and both real-code hits of the census are there:

* `tests/to_annotate/013-greedy-algorithms.py`: `last_end = None` before a loop that rebinds
  it, read under `if last_end is None or start >= last_end` — the short-circuit idiom.
* `src/pycsl/module6_whyml/expressions.py::_call_named_builtins`: `v = None  # defer bool`
  then `if isinstance(v, int): … v < 0` — guarded by the `isinstance`.

Both are AMBIG, so the fence cannot reach them. Verified by probe: the conditional-rebind +
`is not None` shape (`w8`) PROVES today and must keep proving — it is the fence's
completeness control, alongside `w7` (`v = None; v = 0; return v - v + 3`, where the record is
cleared on rebinding).

### POPULATION, censused over 4531 files

`test-suite/corpus` + `src/self-annotate` + `src/pycsl` + `src/pycsl_lib` + `tests`, with a
linear approximation of the recorder: **3 hits, and exactly ONE in the corpus** —
`1060_route44_none_arith.py`, which is `# pycsl-expected: FAIL`. The other two are the AMBIG
pair above. So the predicted sweep is 0 MOVED with **1 GONE** (1060 stops emitting and fails
by the REFUSAL instead of by an undecided postcondition), which is precisely the disposal
route #217 took for `1725_gen30_bytes_count_form_excluded`.

### THE MESSAGE'S ADVICE MUST NAME A CONDITION THE EMITTER CHECKS

Per the campaign's first-ranked generator: advice naming a marker the emitter merely READS is
the hazard. Two conditions here are genuinely checked and may be advised:
* rebinding the name to a definite value clears the record (`statements.py` pops the entry on
  a non-`None` rebinding, and the read site's own comment says so);
* a name conditionally rebound is already AMBIG and this refusal never fires on it.
`is not None` narrowing on a *linear* `None` binding is NOT implemented and must NOT be
advised.
