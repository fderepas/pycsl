# Route #198 — a bare `return` was the integer zero

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present.

## The claim that was wrong

`src/pycsl/module6_whyml/stmt_control_flow.py::_handle_return_stmt`:

```python
val_ir = stmt.value.to_dict() if stmt.value is not None else None
...
if val_ir is None:
    val = "()"          # a BARE `return`
...
elif val == "()":
    val = "0"           # <- the whole route
...
return f"{indent}raise (Return {val})"
```

A bare `return` in a function whose WhyML return type is `int` became `raise (Return 0)`.
Python's bare `return` returns `None`, and `None == 0` is `False`.

## The witness

```python
#@ requires x > 0
#@ ensures \result == 0
def f(x: int) -> int:
    if x > 0:
        return
    return 5
```

PROVED (`Valid`, 24 and 32 steps). CPython: `f(1)` is `None`; `None == 0` is `False`.

**The decisive twin.** `#@ ensures \result != 0` — TRUE of CPython's answer — was REFUSED.
A false contract proving while its true negation is refused is the signature: the model has
not merely lost a value, it has SUBSTITUTED one.

Corpus: `1693_route198_a_bare_return_was_the_integer_zero.py` (expected FAIL),
`1694_route198_a_real_early_return_still_carries_its_value.py` (control, PASSES).

## The evidence that also dictated the repair

The IDENTICAL program spelled `return None` instead of the bare `return` already REFUSED
`\result == 0`: route #191 made the typed `None` leaf read back as the shared opaque
`pycsl_none`. So a single Python statement had two spellings that lowered to two different
values, and exactly one of them was wrong. The repair is not an invention — it is making
the two spellings agree:

```python
elif val == "()":
    self._add_abstract_op("val function pycsl_none : int")
    val = "pycsl_none"
```

`(any int)` would also have been sound, and was rejected for the reason #191 recorded: `any`
is FRESH at every evaluation, so it cannot keep two `None`s equal, while the shared constant
can. Sound AND as complete as the truth allows.

Frame note: `_handle_return_stmt` already calls `self._materialize_bridge()`, whose mirror
frame is the same pair (`_abstract_ops, _obj_state_written`) that `_add_abstract_op`
declares, so the new call adds no field to this method's effective frame. This is the shape
route #193 got wrong on a `@staticmethod`; here the method is already an effectful instance
method, and the mirror already calls an equally-framed sibling from the same body.

## Where it came from — a plane's own written justification

`core_ir_semantic._check_scalar_return_annotation` (route #51's refusal of a `-> str` that
can `return None`) justifies its own scope:

> SCOPED TO `-> str` DELIBERATELY, and the scope was measured, not guessed: the `-> int`
> spelling of the same file FAILS CLOSED today (it reaches route #44's opaque `pycsl_none`),
> so a refusal there would buy nothing.

True of the EXPLICIT `return None`. Never measured for the BARE `return` — even though the
check's own helper `_returns_literal_none` counts both spellings. **A scope justified by
"the other case fails closed" has to name WHICH SPELLINGS of the other case were run.**
The docstring now records the correction.

## Neighbours swept while here (both fail-closed, recorded not assumed)

- `-> str` with a bare `return`: REFUSED by Module 4, with route #51's diagnostic. Both
  spellings are caught there; only `-> int` had the hole.
- `-> int` FALLING OFF THE END (the same docstring's stated RESIDUE): `\result == 0` and
  `\result != 0` both REFUSED. Still fails closed by the type accident the docstring names,
  not by intent — the residue stands as written.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| `\result == 0` (false) | REFUSED | REFUSED |
| `\result != 0` (true twin) | REFUSED (opaque answers neither) | REFUSED |
| control `return 3` | PROVES | PROVES |
| corpus byte-diff | ZERO | see the battery record in `driver-progress.log` |
| mirror emissions | byte-inert | see the battery record in `driver-progress.log` |
