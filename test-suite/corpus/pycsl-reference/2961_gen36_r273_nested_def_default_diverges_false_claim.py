r"""Test 2961 — route #273 (expected FAIL): the nested def's default `spin()` calls a
`#@ \diverges` function when the `def` runs; `f` (not `\diverges`) claims to terminate
with 1. The default was dropped, so termination PROVED at 5a307a33. CPython: never returns
(the alarm below stops it). Now refused (PYCSL-SEM-DEF-TIME-EVALUATION).
"""
# pycsl-expected: FAIL

#@ \diverges
#@ ensures \result == 1
#@ assigns \nothing
def spin() -> int:
    while True:
        pass
    return 1

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    def inner(x: int = spin()) -> int:
        return 1
    return 1

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=f, daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
