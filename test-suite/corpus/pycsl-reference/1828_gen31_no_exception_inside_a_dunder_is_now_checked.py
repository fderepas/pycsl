r"""Test 1828 — gen #31 (expected FAIL): `#@ no_exception \all` inside a DUNDER is checked.

ROUTE #219's decisive pair, one identifier apart from 1829. Before the repair this file
reported

    [+] Verification SUCCESS! All contracts formally proven.

over a method whose only statement divides by zero under a contract saying it raises
nothing. CPython raises `ZeroDivisionError`. The checker that catches it EXISTS AND WORKS —
rename `__enter__` to `enter` (corpus 1829) and the identical file FAILS.

THE MECHANISM WAS A COLLECTION, NOT A CHECK. `Module5._should_skip_method` dropped every
dunder before any IR was built, so the method never entered `ir_data["functions"]`, and
EVERY check that iterates that list was blind to it: UB-7.1's hard refusal (1830), route
#204's interface-frame narrowing, routes #200/#202's actual/formal agreement, route #37's
jumping `try ... else`, and the whole of `core_ir_semantic`.

That is the same headline routes #216 and #219 turn on — "All contracts formally proven"
printed over a module in which one contract was never considered.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ no_exception \all
    def __enter__(self) -> int:
        d: int = 0
        return 10 // d
