"""Test 0697 — strings: `len(<str-returning call>)` → str_length_op (10-1732-gap Gap 2).

DEMAND-DRIVER for Gap 2. Before this fix `_is_string_expr` had no `Call` case, so a call
node was never string-typed; `len(g(s))` taken DIRECTLY (no intermediate local) fell through
to the opaque `iter_length` and `\result >= 0` could not discharge. The strmod model worked
around this by binding the call result to a local first.

The fix adds a `Call` arm to `_is_string_expr` keyed on `_module_method_return_types[fn] ==
"string"` (a `-> str` annotation or string-returning body). So `len(g(s))` now routes to
`String.length` / `str_length_op`, which carries `result = String.length s` — and
`String.length` is `>= 0` by Why3's string law.

STATUS — **PROVES**. `g` returns its `str` param; `len(g(s))` routes to str_length_op so the
`\result >= 0` postcondition of `caller` discharges from the length-nonnegativity law."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def g(s: str) -> str:
    return s

#@ requires \str_length(s) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def caller(s: str) -> int:
    return len(g(s))          # MUST route to str_length_op (not iter_length)

if __name__ == "__main__":
    print("PASS")
