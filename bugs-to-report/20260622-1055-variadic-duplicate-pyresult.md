# `join(*parts)` variadic args cause duplicate py_result ref (type mismatch)

**Category:** Candidate pycsl bug (emitter)
**Filed by:** test-supervise-sl (os.path fleet)
**Date:** 2026-06-22
**Status:** CONFIRMED

## Reproduction

In `src/pycsl_lib/os/path.py`:

```python
def join(a: str, *parts: str) -> str:
    result = a
    for p in parts:
        if p and p[0] == '/':
            result = p
        elif not result or result[-1] == '/':
            result = result + p
        else:
            result = result + '/' + p
    return result
```

Run: `PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os/path.py`

## Observed behavior

WhyML emission produces a **duplicate `py_result` ref** with incompatible types:

```whyml
let py_result = ref 0 in      (* int ref — from the `result = a` line *)
let p = ref 0 in
let py_result = ref a in      (* string ref — shadows the int ref *)
...
py_result := !p               (* TYPE ERROR: assigning string to... *)
```

Why3 error:
```
File "...mlw", line 44, characters 47-63:
This expression has type (), but is expected to have type int
```

The first `let py_result = ref 0` (int) is emitted from the assignment
`result = a`, and the second `let py_result = ref a` (string) from the loop
initialization. Why3's type inference sees the int ref first and the assignment
`py_result := !p` (string) fails.

## Expected behavior

A single `py_result` ref of the correct type (`string`) should be emitted. The
variadic `*parts` pattern should not cause a duplicate ref.

## Impact

Any function using `*args`/`**kwargs` with a result variable may trigger this
emission bug. The entire module containing such a function fails to emit,
blocking verification of ALL functions in the module (even unrelated ones).
