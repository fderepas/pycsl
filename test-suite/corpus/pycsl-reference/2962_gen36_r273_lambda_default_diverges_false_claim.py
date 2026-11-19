r"""Test 2962 — route #273 (expected FAIL): a lambda's default `spin()` is evaluated when
the lambda EXPRESSION is evaluated; `spin` is `#@ \diverges`. The Lambda IR node carries no
defaults, so `f`'s termination PROVED at 5a307a33. CPython: never returns. Now refused
(PYCSL-SEM-DEF-TIME-EVALUATION).
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
    h = lambda x=spin(): x
    return 1

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=f, daemon=True)
    t.start()
    t.join(1.0)
    print("does not terminate" if t.is_alive() else "returned")
