# ROUTE #178 — an implicit raise inside an uncontracted callee is invisible to the caller's context

**Status: CLOSED by gen #29 (battery Q green: suite 3755/3773, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1.
Generator: carrier of #170 (missing-key reads caught by the caller).

## Measured at `2698cc81`, each PROVED

    def get(d): return d["b"]            # d = {"a": 1}
    #@ no_exception KeyError   v = get(d)                                 (CPython KeyError)
    try: v = get(d)  except KeyError: return 9;  return v * 0   == 0      (CPython 9)
    class C: def get(self): return self.d["b"]
    try: v = c.get() except KeyError: return 9;  return v * 0   == 0      (CPython 9)

Inside a function without its own `no_exception` a map read's missing-key arm is the ambient
placeholder (route #57's documented convention), so the raise does not exist in the model; the caller's
declared (or #171-widened) context never reaches it. Divisions and list indexing in a callee are always
checked (refused at HEAD: `10 // (len(d) - 1)`, `xs[5]`).

## Repair (draft)

`_reset_function_state` (trusted), under an active KeyError / IndexError / ValueError context: compute,
per same-file function, the implicit-raise sources not covered by its own `no_exception` (subscripts →
KeyError/IndexError, TupleUnpack and `int()`/`float()` calls → ValueError), closed transitively over
calls (name / method-name suffix); a call from the current function to such code is refused.
Emission inert (corpus/pyref/mirrors). Witnesses 1625-1627 (XFAIL), 1628 (PASS: callee declaring
`no_exception KeyError`).

## Completeness cost

Over-approximate: any subscript in an uncontracted callee blocks calling it under KeyError/IndexError
(even an always-checked list read). 0 affected programs in the corpora and mirrors.
