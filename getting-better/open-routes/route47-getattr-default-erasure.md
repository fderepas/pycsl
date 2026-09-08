# OPEN ROUTE #47 — `getattr(o, <absent>, {})` IS THE INTEGER ZERO, and so is the
# no-default form that Python answers with an AttributeError

**Found 2026-09-08 by relaunch #48, at commit `4289185b`, BY THE PLANE WRITTEN THE SAME
HOUR** (`bin/check-singleton-constant-lowering.py`). The plane's whole purpose is that the
next instance of this shape is found when the instrument is written rather than months
later by hand, and it found this one within minutes of its first run.

## The demonstration (default `hoare` model, no flags, Python run to confirm)

```python
class C:
    #@ requires True
    #@ ensures True
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = C()
    d = getattr(c, "missing", {})     # Python: `{} == 0` is False -> f() returns 0
    if d == 0:
        return 7
    return 0
```
`[+] Verification SUCCESS! All contracts formally proven.`

| program | model | Python |
|---|---|---|
| `d = getattr(c, "missing", {}); if d == 0:` | taken | `{} == 0` is **False** |
| `d = getattr(c, "missing", []); if d == 0:` | taken | `[] == 0` is **False** |
| `d = getattr(c, "missing"); if d == 0:` | taken | **AttributeError** — there is no value |

Reproducers: `scratchpad/w48/probe/k1_getattr_default_dict.py`,
`k3_getattr_default_list.py`, `k2_getattr_no_default.py`.

## Why route #22 did not already close it

Route #22 (witness `0991`) closed the case where the attribute IS DECLARED by the emitted
record — there, taking the default is a WRONG READ. It deliberately left ABSENCE alone, and
its reasoning is quoted in `0991`: *"ABSENCE still takes the default: a name the record does
not declare is genuinely missing at runtime too."*

That reasoning is right about WHICH VALUE is returned and says nothing about HOW THAT VALUE
IS MODELLED. `_lower_getattr`'s absent path ends:

```python
        if len(args_ir) <= 2:
            return "0"
        nt = default_ir.get("type") if isinstance(default_ir, dict) else ""
        if nt in ("DictLit", "ArrayLit", "SetLit", "Call"):
            return "0"
```

The comment calls the coercion "fails-safe: the dict/list content is then unmodeled". It is
not: an *unmodelled* value would be undecidable, and the integer `0` is DECIDABLE. This is
the campaign's general shape a SIXTH time — a Python value the model does not represent,
lowered to an integer literal, is not merely lost but DECIDED, and decided wrongly (routes
#40 `...`, #41 erased locals, #42 the bool singleton, #43 the complex literal, #44 `None`).

The no-default form is worse than the others: Python does not produce a wrong value there,
it produces **no value at all** — `getattr(c, "missing")` raises `AttributeError` — and the
model answers `0` and proves a contract about it.

## THE FIX, and it is the device that has now worked four times

An opaque `val function` with no defining axiom, PER DEFAULT KIND, replacing each `return
"0"`:

* `pycsl_getattr_default_dict` / `_list` / `_set` / `_call` — per KIND rather than shared,
  because `{} == {}` is True in Python and `{} == []` is False, so one constant per kind
  keeps the true equality provable and makes the false one undecidable. (Contrast route
  #41, which needed PER-NAME, and route #44, which needed SHARED — the granularity is a
  semantic decision each time, not a convention.)
* the no-default form is not a value at all and should be REFUSED, not made opaque; but
  measure first — `bin/check-getattr-erasure.py` reports ABSENT 7 / UNKNOWN 19 sites in the
  mirror, and the refusal must not break them.

NOT CLOSED IN THIS INCREMENT because routes #44 and #45 were already staged in the same
files and their whole-file re-proofs had not landed; stacking a third change on an unproven
pair is how a window loses the ability to say which change caused which failure.
