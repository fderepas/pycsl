r"""Test 2270 — route #242 (expected FAIL): a `let function` WHOSE BODY IS NONDETERMINISTIC IS ONE
VALUE PER ARGUMENT. `h` has no writes, so it was emitted as a Why3 `let function`; its body reads the
opaque `py_isinstance_bool_int_op x` (the model cannot tell `True` from `1`), and Why3 froze that
answer per argument. `h(True)` and `h(1)` both lower to `h 1`, so `\result == 1` PROVED at f0fc0201
while CPython `m()` = 0 (h(True) = 1, h(1) = 0). `h` is now a plain `let` (each call a fresh
evaluation), and the postcondition is unproved. Controls: 2275, 2276.
"""
# pycsl-expected: FAIL


#@ assigns \nothing
def h(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if h(True) == h(1):
        return 1
    return 0
